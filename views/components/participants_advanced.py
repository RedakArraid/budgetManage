"""
Composant avancé pour la sélection des participants
Compatible avec les formulaires Streamlit
"""
import streamlit as st
from typing import List, Tuple, Dict, Any
from controllers.demande_controller import DemandeController

def display_participants_advanced(user_role: str, user_id: int) -> Tuple[bool, List[int], str]:
    """
    Affiche un sélecteur de participants avancé pour les formulaires
    
    Returns:
        - demandeur_participe (bool): Si le demandeur participe
        - selected_participants (List[int]): IDs des participants sélectionnés
        - participants_libres (str): Texte libre pour autres participants
    """
    
    if user_role == 'tc':
        # Pour les TCs : participation automatique
        st.info("ℹ️ Vous participez automatiquement à cet événement en tant que TC")
        demandeur_participe = True
        
        # Champ libre pour autres participants
        participants_libres = st.text_area(
            "➕ Autres participants (optionnel)",
            placeholder="Noms et contacts des autres participants extérieurs au système...",
            help="Participants qui ne sont pas dans le système (clients, partenaires, etc.)"
        )
        
        selected_participants = []
        
    elif user_role == 'dr':
        # Pour les DRs : choix de participation + sélection des TCs de son équipe
        col1, col2 = st.columns([1, 2])
        
        with col1:
            demandeur_participe = st.checkbox(
                "Je participe à cet événement",
                value=True,
                help="Cochez si vous participez personnellement à l'événement"
            )
        
        with col2:
            if demandeur_participe:
                st.success("✅ Vous êtes inscrit comme participant")
            else:
                st.info("ℹ️ Vous n'êtes pas inscrit comme participant")
        
        # Sélection des TCs de l'équipe
        st.markdown("**👥 Sélectionner des TCs de votre équipe :**")
        
        # Récupérer les TCs disponibles pour ce DR
        available_tcs = DemandeController.get_available_participants_for_user(user_id, user_role)
        
        if available_tcs:
            # Interface de sélection multiple
            selected_participants = _display_tc_multiselect(available_tcs)
            
            # Affichage des TCs sélectionnés
            if selected_participants:
                _display_selected_tcs_summary(selected_participants, available_tcs)
        else:
            st.warning("⚠️ Aucun TC disponible dans votre équipe")
            selected_participants = []
        
        # Champ libre pour autres participants
        st.markdown("**➕ Autres participants (optionnel) :**")
        participants_libres = st.text_area(
            "",
            placeholder="Noms et contacts d'autres participants (clients, partenaires, externes)...",
            help="Participants qui ne sont pas dans le système",
            label_visibility="collapsed"
        )
        
    elif user_role == 'admin':
        # Pour les admins : accès complet
        demandeur_participe = st.checkbox(
            "Je participe à cet événement",
            value=True,
            help="Cochez si vous participez personnellement à l'événement"
        )
        
        # Sélection de TCs (tous les TCs)
        st.markdown("**👥 Sélectionner des TCs participants :**")
        
        available_tcs = DemandeController.get_available_participants_for_user(user_id, user_role)
        
        if available_tcs:
            selected_participants = _display_tc_multiselect(available_tcs)
            
            if selected_participants:
                _display_selected_tcs_summary(selected_participants, available_tcs)
        else:
            st.warning("⚠️ Aucun TC disponible")
            selected_participants = []
        
        # Champ libre pour autres participants
        participants_libres = st.text_area(
            "Autres participants",
            placeholder="Noms et contacts d'autres participants...",
            help="Participants qui ne sont pas dans le système"
        )
        
    else:
        # Pour les autres rôles (marketing, etc.)
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

def _display_tc_multiselect(available_tcs: List[Dict[str, Any]]) -> List[int]:
    """Affiche un sélecteur multiple pour les TCs avec informations détaillées"""
    
    if not available_tcs:
        return []
    
    # Créer les options pour le multiselect avec plus d'informations
    tc_options = {}
    tc_labels = []
    
    for tc in available_tcs:
        # Format: "Prénom NOM (Région) - email"
        label = f"{tc['prenom']} {tc['nom']} ({tc['region']}) - {tc['email']}"
        tc_options[label] = tc['id']
        tc_labels.append(label)
    
    # Multiselect pour choisir les TCs
    selected_labels = st.multiselect(
        "Choisir les TCs participants",
        options=tc_labels,
        help="Sélectionnez un ou plusieurs TCs qui participeront à l'événement"
    )
    
    # Convertir les labels en IDs
    selected_ids = [tc_options[label] for label in selected_labels]
    
    return selected_ids

def _display_selected_tcs_summary(selected_ids: List[int], available_tcs: List[Dict[str, Any]]):
    """Affiche un résumé des TCs sélectionnés"""
    
    if not selected_ids:
        return
    
    st.markdown("**📋 TCs sélectionnés :**")
    
    # Grouper par région si nécessaire
    tcs_by_region = {}
    
    for tc_id in selected_ids:
        tc_info = next((tc for tc in available_tcs if tc['id'] == tc_id), None)
        
        if tc_info:
            region = tc_info['region']
            if region not in tcs_by_region:
                tcs_by_region[region] = []
            tcs_by_region[region].append(tc_info)
    
    # Afficher par région
    for region, tcs in tcs_by_region.items():
        if len(tcs_by_region) > 1:  # Afficher la région seulement s'il y en a plusieurs
            st.markdown(f"**🌍 {region}:**")
        
        for tc_info in tcs:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"• **{tc_info['prenom']} {tc_info['nom']}**")
                st.caption(f"📧 {tc_info['email']}")
            
            with col2:
                st.success("✅ Sélectionné")
    
    # Résumé total
    if len(selected_ids) > 1:
        st.info(f"**Total: {len(selected_ids)} TC(s) sélectionné(s)**")

def display_participants_readonly(demande_id: int, 
                                demandeur_info: Dict[str, Any],
                                demandeur_participe: bool = True,
                                participants_libres: str = "") -> None:
    """
    Affiche un résumé en lecture seule des participants d'une demande
    """
    
    st.markdown("### 👥 Participants")
    
    # Récupérer les participants de la base de données
    participants_summary = DemandeController.get_participants_summary(demande_id)
    
    # Compter les participants
    total_participants = 0
    
    # Demandeur
    if demandeur_participe:
        total_participants += 1
        st.markdown(f"**🎯 Demandeur :** {demandeur_info['prenom']} {demandeur_info['nom']} ({demandeur_info['role'].upper()})")
    
    # Participants de la base de données (TCs sélectionnés)
    if participants_summary['participants']:
        st.markdown(f"**👥 Équipe ({participants_summary['total_count']}) :**")
        
        # Grouper par région
        participants_by_region = {}
        for participant in participants_summary['participants']:
            region = participant.get('region', 'Non spécifiée')
            if region not in participants_by_region:
                participants_by_region[region] = []
            participants_by_region[region].append(participant)
        
        # Afficher par région
        for region, participants in participants_by_region.items():
            if len(participants_by_region) > 1:
                st.markdown(f"**🌍 {region} :**")
            
            for participant in participants:
                role_emoji = "👔" if participant['role'] == 'tc' else "👨‍💼"
                st.markdown(f"• {role_emoji} {participant['prenom']} {participant['nom']} ({participant['role'].upper()})")
                st.caption(f"📧 {participant['email']}")
        
        total_participants += participants_summary['total_count']
    
    # Participants libres
    if participants_libres and participants_libres.strip():
        st.markdown("**➕ Autres participants :**")
        st.text(participants_libres)
    
    # Résumé total
    if total_participants > 0:
        st.success(f"**Total : {total_participants} participant(s) confirmé(s)**")
    else:
        st.warning("⚠️ Aucun participant confirmé")

def get_participants_count(demande_id: int, demandeur_participe: bool = True) -> int:
    """
    Retourne le nombre total de participants pour une demande
    """
    try:
        participants_summary = DemandeController.get_participants_summary(demande_id)
        count = participants_summary.get('total_count', 0)
        
        if demandeur_participe:
            count += 1
            
        return count
    except Exception:
        return 0
