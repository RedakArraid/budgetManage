"""
Version simplifiée des filtres pour demandes_view.py
"""
import streamlit as st
from utils.filters import FilterUI, FilterManager, apply_combined_filters

def display_simplified_filters():
    """Affiche des filtres simplifiés et robustes"""
    # Initialiser les filtres avec des valeurs par défaut
    default_filters = {
        'search_query': '',
        'status_filter': 'tous',
        'type_filter': 'tous',
        'montant_filter': 'tous',
        'cy_filter': 'tous',
        'by_filter': 'tous'
    }
    
    FilterManager.init_session_filters('demandes', default_filters)
    
    with st.expander("🔍 Filtres et Recherche", expanded=True):
        # Première ligne de filtres
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_query = FilterUI.create_search_input('demandes', "Nom, client, lieu...")
        
        with col2:
            status_filter = FilterUI.create_status_filter('demandes')
        
        with col3:
            type_filter = FilterUI.create_type_filter('demandes')
        
        with col4:
            montant_filter = FilterUI.create_amount_filter('demandes', include_large=True)
        
        # Deuxième ligne pour les nouveaux filtres cy et by
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            cy_filter = FilterUI.create_cy_filter('demandes')
        
        with col6:
            by_filter = FilterUI.create_by_filter('demandes')
        
        with col7:
            st.write("")  # Colonne vide
        
        with col8:
            st.write("")  # Colonne vide
    
    # Actions rapides
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Actualiser", use_container_width=True, key="demandes_filters_refresh"):
            st.rerun()
    
    with col2:
        filter_names = list(default_filters.keys())
        if st.button("🗑️ Effacer Filtres", use_container_width=True, key="demandes_filters_clear"):
            FilterManager.clear_filters('demandes', filter_names, default_filters)
            st.rerun()
    
    with col3:
        from controllers.auth_controller import AuthController
        user_role = AuthController.get_current_user()['role']
        if user_role in ['tc', 'dr', 'marketing']:
            if st.button("➕ Nouvelle Demande", use_container_width=True, type="primary", key="demandes_filters_new"):
                st.session_state.page = "nouvelle_demande"
                st.rerun()

def apply_demandes_filters(df):
    """Applique les filtres aux demandes"""
    from utils.spinner_utils import OperationFeedback
    
    with OperationFeedback.apply_filters():
        # Récupérer les valeurs des filtres
        filters = {
            'search_query': FilterManager.get_filter_value('demandes', 'search_query'),
            'status_filter': FilterManager.get_filter_value('demandes', 'status_filter'),
            'type_filter': FilterManager.get_filter_value('demandes', 'type_filter'),
            'montant_filter': FilterManager.get_filter_value('demandes', 'montant_filter'),
            'cy_filter': FilterManager.get_filter_value('demandes', 'cy_filter'),
            'by_filter': FilterManager.get_filter_value('demandes', 'by_filter')
        }
        
        # Colonnes de recherche textuelle
        search_columns = [
            'nom_manifestation', 'client', 'lieu', 'budget', 'categorie', 
            'prenom', 'nom', 'email', 'typologie_client', 'groupe_groupement'
        ]
        
        return apply_combined_filters(df, filters, search_columns)
