"""
Vue d'administration SIMPLIFIÉE pour la gestion des listes déroulantes
CRUD complet avec répercussion directe sur les demandes
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.auth_controller import AuthController
from models.dropdown_options import DropdownOptionsModel
from models.database import db

def _get_usage_count(category: str, value: str) -> int:
    """
    Obtient le nombre d'utilisations d'une valeur dans les demandes
    Gère le mapping des catégories vers les bonnes colonnes
    """
    try:
        # Mapping des catégories vers les colonnes de la table demandes
        column_mapping = {
            'budget': 'budget',
            'categorie': 'categorie',
            'typologie_client': 'typologie_client',
            'groupe_groupement': 'groupe_groupement',
            'region': 'region',
            'annee_fiscale': None  # Cas spécial - pas de colonne directe
        }
        
        column_name = column_mapping.get(category)
        
        if column_name is None:
            # Pour annee_fiscale, on ne peut pas compter directement
            # car il n'y a pas de colonne annee_fiscale dans demandes
            if category == 'annee_fiscale':
                # On pourrait vérifier fiscal_year mais c'est complexe avec la conversion
                # Pour l'instant, on retourne 0
                return 0
            else:
                return None
        
        # Vérifier si la colonne existe dans la table demandes
        columns_info = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        existing_columns = [col['name'] for col in columns_info]
        
        if column_name not in existing_columns:
            return None
        
        # Compter les utilisations
        result = db.execute_query(f'''
            SELECT COUNT(*) FROM demandes WHERE {column_name} = ?
        ''', (value,), fetch='one')
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Erreur _get_usage_count pour {category}={value}: {e}")
        return None

def _display_fiscal_year_assistant():
    """
    Assistant spécialisé pour la gestion des années fiscales
    Logique métier: BY25 = Mai 2024 à Avril 2025
    """
    st.markdown("### 📅 Assistant Années Fiscales")
    st.markdown("📝 **Logique métier**: BY25 = Mai 2024 à Avril 2025 (année fiscale commence en Mai)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✨ Générer Années Standard", use_container_width=True):
            _generate_standard_fiscal_years()
    
    with col2:
        if st.button("🗑️ Supprimer Toutes", use_container_width=True):
            _delete_all_fiscal_years()
    
    with col3:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            _reset_fiscal_years()
    
    # Ajout manuel rapide
    st.markdown("#### ➕ Ajout Manuel Rapide")
    
    with st.form("quick_fiscal_year_add"):
        col_year, col_add = st.columns([3, 1])
        
        with col_year:
            from datetime import datetime
            current_year = datetime.now().year
            
            start_year = st.number_input(
                "Année de début de période fiscale",
                min_value=2015,
                max_value=2035,
                value=current_year,
                help="Ex: 2024 pour la période Mai 2024 - Avril 2025 (BY25)"
            )
        
        with col_add:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaceur
            submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
        
        if submitted:
            _add_single_fiscal_year(start_year)

def _generate_standard_fiscal_years():
    """Génère les années fiscales standard (BY20 à BY30)"""
    try:
        from utils.fiscal_year_utils import year_to_byxx, get_fiscal_year_display
        
        # Générer les années 2019-2029 (BY20 à BY30)
        success_count = 0
        
        for start_year in range(2019, 2030):
            byxx_code = year_to_byxx(start_year)
            label = get_fiscal_year_display(byxx_code)
            order_index = start_year - 2018  # 2019=1, 2020=2, etc.
            
            try:
                # Ajouter directement sans auto-normalisation pour les années fiscales
                db.execute_query("""
                    INSERT OR IGNORE INTO dropdown_options 
                    (category, value, label, order_index, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, ('annee_fiscale', byxx_code, label, order_index, True))
                success_count += 1
            except Exception as e:
                st.error(f"❌ Erreur {byxx_code}: {e}")
        
        st.success(f"✅ {success_count} années fiscales générées (BY20 à BY30)")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur génération: {e}")

def _delete_all_fiscal_years():
    """Supprime toutes les années fiscales"""
    try:
        deleted_count = db.execute_query("""
            DELETE FROM dropdown_options WHERE category = 'annee_fiscale'
        """)
        
        st.success(f"✅ {deleted_count} années fiscales supprimées")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur suppression: {e}")

def _reset_fiscal_years():
    """Réinitialise complètement les années fiscales"""
    try:
        # Supprimer puis regénérer
        _delete_all_fiscal_years()
        _generate_standard_fiscal_years()
        
        st.success("✅ Années fiscales réinitialisées avec succès!")
        
    except Exception as e:
        st.error(f"❌ Erreur réinitialisation: {e}")

def _add_single_fiscal_year(start_year):
    """Ajoute une seule année fiscale"""
    try:
        from utils.fiscal_year_utils import year_to_byxx, get_fiscal_year_display
        
        byxx_code = year_to_byxx(start_year)
        label = get_fiscal_year_display(byxx_code)
        order_index = start_year - 2018
        
        # Ajouter directement sans auto-normalisation pour les années fiscales
        rows_affected = db.execute_query("""
            INSERT OR IGNORE INTO dropdown_options 
            (category, value, label, order_index, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, ('annee_fiscale', byxx_code, label, order_index, True))
        
        if rows_affected > 0:
            st.success(f"✅ Année ajoutée: {label}")
            st.rerun()
        else:
            st.warning(f"⚠️ {byxx_code} existe déjà")
            
    except Exception as e:
        st.error(f"❌ Erreur ajout: {e}")

@AuthController.require_role(['admin'])
def admin_dropdown_options_page():
    """Page UNIQUE de gestion des listes déroulantes - CRUD complet"""
    from views.components.header import display_header
    
    display_header()
    
    st.title("🎛️ Gestion des Listes Déroulantes")
    
    # Onglets simplifiés
    tab1, tab2, tab3 = st.tabs([
        "📋 Gérer les Options", 
        "➕ Ajouter Option",
        "📊 Impact sur les Demandes"
    ])
    
    with tab1:
        _crud_options_tab()
    
    with tab2:
        _add_option_simple_tab()
    
    with tab3:
        _impact_demandes_tab()

def _crud_options_tab():
    """Onglet CRUD complet des options avec manipulation directe de la base"""
    st.subheader("📋 CRUD des Options - Base Directe")
    
    from models.database import db
    
    # Sélecteur de catégorie
    categories = {
        'budget': '💸 Budget',
        'categorie': '📂 Catégorie', 
        'typologie_client': '🏷️ Typologie Client',
        'groupe_groupement': '👥 Groupe/Groupement',
        'region': '🌍 Région',
        'annee_fiscale': '📅 Année Fiscale'
    }
    
    selected_category = st.selectbox(
        "📂 Choisir une catégorie à gérer",
        options=list(categories.keys()),
        format_func=lambda x: categories[x]
    )
    
    if not selected_category:
        st.warning("Veuillez sélectionner une catégorie")
        return
    
    st.markdown(f"### {categories[selected_category]}")
    
    # Récupération DIRECTE depuis la base de données
    try:
        raw_options = db.execute_query('''
            SELECT id, category, value, label, order_index, is_active, 
                   created_at, updated_at
            FROM dropdown_options 
            WHERE category = ?
            ORDER BY order_index ASC, label ASC
        ''', (selected_category,), fetch='all')
        
        # Convertir en liste de dictionnaires
        options = [dict(row) for row in raw_options] if raw_options else []
        
    except Exception as e:
        st.error(f"❌ Erreur accès base: {e}")
        return
    
    if not options:
        st.info(f"Aucune option dans {categories[selected_category]}")
        st.markdown("➕ Utilisez l'onglet 'Ajouter Option' pour créer la première option")
        return
    
    # État de la base
    st.markdown(f"**📊 {len(options)} option(s) en base** - Dernière actualisation: {datetime.now().strftime('%H:%M:%S')}")
    
    # Actions globales sur la base
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✅ Activer Toutes", key=f"activate_all_{selected_category}", use_container_width=True):
            try:
                count = db.execute_query('''
                    UPDATE dropdown_options 
                    SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
                    WHERE category = ?
                ''', (selected_category,))
                st.success(f"✅ {count} options activées")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    with col2:
        if st.button("❌ Désactiver Toutes", key=f"deactivate_all_{selected_category}", use_container_width=True):
            try:
                count = db.execute_query('''
                    UPDATE dropdown_options 
                    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE category = ?
                ''', (selected_category,))
                st.success(f"✅ {count} options désactivées")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    with col3:
        if st.button("🔄 Actualiser", key=f"refresh_crud_{selected_category}", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button("🗑️ Tout Supprimer", key=f"delete_all_{selected_category}", use_container_width=True):
            if st.session_state.get(f"confirm_delete_all_{selected_category}", False):
                try:
                    count = db.execute_query('''
                        DELETE FROM dropdown_options WHERE category = ?
                    ''', (selected_category,))
                    st.success(f"✅ {count} options supprimées")
                    del st.session_state[f"confirm_delete_all_{selected_category}"]
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
            else:
                st.session_state[f"confirm_delete_all_{selected_category}"] = True
                st.warning("Cliquez encore pour confirmer la suppression TOTALE")
    
    # Tableau CRUD en temps réel
    st.markdown("---")
    
    # En-tête du tableau
    col_header = st.columns([1, 3, 2, 1, 1, 2, 2])
    with col_header[0]:
        st.markdown("**ID**")
    with col_header[1]:
        st.markdown("**Label**")
    with col_header[2]:
        st.markdown("**Valeur**")
    with col_header[3]:
        st.markdown("**Ordre**")
    with col_header[4]:
        st.markdown("**Actif**")
    with col_header[5]:
        st.markdown("**Utilisation**")
    with col_header[6]:
        st.markdown("**Actions**")
    
    st.markdown("---")
    
    # Interface spécialisée pour les années fiscales
    if selected_category == 'annee_fiscale':
        _display_fiscal_year_assistant()
        st.markdown("---")
        st.markdown("### 🚀 Assistant Années Fiscales")
        st.info("📝 Conseil: Utilisez l'assistant ci-dessus pour gérer facilement les années fiscales avec la vraie logique métier (BY25 = Mai 2024 - Avril 2025)")
    
    # CRUD ligne par ligne
    for option in options:
        col = st.columns([1, 3, 2, 1, 1, 2, 2])
        
        # ID
        with col[0]:
            st.text(f"#{option['id']}")
        
        # Label éditable
        with col[1]:
            new_label = st.text_input(
                "Label",
                value=option['label'],
                key=f"edit_label_{option['id']}",
                label_visibility="collapsed"
            )
        
        # Valeur (affichage avec auto-normalisation)
        with col[2]:
            if selected_category == 'annee_fiscale':
                # Pour les années fiscales, pas de normalisation - format BYXX attendu
                if option['value'].startswith('BY') and len(option['value']) == 4:
                    st.success(option['value'])
                else:
                    st.warning(f"{option['value']} ⚠️")
                    st.caption("Attendu: format BYXX (ex: BY24)")
            else:
                # Pour les autres catégories, utiliser la normalisation
                from utils.dropdown_value_normalizer import normalize_dropdown_value
                expected_value = normalize_dropdown_value(option['label'])
                if option['value'] == expected_value:
                    st.success(option['value'])
                else:
                    st.warning(f"{option['value']} ⚠️")
                    st.caption(f"Attendu: {expected_value}")
        
        # Ordre éditable
        with col[3]:
            new_order = st.number_input(
                "Ordre",
                value=int(option['order_index']),
                min_value=1,
                key=f"edit_order_{option['id']}",
                label_visibility="collapsed"
            )
        
        # Actif éditable
        with col[4]:
            is_active = st.checkbox(
                "Actif",
                value=bool(option['is_active']),
                key=f"edit_active_{option['id']}",
                label_visibility="collapsed"
            )
        
        # Utilisation en base
        with col[5]:
            usage_count = _get_usage_count(selected_category, option['value'])
            if usage_count is not None:
                if usage_count > 0:
                    st.caption(f"📊 {usage_count}x")
                else:
                    st.caption("📊 0x")
            else:
                st.caption("❓")
        
        # Actions
        with col[6]:
            col_save, col_del = st.columns(2)
            
            # Bouton sauvegarder avec auto-normalisation (sauf années fiscales)
            with col_save:
                if st.button("💾", key=f"save_db_{option['id']}", help="Sauvegarder"):
                    try:
                        # Désactiver l'auto-normalisation pour les années fiscales
                        auto_normalize = selected_category != 'annee_fiscale'
                        
                        success, message = DropdownOptionsModel.update_option(
                            option_id=option['id'],
                            label=new_label,
                            order_index=new_order,
                            is_active=is_active,
                            auto_normalize_value=auto_normalize
                        )
                        
                        if success:
                            st.success("✅ Sauvé!")
                        else:
                            st.error(f"❌ {message}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")
            
            # Bouton supprimer
            with col_del:
                confirm_key = f"confirm_del_db_{option['id']}"
                if st.button("🗑️", key=f"del_db_{option['id']}", help="Supprimer de la base"):
                    if st.session_state.get(confirm_key, False):
                        try:
                            success, message = DropdownOptionsModel.delete_option(option['id'])
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                            del st.session_state[confirm_key]
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                    else:
                        st.session_state[confirm_key] = True
                        st.warning("Cliquez encore pour confirmer")
        
        st.markdown("---")

def _add_option_simple_tab():
    """Onglet d'ajout simple d'option avec auto-génération de valeur"""
    st.subheader("➕ Ajouter une Option - Génération Automatique")
    
    from models.database import db
    from utils.dropdown_value_normalizer import normalize_dropdown_value, preview_normalization
    
    categories = {
        'budget': '💸 Budget',
        'categorie': '📂 Catégorie', 
        'typologie_client': '🏷️ Typologie Client',
        'groupe_groupement': '👥 Groupe/Groupement',
        'region': '🌍 Région',
        'annee_fiscale': '📅 Année Fiscale'
    }
    
    # Mode de saisie
    st.markdown("### 🎛️ Mode de Saisie")
    auto_mode = st.radio(
        "Comment voulez-vous définir la valeur ?",
        [
            "🤖 Génération automatique (recommandé)",
            "✏️ Saisie manuelle de la valeur"
        ],
        index=0,
        help="Le mode automatique génère la valeur selon : value = replace(lower(label), espaces par _)"
    )
    
    use_auto = auto_mode.startswith("🤖")
    
    with st.form("add_option_auto"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "📂 Catégorie*",
                options=list(categories.keys()),
                format_func=lambda x: categories[x]
            )
            
            label = st.text_input(
                "🏷️ Label affiché*",
                placeholder="Ex: NORD EST, ANIMATION CLIENT, SALES",
                help="Ce que l'utilisateur verra dans les formulaires"
            )
        
        with col2:
            if use_auto:
                # Mode automatique : aperçu en temps réel
                if label:
                    preview = preview_normalization(label)
                    value = preview['normalized']
                    
                    st.text_input(
                        "🔑 Valeur générée automatiquement",
                        value=value,
                        disabled=True,
                        help="Générée automatiquement - Non modifiable en mode auto"
                    )
                    
                    # Affichage de l'aperçu détaillé
                    if preview['warnings']:
                        for warning in preview['warnings']:
                            st.warning(f"⚠️ {warning}")
                    
                    if preview['valid']:
                        st.success("✅ Valeur valide")
                    else:
                        st.error("❌ Valeur invalide")
                else:
                    st.text_input(
                        "🔑 Valeur générée automatiquement",
                        value="",
                        disabled=True,
                        help="Saisissez d'abord un label"
                    )
                    value = ""
            else:
                # Mode manuel
                suggested_value = normalize_dropdown_value(label) if label else ""
                value = st.text_input(
                    "🔑 Valeur stockée*",
                    value=suggested_value,
                    help="Valeur unique stockée en base - format: minuscules_avec_underscores"
                )
            
            # Calcul automatique de l'ordre suivant
            if category:
                try:
                    max_order = db.execute_query('''
                        SELECT COALESCE(MAX(order_index), 0) + 1
                        FROM dropdown_options 
                        WHERE category = ?
                    ''', (category,), fetch='one')[0]
                except:
                    max_order = 1
            else:
                max_order = 1
            
            order_index = st.number_input(
                "📊 Position",
                min_value=1,
                value=max_order,
                help=f"Ordre d'affichage (prochain: {max_order})"
            )
        
        # Submit
        submitted = st.form_submit_button(
            f"✅ {'Auto-Générer et' if use_auto else 'Valider et'} Insérer en Base",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not label or not label.strip():
                st.error("❌ Le label est obligatoire")
            else:
                try:
                    with st.spinner("💾 Insertion en base de données..."):
                        success, message = DropdownOptionsModel.add_option(
                            category=category,
                            label=label,
                            order_index=order_index,
                            value=value if not use_auto else None,
                            auto_normalize=use_auto
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
                            
                except Exception as e:
                    st.error(f"❌ Erreur insertion en base: {e}")

    # Section migration
    st.markdown("---")
    st.markdown("### 🔄 Migration des Valeurs Existantes")
    
    col_migration = st.columns([1, 1, 1])
    
    with col_migration[0]:
        if st.button("🔍 Aperçu Migration", use_container_width=True):
            try:
                options = db.execute_query('''
                    SELECT id, category, value, label
                    FROM dropdown_options
                    ORDER BY category, id
                    LIMIT 10
                ''', fetch='all')
                
                if options:
                    st.markdown("**Aperçu des 10 premières options:**")
                    for opt in options:
                        current_value = opt['value']
                        new_value = normalize_dropdown_value(opt['label'])
                        
                        if current_value != new_value:
                            st.warning(f"ID #{opt['id']}: '{opt['label']}' → '{current_value}' ⇒ '{new_value}'")
                        else:
                            st.success(f"ID #{opt['id']}: '{opt['label']}' → '{current_value}' ✅")
            except Exception as e:
                st.error(f"Erreur aperçu: {e}")
    
    with col_migration[1]:
        if st.button("🔄 Exécuter Migration", use_container_width=True):
            try:
                success, message = DropdownOptionsModel.batch_normalize_existing_values()
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"Erreur migration: {e}")
    
    with col_migration[2]:
        if st.button("📊 Statistiques", use_container_width=True):
            try:
                stats = db.execute_query('''
                    SELECT category, COUNT(*) as total
                    FROM dropdown_options
                    GROUP BY category
                    ORDER BY category
                ''', fetch='all')
                
                if stats:
                    for stat in stats:
                        st.metric(
                            f"{categories.get(stat['category'], stat['category'])}",
                            f"{stat['total']} options"
                        )
            except Exception as e:
                st.error(f"Erreur stats: {e}")

def _impact_demandes_tab():
    """Onglet montrant l'impact sur les demandes avec données en temps réel"""
    st.subheader("📊 Impact sur les Demandes - Données Temps Réel")
    
    from models.database import db
    
    # Actualisation
    if st.button("🔄 Actualiser données", use_container_width=True):
        st.rerun()
    
    st.caption(f"Dernière actualisation: {datetime.now().strftime('%H:%M:%S')}")
    
    # Statistiques globales
    st.markdown("### 📊 Statistiques Globales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            total_options = db.execute_query(
                "SELECT COUNT(*) FROM dropdown_options WHERE is_active = 1", 
                fetch='one'
            )[0]
            st.metric("Options Actives", total_options)
        except Exception as e:
            st.metric("Options Actives", "Erreur")
    
    with col2:
        try:
            total_demandes = db.execute_query("SELECT COUNT(*) FROM demandes", fetch='one')[0]
            st.metric("Total Demandes", total_demandes)
        except Exception as e:
            st.metric("Total Demandes", "Erreur")
    
    with col3:
        try:
            # Liste des catégories qui ont des colonnes dans demandes
            categories_with_columns = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
            invalid_count = 0
            
            for category in categories_with_columns:
                try:
                    # Vérifier si la colonne existe
                    columns_info = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
                    existing_columns = [col['name'] for col in columns_info]
                    
                    if category in existing_columns:
                        invalid = db.execute_query(f'''
                            SELECT COUNT(DISTINCT d.{category})
                            FROM demandes d
                            WHERE d.{category} IS NOT NULL 
                            AND d.{category} != ''
                            AND NOT EXISTS (
                                SELECT 1 FROM dropdown_options o 
                                WHERE o.category = ? AND o.value = d.{category} AND o.is_active = 1
                            )
                        ''', (category,), fetch='one')[0]
                        invalid_count += invalid
                except Exception as e:
                    print(f"Erreur vérification {category}: {e}")
                    pass
            
            st.metric("Valeurs Invalides", invalid_count)
        except Exception as e:
            st.metric("Valeurs Invalides", "Erreur")

# Fonctions utilitaires
def get_valid_dropdown_options(category: str):
    """Récupère les options valides pour un formulaire"""
    from models.database import db
    
    try:
        options = db.execute_query('''
            SELECT value, label FROM dropdown_options 
            WHERE category = ? AND is_active = TRUE
            ORDER BY order_index ASC, label ASC
        ''', (category,), fetch='all')
        
        return [(opt['value'], opt['label']) for opt in options] if options else []
    except Exception as e:
        print(f"Erreur get_valid_dropdown_options: {e}")
        return []

def validate_dropdown_value(category: str, value: str) -> bool:
    """Valide qu'une valeur est autorisée"""
    from models.database import db
    
    try:
        result = db.execute_query('''
            SELECT id FROM dropdown_options
            WHERE category = ? AND value = ? AND is_active = 1
        ''', (category, value), fetch='one')
        
        return result is not None
    except Exception as e:
        print(f"Erreur validate_dropdown_value: {e}")
        return False
