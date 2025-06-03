"""
Composant de filtres pour la page des analytics
"""
import streamlit as st
from utils.filters import FilterUI, FilterManager, apply_combined_filters

def display_analytics_filters():
    """Affiche des filtres pour les analytics"""
    # Initialiser les filtres avec des valeurs par défaut
    default_filters = {
        'status_filter': 'tous',
        'type_filter': 'tous',
        'periode_filter': 'toutes',
        'montant_filter': 'tous'
    }
    
    FilterManager.init_session_filters('analytics', default_filters)
    
    with st.expander("🔍 Filtres d'Analyse", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = FilterUI.create_status_filter('analytics')
        
        with col2:
            type_filter = FilterUI.create_type_filter('analytics')
        
        with col3:
            periode_filter = FilterUI.create_period_filter('analytics')
        
        with col4:
            montant_filter = FilterUI.create_amount_filter('analytics', include_large=True)
    
    # Boutons d'action pour les filtres
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Actualiser Analytics", use_container_width=True, key="analytics_refresh"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Effacer Filtres", use_container_width=True, key="analytics_clear"):
            filter_names = list(default_filters.keys())
            FilterManager.clear_filters('analytics', filter_names, default_filters)
            st.rerun()

def apply_analytics_filters(df):
    """Applique les filtres aux données d'analytics"""
    # Récupérer les valeurs des filtres
    filters = {
        'status_filter': FilterManager.get_filter_value('analytics', 'status_filter'),
        'type_filter': FilterManager.get_filter_value('analytics', 'type_filter'),
        'periode_filter': FilterManager.get_filter_value('analytics', 'periode_filter'),
        'montant_filter': FilterManager.get_filter_value('analytics', 'montant_filter')
    }
    
    return apply_combined_filters(df, filters)

def get_filtered_count_info(original_count, filtered_count):
    """Retourne un message informatif sur le filtrage"""
    if filtered_count != original_count:
        return f"🔍 {filtered_count} élément(s) sur {original_count} après filtrage"
    return f"📊 {original_count} élément(s) au total"
