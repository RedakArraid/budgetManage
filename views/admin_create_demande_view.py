"""
Vue admin pour la création de demandes avec choix du DR et validation directe
"""
import streamlit as st
from datetime import datetime, date
from controllers.auth_controller import AuthController
from controllers.admin_demande_controller import AdminDemandeController
from models.dropdown_options import DropdownOptionsModel
from utils.validators import validate_montant, validate_text_field

@AuthController.require_role(['admin'])
def admin_create_demande_page():
    """Page admin de création de demandes avec fonctionnalités avancées"""
    from views.components.header import display_header
    
    display_header()
    st.title("➕ Nouvelle demande")
    
    # Information sur les privilèges admin
    st.info("""
    💼 **Privilèges Administrateur :**
    - Créer des demandes pour n'importe quel DR
    - Validation directe sans passer par le workflow
    - Notification automatique des DRs/TCs concernés
    """)
    
    # Récupérer les DRs disponibles
    available_drs = AdminDemandeController.get_available_drs()
    
    # Récupérer les options depuis la table dropdown_options
    from views.admin_dropdown_options_view import get_valid_dropdown_options
    
    budget_options = get_valid_dropdown_options('budget')
    categorie_options = get_valid_dropdown_options('categorie')
    typologie_options = get_valid_dropdown_options('typologie_client')
    region_options = get_valid_dropdown_options('region')
    groupe_options = get_valid_dropdown_options('groupe_groupement')
    
    # Affichage d'avertissement si les options ne sont pas disponibles (non bloquant)
    if not budget_options and not categorie_options:
        st.warning("⚠️ Les listes déroulantes ne sont pas encore configurées.")
        st.info("📄 Vous pouvez créer la demande, mais ajoutez d'abord les options dans 'Gestion des Listes Déroulantes' pour une expérience complète.")
        st.markdown("---")
    
    with st.form("admin_create_demande_form"):
        # 1. Configuration Admin
        st.markdown("### ⚙️ Configuration Admin")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélection du DR
            dr_options = [None] + available_drs
            dr_labels = ["🏢 Créer en mon nom (Admin)"] + [f"👤 {dr['prenom']} {dr['nom']} ({dr['region'] or 'Pas de région'})" for dr in available_drs]
            
            selected_dr_index = st.selectbox(
                "📋 Créer la demande pour :",
                range(len(dr_labels)),
                format_func=lambda x: dr_labels[x],
                help="Choisissez le DR pour lequel créer la demande"
            )
            
            selected_dr_id = dr_options[selected_dr_index]['id'] if selected_dr_index > 0 else None
        
        with col2:
            # Mode de validation
            auto_validate = st.checkbox(
                "🚀 Validation directe (bypass workflow)",
                help="Valider immédiatement la demande sans passer par le workflow standard"
            )
        
        # Affichage du workflow qui sera appliqué
        workflow_info = AdminDemandeController.get_workflow_info(selected_dr_id, auto_validate)
        st.markdown(f"**Workflow :** {workflow_info}")
        
        # 2. Classification de la demande
        st.markdown("### 🎯 Classification de la Demande")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if budget_options:
                budget = st.selectbox(
                    "💸 Budget*", 
                    options=[opt[0] for opt in budget_options],
                    format_func=lambda x: next((opt[1] for opt in budget_options if opt[0] == x), x)
                )
            else:
                budget = st.text_input(
                    "💸 Budget* (saisie libre)",
                    placeholder="Ex: small, medium, large",
                    help="Configurez les listes déroulantes pour avoir des options prédéfinies"
                )
            
            if typologie_options:
                typologie_client = st.selectbox(
                    "🏷️ Typologie Client*", 
                    options=[opt[0] for opt in typologie_options],
                    format_func=lambda x: next((opt[1] for opt in typologie_options if opt[0] == x), x)
                )
            else:
                typologie_client = st.text_input(
                    "🏷️ Typologie Client* (saisie libre)",
                    placeholder="Ex: entreprise, particulier",
                    help="Configurez les listes déroulantes pour avoir des options prédéfinies"
                )
        
        with col2:
            if categorie_options:
                categorie = st.selectbox(
                    "📂 Catégorie*", 
                    options=[opt[0] for opt in categorie_options],
                    format_func=lambda x: next((opt[1] for opt in categorie_options if opt[0] == x), x)
                )
            else:
                categorie = st.text_input(
                    "📂 Catégorie* (saisie libre)",
                    placeholder="Ex: marketing, vente, communication",
                    help="Configurez les listes déroulantes pour avoir des options prédéfinies"
                )
            
            if region_options:
                region = st.selectbox(
                    "🌍 Région*", 
                    options=[opt[0] for opt in region_options],
                    format_func=lambda x: next((opt[1] for opt in region_options if opt[0] == x), x)
                )
            else:
                region = st.text_input(
                    "🌍 Région* (saisie libre)",
                    placeholder="Ex: ile_de_france, nord_est",
                    help="Configurez les listes déroulantes pour avoir des options prédéfinies"
                )
        
        with col3:
            if groupe_options:
                groupe_groupement = st.selectbox(
                    "👥 Groupe/Groupement*", 
                    options=[opt[0] for opt in groupe_options],
                    format_func=lambda x: next((opt[1] for opt in groupe_options if opt[0] == x), x)
                )
            else:
                groupe_groupement = st.text_input(
                    "👥 Groupe/Groupement* (saisie libre)",
                    placeholder="Ex: groupe_a, independant",
                    help="Configurez les listes déroulantes pour avoir des options prédéfinies"
                )
            
            agence = st.text_input(
                "🏢 Agence*", 
                placeholder="Ex: Agence Paris Centre"
            )

        # 3. Informations principales
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
            # Année fiscale depuis les dropdowns admin
            from utils.fiscal_year_utils import get_valid_fiscal_years, get_default_fiscal_year
            fiscal_options = get_valid_fiscal_years()
            
            if fiscal_options:
                selected_by = st.selectbox(
                    "🗓️ Année Fiscale*",
                    options=[opt[0] for opt in fiscal_options],
                    format_func=lambda x: next((opt[1] for opt in fiscal_options if opt[0] == x), x),
                    help="Année fiscale selon configuration admin"
                )
            else:
                st.error("⚠️ Aucune année fiscale configurée par l'admin")
                selected_by = st.text_input(
                    "🗓️ Année Fiscale* (manuel)",
                    value=get_default_fiscal_year(),
                    help="Contactez l'admin pour configurer les années fiscales"
                )

        # 4. Gestion des participants
        st.markdown("### 👥 Participants")
        
        # Version simplifiée pour éviter les conflits de formulaires
        demandeur_participe = st.checkbox(
            "Je participe à cet événement",
            value=True,
            help="Cochez si vous participez personnellement à l'événement"
        )
        
        # Sélection des TCs participants (version simplifiée)
        st.markdown("**👥 Sélectionner des TCs participants :**")
        
        try:
            from controllers.demande_controller import DemandeController
            available_tcs = DemandeController.get_available_participants_for_user(
                AuthController.get_current_user_id(), 'admin'
            )
            
            if available_tcs:
                # Créer les options pour le multiselect
                tc_options = {}
                tc_labels = []
                
                for tc in available_tcs:
                    label = f"{tc['prenom']} {tc['nom']} ({tc['region']}) - {tc['email']}"
                    tc_options[label] = tc['id']
                    tc_labels.append(label)
                
                # Multiselect pour choisir les TCs
                selected_tc_labels = st.multiselect(
                    "Choisir les TCs participants",
                    options=tc_labels,
                    help="Sélectionnez un ou plusieurs TCs qui participeront à l'événement"
                )
                
                # Convertir les labels en IDs
                selected_participants = [tc_options[label] for label in selected_tc_labels]
                
                # Affichage des TCs sélectionnés
                if selected_participants:
                    st.success(f"✅ {len(selected_participants)} TC(s) sélectionné(s)")
            else:
                st.warning("⚠️ Aucun TC disponible")
                selected_participants = []
                
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement des TCs: {e}")
            selected_participants = []
        
        # Champ libre pour autres participants
        participants_libres = st.text_area(
            "Autres participants",
            placeholder="Noms et contacts d'autres participants...",
            help="Participants qui ne sont pas dans le système"
        )
        
        # 5. Informations complémentaires
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
        
        # Configuration par défaut
        type_demande = 'budget'  # Valeur par défaut simplifiée
        
        # Validation en temps réel - seulement si des données ont été saisies
        has_user_input = any([
            nom_manifestation and nom_manifestation.strip(),
            client and client.strip(),
            lieu and lieu.strip(),
            montant > 0
        ])
        
        validation_errors = []
        if has_user_input:
            is_valid, validation_errors = AdminDemandeController.validate_admin_demande_data(
                nom_manifestation, client, lieu, montant, str(date_evenement)
            )
            
            # Affichage des erreurs de validation de base
            if validation_errors:
                for error in validation_errors:
                    st.error(f"⚠️ {error}")
        
        # Validation des listes déroulantes (optionnelle si pas d'options)
        dropdown_errors = []
        try:
            from views.admin_dropdown_options_view import validate_dropdown_value
            
            # Vérifier seulement si les options existent et sont sélectionnées
            if budget_options and budget and not validate_dropdown_value('budget', budget):
                dropdown_errors.append(f"Budget '{budget}' non autorisé")
            if categorie_options and categorie and not validate_dropdown_value('categorie', categorie):
                dropdown_errors.append(f"Catégorie '{categorie}' non autorisée")
            if typologie_options and typologie_client and not validate_dropdown_value('typologie_client', typologie_client):
                dropdown_errors.append(f"Typologie '{typologie_client}' non autorisée")
            if groupe_options and groupe_groupement and not validate_dropdown_value('groupe_groupement', groupe_groupement):
                dropdown_errors.append(f"Groupe '{groupe_groupement}' non autorisé")
            if region_options and region and not validate_dropdown_value('region', region):
                dropdown_errors.append(f"Région '{region}' non autorisée")
                
        except Exception as e:
            # Si erreur de validation des dropdowns, on continue sans bloquer
            st.warning(f"⚠️ Avertissement validation listes: {e}")
            dropdown_errors = []  # Réinitialiser les erreurs pour ne pas bloquer
        
        # Affichage des erreurs dropdown seulement si il y en a
        if dropdown_errors:
            for error in dropdown_errors:
                st.error(f"❌ {error}")
        
        # Validation des champs obligatoires minimaux - adaptation selon la disponibilité des options
        required_fields_ok = (
            nom_manifestation and nom_manifestation.strip() and
            client and client.strip() and
            lieu and lieu.strip() and
            montant > 0 and
            agence and agence.strip()
        )
        
        # Vérifier les listes déroulantes - logique adaptée selon disponibilité
        dropdown_fields_ok = True
        
        # Budget: obligatoire seulement si des options existent
        if budget_options:
            # Mode selectbox: une option doit être sélectionnée
            dropdown_fields_ok = dropdown_fields_ok and budget and budget.strip()
        else:
            # Mode text_input: soit rempli soit optionnel pour permettre la création
            # On rend le champ optionnel si pas d'options configurées
            pass  # Le champ devient optionnel
        
        # Catégorie: même logique
        if categorie_options:
            dropdown_fields_ok = dropdown_fields_ok and categorie and categorie.strip()
        else:
            pass  # Optionnel si pas d'options
        
        # Typologie client: même logique
        if typologie_options:
            dropdown_fields_ok = dropdown_fields_ok and typologie_client and typologie_client.strip()
        else:
            pass  # Optionnel si pas d'options
        
        # Région: même logique
        if region_options:
            dropdown_fields_ok = dropdown_fields_ok and region and region.strip()
        else:
            pass  # Optionnel si pas d'options
        
        # Groupe/Groupement: même logique
        if groupe_options:
            dropdown_fields_ok = dropdown_fields_ok and groupe_groupement and groupe_groupement.strip()
        else:
            pass  # Optionnel si pas d'options
        
        # Condition finale pour activer le bouton
        button_enabled = required_fields_ok and dropdown_fields_ok and not dropdown_errors
        
        # DEBUG TEMPORAIRE - pour identifier le problème
        if has_user_input:
            st.markdown("---")
            st.markdown("### 🔍 **DEBUG - État du formulaire**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Champs de base:**")
                st.write(f"- nom_manifestation: `{repr(nom_manifestation)}` {'✅' if nom_manifestation and nom_manifestation.strip() else '❌'}")
                st.write(f"- client: `{repr(client)}` {'✅' if client and client.strip() else '❌'}")
                st.write(f"- lieu: `{repr(lieu)}` {'✅' if lieu and lieu.strip() else '❌'}")
                st.write(f"- montant: `{montant}` {'✅' if montant > 0 else '❌'}")
                st.write(f"- agence: `{repr(agence)}` {'✅' if agence and agence.strip() else '❌'}")
            
            with col2:
                st.markdown("**Listes déroulantes:**")
                st.write(f"- budget_options: {len(budget_options) if budget_options else 0} option(s)")
                st.write(f"- budget: `{repr(budget)}` {'✅' if not budget_options or (budget and budget.strip()) else '❌'}")
                st.write(f"- categorie_options: {len(categorie_options) if categorie_options else 0} option(s)")
                st.write(f"- categorie: `{repr(categorie)}` {'✅' if not categorie_options or (categorie and categorie.strip()) else '❌'}")
                st.write(f"- typologie_options: {len(typologie_options) if typologie_options else 0} option(s)")
                st.write(f"- typologie_client: `{repr(typologie_client)}` {'✅' if not typologie_options or (typologie_client and typologie_client.strip()) else '❌'}")
            
            with col3:
                st.markdown("**Conditions de validation:**")
                st.write(f"- required_fields_ok: {'✅' if required_fields_ok else '❌'}")
                st.write(f"- dropdown_fields_ok: {'✅' if dropdown_fields_ok else '❌'}")
                st.write(f"- dropdown_errors: {len(dropdown_errors)} erreur(s)")
                st.write(f"- **BOUTON ACTIF: {'✅' if button_enabled else '❌'}**")
            
            st.markdown("---")
        
        # Affichage de l'état de validation pour debug - seulement si l'utilisateur a commencé à remplir
        if not button_enabled and has_user_input:
            debug_info = []
            if not nom_manifestation or not nom_manifestation.strip():
                debug_info.append("Nom manifestation manquant")
            if not client or not client.strip():
                debug_info.append("Client manquant")
            if not lieu or not lieu.strip():
                debug_info.append("Lieu manquant")
            if montant <= 0:
                debug_info.append("Montant invalide")
            if not agence or not agence.strip():
                debug_info.append("Agence manquante")
            
            # Vérification des listes déroulantes - seulement si elles ont des options
            if budget_options and (not budget or not budget.strip()):
                debug_info.append("Budget manquant (options disponibles)")
            if categorie_options and (not categorie or not categorie.strip()):
                debug_info.append("Catégorie manquante (options disponibles)")
            if typologie_options and (not typologie_client or not typologie_client.strip()):
                debug_info.append("Typologie client manquante (options disponibles)")
            if region_options and (not region or not region.strip()):
                debug_info.append("Région manquante (options disponibles)")
            if groupe_options and (not groupe_groupement or not groupe_groupement.strip()):
                debug_info.append("Groupe/Groupement manquant (options disponibles)")
            
            # Affichage des champs optionnels
            optional_fields = []
            if not budget_options:
                optional_fields.append("Budget (optionnel - pas d'options configurées)")
            if not categorie_options:
                optional_fields.append("Catégorie (optionnel - pas d'options configurées)")
            if not typologie_options:
                optional_fields.append("Typologie (optionnel - pas d'options configurées)")
            if not region_options:
                optional_fields.append("Région (optionnel - pas d'options configurées)")
            if not groupe_options:
                optional_fields.append("Groupe (optionnel - pas d'options configurées)")
            
            if dropdown_errors:
                debug_info.append("Erreurs listes déroulantes")
            
            if debug_info:
                st.warning(f"🔧 Pour activer le bouton: {', '.join(debug_info)}")
            
            if optional_fields:
                st.info(f"📢 Champs optionnels: {', '.join(optional_fields)}")
        
        # Actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
        
        with col2:
            create_draft = st.form_submit_button(
                "💾 Créer Brouillon", 
                use_container_width=True,
                help="Créer sans validation"
            )
        
        with col3:
            create_and_process = st.form_submit_button(
                f"🚀 {'Créer et Valider' if auto_validate else 'Créer et Traiter'}", 
                use_container_width=True,
                type="primary",
                help="Créer et appliquer le workflow sélectionné"
            )
    
    # Traitement du formulaire
    if create_draft or create_and_process:
        # Vérification finale avant traitement (maintenant faite après le clic)
        if create_and_process:
            # Re-valider les champs obligatoires
            required_fields_ok = (
                nom_manifestation and nom_manifestation.strip() and
                client and client.strip() and
                lieu and lieu.strip() and
                montant > 0 and
                agence and agence.strip()
            )
            
            # Vérifier les listes déroulantes - logique adaptée selon disponibilité
            dropdown_fields_ok = True
            dropdown_errors_submit = [] # Utiliser une liste séparée pour les erreurs de soumission
            
            try:
                from views.admin_dropdown_options_view import validate_dropdown_value
                
                if budget_options:
                    if not budget or not budget.strip():
                         dropdown_errors_submit.append("Budget manquant (options disponibles)")
                    elif not validate_dropdown_value('budget', budget):
                         dropdown_errors_submit.append(f"Budget '{budget}' non autorisé")
                
                if categorie_options:
                    if not categorie or not categorie.strip():
                        dropdown_errors_submit.append("Catégorie manquante (options disponibles)")
                    elif not validate_dropdown_value('categorie', categorie):
                         dropdown_errors_submit.append(f"Catégorie '{categorie}' non autorisée")
                         
                if typologie_options:
                    if not typologie_client or not typologie_client.strip():
                         dropdown_errors_submit.append("Typologie client manquante (options disponibles)")
                    elif not validate_dropdown_value('typologie_client', typologie_client):
                         dropdown_errors_submit.append(f"Typologie '{typologie_client}' non autorisée")
                         
                if region_options:
                     if not region or not region.strip():
                         dropdown_errors_submit.append("Région manquante (options disponibles)")
                     elif not validate_dropdown_value('region', region):
                         dropdown_errors_submit.append(f"Région '{region}' non autorisée")
                         
                if groupe_options:
                    if not groupe_groupement or not groupe_groupement.strip():
                        dropdown_errors_submit.append("Groupe/Groupement manquant (options disponibles)")
                    elif not validate_dropdown_value('groupe_groupement', groupe_groupement):
                        dropdown_errors_submit.append(f"Groupe '{groupe_groupement}' non autorisé")

            except Exception as e:
                 st.warning(f"⚠️ Avertissement validation listes lors de la soumission: {e}")
                 dropdown_errors_submit = [] # Ne pas bloquer la soumission en cas d'erreur technique
                 
            all_fields_valid = required_fields_ok and not dropdown_errors_submit

            if not all_fields_valid:
                error_messages = []
                if not nom_manifestation or not nom_manifestation.strip():
                    error_messages.append("Nom manifestation")
                if not client or not client.strip():
                    error_messages.append("Client")
                if not lieu or not lieu.strip():
                    error_messages.append("Lieu")
                if montant <= 0:
                    error_messages.append("Montant")
                if not agence or not agence.strip():
                    error_messages.append("Agence")

                # Ajouter les erreurs spécifiques des dropdowns si elles existent
                error_messages.extend(dropdown_errors_submit)

                if error_messages:
                     st.error(f"⚠️ Veuillez remplir les champs requis : {', '.join(error_messages)}")
                return # Arrêter le traitement si validation échoue

        # Pour les brouillons, on est plus permissif
        if create_draft:
             if not nom_manifestation or not client:
                 st.error("⚠️ Au minimum le nom de la manifestation et le client sont requis pour un brouillon")
                 return # Arrêter le traitement si validation brouillon échoue

        with st.spinner("🚀 Création de la demande admin en cours..."):
            success, demande_id = AdminDemandeController.create_admin_demande(
                admin_id=AuthController.get_current_user_id(),
                selected_dr_id=selected_dr_id,
                type_demande=type_demande,
                nom_manifestation=nom_manifestation,
                client=client,
                date_evenement=date_evenement.strftime('%Y-%m-%d'),
                lieu=lieu,
                montant=montant,
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
                auto_validate=create_and_process and auto_validate,
                selected_participants=selected_participants,
                by=selected_by
            )
        
        if success:
            if create_and_process and auto_validate:
                st.success("✅ Demande créée et validée directement avec succès!")
                st.balloons()
                
                # Afficher le résumé avec info admin
                _display_admin_success_summary(
                    demande_id, nom_manifestation, montant, type_demande, 
                    selected_dr_id, auto_validate, available_drs
                )
            elif create_and_process:
                st.success("✅ Demande créée et envoyée en validation financière!")
                st.info("📋 La demande suit maintenant le workflow normal de validation")
            else:
                st.success("✅ Demande créée en brouillon!")
                st.info("💡 Vous pouvez la modifier et la traiter plus tard")
            
            # Bouton pour retourner au tableau de bord
            if st.button("← Retour au tableau de bord", type="secondary"):
                st.session_state.page = "dashboard"
                st.rerun()
        else:
            st.error("❌ Erreur lors de la création de la demande admin")

def _display_admin_success_summary(demande_id: int, nom_manifestation: str, montant: float, 
                                  type_demande: str, selected_dr_id: int, auto_validate: bool, 
                                  available_drs: list):
    """Affiche un résumé de la demande créée par l'admin"""
    st.markdown("---")
    st.subheader("📋 Résumé de la demande admin")
    
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
        # Info sur le DR sélectionné
        if selected_dr_id:
            selected_dr = next((dr for dr in available_drs if dr['id'] == selected_dr_id), None)
            if selected_dr:
                st.markdown(f"""
                **👤 Créée pour:**
                - **DR:** {selected_dr['prenom']} {selected_dr['nom']}
                - **Email:** {selected_dr['email']}
                - **Région:** {selected_dr['region'] or 'Non spécifiée'}
                """)
        else:
            st.markdown("""
            **👤 Créateur:**
            - **Admin:** Vous-même
            - **Statut:** Administrateur
            """)
    
    # Info workflow
    if auto_validate:
        st.success("""
        🚀 **Validation directe appliquée:**
        - ✅ Demande immédiatement validée
        - 📧 Notifications envoyées aux DRs/TCs concernés
        - 💼 Tous les niveaux de validation marqués avec votre ID admin
        """)
    else:
        st.info("""
        📋 **Workflow normal appliqué:**
        - ⏳ Demande en attente de validation financière
        - 📧 DR concerné notifié
        - 🔄 Suit le processus standard
        """)
