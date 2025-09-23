import streamlit as st
import pandas as pd
import altair as alt
import os
# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Biblioteca olfativa",
    page_icon="🥀",
    layout="wide"
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">

    <style>
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🥀 Biblioteca olfativa 🥀")
# -----------------------------
# Cargar Excel
# -----------------------------
df = pd.read_excel("Catalogo/perfumes.xlsx", sheet_name="Hoja1")
if "IMAGEN" not in df.columns:
    df["IMAGEN"] = None

# -----------------------------
# Selección de marca
# -----------------------------
marcas = ["Todas las marcas"] + sorted(df["MARCA"].astype(str).unique())
marca_sel = st.selectbox("Ingrese la marca:", marcas)

# -----------------------------
# Buscador
# -----------------------------
busqueda = st.text_input("🔍 Buscar por perfume, perfil o definiciones:")

if marca_sel == "Todas las marcas":
    if busqueda:
        mask = (
            df["PERFUME"].str.contains(busqueda, case=False, na=False)
            | df["PERFIL PRINCIPAL"].str.contains(busqueda, case=False, na=False)
            | df["PERFIL SECUNDARIO"].str.contains(busqueda, case=False, na=False)
            | df["ACORDES"].str.contains(busqueda, case=False, na=False)
        )
        df_filtrado = df[mask]
    else:
        df_filtrado = pd.DataFrame(columns=df.columns)  # vacío hasta que busque
else:
    df_filtrado = df[df["MARCA"] == marca_sel]
    if busqueda:
        mask = (
            df_filtrado["PERFUME"].str.contains(busqueda, case=False, na=False)
            | df_filtrado["PERFIL PRINCIPAL"].str.contains(busqueda, case=False, na=False)
            | df_filtrado["PERFIL SECUNDARIO"].str.contains(busqueda, case=False, na=False)
            | df_filtrado["ACORDES"].str.contains(busqueda, case=False, na=False)
        )
        df_filtrado = df_filtrado[mask]


# -----------------------------
# Toggle mostrar todos
# -----------------------------
mostrar_todos = st.toggle("👀 Mostrar todos los perfumes", value=False)

# -----------------------------
# Layout en grilla
# -----------------------------
st.subheader(f"Perfumes de {marca_sel}")
if df_filtrado.empty:
    st.warning("No se encontraron perfumes.")
else:
    n_cols = 3
    if mostrar_todos:
        df_a_mostrar = df_filtrado
    else:
        df_a_mostrar = df_filtrado.head(n_cols)

    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(df_a_mostrar.iterrows()):
        with cols[i % n_cols]:
            # Imagen
            if pd.notna(row["IMAGEN"]) and os.path.exists(row["IMAGEN"]):
                st.image(row["IMAGEN"], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/200", caption="Sin imagen", use_container_width=True)

            # Info adaptada al tema
            with st.container(border=True):
                st.subheader(row["PERFUME"])
                st.write(f"**Perfil:** {row['PERFIL PRINCIPAL']}")
                st.write(f"**Secundario:** {row['PERFIL SECUNDARIO']}")
                st.caption(f"Definiciones: {row['ACORDES']}")

# -----------------------------
# Gráfico Altair
# -----------------------------
df_long = pd.melt(
    df_filtrado,
    id_vars=["MARCA", "PERFUME"],
    value_vars=["PERFIL PRINCIPAL", "PERFIL SECUNDARIO"],
    var_name="TIPO_PERFIL",
    value_name="PERFIL_TOTAL"
).dropna(subset=["PERFIL_TOTAL"])

if not df_long.empty:
    chart = alt.Chart(df_long).mark_circle(size=200).encode(
        x="PERFIL_TOTAL",
        y=alt.Y("PERFUME", sort=None),
        color="PERFIL_TOTAL",
        tooltip=["PERFUME", "PERFIL_TOTAL", "TIPO_PERFIL"]
    ).properties(
        title=f"Perfumes de {marca_sel} agrupados por Perfil y Perfil Secundario",
        height=600
    )
    st.altair_chart(chart, use_container_width=True)

