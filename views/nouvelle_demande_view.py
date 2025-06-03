"""
Vue pour la création de nouvelles demandes
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
    
    # Déterminer le type de demande selon le rôle
    if user_info['role'] == 'marketing':
        type_demande = 'marketing'
        st.info("📢 Vous créez une demande Marketing qui sera envoyée aux financiers et admins")
    else:
        type_demande = 'budget'
        st.info("💰 Vous créez une demande Budget qui suivra le workflow de validation")
    
    # Récupérer les options depuis la table dropdown_options
    from views.admin_dropdown_options_view import get_valid_dropdown_options
    
    # Récupérer les options valides (SEULES ces options peuvent être utilisées)
    budget_options = get_valid_dropdown_options('budget')
    categorie_options = get_valid_dropdown_options('categorie')
    typologie_options = get_valid_dropdown_options('typologie_client')
    region_options = get_valid_dropdown_options('region')
    groupe_options = get_valid_dropdown_options('groupe_groupement')
    
    # Vérifier si les options sont disponibles
    if not budget_options and not categorie_options:
        st.error("⚠️ Impossible de charger les options des listes déroulantes. Contactez l'administrateur.")
        st.info("📄 Les options doivent d'abord être définies dans la page 'Listes Déroulantes' par un administrateur.")
        return
    
    with st.form("nouvelle_demande_form"):
        # 1. Listes déroulantes dynamiques en premier
        st.markdown("### 🎯 Classification de la Demande")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget = st.selectbox(
                "💸 Budget*", 
                options=[opt[0] for opt in budget_options],
                format_func=lambda x: next((opt[1] for opt in budget_options if opt[0] == x), x),
                help="Options gérées par la page admin"
            ) if budget_options else st.selectbox("💸 Budget*", ["Aucune option disponible"], disabled=True)
            
            typologie_client = st.selectbox(
                "🏷️ Typologie Client*", 
                options=[opt[0] for opt in typologie_options],
                format_func=lambda x: next((opt[1] for opt in typologie_options if opt[0] == x), x),
                help="Options gérées par la page admin"
            ) if typologie_options else st.selectbox("🏷️ Typologie Client*", ["Aucune option disponible"], disabled=True)
        
        with col2:
            categorie = st.selectbox(
                "📂 Catégorie*", 
                options=[opt[0] for opt in categorie_options],
                format_func=lambda x: next((opt[1] for opt in categorie_options if opt[0] == x), x),
                help="Options gérées par la page admin"
            ) if categorie_options else st.selectbox("📂 Catégorie*", ["Aucune option disponible"], disabled=True)
            
            region = st.selectbox(
                "🌍 Région*", 
                options=[opt[0] for opt in region_options],
                format_func=lambda x: next((opt[1] for opt in region_options if opt[0] == x), x),
                help="Options gérées par la page admin"
            ) if region_options else st.selectbox("🌍 Région*", ["Aucune option disponible"], disabled=True)
        
        with col3:
            groupe_groupement = st.selectbox(
                "👥 Groupe/Groupement*", 
                options=[opt[0] for opt in groupe_options],
                format_func=lambda x: next((opt[1] for opt in groupe_options if opt[0] == x), x),
                help="Options gérées par la page admin"
            ) if groupe_options else st.selectbox("👥 Groupe/Groupement*", ["Aucune option disponible"], disabled=True)
            
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

        # 3. Gestion des participants selon le rôle
        st.markdown("### 👥 Participants")
        
        # Utiliser le composant avancé pour la sélection des participants
        from views.components.participants_advanced import display_participants_advanced
        
        demandeur_participe, selected_participants, participants_libres = display_participants_advanced(
            user_role=user_info['role'],
            user_id=AuthController.get_current_user_id()
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
                st.session_state.page = "dashboard"
                st.rerun()
    
    # Traitement du formulaire
    if save_draft or submit_btn:
        # Validation des champs obligatoires
        required_fields = {
            'nom_manifestation': nom_manifestation,
            'client': client,
            'lieu': lieu,
            'montant': montant
        }
        
        missing_fields = [name for name, value in required_fields.items() 
                         if not value or (name == 'montant' and value <= 0)]
        
        if missing_fields:
            st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
            return
        
        if errors:
            st.error("⚠️ Veuillez corriger les erreurs avant de continuer")
            return
        
        # Créer la demande avec validation
        from views.admin_dropdown_options_view import validate_dropdown_value
        
        # Valider que toutes les valeurs sont autorisées
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
            st.error("⚠️ Demande rejetée - Seules les valeurs définies par l'admin sont autorisées")
            return
        with st.spinner("Création de la demande en cours..."):
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
                region=region,
                agence=agence,
                client_enseigne=client_enseigne,
                mail_contact=mail_contact,
                nom_contact=nom_contact,
                demandeur_participe=demandeur_participe,
                participants_libres=participants_libres,
                selected_participants=selected_participants
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
                    
                    # Afficher le résumé
                    _display_success_summary(demande_id, nom_manifestation, montant, type_demande)
                else:
                    st.error(f"❌ Erreur lors de la soumission: {submit_message}")
            else:
                st.success("✅ Demande sauvegardée en brouillon!")
                st.info("💡 Vous pouvez la modifier et la soumettre plus tard depuis la page 'Mes Demandes'")
            
            # Bouton pour retourner au tableau de bord
            if st.button("← Retour au tableau de bord", type="secondary"):
                st.session_state.page = "dashboard"
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
