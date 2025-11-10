"""
Vue pour la gestion des utilisateurs (CRUD complet)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from config.settings import role_config, get_role_label, get_role_color
from utils.validators import validate_email

@AuthController.require_auth
@AuthController.require_role(['admin'])
def gestion_utilisateurs_page():
    """Page de gestion des utilisateurs - Admin uniquement"""
    
    st.subheader("👥 Gestion des Utilisateurs")
    
    # Onglets pour organiser les fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "➕ Créer", "📊 Statistiques", "📤 Export"])
    
    with tab1:
        _display_users_list()
    
    with tab2:
        _display_create_user_form()
    
    with tab3:
        _display_user_statistics()
    
    with tab4:
        _display_export_options()

def _display_users_list():
    """Afficher la liste des utilisateurs avec filtres et actions"""
    st.markdown("### 📋 Liste des Utilisateurs")
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_query = st.text_input("🔍 Rechercher", placeholder="Nom, prénom, email...")
    
    with col2:
        role_options = ['tous'] + list(role_config.roles.keys())
        role_filter = st.selectbox(
            "🎭 Filtrer par rôle",
            options=role_options,
            format_func=lambda x: "Tous les rôles" if x == 'tous' else get_role_label(x)
        )
    
    with col3:
        status_filter = st.selectbox(
            "✅ Statut",
            options=['tous', 'actifs', 'inactifs'],
            format_func=lambda x: {
                'tous': 'Tous',
                'actifs': 'Actifs uniquement',
                'inactifs': 'Inactifs uniquement'
            }[x]
        )
    
    with col4:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    # Récupérer les utilisateurs
    users_df = UserController.get_all_users(search_query, role_filter, status_filter)
    
    if users_df.empty:
        st.info("Aucun utilisateur trouvé avec ces critères")
        return
    
    # Affichage des résultats
    st.markdown(f"**{len(users_df)} utilisateur(s) trouvé(s)**")
    
    # Table des utilisateurs avec actions
    for idx, user in users_df.iterrows():
        _display_user_card(user)

def _display_user_card(user):
    """Afficher une carte utilisateur avec actions"""
    # Couleur selon le statut
    status_color = "#28a745" if user['is_active'] else "#dc3545"
    role_color = get_role_color(user['role'])
    
    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; 
                    border-left: 4px solid {status_color};">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.markdown(f"""
            **👤 {user['prenom']} {user['nom']}**  
            📧 {user['email']}  
            🎭 <span style="color: {role_color}; font-weight: bold;">{get_role_label(user['role'])}</span>  
            🌍 {user['region'] or 'N/A'}  
            {'✅ Actif' if user['is_active'] else '❌ Inactif'}
            """, unsafe_allow_html=True)
        
        with col2:
            if user.get('directeur_nom'):
                st.markdown(f"""
                **👨‍💼 Directeur:**  
                {user['directeur_prenom']} {user['directeur_nom']}
                """)
            
            st.markdown(f"""
            **📅 Créé le:**  
            {pd.to_datetime(user['created_at']).strftime('%d/%m/%Y')}
            """)
        
        with col3:
            # Actions
            if st.button(f"✏️ Modifier", key=f"edit_{user['id']}", use_container_width=True):
                st.session_state[f'edit_user_{user["id"]}'] = True
                st.rerun()
            
            status_btn_text = "❌ Désactiver" if user['is_active'] else "✅ Activer"
            if st.button(status_btn_text, key=f"toggle_{user['id']}", use_container_width=True):
                success, message = UserController.activate_user(user['id'], not user['is_active'])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            
            if st.button(f"🔑 Reset MDP", key=f"reset_{user['id']}", use_container_width=True):
                success, message = UserController.reset_password(user['id'])
                if success:
                    st.success(message)
                else:
                    st.error(message)
            
            # Bouton suppression complète (ADMIN ONLY)
            if st.button(f"🗑️ Suppr. TOTALE", key=f"delete_complete_{user['id']}", use_container_width=True, help="Suppression définitive avec toutes les données liées (IRRÉVERSIBLE)"):
                st.session_state[f'confirm_delete_complete_{user["id"]}'] = True
                st.rerun()
        
        # Gestion de la suppression complète avec confirmation (intégrée dans la carte)
        if st.session_state.get(f'confirm_delete_complete_{user["id"]}'):
            _display_inline_delete_confirmation(user)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Formulaire de modification (si activé)
        if st.session_state.get(f'edit_user_{user["id"]}'):
            _display_edit_user_form(user)

def _display_delete_confirmation(user):
    """Afficher la confirmation de suppression complète"""
    st.markdown("---")
    st.markdown(f"### ⚠️ Suppression Définitive de {user['prenom']} {user['nom']}")
    
    # Récupérer les dépendances
    dependencies = UserController.get_user_dependencies(user['id'])
    
    # Affichage des informations de l'utilisateur
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **👤 Informations utilisateur:**
        - **Nom:** {user['prenom']} {user['nom']}
        - **Email:** {user['email']}
        - **Rôle:** {get_role_label(user['role'])}
        - **Région:** {user.get('region', 'N/A')}
        - **Statut:** {'Actif' if user['is_active'] else 'Inactif'}
        """)
    
    with col2:
        st.markdown(f"""
        **📄 Données qui seront supprimées:**
        - **Demandes créées:** {dependencies.get('demandes_creees', 0)}
        - **Participations:** {dependencies.get('participations', 0)}
        - **Validations:** {dependencies.get('validations', 0)}
        - **Notifications:** {dependencies.get('notifications', 0)}
        - **Subordonnés affectés:** {dependencies.get('subordonnes', 0)}
        """)
    
    # Avertissements
    st.error("""
    ⚠️ **ATTENTION - SUPPRESSION DÉFINITIVE:**
    
    Cette action va **détruire complètement** cet utilisateur et **TOUTES** ses données associées:
    - L'utilisateur et son compte seront **définitivement supprimés**
    - **Toutes ses demandes** seront supprimées (avec participants, validations, notifications)
    - **Toutes ses participations** à d'autres demandes seront supprimées
    - **Toutes ses validations** seront supprimées
    - **Toutes ses notifications** seront supprimées
    - Ses **subordonnés** perdront leur lien hiérarchique
    
    **Cette action est IRRÉVERSIBLE et ne peut pas être annulée.**
    """)
    
    # Zone de confirmation
    st.markdown("### ✅ Confirmation")
    
    # Checkbox de confirmation
    confirm_understood = st.checkbox(
        f"Je comprends que cette action va supprimer définitivement {user['prenom']} {user['nom']} et toutes ses données",
        key=f"confirm_understood_{user['id']}"
    )
    
    # Saisie du nom pour double confirmation
    expected_text = f"{user['prenom']} {user['nom']}"
    confirmation_text = st.text_input(
        f"Pour confirmer, tapez exactement: **{expected_text}**",
        key=f"confirmation_text_{user['id']}",
        placeholder=expected_text
    )
    
    text_matches = confirmation_text.strip() == expected_text
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❌ Annuler", key=f"cancel_delete_{user['id']}", use_container_width=True):
            del st.session_state[f'confirm_delete_complete_{user["id"]}']
            if f"confirm_understood_{user['id']}" in st.session_state:
                del st.session_state[f"confirm_understood_{user['id']}"]
            if f"confirmation_text_{user['id']}" in st.session_state:
                del st.session_state[f"confirmation_text_{user['id']}"]
            st.rerun()
    
    with col2:
        # Bouton "Supprimer TOUT" - activé seulement si toutes les conditions sont remplies
        can_delete = confirm_understood and text_matches
        
        if st.button(
            "🗑️ SUPPRIMER TOUT", 
            key=f"execute_delete_{user['id']}", 
            use_container_width=True,
            type="primary" if can_delete else "secondary",
            disabled=not can_delete

def _display_edit_user_form(user):
    """Formulaire de modification d'un utilisateur"""
    st.markdown("---")
    st.markdown(f"### ✏️ Modification de {user['prenom']} {user['nom']}")
    
    # Debug: Afficher les données actuelles de l'utilisateur
    with st.expander("🔧 Debug - Données actuelles"):
        st.json({
            'id': user['id'],
            'email': user['email'],
            'nom': user['nom'],
            'prenom': user['prenom'],
            'role': user['role'],
            'region': user.get('region'),
            'budget_alloue': user.get('budget_alloue', 0),
            'directeur_id': user.get('directeur_id'),
            'is_active': user['is_active']
        })
    
    with st.form(f"edit_user_form_{user['id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("📧 Email", value=user['email'])
            new_nom = st.text_input("👤 Nom", value=user['nom'])
            new_prenom = st.text_input("👤 Prénom", value=user['prenom'])
        
        with col2:
            new_role = st.selectbox(
                "🎭 Rôle",
                options=list(role_config.roles.keys()),
                index=list(role_config.roles.keys()).index(user['role']),
                format_func=get_role_label
            )
            
            # Gestion des champs spécifiques selon le rôle
            new_region = None
            new_directeur_id = None
            
            if new_role == 'dr':
                # DR doit choisir une région
                regions = UserController.get_regions()
                if regions:
                    current_region = user.get('region', '')
                    region_index = regions.index(current_region) if current_region in regions else 0
                    new_region = st.selectbox(
                        "🌍 Région", 
                        options=regions,
                        index=region_index
                    )
                else:
                    st.error("⚠️ Aucune région disponible")
                    new_region = user.get('region', '')
            
            elif new_role == 'tc':
                # TC doit choisir un DR
                directors = UserController.get_directors()
                if directors:
                    dr_options = [f"{dr['prenom']} {dr['nom']} ({dr['region']})" for dr in directors]
                    dr_ids = [dr['id'] for dr in directors]
                    
                    current_dir_id = user.get('directeur_id')
                    dr_index = dr_ids.index(current_dir_id) if current_dir_id in dr_ids else 0
                    
                    selected_dr_idx = st.selectbox(
                        "👨‍💼 Directeur Régional",
                        options=range(len(dr_options)),
                        format_func=lambda x: dr_options[x],
                        index=dr_index
                    )
                    new_directeur_id = dr_ids[selected_dr_idx]
                    new_region = directors[selected_dr_idx]['region']  # Région automatique
                    
                    st.info(f"🌍 Région automatique: {new_region}")
                else:
                    st.error("⚠️ Aucun directeur disponible")
                    new_directeur_id = user.get('directeur_id')
                    new_region = user.get('region', '')
            else:
                # Pour les autres rôles, garder la région actuelle
                new_region = user.get('region', '')
                new_directeur_id = user.get('directeur_id')
            
            new_budget = st.number_input(
                "💰 Budget Alloué", 
                value=float(user.get('budget_alloue', 0)),
                min_value=0.0,
                step=100.0
            )
        
        # Debug: Afficher les nouvelles valeurs
        with st.expander("🔧 Debug - Nouvelles valeurs"):
            new_data_preview = {
                'email': new_email,
                'nom': new_nom,
                'prenom': new_prenom,
                'role': new_role,
                'region': new_region,
                'directeur_id': new_directeur_id,
                'budget_alloue': new_budget
            }
            st.json(new_data_preview)
        
        # Actions du formulaire
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True):
                # Préparer les données de mise à jour
                update_data = {
                    'email': new_email,
                    'nom': new_nom,
                    'prenom': new_prenom,
                    'role': new_role,
                    'budget_alloue': new_budget
                }
                
                # Ajouter région et directeur si applicable
                if new_region is not None:
                    update_data['region'] = new_region
                
                if new_directeur_id is not None:
                    update_data['directeur_id'] = new_directeur_id
                
                # Debug: Afficher les données envoyées
                st.write("🔧 **Debug - Données à mettre à jour:**")
                st.json(update_data)
                
                # Exécuter la mise à jour
                with st.spinner("🔄 Mise à jour en cours..."):
                    success, message = UserController.update_user(user['id'], **update_data)
                
                st.write(f"🔧 **Résultat:** Succès={success}, Message={message}")
                
                if success:
                    st.success(message)
                    st.write("🔄 Actualisation de la page...")
                    del st.session_state[f'edit_user_{user["id"]}']
                    st.rerun()
                else:
                    st.error(message)
                    
                    # Debug supplémentaire en cas d'erreur
                    st.write("🔧 **Debug supplémentaire:**")
                    try:
                        from models.database import db
                        # Vérifier si l'utilisateur existe toujours
                        check_user = db.execute_query("SELECT * FROM users WHERE id = ?", (user['id'],), fetch='one')
                        if check_user:
                            st.write("L'utilisateur existe dans la DB")
                            st.json(dict(check_user))
                        else:
                            st.write("L'utilisateur n'existe plus dans la DB")
                    except Exception as e:
                        st.write(f"Erreur debug: {e}")
        
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                del st.session_state[f'edit_user_{user["id"]}']
                st.rerun()
        
        with col3:
            if st.form_submit_button("🗑️ Supprimer", use_container_width=True):
                with st.spinner("🗑️ Suppression en cours..."):
                    success, message = UserController.delete_user(user['id'])
                
                if success:
                    st.success(message)
                    del st.session_state[f'edit_user_{user["id"]}']
                    st.rerun()
                else:
                    st.error(message)

def _display_create_user_form():
    """Formulaire de création d'un nouvel utilisateur"""
    st.markdown("### ➕ Créer un Nouvel Utilisateur")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("📧 Email*", placeholder="utilisateur@entreprise.com")
            nom = st.text_input("👤 Nom de famille*", placeholder="Dupont")
            prenom = st.text_input("👤 Prénom*", placeholder="Jean")
        
        with col2:
            role = st.selectbox(
                "🎭 Rôle*",
                options=list(role_config.roles.keys()),
                format_func=get_role_label
            )
            
            budget_alloue = st.number_input(
                "💰 Budget Alloué", 
                value=0.0,
                min_value=0.0,
                step=100.0,
                help="Budget en euros (optionnel)"
            )
        
        # Champs conditionnels selon le rôle
        region = None
        directeur_id = None
        
        if role == 'dr':
            st.markdown("#### 🌍 Configuration Directeur Régional")
            regions = UserController.get_regions()
            if regions:
                region = st.selectbox("🌍 Région*", options=regions)
            else:
                st.error("⚠️ Aucune région disponible dans le système")
        
        elif role == 'tc':
            st.markdown("#### 👨‍💼 Configuration Technico-Commercial")
            directors = UserController.get_directors()
            if directors:
                dr_options = [f"{dr['prenom']} {dr['nom']} ({dr['region']})" for dr in directors]
                dr_ids = [dr['id'] for dr in directors]
                
                selected_dr_idx = st.selectbox(
                    "👨‍💼 Directeur Régional*",
                    options=range(len(dr_options)),
                    format_func=lambda x: dr_options[x]
                )
                directeur_id = dr_ids[selected_dr_idx]
                region = directors[selected_dr_idx]['region']
                
                st.info(f"🌍 Région automatique: **{region}** (région du DR sélectionné)")
            else:
                st.error("⚠️ Aucun directeur régional disponible. Créez d'abord un DR.")
        
        # Informations supplémentaires
        with st.expander("ℹ️ Informations importantes"):
            st.markdown("""
            - **Mot de passe temporaire** : `TempPass123!` (à changer à la première connexion)
            - **Statut** : L'utilisateur sera créé comme **inactif** et devra être activé manuellement
            - **DR** : Un DR gère une région et peut avoir des TCs sous sa responsabilité
            - **TC** : Un TC est rattaché à un DR et hérite automatiquement de sa région
            """)
        
        # Bouton de création
        if st.form_submit_button("✅ Créer l'Utilisateur", type="primary", use_container_width=True):
            # Validation des champs obligatoires
            if not email or not nom or not prenom:
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
                return
            
            if role == 'dr' and not region:
                st.error("⚠️ Veuillez sélectionner une région pour le DR")
                return
            
            if role == 'tc' and not directeur_id:
                st.error("⚠️ Veuillez sélectionner un directeur pour le TC")
                return
            
            # Créer l'utilisateur
            with st.spinner("Création de l'utilisateur en cours..."):
                success, message = UserController.create_user(
                    email=email,
                    nom=nom,
                    prenom=prenom,
                    role=role,
                    region=region,
                    directeur_id=directeur_id,
                    budget_alloue=budget_alloue
                )
            
            if success:
                st.success("✅ Utilisateur créé avec succès!")
                st.info(message)  # Affiche le mot de passe temporaire
                st.balloons()
                
                # Afficher résumé
                st.markdown("#### 📋 Résumé de l'utilisateur créé:")
                st.markdown(f"""
                - **Email:** {email}
                - **Nom:** {prenom} {nom}
                - **Rôle:** {get_role_label(role)}
                - **Région:** {region or 'N/A'}
                - **Budget:** {budget_alloue:,.0f}€
                """)
                
                if role == 'tc' and directeur_id:
                    dr_info = next((dr for dr in UserController.get_directors() if dr['id'] == directeur_id), None)
                    if dr_info:
                        st.markdown(f"- **Directeur:** {dr_info['prenom']} {dr_info['nom']}")
                
                st.warning("⚠️ N'oubliez pas d'**activer** l'utilisateur dans la liste des utilisateurs")
            else:
                st.error(f"❌ Erreur lors de la création: {message}")

def _display_user_statistics():
    """Afficher les statistiques des utilisateurs"""
    st.markdown("### 📊 Statistiques des Utilisateurs")
    
    stats = UserController.get_user_statistics()
    
    if not stats:
        st.info("Aucune donnée disponible")
        return
    
    # Métriques générales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Total Utilisateurs", stats.get('total_users', 0))
    
    with col2:
        st.metric("✅ Utilisateurs Actifs", stats.get('active_users', 0))
    
    with col3:
        st.metric("❌ Utilisateurs Inactifs", stats.get('inactive_users', 0))
    
    # Répartition par rôle
    if stats.get('by_role'):
        st.markdown("#### 🎭 Répartition par Rôle")
        
        role_data = []
        for role, count in stats['by_role'].items():
            role_data.append({
                'Rôle': get_role_label(role),
                'Nombre': count,
                'Couleur': get_role_color(role)
            })
        
        role_df = pd.DataFrame(role_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(role_df[['Rôle', 'Nombre']], use_container_width=True)
        
        with col2:
            if len(role_df) > 0:
                import plotly.express as px
                fig = px.pie(
                    role_df, 
                    values='Nombre', 
                    names='Rôle',
                    color_discrete_sequence=[row['Couleur'] for _, row in role_df.iterrows()]
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    # Répartition par région
    if stats.get('by_region'):
        st.markdown("#### 🌍 Répartition par Région")
        
        region_data = pd.DataFrame(list(stats['by_region'].items()), columns=['Région', 'Nombre'])
        region_data = region_data[region_data['Région'].notna()]  # Exclure les valeurs nulles
        
        if not region_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(region_data, use_container_width=True)
            
            with col2:
                import plotly.express as px
                fig = px.bar(region_data, x='Région', y='Nombre', color='Nombre')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

def _display_export_options():
    """Options d'export des données utilisateurs"""
    st.markdown("### 📤 Export des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Données à Exporter")
        export_all = st.checkbox("Tous les utilisateurs", value=True)
        export_active_only = st.checkbox("Utilisateurs actifs uniquement", value=False)
        
        if st.button("📥 Générer Export Excel", type="primary", use_container_width=True):
            with st.spinner("Génération de l'export en cours..."):
                export_df = UserController.export_users()
                
                if not export_df.empty:
                    if export_active_only:
                        export_df = export_df[export_df['Actif'] == 'Oui']
                    
                    # Convertir en Excel
                    from io import BytesIO
                    import pandas as pd
                    
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, sheet_name='Utilisateurs', index=False)
                        
                        # Ajouter les statistiques
                        stats_df = pd.DataFrame([
                            ['Total utilisateurs', len(export_df)],
                            ['Date export', datetime.now().strftime('%d/%m/%Y %H:%M')],
                            ['Exporté par', AuthController.get_current_user()['email']]
                        ], columns=['Statistique', 'Valeur'])
                        
                        stats_df.to_excel(writer, sheet_name='Informations', index=False)
                    
                    st.download_button(
                        label="📥 Télécharger Excel",
                        data=buffer.getvalue(),
                        file_name=f"utilisateurs_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.success(f"✅ Export généré: {len(export_df)} utilisateur(s)")
                else:
                    st.error("❌ Aucune donnée à exporter")
    
    with col2:
        st.markdown("#### ℹ️ Informations Export")
        st.info("""
        **Contenu de l'export:**
        - Informations personnelles (nom, prénom, email)
        - Rôle et région
        - Statut (actif/inactif)
        - Date de création
        - Budget alloué
        
        **Formats disponibles:**
        - Excel (.xlsx) avec feuilles multiples
        - Statistiques incluses
        """)
        
        # Aperçu des données
        preview_df = UserController.export_users()
        if not preview_df.empty:
            st.markdown("#### 👀 Aperçu des données")
            st.dataframe(preview_df.head(3), use_container_width=True)
