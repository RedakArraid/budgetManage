"""
Vue pour la création de nouvelles demandes - Version Sans Boucle Infinie
"""
import streamlit as st
from datetime import datetime, date
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from models.dropdown_options import DropdownOptionsModel
from utils.validators import validate_montant, validate_text_field

@AuthController.require_auth
def nouvelle_demande_page():
    """Page de création d'une nouvelle demande"""
    from views.components.header import display_header
    
    display_header()
    user_info = AuthController.get_current_user()
    st.subheader("➕ Nouvelle Demande")
    
    # 🔧 CORRECTION BOUCLE INFINIE: Vérifier si on revient d'une création réussie
    if st.session_state.get('demande_creation_success', False):
        # Afficher le message de succès UNE SEULE FOIS
        demande_id = st.session_state.get('last_created_demande_id')
        nom_manifestation = st.session_state.get('last_created_demande_nom', 'N/A')
        montant = st.session_state.get('last_created_demande_montant', 0)
        type_demande = st.session_state.get('last_created_demande_type', 'budget')
        
        st.success("✅ Demande créée avec succès !")
        st.balloons()
        
        # Afficher le résumé
        _display_success_summary(demande_id, nom_manifestation, montant, type_demande)
        
        # Navigation après succès
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Voir mes demandes", type="primary", use_container_width=True, key="btn_voir_demandes"):
                # Nettoyer TOUS les états avant navigation
                _clear_creation_state()
                st.session_state.page = "demandes"
                st.rerun()
        
        with col2:
            if st.button("🏠 Tableau de bord", use_container_width=True, key="btn_dashboard"):
                # Nettoyer TOUS les états avant navigation
                _clear_creation_state()
                st.session_state.page = "dashboard"
                st.rerun()
        
        # Option pour créer une nouvelle demande
        st.markdown("---")
        if st.button("➕ Créer une nouvelle demande", type="secondary", use_container_width=True, key="btn_nouvelle"):
            # Nettoyer les états pour permettre une nouvelle création
            _clear_creation_state()
            st.rerun()
        
        return  # 🔧 CRITIQUE: Sortir ici pour éviter d'afficher le formulaire
    
    # Déterminer le type de demande selon le rôle
    if user_info['role'] == 'marketing':
        type_demande = 'marketing'
        st.info("📢 Vous créez une demande Marketing qui sera envoyée aux financiers et admins")
    else:
        type_demande = 'budget'
        st.info("💰 Vous créez une demande Budget qui suivra le workflow de validation")
    
    # Récupérer les options depuis la table dropdown_options
    from views.admin_dropdown_options_view import get_valid_dropdown_options
    
    budget_options = get_valid_dropdown_options('budget')
    categorie_options = get_valid_dropdown_options('categorie')
    typologie_options = get_valid_dropdown_options('typologie_client')
    region_options = get_valid_dropdown_options('region')
    groupe_options = get_valid_dropdown_options('groupe_groupement')
    annee_fiscale_options = get_valid_dropdown_options('annee_fiscale')
    
    # Vérifier si les options sont disponibles
    if not budget_options and not categorie_options:
        st.error("⚠️ Impossible de charger les options des listes déroulantes. Contactez l'administrateur.")
        st.info("📄 Les options doivent d'abord être définies dans la page 'Listes Déroulantes' par un administrateur.")
        
        # Formulaire simplifié
        _display_simplified_form(type_demande, user_info)
        return
    
    # Formulaire complet
    _display_full_form(type_demande, user_info, budget_options, categorie_options, 
    typologie_options, region_options, groupe_options, annee_fiscale_options)

def _clear_creation_state():
    """Nettoie complètement l'état de création"""
    keys_to_clear = [
        'demande_creation_success', 'last_created_demande_id', 'last_created_demande_nom',
        'last_created_demande_montant', 'last_created_demande_type',
        'demande_created', 'created_demande_id', 'created_demande_nom', 
        'created_demande_montant', 'created_demande_type'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def _set_creation_success(demande_id, nom_manifestation, montant, type_demande):
    """Marque une création comme réussie"""
    # Nettoyer d'abord les anciens états
    _clear_creation_state()
    
    # Définir les nouveaux états
    st.session_state.demande_creation_success = True
    st.session_state.last_created_demande_id = demande_id
    st.session_state.last_created_demande_nom = nom_manifestation
    st.session_state.last_created_demande_montant = montant
    st.session_state.last_created_demande_type = type_demande

def _display_simplified_form(type_demande, user_info):
    """Affiche le formulaire simplifié"""
    st.markdown("---")
    st.markdown("### 🛠️ Mode Dégradé - Formulaire Simplifié")
    st.warning("💡 En attendant la configuration des listes déroulantes, vous pouvez utiliser ce formulaire simplifié.")
    
    with st.form("form_simple", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nom_manifestation = st.text_input("📝 Nom de la manifestation*", key="simple_nom")
            client = st.text_input("🏢 Client*", key="simple_client")
            lieu = st.text_input("📍 Lieu*", key="simple_lieu")
        
        with col2:
            montant = st.number_input("💰 Montant (€)*", min_value=0.0, step=50.0, key="simple_montant")
            date_evenement = st.date_input("📅 Date de l'événement*", value=date.today(), key="simple_date")
            urgence = st.selectbox("🚨 Urgence", options=['normale', 'urgent', 'critique'], key="simple_urgence")
            
            current_year = date.today().year
            # Année fiscale au format BYXX même en mode simplifié
            default_byxx = f"BY{(current_year + 1) % 100:02d}"
            fiscal_year = st.text_input("🗓️ Année Fiscale*", 
                                      value=default_byxx,
                                      help="Format BYXX (ex: BY25 pour Mai 2024 - Avril 2025)",
                                      key="simple_fiscal")
        
        commentaires = st.text_area("💭 Commentaires", height=100, key="simple_comments")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_simple = st.form_submit_button("📤 Créer Demande", type="primary", use_container_width=True)
        with col2:
            cancel_simple = st.form_submit_button("❌ Annuler", use_container_width=True)
    
    if cancel_simple:
        st.session_state.page = "dashboard"
        st.rerun()
    
    if submit_simple:
        if not nom_manifestation or not client or not lieu or montant <= 0:
            st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
        else:
            with st.spinner("Création de la demande..."):
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
                        selected_participants=[],
                        fiscal_year=fiscal_year
                    )
                    
                    if success:
                        _set_creation_success(demande_id, nom_manifestation, montant, type_demande)
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la création de la demande")
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

def _display_full_form(type_demande, user_info, budget_options, categorie_options, 
                       typologie_options, region_options, groupe_options, annee_fiscale_options):
    """Affiche le formulaire complet"""
    
    with st.form("form_complet", clear_on_submit=False):
        # 1. Classification
        st.markdown("### 🎯 Classification de la Demande")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget = st.selectbox("💸 Budget*", 
                                options=[opt[0] for opt in budget_options],
                                format_func=lambda x: next((opt[1] for opt in budget_options if opt[0] == x), x),
                                key="full_budget") if budget_options else None
            
            typologie_client = st.selectbox("🏷️ Typologie Client*", 
                                          options=[opt[0] for opt in typologie_options],
                                          format_func=lambda x: next((opt[1] for opt in typologie_options if opt[0] == x), x),
                                          key="full_typologie") if typologie_options else None
        
        with col2:
            categorie = st.selectbox("📂 Catégorie*", 
                                   options=[opt[0] for opt in categorie_options],
                                   format_func=lambda x: next((opt[1] for opt in categorie_options if opt[0] == x), x),
                                   key="full_categorie") if categorie_options else None
            
            region = st.selectbox("🌍 Région*", 
                                options=[opt[0] for opt in region_options],
                                format_func=lambda x: next((opt[1] for opt in region_options if opt[0] == x), x),
                                key="full_region") if region_options else None
        
        with col3:
            groupe_groupement = st.selectbox("👥 Groupe/Groupement*", 
                                           options=[opt[0] for opt in groupe_options],
                                           format_func=lambda x: next((opt[1] for opt in groupe_options if opt[0] == x), x),
                                           key="full_groupe") if groupe_options else None
            
            agence = st.text_input("🏢 Agence*", key="full_agence")

        # 2. Informations principales
        st.markdown("### 📋 Informations Principales")
        col1, col2 = st.columns(2)
        
        with col1:
            nom_manifestation = st.text_input("📝 Nom de la manifestation*", key="full_nom")
            client = st.text_input("🏢 Client*", key="full_client")
            date_evenement = st.date_input("📅 Date de l'événement*", value=date.today(), key="full_date")
        
        with col2:
            lieu = st.text_input("📍 Lieu*", key="full_lieu")
            montant = st.number_input("💰 Montant (€)*", min_value=0.0, step=50.0, key="full_montant")
            urgence = st.selectbox("🚨 Urgence", options=['normale', 'urgent', 'critique'], key="full_urgence")
            
            # Generate list of fiscal years (BY format)
            current_calendar_year = date.today().year
            fiscal_year_options_by = []
            # Generate BY options for roughly 5 years before and 5 years after the current calendar year
            for year in range(current_calendar_year - 5, current_calendar_year + 6):
                fiscal_year_options_by.append(f"BY{str(year)[2:]}")
            # You might want to pre-select the current fiscal year based on the current date
            # For simplicity now, let's just set a default or leave it to the first option

            selected_by = st.selectbox("🗓️ Année Fiscale*", 
                                       options=fiscal_year_options_by,
                                       index=fiscal_year_options_by.index(f"BY{str(current_calendar_year)[2:]}") if f"BY{str(current_calendar_year)[2:]}" in fiscal_year_options_by else 0,
                                       key="full_by")

        # 3. Participants
        st.markdown("### 👥 Participants")
        
        # Version simplifiée des participants (sans formulaire imbriqué)
        demandeur_participe = st.checkbox("Je participe à cet événement", value=True, key="full_participe")
        
        # Participants libres (texte simple)
        participants_libres = st.text_area(
            "Autres participants (optionnel)", 
            key="full_participants_libres", 
            help="Listez les autres participants à cet événement",
            placeholder="Ex: Jean Dupont, Marie Martin, ..."
        )
        
        selected_participants = []  # Pour l'instant, pas de sélection avancée

        # 4. Informations complémentaires
        st.markdown("### 📝 Informations Complémentaires")
        col1, col2 = st.columns(2)
        
        with col1:
            client_enseigne = st.text_input("🏪 Client/Enseigne", key="full_enseigne")
            nom_contact = st.text_input("👤 Nom Contact", key="full_nom_contact")
        
        with col2:
            mail_contact = st.text_input("📧 Email Contact", key="full_mail_contact")
        
        commentaires = st.text_area("💭 Commentaires", height=100, key="full_commentaires")
        
        # Actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_draft = st.form_submit_button("💾 Sauvegarder Brouillon", use_container_width=True)
        with col2:
            submit_btn = st.form_submit_button("📤 Soumettre", type="primary", use_container_width=True)
        with col3:
            cancel_btn = st.form_submit_button("❌ Annuler", use_container_width=True)
    
    if cancel_btn:
        st.session_state.page = "dashboard"
        st.rerun()
    
    if save_draft or submit_btn:
        # Validation
        if not nom_manifestation or not client or not lieu or montant <= 0:
            st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
            return
        
        # Validation des listes déroulantes
        from views.admin_dropdown_options_view import validate_dropdown_value
        validation_errors = []
        
        if budget and not validate_dropdown_value('budget', budget):
            validation_errors.append(f"Budget '{budget}' non autorisé")
        if categorie and not validate_dropdown_value('categorie', categorie):
            validation_errors.append(f"Catégorie '{categorie}' non autorisée")
        if typologie_client and not validate_dropdown_value('typologie_client', typologie_client):
            validation_errors.append(f"Typologie '{typologie_client}' non autorisée")
        if groupe_groupement and not validate_dropdown_value('groupe_groupement', groupe_groupement):
            validation_errors.append(f"Groupe '{groupe_groupement}' non autorisé")
        if region and not validate_dropdown_value('region', region):
            validation_errors.append(f"Région '{region}' non autorisée")
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            return
        
        # Création de la demande
        with st.spinner("Création de la demande en cours..."):
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
                budget=budget or "",
                categorie=categorie or "",
                typologie_client=typologie_client or "",
                groupe_groupement=groupe_groupement or "",
                region=region or "",
                agence=agence or "",
                client_enseigne=client_enseigne or "",
                mail_contact=mail_contact or "",
                nom_contact=nom_contact or "",
                demandeur_participe=demandeur_participe,
                participants_libres=participants_libres or "",
                selected_participants=selected_participants,
                # Passing the selected BY string from the selectbox
                by=selected_by,
                # The controller will need to derive fy from the 'by' string if needed for the DB.
                fy=None, # Explicitly pass None for fy as it's not entered here
                # fiscal_year=fiscal_year # Remove this line as it's no longer used
            )
        
        if success:
            if submit_btn:
                # Soumettre immédiatement
                with st.spinner("Soumission en cours..."):
                    submit_success, submit_message = DemandeController.submit_demande(
                        demande_id, AuthController.get_current_user_id()
                    )
                
                if submit_success:
                    _set_creation_success(demande_id, nom_manifestation, montant, type_demande)
                    st.rerun()
                else:
                    st.error(f"❌ Erreur lors de la soumission: {submit_message}")
            else:
                # Brouillon seulement
                _set_creation_success(demande_id, nom_manifestation, montant, type_demande)
                st.rerun()
        else:
            st.error("❌ Erreur lors de la création de la demande")

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
