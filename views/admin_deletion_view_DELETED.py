"""
Interface d'administration pour la suppression complète des demandes et utilisateurs
"""
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from controllers.demande_controller import DemandeController
from config.settings import get_role_label

@AuthController.require_auth
@AuthController.require_role(['admin'])
def admin_deletion_page():
    """Page d'administration pour les suppressions définitives"""
    
    st.title("🗑️ Administration - Suppressions Définitives")
    
    st.error("""
    ⚠️ **ZONE DANGEREUSE - ADMINISTRATEURS UNIQUEMENT**
    
    Cette page permet la suppression complète et définitive d'utilisateurs et de demandes.
    **Ces actions sont IRRÉVERSIBLES** et supprimeront toutes les données associées.
    """)
    
    # Onglets pour séparer les types de suppressions
    tab1, tab2 = st.tabs(["👥 Suppression Utilisateurs", "📋 Suppression Demandes"])
    
    with tab1:
        _display_user_deletion_interface()
    
    with tab2:
        _display_demande_deletion_interface()

def _display_user_deletion_interface():
    """Interface de suppression d'utilisateurs"""
    st.markdown("### 👥 Suppression Complète d'Utilisateurs")
    
    # Filtres pour trouver l'utilisateur
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_user = st.text_input("🔍 Rechercher utilisateur", placeholder="Nom, prénom, email...")
    
    with col2:
        role_filter = st.selectbox(
            "🎭 Filtrer par rôle",
            options=['tous'] + list(['tc', 'dr', 'marketing', 'dr_financier', 'dg']),
            format_func=lambda x: "Tous les rôles" if x == 'tous' else get_role_label(x)
        )
    
    with col3:
        show_inactive = st.checkbox("Voir utilisateurs inactifs", value=True)
    
    # Récupérer les utilisateurs
    users_df = UserController.get_all_users(search_user, role_filter, 'tous' if show_inactive else 'actifs')
    
    if users_df.empty:
        st.info("Aucun utilisateur trouvé")
        return
    
    # Exclure les admins de la liste (sécurité)
    users_df = users_df[users_df['role'] != 'admin']
    
    if users_df.empty:
        st.info("Aucun utilisateur non-admin trouvé")
        return
    
    st.markdown(f"**{len(users_df)} utilisateur(s) trouvé(s)**")
    
    # Liste des utilisateurs avec bouton de suppression
    for idx, user in users_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                status_icon = "✅" if user['is_active'] else "❌"
                st.markdown(f"""
                {status_icon} **{user['prenom']} {user['nom']}** ({get_role_label(user['role'])})  
                📧 {user['email']} | 🌍 {user.get('region', 'N/A')}
                """)
            
            with col2:
                # Afficher les dépendances
                dependencies = UserController.get_user_dependencies(user['id'])
                total_deps = sum(dependencies.values()) if dependencies else 0
                
                if total_deps > 0:
                    st.warning(f"📊 {total_deps} dépendance(s)")
                    with st.expander("Détails"):
                        for key, value in dependencies.items():
                            if value > 0:
                                st.write(f"- {key.replace('_', ' ').title()}: {value}")
                else:
                    st.success("✅ Aucune dépendance")
            
            with col3:
                if st.button(
                    f"🗑️ Supprimer {user['prenom']}", 
                    key=f"delete_user_{user['id']}", 
                    use_container_width=True,
                    help="Suppression définitive avec toutes les données"
                ):
                    st.session_state[f'confirm_user_delete_{user["id"]}'] = True
                    st.rerun()
        
        # Affichage de la confirmation si activée
        if st.session_state.get(f'confirm_user_delete_{user["id"]}'):
            _display_user_deletion_confirmation(user, dependencies)
        
        st.markdown("---")

def _display_demande_deletion_interface():
    """Interface de suppression de demandes"""
    st.markdown("### 📋 Suppression Complète de Demandes")
    
    # Filtres pour trouver les demandes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_demande = st.text_input("🔍 Rechercher demande", placeholder="Nom manifestation, client...")
    
    with col2:
        status_filter = st.selectbox(
            "📊 Statut",
            options=['tous', 'brouillon', 'en_attente_dr', 'en_attente_financier', 'validee', 'rejetee']
        )
    
    with col3:
        if st.button("🔍 Rechercher", use_container_width=True):
            st.rerun()
    
    # Récupérer toutes les demandes (admin voit tout)
    demandes_df = DemandeController.get_demandes_for_user(
        AuthController.get_current_user_id(), 
        'admin', 
        search_demande, 
        status_filter
    )
    
    if demandes_df.empty:
        st.info("Aucune demande trouvée")
        return
    
    st.markdown(f"**{len(demandes_df)} demande(s) trouvée(s)**")
    
    # Liste des demandes avec bouton de suppression
    for idx, demande in demandes_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                status_colors = {
                    'brouillon': '⚪',
                    'en_attente_dr': '🟡',
                    'en_attente_financier': '🟠',
                    'validee': '🟢',
                    'rejetee': '🔴'
                }
                status_icon = status_colors.get(demande['status'], '⚫')
                
                st.markdown(f"""
                {status_icon} **{demande['nom_manifestation']}**  
                👤 {demande['prenom']} {demande['nom']} | 🏢 {demande['client']}  
                💰 {demande['montant']:,.0f}€ | 📅 {demande['date_evenement']}
                """)
            
            with col2:
                # Afficher les dépendances
                dependencies = DemandeController.get_demande_dependencies(demande['id'])
                total_deps = sum(dependencies.values()) if dependencies else 0
                
                if total_deps > 0:
                    st.warning(f"📄 {total_deps} dépendance(s)")
                    with st.expander("Détails"):
                        for key, value in dependencies.items():
                            if value > 0:
                                st.write(f"- {key.replace('_', ' ').title()}: {value}")
                else:
                    st.success("✅ Aucune dépendance")
            
            with col3:
                if st.button(
                    f"🗑️ Supprimer #{demande['id']}", 
                    key=f"delete_demande_{demande['id']}", 
                    use_container_width=True,
                    help="Suppression définitive avec toutes les données"
                ):
                    st.session_state[f'confirm_demande_delete_{demande["id"]}'] = True
                    st.rerun()
        
        # Affichage de la confirmation si activée
        if st.session_state.get(f'confirm_demande_delete_{demande["id"]}'):
            _display_demande_deletion_confirmation(demande, dependencies)
        
        st.markdown("---")

def _display_user_deletion_confirmation(user, dependencies):
    """Confirmation de suppression d'utilisateur"""
    st.markdown("---")
    st.error(f"⚠️ **CONFIRMATION SUPPRESSION - {user['prenom']} {user['nom']}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **👤 Utilisateur à supprimer:**
        - ID: #{user['id']}
        - Nom: {user['prenom']} {user['nom']}
        - Email: {user['email']}
        - Rôle: {get_role_label(user['role'])}
        """)
    
    with col2:
        st.markdown(f"""
        **📄 Données qui seront détruites:**
        - Demandes créées: {dependencies.get('demandes_creees', 0)}
        - Participations: {dependencies.get('participations', 0)}
        - Validations: {dependencies.get('validations', 0)}
        - Notifications: {dependencies.get('notifications', 0)}
        """)
    
    # Confirmation
    expected_text = f"SUPPRIMER {user['prenom']} {user['nom']}"
    confirmation = st.text_input(
        f"Tapez exactement '{expected_text}' pour confirmer:",
        key=f"confirm_text_user_{user['id']}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Annuler", key=f"cancel_user_{user['id']}", use_container_width=True):
            del st.session_state[f'confirm_user_delete_{user["id"]}']
            if f"confirm_text_user_{user['id']}" in st.session_state:
                del st.session_state[f"confirm_text_user_{user['id']}"]
            st.rerun()
    
    with col2:
        if confirmation == expected_text:
            if st.button(
                "🗑️ SUPPRIMER DÉFINITIVEMENT", 
                key=f"execute_user_{user['id']}", 
                use_container_width=True,
                type="primary"
            ):
                with st.spinner(f"Suppression de {user['prenom']} {user['nom']}..."):
                    success, message = UserController.permanently_delete_user(user['id'])
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    
                    # Nettoyer la session
                    del st.session_state[f'confirm_user_delete_{user["id"]}']
                    if f"confirm_text_user_{user['id']}" in st.session_state:
                        del st.session_state[f"confirm_text_user_{user['id']}"]
                    
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        else:
            st.button(
                "🔒 Saisie requise", 
                disabled=True, 
                use_container_width=True,
                help="Tapez le texte de confirmation d'abord"
            )

def _display_demande_deletion_confirmation(demande, dependencies):
    """Confirmation de suppression de demande"""
    st.markdown("---")
    st.error(f"⚠️ **CONFIRMATION SUPPRESSION - Demande #{demande['id']}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📋 Demande à supprimer:**
        - ID: #{demande['id']}
        - Manifestation: {demande['nom_manifestation']}
        - Client: {demande['client']}
        - Montant: {demande['montant']:,.0f}€
        - Créateur: {demande['prenom']} {demande['nom']}
        - Statut: {demande['status']}
        """)
    
    with col2:
        st.markdown(f"""
        **📄 Données qui seront détruites:**
        - Participants: {dependencies.get('participants', 0)}
        - Validations: {dependencies.get('validations', 0)}
        - Notifications: {dependencies.get('notifications', 0)}
        - Logs d'activité: {dependencies.get('activity_logs', 0)}
        """)
    
    # Confirmation
    expected_text = f"SUPPRIMER DEMANDE {demande['id']}"
    confirmation = st.text_input(
        f"Tapez exactement '{expected_text}' pour confirmer:",
        key=f"confirm_text_demande_{demande['id']}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Annuler", key=f"cancel_demande_{demande['id']}", use_container_width=True):
            del st.session_state[f'confirm_demande_delete_{demande["id"]}']
            if f"confirm_text_demande_{demande['id']}" in st.session_state:
                del st.session_state[f"confirm_text_demande_{demande['id']}"]
            st.rerun()
    
    with col2:
        if confirmation == expected_text:
            if st.button(
                "🗑️ SUPPRIMER DÉFINITIVEMENT", 
                key=f"execute_demande_{demande['id']}", 
                use_container_width=True,
                type="primary"
            ):
                with st.spinner(f"Suppression de la demande #{demande['id']}..."):
                    success, message = DemandeController.permanently_delete_demande(demande['id'])
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    
                    # Nettoyer la session
                    del st.session_state[f'confirm_demande_delete_{demande["id"]}']
                    if f"confirm_text_demande_{demande['id']}" in st.session_state:
                        del st.session_state[f"confirm_text_demande_{demande['id']}"]
                    
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        else:
            st.button(
                "🔒 Saisie requise", 
                disabled=True, 
                use_container_width=True,
                help="Tapez le texte de confirmation d'abord"
            )
