"""
Vue pour la page de validations
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from config.settings import get_status_info
from utils.date_utils import format_date
from models.user import UserModel

@AuthController.require_role(['dr', 'dr_financier', 'dg'])
def validations_page():
    """Page de validation des demandes"""
    from views.components.header import display_header
    
    display_header()
    user_info = AuthController.get_current_user()
    
    st.subheader("✅ Validations en Attente")
    
    # Récupérer les demandes en attente de validation
    demandes_en_attente = _get_demandes_validation(user_info)
    
    if demandes_en_attente.empty:
        st.info("🎉 Aucune demande en attente de validation")
        _display_validation_stats(user_info)
        return
    
    # Statistiques de validation
    _display_validation_overview(demandes_en_attente, user_info)
    
    # Filtres
    try:
        from views.components.validation_filters import display_validation_filters, apply_validation_filters
        display_validation_filters()
        
        # Appliquer les filtres
        if not demandes_en_attente.empty:
            demandes_en_attente = apply_validation_filters(demandes_en_attente)
            
    except ImportError:
        # Fallback vers l'ancienne méthode
        _display_validation_filters()
    
    # Affichage des demandes à valider
    _display_pending_validations(demandes_en_attente, user_info)
    
    # Historique des validations récentes
    _display_recent_validations(user_info)

def _get_demandes_validation(user_info):
    """Récupère les demandes en attente selon le rôle"""
    user_id = AuthController.get_current_user_id()
    role = user_info['role']
    
    # Get fiscal year filter from session state
    fiscal_year_filter = st.session_state.get('validation_fiscal_year_filter', 'Tous')
    # Convert to int or None for the controller
    fiscal_year_param = int(fiscal_year_filter) if fiscal_year_filter != 'Tous' else None
    
    if role == 'dr':
        # DR voit les demandes en attente DR de son équipe
        return DemandeController.get_demandes_for_user(
            user_id,
            role,
            status_filter='en_attente_dr',
            fiscal_year=fiscal_year_param
        )
    elif role in ['dr_financier', 'dg']:
        # Financiers voient toutes les demandes en attente financière
        return DemandeController.get_demandes_for_user(
            user_id, 
            role, 
            status_filter='en_attente_financier',
            fiscal_year=fiscal_year_param
        )
    
    return pd.DataFrame()

def _display_validation_overview(demandes, user_info):
    """Affiche un aperçu des validations"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_demandes = len(demandes)
    total_montant = demandes['montant'].sum()
    urgent_count = len(demandes[demandes.get('urgence', 'normale') == 'urgent'])
    critique_count = len(demandes[demandes.get('urgence', 'normale') == 'critique'])
    
    with col1:
        st.metric("À Valider", total_demandes)
    with col2:
        st.metric("Montant Total", f"{total_montant:,.0f}€")
    with col3:
        st.metric("Urgent", urgent_count, delta_color="off")
    with col4:
        st.metric("Critique", critique_count, delta_color="inverse")
    
    # Alertes pour les demandes urgentes
    if critique_count > 0:
        st.error(f"🚨 {critique_count} demande(s) critique(s) en attente!")
    elif urgent_count > 0:
        st.warning(f"🟡 {urgent_count} demande(s) urgente(s) en attente")

def _display_validation_filters():
    """Affiche les filtres pour les validations"""
    # Initialiser les filtres de validation
    if 'validation_search_query' not in st.session_state:
        st.session_state.validation_search_query = ''
    if 'validation_urgence_filter' not in st.session_state:
        st.session_state.validation_urgence_filter = 'toutes'
    if 'validation_montant_filter' not in st.session_state:
        st.session_state.validation_montant_filter = 'tous'
    if 'validation_type_filter' not in st.session_state:
        st.session_state.validation_type_filter = 'tous'
    # Initialize fiscal year filter
    current_year = datetime.now().year
    # Generate a list of fiscal years (e.g., past 5 years, current year, next 5 years)
    fiscal_years_options = ['Tous'] + list(range(current_year - 5, current_year + 6))
    if 'validation_fiscal_year_filter' not in st.session_state:
        st.session_state.validation_fiscal_year_filter = 'Tous'

    with st.expander("🔍 Filtres", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5) # Added one more column for fiscal year

        with col1:
            search = st.text_input(
                "Rechercher", 
                value=st.session_state.validation_search_query,
                placeholder="Nom, client, lieu...",
                key="validation_search_input"
            )
            if search != st.session_state.validation_search_query:
                st.session_state.validation_search_query = search

        with col2:
            urgence_options = ['toutes', 'normale', 'urgent', 'critique']
            urgence_filter = st.selectbox(
                "Urgence",
                options=urgence_options,
                index=urgence_options.index(st.session_state.validation_urgence_filter),
                key="validation_urgence_select"
            )
            if urgence_filter != st.session_state.validation_urgence_filter:
                st.session_state.validation_urgence_filter = urgence_filter

        with col3:
            montant_options = {
                'tous': 'Tous montants',
                'moins_1000': '< 1 000€',
                '1000_5000': '1 000 - 5 000€',
                'plus_5000': '> 5 000€'
            }
            montant_filter = st.selectbox(
                "Montant",
                options=list(montant_options.keys()),
                index=list(montant_options.keys()).index(st.session_state.validation_montant_filter),
                format_func=lambda x: montant_options[x],
                key="validation_montant_select"
            )
            if montant_filter != st.session_state.validation_montant_filter:
                st.session_state.validation_montant_filter = montant_filter

        with col4:
            type_options = {
                'tous': 'Tous types',
                'budget': 'Budget',
                'marketing': 'Marketing'
            }
            type_filter = st.selectbox(
                "Type", 
                options=list(type_options.keys()),
                index=list(type_options.keys()).index(st.session_state.validation_type_filter),
                format_func=lambda x: type_options[x],
                key="validation_type_select"
            )
            if type_filter != st.session_state.validation_type_filter:
                st.session_state.validation_type_filter = type_filter

        with col5:
             # Fiscal Year Filter
            fiscal_year_filter = st.selectbox(
                "Année Fiscale",
                options=fiscal_years_options,
                index=fiscal_years_options.index(st.session_state.validation_fiscal_year_filter),
                key='validation_fiscal_year_select'
            )
             # Mettre à jour la session state
            if fiscal_year_filter != st.session_state.validation_fiscal_year_filter:
                st.session_state.validation_fiscal_year_filter = fiscal_year_filter

    # Boutons d'action pour les filtres
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualiser Validations", use_container_width=True, key="validations_refresh"):
            st.rerun()
    with col2:
        if st.button("🗑️ Effacer Filtres", use_container_width=True, key="validations_clear_filters"):
            st.session_state.validation_search_query = ''
            st.session_state.validation_urgence_filter = 'toutes'
            st.session_state.validation_montant_filter = 'tous'
            st.session_state.validation_type_filter = 'tous'
            st.session_state.validation_fiscal_year_filter = 'Tous'
            st.rerun()

def _display_pending_validations(demandes, user_info):
    """Affiche les demandes en attente de validation"""
    st.markdown("### 📋 Demandes à Valider")
    
    # Appliquer les filtres de validation
    filtered_demandes = _apply_validation_filters(demandes)
    
    if filtered_demandes.empty:
        st.info("🎉 Aucune demande correspondant aux filtres")
        return
    
    # Trier par urgence puis par date
    urgence_order = {'critique': 0, 'urgent': 1, 'normale': 2}
    filtered_demandes['urgence_order'] = filtered_demandes.get('urgence', 'normale').map(urgence_order)
    filtered_demandes = filtered_demandes.sort_values(['urgence_order', 'created_at'])
    
    # Afficher le nombre de résultats
    if len(filtered_demandes) != len(demandes):
        st.info(f"🔍 {len(filtered_demandes)} demande(s) sur {len(demandes)} après filtrage")
    
    for idx, row in filtered_demandes.iterrows():
        _display_validation_card(row, user_info)

def _apply_validation_filters(demandes):
    """Applique les filtres aux demandes de validation"""
    filtered_demandes = demandes.copy()
    
    # Filtre par recherche textuelle
    search_query = st.session_state.get('validation_search_query', '')
    if search_query:
        search_query = search_query.lower()
        mask = (
            filtered_demandes['nom_manifestation'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes['client'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes['lieu'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('prenom', '').astype(str).str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('nom', '').astype(str).str.lower().str.contains(search_query, na=False)
        )
        filtered_demandes = filtered_demandes[mask]
    
    # Filtre par urgence
    urgence_filter = st.session_state.get('validation_urgence_filter', 'toutes')
    if urgence_filter != 'toutes':
        filtered_demandes = filtered_demandes[
            filtered_demandes.get('urgence', 'normale') == urgence_filter
        ]
    
    # Filtre par montant
    montant_filter = st.session_state.get('validation_montant_filter', 'tous')
    if montant_filter != 'tous':
        if montant_filter == 'moins_1000':
            filtered_demandes = filtered_demandes[filtered_demandes['montant'] < 1000]
        elif montant_filter == '1000_5000':
            filtered_demandes = filtered_demandes[
                (filtered_demandes['montant'] >= 1000) & (filtered_demandes['montant'] <= 5000)
            ]
        elif montant_filter == 'plus_5000':
            filtered_demandes = filtered_demandes[filtered_demandes['montant'] > 5000]
    
    # Filtre par type
    type_filter = st.session_state.get('validation_type_filter', 'tous')
    if type_filter != 'tous':
        filtered_demandes = filtered_demandes[
            filtered_demandes.get('type_demande', '') == type_filter
        ]
    
    return filtered_demandes

def _display_validation_card(row, user_info):
    """Affiche une carte de validation pour une demande (maintenant un expander)"""
    urgence_colors = {
        'normale': '🟢',
        'urgent': '🟡', 
        'critique': '🔴'
    }

    # Préparer les informations pour l'en-tête de l'expander
    urgence = row.get('urgence', 'normale')
    urgence_icon = urgence_colors[urgence]
    header_text = f"{urgence_icon} {row['nom_manifestation']} - {row['montant']:,.0f}€"

    # Remplacer st.container par st.expander
    with st.expander(header_text):
        # Supprimer le contenu précédent du container et ajouter les détails complets
        col1, col2 = st.columns(2) # Utiliser deux colonnes pour organiser les détails

        with col1:
            # Récupérer les labels d'affichage pour les options
            try:
                from utils.dropdown_display import DropdownDisplayUtils
                display_labels = DropdownDisplayUtils.get_display_labels_for_demande(row)
            except ImportError:
                # Fallback vers les valeurs brutes si l'utilitaire n'est pas disponible
                display_labels = {
                    'budget': row.get('budget', 'N/A'),
                    'categorie': row.get('categorie', 'N/A'),
                    'typologie_client': row.get('typologie_client', 'N/A'),
                    'groupe_groupement': row.get('groupe_groupement', 'N/A'),
                    'region': row.get('region', 'N/A')
                }
            
            st.markdown("**📝 Détails:**")
            st.markdown(f"- **Type:** {row.get('type_demande','N/A').title()}")
            st.markdown(f"- **Budget:** {display_labels['budget']}")
            st.markdown(f"- **Catégorie:** {display_labels['categorie']}")
            st.markdown(f"- **Typologie Client:** {display_labels['typologie_client']}")
            st.markdown(f"- **Groupe/Groupement:** {display_labels['groupe_groupement']}")
            st.markdown(f"- **Région:** {display_labels['region']}")
            st.markdown(f"- **Agence:** {row.get('agence','N/A')}")
            st.markdown(f"- **Client/Enseigne:** {row.get('client_enseigne','N/A')}")
            st.markdown(f"- **Email Contact:** {row.get('mail_contact','N/A')}")
            st.markdown(f"- **Nom Contact:** {row.get('nom_contact','N/A')}")
            st.markdown(f"- **Client:** {row.get('client','N/A')}") # Répété pour clarté si différent de client_enseigne
            st.markdown(f"- **Date événement:** {format_date(row.get('date_evenement'))}")
            st.markdown(f"- **Lieu:** {row.get('lieu','N/A')}")
            st.markdown(f"- **Montant:** {row.get('montant', 0.0):,.0f}€")
            
            # Afficher les participants améliorés
            try:
                from views.components.participants_selector import get_participants_display_text
                participants_text = get_participants_display_text(
                    row['id'], 
                    {'prenom': row.get('prenom', 'N/A'), 'nom': row.get('nom', 'N/A'), 'role': row.get('user_role', 'tc')},
                    row.get('demandeur_participe', True),
                    row.get('participants_libres', '')
                )
                if participants_text and participants_text != "Aucun participant":
                    st.markdown(f"- **Participants:** {participants_text}")
            except ImportError:
                # Fallback vers l'ancien affichage
                if row.get('participants'):
                    st.markdown(f"- **Participants:** {row.get('participants','N/A')}")

        with col2:
            st.markdown("**👤 Informations:**")
            st.markdown(f"- **Demandeur:** {row.get('prenom','N/A')} {row.get('nom','N/A')}")
            st.markdown(f"- **Email Demandeur:** {row.get('email','N/A')}") # Utiliser 'email' du JOIN
            st.markdown(f"- **Rôle Demandeur:** {row.get('user_role','N/A')}") # Utiliser 'user_role' du JOIN
            st.markdown(f"- **Statut:** {get_status_info(row.get('status','N/A'))['label']}")
            st.markdown(f"- **Année Fiscale:** {row.get('by', 'N/A')}") # Display BYNN format
            st.markdown(f"- **Urgence:** {row.get('urgence','normale').title()}")
            st.markdown(f"- **Créée le:** {format_date(row.get('created_at'))}")
            st.markdown(f"- **Modifiée le:** {format_date(row.get('updated_at'))}")

            # --- Statut Validations: DR, Financier, DG ---
            st.markdown("**Statut Validations:**")
            from models.user import UserModel # Importer ici pour éviter les dépendances circulaires
            import pandas as pd # Importer pandas pour isna

            # Statut DR
            dr_validated_id = row.get('valideur_dr_id')
            dr_status_text = "⏳ En attente DR"
            if dr_validated_id is not None and isinstance(dr_validated_id, (int, float)) and not pd.isna(dr_validated_id):
                 dr_validated_id = int(dr_validated_id)
                 dr_validator = UserModel.get_user_by_id(dr_validated_id)
                 if dr_validator:
                      dr_status_text = f"✅ Validé par {dr_validator.get('prenom', '')} {dr_validator.get('nom', '')} : {format_date(row.get('date_validation_dr'))}"
                 else:
                      dr_status_text = f"✅ Validé par inconnu : {format_date(row.get('date_validation_dr'))}"

            st.markdown(f"- {dr_status_text}")

            # Statut Financier
            fin_validated_id = row.get('valideur_financier_id')
            fin_status_text = "⏳ En attente Financier"
            if fin_validated_id is not None and isinstance(fin_validated_id, (int, float)) and not pd.isna(fin_validated_id):
                 fin_validated_id = int(fin_validated_id)
                 fin_validator = UserModel.get_user_by_id(fin_validated_id)
                 if fin_validator:
                      fin_status_text = f"✅ Validé par {fin_validator.get('prenom', '')} {fin_validator.get('nom', '')} : {format_date(row.get('date_validation_financier'))}"
                 else:
                      fin_status_text = f"✅ Validé par inconnu : {format_date(row.get('date_validation_financier'))}"
            st.markdown(f"- {fin_status_text}")

            # Statut DG
            dg_validated_id = row.get('valideur_dg_id')
            dg_status_text = "⏳ En attente DG"
            if dg_validated_id is not None and isinstance(dg_validated_id, (int, float)) and not pd.isna(dg_validated_id):
                dg_validated_id = int(dg_validated_id)
                dg_validator = UserModel.get_user_by_id(dg_validated_id)
                if dg_validator:
                     dg_status_text = f"✅ Validé par {dg_validator.get('prenom', '')} {dg_validator.get('nom', '')} : {format_date(row.get('date_validation_dg'))}"
                else:
                     dg_status_text = f"✅ Validé par inconnu : {format_date(row.get('date_validation_dg'))}"

            st.markdown(f"- {dg_status_text}")

            # Commentaires généraux sous les colonnes
            if row.get('commentaires'):
                st.markdown("**💭 Commentaires Généraux:**")
                st.markdown(row.get('commentaires'))

            st.markdown("---") # Séparateur avant les actions

            # Actions disponibles (maintenant à l'intérieur de l'expander)
            _display_validation_actions(row, user_info)

def _display_validation_actions(row, user_info):
    """Affiche les actions de validation - Version corrigée"""
    role = user_info['role']
    demande_id = row['id']
    
    # Debug: Afficher le rôle perçu par cette fonction pour cette demande
    print(f"[DEBUG] _display_validation_actions - Demande ID: {demande_id}, Perceived Role: {role}, Demande Status: {row['status']}")
    
    # Debug info pour diagnostiquer les problèmes
    if st.checkbox(f"Debug demande {demande_id}", key=f"debug_{demande_id}"):
        st.write(f"🔍 DEBUG - Rôle: {role}, Demande ID: {demande_id}, Statut: {row['status']}")
        st.write(f"🔍 DEBUG - Current User ID: {user_info.get('id')}")
        st.write(f"🔍 DEBUG - Valideur Financier: {row.get('valideur_financier_id')}")
        st.write(f"🔍 DEBUG - Valideur DG: {row.get('valideur_dg_id')}")
    
    if role == 'dr' and row['status'] == 'en_attente_dr':
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Valider", key=f"val_dr_{demande_id}", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Validation DR en cours..."):
                        success, message = DemandeController.validate_demande(
                            demande_id, 
                            AuthController.get_current_user_id(), 
                            'valider', 
                            "Validation par le DR"
                        )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"❌ Erreur validation DR: {e}")
        
        with col2:
            if st.button("❌ Rejeter", key=f"rej_dr_{demande_id}", use_container_width=True):
                motif = st.text_input("Motif du rejet:", key=f"motif_dr_{demande_id}")
                if motif:
                    try:
                        with st.spinner("Rejet DR en cours..."):
                            success, message = DemandeController.validate_demande(
                                demande_id, 
                                AuthController.get_current_user_id(), 
                                'rejeter', 
                                motif
                            )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur rejet DR: {e}")
    
    elif role in ['dr_financier', 'dg'] and row['status'] == 'en_attente_financier':
        current_user_id = user_info['id']
        
        # Vérifier si l'utilisateur actuel a déjà validé
        has_current_user_validated = False
        if role == 'dr_financier' and row.get('valideur_financier_id') == current_user_id:
            has_current_user_validated = True
        elif role == 'dg' and row.get('valideur_dg_id') == current_user_id:
            has_current_user_validated = True
        
        # Utiliser un formulaire simple pour éviter les problèmes de session
        st.markdown(f"**Validation {role.upper()}**")
        
        # Zone de commentaire
        commentaire_key = f"comment_{role}_{demande_id}"
        commentaire = st.text_area(
            "Commentaire:",
            placeholder="Votre commentaire...",
            key=commentaire_key
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if has_current_user_validated:
                st.info("✅ Vous avez déjà validé cette demande.")
            else:
                if st.button(f"✅ Valider ({role})", key=f"val_fin_{demande_id}", use_container_width=True, type="primary"):
                    try:
                        # Debug: Vérifier si le bouton Valider Financier/DG est cliqué
                        print(f"[DEBUG] Valider ({role}) button clicked for demande {demande_id}")
                        # Debug: Marquer que le bouton a été cliqué
                        st.session_state[f'val_fin_{demande_id}_clicked'] = True
                        
                        with st.spinner(f"Validation {role} en cours..."):
                            success, message = DemandeController.validate_demande(
                                demande_id, 
                                current_user_id, 
                                'valider', 
                                commentaire or f"Validation par {role}"
                            )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur validation {role}: {e}")
                        # Affichage de debug en cas d'erreur
                        import traceback
                        with st.expander("Détails de l'erreur"):
                            st.code(traceback.format_exc())
        
        with col2:
            if st.button(f"❌ Rejeter ({role})", key=f"rej_fin_{demande_id}", use_container_width=True):
                if not commentaire.strip():
                    st.error("Un motif de rejet est obligatoire")
                else:
                    try:
                        with st.spinner(f"Rejet {role} en cours..."):
                            success, message = DemandeController.validate_demande(
                                demande_id, 
                                current_user_id, 
                                'rejeter', 
                                commentaire
                            )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur rejet {role}: {e}")
        
        # Affichage du statut de validation combinée pour DF/DG
        st.markdown("**Statut de la double validation Financier/DG :**")
        
        # Vérifier si chaque partie a validé
        dr_fin_validated = row.get('valideur_financier_id') is not None
        dg_validated = row.get('valideur_dg_id') is not None
        
        col1, col2 = st.columns(2)
        with col1:
            fin_status = "✅ Validé" if dr_fin_validated else "⏳ En attente"
            st.markdown(f"- **Financier:** {fin_status}")
        with col2:
            dg_status = "✅ Validé" if dg_validated else "⏳ En attente"
            st.markdown(f"- **DG:** {dg_status}")
        
        # Messages informatifs
        if role == 'dr_financier' and dg_validated and not dr_fin_validated:
            st.info("Le DG a déjà validé. Votre validation finalisera l'approbation.")
        elif role == 'dg' and dr_fin_validated and not dg_validated:
            st.info("Le Financier a déjà validé. Votre validation finalisera l'approbation.")
        elif dr_fin_validated and dg_validated:
            st.success("Les deux parties ont validé. Demande approuvée !")

# Fonctions de gestion simplifiée - Version corrigée
# Les anciennes fonctions de dialog complexes ont été remplacées par des actions directes

def _display_recent_validations(user_info):
    """Affiche l'historique des validations récentes"""
    st.markdown("---")
    st.markdown("### 📊 Validations Récentes")
    
    # Utiliser get_demandes_for_user et filtrer par statuts validés ou rejetés
    all_demandes = DemandeController.get_demandes_for_user(
        AuthController.get_current_user_id(),
        user_info['role']
    )

    if not all_demandes.empty:
        # Filtrer les demandes qui sont validées ou rejetées
        recent_validations = all_demandes[all_demandes['status'].isin(['validee', 'rejetee'])]

        if not recent_validations.empty:
            # Trier par date de mise à jour pour avoir les plus récentes
            recent_validations = recent_validations.sort_values('updated_at', ascending=False)

            for idx, row in recent_validations.head(5).iterrows():
                status_info = get_status_info(row['status'])
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{row['nom_manifestation']}** - {row['client']}")
                with col2:
                    st.markdown(f"{status_info['icon']} {status_info['label']}")
                with col3:
                    st.markdown(f"{row['montant']:,.0f}€")
    else:
        st.info("Aucune validation récente")

def _display_validation_stats(user_info):
    """Affiche les statistiques de validation quand il n'y a rien à valider"""
    st.markdown("### 📊 Statistiques de Validation")
    
    stats = DemandeController.get_validation_stats(
        AuthController.get_current_user_id(),
        user_info['role']
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Validées", stats.get('total_validees', 0))
    with col2:
        st.metric("Ce Mois", stats.get('ce_mois', 0))
    with col3:
        st.metric("Montant Validé", f"{stats.get('montant_valide', 0):,.0f}€")
    with col4:
        st.metric("Temps Moyen", f"{stats.get('temps_moyen', 0):.1f}h")

# Version simplifiée - Plus de gestion complexe des formulaires de validation
# Tout est géré directement dans _display_validation_actions
