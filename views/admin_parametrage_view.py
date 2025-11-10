import streamlit as st
import json
import os

PARAMS_FILE = "param_choices.json"
DEFAULTS = {
    "budget": ["Budget 1", "Budget 2", "Budget 3"],
    "categorie": ["Catégorie 1", "Catégorie 2", "Catégorie 3"],
    "typologie_client": ["Type 1", "Type 2", "Type 3"],
    "groupe_groupement": ["Groupe 1", "Groupe 2", "Groupe 3"],
    "region": ["Nord", "Sud", "Est"],
    "agence": ["Agence 1", "Agence 2", "Agence 3"]
}

def load_params():
    if os.path.exists(PARAMS_FILE):
        with open(PARAMS_FILE, "r") as f:
            return json.load(f)
    return DEFAULTS.copy()

def save_params(params):
    with open(PARAMS_FILE, "w") as f:
        json.dump(params, f, indent=2)

def admin_parametrage_page():
    st.title("⚙️ Paramétrage des listes déroulantes")
    params = load_params()
    for key, label in [
        ("budget", "Budgets"),
        ("categorie", "Catégories"),
        ("typologie_client", "Typologies Client"),
        ("groupe_groupement", "Groupes/Groupements"),
        ("region", "Régions"),
        ("agence", "Agences")
    ]:
        st.subheader(label)
        values = params.get(key, [])
        new_value = st.text_input(f"Ajouter une valeur à {label}", key=f"add_{key}")
        if st.button(f"Ajouter à {label}", key=f"btn_add_{key}"):
            if new_value and new_value not in values:
                values.append(new_value)
                params[key] = values
                save_params(params)
                st.success(f"Ajouté à {label}")
        for i, v in enumerate(values):
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(v)
            with col2:
                if st.button(f"Supprimer", key=f"del_{key}_{i}"):
                    values.pop(i)
                    params[key] = values
                    save_params(params)
                    st.warning(f"Supprimé de {label}")
    st.info("Les modifications sont prises en compte immédiatement.") 