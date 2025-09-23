import streamlit as st
import pandas as pd
import altair as alt
import os
import io
from altair_saver import save  # 👈 asegurate de tenerlo: pip install altair_saver

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Catálogo de Perfumes",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 Catálogo de Perfumes 🌸")

# -----------------------------
# Cargar Excel
# -----------------------------
df = pd.read_excel("Catalogo/perfumes.xlsx", sheet_name="Hoja1")
if "IMAGEN" not in df.columns:
    df["IMAGEN"] = None

# -----------------------------
# Selección de marca
# -----------------------------
marcas = sorted(df["MARCA"].astype(str).unique())
marca_sel = st.selectbox("Ingrese la marca:", marcas)

# -----------------------------
# Filtrar DataFrame
# -----------------------------
df_filtrado = df[df["MARCA"] == marca_sel]

# -----------------------------
# Buscador
# -----------------------------
busqueda = st.text_input("🔍 Buscar perfume dentro de la marca:")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado["PERFUME"].str.contains(busqueda, case=False, na=False)]

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
                st.image("https://via.placeholder.com/200", caption="Sin imagen")

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

    # -----------------------------
    # Botones de descarga del gráfico
    # -----------------------------
    buf_png = io.BytesIO()
    save(chart, buf_png, format="png")
    buf_png.seek(0)

    buf_svg = io.BytesIO()
    save(chart, buf_svg, format="svg")
    buf_svg.seek(0)

    st.download_button(
        "📊 Descargar gráfico (PNG)",
        data=buf_png,
        file_name=f"grafico_{marca_sel}.png",
        mime="image/png"
    )

    st.download_button(
        "📊 Descargar gráfico (SVG)",
        data=buf_svg,
        file_name=f"grafico_{marca_sel}.svg",
        mime="image/svg+xml"
    )
