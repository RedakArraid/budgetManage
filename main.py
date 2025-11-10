"""
Point d'entrée principal de l'application BudgetManage.
Ce script configure la page Streamlit, initialise la base de données et les styles,
gère l'état de la session utilisateur (connexion, ID utilisateur, etc.)
et route vers les différentes pages de l'application en fonction de l'état de la session et du rôle de l'utilisateur.
Il implémente une architecture MVC simple en important les contrôleurs et les vues nécessaires.
"""
import streamlit as st
import sys
import os

# Ajoute le répertoire racine du projet au chemin de recherche Python.
# Cela permet d'importer des modules depuis les sous-répertoires comme config, models, controllers, etc.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importe les configurations de l'application, l'objet base de données et les styles CSS.
# app_config contient les paramètres généraux de la page Streamlit.
# db est l'instance de la base de données SQLite.
# load_css charge les styles personnalisés pour l'interface.
from config.settings import app_config
from models.database import db
from static.styles import load_css

# Importe les contrôleurs nécessaires.
# Le AuthController gère l'authentification et les permissions des utilisateurs.
from controllers.auth_controller import AuthController

# Importe les vues nécessaires.
# Chaque vue correspond à une page différente de l'application (connexion, tableau de bord).
from views.login_view import login_page
from views.dashboard_view import dashboard_page

def configure_page():
    """
    Configure les paramètres initiaux de la page Streamlit.
    Définit le titre, la mise en page, l'icône et l'état initial de la barre latérale.
    Ces paramètres sont définis dans le fichier de configuration config/settings.py.
    """
    st.set_page_config(
        page_title=app_config.page_title,
        layout=app_config.layout,
        page_icon=app_config.page_icon,
        initial_sidebar_state=app_config.initial_sidebar_state
    )

def initialize_app():
    """
    Initialise l'application.
    Cela inclut l'initialisation de la base de données (création des tables si elles n'existent pas)
    et le chargement des styles CSS personnalisés.
    Initialise également les variables nécessaires dans l'état de session Streamlit.
    """
    # Initialise la base de données (crée le fichier .db et les tables si besoin).
    db.init_database()
    
    # Exécuter les migrations nécessaires
    try:
        from migrations.migrate_participants import migrate_participants_table
        migrate_participants_table()
    except Exception as e:
        print(f"Avertissement: Erreur lors des migrations: {e}")

    # Charge et applique les styles CSS personnalisés.
    st.markdown(load_css(), unsafe_allow_html=True)

    # Initialise les variables clés dans st.session_state si elles n'existent pas.
    # 'logged_in': Indique si un utilisateur est connecté (booléen).
    # 'user_id': L'ID de l'utilisateur connecté (None si déconnecté).
    # 'user_info': Un dictionnaire contenant les informations de l'utilisateur connecté.
    # 'page': Le nom de la page actuelle à afficher.
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'page' not in st.session_state:
        st.session_state.page = "login"

def display_sidebar():
    """
    Affiche la barre latérale de navigation pour les utilisateurs authentifiés.
    Contient les informations de l'utilisateur connecté, le menu de navigation
    basé sur le rôle et le bouton de déconnexion.
    """
    # Vérifie si l'utilisateur est connecté. Si non, la barre latérale n'est pas affichée.
    if not AuthController.check_session():
        return

    # Utilise le conteneur de la barre latérale Streamlit.
    with st.sidebar:
        # Récupère les informations de l'utilisateur connecté depuis la session.
        user_info = AuthController.get_current_user()

        # Affiche le nom, prénom, rôle et région de l'utilisateur.
        st.markdown(f"""
        ### 👤 {user_info['prenom']} {user_info['nom']}
        **Rôle:** {user_info['role']}  
        **Région:** {user_info.get('region', 'N/A')}
        """)

        st.markdown("---") # Ligne séparatrice

        # Titre du menu de navigation.
        st.markdown("### 🧭 Navigation")

        # Construit la liste des éléments de navigation disponibles en fonction du rôle de l'utilisateur.
        nav_items = _get_navigation_items(user_info['role'])

        # Affiche les boutons de navigation.
        # Chaque bouton met à jour l'état de session 'page' et relance l'application pour afficher la nouvelle page.
        for icon, label, page in nav_items:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        st.markdown("---") # Ligne séparatrice

        # Affiche le compteur de notifications non lues (si > 0).
        _display_notification_count()

        st.markdown("---") # Ligne séparatrice

        # Bouton de déconnexion.
        # Déconnecte l'utilisateur via le AuthController et relance l'application pour revenir à la page de connexion.
        if st.button("🚪 Se Déconnecter", use_container_width=True, type="secondary"):
            AuthController.logout(st.session_state.user_id)
            st.rerun()

def _get_navigation_items(role):
    """Détermine la liste des pages de navigation accessibles pour un rôle d'utilisateur donné."""
    # Éléments de navigation de base accessibles à la plupart des rôles.
    nav_items = [
        ("🏠", "Tableau de Bord", "dashboard"),
        ("📋", "Demandes", "demandes"),
        ("📊", "Analytics", "analytics"),
        ("🔔", "Notifications", "notifications"),
    ]

    # Ajoute les éléments de navigation spécifiques aux rôles.
    if role == 'admin':
        # Les administrateurs ont accès à toutes les fonctionnalités admin
        nav_items.insert(1, ("➕", "Nouvelle demande", "admin_create_demande"))
        nav_items.insert(2, ("👥", "Utilisateurs", "gestion_utilisateurs"))
        nav_items.insert(3, ("🏦️", "Listes Déroulantes", "admin_dropdown_options"))

    if role in ['tc', 'dr', 'marketing']:
        # Les créateurs de demandes (TC, DR, Marketing) peuvent créer de nouvelles demandes.
        nav_items.insert(1, ("➕", "Nouvelle Demande", "nouvelle_demande"))

    if role in ['dr', 'dr_financier', 'dg']:
        # Les validateurs (DR, DR Financier, DG) ont accès à la page de validation.
        nav_items.insert(-2, ("✅", "Validations", "validations"))

    return nav_items

def _display_notification_count():
    """
    Affiche le nombre de notifications non lues pour l'utilisateur connecté dans la barre latérale.
    Cette fonction est appelée par display_sidebar.
    """
    try:
        # Importe le modèle de notification localement pour éviter les importations circulaires si nécessaire.
        from models.notification import NotificationModel
        # Récupère l'ID de l'utilisateur connecté.
        user_id = AuthController.get_current_user_id()
        # Si un utilisateur est connecté, compte les notifications non lues.
        if user_id:
            unread_count = NotificationModel.get_unread_count(user_id)
            # Affiche le compteur si supérieur à 0.
            if unread_count > 0:
                st.markdown(f"""
                ### 🔔 Notifications
                **{unread_count} non lue(s)**
                """)
    except Exception:
        # Ignore les erreurs si la table notifications n'existe pas encore, par exemple.
        pass

def route_pages():
    """
    Gère le routage vers la page appropriée en fonction de la valeur de st.session_state.page.
    Vérifie d'abord l'authentification, puis les permissions d'accès à la page demandée.
    """
    # Si l'utilisateur n'est pas connecté, affiche la page de connexion et arrête le routage.
    if not AuthController.check_session():
        login_page()
        return

    # Récupère la page actuelle depuis l'état de session (par défaut : dashboard).
    page = st.session_state.get('page', 'dashboard')

    # Vérifie si l'utilisateur connecté a les permissions nécessaires pour accéder à la page demandée.
    if not AuthController.can_access_page(page):
        # Si l'accès est refusé, affiche un message d'erreur, redirige vers le tableau de bord et relance.
        st.error("❌ Vous n'avez pas les permissions pour accéder à cette page")
        st.session_state.page = "dashboard"
        st.rerun()
        return

    # Route vers la fonction de vue correspondante en fonction de la page demandée.
    # Les vues sont importées localement ici pour une meilleure organisation et potentiellement pour éviter les importations circulaires.
    if page == "dashboard":
        dashboard_page()
    elif page == "admin_create_demande":
        from views.admin_create_demande_view import admin_create_demande_page
        admin_create_demande_page()
    elif page == "nouvelle_demande":
        from views.nouvelle_demande_view import nouvelle_demande_page
        nouvelle_demande_page()
    elif page == "demandes":
        from views.demandes_view import demandes_page
        demandes_page()
    elif page == "gestion_utilisateurs":
        from views.gestion_utilisateurs_view import gestion_utilisateurs_page
        gestion_utilisateurs_page()
    elif page == "admin_dropdown_options":
        from views.admin_dropdown_options_view import admin_dropdown_options_page
        admin_dropdown_options_page()
    elif page == "validations":
        from views.validations_view import validations_page
        validations_page()
    elif page == "analytics":
        from views.analytics_view import analytics_page
        analytics_page()
    elif page == "notifications":
        from views.notifications_view import notifications_page
        notifications_page()
    else:
        # Si la page demandée n'est pas reconnue, affiche le tableau de bord par défaut.
        st.session_state.page = "dashboard"
        dashboard_page()

def main():
    """
    Fonction principale de l'application.
    Appelle les fonctions de configuration, d'initialisation, d'affichage de la barre latérale
    et de routage des pages pour lancer l'application Streamlit.
    """
    # Configure les paramètres de la page Streamlit.
    configure_page()

    # Initialise les composants de l'application (base de données, styles, session state).
    initialize_app()

    # Affiche la barre latérale si l'utilisateur est connecté.
    if AuthController.check_session():
        display_sidebar()

    # Gère l'affichage de la page principale en fonction de l'état de session.
    route_pages()

# Point d'entrée du script.
# Exécute la fonction main() lorsque le script est lancé directement.
if __name__ == "__main__":
    main()
