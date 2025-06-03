"""
User account settings page view
"""
import streamlit as st
from controllers.auth_controller import AuthController
from utils.spinner_utils import OperationFeedback

# Keep the decorator for authentication
@AuthController.require_auth
def account_settings_page():
    """Display account settings page with password change form"""
    st.subheader("⚙️ Paramètres du Compte - Test d'affichage")

# You might add other account settings sections here later if needed
# For example: Profile information, notification preferences, etc. 