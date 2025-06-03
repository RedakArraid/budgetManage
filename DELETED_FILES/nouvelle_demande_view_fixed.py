"""
Vue pour la création de nouvelles demandes - VERSION CORRIGÉE
Gestion améliorée des erreurs et des cas d'échec
"""
import streamlit as st
from datetime import datetime, date
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from models.dropdown_options import DropdownOptionsModel
from utils.validators import validate_montant, validate_text_field

@AuthController.require_auth
def nouvelle_demande_page():
    """Page de création d'une nouvelle demande - Version corrigée"""
    from views.components.header import display_header
    
    display_header()
    user_info = AuthController.get_current_user()
    st.subheader("➕ Nouvelle Demande")
    
    # Déterminer le type de demande selon le rôle
    if user_info['role'] == 'marketing':
        type_demande = 'marketing'
        st.info("📢 Vous créez une demande Marketing qui sera envoyée aux financiers et admins")
    else:
        type_demande = 'budget'
        st.info("💰 Vous créez une demande Budget qui suivra le workflow de validation")
    
    # Récupérer les options avec gestion d'erreur robuste
    try:
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        budget_options = get_valid_dropdown_options('budget')
        categorie_options = get_valid_dropdown_options('categorie')
        typologie_options = get_valid_dropdown_options('typologie_client')
        region_options = get_valid_dropdown_options('region')
        groupe_options = get_valid_dropdown_options('groupe_groupement')
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des options : {e}")
        budget_options = []
        categorie_options = []
        typologie_options = []
        region_options = []
        groupe_options = []
    
    # Vérifier si TOUTES les catégories critiques sont vides
    critical_categories_empty = (
        len(budget_options) == 0 and 
        len(categorie_options) == 0 and 
        len(typologie_options) == 0
    )
    
    # Afficher un avertissement si des options manquent
    missing_categories = []
    if not budget_options: missing_categories.append("Budget")
    if not categorie_options: missing_categories.append("Catégorie")
    if not typologie_options: missing_categories.append("Typologie Client")
    if not region_options: missing_categories.append("Région")
    if not groupe_options: missing_categories.append("Groupe/Groupement")
    
    if missing_categories:
        st.warning(f"⚠️ Options manquantes : {', '.join(missing_categories)}")
        
        # Bouton pour aller à la page d'initialisation
        if st.button("🔧 Initialiser les listes déroulantes automatiquement", type="primary"):
            try:
                # Tentative d'initialisation automatique
                with st.spinner("Initialisation en cours..."):
                    from models.dropdown_options import DropdownOptionsModel
                    
                    # Options par défaut optimisées
                    default_options = {
                        'budget': ['Budget Commercial', 'Budget Marketing', 'Budget Formation'],
                        'categorie': ['Animation Commerciale', 'Prospection Client', 'Formation Équipe'],
                        'typologie_client': ['Grand Compte', 'PME/ETI', 'Particulier'],
                        'region': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine'],
                        'groupe_groupement': ['Indépendant', 'Franchise', 'Groupement Achats']
                    }
                    
                    for category, options_list in default_options.items():
                        for idx, option_label in enumerate(options_list, 1):
                            try:
                                DropdownOptionsModel.add_option(
                                    category=category,
                                    label=option_label,
                                    order_index=idx,
                                    auto_normalize=True
                                )
                            except:
                                pass  # Ignore si existe déjà
                
                st.success("✅ Initialisation terminée ! Rechargement de la page...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de l'initialisation : {e}")
                st.info("💡 Contactez l'administrateur pour initialiser les listes déroulantes")
    
    # Si TOUTES les catégories critiques sont vides, proposer le mode dégradé
    if critical_categories_empty:
        st.error("⚠️ Impossible de charger les options des listes déroulantes critiques.")
        st.info("📄 Les options doivent d'abord être définies par un administrateur.")
        
        # Afficher un formulaire simplifié
        st.markdown("---")
        st.markdown("### 🛠️ Mode Dégradé - Formulaire Simplifié")
        st.warning("💡 En attendant la configuration des listes déroulantes, vous pouvez utiliser ce formulaire simplifié.")
        
        _display_simplified_form(type_demande, user_info)
        return
    
    # Formulaire complet si au moins les catégories critiques sont disponibles
    _display_full_form(
        type_demande, user_info, 
        budget_options, categorie_options, typologie_options, 
        region_options, groupe_options
    )

def _display_simplified_form(type_demande, user_info):
    """Affiche le formulaire simplifié en mode dégradé"""
    with st.form("nouvelle_demande_form_simple"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom_manifestation = st.text_input(
                "📝 Nom de la manifestation*", 
                placeholder="Ex: Salon du Marketing 2024"
            )
            client = st.text_input(
                "🏢 Client*", 
                placeholder="Ex: Entreprise ABC"
            )
            lieu = st.text_input(
                "📍 Lieu*", 
                placeholder="Ex: Paris, France"
            )
        
        with col2:
            montant = st.number_input(
                "💰 Montant (€)*", 
                min_value=0.0, 
                step=50.0,
                help="Montant en euros"
            )
            date_evenement = st.date_input(
                "📅 Date de l'événement*",
                value=date.today(),
                min_value=date.today()
            )
            urgence = st.selectbox(
                "🚨 Urgence",
                options=['normale', 'urgent', 'critique'],
                format_func=lambda x: {
                    'normale': '🟢 Normale',
                    'urgent': '🟡 Urgent',
                    'critique': '🔴 Critique'
                }[x]
            )
        
        commentaires = st.text_area(
            "💭 Commentaires", 
            placeholder="Informations complémentaires, justifications...",
            height=100
        )
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            submit_simple = st.form_submit_button(
                "📤 Créer Demande Simplifiée", 
                use_container_width=True,
                type="primary"
            )
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                from utils.session_manager import session_manager
                session_manager.set_current_page("dashboard")
                st.rerun()
    
    # Traitement du formulaire simplifié
    if submit_simple:
        _process_simplified_form(
            nom_manifestation, client, lieu, montant, date_evenement, 
            urgence, commentaires, type_demande, user_info
        )

def _display_full_form(type_demande, user_info, budget_options, categorie_options, 
                      typologie_options, region_options, groupe_options):
    """Affiche le formulaire complet"""
    with st.form("nouvelle_demande_form"):
        # 1. Listes déroulantes dynamiques
        st.markdown("### 🎯 Classification de la Demande")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Budget avec gestion d'erreur
            if budget_options:
                budget = st.selectbox(
                    "💸 Budget*", 
                    options=[opt[0] for opt in budget_options],
                    format_func=lambda x: next((opt[1] for opt in budget_options if opt[0] == x), x),
                    help="Options gérées par la page admin"
                )
            else:
                budget = st.text_input("💸 Budget* (saisie libre)", 
                                     placeholder="Ex: Budget Commercial")
            
            # Typologie avec gestion d'erreur
            if typologie_options:
                typologie_client = st.selectbox(
                    "🏷️ Typologie Client*", 
                    options=[opt[0] for opt in typologie_options],
                    format_func=lambda x: next((opt[1] for opt in typologie_options if opt[0] == x), x),
                    help="Options gérées par la page admin"
                )
            else:
                typologie_client = st.text_input("🏷️ Typologie Client* (saisie libre)",
                                                placeholder="Ex: Grand Compte")
        
        with col2:
            # Catégorie avec gestion d'erreur
            if categorie_options:
                categorie = st.selectbox(
                    "📂 Catégorie*", 
                    options=[opt[0] for opt in categorie_options],
                    format_func=lambda x: next((opt[1] for opt in categorie_options if opt[0] == x), x),
                    help="Options gérées par la page admin"
                )
            else:
                categorie = st.text_input("📂 Catégorie* (saisie libre)",
                                        placeholder="Ex: Animation Commerciale")
            
            # Région avec gestion d'erreur
            if region_options:
                region = st.selectbox(
                    "🌍 Région*", 
                    options=[opt[0] for opt in region_options],
                    format_func=lambda x: next((opt[1] for opt in region_options if opt[0] == x), x),
                    help="Options gérées par la page admin"
                )
            else:
                region = st.text_input("🌍 Région* (saisie libre)",
                                      placeholder="Ex: Île-de-France")
        
        with col3:
            # Groupe avec gestion d'erreur
            if groupe_options:
                groupe_groupement = st.selectbox(
                    "👥 Groupe/Groupement*", 
                    options=[opt[0] for opt in groupe_options],
                    format_func=lambda x: next((opt[1] for opt in groupe_options if opt[0] == x), x),
                    help="Options gérées par la page admin"
                )
            else:
                groupe_groupement = st.text_input("👥 Groupe/Groupement* (saisie libre)",
                                                 placeholder="Ex: Indépendant")
            
            # Agence - champ de saisie libre
            agence = st.text_input(
                "🏢 Agence*", 
                placeholder="Ex: Agence Paris Centre"
            )

        # 2. Champs principaux
        st.markdown("### 📋 Informations Principales")
        col1, col2 = st.columns(2)
        
        with col1:
            nom_manifestation = st.text_input(
                "📝 Nom de la manifestation*", 
                placeholder="Ex: Salon du Marketing 2024"
            )
            client = st.text_input(
                "🏢 Client*", 
                placeholder="Ex: Entreprise ABC"
            )
            date_evenement = st.date_input(
                "📅 Date de l'événement*",
                value=date.today(),
                min_value=date.today()
            )
        
        with col2:
            lieu = st.text_input(
                "📍 Lieu*", 
                placeholder="Ex: Paris, France"
            )
            montant = st.number_input(
                "💰 Montant (€)*", 
                min_value=0.0, 
                step=50.0,
                help="Montant en euros"
            )
            urgence = st.selectbox(
                "🚨 Urgence",
                options=['normale', 'urgent', 'critique'],
                format_func=lambda x: {
                    'normale': '🟢 Normale',
                    'urgent': '🟡 Urgent',
                    'critique': '🔴 Critique'
                }[x]
            )

        # 3. Gestion des participants (simplifiée pour éviter les erreurs)
        st.markdown("### 👥 Participants")
        
        demandeur_participe = st.checkbox(
            "Le demandeur participe à l'événement", 
            value=True
        )
        
        participants_libres = st.text_area(
            "Autres participants (texte libre)",
            placeholder="Noms et fonctions des autres participants...",
            height=80
        )
        
        # 4. Champs complémentaires
        st.markdown("### 📝 Informations Complémentaires")
        
        col1, col2 = st.columns(2)
        with col1:
            client_enseigne = st.text_input(
                "🏪 Client/Enseigne", 
                placeholder="Nom de l'enseigne ou client"
            )
            nom_contact = st.text_input(
                "👤 Nom Contact", 
                placeholder="Nom du contact"
            )
        
        with col2:
            mail_contact = st.text_input(
                "📧 Email Contact", 
                placeholder="contact@email.com"
            )
        
        commentaires = st.text_area(
            "💭 Commentaires", 
            placeholder="Informations complémentaires, justifications...",
            height=100
        )
        
        # Validation en temps réel
        errors = []
        if nom_manifestation and not validate_text_field(nom_manifestation, min_length=3):
            errors.append("Le nom de la manifestation doit contenir au moins 3 caractères")
        if client and not validate_text_field(client, min_length=2):
            errors.append("Le nom du client doit contenir au moins 2 caractères")
        if lieu and not validate_text_field(lieu, min_length=2):
            errors.append("Le lieu doit contenir au moins 2 caractères")
        if montant > 0 and not validate_montant(montant):
            errors.append("Le montant doit être positif et réaliste")
        
        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
        
        # Actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_draft = st.form_submit_button(
                "💾 Sauvegarder Brouillon", 
                use_container_width=True,
                help="Sauvegarder sans soumettre"
            )
        
        with col2:
            submit_btn = st.form_submit_button(
                "📤 Soumettre", 
                use_container_width=True,
                type="primary",
                help="Soumettre pour validation"
            )
        
        with col3:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                from utils.session_manager import session_manager
                session_manager.set_current_page("dashboard")
                st.rerun()
    
    # Traitement du formulaire complet
    if save_draft or submit_btn:
        _process_full_form(
            nom_manifestation, client, lieu, montant, date_evenement,
            urgence, commentaires, type_demande, user_info,
            budget, categorie, typologie_client, region, groupe_groupement, agence,
            client_enseigne, mail_contact, nom_contact,
            demandeur_participe, participants_libres,
            save_draft, submit_btn, errors
        )

def _process_simplified_form(nom_manifestation, client, lieu, montant, date_evenement, 
                           urgence, commentaires, type_demande, user_info):
    """Traite le formulaire simplifié"""
    if not nom_manifestation or not client or not lieu or montant <= 0:
        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
        return
    
    with st.spinner("Création de la demande simplifiée en cours..."):
        try:
            success, demande_id = DemandeController.create_demande(
                user_id=AuthController.get_current_user_id(),
                type_demande=type_demande,
                nom_manifestation=nom_manifestation,
                client=client,
                date_evenement=date_evenement.strftime('%Y-%m-%d'),
                lieu=lieu,
                montant=montant,
                participants="",
                commentaires=commentaires,
                urgence=urgence,
                # Valeurs par défaut pour les champs manquants
                budget="non_defini",
                categorie="non_defini",
                typologie_client="non_defini",
                groupe_groupement="non_defini",
                region=user_info.get('region', 'non_defini'),
                agence="non_defini",
                client_enseigne="",
                mail_contact="",
                nom_contact="",
                demandeur_participe=True,
                participants_libres="",
                selected_participants=[]
            )
            
            if success:
                st.success("✅ Demande simplifiée créée avec succès!")
                st.info("💡 Cette demande pourra être complétée plus tard quand les listes déroulantes seront configurées.")
                st.balloons()
                
                if st.button("← Retour au tableau de bord", type="secondary"):
                    from utils.session_manager import session_manager
                    session_manager.set_current_page("dashboard")
                    st.rerun()
            else:
                st.error("❌ Erreur lors de la création de la demande")
                
        except Exception as e:
            st.error(f"❌ Erreur: {e}")

def _process_full_form(nom_manifestation, client, lieu, montant, date_evenement,
                      urgence, commentaires, type_demande, user_info,
                      budget, categorie, typologie_client, region, groupe_groupement, agence,
                      client_enseigne, mail_contact, nom_contact,
                      demandeur_participe, participants_libres,
                      save_draft, submit_btn, errors):
    """Traite le formulaire complet"""
    # Validation des champs obligatoires
    required_fields = {
        'nom_manifestation': nom_manifestation,
        'client': client,
        'lieu': lieu,
        'montant': montant,
        'budget': budget,
        'categorie': categorie,
        'typologie_client': typologie_client,
        'agence': agence
    }
    
    missing_fields = [name for name, value in required_fields.items() 
                     if not value or (name == 'montant' and value <= 0)]
    
    if missing_fields:
        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
        return
    
    if errors:
        st.error("⚠️ Veuillez corriger les erreurs avant de continuer")
        return
    
    # Créer la demande
    with st.spinner("Création de la demande en cours..."):
        try:
            success, demande_id = DemandeController.create_demande(
                user_id=AuthController.get_current_user_id(),
                type_demande=type_demande,
                nom_manifestation=nom_manifestation,
                client=client,
                date_evenement=date_evenement.strftime('%Y-%m-%d'),
                lieu=lieu,
                montant=montant,
                participants="",  # Ancien champ gardé pour compatibilité
                commentaires=commentaires,
                urgence=urgence,
                budget=budget,
                categorie=categorie,
                typologie_client=typologie_client,
                groupe_groupement=groupe_groupement,
                region=region or user_info.get('region', 'non_defini'),
                agence=agence,
                client_enseigne=client_enseigne,
                mail_contact=mail_contact,
                nom_contact=nom_contact,
                demandeur_participe=demandeur_participe,
                participants_libres=participants_libres,
                selected_participants=[]  # Simplifié pour éviter les erreurs
            )
        
            if success:
                if submit_btn:
                    # Soumettre immédiatement
                    with st.spinner("Soumission de la demande en cours..."):
                        submit_success, submit_message = DemandeController.submit_demande(
                            demande_id, AuthController.get_current_user_id()
                        )
                    
                    if submit_success:
                        st.success("✅ Demande créée et soumise avec succès!")
                        st.balloons()
                        _display_success_summary(demande_id, nom_manifestation, montant, type_demande)
                    else:
                        st.error(f"❌ Erreur lors de la soumission: {submit_message}")
                else:
                    st.success("✅ Demande sauvegardée en brouillon!")
                    st.info("💡 Vous pouvez la modifier et la soumettre plus tard depuis la page 'Mes Demandes'")
                
                # Bouton pour retourner au tableau de bord
                if st.button("← Retour au tableau de bord", type="secondary"):
                    from utils.session_manager import session_manager
                    session_manager.set_current_page("dashboard")
                    st.rerun()
            else:
                st.error("❌ Erreur lors de la création de la demande")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la création de la demande: {e}")
            st.info("💡 Vérifiez que tous les services sont disponibles et réessayez")

def _display_success_summary(demande_id: int, nom_manifestation: str, montant: float, type_demande: str):
    """Affiche un résumé de la demande créée"""
    st.markdown("---")
    st.subheader("📋 Résumé de la demande")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📝 Détails:**
        - **ID:** #{demande_id}
        - **Manifestation:** {nom_manifestation}
        - **Montant:** {montant:,.0f}€
        - **Type:** {type_demande.title()}
        """)
    
    with col2:
        if type_demande == 'budget':
            st.markdown("""
            **📋 Prochaines étapes:**
            1. ⏳ Validation par le Directeur Régional
            2. 💰 Validation financière
            3. ✅ Demande validée
            """)
        else:
            st.markdown("""
            **📋 Prochaines étapes:**
            1. 💰 Validation financière directe
            2. ✅ Demande validée
            """)
