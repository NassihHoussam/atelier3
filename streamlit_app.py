"""Interface Streamlit pour l'API de prédiction LogiAI."""
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="LogiAI", page_icon="🚚")
st.title("🚚 LogiAI — Risque de retard")
st.write("Renseignez les caractéristiques de la livraison pour estimer son risque de retard.")

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        distance_km = st.number_input("Distance (km)", min_value=1.0, max_value=1000.0, value=120.0)
        poids_kg = st.number_input("Poids (kg)", min_value=0.0, max_value=3000.0, value=450.0)
        heure_depart = st.number_input("Heure de départ", min_value=0, max_value=23, value=17)
        type_vehicule = st.selectbox("Type de véhicule", ["moto", "fourgon", "camion"])

    with col2:
        pluie_mm = st.number_input("Pluie (mm)", min_value=0.0, max_value=100.0, value=8.0)
        trafic_index = st.number_input("Indice de trafic", min_value=0.0, max_value=10.0, value=7.5)
        nb_arrets = st.number_input("Nombre d'arrêts", min_value=0, max_value=12, value=4)

    submitted = st.form_submit_button("Prédire le risque")

if submitted:
    livraison = {
        "distance_km": distance_km,
        "poids_kg": poids_kg,
        "heure_depart": heure_depart,
        "pluie_mm": pluie_mm,
        "trafic_index": trafic_index,
        "nb_arrets": nb_arrets,
        "type_vehicule": type_vehicule,
    }

    try:
        response = requests.post(f"{API_URL}/v1/predict", json=livraison, timeout=10)
    except requests.ConnectionError:
        st.error("Impossible de joindre l'API. Vérifiez qu'elle tourne dans un autre terminal.")
    except requests.Timeout:
        st.error("L'API n'a pas répondu à temps. Réessayez.")
    else:
        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except requests.exceptions.JSONDecodeError:
                detail = response.text
            st.error(f"Erreur de l'API ({response.status_code}) : {detail}")
        else:
            prediction = response.json()
            st.metric("Probabilité de retard", f"{prediction['probabilite_retard']:.1%}")

            if prediction["alerte"]:
                st.warning(f"⚠️ Alerte retard (seuil : {prediction['seuil']:.0%})")
            else:
                st.success(f"Pas d'alerte (seuil : {prediction['seuil']:.0%})")

            st.caption(f"Version du modèle : {prediction['model_version']}")
