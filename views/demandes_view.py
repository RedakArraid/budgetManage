"""
Vue pour la gestion des demandes
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from config.settings import get_status_info
from utils.date_utils import format_date
from utils.spinner_utils import OperationFeedback

@AuthController.require_auth
def demandes_page():
    """Page de gestion des demandes"""
    try:
        from views.components.header import display_header
        display_header()
    except ImportError:
        st.subheader("📋 Gestion des Demandes")
    
    user_info = AuthController.get_current_user()
    
    # Filtres et recherche (version simplifiée)
    try:
        from views.components.demandes_filters import display_simplified_filters, apply_demandes_filters
        display_simplified_filters()
        
        # Récupérer toutes les demandes d'abord
        with OperationFeedback.load_demandes():
            demandes = DemandeController.get_demandes_for_user(
                user_id=AuthController.get_current_user_id(),
                role=user_info['role']
            )
        
        # Appliquer les filtres
        if not demandes.empty:
            demandes = apply_demandes_filters(demandes)
            
    except ImportError:
        # Fallback vers l'ancienne méthode si le composant n'est pas disponible
        _display_filters()
        
        search_query = st.session_state.get('demandes_search_query', '')
        status_filter = st.session_state.get('demandes_status_filter', 'tous')
        type_filter = st.session_state.get('demandes_type_filter', 'tous')
        montant_filter = st.session_state.get('demandes_montant_filter', 'tous')
        
        demandes = DemandeController.get_demandes_for_user(
            user_id=AuthController.get_current_user_id(),
            role=user_info['role'],
            search_query=search_query,
            status_filter=status_filter if status_filter != 'tous' else ''
        )
        
        if not demandes.empty:
            demandes = _apply_filters(demandes, type_filter, montant_filter, search_query)
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des demandes: {e}")
        demandes = pd.DataFrame()
    
    if demandes.empty:
        st.info("Aucune demande trouvée")
        _display_no_demandes_help()
        return
    
    # Statistiques rapides
    _display_quick_stats(demandes)
    
    # Affichage des demandes
    _display_cards_view(demandes, user_info)

def _apply_filters(demandes, type_filter, montant_filter, search_query):
    """Applique les filtres supplémentaires aux demandes"""
    filtered_demandes = demandes.copy()
    
    # Filtre par type
    if type_filter != 'tous':
        filtered_demandes = filtered_demandes[filtered_demandes['type_demande'] == type_filter]
    
    # Filtre par montant
    if montant_filter != 'tous':
        if montant_filter == 'moins_1000':
            filtered_demandes = filtered_demandes[filtered_demandes['montant'] < 1000]
        elif montant_filter == '1000_5000':
            filtered_demandes = filtered_demandes[
                (filtered_demandes['montant'] >= 1000) & (filtered_demandes['montant'] <= 5000)
            ]
        elif montant_filter == '5000_10000':
            filtered_demandes = filtered_demandes[
                (filtered_demandes['montant'] >= 5000) & (filtered_demandes['montant'] <= 10000)
            ]
        elif montant_filter == 'plus_10000':
            filtered_demandes = filtered_demandes[filtered_demandes['montant'] > 10000]
    
    # Recherche textuelle avancée (si pas déjà appliquée côté serveur)
    if search_query:
        search_query = search_query.lower()
        mask = (
            filtered_demandes['nom_manifestation'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes['client'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes['lieu'].str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('budget', '').astype(str).str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('categorie', '').astype(str).str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('prenom', '').astype(str).str.lower().str.contains(search_query, na=False) |
            filtered_demandes.get('nom', '').astype(str).str.lower().str.contains(search_query, na=False)
        )
        filtered_demandes = filtered_demandes[mask]
    
    return filtered_demandes

def _display_filters():
    """Affiche les filtres de recherche"""
    # Initialiser les valeurs par défaut si elles n'existent pas
    if 'demandes_search_query' not in st.session_state:
        st.session_state.demandes_search_query = ''
    if 'demandes_status_filter' not in st.session_state:
        st.session_state.demandes_status_filter = 'tous'
    if 'demandes_type_filter' not in st.session_state:
        st.session_state.demandes_type_filter = 'tous'
    if 'demandes_montant_filter' not in st.session_state:
        st.session_state.demandes_montant_filter = 'tous'
        
    with st.expander("🔍 Filtres et Recherche", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_query = st.text_input(
                "Rechercher", 
                value=st.session_state.demandes_search_query,
                placeholder="Nom, client, lieu...",
                key='demandes_search_input',
                help="Recherche dans le nom, client, lieu, etc."
            )
            # Mettre à jour la session state
            if search_query != st.session_state.demandes_search_query:
                st.session_state.demandes_search_query = search_query
        
        with col2:
            status_options = {
                'tous': 'Tous les statuts',
                'brouillon': 'Brouillon',
                'en_attente_dr': 'Attente DR',
                'en_attente_financier': 'Attente Financier',
                'validee': 'Validée',
                'rejetee': 'Rejetée'
            }
            status_filter = st.selectbox(
                "Statut", 
                options=list(status_options.keys()),
                index=list(status_options.keys()).index(st.session_state.demandes_status_filter),
                format_func=lambda x: status_options[x],
                key='demandes_status_select'
            )
            # Mettre à jour la session state
            if status_filter != st.session_state.demandes_status_filter:
                st.session_state.demandes_status_filter = status_filter
        
        with col3:
            type_options = {
                'tous': 'Tous types',
                'budget': 'Budget',
                'marketing': 'Marketing'
            }
            type_filter = st.selectbox(
                "Type", 
                options=list(type_options.keys()),
                index=list(type_options.keys()).index(st.session_state.demandes_type_filter),
                format_func=lambda x: type_options[x],
                key='demandes_type_select'
            )
            # Mettre à jour la session state
            if type_filter != st.session_state.demandes_type_filter:
                st.session_state.demandes_type_filter = type_filter
        
        with col4:
            montant_options = {
                'tous': 'Tous montants',
                'moins_1000': '< 1 000€',
                '1000_5000': '1 000 - 5 000€',
                '5000_10000': '5 000 - 10 000€',
                'plus_10000': '> 10 000€'
            }
            montant_filter = st.selectbox(
                "Montant", 
                options=list(montant_options.keys()),
                index=list(montant_options.keys()).index(st.session_state.demandes_montant_filter),
                format_func=lambda x: montant_options[x],
                key='demandes_montant_select'
            )
            # Mettre à jour la session state
            if montant_filter != st.session_state.demandes_montant_filter:
                st.session_state.demandes_montant_filter = montant_filter
    
    # Actions rapides
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Actualiser", use_container_width=True, key="demandes_simple_refresh"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Effacer Filtres", use_container_width=True, key="demandes_clear_filters"):
            st.session_state.demandes_search_query = ''
            st.session_state.demandes_status_filter = 'tous'
            st.session_state.demandes_type_filter = 'tous'
            st.session_state.demandes_montant_filter = 'tous'
            st.rerun()
    
    with col3:
        user_role = AuthController.get_current_user()['role']
        if user_role in ['tc', 'dr', 'marketing']:
            if st.button("➕ Nouvelle Demande", use_container_width=True, type="primary", key="demandes_simple_new"):
                st.session_state.page = "nouvelle_demande"
                st.rerun()

def _display_quick_stats(demandes):
    """Affiche des statistiques rapides"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_montant = demandes['montant'].sum()
    montant_valide = demandes[demandes['status'] == 'validee']['montant'].sum()
    en_attente = len(demandes[demandes['status'].str.contains('attente', na=False)])
    taux_validation = (len(demandes[demandes['status'] == 'validee']) / len(demandes) * 100) if len(demandes) > 0 else 0
    
    with col1:
        st.metric("Montant Total", f"{total_montant:,.0f}€")
    with col2:
        st.metric("Montant Validé", f"{montant_valide:,.0f}€")
    with col3:
        st.metric("En Attente", en_attente)
    with col4:
        st.metric("Taux Validation", f"{taux_validation:.1f}%")

def _display_cards_view(demandes, user_info):
    """Affiche les demandes en mode cartes"""
    for idx, row in demandes.iterrows():
        status_info = get_status_info(row['status'])
        
        with st.expander(
            f"{status_info['icon']} {row['nom_manifestation']} - {row['montant']:,.0f}€",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                # Utiliser la nouvelle transformation pour les régions
                from models.dropdown_options import DropdownOptionsModel
                
                display_labels = {
                    'budget': row.get('budget', 'Non spécifié'),
                    'categorie': row.get('categorie', 'Non spécifié'),
                    'typologie_client': row.get('typologie_client', 'Non spécifié'),
                    'groupe_groupement': row.get('groupe_groupement', 'Non spécifié'),
                    'region': DropdownOptionsModel.get_region_display_value(row.get('region', '')) if row.get('region') else 'Non spécifié'
                }
                
                st.markdown(f"""
                **📝 Détails:**
                - **Client:** {row['client']}
                - **Date événement:** {format_date(row['date_evenement'])}
                - **Année civile (CY):** {row.get('cy', 'N/A')}
                - **Année fiscale (BY):** {row.get('by', 'N/A')}
                - **Lieu:** {row['lieu']}
                - **Montant:** {row['montant']:,.0f}€
                - **Type:** {row['type_demande'].title()}
                - **Budget:** {display_labels['budget']}
                - **Catégorie:** {display_labels['categorie']}
                - **Typologie Client:** {display_labels['typologie_client']}
                - **Groupe/Groupement:** {display_labels['groupe_groupement']}
                - **Région:** {display_labels['region']}
                - **Agence:** {row['agence']}
                - **Client/Enseigne:** {row['client_enseigne']}
                - **Email Contact:** {row['mail_contact']}
                - **Nom Contact:** {row['nom_contact']}
                """)
                
                # Afficher les nouveaux participants
                try:
                    from views.components.participants_advanced import display_participants_readonly
                    
                    # Créer un conteneur pour l'affichage des participants
                    participants_container = st.container()
                    with participants_container:
                        display_participants_readonly(
                            row['id'], 
                            {'prenom': row['prenom'], 'nom': row['nom'], 'role': row.get('user_role', 'tc')},
                            row.get('demandeur_participe', True),
                            row.get('participants_libres', '')
                        )
                        
                except ImportError:
                    # Fallback vers l'ancien affichage
                    if row.get('participants'):
                        st.markdown(f"**👥 Participants (ancien):** {row['participants']}")
                    
                    # Afficher les participants libres s'ils existent
                    if row.get('participants_libres'):
                        st.markdown(f"**👥 Autres participants:** {row.get('participants_libres')}")
            
            with col2:
                st.markdown(f"""
                **👤 Informations:**
                - **Demandeur:** {row['prenom']} {row['nom']}
                - **Email:** {row['email']}
                - **Statut:** {status_info['label']}
                - **Créée le:** {format_date(row['created_at'])}
                - **Modifiée le:** {format_date(row['updated_at'])}
                """)
            
            if row.get('commentaires'):
                st.markdown(f"**💭 Commentaires:** {row['commentaires']}")
            
            # Actions disponibles
            _display_demande_actions(row, user_info)
            
            # Add delete button for admins
            if user_info['role'] == 'admin':
                with st.form(key=f'delete_demande_form_{row['id']}', clear_on_submit=True):
                    st.write("⚠️ **Danger Zone**")
                    if st.form_submit_button("Supprimer la demande", type="secondary", help="Supprimer définitivement cette demande (action irréversible)"):
                         with OperationFeedback.delete_demande():
                            success, message = DemandeController.admin_delete_demande(row['id'], user_info['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

def _display_demande_actions(row, user_info):
    """Affiche les actions disponibles pour une demande"""
    col1, col2, col3, col4 = st.columns(4)
    user_id = AuthController.get_current_user_id()
    
    # Actions selon le statut et le rôle
    if row['status'] == 'brouillon' and row['user_id'] == user_id:
        with col1:
            if st.button("📤 Soumettre", key=f"submit_{row['id']}", use_container_width=True):
                _handle_submit_demande(row['id'])
        
        with col2:
            if st.button("✏️ Modifier", key=f"edit_{row['id']}", use_container_width=True):
                st.session_state.edit_demande_id = row['id']
                st.session_state.page = "modifier_demande"
                st.rerun()
        
        with col3:
            if st.button("🗑️ Supprimer", key=f"delete_{row['id']}", use_container_width=True):
                _handle_delete_demande(row['id'])
    
    elif (row['status'] == 'en_attente_dr' and 
          user_info['role'] == 'dr'):
        
        with col1:
            if st.button("✅ Valider", key=f"validate_dr_{row['id']}", use_container_width=True):
                _handle_dr_validation(row['id'], 'valider')
        
        with col2:
            if st.button("❌ Rejeter", key=f"reject_dr_{row['id']}", use_container_width=True):
                _handle_dr_validation(row['id'], 'rejeter')
    
    elif (row['status'] == 'en_attente_financier' and 
          user_info['role'] in ['dr_financier', 'dg']):
        
        with col1:
            if st.button("✅ Valider", key=f"fin_validate_{row['id']}", use_container_width=True):
                _handle_financial_validation(row['id'], 'valider')
        
        with col2:
            if st.button("❌ Rejeter", key=f"fin_reject_{row['id']}", use_container_width=True):
                _handle_financial_validation(row['id'], 'rejeter')
    
    elif row['status'] == 'validee':
        with col1:
            if st.button("📧 Email Client", key=f"mail_{row['id']}", use_container_width=True):
                st.info("Fonctionnalité d'email à implémenter")
        
        with col2:
            if st.button("📄 Rapport", key=f"report_{row['id']}", use_container_width=True):
                st.info("Génération de rapport à implémenter")

def _display_no_demandes_help():
    """Affiche de l'aide quand aucune demande n'est trouvée"""
    user_info = AuthController.get_current_user()
    
    st.markdown("---")
    st.markdown("### 💡 Pour commencer")
    
    if user_info['role'] in ['tc', 'dr', 'marketing']:
        if st.button("➕ Créer ma première demande", use_container_width=True, type="primary"):
            st.session_state.page = "nouvelle_demande"
            st.rerun()
    
    st.markdown("""    
    **Conseils:**
    - Utilisez les filtres pour affiner votre recherche
    - Vérifiez les permissions selon votre rôle
    - Contactez votre administrateur en cas de problème
    """)

# Fonctions de gestion des actions
def _handle_submit_demande(demande_id):
    """Gère la soumission d'une demande"""
    with st.spinner("Soumission en cours..."):
        try:
            success, message = DemandeController.submit_demande(
                demande_id, AuthController.get_current_user_id()
            )
            
            if success:
                st.success("✅ Demande soumise avec succès!")
                st.rerun()
            else:
                st.error(f"❌ {message}")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")

def _handle_delete_demande(demande_id):
    """Gère la suppression d'une demande"""
    if st.session_state.get(f'confirm_delete_{demande_id}'):
        with st.spinner("Suppression en cours..."):
            try:
                success = DemandeController.delete_demande(demande_id, AuthController.get_current_user_id())
                
                if success:
                    st.success("✅ Demande supprimée!")
                    del st.session_state[f'confirm_delete_{demande_id}']
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la suppression")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    else:
        st.warning("⚠️ Confirmer la suppression")
        if st.button("Oui, supprimer", key=f"confirm_delete_btn_{demande_id}"):
            st.session_state[f'confirm_delete_{demande_id}'] = True
            st.rerun()

def _handle_dr_validation(demande_id, action):
    """Gère la validation DR"""
    with st.form(f"dr_validation_{demande_id}_{action}"):
        commentaire = st.text_area(
            f"Commentaire {action}" if action == 'valider' else "Motif du rejet (obligatoire)",
            placeholder="Votre commentaire..."
        )
        
        submitted = st.form_submit_button(f"{action.title()} la demande")
        
        if submitted:
            if action == 'rejeter' and not commentaire:
                st.error("Un motif de rejet est obligatoire")
                return
            
            with st.spinner(f"{action.title()} en cours..."):
                try:
                    success, message = DemandeController.validate_demande(
                        demande_id, AuthController.get_current_user_id(), action, commentaire
                    )
                    
                    if success:
                        st.success(f"✅ Demande {action}ée avec succès!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

def _handle_financial_validation(demande_id, action):
    """Gère la validation financière"""
    with st.form(f"fin_validation_{demande_id}_{action}"):
        commentaire = st.text_area(
            f"Commentaire financier" if action == 'valider' else "Motif du rejet (obligatoire)",
            placeholder="Votre commentaire..."
        )
        
        submitted = st.form_submit_button(f"{action.title()} la demande")
        
        if submitted:
            if action == 'rejeter' and not commentaire:
                st.error("Un motif de rejet est obligatoire")
                return
            
            with st.spinner(f"{action.title()} en cours..."):
                try:
                    success, message = DemandeController.validate_demande(
                        demande_id, AuthController.get_current_user_id(), action, commentaire
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
