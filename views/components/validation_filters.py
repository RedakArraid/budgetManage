"""
Composant de filtres pour la page des validations
"""
import streamlit as st
from utils.filters import FilterUI, FilterManager, apply_combined_filters

def display_validation_filters():
    """Affiche des filtres pour les validations"""
    # Initialiser les filtres avec des valeurs par défaut
    default_filters = {
        'search_query': '',
        'urgence_filter': 'toutes',
        'montant_filter': 'tous',
        'type_filter': 'tous'
    }
    
    FilterManager.init_session_filters('validation', default_filters)
    
    with st.expander("🔍 Filtres", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_query = FilterUI.create_search_input('validation', "Nom, client, lieu...")
        
        with col2:
            urgence_filter = FilterUI.create_urgency_filter('validation')
        
        with col3:
            montant_filter = FilterUI.create_amount_filter('validation', include_large=False)
        
        with col4:
            type_filter = FilterUI.create_type_filter('validation')
    
    # Boutons d'action pour les filtres
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Actualiser Validations", use_container_width=True, key="validation_filters_refresh"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Effacer Filtres", use_container_width=True, key="validation_filters_clear"):
            filter_names = list(default_filters.keys())
            FilterManager.clear_filters('validation', filter_names, default_filters)
            st.rerun()

def apply_validation_filters(df):
    """Applique les filtres aux demandes de validation"""
    # Récupérer les valeurs des filtres
    filters = {
        'search_query': FilterManager.get_filter_value('validation', 'search_query'),
        'urgence_filter': FilterManager.get_filter_value('validation', 'urgence_filter'),
        'montant_filter': FilterManager.get_filter_value('validation', 'montant_filter'),
        'type_filter': FilterManager.get_filter_value('validation', 'type_filter')
    }
    
    # Colonnes de recherche textuelle
    search_columns = [
        'nom_manifestation', 'client', 'lieu', 'prenom', 'nom', 'email'
    ]
    
    return apply_combined_filters(df, filters, search_columns)
