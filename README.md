# Kommunalhaushalt-App (private MVP)

Diese Streamlit-App ist eine **private** Web-App für Kommunen, um Haushaltsdaten schrittweise einzugeben und als Dashboard bereitzustellen.

## Funktionen

- Passwortschutz für die gesamte App (privater Startmodus)
- Login-Bereich für Kommunen zur Dateneingabe
- Schrittweise Datenerfassung je Haushaltsjahr (2026–2029)
- Dashboard-Ansicht mit:
  - Jahresergebnis, Gewerbesteuererträge, Kreisumlage
  - Donut-Diagrammen für wesentliche Erträge/Aufwendungen
  - Haushaltssimulator (Hebesätze + freiwillige Aufwendungen)
  - Projekten, Benchmarks, freiwilligen Leistungen und Fakten
- Token-gesicherter Dashboard-Link pro Kommune

## Lokal starten

1. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

2. App starten

```bash
streamlit run streamlit_app.py
```

## Standardzugänge (Demo)

- App-Passwort (falls nicht in `st.secrets` gesetzt): `kommunal-start`
- Demo-Kommune Login: `demo` / `demo123`
- Demo-Dashboard-Token: `demo-link`

## Optional: App-Passwort per Umgebungsvariable setzen

```bash
export APP_PASSWORD="DEIN_SICHERES_PASSWORT"
streamlit run streamlit_app.py
```
