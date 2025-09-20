import streamlit as st
import pandas as pd
import altair as alt
import json

# Cargar Excel
df = pd.read_excel("perfumes.xlsx", sheet_name="Hoja1")
if "IMAGEN" not in df.columns:
    df["IMAGEN"] = None

# Selección de marca
marcas = sorted(df["MARCA"].astype(str).unique())
marca_sel = st.selectbox("Ingrese la marca:", marcas)
# Filtrar DataFrame
df_filtrado = df[df["MARCA"] == marca_sel]

# Buscador
busqueda = st.text_input("🔍 Buscar perfume dentro de la marca:")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado["PERFUME"].str.contains(busqueda, case=False, na=False)]

# Toggle
mostrar_todos = st.toggle("👀 Mostrar todos los perfumes", value=False)

# Layout en grilla
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
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin:10px;
                            box-shadow: 2px 2px 8px rgba(0,0,0,0.1); text-align:center;">
                    <img src="{row['IMAGEN'] if pd.notna(row['IMAGEN']) else 'https://via.placeholder.com/200'}"
                         style="max-width:100%; height:auto; border-radius:10px; margin-bottom:10px;">
                    <h3 style="margin:5px 0;">{row['PERFUME']}</h3>
                    <p><b>Perfil:</b> {row['PERFIL']}</p>
                    <p><b>Secundario:</b> {row['PERFIL SECUNDARIO']}</p>
                    <p><b>Definiciones:</b> {row['DEFINICIONES']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Gráfico
df_long = pd.melt(
    df_filtrado,
    id_vars=["MARCA", "PERFUME"],
    value_vars=["PERFIL", "PERFIL SECUNDARIO"],
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

# Botón descarga
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    "💾 Descargar catálogo filtrado (CSV)",
    csv,
    f"catalogo_{marca_sel}.csv",
    "text/csv",
    key="download-csv"
)

