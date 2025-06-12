"""
Vue pour la gestion des budgets utilisateurs par année fiscale
"""
import streamlit as st
from datetime import date
from controllers.auth_controller import AuthController
from models.user_budget import UserBudgetModel
from models.user import UserModel
from views.admin_dropdown_options_view import get_valid_dropdown_options
from utils.fiscal_year_utils import byxx_to_year

@AuthController.require_auth
def gestion_budgets_view():
    """Page de gestion des budgets utilisateurs"""
    user_info = AuthController.get_current_user()
    
    # Vérifier les permissions admin
    if user_info['role'] != 'admin':
        st.error("❌ Accès réservé aux administrateurs")
        return
    
    st.subheader("💰 Gestion des Budgets Utilisateurs")
    
    # Récupérer les années fiscales disponibles
    annee_fiscale_options = get_valid_dropdown_options('annee_fiscale')
    
    if not annee_fiscale_options:
        st.error("⚠️ Aucune année fiscale configurée dans les listes déroulantes")
        st.info("Veuillez d'abord configurer les années fiscales dans 'Listes Déroulantes'")
        return
    
    # Sélection de l'année fiscale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sélectionner l'année fiscale depuis les options configurées
        selected_year_str = st.selectbox(
            "📅 Année Fiscale",
            options=[opt[0] for opt in annee_fiscale_options],
            format_func=lambda x: next((opt[1] for opt in annee_fiscale_options if opt[0] == x), x),
            index=len(annee_fiscale_options)-1 if annee_fiscale_options else 0,  # Dernière année par défaut
            help="Sélectionnez l'année fiscale à gérer"
        )
        # Utiliser directement la valeur sélectionnée
        selected_year = selected_year_str
    
    with col2:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    # Affichage des onglets
    tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "👥 Attribution budgets", "📈 Analyse"])
    
    with tab1:
        _display_budget_overview(selected_year)
    
    with tab2:
        _display_budget_assignment(selected_year, annee_fiscale_options)
    
    with tab3:
        _display_budget_analysis(selected_year)

def _display_budget_overview(fiscal_year):
    """Affiche la vue d'ensemble des budgets"""
    st.markdown("### 📊 Vue d'ensemble")
    
    # Récupérer le résumé des budgets
    summary = UserBudgetModel.get_budget_summary_by_year(fiscal_year)
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Budget Total Alloué",
            f"{summary['total_allocated']:,.0f}€",
            help="Somme de tous les budgets alloués"
        )
    
    with col2:
        st.metric(
            "👥 Utilisateurs avec Budget",
            f"{summary['users_with_budget']}/{summary['total_users']}",
            help="Nombre d'utilisateurs ayant un budget alloué"
        )
    
    with col3:
        st.metric(
            "📊 Budget Moyen",
            f"{summary['average_budget']:,.0f}€",
            help="Budget moyen par utilisateur"
        )
    
    with col4:
        coverage_pct = (summary['users_with_budget'] / summary['total_users'] * 100) if summary['total_users'] > 0 else 0
        st.metric(
            "📈 Couverture",
            f"{coverage_pct:.1f}%",
            help="Pourcentage d'utilisateurs avec budget"
        )
    
    # Répartition par rôle
    if summary['by_role']:
        st.markdown("#### 📋 Répartition par Rôle")
        
        for role_data in summary['by_role']:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{role_data['role'].upper()}**")
            with col2:
                st.write(f"{role_data['user_count']} utilisateur(s)")
            with col3:
                st.write(f"{role_data['total_budget']:,.0f}€")
    
    # Liste des utilisateurs avec budgets
    budgets = UserBudgetModel.get_all_budgets_for_year(fiscal_year)
    
    if budgets:
        st.markdown("#### 👥 Utilisateurs avec Budget")
        
        for budget in budgets:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{budget['prenom']} {budget['nom']}** ({budget['role']})")
                st.caption(f"📧 {budget['email']} • 🌍 {budget.get('region', 'N/A')}")
            
            with col2:
                st.write(f"{budget['allocated_budget']:,.0f}€")
            
            with col3:
                consumption = UserBudgetModel.get_budget_consumption(budget['user_id'], fiscal_year)
                st.write(f"{consumption['consumption_rate']:.1f}%")
            
            with col4:
                if st.button("✏️", key=f"edit_budget_{budget['user_id']}", help="Modifier le budget"):
                    st.session_state[f'edit_budget_user_{budget['user_id']}'] = True
                    st.rerun()

def _display_budget_assignment(fiscal_year, annee_fiscale_options):
    """Affiche l'interface d'attribution des budgets"""
    st.markdown("### 👥 Attribution des Budgets")
    
    # Sélection du mode
    mode = st.radio(
        "Mode d'attribution",
        ["Attribution individuelle", "Attribution en lot", "Copie année précédente"],
        horizontal=True
    )
    
    if mode == "Attribution individuelle":
        _display_individual_assignment(fiscal_year)
    elif mode == "Attribution en lot":
        _display_bulk_assignment(fiscal_year)
    else:
        _display_copy_previous_year(fiscal_year, annee_fiscale_options)

def _display_individual_assignment(fiscal_year):
    """Attribution individuelle de budget"""
    st.markdown("#### 🎯 Attribution Individuelle")
    
    # Récupérer tous les utilisateurs actifs
    users = UserModel.get_all_users_list()
    active_users = [u for u in users if u.get('is_active', False)]
    
    if not active_users:
        st.warning("Aucun utilisateur actif trouvé")
        return
    
    with st.form("individual_budget_form"):
        # Sélection utilisateur
        user_options = [(u['id'], f"{u['prenom']} {u['nom']} ({u['role']}) - {u['email']}") for u in active_users]
        selected_user_id = st.selectbox(
            "👤 Sélectionner un utilisateur",
            options=[opt[0] for opt in user_options],
            format_func=lambda x: next((opt[1] for opt in user_options if opt[0] == x), ""),
            help="Choisissez l'utilisateur à qui attribuer un budget"
        )
        
        # Montant du budget
        budget_amount = st.number_input(
            "💰 Montant du budget (€)",
            min_value=0.0,
            step=1000.0,
            value=50000.0,
            help="Montant en euros à allouer"
        )
        
        # Vérifier si l'utilisateur a déjà un budget
        existing_budget = UserBudgetModel.get_user_budget(selected_user_id, fiscal_year)
        if existing_budget:
            st.warning(f"⚠️ Cet utilisateur a déjà un budget de {existing_budget['allocated_budget']:,.0f}€ pour {fiscal_year}")
            st.info("L'attribution remplacera le budget existant")
        
        submitted = st.form_submit_button("💾 Attribuer le Budget", type="primary")
        
        if submitted:
            success = UserBudgetModel.create_budget(selected_user_id, fiscal_year, budget_amount)
            
            if success:
                st.success(f"✅ Budget de {budget_amount:,.0f}€ attribué avec succès !")
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'attribution du budget")

def _display_bulk_assignment(fiscal_year):
    """Attribution en lot de budgets"""
    st.markdown("#### 📊 Attribution en Lot")
    
    # Récupérer tous les utilisateurs actifs par rôle
    users = UserModel.get_all_users_list()
    active_users = [u for u in users if u.get('is_active', False)]
    
    if not active_users:
        st.warning("Aucun utilisateur actif trouvé")
        return
    
    # Grouper par rôle
    users_by_role = {}
    for user in active_users:
        role = user['role']
        if role not in users_by_role:
            users_by_role[role] = []
        users_by_role[role].append(user)
    
    with st.form("bulk_budget_form"):
        st.markdown("**Attribution par rôle**")
        
        budgets_to_assign = []
        
        for role, role_users in users_by_role.items():
            st.markdown(f"**{role.upper()}** ({len(role_users)} utilisateur(s))")
            
            col1, col2 = st.columns(2)
            
            with col1:
                assign_role = st.checkbox(f"Attribuer budget aux {role}", key=f"assign_{role}")
            
            with col2:
                if assign_role:
                    role_budget = st.number_input(
                        f"Budget pour {role} (€)",
                        min_value=0.0,
                        step=1000.0,
                        value=30000.0 if role == 'tc' else 50000.0,
                        key=f"budget_{role}"
                    )
                    
                    for user in role_users:
                        budgets_to_assign.append({
                            'user_id': user['id'],
                            'fiscal_year': fiscal_year,
                            'allocated_budget': role_budget
                        })
        
        if budgets_to_assign:
            st.info(f"📊 {len(budgets_to_assign)} budget(s) seront attribué(s)")
        
        submitted = st.form_submit_button("💾 Attribuer tous les Budgets", type="primary")
        
        if submitted and budgets_to_assign:
            result = UserBudgetModel.bulk_create_budgets(budgets_to_assign)
            
            st.success(f"✅ {result['success_count']} budget(s) attribué(s) avec succès !")
            if result['error_count'] > 0:
                st.warning(f"⚠️ {result['error_count']} erreur(s) rencontrée(s)")
            
            st.rerun()

def _display_copy_previous_year(fiscal_year, annee_fiscale_options):
    """Copie des budgets de l'année précédente"""
    st.markdown("#### 📋 Copie Année Précédente")
    
    with st.form("copy_budget_form"):
        # Sélection année source
        # Filtrer les années précédentes en convertissant le format BYXX
        source_years = []
        current_year_num = byxx_to_year(fiscal_year)
        
        if current_year_num is None:
            st.error(f"❌ Format d'année fiscale invalide: {fiscal_year}")
            return
        
        for opt in annee_fiscale_options:
            source_year_num = byxx_to_year(opt[0])
            if source_year_num and source_year_num < current_year_num:
                source_years.append(opt)
        
        if not source_years:
            st.warning("Aucune année précédente disponible")
            return
        
        source_year_str = st.selectbox(
            "📅 Année source",
            options=[opt[0] for opt in source_years],
            format_func=lambda x: next((opt[1] for opt in source_years if opt[0] == x), x),
            help="Année dont copier les budgets"
        )
        # Utiliser directement la chaîne BYXX pour la source
        source_year = source_year_str
        
        # Pourcentage d'augmentation
        increase_pct = st.number_input(
            "📈 Augmentation (%)",
            min_value=-50.0,
            max_value=100.0,
            value=5.0,
            step=1.0,
            help="Pourcentage d'augmentation/diminution par rapport à l'année source"
        )
        
        # Aperçu
        source_budgets = UserBudgetModel.get_all_budgets_for_year(source_year)
        if source_budgets:
            st.info(f"📊 {len(source_budgets)} budget(s) trouvé(s) pour {source_year}")
            
            if increase_pct != 0:
                total_old = sum(b['allocated_budget'] for b in source_budgets)
                total_new = total_old * (1 + increase_pct / 100)
                st.info(f"💰 Total: {total_old:,.0f}€ → {total_new:,.0f}€")
        else:
            st.warning(f"Aucun budget trouvé pour {source_year}")
        
        submitted = st.form_submit_button("📋 Copier les Budgets", type="primary")
        
        if submitted and source_budgets:
            result = UserBudgetModel.copy_budgets_to_next_year(source_year, fiscal_year, increase_pct)
            
            st.success(f"✅ {result['success_count']} budget(s) copié(s) avec succès !")
            if result['error_count'] > 0:
                st.warning(f"⚠️ {result['error_count']} erreur(s) rencontrée(s)")
            
            st.rerun()

def _display_budget_analysis(fiscal_year):
    """Affiche l'analyse des budgets"""
    st.markdown("### 📈 Analyse des Budgets")
    
    # Récupérer toutes les données
    budgets = UserBudgetModel.get_all_budgets_for_year(fiscal_year)
    
    if not budgets:
        st.info("Aucun budget configuré pour cette année")
        return
    
    # Analyse de consommation
    st.markdown("#### 🎯 Consommation des Budgets")
    
    for budget in budgets:
        consumption = UserBudgetModel.get_budget_consumption(budget['user_id'], fiscal_year)
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{budget['prenom']} {budget['nom']}**")
        
        with col2:
            st.write(f"{consumption['allocated_budget']:,.0f}€")
        
        with col3:
            progress_color = "green" if consumption['consumption_rate'] <= 80 else "orange" if consumption['consumption_rate'] <= 100 else "red"
            st.write(f":{progress_color}[{consumption['consumption_rate']:.1f}%]")
        
        with col4:
            st.write(f"{consumption['remaining_budget']:,.0f}€")
        
        # Barre de progression
        progress = min(consumption['consumption_rate'] / 100, 1.0)
        st.progress(progress)
    
    # Graphiques d'analyse
    if len(budgets) > 1:
        st.markdown("#### 📊 Graphiques d'Analyse")
        
        # TODO: Ajouter des graphiques avec plotly
        # - Répartition des budgets par rôle
        # - Évolution de la consommation
        # - Comparaison avec l'année précédente
        
        st.info("📈 Graphiques d'analyse à venir...")
