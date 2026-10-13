# ✈️ AéroLog — Suivi des heures de vol et des cycles

Application Streamlit (thème light yellow animé) : tableau de bord, état de la flotte,
saisie de nouvelles données avec mise à jour instantanée, export CSV.

## Lancer
    pip install -r requirements.txt
    streamlit run app.py

## Connexion (démo)
admin / aero2026 · technicien / aero2026 · planning / aero2026

## Structure
    aerolog/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── data/dataset.csv          # journal des vols (modifié par le formulaire de saisie)
    └── .streamlit/config.toml    # thème
