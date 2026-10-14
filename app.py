import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

st.set_page_config(
    page_title="Farmacias Valle Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

pio.templates.default = "plotly_white"

# ====================================================
# FORZAR TEMA CLARO
# ====================================================

st.markdown("""
<style>

/* Fondo principal */
.stApp{
    background-color:#FFFFFF !important;
}

/* Contenedor principal */
.main{
    background-color:#FFFFFF !important;
}

/* Área central */
section.main > div{
    backgrou*d-color:#FFFFFF !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#F3F4F6 !important;
}

/* Todo el texto */
body,
p,
span,
label,
div,
h1,
h*,
h3,
h4,
h5,
h6*{
*   color:#111827 !important;
}

/* Fecha */
.stDateInput input{
    b*ckground:white !important;
    color:black !important;
}

/* Select */
.stSelectbox div[data-baseweb="select"]{
    background:white !important;
}

/* Multiselect */
.stMultiSelect div[data-baseweb="select"]{
    background:white !important;
}

/* Opciones seleccionadas */
div[data-baseweb="tag"]{
    background:#3B82F6 !important;
    color:white !important;
}

/* KPI */
[data-testid="metric-container"]{
    background:white !important;

    border:1px solid #E5E7EB;

    border-radius:12px;

    padding:20px;

    box-shadow:0 2px 6px rgba(0,0,0,.08);
}

/* KPI centrados */
[data-testid="metric-container"]{
    text-align:center;
}

[data-testid="stMetricLabel"]{
    justify-content:center !important;
}

[data-testid="stMetricValue"]{
    justify-content:center !important;
}

[data-testid="stMetricDelta"]{
    justify-content:center !important;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    background:white !important;
}

</style>
""", unsafe_allow_html=True)



# Ocultar únicamente menú y footer

st.markdown("""
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ====================================================
# CARGA DE DATOS
# ====================================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("Farmacias_Valle_Demanda_1200.csv")
    df["Mes"] = pd.to_datetime(df["Mes"])
    return df

df = cargar_datos()

# ====================================================
# SIDEBAR
# ====================================================

st.sidebar.header("🎯 Filtros")

categorias = st.sidebar.multiselect(
    "Categorías",
    options=sorted(df["Categoria"].unique()),
    default=sorted(df["Categoria"].unique())
)

fecha_inicio = st.sidebar.date_input(
    "Fecha Inicio",
    value=df["Mes"].min()
)

fecha_fin = st.sidebar.date_input(
    "Fecha Fin",
    value=df["Mes"].max()
)

# ====================================================
# FILTRO GENERAL
# ====================================================

df_filtrado = df[
    (df["Categoria"].isin(categorias))
    &
    (df["Mes"] >= pd.to_datetime(fecha_inicio))
    &
    (df["Mes"] <= pd.to_datetime(fecha_fin))
]

# ====================================================
# TITULO NARRATIVO
# ====================================================

st.markdown(
    """
    <h1 style='text-align:center; color:#1f2937; margin-bottom:10px;'>
    💊 Las categorías crónicas y vitaminas impulsan el crecimiento de Farmacias Valle
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h4 style='text-align:center; color:#6b7280; font-weight:400; margin-top:0;'>
    Este tablero permite monitorear la salud comercial del negocio,
    identificar oportunidades de crecimiento y detectar riesgos de inventario.
    </h4>
    """,
    unsafe_allow_html=True
)

# Espacio antes de los KPIs
st.markdown("<br><br><br><br>", unsafe_allow_html=True)



# ====================================================
# KPI ACTUAL VS PERIODO ANTERIOR
# ====================================================

ultimos_12 = df_filtrado.sort_values("Mes")["Mes"].unique()

if len(ultimos_12) >= 24:

    periodo_actual = ultimos_12[-12:]
    periodo_anterior = ultimos_12[-24:-12]

    actual = df_filtrado[
        df_filtrado["Mes"].isin(periodo_actual)
    ]

    anterior = df_filtrado[
        df_filtrado["Mes"].isin(periodo_anterior)
    ]

else:

    actual = df_filtrado
    anterior = df_filtrado

# KPI 1

ingreso_actual = actual["Ingreso_Mensual"].sum()
ingreso_anterior = anterior["Ingreso_Mensual"].sum()

delta_ingreso = (
    (ingreso_actual - ingreso_anterior)
    /
    ingreso_anterior
) * 100

# KPI 2

unidades_actual = actual["Unidades_Vendidas"].sum()
unidades_anterior = anterior["Unidades_Vendidas"].sum()

delta_unidades = (
    (unidades_actual - unidades_anterior)
    /
    unidades_anterior
) * 100

# KPI 3

rotacion_actual = (
    actual["Unidades_Vendidas"].sum()
    /
    actual["Stock_Disponible"].mean()
)

rotacion_anterior = (
    anterior["Unidades_Vendidas"].sum()
    /
    anterior["Stock_Disponible"].mean()
)

delta_rotacion = (
    (rotacion_actual - rotacion_anterior)
    /
    rotacion_anterior
) * 100




# ====================================================
# KPIS
# ====================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "💰 Ingreso Total",
        f"${ingreso_actual:,.0f}",
        f"{delta_ingreso:.1f}%"
    )

with c2:
    st.metric(
        "📦 Unidades Vendidas",
        f"{unidades_actual:,.0f}",
        f"{delta_unidades:.1f}%"
    )

with c3:
    st.metric(
        "🔄 Rotación Inventario",
        f"{rotacion_actual:.2f}",
        f"{delta_rotacion:.1f}%"
    )

# ====================================================
# VISUALIZACION 1
# TENDENCIA
# ====================================================

st.subheader("📈 Evolución de los ingresos")

ventas_mes = (
    df_filtrado
    .groupby("Mes")["Ingreso_Mensual"]
    .sum()
    .reset_index()
)

fig1 = px.line(
    ventas_mes,
    x="Mes",
    y="Ingreso_Mensual",
    markers=True,
    title="Tendencia mensual de ingresos",
    template="plotly_white"
)

fig1.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font_color="black"
)

st.plotly_chart(fig1, use_container_width=True)

# ====================================================
# STORYTELLING
# ====================================================

st.info(
    """
    📌 Se observa una tendencia creciente en ingresos durante los periodos
    de temporada alta, especialmente en productos de consumo recurrente.
    """
)

# ====================================================
# VISUALIZACION 2
# COMPARACION
# ====================================================

categoria_ingresos = (
    df_filtrado
    .groupby("Categoria")["Ingreso_Mensual"]
    .sum()
    .reset_index()
    .sort_values("Ingreso_Mensual", ascending=False)
)

fig2 = px.bar(
    categoria_ingresos,
    x="Categoria",
    y="Ingreso_Mensual",
    color="Categoria",
    title="Comparación de ingresos por categoría"
)

# ====================================================
# VISUALIZACION 3
# DISTRIBUCION
# ====================================================

fig3 = px.box(
    df_filtrado,
    x="Categoria",
    y="Unidades_Vendidas",
    color="Categoria",
    title="Distribución de unidades vendidas"
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.plotly_chart(fig3, use_container_width=True)

# ====================================================
# VISUALIZACION 4
# STOCK VS VENTAS
# ====================================================

st.subheader("📦 Relación entre inventario y demanda")

fig4 = px.scatter(
    df_filtrado,
    x="Stock_Disponible",
    y="Unidades_Vendidas",
    color="Categoria",
    size="Ingreso_Mensual",
    hover_name="Producto_Nombre",
    title="Stock vs Ventas"
)

st.plotly_chart(fig4, use_container_width=True)

st.warning(
    """
    ⚠️ Productos con alto stock y baja venta pueden representar
    sobreinventario y costos innecesarios.
    """
)

# ====================================================
# TOP PRODUCTOS
# ====================================================

st.subheader("🏆 Top 10 productos por ingreso")

top10 = (
    df_filtrado
    .groupby("Producto_Nombre")["Ingreso_Mensual"]
    .sum()
    .reset_index()
    .sort_values("Ingreso_Mensual", ascending=False)
    .head(10)
)

fig5 = px.bar(
    top10,
    x="Ingreso_Mensual",
    y="Producto_Nombre",
    orientation="h",
    color="Ingreso_Mensual",
    title="Productos más rentables"
)

st.plotly_chart(fig5, use_container_width=True)

# ====================================================
# RIESGO DE DESABASTO
# ====================================================

st.subheader("🚨 Productos con riesgo de desabasto")

riesgo = df_filtrado[
    df_filtrado["Stock_Disponible"]
    <
    df_filtrado["Unidades_Vendidas"]
]

if len(riesgo) > 0:

    st.dataframe(
        riesgo[
            [
                "Producto_Nombre",
                "Categoria",
                "Stock_Disponible",
                "Unidades_Vendidas"
            ]
        ]
        .sort_values(
            "Stock_Disponible"
        )
        .head(15),
        use_container_width=True
    )

else:

    st.success(
        "No se detectaron productos con riesgo de desabasto."
    )

# ====================================================
# HALLAZGOS
# ====================================================

st.subheader("📋 Hallazgos Ejecutivos")

producto_top = (
    df_filtrado
    .groupby("Producto_Nombre")["Ingreso_Mensual"]
    .sum()
    .idxmax()
)

categoria_top = (
    df_filtrado
    .groupby("Categoria")["Ingreso_Mensual"]
    .sum()
    .idxmax()
)

st.success(
    f"✅ El producto más rentable es: {producto_top}"
)

st.success(
    f"✅ La categoría líder es: {categoria_top}"
)

st.info(
    """
    📌 Recomendación: incrementar compras de categorías líderes,
    revisar productos con baja rotación y fortalecer promociones
    durante temporadas altas.
    """
)