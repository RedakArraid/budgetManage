"""
Utilitaires pour la gestion des filtres dans l'application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class FilterManager:
    """Gestionnaire centralisé des filtres pour toutes les pages"""
    
    @staticmethod
    def init_session_filters(page_prefix: str, default_filters: Dict[str, Any]):
        """Initialise les filtres dans la session state"""
        for filter_name, default_value in default_filters.items():
            session_key = f"{page_prefix}_{filter_name}"
            if session_key not in st.session_state:
                st.session_state[session_key] = default_value
    
    @staticmethod
    def get_filter_value(page_prefix: str, filter_name: str, default: Any = ''):
        """Récupère la valeur d'un filtre depuis la session state"""
        session_key = f"{page_prefix}_{filter_name}"
        return st.session_state.get(session_key, default)
    
    @staticmethod
    def set_filter_value(page_prefix: str, filter_name: str, value: Any):
        """Met à jour la valeur d'un filtre dans la session state"""
        session_key = f"{page_prefix}_{filter_name}"
        st.session_state[session_key] = value
    
    @staticmethod
    def clear_filters(page_prefix: str, filter_names: List[str], default_values: Dict[str, Any]):
        """Efface tous les filtres d'une page"""
        for filter_name in filter_names:
            session_key = f"{page_prefix}_{filter_name}"
            default_value = default_values.get(filter_name, '')
            st.session_state[session_key] = default_value
    
    @staticmethod
    def apply_text_search(df: pd.DataFrame, search_query: str, search_columns: List[str]) -> pd.DataFrame:
        """Applique une recherche textuelle sur plusieurs colonnes"""
        if not search_query or df.empty:
            return df
        
        search_query = search_query.lower()
        mask = pd.Series(False, index=df.index)
        
        for column in search_columns:
            if column in df.columns:
                mask |= df[column].astype(str).str.lower().str.contains(search_query, na=False)
        
        return df[mask]
    
    @staticmethod
    def apply_status_filter(df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
        """Applique un filtre par statut"""
        if status_filter == 'tous' or not status_filter or df.empty:
            return df
        return df[df['status'] == status_filter]
    
    @staticmethod
    def apply_type_filter(df: pd.DataFrame, type_filter: str) -> pd.DataFrame:
        """Applique un filtre par type de demande"""
        if type_filter == 'tous' or not type_filter or df.empty:
            return df
        return df[df.get('type_demande', '') == type_filter]
    
    @staticmethod
    def apply_amount_filter(df: pd.DataFrame, amount_filter: str) -> pd.DataFrame:
        """Applique un filtre par montant"""
        if amount_filter == 'tous' or not amount_filter or df.empty:
            return df
        
        if amount_filter == 'moins_1000':
            return df[df['montant'] < 1000]
        elif amount_filter == '1000_5000':
            return df[(df['montant'] >= 1000) & (df['montant'] <= 5000)]
        elif amount_filter == '5000_10000':
            return df[(df['montant'] >= 5000) & (df['montant'] <= 10000)]
        elif amount_filter == 'plus_5000':
            return df[df['montant'] > 5000]
        elif amount_filter == 'plus_10000':
            return df[df['montant'] > 10000]
        
        return df
    
    @staticmethod
    def apply_urgency_filter(df: pd.DataFrame, urgency_filter: str) -> pd.DataFrame:
        """Applique un filtre par urgence"""
        if urgency_filter == 'toutes' or not urgency_filter or df.empty:
            return df
        return df[df.get('urgence', 'normale') == urgency_filter]
    
    @staticmethod
    def apply_period_filter(df: pd.DataFrame, period_filter: str, date_column: str = 'created_at') -> pd.DataFrame:
        """Applique un filtre par période"""
        if period_filter == 'toutes' or not period_filter or df.empty or date_column not in df.columns:
            return df
        
        try:
            # Convertir la colonne de date
            df[date_column] = pd.to_datetime(df[date_column])
            now = datetime.now()
            
            if period_filter == 'ce_mois':
                debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                return df[df[date_column] >= debut_mois]
            elif period_filter == '3_mois':
                trois_mois_avant = now - timedelta(days=90)
                return df[df[date_column] >= trois_mois_avant]
            elif period_filter == '6_mois':
                six_mois_avant = now - timedelta(days=180)
                return df[df[date_column] >= six_mois_avant]
            elif period_filter == 'cette_annee':
                debut_annee = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                return df[df[date_column] >= debut_annee]
            
        except Exception as e:
            st.warning(f"Erreur lors du filtrage par période: {e}")
        
        return df
    
    @staticmethod
    def apply_cy_filter(df: pd.DataFrame, cy_filter: str) -> pd.DataFrame:
        """Applique un filtre par année civile (cy)"""
        if cy_filter == 'tous' or not cy_filter or df.empty:
            return df
        
        # Vérifier si la colonne cy existe
        if 'cy' not in df.columns:
            st.warning("⚠️ Les données CY ne sont pas encore disponibles. Exécutez d'abord le script de déploiement.")
            return df
        
        try:
            cy_value = int(cy_filter)
            # Filtrer en gérant les valeurs nulles
            return df[df['cy'].fillna(0) == cy_value]
        except (ValueError, TypeError):
            return df
    
    @staticmethod
    def apply_by_filter(df: pd.DataFrame, by_filter: str) -> pd.DataFrame:
        """Applique un filtre par année fiscale (by)"""
        if by_filter == 'tous' or not by_filter or df.empty:
            return df
        
        # Vérifier si la colonne by existe
        if 'by' not in df.columns:
            st.warning("⚠️ Les données BY ne sont pas encore disponibles. Exécutez d'abord le script de déploiement.")
            return df
        
        # Filtrer en gérant les valeurs nulles
        return df[df['by'].fillna('') == by_filter]

class FilterUI:
    """Interface utilisateur pour les filtres"""
    
    @staticmethod
    def create_search_input(page_prefix: str, placeholder: str = "Rechercher...") -> str:
        """Crée un champ de recherche textuelle"""
        current_value = FilterManager.get_filter_value(page_prefix, 'search_query')
        
        search_query = st.text_input(
            "Rechercher",
            value=current_value,
            placeholder=placeholder,
            key=f"{page_prefix}_search_input",
            help="Recherche dans le nom, client, lieu, etc."
        )
        
        if search_query != current_value:
            FilterManager.set_filter_value(page_prefix, 'search_query', search_query)
        
        return search_query
    
    @staticmethod
    def create_status_filter(page_prefix: str) -> str:
        """Crée un filtre par statut"""
        status_options = {
            'tous': 'Tous les statuts',
            'brouillon': 'Brouillon',
            'en_attente_dr': 'Attente DR',
            'en_attente_financier': 'Attente Financier',
            'validee': 'Validée',
            'rejetee': 'Rejetée'
        }
        
        current_value = FilterManager.get_filter_value(page_prefix, 'status_filter', 'tous')
        
        status_filter = st.selectbox(
            "Statut",
            options=list(status_options.keys()),
            index=list(status_options.keys()).index(current_value),
            format_func=lambda x: status_options[x],
            key=f"{page_prefix}_status_select"
        )
        
        if status_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'status_filter', status_filter)
        
        return status_filter
    
    @staticmethod
    def create_type_filter(page_prefix: str) -> str:
        """Crée un filtre par type"""
        type_options = {
            'tous': 'Tous types',
            'budget': 'Budget',
            'marketing': 'Marketing'
        }
        
        current_value = FilterManager.get_filter_value(page_prefix, 'type_filter', 'tous')
        
        type_filter = st.selectbox(
            "Type",
            options=list(type_options.keys()),
            index=list(type_options.keys()).index(current_value),
            format_func=lambda x: type_options[x],
            key=f"{page_prefix}_type_select"
        )
        
        if type_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'type_filter', type_filter)
        
        return type_filter
    
    @staticmethod
    def create_amount_filter(page_prefix: str, include_large: bool = True) -> str:
        """Crée un filtre par montant"""
        amount_options = {
            'tous': 'Tous montants',
            'moins_1000': '< 1 000€',
            '1000_5000': '1 000 - 5 000€'
        }
        
        if include_large:
            amount_options.update({
                '5000_10000': '5 000 - 10 000€',
                'plus_10000': '> 10 000€'
            })
        else:
            amount_options['plus_5000'] = '> 5 000€'
        
        current_value = FilterManager.get_filter_value(page_prefix, 'montant_filter', 'tous')
        
        # Vérifier que la valeur actuelle existe dans les options
        if current_value not in amount_options:
            current_value = 'tous'
        
        amount_filter = st.selectbox(
            "Montant",
            options=list(amount_options.keys()),
            index=list(amount_options.keys()).index(current_value),
            format_func=lambda x: amount_options[x],
            key=f"{page_prefix}_amount_select"
        )
        
        if amount_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'montant_filter', amount_filter)
        
        return amount_filter
    
    @staticmethod
    def create_urgency_filter(page_prefix: str) -> str:
        """Crée un filtre par urgence"""
        urgency_options = ['toutes', 'normale', 'urgent', 'critique']
        current_value = FilterManager.get_filter_value(page_prefix, 'urgence_filter', 'toutes')
        
        urgency_filter = st.selectbox(
            "Urgence",
            options=urgency_options,
            index=urgency_options.index(current_value),
            key=f"{page_prefix}_urgency_select"
        )
        
        if urgency_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'urgence_filter', urgency_filter)
        
        return urgency_filter
    
    @staticmethod
    def create_period_filter(page_prefix: str) -> str:
        """Crée un filtre par période"""
        period_options = {
            'toutes': 'Toutes périodes',
            'ce_mois': 'Ce mois',
            '3_mois': '3 derniers mois',
            '6_mois': '6 derniers mois',
            'cette_annee': 'Cette année'
        }
        
        current_value = FilterManager.get_filter_value(page_prefix, 'periode_filter', 'toutes')
        
        period_filter = st.selectbox(
            "Période",
            options=list(period_options.keys()),
            index=list(period_options.keys()).index(current_value),
            format_func=lambda x: period_options[x],
            key=f"{page_prefix}_period_select"
        )
        
        if period_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'periode_filter', period_filter)
        
        return period_filter
    
    @staticmethod
    def get_available_cy_options():
        """Récupère les années civiles disponibles dans les demandes"""
        try:
            from models.database import db
            from utils.spinner_utils import SpinnerMessages, loading_spinner
            
            # Afficher un spinner pendant le chargement
            with loading_spinner(SpinnerMessages.FILTERS_LOADING_CY):
                # Récupérer toutes les valeurs cy distinctes
                result = db.execute_query(
                    "SELECT DISTINCT cy FROM demandes WHERE cy IS NOT NULL ORDER BY cy DESC",
                    fetch='all'
                )
                
                # Convertir en liste d'années
                available_years = [str(row['cy']) for row in result if row['cy']]
                
                # Construire les options
                year_options = {'tous': 'Toutes années'}
                for year in available_years:
                    year_options[year] = year
                    
                return year_options
            
        except Exception as e:
            print(f"Erreur récupération cy: {e}")
            # Fallback vers les années par défaut
            from datetime import datetime
            current_year = datetime.now().year
            year_options = {'tous': 'Toutes années'}
            for year in range(current_year - 2, current_year + 3):
                year_options[str(year)] = str(year)
            return year_options
    
    @staticmethod
    def get_available_by_options():
        """Récupère les années fiscales disponibles dans les demandes"""
        try:
            from models.database import db
            from utils.spinner_utils import SpinnerMessages, loading_spinner
            
            # Afficher un spinner pendant le chargement
            with loading_spinner(SpinnerMessages.FILTERS_LOADING_BY):
                # Récupérer toutes les valeurs by distinctes
                result = db.execute_query(
                    "SELECT DISTINCT by FROM demandes WHERE by IS NOT NULL ORDER BY by DESC",
                    fetch='all'
                )
                
                # Convertir en liste d'années fiscales
                available_by = [row['by'] for row in result if row['by']]
                
                # Construire les options avec labels complets
                by_options = {'tous': 'Toutes années fiscales'}
                for by_value in available_by:
                    # Convertir 23/24 en 2023/2024 pour l'affichage
                    try:
                        parts = by_value.split('/')
                        if len(parts) == 2:
                            year_start = int(f"20{parts[0]}")
                            year_end = int(f"20{parts[1]}")
                            by_options[by_value] = f"{year_start}/{year_end}"
                        else:
                            by_options[by_value] = by_value
                    except:
                        by_options[by_value] = by_value
                        
                return by_options
            
        except Exception as e:
            print(f"Erreur récupération by: {e}")
            # Fallback vers les années fiscales par défaut
            from datetime import datetime
            current_year = datetime.now().year
            by_options = {'tous': 'Toutes années fiscales'}
            for year in range(current_year - 2, current_year + 3):
                by_value = f"{str(year)[2:]}/{str(year + 1)[2:]}"
                by_options[by_value] = f"{year}/{year + 1}"
            return by_options
        
    @staticmethod
    def create_cy_filter(page_prefix: str) -> str:
        """Crée un filtre par année civile (cy) basé sur les données réelles"""
        # Récupérer les options disponibles
        year_options = FilterUI.get_available_cy_options()
        
        current_value = FilterManager.get_filter_value(page_prefix, 'cy_filter', 'tous')
        
        # Vérifier que la valeur actuelle existe toujours
        if current_value not in year_options:
            current_value = 'tous'
        
        cy_filter = st.selectbox(
            "Année civile",
            options=list(year_options.keys()),
            index=list(year_options.keys()).index(current_value),
            format_func=lambda x: year_options[x],
            key=f"{page_prefix}_cy_select",
            help="Filtre par année de la date d'événement"
        )
        
        if cy_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'cy_filter', cy_filter)
        
        return cy_filter
    
    @staticmethod
    def create_by_filter(page_prefix: str) -> str:
        """Crée un filtre par année fiscale (by) basé sur les données réelles"""
        # Récupérer les options disponibles
        by_options = FilterUI.get_available_by_options()
        
        current_value = FilterManager.get_filter_value(page_prefix, 'by_filter', 'tous')
        
        # Vérifier que la valeur actuelle existe toujours
        if current_value not in by_options:
            current_value = 'tous'
        
        by_filter = st.selectbox(
            "Année fiscale",
            options=list(by_options.keys()),
            index=list(by_options.keys()).index(current_value),
            format_func=lambda x: by_options[x],
            key=f"{page_prefix}_by_select",
            help="Filtre par année fiscale (mai à avril)"
        )
        
        if by_filter != current_value:
            FilterManager.set_filter_value(page_prefix, 'by_filter', by_filter)
        
        return by_filter
    
    @staticmethod
    def create_filter_actions(page_prefix: str, filter_names: List[str], default_values: Dict[str, Any]):
        """Crée les boutons d'action pour les filtres"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Actualiser", use_container_width=True, key=f"{page_prefix}_refresh"):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Effacer Filtres", use_container_width=True, key=f"{page_prefix}_clear"):
                FilterManager.clear_filters(page_prefix, filter_names, default_values)
                st.rerun()

def apply_combined_filters(df: pd.DataFrame, filters: Dict[str, str], search_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Applique tous les filtres de manière combinée"""
    filtered_df = df.copy()
    
    # Recherche textuelle
    if 'search_query' in filters and search_columns:
        filtered_df = FilterManager.apply_text_search(filtered_df, filters['search_query'], search_columns)
    
    # Filtre par statut
    if 'status_filter' in filters:
        filtered_df = FilterManager.apply_status_filter(filtered_df, filters['status_filter'])
    
    # Filtre par type
    if 'type_filter' in filters:
        filtered_df = FilterManager.apply_type_filter(filtered_df, filters['type_filter'])
    
    # Filtre par montant
    if 'montant_filter' in filters:
        filtered_df = FilterManager.apply_amount_filter(filtered_df, filters['montant_filter'])
    
    # Filtre par urgence
    if 'urgence_filter' in filters:
        filtered_df = FilterManager.apply_urgency_filter(filtered_df, filters['urgence_filter'])
    
    # Filtre par période
    if 'periode_filter' in filters:
        filtered_df = FilterManager.apply_period_filter(filtered_df, filters['periode_filter'])
    
    # Filtre par année civile (cy)
    if 'cy_filter' in filters:
        filtered_df = FilterManager.apply_cy_filter(filtered_df, filters['cy_filter'])
    
    # Filtre par année fiscale (by)
    if 'by_filter' in filters:
        filtered_df = FilterManager.apply_by_filter(filtered_df, filters['by_filter'])
    
    return filtered_df
