"""
User account settings page view - VERSION COMPLÈTE
Gestion complète des paramètres du compte utilisateur
"""
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from utils.security import verify_password, hash_password

@AuthController.require_auth
def account_settings_page():
    """Page des paramètres du compte utilisateur"""
    from views.components.header import display_header
    
    display_header()
    user_info = AuthController.get_current_user()
    user_id = AuthController.get_current_user_id()
    
    st.subheader("⚙️ Paramètres du Compte")
    
    # Onglets pour organiser les paramètres
    tab1, tab2, tab3 = st.tabs([
        "🔑 Mot de Passe", 
        "👤 Informations Personnelles",
        "🔔 Préférences"
    ])
    
    with tab1:
        _display_password_change_section(user_id, user_info)
    
    with tab2:
        _display_profile_section(user_id, user_info)
    
    with tab3:
        _display_preferences_section(user_id, user_info)

def _display_password_change_section(user_id, user_info):
    """Section de changement de mot de passe"""
    st.markdown("### 🔒 Changer le Mot de Passe")
    
    # Conseils de sécurité
    with st.expander("💡 Conseils pour un mot de passe sécurisé"):
        st.markdown("""
        **Votre mot de passe doit contenir :**
        - ✅ Au moins 8 caractères
        - ✅ Au moins une lettre majuscule (A-Z)
        - ✅ Au moins une lettre minuscule (a-z)
        - ✅ Au moins un chiffre (0-9)
        - ✅ Au moins un caractère spécial (!@#$%^&*)
        
        **Évitez :**
        - ❌ Informations personnelles (nom, date de naissance)
        - ❌ Mots de passe communs (123456, password, azerty)
        - ❌ Réutiliser d'anciens mots de passe
        """)
    
    with st.form("password_change_form"):
        st.markdown("#### Modification du Mot de Passe")
        
        # Champs de saisie
        current_password = st.text_input(
            "🔑 Mot de passe actuel*",
            type="password",
            help="Saisissez votre mot de passe actuel pour confirmer votre identité"
        )
        
        new_password = st.text_input(
            "🆕 Nouveau mot de passe*",
            type="password",
            help="Minimum 8 caractères avec majuscules, minuscules, chiffres et caractères spéciaux"
        )
        
        confirm_password = st.text_input(
            "✅ Confirmer le nouveau mot de passe*",
            type="password",
            help="Retapez le nouveau mot de passe pour confirmation"
        )
        
        # Validation en temps réel du nouveau mot de passe
        if new_password:
            _display_password_strength(new_password)
        
        # Bouton de soumission
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_password = st.form_submit_button(
                "🔄 Changer le Mot de Passe",
                type="primary",
                use_container_width=True
            )
        
        # Traitement du formulaire
        if submit_password:
            _process_password_change(
                user_id, user_info,
                current_password, new_password, confirm_password
            )

def _display_password_strength(password):
    """Affiche la force du mot de passe en temps réel"""
    strength_score = 0
    requirements = []
    
    # Vérifications
    if len(password) >= 8:
        requirements.append("✅ Au moins 8 caractères")
        strength_score += 1
    else:
        requirements.append("❌ Au moins 8 caractères")
    
    if any(c.isupper() for c in password):
        requirements.append("✅ Lettre majuscule")
        strength_score += 1
    else:
        requirements.append("❌ Lettre majuscule")
    
    if any(c.islower() for c in password):
        requirements.append("✅ Lettre minuscule")
        strength_score += 1
    else:
        requirements.append("❌ Lettre minuscule")
    
    if any(c.isdigit() for c in password):
        requirements.append("✅ Chiffre")
        strength_score += 1
    else:
        requirements.append("❌ Chiffre")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        requirements.append("✅ Caractère spécial")
        strength_score += 1
    else:
        requirements.append("❌ Caractère spécial")
    
    # Affichage de la force
    if strength_score == 5:
        st.success("🔒 **Mot de passe très fort**")
    elif strength_score >= 4:
        st.info("🔐 **Mot de passe fort**")
    elif strength_score >= 3:
        st.warning("⚠️ **Mot de passe moyen**")
    else:
        st.error("🚨 **Mot de passe faible**")
    
    # Détails des exigences
    with st.expander("Détails des exigences"):
        for req in requirements:
            st.write(req)

def _process_password_change(user_id, user_info, current_password, new_password, confirm_password):
    """Traite le changement de mot de passe"""
    
    # Validation des champs
    if not current_password or not new_password or not confirm_password:
        st.error("⚠️ Tous les champs sont obligatoires")
        return
    
    # Vérification que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        st.error("❌ Les nouveaux mots de passe ne correspondent pas")
        return
    
    # Vérification que le nouveau mot de passe est différent de l'ancien
    if current_password == new_password:
        st.error("⚠️ Le nouveau mot de passe doit être différent de l'ancien")
        return
    
    # Validation de la force du nouveau mot de passe
    if not _validate_password_strength(new_password):
        st.error("🚨 Le nouveau mot de passe ne respecte pas les exigences de sécurité")
        return
    
    try:
        # Vérifier le mot de passe actuel
        user_data = UserController.get_user_by_id(user_id)
        if not user_data:
            st.error("❌ Erreur : Utilisateur non trouvé")
            return
        
        if not verify_password(current_password, user_data['password_hash']):
            st.error("❌ Mot de passe actuel incorrect")
            return
        
        # Changer le mot de passe
        with st.spinner("🔄 Changement du mot de passe en cours..."):
            success = UserController.change_password(user_id, new_password)
        
        if success:
            st.success("✅ Mot de passe changé avec succès !")
            st.info("🔒 Pour votre sécurité, veuillez vous reconnecter")
            
            # Proposer de se déconnecter
            if st.button("🚪 Se déconnecter maintenant", type="secondary"):
                AuthController.logout(user_id)
                st.rerun()
        else:
            st.error("❌ Erreur lors du changement de mot de passe")
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

def _validate_password_strength(password):
    """Valide la force du mot de passe"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    return True

def _display_profile_section(user_id, user_info):
    """Section des informations personnelles"""
    st.markdown("### 👤 Informations Personnelles")
    
    with st.form("profile_form"):
        st.markdown("#### Modifier les Informations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_prenom = st.text_input(
                "Prénom*",
                value=user_info.get('prenom', ''),
                help="Votre prénom"
            )
            
            new_nom = st.text_input(
                "Nom*", 
                value=user_info.get('nom', ''),
                help="Votre nom de famille"
            )
        
        with col2:
            # Email en lecture seule (pour éviter les conflits)
            st.text_input(
                "Email",
                value=user_info.get('email', ''),
                disabled=True,
                help="L'email ne peut pas être modifié (contactez l'administrateur)"
            )
            
            new_region = st.text_input(
                "Région",
                value=user_info.get('region', ''),
                help="Votre région de travail"
            )
        
        # Informations de rôle (lecture seule)
        st.info(f"🏷️ **Rôle :** {user_info.get('role', 'N/A')} (non modifiable)")
        
        # Bouton de soumission
        submit_profile = st.form_submit_button(
            "💾 Sauvegarder les Informations",
            type="primary",
            use_container_width=True
        )
        
        if submit_profile:
            _process_profile_update(user_id, new_prenom, new_nom, new_region)

def _process_profile_update(user_id, new_prenom, new_nom, new_region):
    """Traite la mise à jour du profil"""
    
    # Validation
    if not new_prenom or not new_nom:
        st.error("⚠️ Le prénom et le nom sont obligatoires")
        return
    
    if len(new_prenom.strip()) < 2 or len(new_nom.strip()) < 2:
        st.error("⚠️ Le prénom et le nom doivent contenir au moins 2 caractères")
        return
    
    try:
        with st.spinner("💾 Mise à jour des informations..."):
            success = UserController.update_user_profile(
                user_id=user_id,
                prenom=new_prenom.strip(),
                nom=new_nom.strip(),
                region=new_region.strip() if new_region else None
            )
        
        if success:
            st.success("✅ Informations mises à jour avec succès !")
            st.info("🔄 Veuillez actualiser la page pour voir les changements")
            
            # Bouton pour actualiser
            if st.button("🔄 Actualiser la page", type="secondary"):
                st.rerun()
        else:
            st.error("❌ Erreur lors de la mise à jour des informations")
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

def _display_preferences_section(user_id, user_info):
    """Section des préférences utilisateur"""
    st.markdown("### 🔔 Préférences")
    
    with st.form("preferences_form"):
        st.markdown("#### Paramètres de Notification")
        
        # Simuler des préférences (à implémenter selon les besoins)
        email_notifications = st.checkbox(
            "📧 Recevoir les notifications par email",
            value=True,
            help="Notifications pour les validations, rejets, etc."
        )
        
        browser_notifications = st.checkbox(
            "🔔 Notifications dans le navigateur",
            value=True,
            help="Notifications en temps réel dans l'application"
        )
        
        daily_summary = st.checkbox(
            "📊 Résumé quotidien par email",
            value=False,
            help="Recevoir un résumé quotidien de vos demandes"
        )
        
        st.markdown("#### Paramètres d'Affichage")
        
        items_per_page = st.selectbox(
            "📄 Éléments par page",
            options=[10, 20, 50, 100],
            index=1,
            help="Nombre d'éléments affichés par page dans les listes"
        )
        
        date_format = st.selectbox(
            "📅 Format de date",
            options=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
            index=0,
            help="Format d'affichage des dates"
        )
        
        # Note sur les préférences
        st.info("💡 Ces préférences seront sauvegardées dans votre profil utilisateur")
        
        # Bouton de soumission
        submit_preferences = st.form_submit_button(
            "💾 Sauvegarder les Préférences",
            type="primary",
            use_container_width=True
        )
        
        if submit_preferences:
            # Pour l'instant, juste un message de confirmation
            # À implémenter selon les besoins réels
            st.success("✅ Préférences sauvegardées !")
            st.info("🔧 Fonctionnalité en développement - Les préférences seront bientôt pleinement opérationnelles")

def _display_account_info_summary(user_info):
    """Affiche un résumé des informations du compte"""
    st.markdown("### 📋 Résumé du Compte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **👤 Informations Personnelles:**
        - **Nom complet :** {user_info.get('prenom', '')} {user_info.get('nom', '')}
        - **Email :** {user_info.get('email', '')}
        - **Région :** {user_info.get('region', 'Non définie')}
        """)
    
    with col2:
        st.markdown(f"""
        **🏷️ Informations Système:**
        - **Rôle :** {user_info.get('role', '')}
        - **Compte actif :** {'✅ Oui' if user_info.get('is_active') else '❌ Non'}
        - **Dernière connexion :** {user_info.get('last_login', 'Inconnue')}
        """)
