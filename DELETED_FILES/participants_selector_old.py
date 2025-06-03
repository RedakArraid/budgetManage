"""
Composant pour la sélection et gestion des participants
"""
import streamlit as st
from typing import List, Dict, Any, Tuple
from controllers.demande_controller import DemandeController
from models.user import UserModel

def display_participants_selector(user_role: str, user_id: int, 
                                current_participants: List[int] = None,
                                demandeur_participe: bool = True,
                                participants_libres: str = "") -> Tuple[bool, List[int], str]:
    """
    Affiche le sélecteur de participants selon le rôle utilisateur
    
    Returns:
        - demandeur_participe (bool): Si le demandeur participe
        - selected_participants (List[int]): IDs des participants sélectionnés
        - participants_libres (str): Texte libre pour autres participants
    """
    
    st.markdown("### 👥 Participants à l'événement")
    
    if current_participants is None:
        current_participants = []
    
    # Variables de retour
    new_demandeur_participe = demandeur_participe
    new_selected_participants = current_participants.copy()
    new_participants_libres = participants_libres
    
    if user_role == 'tc':
        # Pour les TCs : participation automatique + champ libre
        st.info("ℹ️ Vous participez automatiquement à cet événement en tant que TC")
        new_demandeur_participe = True
        
        # Champ libre pour autres participants
        new_participants_libres = st.text_area(
            "➕ Autres participants (optionnel)",
            value=participants_libres,
            placeholder="Noms et contacts des autres participants...",
            help="Vous pouvez ajouter d'autres participants qui ne sont pas dans le système"
        )
        
    elif user_role == 'dr':
        # Pour les DRs : choix de participation + sélection TCs
        col1, col2 = st.columns([1, 2])
        
        with col1:
            new_demandeur_participe = st.checkbox(
                "Je participe à cet événement",
                value=demandeur_participe,
                help="Cochez si vous participez personnellement à l'événement"
            )
        
        with col2:
            if new_demandeur_participe:
                st.success("✅ Vous êtes inscrit comme participant")
            else:
                st.info("ℹ️ Vous n'êtes pas inscrit comme participant")
        
        # Sélection des TCs
        st.markdown("**👥 Sélectionner des TCs participants:**")
        
        # Récupérer les TCs disponibles
        available_tcs = DemandeController.get_available_participants_for_user(user_id, user_role)
        
        if available_tcs:
            # Interface de sélection multiple
            new_selected_participants = _display_tc_multiselect(
                available_tcs, current_participants
            )
            
            # Affichage des participants sélectionnés
            if new_selected_participants:
                _display_selected_participants(new_selected_participants, available_tcs)
        else:
            st.warning("⚠️ Aucun TC disponible dans votre équipe")
        
        # Champ libre pour autres participants
        st.markdown("**➕ Autres participants (optionnel):**")
        new_participants_libres = st.text_area(
            "",
            value=participants_libres,
            placeholder="Noms et contacts d'autres participants externes...",
            help="Participants qui ne sont pas dans le système (clients, partenaires, etc.)",
            label_visibility="collapsed"
        )
    
    else:
        # Pour les autres rôles (marketing, admin, etc.) : comportement simple
        st.info("ℹ️ Gestion des participants selon votre rôle")
        new_demandeur_participe = st.checkbox(
            "Je participe à cet événement",
            value=demandeur_participe
        )
        
        new_participants_libres = st.text_area(
            "Autres participants",
            value=participants_libres,
            placeholder="Noms et contacts des participants..."
        )
    
    return new_demandeur_participe, new_selected_participants, new_participants_libres

def _display_tc_multiselect(available_tcs: List[Dict[str, Any]], 
                           current_selection: List[int]) -> List[int]:
    """Affiche un sélecteur multiple pour les TCs"""
    
    if not available_tcs:
        return []
    
    # Créer les options pour le multiselect
    tc_options = {}
    tc_labels = []
    
    for tc in available_tcs:
        label = f"{tc['prenom']} {tc['nom']} ({tc['region']})"
        tc_options[label] = tc['id']
        tc_labels.append(label)
    
    # Déterminer les valeurs par défaut
    default_labels = []
    for tc_id in current_selection:
        for tc in available_tcs:
            if tc['id'] == tc_id:
                label = f"{tc['prenom']} {tc['nom']} ({tc['region']})"
                if label in tc_labels:
                    default_labels.append(label)
                break
    
    # Multiselect
    selected_labels = st.multiselect(
        "Choisir les TCs participants",
        options=tc_labels,
        default=default_labels,
        help="Sélectionnez un ou plusieurs TCs de votre équipe"
    )
    
    # Convertir les labels en IDs
    selected_ids = [tc_options[label] for label in selected_labels]
    
    return selected_ids

def _display_selected_participants(selected_ids: List[int], 
                                 available_tcs: List[Dict[str, Any]]):
    """Affiche la liste des participants sélectionnés"""
    
    if not selected_ids:
        return
    
    st.markdown("**📋 Participants sélectionnés:**")
    
    for tc_id in selected_ids:
        # Trouver les infos du TC
        tc_info = next((tc for tc in available_tcs if tc['id'] == tc_id), None)
        
        if tc_info:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"• **{tc_info['prenom']} {tc_info['nom']}** ({tc_info['region']})")
                st.caption(f"📧 {tc_info['email']}")
            
            with col2:
                # Bouton de suppression (pour interface avancée)
                if st.button("🗑️", key=f"remove_tc_{tc_id}", help="Retirer ce participant"):
                    # Fonctionnalité de suppression à implémenter
                    st.info("Fonctionnalité de suppression à implémenter")

def display_participants_summary(demande_id: int, 
                               demandeur_info: Dict[str, Any],
                               demandeur_participe: bool = True,
                               participants_libres: str = "",
                               show_edit_button: bool = False) -> None:
    """
    Affiche un résumé des participants d'une demande (lecture seule)
    """
    
    st.markdown("### 👥 Participants")
    
    participants_summary = DemandeController.get_participants_summary(demande_id)
    
    # Compter les participants
    total_participants = 0
    
    # Demandeur
    if demandeur_participe:
        total_participants += 1
        st.markdown(f"**🎯 Demandeur:** {demandeur_info['prenom']} {demandeur_info['nom']} ({demandeur_info['role'].upper()})")
    
    # Participants de la base de données
    if participants_summary['participants']:
        st.markdown(f"**👥 Équipe ({participants_summary['total_count']}):**")
        
        for participant in participants_summary['participants']:
            st.markdown(f"• {participant['prenom']} {participant['nom']} ({participant['role'].upper()}) - {participant['region']}")
        
        total_participants += participants_summary['total_count']
    
    # Participants libres
    if participants_libres and participants_libres.strip():
        st.markdown("**➕ Autres participants:**")
        st.markdown(participants_libres)
        # On ne peut pas compter précisément les participants libres
    
    # Résumé total
    if total_participants > 0:
        st.success(f"**Total: {total_participants} participant(s) confirmé(s)**")
    else:
        st.warning("⚠️ Aucun participant confirmé")
    
    # Bouton d'édition (si autorisé)
    if show_edit_button:
        if st.button("✏️ Modifier les participants"):
            # Cette fonctionnalité pourrait ouvrir un modal ou rediriger vers une page d'édition
            st.info("Fonctionnalité d'édition à implémenter")

def get_participants_display_text(demande_id: int, 
                                demandeur_info: Dict[str, Any],
                                demandeur_participe: bool = True,
                                participants_libres: str = "") -> str:
    """
    Retourne une chaîne formatée des participants pour affichage dans les listes
    """
    from models.participant import ParticipantModel
    
    return ParticipantModel.get_participants_for_display(
        demande_id, demandeur_participe, participants_libres
    )
