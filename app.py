# app.py — Confronto costi: BLOCCO vs LASTRE
import streamlit as st
import pandas as pd
import base64

st.set_page_config(
    page_title="Confronto costi: BLOCCO vs LASTRE",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# Barra nera con logo (lys.png nella root del repo)
# ---------------------------
def get_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_base64 = get_base64("lys.png")

st.markdown(
    f"""
    <div style="
        background-color:#000000;
        width:100%;
        padding:18px 0px;
        display:flex;
        justify-content:center;
        align-items:center;
        margin-bottom:18px;
    ">
        <img src="data:image/png;base64,{logo_base64}" style="
            height:60px;
            width:auto;
            display:block;
        ">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# CSS: font più piccoli + cards BLOCCO/LASTRE
# ---------------------------
st.markdown("""
<style>
/* Titoli più piccoli */
h1 { font-size: 1.6rem !important; }
h2 { font-size: 1.20rem !important; }
h3 { font-size: 1.05rem !important; }

/* Metriche più compatte */
div[data-testid="stMetricValue"] { font-size: 1.15rem !important; }
div[data-testid="stMetricLabel"] { font-size: 0.88rem !important; }

/* Dataframe: testo più piccolo */
div[data-testid="stDataFrame"] * { font-size: 0.85rem !important; }

/* Cards */
.card-blocco {
    background: rgba(0, 80, 160, 0.12);
    border: 1px solid rgba(0, 80, 160, 0.35);
    padding: 16px;
    border-radius: 14px;
}

.card-lastre {
    background: rgba(200, 120, 0, 0.12);
    border: 1px solid rgba(200, 120, 0, 0.35);
    padding: 16px;
    border-radius: 14px;
}

.card-title {
    font-size: 1.02rem;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: 0.4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Calcolo
# ---------------------------
def calc(inputs: dict) -> dict:
    # Inputs
    B4 = float(inputs["lunghezza_blocco_mm"])
    B5 = float(inputs["altezza_blocco_mm"])
    B6 = float(inputs["profondita_blocco_mm"])
    B7 = float(inputs["squadra_per_lato_L_mm"])
    B8 = float(inputs["squadra_per_lato_H_mm"])
    B9 = float(inputs["kerf_mm"])
    B10 = float(inputs["spessore_finale_mm"])
    B11 = float(inputs["prezzo_blocco_eur_m3"])
    B12 = float(inputs["prezzo_blocco_eur_ton"])
    B13 = float(inputs["densita_kg_m3"])
    B15 = float(inputs["costo_segagione_eur_m3"])
    B16 = float(inputs["trasporto_blocco_eur"])

    B18 = float(inputs["lunghezza_lastra_acq_mm"])
    B19 = float(inputs["altezza_lastra_acq_mm"])
    B20 = float(inputs["spessore_lastra_acq_mm"])
    B21 = float(inputs["numero_lastre_acq_pz"])
    B22 = float(inputs["prezzo_lastre_eur_m2"])
    B23 = float(inputs["calibratura_extra_eur_m2"])
    B24 = float(inputs["splittatura_eur_m2"])
    B25 = float(inputs["taglio_misura_eur_m2"])
    B26 = float(inputs["trasporto_lastre_eur"])

    B28 = float(inputs["lunghezza_pezzo_finito_mm"])
    B29 = float(inputs["altezza_pezzo_finito_mm"])

    # --- BLOCCO
    E4 = max(0.0, B4 - 2 * B7)
    E5 = max(0.0, B5 - 2 * B8)
    E6 = (E4 / 1000.0) * (E5 / 1000.0)
    E7 = (B4 / 1000.0) * (B5 / 1000.0) * (B6 / 1000.0)

    denom = (B10 + B9)
    E8 = "" if denom == 0 else max(0, int((B6 + B9) // denom))
    E9 = "" if E8 == "" else E8 * 2

    E11 = E6 * (E9 if E9 != "" else 0)

    E12 = "" if (B28 == 0 or B29 == 0) else (B28 / 1000.0) * (B29 / 1000.0)

    if B28 == 0 or B29 == 0 or E4 == 0 or E5 == 0:
        E14 = ""
    else:
        a = int(E4 // B28) * int(E5 // B29)
        b = int(E4 // B29) * int(E5 // B28)
        E14 = max(a, b)

    E15 = "" if E14 == "" or E9 == "" else E14 * E9
    E13 = "" if E15 == "" else E15 * (E12 if E12 != "" else 0)

    if B11 > 0:
        E16 = E7 * B11
    elif B12 > 0:
        E16 = E7 * (B13 / 1000.0) * B12
    else:
        E16 = ""

    E17 = B15 * E7
    E18 = (E13 / 2.0) * B24 if E13 != "" else ""
    E21 = "" if E16 == "" else (E16 + E17 + (E18 if E18 != "" else 0) + B16)
    E22 = "" if E11 == 0 else (E21 / E11) if E21 != "" else ""
    E23 = "" if E15 == "" or E15 == 0 or E21 == "" else (E21 / E15)

    E25 = "" if E8 == "" else (0 if E8 == 0 else (E8 * B10 + (E8 - 1) * B9))
    E26 = "" if E25 == "" else max(0.0, B6 - E25)

    E10 = "" if E6 == 0 else (1.0 - (E13 / E11)) if E13 != "" else ""
    E51 = "" if E13 in ("", 0) or E21 == "" else E21 / E13

    # --- LASTRE
    E28 = (B18 / 1000.0) * (B19 / 1000.0)
    if B20 <= 0:
        E30 = ""
    else:
        E30 = 2 if B20 > 20 else 1

    E31 = "" if E30 == "" else B21 * E30
    E32 = E28 * B21
    E33 = "" if E31 == "" else E28 * E31

    if B28 == 0 or B29 == 0:
        E34 = ""
    else:
        a = int(B18 // B28) * int(B19 // B29)
        b = int(B18 // B29) * int(B19 // B28)
        E34 = max(a, b)

    E35 = "" if E34 == "" or E31 == "" else E34 * E31

    E36 = E32 * B22
    E44 = "" if E35 == "" else E35 * (E12 if E12 != "" else 0)

    if E44 == "":
        E39 = ""
    else:
        if B20 == 20:
            coef = (B23 + B25)
        elif B20 > 20:
            coef = (B25 / 2.0) + (B24 / 2.0)
        else:
            coef = 0.0
        E39 = E44 * coef

    E40 = "" if E39 == "" else (E36 + E39 + B26)
    E41 = "" if E33 in ("", 0) or E40 == "" else E40 / E33
    E42 = "" if E35 in ("", 0) or E40 == "" else E40 / E35

    E45 = "" if (E33 in ("", 0) or E12 == "") else (1.0 - (E44 / E33)) if E44 != "" else ""
    E46 = "" if E44 in ("", 0) or E40 == "" else E40 / E44

    # --- CONFRONTO
    E49 = "" if (E40 == "" or E21 == "") else (E40 - E21)
    E52 = "" if (E46 == "" or E51 == "") else (E46 - E51)
    E54 = "" if (E42 == "" or E23 == "") else ("Meglio BLOCCO" if E23 < E42 else "Meglio LASTRE")
    E55 = "" if (E21 == "" or E40 in ("", 0)) else (1.0 - (E21 / E40))

    return {
        "Costo totale BLOCCO (€)": E21,
        "Costo per pezzo finito – BLOCCO (€)": E23,
        "Costo per m² LORDO – BLOCCO (€/m²)": E22,
        "Costo per m² NETTO – BLOCCO (€/m²)": E51,
        "Sfrido % – BLOCCO": E10,
        "Pezzi totali – BLOCCO": E15,

        "Costo totale LASTRE (€)": E40,
        "Costo per pezzo finito – LASTRE (€)": E42,
        "Costo per m² LORDO – LASTRE (€/m²)": E41,
        "Costo per m² NETTO – LASTRE (€/m²)": E46,
        "Sfrido % – LASTRE": E45,
        "Pezzi totali – LASTRE": E35,

        "Differenza costo totale (LASTRE - BLOCCO) (€)": E49,
        "Differenza costo €/m² NETTO (LASTRE - BLOCCO)": E52,
        "Scelta (costo per pezzo finito)": E54,
        "Risparmio % BLOCCO vs LASTRE": E55,

        "Profondità usata (mm)": E25,
        "Residuo profondità (mm)": E26,
    }

def metric(label, val, kind="num"):
    if val == "" or val is None:
        st.metric(label, "—")
        return
    if kind == "eur":
        st.metric(label, f"{val:,.2f} €")
    elif kind == "eur_m2":
        st.metric(label, f"{val:,.2f} €/m²")
    elif kind == "pct":
        st.metric(label, f"{val*100:,.1f}%")
    else:
        st.metric(label, f"{val:,.2f}")

def format_2dec(v):
    if v == "" or v is None:
        return "—"
    if isinstance(v, str):
        return v
    return f"{v:,.2f}"

# ---------------------------
# UI
# ---------------------------
st.markdown("## Confronto costi: BLOCCO vs LASTRE")

defaults = dict(
    lunghezza_blocco_mm=3000,
    altezza_blocco_mm=1500,
    profondita_blocco_mm=1000,
    squadra_per_lato_L_mm=0,
    squadra_per_lato_H_mm=0,
    kerf_mm=5,
    spessore_finale_mm=25,
    prezzo_blocco_eur_m3=800,
    prezzo_blocco_eur_ton=0,
    densita_kg_m3=2700,
    costo_segagione_eur_m3=400,
    trasporto_blocco_eur=1000,

    lunghezza_lastra_acq_mm=2900,
    altezza_lastra_acq_mm=1500,
    spessore_lastra_acq_mm=30,
    numero_lastre_acq_pz=33,
    prezzo_lastre_eur_m2=85,
    calibratura_extra_eur_m2=6,
    splittatura_eur_m2=20,
    taglio_misura_eur_m2=7,
    trasporto_lastre_eur=400,

    lunghezza_pezzo_finito_mm=2500,
    altezza_pezzo_finito_mm=1250,
)

inputs = {}
with st.expander("Input (apri/chiudi)", expanded=False):
    st.subheader("Blocco")
    c1, c2 = st.columns(2)
    with c1:
        inputs["lunghezza_blocco_mm"] = st.number_input("Lunghezza blocco (mm)", value=float(defaults["lunghezza_blocco_mm"]), step=10.0)
        inputs["profondita_blocco_mm"] = st.number_input("Profondità blocco (mm)", value=float(defaults["profondita_blocco_mm"]), step=10.0)
        inputs["squadra_per_lato_L_mm"] = st.number_input("Squadratura per lato (L) (mm)", value=float(defaults["squadra_per_lato_L_mm"]), step=1.0)
        inputs["kerf_mm"] = st.number_input("Strido / kerf (mm)", value=float(defaults["kerf_mm"]), step=0.5)
    with c2:
        inputs["altezza_blocco_mm"] = st.number_input("Altezza blocco (mm)", value=float(defaults["altezza_blocco_mm"]), step=10.0)
        inputs["squadra_per_lato_H_mm"] = st.number_input("Squadratura per lato (H) (mm)", value=float(defaults["squadra_per_lato_H_mm"]), step=1.0)
        inputs["spessore_finale_mm"] = st.number_input("Spessore lastra finale (mm)", value=float(defaults["spessore_finale_mm"]), step=1.0)

    st.subheader("Prezzi blocco")
    c1, c2, c3 = st.columns(3)
    with c1:
        inputs["prezzo_blocco_eur_m3"] = st.number_input("Prezzo (€/m³)", value=float(defaults["prezzo_blocco_eur_m3"]), step=10.0)
        inputs["costo_segagione_eur_m3"] = st.number_input("Segagione (€/m³)", value=float(defaults["costo_segagione_eur_m3"]), step=10.0)
    with c2:
        inputs["prezzo_blocco_eur_ton"] = st.number_input("Prezzo (€/ton) (opz.)", value=float(defaults["prezzo_blocco_eur_ton"]), step=10.0)
        inputs["densita_kg_m3"] = st.number_input("Densità (kg/m³)", value=float(defaults["densita_kg_m3"]), step=10.0)
    with c3:
        inputs["trasporto_blocco_eur"] = st.number_input("Trasporto BLOCCO (€)", value=float(defaults["trasporto_blocco_eur"]), step=50.0)

    st.subheader("Lastre acquistate")
    c1, c2 = st.columns(2)
    with c1:
        inputs["lunghezza_lastra_acq_mm"] = st.number_input("Lunghezza lastra (mm)", value=float(defaults["lunghezza_lastra_acq_mm"]), step=10.0)
        inputs["spessore_lastra_acq_mm"] = st.number_input("Spessore lastra (mm)", value=float(defaults["spessore_lastra_acq_mm"]), step=1.0)
        inputs["prezzo_lastre_eur_m2"] = st.number_input("Prezzo lastre (€/m²)", value=float(defaults["prezzo_lastre_eur_m2"]), step=1.0)
        inputs["splittatura_eur_m2"] = st.number_input("Splittatura (€/m²)", value=float(defaults["splittatura_eur_m2"]), step=0.5)
    with c2:
        inputs["altezza_lastra_acq_mm"] = st.number_input("Altezza lastra (mm)", value=float(defaults["altezza_lastra_acq_mm"]), step=10.0)
        inputs["numero_lastre_acq_pz"] = st.number_input("N° lastre acquistate (pz)", value=float(defaults["numero_lastre_acq_pz"]), step=1.0)
        inputs["calibratura_extra_eur_m2"] = st.number_input("Calibratura (se 20mm) (€/m²)", value=float(defaults["calibratura_extra_eur_m2"]), step=0.5)
        inputs["taglio_misura_eur_m2"] = st.number_input("Taglio a misura (€/m²)", value=float(defaults["taglio_misura_eur_m2"]), step=0.5)

    inputs["trasporto_lastre_eur"] = st.number_input("Trasporto LASTRE (€)", value=float(defaults["trasporto_lastre_eur"]), step=50.0)

    st.subheader("Formato pezzo finito")
    c1, c2 = st.columns(2)
    with c1:
        inputs["lunghezza_pezzo_finito_mm"] = st.number_input("Lunghezza pezzo (mm)", value=float(defaults["lunghezza_pezzo_finito_mm"]), step=10.0)
    with c2:
        inputs["altezza_pezzo_finito_mm"] = st.number_input("Altezza pezzo (mm)", value=float(defaults["altezza_pezzo_finito_mm"]), step=10.0)

res = calc(inputs)

# ---------------------------
# Risultati principali (cards)
# ---------------------------
st.subheader("Risultati principali")

colA, colB = st.columns(2)

with colA:
    st.markdown('<div class="card-blocco"><div class="card-title">BLOCCO</div>', unsafe_allow_html=True)
    metric("Costo totale", res["Costo totale BLOCCO (€)"], "eur")
    metric("€/m² NETTO", res["Costo per m² NETTO – BLOCCO (€/m²)"], "eur_m2")
    metric("Costo/pezzo", res["Costo per pezzo finito – BLOCCO (€)"], "eur")
    metric("Sfrido", res["Sfrido % – BLOCCO"], "pct")
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown('<div class="card-lastre"><div class="card-title">LASTRE</div>', unsafe_allow_html=True)
    metric("Costo totale", res["Costo totale LASTRE (€)"], "eur")
    metric("€/m² NETTO", res["Costo per m² NETTO – LASTRE (€/m²)"], "eur_m2")
    metric("Costo/pezzo", res["Costo per pezzo finito – LASTRE (€)"], "eur")
    metric("Sfrido", res["Sfrido % – LASTRE"], "pct")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Confronto
# ---------------------------
st.divider()
st.subheader("Confronto")

c1, c2 = st.columns(2)
with c1:
    metric("Differenza costo totale (LASTRE - BLOCCO)", res["Differenza costo totale (LASTRE - BLOCCO) (€)"], "eur")
    metric("Differenza €/m² NETTO (LASTRE - BLOCCO)", res["Differenza costo €/m² NETTO (LASTRE - BLOCCO)"], "eur_m2")
with c2:
    st.metric("Scelta (costo per pezzo finito)", res["Scelta (costo per pezzo finito)"] if res["Scelta (costo per pezzo finito)"] else "—")
    metric("Risparmio % BLOCCO vs LASTRE", res["Risparmio % BLOCCO vs LASTRE"], "pct")

# ---------------------------
# Dettaglio
# ---------------------------
with st.expander("Dettaglio (valori di controllo / debug)", expanded=False):
    df = pd.DataFrame({"Voce": list(res.keys()), "Valore": [format_2dec(res[k]) for k in res.keys()]})
    st.dataframe(df, use_container_width=True)

st.caption("Suggerimento: su mobile apri l’area “Input” solo quando devi cambiare i parametri.")
