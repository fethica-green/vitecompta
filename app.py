import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="ViteCompta", page_icon="💼", layout="centered")
st.title("💼 ViteCompta")
st.subheader("La comptabilité rapide et automatisée pour les indépendants")

# Chargement/initialisation
DATA_FILE = "transactions.csv"
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Date", "Type", "Montant", "Catégorie", "TVA", "Description"])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["Date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Tabs
tabs = st.tabs(["➕ Saisie", "📊 Tableau de bord", "📁 États financiers"])

# Tab 1 – Saisie
with tabs[0]:
    st.markdown("### Ajouter une opération")
    with st.form("form_saisie"):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", datetime.today())
        type_op = col2.selectbox("Type", ["Recette", "Dépense"])
        montant = st.number_input("Montant (€)", min_value=0.0, step=0.5)
        categorie = st.text_input("Catégorie")
        tva = st.number_input("TVA (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        desc = st.text_area("Description")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            df = load_data()
            new_row = pd.DataFrame([[date, type_op, montant, categorie, tva, desc]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("✅ Opération ajoutée avec succès !")

# Tab 2 – Dashboard
with tabs[1]:
    st.markdown("### Vue d'ensemble")
    df = load_data()
    if df.empty:
        st.info("Aucune donnée disponible.")
    else:
        recettes = df[df["Type"] == "Recette"]["Montant"].sum()
        depenses = df[df["Type"] == "Dépense"]["Montant"].sum()
        resultat = recettes - depenses

        col1, col2, col3 = st.columns(3)
        col1.metric("Chiffre d'affaires", f"{recettes:.2f} €")
        col2.metric("Charges", f"{depenses:.2f} €")
        col3.metric("Résultat net", f"{resultat:.2f} €")

        df["Mois"] = df["Date"].dt.to_period("M").astype(str)
        cashflow = df.groupby(["Mois", "Type"]).sum(numeric_only=True).reset_index()
        pivot = cashflow.pivot(index="Mois", columns="Type", values="Montant").fillna(0)
        pivot["Solde"] = pivot.get("Recette", 0) - pivot.get("Dépense", 0)
        st.line_chart(pivot["Solde"])
        st.dataframe(pivot)

# Tab 3 – États Financiers
with tabs[2]:
    st.markdown("### 📄 États financiers")
    df = load_data()
    if df.empty:
        st.info("Aucune donnée disponible.")
    else:
        recettes = df[df["Type"] == "Recette"]["Montant"].sum()
        depenses = df[df["Type"] == "Dépense"]["Montant"].sum()
        resultat = recettes - depenses

        bilan_df = pd.DataFrame({
            "Actif": ["Trésorerie"],
            "Montant Actif (€)": [recettes - depenses],
            "Passif": ["Résultat net"],
            "Montant Passif (€)": [resultat]
        })

        st.markdown("#### 🧾 Bilan simplifié")
        st.dataframe(bilan_df)

        st.markdown("#### 📊 Compte de résultat")
        st.write(f"**Chiffre d'affaires** : {recettes:.2f} €")
        st.write(f"**Charges** : {depenses:.2f} €")
        st.write(f"**Résultat net** : {resultat:.2f} €")

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transactions', index=False)
            bilan_df.to_excel(writer, sheet_name='Bilan', index=False)
        output.seek(0)
        st.download_button("📥 Exporter en Excel", data=output, file_name="vitecompta_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
