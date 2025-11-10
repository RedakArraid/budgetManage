
import streamlit as st

# Nettoyer les états problématiques
keys_to_clean = [
    'demande_created', 'created_demande_id', 'created_demande_nom',
    'created_demande_montant', 'created_demande_type'
]

for key in keys_to_clean:
    if key in st.session_state:
        del st.session_state[key]

st.success("✅ État de session nettoyé!")
st.info("Vous pouvez maintenant créer des demandes normalement.")
