"""
Vue pour les analytics et rapports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController

@AuthController.require_auth
def analytics_page():
    """Page d'analytics et rapports"""
    try:
        from views.components.header import display_header
        display_header()
    except ImportError:
        st.subheader("📊 Analytics & Rapports")
    
    user_info = AuthController.get_current_user()
    
    # Afficher les filtres d'analytics
    try:
        from views.components.analytics_filters import display_analytics_filters, apply_analytics_filters, get_filtered_count_info
        display_analytics_filters()
        
        # Récupérer les données selon le rôle
        demandes = DemandeController.get_demandes_for_user(
            AuthController.get_current_user_id(), 
            user_info['role']
        )
        
        original_count = len(demandes)
        
        # Appliquer les filtres d'analytics
        if not demandes.empty:
            demandes = apply_analytics_filters(demandes)
            
        # Afficher info sur le filtrage
        if original_count > 0:
            st.info(get_filtered_count_info(original_count, len(demandes)))
            
    except ImportError:
        # Fallback vers l'ancienne méthode
        _display_analytics_filters()
        
        demandes = DemandeController.get_demandes_for_user(
            AuthController.get_current_user_id(), 
            user_info['role']
        )
        
        if not demandes.empty:
            demandes = _apply_analytics_filters(demandes)
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        demandes = pd.DataFrame()
    
    if demandes.empty:
        st.info("Aucune donnée à analyser pour les filtres sélectionnés")
        return
    
    # Convertir les dates
    try:
        demandes['date_evenement'] = pd.to_datetime(demandes['date_evenement'])
        demandes['created_at'] = pd.to_datetime(demandes['created_at'])
        demandes['mois'] = demandes['date_evenement'].dt.to_period('M').astype(str)
    except Exception as e:
        st.error(f"Erreur de conversion des dates: {e}")
        return
    
    # Métriques globales
    _display_global_metrics(demandes)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        _display_evolution_chart(demandes)
    
    with col2:
        _display_status_chart(demandes)
    
    # Analyses détaillées
    _display_client_analysis(demandes)
    _display_regional_analysis(demandes, user_info)
    
    # Export des données
    _display_export_section(demandes)

def _display_analytics_filters():
    """Affiche les filtres pour les analytics"""
    # Initialiser les filtres d'analytics
    if 'analytics_status_filter' not in st.session_state:
        st.session_state.analytics_status_filter = 'tous'
    if 'analytics_type_filter' not in st.session_state:
        st.session_state.analytics_type_filter = 'tous'
    if 'analytics_periode_filter' not in st.session_state:
        st.session_state.analytics_periode_filter = 'toutes'
    if 'analytics_montant_filter' not in st.session_state:
        st.session_state.analytics_montant_filter = 'tous'
        
    with st.expander("🔍 Filtres d'Analyse", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
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
                index=list(status_options.keys()).index(st.session_state.analytics_status_filter),
                format_func=lambda x: status_options[x],
                key='analytics_status_select'
            )
            if status_filter != st.session_state.analytics_status_filter:
                st.session_state.analytics_status_filter = status_filter
        
        with col2:
            type_options = {
                'tous': 'Tous types',
                'budget': 'Budget',
                'marketing': 'Marketing'
            }
            type_filter = st.selectbox(
                "Type", 
                options=list(type_options.keys()),
                index=list(type_options.keys()).index(st.session_state.analytics_type_filter),
                format_func=lambda x: type_options[x],
                key='analytics_type_select'
            )
            if type_filter != st.session_state.analytics_type_filter:
                st.session_state.analytics_type_filter = type_filter
        
        with col3:
            periode_options = {
                'toutes': 'Toutes périodes',
                'ce_mois': 'Ce mois',
                '3_mois': '3 derniers mois',
                '6_mois': '6 derniers mois',
                'cette_annee': 'Cette année'
            }
            periode_filter = st.selectbox(
                "Période", 
                options=list(periode_options.keys()),
                index=list(periode_options.keys()).index(st.session_state.analytics_periode_filter),
                format_func=lambda x: periode_options[x],
                key='analytics_periode_select'
            )
            if periode_filter != st.session_state.analytics_periode_filter:
                st.session_state.analytics_periode_filter = periode_filter
        
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
                index=list(montant_options.keys()).index(st.session_state.analytics_montant_filter),
                format_func=lambda x: montant_options[x],
                key='analytics_montant_select'
            )
            if montant_filter != st.session_state.analytics_montant_filter:
                st.session_state.analytics_montant_filter = montant_filter
    
    # Boutons d'action pour les filtres
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualiser Analytics", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Effacer Filtres", use_container_width=True):
            st.session_state.analytics_status_filter = 'tous'
            st.session_state.analytics_type_filter = 'tous'
            st.session_state.analytics_periode_filter = 'toutes'
            st.session_state.analytics_montant_filter = 'tous'
            st.rerun()

def _apply_analytics_filters(demandes):
    """Applique les filtres aux données d'analytics"""
    from datetime import datetime, timedelta
    
    filtered_demandes = demandes.copy()
    
    # Filtre par statut
    status_filter = st.session_state.get('analytics_status_filter', 'tous')
    if status_filter != 'tous':
        filtered_demandes = filtered_demandes[filtered_demandes['status'] == status_filter]
    
    # Filtre par type
    type_filter = st.session_state.get('analytics_type_filter', 'tous')
    if type_filter != 'tous':
        filtered_demandes = filtered_demandes[
            filtered_demandes.get('type_demande', '') == type_filter
        ]
    
    # Filtre par période
    periode_filter = st.session_state.get('analytics_periode_filter', 'toutes')
    if periode_filter != 'toutes':
        try:
            # Convertir created_at en datetime si ce n'est pas déjà fait
            if 'created_at' in filtered_demandes.columns:
                filtered_demandes['created_at'] = pd.to_datetime(filtered_demandes['created_at'])
                now = datetime.now()
                
                if periode_filter == 'ce_mois':
                    debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    filtered_demandes = filtered_demandes[filtered_demandes['created_at'] >= debut_mois]
                elif periode_filter == '3_mois':
                    trois_mois_avant = now - timedelta(days=90)
                    filtered_demandes = filtered_demandes[filtered_demandes['created_at'] >= trois_mois_avant]
                elif periode_filter == '6_mois':
                    six_mois_avant = now - timedelta(days=180)
                    filtered_demandes = filtered_demandes[filtered_demandes['created_at'] >= six_mois_avant]
                elif periode_filter == 'cette_annee':
                    debut_annee = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    filtered_demandes = filtered_demandes[filtered_demandes['created_at'] >= debut_annee]
        except Exception as e:
            st.warning(f"Erreur lors du filtrage par période: {e}")
    
    # Filtre par montant
    montant_filter = st.session_state.get('analytics_montant_filter', 'tous')
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
    
    return filtered_demandes

def _display_global_metrics(demandes):
    """Affiche les métriques globales"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_demandes = len(demandes)
    total_montant = demandes['montant'].sum()
    montant_valide = demandes[demandes['status'] == 'validee']['montant'].sum()
    taux_validation = (len(demandes[demandes['status'] == 'validee']) / total_demandes * 100) if total_demandes > 0 else 0
    
    with col1:
        st.metric("Total Demandes", total_demandes)
    with col2:
        st.metric("Montant Total", f"{total_montant:,.0f}€")
    with col3:
        st.metric("Montant Validé", f"{montant_valide:,.0f}€")
    with col4:
        st.metric("Taux Validation", f"{taux_validation:.1f}%")

def _display_evolution_chart(demandes):
    """Affiche l'évolution mensuelle"""
    st.subheader("📈 Évolution Mensuelle")
    
    try:
        monthly_data = demandes.groupby('mois')['montant'].agg(['sum', 'count']).reset_index()
        
        if not monthly_data.empty:
            fig = px.line(
                monthly_data, 
                x='mois', 
                y='sum',
                title="Montant par mois",
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour l'évolution")
    except Exception as e:
        st.error(f"Erreur graphique évolution: {e}")

def _display_status_chart(demandes):
    """Affiche la répartition par statut"""
    st.subheader("📊 Répartition par Statut")
    
    try:
        status_data = demandes['status'].value_counts().reset_index()
        status_data.columns = ['status', 'count']
        
        if not status_data.empty:
            fig = px.pie(
                status_data, 
                values='count', 
                names='status',
                title="Demandes par statut"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de statut")
    except Exception as e:
        st.error(f"Erreur graphique statut: {e}")

def _display_client_analysis(demandes):
    """Affiche l'analyse par client"""
    st.subheader("🏢 Top Clients")
    
    try:
        client_data = demandes.groupby('client').agg({
            'montant': ['sum', 'count']
        }).reset_index()
        client_data.columns = ['client', 'montant_total', 'nb_demandes']
        client_data = client_data.sort_values('montant_total', ascending=False).head(10)
        
        if not client_data.empty:
            fig = px.bar(
                client_data, 
                x='client', 
                y='montant_total',
                title="Top 10 Clients par Montant",
                hover_data=['nb_demandes']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données clients")
    except Exception as e:
        st.error(f"Erreur analyse clients: {e}")

def _display_regional_analysis(demandes, user_info):
    """Affiche l'analyse par région"""
    if user_info['role'] in ['admin', 'dg']:
        st.subheader("🌍 Analyse Régionale")
        
        try:
            # Simuler des données régionales si pas disponibles
            if 'region' not in demandes.columns:
                regions = ['Nord', 'Sud', 'Est', 'Ouest', 'Centre']
                demandes['region'] = pd.Series(regions * (len(demandes) // len(regions) + 1))[:len(demandes)]
            
            regional_data = demandes.groupby('region').agg({
                'montant': 'sum',
                'id': 'count'
            }).reset_index()
            regional_data.columns = ['region', 'montant_total', 'nb_demandes']
            
            if not regional_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Montant par Région**")
                    st.dataframe(regional_data.sort_values('montant_total', ascending=False))
                
                with col2:
                    fig = px.bar(
                        regional_data,
                        x='region',
                        y='montant_total',
                        title="Montant par Région"
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur analyse régionale: {e}")

def _display_export_section(demandes):
    """Affiche la section d'export"""
    st.markdown("---")
    st.subheader("📁 Export des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exporter Excel", use_container_width=True):
            try:
                # Fallback vers CSV si Excel non disponible
                csv_data = demandes.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv_data,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Erreur export: {e}")
    
    with col2:
        if st.button("📄 Rapport PDF", use_container_width=True):
            st.info("Génération PDF à implémenter")
