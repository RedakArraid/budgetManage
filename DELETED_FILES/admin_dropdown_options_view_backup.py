"""
Vue d'administration pour la gestion des listes déroulantes
"""
import streamlit as st
import pandas as pd
from controllers.auth_controller import AuthController
from models.dropdown_options import DropdownOptionsModel

@AuthController.require_role(['admin'])
def admin_dropdown_options_page():
    """Page d'administration des listes déroulantes"""
    from views.components.header import display_header
    
    display_header()
    
    st.title("🎛️ Gestion des Listes Déroulantes")
    st.markdown("Interface d'administration pour gérer toutes les options des listes déroulantes")
    
    # Onglets pour organiser les fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Gestion des Options", 
        "➕ Ajouter Option", 
        "📊 Statistiques",
        "🔍 Recherche"
    ])
    
    with tab1:
        _manage_options_tab()
    
    with tab2:
        _add_option_tab()
    
    with tab3:
        _statistics_tab()
    
    with tab4:
        _search_tab()

def _manage_options_tab():
    """Onglet de gestion des options"""
    st.subheader("📋 Gestion des Options Existantes")
    
    # Sélecteur de catégorie
    categories = {
        'budget': '💸 Budget',
        'categorie': '📂 Catégorie', 
        'typologie_client': '🏷️ Typologie Client',
        'groupe_groupement': '👥 Groupe/Groupement',
        'region': '🌍 Région',
        'agence': '🏢 Agence'
    }
    
    selected_category = st.selectbox(
        "Choisir une catégorie à gérer",
        options=list(categories.keys()),
        format_func=lambda x: categories[x]
    )
    
    if selected_category:
        st.markdown(f"### {categories[selected_category]}")
        
        # Récupérer les options pour cette catégorie
        options = DropdownOptionsModel.get_options_for_category(selected_category)
        
        if not options:
            st.info("Aucune option dans cette catégorie")
            return
        
        # Afficher les options avec possibilité de modification
        for idx, option in enumerate(options):
            with st.expander(f"{option['label']} {'✅' if option.get('is_active', True) else '❌'}", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    new_label = st.text_input(
                        "Libellé", 
                        value=option['label'],
                        key=f"label_{option['id']}"
                    )
                
                with col2:
                    new_order = st.number_input(
                        "Ordre",
                        value=option['order_index'],
                        min_value=1,
                        key=f"order_{option['id']}"
                    )
                
                with col3:
                    is_active = st.checkbox(
                        "Actif",
                        value=option.get('is_active', True),
                        key=f"active_{option['id']}"
                    )
                
                with col4:
                    col_update, col_delete = st.columns(2)
                    
                    with col_update:
                        if st.button("💾 Modifier", key=f"update_{option['id']}", use_container_width=True):
                            success, message = DropdownOptionsModel.update_option(
                                option['id'], 
                                label=new_label,
                                order_index=new_order,
                                is_active=is_active
                            )
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col_delete:
                        if st.button("🗑️ Supprimer", key=f"delete_{option['id']}", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_{option['id']}", False):
                                success, message = DropdownOptionsModel.delete_option(option['id'])
                                
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.session_state[f"confirm_delete_{option['id']}"] = True
                                st.warning("Cliquez à nouveau pour confirmer la suppression")

def _add_option_tab():
    """Onglet d'ajout d'option avec système centralisé"""
    st.subheader("➕ Ajouter une Nouvelle Option")
    
    # Importer le système centralisé
    from utils.dropdown_manager import DropdownCentralManager
    
    st.info("🎯 **Système Centralisé Activé** - Les valeurs sont automatiquement normalisées")
    
    categories = {
        'budget': '💸 Budget',
        'categorie': '📂 Catégorie', 
        'typologie_client': '🏷️ Typologie Client',
        'groupe_groupement': '👥 Groupe/Groupement',
        'region': '🌍 Région'
    }
    
    with st.form("add_option_form_centralized"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Catégorie*",
                options=list(categories.keys()),
                format_func=lambda x: categories[x]
            )
            
            label = st.text_input(
                "Libellé affiché*",
                placeholder="Ex: NORD EST, Animation Client, SALES",
                help="Ce qui sera affiché à l'utilisateur"
            )
        
        with col2:
            # Afficher l'aperçu de normalisation EN TEMPS RÉEL
            if label:
                normalized_value = DropdownCentralManager.normalize_label_to_value(label)
                st.text_input(
                    "Valeur stockée (auto-générée)",
                    value=normalized_value,
                    disabled=True,
                    help="Générée automatiquement : minuscule + espaces → _"
                )
            else:
                st.text_input(
                    "Valeur stockée (auto-générée)",
                    value="",
                    disabled=True,
                    help="Saisissez d'abord un libellé"
                )
            
            order_index = st.number_input(
                "Position dans la liste",
                min_value=1,
                value=1,
                help="Plus le numéro est petit, plus l'option apparaît en haut"
            )
        
        # Validation en temps réel
        errors = []
        if label and len(label.strip()) < 2:
            errors.append("Le libellé doit contenir au moins 2 caractères")
        
        if label:
            normalized_value = DropdownCentralManager.normalize_label_to_value(label)
            if not normalized_value:
                errors.append("Impossible de générer une valeur valide à partir du libellé")
        
        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
        
        # Aperçu de la transformation
        if label and not errors:
            st.markdown("### 🔎 Aperçu de la Transformation")
            normalized_value = DropdownCentralManager.normalize_label_to_value(label)
            
            col_before, col_arrow, col_after = st.columns([2, 1, 2])
            with col_before:
                st.code(f"Libellé: '{label}'")
            with col_arrow:
                st.markdown("<div style='text-align: center; font-size: 24px;'>→</div>", unsafe_allow_html=True)
            with col_after:
                st.code(f"Valeur: '{normalized_value}'")
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            submit_btn = st.form_submit_button(
                "✅ Ajouter l'Option",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.form_submit_button("🔄 Réinitialiser", use_container_width=True):
                st.rerun()
    
    # Traitement du formulaire
    if submit_btn:
        if not all([category, label]):
            st.error("⚠️ Veuillez remplir tous les champs obligatoires")
            return
        
        if errors:
            st.error("⚠️ Veuillez corriger les erreurs avant de continuer")
            return
        
        # Utiliser le système centralisé pour créer l'option
        success, message = DropdownCentralManager.create_option_from_admin(
            category, label.strip(), order_index
        )
        
        if success:
            st.success(f"✅ Option créée avec succès!")
            st.balloons()
            
            # Afficher un aperçu détaillé
            normalized_value = DropdownCentralManager.normalize_label_to_value(label)
            
            st.markdown("### 👁️ Résumé de l'Option Créée")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Catégorie:** {categories[category]}")
                st.info(f"**Libellé affiché:** {label}")
            with col2:
                st.info(f"**Valeur stockée:** {normalized_value}")
                st.info(f"**Position:** {order_index}")
                
            st.success("🔒 Cette option est maintenant la SEULE façon d'utiliser cette valeur dans le système")
        else:
            st.error(f"❌ {message}")

def _statistics_tab():
    """Onglet des statistiques"""
    st.subheader("📊 Statistiques des Listes Déroulantes")
    
    # Statistiques par catégorie
    stats = DropdownOptionsModel.get_category_stats()
    
    if stats:
        df_stats = pd.DataFrame(stats)
        
        # Renommer les colonnes pour l'affichage
        df_stats['Catégorie'] = df_stats['category'].map({
            'budget': '💸 Budget',
            'categorie': '📂 Catégorie', 
            'typologie_client': '🏷️ Typologie Client',
            'groupe_groupement': '👥 Groupe/Groupement',
            'region': '🌍 Région',
            'agence': '🏢 Agence'
        })
        
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_options = df_stats['total'].sum()
            st.metric("Total Options", total_options)
        
        with col2:
            total_active = df_stats['active'].sum()
            st.metric("Options Actives", total_active)
        
        with col3:
            total_inactive = df_stats['inactive'].sum()
            st.metric("Options Inactives", total_inactive)
        
        with col4:
            nb_categories = len(df_stats)
            st.metric("Catégories", nb_categories)
        
        # Tableau détaillé
        st.markdown("### 📈 Détail par Catégorie")
        
        # Préparer le dataframe pour l'affichage
        display_df = df_stats[['Catégorie', 'total', 'active', 'inactive']].copy()
        display_df.columns = ['Catégorie', 'Total', 'Actives', 'Inactives']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Graphique
        import plotly.express as px
        
        fig = px.bar(
            df_stats, 
            x='Catégorie', 
            y=['active', 'inactive'],
            title="Répartition des Options par Catégorie",
            color_discrete_map={'active': '#28a745', 'inactive': '#dc3545'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Aucune donnée statistique disponible")

def _search_tab():
    """Onglet de recherche"""
    st.subheader("🔍 Recherche dans les Options")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "Terme de recherche",
            placeholder="Rechercher dans les libellés ou valeurs..."
        )
    
    with col2:
        category_filter = st.selectbox(
            "Filtrer par catégorie",
            options=[''] + list({
                'budget': '💸 Budget',
                'categorie': '📂 Catégorie', 
                'typologie_client': '🏷️ Typologie Client',
                'groupe_groupement': '👥 Groupe/Groupement',
                'region': '🌍 Région',
                'agence': '🏢 Agence'
            }.keys()),
            format_func=lambda x: "Toutes les catégories" if x == '' else {
                'budget': '💸 Budget',
                'categorie': '📂 Catégorie', 
                'typologie_client': '🏷️ Typologie Client',
                'groupe_groupement': '👥 Groupe/Groupement',
                'region': '🌍 Région',
                'agence': '🏢 Agence'
            }[x]
        )
    
    if search_term:
        # Effectuer la recherche
        results = DropdownOptionsModel.search_options(
            search_term, 
            category_filter if category_filter else None
        )
        
        if not results.empty:
            st.markdown(f"### 📋 Résultats ({len(results)} trouvés)")
            
            # Afficher les résultats
            for _, row in results.iterrows():
                status_icon = "✅" if row['is_active'] else "❌"
                category_icon = {
                    'budget': '💸',
                    'categorie': '📂', 
                    'typologie_client': '🏷️',
                    'groupe_groupement': '👥',
                    'region': '🌍',
                    'agence': '🏢'
                }.get(row['category'], '📁')
                
                with st.expander(f"{status_icon} {category_icon} {row['label']} ({row['category']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Libellé:** {row['label']}")
                        st.markdown(f"**Valeur:** `{row['value']}`")
                    
                    with col2:
                        st.markdown(f"**Catégorie:** {row['category']}")
                        st.markdown(f"**Position:** {row['order_index']}")
                    
                    with col3:
                        st.markdown(f"**Statut:** {'Actif' if row['is_active'] else 'Inactif'}")
                        
                        # Boutons d'action rapide
                        if st.button(f"✏️ Modifier", key=f"edit_search_{row['id']}"):
                            st.session_state.edit_option_id = row['id']
                            st.session_state.page = "admin_dropdown_options"
                            st.rerun()
        else:
            st.info("Aucun résultat trouvé pour cette recherche")
    
    else:
        st.info("💡 Saisissez un terme de recherche pour commencer")
        
        # Afficher quelques exemples
        st.markdown("### 💡 Exemples de recherche")
        st.markdown("- `Marketing` - Trouve toutes les options contenant 'Marketing'")
        st.markdown("- `Paris` - Trouve les agences ou régions contenant 'Paris'")
        st.markdown("- `Budget` - Trouve toutes les options liées au budget")

def _export_import_section():
    """Section d'export/import (bonus)"""
    st.markdown("---")
    st.subheader("📤📥 Export / Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Exporter les Options")
        if st.button("💾 Exporter vers Excel", use_container_width=True):
            # Récupérer toutes les options
            df = DropdownOptionsModel.get_all_options()
            
            if not df.empty:
                # Créer le fichier Excel
                from io import BytesIO
                buffer = BytesIO()
                
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Options', index=False)
                
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Télécharger le fichier Excel",
                    data=buffer.getvalue(),
                    file_name=f"dropdown_options_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Aucune donnée à exporter")
    
    with col2:
        st.markdown("#### 📥 Importer des Options")
        st.info("Fonctionnalité disponible prochainement")
