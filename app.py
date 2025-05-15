import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="ViteCompta", page_icon="💼", layout="wide")

# En-tête avec logo
st.markdown("""
<div style='display: flex; align-items: center;'>
    <img src='https://raw.githubusercontent.com/yourusername/vitecompta/main/logo_bleu.png' width='70'>
    <h1 style='margin-left: 15px; color: #2c3e50;'>ViteCompta</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color: #555'>Votre comptabilité simplifiée et automatisée</h3>", unsafe_allow_html=True)

# Barre horizontale de navigation avec boutons
pages = ["🏠 Accueil", "➕ Saisie", "📊 Tableau de bord", "📁 États financiers", "ℹ️ À propos"]
selected_page = st.columns(len(pages))
for i, page in enumerate(pages):
    if selected_page[i].button(page):
        st.session_state["page"] = page

if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Accueil"

DATA_FILE = "data/transactions.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Date", "Type", "Montant", "Catégorie", "TVA", "Description"])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["Date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Page Accueil
if st.session_state.page == "🏠 Accueil":
    st.markdown("""
    ### Bienvenue sur ViteCompta 👋
    Cette application vous aide à gérer votre comptabilité quotidienne simplement, rapidement et efficacement. 
    Choisissez une section dans le menu ci-dessus pour commencer.
    """)

# Page Saisie
elif st.session_state.page == "➕ Saisie":
    st.markdown("<h4 style='color:#2c3e50;'>Ajouter une opération</h4>", unsafe_allow_html=True)
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

# Page Dashboard
elif st.session_state.page == "📊 Tableau de bord":
    st.markdown("<h4 style='color:#2c3e50;'>Vue d'ensemble</h4>", unsafe_allow_html=True)
    df = load_data()
    if df.empty:
        st.info("Aucune donnée disponible. Ajoutez des opérations.")
    else:
        recettes = df[df["Type"] == "Recette"]["Montant"].sum()
        depenses = df[df["Type"] == "Dépense"]["Montant"].sum()
        resultat = recettes - depenses

        st.markdown("### 📈 Indicateurs clés")
        col1, col2, col3 = st.columns(3)
        col1.metric("Chiffre d'affaires", f"{recettes:,.2f} €")
        col2.metric("Charges", f"{depenses:,.2f} €")
        col3.metric("Résultat net", f"{resultat:,.2f} €")

        st.markdown("### 💵 Cash Flow mensuel")
        df["Mois"] = df["Date"].dt.to_period("M").astype(str)
        cashflow = df.groupby(["Mois", "Type"]).sum(numeric_only=True).reset_index()
        pivot = cashflow.pivot(index="Mois", columns="Type", values="Montant").fillna(0)
        pivot["Solde"] = pivot.get("Recette", 0) - pivot.get("Dépense", 0)
        st.line_chart(pivot["Solde"])
        st.dataframe(pivot)

# Page États Financiers
elif st.session_state.page == "📁 États financiers":
    st.markdown("<h4 style='color:#2c3e50;'>📄 États financiers</h4>", unsafe_allow_html=True)
    df = load_data()
    if df.empty:
        st.info("Aucune donnée disponible pour générer un état.")
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

# Page À propos
elif st.session_state.page == "ℹ️ À propos":
    st.markdown("""
    ### ℹ️ À propos de ViteCompta
    ViteCompta est une application pensée pour simplifier la gestion comptable des petits indépendants : chauffeurs VTC, commerçants, freelances...

    Elle a été créée pour vous faire gagner du temps, éviter les erreurs fiscales, et suivre en temps réel votre activité.

    **Contact :** me.trabelsi@gmail.com  
    **Version :** 1.0 Bêta  
    """)
