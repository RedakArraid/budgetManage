"""
Composant simplifié pour la sélection des participants
Compatible avec les formulaires Streamlit
"""
import streamlit as st
from typing import List, Tuple
from controllers.demande_controller import DemandeController

def display_participants_simple(user_role: str, user_id: int) -> Tuple[bool, List[int], str]:
    """
    Affiche un sélecteur de participants simplifié pour les formulaires
    
    Returns:
        - demandeur_participe (bool): Si le demandeur participe
        - selected_participants (List[int]): IDs des participants sélectionnés (vide pour l'instant)
        - participants_libres (str): Texte libre pour autres participants
    """
    
    if user_role == 'tc':
        # Pour les TCs : participation automatique
        st.info("ℹ️ Vous participez automatiquement à cet événement en tant que TC")
        demandeur_participe = True
        
        # Champ libre pour autres participants
        participants_libres = st.text_area(
            "➕ Autres participants (optionnel)",
            placeholder="Noms et contacts des autres participants...",
            help="Vous pouvez ajouter d'autres participants qui ne sont pas dans le système"
        )
        
        selected_participants = []
        
    elif user_role == 'dr':
        # Pour les DRs : choix de participation
        demandeur_participe = st.checkbox(
            "Je participe à cet événement",
            value=True,
            help="Cochez si vous participez personnellement à l'événement"
        )
        
        # Information sur les TCs (pour l'instant en texte libre)
        st.markdown("**👥 Participants de l'équipe:**")
        participants_libres = st.text_area(
            "Participants (TCs et autres)",
            placeholder="Noms et contacts des participants de votre équipe...",
            help="Participants qui ne sont pas dans le système (TCs, clients, partenaires, etc.)"
        )
        
        selected_participants = []
        
    else:
        # Pour les autres rôles (marketing, admin, etc.)
        demandeur_participe = st.checkbox(
            "Je participe à cet événement",
            value=True
        )
        
        participants_libres = st.text_area(
            "Autres participants",
            placeholder="Noms et contacts des participants...",
            help="Participants à l'événement"
        )
        
        selected_participants = []
    
    return demandeur_participe, selected_participants, participants_libres
