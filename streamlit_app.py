import json
import os
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kommunalhaushalt", layout="wide")

DATA_PATH = Path("data/kommunen.json")
YEARS = ["2026", "2027", "2028", "2029"]


def _default_record() -> dict[str, Any]:
    return {
        "username": "demo",
        "password": "demo123",
        "viewer_token": "demo-link",
        "name": "Musterstadt",
        "tagline": "Kommunalfinanzen transparent und verständlich",
        "years": {
            year: {
                "annual_result": -2_400_000,
                "trade_tax": 13_000_000,
                "district_levy": 8_500_000,
                "revenues": {
                    "Gewerbesteuer": 13_000_000,
                    "Grundsteuer": 4_500_000,
                    "Einkommensteueranteil": 7_200_000,
                    "Gebühren": 2_000_000,
                },
                "expenses": {
                    "Personal": 9_500_000,
                    "Kreisumlage": 8_500_000,
                    "Soziales": 4_200_000,
                    "Sachaufwand": 3_600_000,
                },
                "projects": [
                    "Grundschulsanierung",
                    "Radweg Hauptstraße",
                    "Spielplatz-Modernisierung",
                    "Kita-Neubau",
                ],
                "total_investments": 9_000_000,
                "benchmarks": {
                    "Schulden pro Kopf": {"own": 1850, "avg": 2100, "comment": "Unter Durchschnitt"},
                    "Investitionsquote": {"own": 17.3, "avg": 13.8, "comment": "Überdurchschnittlich zukunftsorientiert"},
                    "Gewerbesteuererträge": {"own": 13000000, "avg": 9800000, "comment": "Starke lokale Wirtschaft"},
                },
                "voluntary_services": {
                    "total": 1_300_000,
                    "share": 3.9,
                    "items": ["Kulturförderung", "Sportvereine", "Veranstaltungen", "Grünflächen & Parks"],
                },
                "facts": [
                    "Ein Schüler kostet ca. 8.200 € pro Jahr.",
                    "Ein Musikschulplatz kostet ca. 1.400 € pro Jahr.",
                    "1 km Straßensanierung kostet im Schnitt 1,1 Mio. €.",
                ],
            }
            for year in YEARS
        },
    }


def load_data() -> dict[str, Any]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        data = {"musterstadt": _default_record()}
        save_data(data)
        return data
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(data: dict[str, Any]) -> None:
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def money(value: float) -> str:
    return f"{value:,.0f} €".replace(",", ".")


def badge(is_good: bool) -> str:
    return "🟢" if is_good else "🔴"


def login_guard() -> bool:
    app_password = os.getenv("APP_PASSWORD", "kommunal-start")
    if st.session_state.get("app_ok"):
        return True

    st.info("Diese Anwendung ist im privaten Modus. Zugang nur mit App-Passwort.")
    entered = st.text_input("App-Passwort", type="password")
    if st.button("Freischalten", type="primary"):
        if entered == app_password:
            st.session_state["app_ok"] = True
            st.rerun()
        st.error("Passwort nicht korrekt.")
    return False


def municipality_login(data: dict[str, Any]) -> str | None:
    st.subheader("Login für Kommunen")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password", key="kommunal_pw")
    if st.button("Anmelden", type="primary"):
        for slug, rec in data.items():
            if rec["username"] == username and rec["password"] == password:
                st.session_state["slug"] = slug
                st.success(f"Willkommen, {rec['name']}!")
                st.rerun()
        st.error("Ungültige Zugangsdaten.")

    with st.expander("Neue Kommune registrieren"):
        slug = st.text_input("Technischer Kurzname (z. B. rathausstadt)")
        name = st.text_input("Anzeigename der Kommune")
        new_user = st.text_input("Neuer Benutzername")
        new_pw = st.text_input("Neues Passwort", type="password")
        if st.button("Kommune anlegen"):
            if not slug or not name or not new_user or not new_pw:
                st.warning("Bitte alle Felder ausfüllen.")
            elif slug in data:
                st.error("Der Kurzname existiert bereits.")
            else:
                new_rec = _default_record()
                new_rec["name"] = name
                new_rec["username"] = new_user
                new_rec["password"] = new_pw
                new_rec["viewer_token"] = f"{slug}-link"
                data[slug] = new_rec
                save_data(data)
                st.success("Kommune angelegt. Bitte jetzt anmelden.")

    return st.session_state.get("slug")


def edit_year(year_data: dict[str, Any], year: str) -> None:
    st.markdown(f"#### Eingabe für Haushaltsjahr {year}")

    with st.form(f"core_{year}"):
        c1, c2, c3 = st.columns(3)
        year_data["annual_result"] = c1.number_input("Jahresergebnis", value=float(year_data["annual_result"]), step=100000.0)
        year_data["trade_tax"] = c2.number_input("Gewerbesteuererträge", value=float(year_data["trade_tax"]), step=100000.0)
        year_data["district_levy"] = c3.number_input("Kreisumlage", value=float(year_data["district_levy"]), step=100000.0)
        st.form_submit_button("Kennzahlen speichern")

    st.caption("Wesentliche Erträge")
    rev_cols = st.columns(2)
    for idx, key in enumerate(list(year_data["revenues"].keys())):
        year_data["revenues"][key] = rev_cols[idx % 2].number_input(
            f"{key} ({year})", value=float(year_data["revenues"][key]), key=f"rev_{year}_{key}"
        )

    st.caption("Wesentliche Aufwendungen")
    exp_cols = st.columns(2)
    for idx, key in enumerate(list(year_data["expenses"].keys())):
        year_data["expenses"][key] = exp_cols[idx % 2].number_input(
            f"{key} ({year})", value=float(year_data["expenses"][key]), key=f"exp_{year}_{key}"
        )

    year_data["total_investments"] = st.number_input(
        "Investitionen insgesamt", value=float(year_data["total_investments"]), step=100000.0, key=f"invest_{year}"
    )
    projects = st.text_area(
        "Projekte (eine Zeile pro Projekt)", value="\n".join(year_data["projects"]), key=f"proj_{year}"
    )
    year_data["projects"] = [p for p in projects.splitlines() if p.strip()]


def dashboard_view(name: str, rec: dict[str, Any]) -> None:
    st.title(name)
    st.markdown(f"### {rec['tagline']}")

    year = st.radio("Haushaltsjahr", YEARS, horizontal=True)
    data = rec["years"][year]

    a, b, c = st.columns(3)
    a.metric(f"Jahresergebnis {year}", money(data["annual_result"]))
    a.markdown(f"{badge(data['annual_result'] >= 0)} {'Überschuss' if data['annual_result'] >= 0 else 'Defizit'}")
    b.metric("Gewerbesteuererträge", money(data["trade_tax"]))
    b.markdown("🟢 Haupteinnahmequelle")
    c.metric("Kreisumlage", money(data["district_levy"]))
    c.markdown("🔴 Pflichtabgabe an den Kreis")

    d1, d2 = st.columns(2)
    rev_df = pd.DataFrame({"Kategorie": list(data["revenues"].keys()), "Wert": list(data["revenues"].values())})
    exp_df = pd.DataFrame({"Kategorie": list(data["expenses"].keys()), "Wert": list(data["expenses"].values())})

    def donut(df: pd.DataFrame, title: str):
        return alt.Chart(df).mark_arc(innerRadius=70).encode(theta=alt.Theta("Wert:Q"), color=alt.Color("Kategorie:N"), tooltip=["Kategorie", "Wert"]).properties(title=title)

    d1.altair_chart(donut(rev_df, "Wesentliche Erträge"), use_container_width=True)
    d2.altair_chart(donut(exp_df, "Wesentliche Aufwendungen"), use_container_width=True)

    st.markdown("### Haushaltssimulator")
    left, right = st.columns(2)
    with left:
        gw_factor = st.slider("Gewerbesteuer-Hebesatz (Faktor)", min_value=0.7, max_value=1.3, value=1.0, step=0.01)
        gr_factor = st.slider("Grundsteuer-Hebesatz (Faktor)", min_value=0.7, max_value=1.3, value=1.0, step=0.01)
        free_spend = st.slider("Freiwillige Aufwendungen", min_value=0.5, max_value=2.0, value=1.0, step=0.01)

    base = data["annual_result"]
    base_trade = data["revenues"].get("Gewerbesteuer", 0)
    base_property = data["revenues"].get("Grundsteuer", 0)
    voluntary = data["voluntary_services"]["total"]
    simulated = base + (gw_factor - 1) * base_trade + (gr_factor - 1) * base_property - (free_spend - 1) * voluntary

    with right:
        st.metric("Originales Ergebnis", money(base))
        st.metric("Simuliertes Ergebnis", money(simulated), delta=money(simulated - base))

    st.markdown("### Projekte und Investitionen")
    st.write("**Konkrete Projekte:**")
    for p in data["projects"]:
        with st.expander(p):
            st.write(f"Mehr Infos zum Projekt **{p}** können hier hinterlegt werden.")
    st.write(f"**Investitionen insgesamt:** {money(data['total_investments'])}")

    st.markdown("### Vergleich mit anderen Kommunen")
    for label, vals in data["benchmarks"].items():
        col1, col2, col3 = st.columns([2, 1, 2])
        col1.write(f"**{label}**")
        col2.write(f"Unsere Kommune: {vals['own']}")
        col3.write(f"Durchschnitt: {vals['avg']} · {vals['comment']}")

    st.markdown("### Freiwillige Leistungen")
    st.write(
        f"Gesamtvolumen: **{money(data['voluntary_services']['total'])}** "
        f"({data['voluntary_services']['share']} % des Gesamthaushalts)"
    )
    for item in data["voluntary_services"]["items"]:
        with st.expander(item):
            st.write(f"Zusatzinformationen zu **{item}**.")

    st.markdown("### Wussten Sie schon?")
    for fact in data["facts"]:
        st.info(fact)


def main() -> None:
    st.sidebar.title("Kommunalhaushalt-App")
    st.sidebar.caption("Private MVP-Version")

    if not login_guard():
        return

    data = load_data()
    mode = st.sidebar.radio("Bereich", ["Dashboard-Link", "Kommune bearbeiten"], index=0)

    if mode == "Dashboard-Link":
        slug = st.sidebar.selectbox("Kommune", list(data.keys()))
        token = st.text_input("Zugriffs-Token", type="password")
        if token != data[slug]["viewer_token"]:
            st.warning("Bitte gültigen Token eingeben, um das Dashboard zu sehen.")
            return
        dashboard_view(data[slug]["name"], data[slug])
        st.code(f"?kommune={slug}&token={data[slug]['viewer_token']}")
        st.caption("Diesen Link können Kommunen in ihre Webseite einbauen (aktuell privat abgesichert).")
        return

    slug = municipality_login(data)
    if not slug:
        return

    rec = data[slug]
    st.subheader(f"Datenpflege für {rec['name']}")
    st.caption("Schritt für Schritt ausfüllen – Zwischenspeichern jederzeit möglich.")
    selected = st.selectbox("Bearbeitungsschritt", YEARS)

    edit_year(rec["years"][selected], selected)
    if st.button("Alle Änderungen speichern", type="primary"):
        data[slug] = rec
        save_data(data)
        st.success("Daten gespeichert.")

    st.markdown("#### Öffentlicher Dashboard-Link (intern nutzbar)")
    st.code(f"?kommune={slug}&token={rec['viewer_token']}")


if __name__ == "__main__":
    main()
