"""
Utilitaires pour les spinners et indicateurs de chargement
"""
import streamlit as st
from contextlib import contextmanager
from typing import Optional
import time

class SpinnerMessages:
    """Messages prédéfinis pour les spinners"""
    
    # Base de données
    DB_LOADING = "🔄 Chargement des données..."
    DB_SAVING = "💾 Sauvegarde en cours..."
    DB_UPDATING = "🔄 Mise à jour..."
    DB_DELETING = "🗑️ Suppression en cours..."
    
    # Demandes
    DEMANDES_LOADING = "📄 Chargement des demandes..."
    DEMANDES_CREATING = "📋 Création de la demande..."
    DEMANDES_UPDATING = "🔄 Mise à jour de la demande..."
    DEMANDES_SUBMITTING = "📤 Soumission en cours..."
    DEMANDES_VALIDATING = "✅ Validation en cours..."
    DEMANDES_REJECTING = "❌ Rejet en cours..."
    
    # Filtres
    FILTERS_LOADING_CY = "🔄 Chargement des années civiles..."
    FILTERS_LOADING_BY = "🔄 Chargement des années fiscales..."
    FILTERS_APPLYING = "🔍 Application des filtres..."
    
    # Calculs
    CALC_CY_BY = "🧮 Calcul des années civile/fiscale..."
    CALC_STATS = "📊 Calcul des statistiques..."
    
    # Export/Import
    EXPORT_DATA = "📋 Export des données..."
    IMPORT_DATA = "📥 Import des données..."
    
    # Authentification
    AUTH_LOGIN = "🔐 Connexion en cours..."
    AUTH_LOGOUT = "👋 Déconnexion..."
    
    # Général
    PROCESSING = "⚙️ Traitement en cours..."
    SAVING = "💾 Sauvegarde..."
    LOADING = "🔄 Chargement..."

@contextmanager
def smart_spinner(message: str, success_message: Optional[str] = None, min_duration: float = 0.5):
    """
    Spinner intelligent avec durée minimale et message de succès optionnel
    
    Args:
        message: Message à afficher pendant le chargement
        success_message: Message de succès optionnel
        min_duration: Durée minimale d'affichage du spinner (en secondes)
    """
    start_time = time.time()
    
    with st.spinner(message):
        try:
            yield
            
            # Attendre la durée minimale si nécessaire
            elapsed = time.time() - start_time
            if elapsed < min_duration:
                time.sleep(min_duration - elapsed)
                
            # Afficher le message de succès si fourni
            if success_message:
                st.success(success_message, icon="✅")
                
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            raise

@contextmanager  
def loading_spinner(message: str = SpinnerMessages.LOADING):
    """Spinner simple pour le chargement"""
    with st.spinner(message):
        yield

def show_progress_bar(progress: float, message: str = ""):
    """
    Affiche une barre de progression
    
    Args:
        progress: Progression entre 0.0 et 1.0
        message: Message optionnel à afficher
    """
    if message:
        st.write(message)
    
    progress_bar = st.progress(progress)
    return progress_bar

def update_progress(progress_bar, progress: float, message: str = ""):
    """Met à jour une barre de progression existante"""
    progress_bar.progress(progress)
    if message:
        st.write(message)

class OperationFeedback:
    """Classe pour gérer les retours d'opérations avec spinners"""
    
    @staticmethod
    def create_demande():
        """Feedback pour création de demande"""
        return smart_spinner(
            SpinnerMessages.DEMANDES_CREATING,
            "✅ Demande créée avec succès !"
        )
    
    @staticmethod
    def update_demande():
        """Feedback pour mise à jour de demande"""
        return smart_spinner(
            SpinnerMessages.DEMANDES_UPDATING,
            "✅ Demande mise à jour !"
        )
    
    @staticmethod
    def submit_demande():
        """Feedback pour soumission de demande"""
        return smart_spinner(
            SpinnerMessages.DEMANDES_SUBMITTING,
            "✅ Demande soumise !"
        )
    
    @staticmethod
    def validate_demande():
        """Feedback pour validation de demande"""
        return smart_spinner(
            SpinnerMessages.DEMANDES_VALIDATING,
            "✅ Demande validée !"
        )
    
    @staticmethod
    def load_demandes():
        """Feedback pour chargement des demandes"""
        return loading_spinner(SpinnerMessages.DEMANDES_LOADING)
    
    @staticmethod
    def apply_filters():
        """Feedback pour application des filtres"""
        return loading_spinner(SpinnerMessages.FILTERS_APPLYING)
    
    @staticmethod
    def load_filter_options():
        """Feedback pour chargement des options de filtres"""
        return loading_spinner("🔄 Chargement des options...")

# Décorateur pour ajouter automatiquement un spinner
def with_spinner(message: str = SpinnerMessages.PROCESSING):
    """
    Décorateur pour ajouter automatiquement un spinner à une fonction
    
    Usage:
        @with_spinner("🔄 Opération en cours...")
        def my_function():
            # Code de la fonction
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with loading_spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Fonctions utilitaires pour les cas d'usage courants
def with_db_operation(operation_type: str = "opération"):
    """Spinner pour opérations de base de données"""
    messages = {
        "create": SpinnerMessages.DB_SAVING,
        "update": SpinnerMessages.DB_UPDATING,
        "delete": SpinnerMessages.DB_DELETING,
        "load": SpinnerMessages.DB_LOADING
    }
    message = messages.get(operation_type, SpinnerMessages.PROCESSING)
    return loading_spinner(message)

def with_calculation():
    """Spinner pour calculs"""
    return loading_spinner(SpinnerMessages.CALC_STATS)

def with_file_operation(operation_type: str = "traitement"):
    """Spinner pour opérations sur fichiers"""
    messages = {
        "export": SpinnerMessages.EXPORT_DATA,
        "import": SpinnerMessages.IMPORT_DATA
    }
    message = messages.get(operation_type, SpinnerMessages.PROCESSING)
    return loading_spinner(message)
