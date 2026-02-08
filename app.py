import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Confronto costi: Blocco vs Lastre", layout="wide")

def safe_int(x):
    try:
        return int(x)
    except Exception:
        return None

def calc(inputs: dict) -> dict:
    # Inputs (matching the Excel model)
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

    # --- BLOCCO (Excel E4..E26 + E16..E23 + E51)
    E4 = max(0.0, B4 - 2 * B7)  # lunghezza lastra grezza
    E5 = max(0.0, B5 - 2 * B8)  # altezza lastra grezza
    E6 = (E4 / 1000.0) * (E5 / 1000.0)  # area per lastra grezza
    E7 = (B4 / 1000.0) * (B5 / 1000.0) * (B6 / 1000.0)  # volume blocco m3

    # E8: lastre prima splittatura (taglio 25mm nel file; qui usiamo lo spessore finale desiderato come proxy)
    # Excel: INT((B6+B9)/(25+B9)) con MAX(0, ...)
    denom = (B10 + B9)
    E8 = "" if denom == 0 else max(0, int((B6 + B9) // denom))
    E9 = "" if E8 == "" else E8 * 2  # lastre finali dopo splittatura

    E11 = E6 * (E9 if E9 != "" else 0)  # area totale grezza
    E12 = "" if (B28 == 0 or B29 == 0) else (B28 / 1000.0) * (B29 / 1000.0)  # area pezzo finito
    # E14 pezzi per lastra
    if B28 == 0 or B29 == 0 or E4 == 0 or E5 == 0:
        E14 = ""
    else:
        # MAX(INT(E4/B28)*INT(E5/B29), INT(E4/B29)*INT(E5/B28))
        a = int(E4 // B28) * int(E5 // B29)
        b = int(E4 // B29) * int(E5 // B28)
        E14 = max(a, b)
    E15 = "" if E14 == "" or E9 == "" else E14 * E9  # pezzi totali
    E13 = "" if E15 == "" else E15 * (E12 if E12 != "" else 0)  # area netta ottenuta

    # costo blocco (E16) in base a €/m3 o €/ton
    if B11 > 0:
        E16 = E7 * B11
    elif B12 > 0:
        E16 = E7 * (B13 / 1000.0) * B12  # densità kg/m3 -> ton/m3
    else:
        E16 = ""

    # costi lavorazioni su blocco
    E18 = (E13 / 2.0) * B24 if E13 != "" else ""  # costo splittatura lastre
    E17 = B15 * E7  # costo tot segagione
    E21 = "" if E16 == "" else (E16 + E17 + (E18 if E18 != "" else 0) + B16)  # totale scenario blocco
    E22 = "" if E11 == 0 else (E21 / E11) if E21 != "" else ""  # costo per m2 grezzo
    E23 = "" if E15 == "" or E15 == 0 or E21 == "" else (E21 / E15)  # costo per pezzo finito (formato)

    # kerf usage (E25/E26)
    E25 = "" if E8 == "" else (0 if E8 == 0 else (E8 * B10 + (E8 - 1) * B9))
    E26 = "" if E25 == "" else max(0.0, B6 - E25)

    # sfrido blocco (E10)
    E10 = "" if E6 == 0 else (1.0 - (E13 / E11)) if E13 != "" else ""

    # costo per m2 netto blocco (E51)
    E51 = "" if E13 in ("", 0) or E21 == "" else E21 / E13

    # --- LASTRE ACQUISTATE (Excel E28..E46 + E36..E42)
    E28 = (B18 / 1000.0) * (B19 / 1000.0)  # area per lastra acquistata
    E29 = (B28 * B29) / 1_000_000.0 if (B28 and B29) else ""  # area lastra formato finito (non usata nel file)
    # lastre ricavabili dallo spessore
    if B20 == "" or B20 <= 0:
        E30 = ""
    else:
        E30 = 2 if B20 > 20 else 1

    E31 = "" if E30 == "" else B21 * E30  # lastre totali ricavate
    E32 = E28 * B21  # area totale senza splittatura
    E33 = "" if E31 == "" else E28 * E31  # area totale ricavata

    if B28 == 0 or B29 == 0:
        E34 = ""
    else:
        a = int(B18 // B28) * int(B19 // B29)
        b = int(B18 // B29) * int(B19 // B28)
        E34 = max(a, b)
    E35 = "" if E34 == "" or E31 == "" else E34 * E31  # pezzi totali

    E36 = E32 * B22  # costo acquisto lastre

    # costo lavorazioni tot (E39): E44 * (IF(B20=20, B23+B25, IF(B20>20, (B25/2)+(B24/2), 0)))
    E44 = "" if E35 == "" else E35 * (E12 if E12 != "" else 0)  # area netta ottenuta
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

    E40 = "" if E39 == "" else (E36 + E39 + B26)  # costo totale scenario lastre
    E41 = "" if E33 in ("", 0) or E40 == "" else E40 / E33  # costo per m2 lordo
    E42 = "" if E35 in ("", 0) or E40 == "" else E40 / E35  # costo per pezzo finito

    E45 = "" if (E33 in ("", 0) or E12 == "") else (1.0 - (E44 / E33)) if E44 != "" else ""
    E46 = "" if E44 in ("", 0) or E40 == "" else E40 / E44  # costo per m2 netto

    # --- CONFRONTO (Excel E49..E55)
    E49 = "" if (E40 == "" or E21 == "") else (E40 - E21)
    E50 = "" if (E41 == "" or E22 == "") else (E41 - E22)
    E52 = "" if (E46 == "" or E51 == "") else (E46 - E51)
    E53 = "" if (E42 == "" or E23 == "") else (E42 - E23)
    E54 = "" if (E42 == "" or E23 == "") else ("Meglio BLOCCO" if E23 < E42 else "Meglio LASTRE")
    E55 = "" if (E21 == "" or E40 in ("", 0)) else (1.0 - (E21 / E40))

    return {
        # blocco
        "Lunghezza lastra grezza (mm)": E4,
        "Altezza lastra grezza (mm)": E5,
        "Area per lastra grezza (m²)": E6,
        "Volume blocco (m³)": E7,
        "N° lastre (prima splittatura)": E8,
        "N° lastre finali": E9,
        "Area totale grezza (m²) – BLOCCO": E11,
        "Pezzi per lastra (formato)": E14,
        "Pezzi totali (formato) – BLOCCO": E15,
        "Area netta ottenuta (m²) – BLOCCO": E13,
        "Sfrido % – BLOCCO": E10,
        "Costo blocco (€)": E16,
        "Costo segagione (tot) (€)": E17,
        "Costo splittatura (tot) (€)": E18,
        "Costo totale BLOCCO (€)": E21,
        "Costo per m² LORDO – BLOCCO (€/m²)": E22,
        "Costo per pezzo finito – BLOCCO (€)": E23,
        "Costo per m² NETTO – BLOCCO (€/m²)": E51,
        # lastre
        "Area per lastra acquistata (m²)": E28,
        "N° lastre ricavabili dallo spessore": E30,
        "N° lastre totali ricavate": E31,
        "Area totale ricavata (m²) – LASTRE": E33,
        "Pezzi per lastra (formato) – LASTRE": E34,
        "Pezzi totali (formato) – LASTRE": E35,
        "Area netta ottenuta (m²) – LASTRE": E44,
        "Sfrido % – LASTRE": E45,
        "Costo acquisto lastre (€)": E36,
        "Costo lavorazioni (tot) (€)": E39,
        "Costo totale LASTRE (€)": E40,
        "Costo per m² LORDO – LASTRE (€/m²)": E41,
        "Costo per pezzo finito – LASTRE (€)": E42,
        "Costo per m² NETTO – LASTRE (€/m²)": E46,
        # confronto
        "Differenza costo totale (LASTRE - BLOCCO) (€)": E49,
        "Differenza costo €/m² LORDO (LASTRE - BLOCCO)": E50,
        "Differenza costo €/m² NETTO (LASTRE - BLOCCO)": E52,
        "Differenza costo per pezzo (LASTRE - BLOCCO) (€)": E53,
        "Scelta (costo per pezzo finito)": E54,
        "Risparmio % BLOCCO vs LASTRE": E55,
        # debug utili
        "Profondità usata (mm)": E25,
        "Residuo profondità (mm)": E26,
    }

def fmt(v):
    if v == "" or v is None:
        return "—"
    if isinstance(v, str):
        return v
    # percentuali (valori 0..1) riconosciuti dal nome nel dataframe a valle
    return v

st.title("Confronto costi: BLOCCO vs LASTRE ACQUISTATE")

# Default values taken from the Excel file
defaults = dict(
    # BLOCCO
    lunghezza_blocco_mm=3000,
    altezza_blocco_mm=1500,
    profondita_blocco_mm=1000,
    squadra_per_lato_L_mm=0,     # non presente come input esplicito nel file; default 0
    squadra_per_lato_H_mm=0,     # non presente come input esplicito nel file; default 0
    kerf_mm=5,
    spessore_finale_mm=25,
    prezzo_blocco_eur_m3=800,
    prezzo_blocco_eur_ton=0,
    densita_kg_m3=2700,
    costo_segagione_eur_m3=400,
    trasporto_blocco_eur=1000,
    # LASTRE ACQUISTATE
    lunghezza_lastra_acq_mm=2900,
    altezza_lastra_acq_mm=1500,
    spessore_lastra_acq_mm=30,
    numero_lastre_acq_pz=33,
    prezzo_lastre_eur_m2=85,
    calibratura_extra_eur_m2=6,
    splittatura_eur_m2=20,
    taglio_misura_eur_m2=7,
    trasporto_lastre_eur=400,
    # PEZZO
    lunghezza_pezzo_finito_mm=2500,
    altezza_pezzo_finito_mm=1250,
)

with st.sidebar:
    st.header("Input")
    st.subheader("Blocco")
    inputs = {}
    inputs["lunghezza_blocco_mm"] = st.number_input("Lunghezza blocco (mm)", value=float(defaults["lunghezza_blocco_mm"]), step=10.0)
    inputs["altezza_blocco_mm"] = st.number_input("Altezza blocco (mm)", value=float(defaults["altezza_blocco_mm"]), step=10.0)
    inputs["profondita_blocco_mm"] = st.number_input("Profondità blocco (mm) (direzione taglio)", value=float(defaults["profondita_blocco_mm"]), step=10.0)
    inputs["squadra_per_lato_L_mm"] = st.number_input("Squadratura per lato (L) (mm)", value=float(defaults["squadra_per_lato_L_mm"]), step=1.0)
    inputs["squadra_per_lato_H_mm"] = st.number_input("Squadratura per lato (H) (mm)", value=float(defaults["squadra_per_lato_H_mm"]), step=1.0)
    inputs["kerf_mm"] = st.number_input("Strido / kerf per taglio (mm)", value=float(defaults["kerf_mm"]), step=0.5)
    inputs["spessore_finale_mm"] = st.number_input("Spessore lastra finale desiderato (mm)", value=float(defaults["spessore_finale_mm"]), step=1.0)

    st.subheader("Prezzi blocco")
    inputs["prezzo_blocco_eur_m3"] = st.number_input("Prezzo blocco (€/m³) (0 se usi €/ton)", value=float(defaults["prezzo_blocco_eur_m3"]), step=10.0)
    inputs["prezzo_blocco_eur_ton"] = st.number_input("Prezzo blocco (€/ton) (0 se usi €/m³)", value=float(defaults["prezzo_blocco_eur_ton"]), step=10.0)
    inputs["densita_kg_m3"] = st.number_input("Densità materiale (kg/m³)", value=float(defaults["densita_kg_m3"]), step=10.0)
    inputs["costo_segagione_eur_m3"] = st.number_input("Costo segagione incluso squadratura (€/m³)", value=float(defaults["costo_segagione_eur_m3"]), step=10.0)
    inputs["trasporto_blocco_eur"] = st.number_input("Trasporto BLOCCO (€)", value=float(defaults["trasporto_blocco_eur"]), step=50.0)

    st.subheader("Lastre acquistate")
    inputs["lunghezza_lastra_acq_mm"] = st.number_input("Lunghezza lastra acquistata (mm)", value=float(defaults["lunghezza_lastra_acq_mm"]), step=10.0)
    inputs["altezza_lastra_acq_mm"] = st.number_input("Altezza lastra acquistata (mm)", value=float(defaults["altezza_lastra_acq_mm"]), step=10.0)
    inputs["spessore_lastra_acq_mm"] = st.number_input("Spessore lastra acquistata (mm)", value=float(defaults["spessore_lastra_acq_mm"]), step=1.0)
    inputs["numero_lastre_acq_pz"] = st.number_input("Numero lastre acquistate (pz)", value=float(defaults["numero_lastre_acq_pz"]), step=1.0)
    inputs["prezzo_lastre_eur_m2"] = st.number_input("Prezzo lastre acquistate (€/m²)", value=float(defaults["prezzo_lastre_eur_m2"]), step=1.0)
    inputs["calibratura_extra_eur_m2"] = st.number_input("Calibratura extra se spessore = 20 mm (€/m²)", value=float(defaults["calibratura_extra_eur_m2"]), step=0.5)
    inputs["splittatura_eur_m2"] = st.number_input("Splittatura se spessore > 20 mm (€/m²)", value=float(defaults["splittatura_eur_m2"]), step=0.5)
    inputs["taglio_misura_eur_m2"] = st.number_input("Taglio a misura lastre (€/m²)", value=float(defaults["taglio_misura_eur_m2"]), step=0.5)
    inputs["trasporto_lastre_eur"] = st.number_input("Trasporto LASTRE (€)", value=float(defaults["trasporto_lastre_eur"]), step=50.0)

    st.subheader("Pezzo / formato finito (0 = disattivo)")
    inputs["lunghezza_pezzo_finito_mm"] = st.number_input("Lunghezza pezzo finito (mm)", value=float(defaults["lunghezza_pezzo_finito_mm"]), step=10.0)
    inputs["altezza_pezzo_finito_mm"] = st.number_input("Altezza pezzo finito (mm)", value=float(defaults["altezza_pezzo_finito_mm"]), step=10.0)

res = calc(inputs)

# Helper: format for display
def display_metrics(cols, items):
    c = st.columns(cols)
    for i, (label, val, kind) in enumerate(items):
        with c[i % cols]:
            if val == "" or val is None:
                st.metric(label, "—")
            elif kind == "eur":
                st.metric(label, f"{val:,.2f} €")
            elif kind == "eur_m2":
                st.metric(label, f"{val:,.2f} €/m²")
            elif kind == "pct":
                st.metric(label, f"{val*100:,.1f}%")
            else:
                st.metric(label, f"{val:,.2f}")

top = st.columns(2)
with top[0]:
    st.subheader("Risultati principali – BLOCCO")
    display_metrics(2, [
        ("Costo totale", res["Costo totale BLOCCO (€)"], "eur"),
        ("Costo per pezzo finito", res["Costo per pezzo finito – BLOCCO (€)"], "eur"),
        ("Costo per m² LORDO", res["Costo per m² LORDO – BLOCCO (€/m²)"], "eur_m2"),
        ("Costo per m² NETTO", res["Costo per m² NETTO – BLOCCO (€/m²)"], "eur_m2"),
        ("Sfrido %", res["Sfrido % – BLOCCO"], "pct"),
        ("Pezzi totali", res["Pezzi totali (formato) – BLOCCO"], "num"),
    ])

with top[1]:
    st.subheader("Risultati principali – LASTRE ACQUISTATE")
    display_metrics(2, [
        ("Costo totale", res["Costo totale LASTRE (€)"], "eur"),
        ("Costo per pezzo finito", res["Costo per pezzo finito – LASTRE (€)"], "eur"),
        ("Costo per m² LORDO", res["Costo per m² LORDO – LASTRE (€/m²)"], "eur_m2"),
        ("Costo per m² NETTO", res["Costo per m² NETTO – LASTRE (€/m²)"], "eur_m2"),
        ("Sfrido %", res["Sfrido % – LASTRE"], "pct"),
        ("Pezzi totali", res["Pezzi totali (formato) – LASTRE"], "num"),
    ])

st.divider()
st.subheader("Confronto")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Differenza costo totale (LASTRE - BLOCCO)", "—" if res["Differenza costo totale (LASTRE - BLOCCO) (€)"]=="" else f"{res['Differenza costo totale (LASTRE - BLOCCO) (€)']:,.2f} €")
with c2:
    st.metric("Differenza €/m² NETTO (LASTRE - BLOCCO)", "—" if res["Differenza costo €/m² NETTO (LASTRE - BLOCCO)"]=="" else f"{res['Differenza costo €/m² NETTO (LASTRE - BLOCCO)']:,.2f} €/m²")
with c3:
    st.metric("Scelta (costo per pezzo finito)", res["Scelta (costo per pezzo finito)"] if res["Scelta (costo per pezzo finito)"]!="" else "—")

# Details tables
left, right = st.columns(2)
with left:
    st.subheader("Dettaglio – BLOCCO")
    keys = [
        "Lunghezza lastra grezza (mm)","Altezza lastra grezza (mm)","Area per lastra grezza (m²)","Volume blocco (m³)",
        "N° lastre (prima splittatura)","N° lastre finali","Area totale grezza (m²) – BLOCCO",
        "Pezzi per lastra (formato)","Pezzi totali (formato) – BLOCCO","Area netta ottenuta (m²) – BLOCCO",
        "Sfrido % – BLOCCO","Costo blocco (€)","Costo segagione (tot) (€)","Costo splittatura (tot) (€)",
        "Costo totale BLOCCO (€)","Costo per m² LORDO – BLOCCO (€/m²)","Costo per m² NETTO – BLOCCO (€/m²)",
        "Costo per pezzo finito – BLOCCO (€)","Profondità usata (mm)","Residuo profondità (mm)"
    ]
    df = pd.DataFrame({"Voce": keys, "Valore": [res[k] for k in keys]})
    st.dataframe(df, use_container_width=True)

with right:
    st.subheader("Dettaglio – LASTRE ACQUISTATE")
    keys = [
        "Area per lastra acquistata (m²)","N° lastre ricavabili dallo spessore","N° lastre totali ricavate",
        "Area totale ricavata (m²) – LASTRE","Pezzi per lastra (formato) – LASTRE","Pezzi totali (formato) – LASTRE",
        "Area netta ottenuta (m²) – LASTRE","Sfrido % – LASTRE","Costo acquisto lastre (€)","Costo lavorazioni (tot) (€)",
        "Costo totale LASTRE (€)","Costo per m² LORDO – LASTRE (€/m²)","Costo per m² NETTO – LASTRE (€/m²)",
        "Costo per pezzo finito – LASTRE (€)"
    ]
    df = pd.DataFrame({"Voce": keys, "Valore": [res[k] for k in keys]})
    st.dataframe(df, use_container_width=True)

st.caption("Nota: questa app replica la logica del foglio Excel. Se il tuo file Excel usa una regola diversa per il calcolo del numero lastre (prima splittatura), dimmi quale e la adeguo.")
