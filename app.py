import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from streamlit_option_menu import option_menu

# ── Configuracao ──────────────────────────────────────────────
SUPABASE_URL = "https://tjpasfrzsogdhxnerxhs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqcGFzZnJ6c29nZGh4bmVyeGhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MDIyMTMsImV4cCI6MjA4OTk3ODIxM30.6Mzblk0TNdUjQGQGAsjrRpgfSp4gUB_jSTQxyJpBSqc"

VERDE = "#223631"
VERDE_CLARO = "#2d4a3e"
OFF_WHITE = "#f5f3ef"
CREME = "#eae6df"

STATUS_OPTIONS = [
    "EM ANDAMENTO", "CONCLUIDO", "SUBSTABELECIDO", "EM MONITORAMENTO"
]

# ── Cores dos badges ─────────────────────────────────────────
CORES_PRIORIDADE = {
    "P1": {"bg": "#fde8e8", "cor": "#c0392b"},
    "P2": {"bg": "#fef9e7", "cor": "#b7950b"},
    "P3": {"bg": "#e8f0fe", "cor": "#2b6cb0"},
    "P4": {"bg": "#f0f0f0", "cor": "#666666"},
}
CORES_STATUS = {
    "EM ANDAMENTO": {"bg": "#fef9e7", "cor": "#b7950b"},
    "CONCLUIDO": {"bg": "#e0edda", "cor": "#2d5a1e"},
    "SUBSTABELECIDO": {"bg": "#e8f5e9", "cor": "#4caf50"},
    "EM MONITORAMENTO": {"bg": "#fff3e0", "cor": "#e65100"},
}
CORES_RESPONSAVEL = {
    "LENON": {"bg": "#f0e0d0", "cor": "#6d4c2e"},
    "GILBERTO": {"bg": "#fef3c7", "cor": "#b45309"},
}
CORES_NUCLEO = {
    "AMBIENTAL": {"bg": "#223631", "cor": "#ffffff"},
    "COBRAN\u00c7AS": {"bg": "#1a3a5c", "cor": "#ffffff"},
    "GENERALISTA": {"bg": "#5b9bd5", "cor": "#ffffff"},
}

st.set_page_config(page_title="Escritorio", page_icon="\u2696\ufe0f", layout="wide")

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}

    /* Fundo off-white geral */
    .stApp {{ background-color: {OFF_WHITE}; }}
    .block-container {{ padding: 2.5rem 2.5rem 1.5rem 2.5rem; max-width: 100%; }}
    header[data-testid="stHeader"] {{ background: {OFF_WHITE}; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {VERDE};
        border-right: none;
    }}
    [data-testid="stSidebar"] .block-container {{ padding-top: 1rem; }}
    [data-testid="stSidebar"] * {{ color: white; }}
    [data-testid="stSidebar"] label {{ color: rgba(255,255,255,0.7) !important; }}
    [data-testid="stSidebar"] .stMarkdown p {{ color: rgba(255,255,255,0.9); }}
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {{ color: white; }}

    /* Sidebar option-menu */
    [data-testid="stSidebar"] iframe {{
        background-color: transparent !important;
    }}
    [data-testid="stSidebar"] .nav-link {{
        color: rgba(255,255,255,0.75) !important;
        background-color: transparent !important;
    }}
    [data-testid="stSidebar"] .nav-link.active,
    [data-testid="stSidebar"] .nav-link-selected {{
        color: white !important;
        background-color: rgba(255,255,255,0.15) !important;
    }}
    [data-testid="stSidebar"] .nav-link:hover {{
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
    }}

    /* Sidebar inputs */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stMultiSelect > div > div {{
        background: {VERDE_CLARO};
        border: 1px solid rgba(255,255,255,0.15);
        color: white;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,255,255,0.12);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.4);
    }}

    /* Metricas */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        border-left: 4px solid {VERDE};
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    [data-testid="stMetricValue"] {{ font-size: 1.8rem; font-weight: 700; color: {VERDE}; }}
    [data-testid="stMetricLabel"] {{ font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* Dataframe */
    .stDataFrame {{ border-radius: 10px; border: 1px solid #e0ddd6; }}

    /* Selectbox */
    .stSelectbox > div > div {{ font-size: 0.85rem; }}

    /* ── Filtros — area principal ────────────────────────── */
    /* Multiselect — fundo transparente */
    [data-testid="stAppViewContainer"] .stMultiSelect > div > div,
    [data-testid="stAppViewContainer"] .stMultiSelect [data-baseweb="select"] > div,
    [data-testid="stAppViewContainer"] [data-baseweb="select"],
    [data-testid="stAppViewContainer"] [data-baseweb="input"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: 1px solid #d4d0c8 !important;
        border-radius: 6px !important;
        color: #333 !important;
    }}
    [data-testid="stAppViewContainer"] .stMultiSelect label {{
        color: #777 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: none !important;
        margin-bottom: 2px !important;
    }}
    /* Tags — estilo base compacto */
    [data-testid="stAppViewContainer"] span[data-baseweb="tag"] {{
        border-radius: 3px !important;
        font-size: 0.62rem !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 1px 5px !important;
        height: 18px !important;
        line-height: 18px !important;
    }}
    /* Inputs menores */
    [data-testid="stAppViewContainer"] .stMultiSelect > div > div,
    [data-testid="stAppViewContainer"] .stMultiSelect [data-baseweb="select"] > div {{
        min-height: 28px !important;
        padding: 1px 4px !important;
        font-size: 0.72rem !important;
    }}
    [data-testid="stAppViewContainer"] .stTextInput input {{
        height: 28px !important;
        font-size: 0.72rem !important;
        padding: 2px 8px !important;
    }}
    [data-testid="stAppViewContainer"] .stMultiSelect label,
    [data-testid="stAppViewContainer"] .stTextInput label {{
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: #555 !important;
        margin-bottom: 2px !important;
    }}

    /* ── Tags coloridas por conteudo (Nucleo) ────────── */
    span[data-baseweb="tag"][aria-label*="AMBIENTAL"] {{
        background: #223631 !important;
    }}
    span[data-baseweb="tag"][aria-label*="AMBIENTAL"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="AMBIENTAL"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="COBRAN"] {{
        background: #1a3a5c !important;
    }}
    span[data-baseweb="tag"][aria-label*="COBRAN"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="COBRAN"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="GENERALISTA"] {{
        background: #5b9bd5 !important;
    }}
    span[data-baseweb="tag"][aria-label*="GENERALISTA"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="GENERALISTA"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}

    /* ── Tags coloridas (Responsavel) ────────────────── */
    span[data-baseweb="tag"][aria-label*="LENON"] {{
        background: #6d4c2e !important;
    }}
    span[data-baseweb="tag"][aria-label*="LENON"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="LENON"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="GILBERTO"] {{
        background: #d4a017 !important;
    }}
    span[data-baseweb="tag"][aria-label*="GILBERTO"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="GILBERTO"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}

    /* ── Tags coloridas (Prioridade) ─────────────────── */
    span[data-baseweb="tag"][aria-label*="P1"] {{
        background: #c0392b !important;
    }}
    span[data-baseweb="tag"][aria-label*="P1"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="P1"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="P2"] {{
        background: #b7950b !important;
    }}
    span[data-baseweb="tag"][aria-label*="P2"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="P2"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="P3"] {{
        background: #2b6cb0 !important;
    }}
    span[data-baseweb="tag"][aria-label*="P3"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="P3"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="P4"] {{
        background: #888888 !important;
    }}
    span[data-baseweb="tag"][aria-label*="P4"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="P4"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}

    /* ── Tags coloridas (Status) ─────────────────────── */
    span[data-baseweb="tag"][aria-label*="SEM STATUS"] {{
        background: #999999 !important;
    }}
    span[data-baseweb="tag"][aria-label*="SEM STATUS"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="SEM STATUS"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM ANDAMENTO"] {{
        background: #b7950b !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM ANDAMENTO"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM ANDAMENTO"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="CONCLUIDO"] {{
        background: #2d5a1e !important;
    }}
    span[data-baseweb="tag"][aria-label*="CONCLUIDO"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="CONCLUIDO"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="SUBSTABELECIDO"] {{
        background: #4caf50 !important;
    }}
    span[data-baseweb="tag"][aria-label*="SUBSTABELECIDO"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="SUBSTABELECIDO"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM MONITOR"] {{
        background: #e65100 !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM MONITOR"] span {{
        color: white !important;
    }}
    span[data-baseweb="tag"][aria-label*="EM MONITOR"] svg {{
        fill: rgba(255,255,255,0.8) !important;
    }}

    /* Dropdown popover e icones */
    [data-testid="stAppViewContainer"] .stMultiSelect svg {{
        fill: #999 !important;
    }}
    [data-testid="stAppViewContainer"] [data-baseweb="popover"],
    [data-testid="stAppViewContainer"] [data-baseweb="popover"] ul,
    [data-testid="stAppViewContainer"] [data-baseweb="menu"] {{
        background: white !important;
        background-color: white !important;
    }}

    /* Text input — compacto */
    [data-testid="stAppViewContainer"] .stTextInput input {{
        background: white !important;
        border: 1px solid #d4d0c8 !important;
        border-radius: 6px !important;
        color: #333 !important;
        height: 34px !important;
        padding: 4px 10px !important;
    }}
    [data-testid="stAppViewContainer"] .stTextInput label {{
        color: #777 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: none !important;
        margin-bottom: 2px !important;
    }}
    [data-testid="stAppViewContainer"] .stTextInput input::placeholder {{
        color: #bbb !important;
        font-size: 0.8rem !important;
    }}

    /* Botao limpar filtros */
    [data-testid="stAppViewContainer"] .stButton > button {{
        background: white !important;
        color: #999 !important;
        border: 1px solid #d4d0c8 !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        height: 34px !important;
        padding: 0 12px !important;
    }}
    [data-testid="stAppViewContainer"] .stButton > button:hover {{
        background: #f5f3ef !important;
        color: #666 !important;
        border-color: #bbb !important;
    }}

    /* Divider */
    hr {{ border: none; border-top: 1px solid #ddd8cf; margin: 1.2rem 0; }}

    /* Hide streamlit branding */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* Status cards */
    .status-card {{
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border: 1px solid #e8e4dc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    /* Botoes de status coloridos */
    button[kind="secondary"]:has(p) {{
        font-size: 0.68rem !important;
        padding: 4px 6px !important;
        height: auto !important;
        min-height: 30px !important;
    }}
    /* Em andamento - amarelo */
    button[key*="and_"] p, div[data-testid="stButton"] button p {{
        font-size: 0.68rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Supabase ──────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_dados():
    supabase = get_supabase()
    response = supabase.table("casos").select("*").order("prioridade").order("id").execute()
    df = pd.DataFrame(response.data)
    df["status"] = df["status"].fillna("SEM STATUS")
    df["cliente"] = df["cliente"].fillna("\u2014")
    return df

def salvar_status(caso_id, novo_status):
    supabase = get_supabase()
    value = None if novo_status == "SEM STATUS" else novo_status
    supabase.table("casos").update({"status": value}).eq("id", caso_id).execute()

# ── Modal de edicao de status ──────────────────────────────────
@st.dialog("Editar Status")
def modal_editar_status(caso_id, nome_caso, status_atual):
    st.markdown(f"**{nome_caso}**")
    estilo = CORES_STATUS.get(status_atual, {"bg": "#f0f0f0", "cor": "#666"})
    st.markdown(
        f'<span style="background:{estilo["bg"]};color:{estilo["cor"]};'
        f'padding:5px 14px;border-radius:12px;font-weight:600;font-size:0.85rem;">'
        f'{status_atual}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    idx = STATUS_OPTIONS.index(status_atual) if status_atual in STATUS_OPTIONS else 0
    novo = st.selectbox("Novo status", STATUS_OPTIONS, index=idx)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar", type="primary", use_container_width=True):
            salvar_status(caso_id, novo)
            st.session_state.dados.loc[st.session_state.dados["id"] == caso_id, "status"] = novo
            st.toast(f"Status atualizado: {novo}")
            st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    pagina = option_menu(
        None,
        ["Dashboard", "Casos"],
        icons=["bar-chart-fill", "folder2-open"],
        default_index=0,
        styles={
            "container": {"padding": "8px 0 0 0", "background-color": VERDE},
            "menu-title": {"display": "none"},
            "icon": {"color": "#a8c4b8", "font-size": "18px"},
            "nav-link": {
                "font-size": "15px", "text-align": "left", "margin": "2px 0",
                "color": "rgba(255,255,255,0.75)", "border-radius": "8px",
                "padding": "10px 14px", "background-color": "transparent",
            },
            "nav-link-selected": {
                "background-color": "rgba(255,255,255,0.15)",
                "color": "white", "font-weight": "600",
            },
        }
    )

    st.markdown("---")

    if st.button("\u21bb Atualizar dados", use_container_width=True):
        st.session_state.pop("dados", None)

# ── Carregar dados ────────────────────────────────────────────
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

df = st.session_state.dados

# ══════════════════════════════════════════════════════════════
# PAGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════
if pagina == "Dashboard":
    st.markdown("## Dashboard")
    st.caption(f"{len(df)} casos no total")

    # ── Metricas ──────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", len(df))
    c2.metric("P1", len(df[df["prioridade"] == "P1"]))
    c3.metric("Ambiental", len(df[df["nucleo"] == "AMBIENTAL"]))
    c4.metric("Lenon", len(df[df["responsavel"] == "LENON"]))
    c5.metric("Gilberto", len(df[df["responsavel"] == "GILBERTO"]))

    st.markdown("---")

    # ── Graficos ──────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        nucleo_ct = df["nucleo"].value_counts().reset_index()
        nucleo_ct.columns = ["Nucleo", "Qtd"]
        fig = px.pie(nucleo_ct, values="Qtd", names="Nucleo", hole=0.45,
                     color_discrete_sequence=[VERDE, "#3d6b5a", "#5a9a80", "#8bc4a9"])
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(size=12, color="#333"))
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        prio_ct = df["prioridade"].value_counts().sort_index().reset_index()
        prio_ct.columns = ["Prioridade", "Qtd"]
        cores = {"P1": "#c0392b", "P2": "#e67e22", "P3": "#27ae60", "P4": "#95a5a6"}
        fig = px.bar(prio_ct, x="Prioridade", y="Qtd", color="Prioridade",
                     color_discrete_map=cores, text="Qtd")
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, font=dict(size=12, color="#333"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    col_g3, col_g4 = st.columns(2)

    with col_g3:
        status_ct = df["status"].value_counts().reset_index()
        status_ct.columns = ["Status", "Qtd"]
        fig = px.pie(status_ct, values="Qtd", names="Status", hole=0.45,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(size=11, color="#333"))
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

    with col_g4:
        cross = df.groupby(["responsavel", "nucleo"]).size().reset_index(name="Qtd")
        fig = px.bar(cross, x="responsavel", y="Qtd", color="nucleo", barmode="stack",
                     color_discrete_sequence=[VERDE, "#3d6b5a", "#5a9a80"],
                     labels={"responsavel": "Responsavel", "nucleo": "Nucleo"})
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(size=12, color="#333"),
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGINA: CASOS
# ══════════════════════════════════════════════════════════════
elif pagina == "Casos":
    # ── Filtros (linha unica compacta) ──────────────────────
    f1, f2, f3, f4, f5, f6 = st.columns([2, 1.5, 1.5, 1, 1.5, 0.8])
    with f1:
        busca = st.text_input("Buscar", placeholder="Nome ou cliente...")
    with f2:
        nucleo = st.multiselect(
            "N\u00facleo", sorted(df["nucleo"].dropna().unique()),
            default=sorted(df["nucleo"].dropna().unique())
        )
    with f3:
        responsavel = st.multiselect(
            "Respons\u00e1vel", sorted(df["responsavel"].dropna().unique()),
            default=sorted(df["responsavel"].dropna().unique())
        )
    with f4:
        prioridade = st.multiselect(
            "Prioridade", sorted(df["prioridade"].dropna().unique()),
            default=sorted(df["prioridade"].dropna().unique())
        )
    with f5:
        status_filtro = st.multiselect(
            "Status", sorted(df["status"].unique()),
            default=["EM ANDAMENTO", "EM MONITORAMENTO"]
        )
    with f6:
        st.markdown('<p style="font-size:0.75rem;color:transparent;margin-bottom:2px;">_</p>', unsafe_allow_html=True)
        if st.button("Limpar", use_container_width=True):
            st.rerun()

    # Aplicar filtros
    mask = (
        df["nucleo"].isin(nucleo) &
        df["responsavel"].isin(responsavel) &
        df["prioridade"].isin(prioridade) &
        df["status"].isin(status_filtro)
    )
    if busca:
        busca_lower = busca.lower()
        mask = mask & (
            df["nome_do_caso"].str.lower().str.contains(busca_lower, na=False) |
            df["cliente"].str.lower().str.contains(busca_lower, na=False)
        )
    dados = df[mask]

    st.caption(f"{len(dados)} de {len(df)} casos filtrados")

    # ── Toggle coluna cliente ──────────────────────────────
    mostrar_cliente = st.checkbox("Mostrar coluna Cliente", value=False)

    # ── Paginacao ──────────────────────────────────────────
    LINHAS_POR_PAGINA = 25
    total_paginas = max(1, -(-len(dados) // LINHAS_POR_PAGINA))
    if "pagina_tabela" not in st.session_state:
        st.session_state.pagina_tabela = 0
    if st.session_state.pagina_tabela >= total_paginas:
        st.session_state.pagina_tabela = 0
    pag = st.session_state.pagina_tabela
    pagina_dados = dados.iloc[pag * LINHAS_POR_PAGINA : (pag + 1) * LINHAS_POR_PAGINA]

    # ── Funcoes de estilo (pandas Styler) ──────────────────
    def estilo_celula(val, mapa):
        c = mapa.get(str(val), {"bg": "#f0f0f0", "cor": "#666"})
        return f'background-color: {c["bg"]}; color: {c["cor"]}; font-weight: 600; text-align: center;'

    # ── Montar DataFrame da pagina (sem coluna status) ─────
    colunas = ["nome_do_caso", "nucleo", "responsavel", "prioridade"]
    renomear = {
        "nome_do_caso": "CASO", "nucleo": "NÚCLEO",
        "responsavel": "RESPONSÁVEL", "prioridade": "PRIORIDADE",
    }
    if mostrar_cliente:
        colunas = ["cliente"] + colunas
        renomear["cliente"] = "CLIENTE"

    df_exibir = pagina_dados[colunas].rename(columns=renomear).reset_index(drop=True)

    # ── Estilos da tabela ──────────────────────────────────
    styler = (
        df_exibir.style
        .map(lambda v: "font-weight: 700; color: #1a1a1a;", subset=["CASO"])
        .map(lambda v: estilo_celula(v, CORES_NUCLEO), subset=["NÚCLEO"])
        .map(lambda v: estilo_celula(v, CORES_RESPONSAVEL), subset=["RESPONSÁVEL"])
        .map(lambda v: estilo_celula(v, CORES_PRIORIDADE), subset=["PRIORIDADE"])
        .set_table_styles([
            {"selector": "table", "props": [
                ("width", "100%"), ("border-collapse", "collapse"),
                ("font-family", "'Inter', sans-serif"), ("font-size", "0.84rem"),
            ]},
            {"selector": "thead th", "props": [
                ("background-color", VERDE), ("color", "white"),
                ("font-weight", "600"), ("font-size", "0.73rem"),
                ("text-transform", "uppercase"), ("letter-spacing", "0.5px"),
                ("padding", "11px 14px"), ("text-align", "left"),
                ("border-bottom", "none"), ("white-space", "nowrap"),
            ]},
            {"selector": "thead th:first-child", "props": [("border-radius", "10px 0 0 0")]},
            {"selector": "thead th:last-child",  "props": [("border-radius", "0 10px 0 0")]},
            {"selector": "tbody td", "props": [
                ("padding", "9px 14px"), ("border-bottom", "1px solid #eae6df"),
                ("vertical-align", "middle"),
            ]},
            {"selector": "tbody tr:hover td", "props": [("background-color", "#faf8f5 !important")]},
        ])
        .hide(axis="index")
    )
    if mostrar_cliente:
        styler = styler.map(lambda v: "color: #555; font-size: 0.82em;", subset=["CLIENTE"])

    # ── Layout: tabela (esq) + coluna status/botoes (dir) ──
    col_tab, col_status = st.columns([0.84, 0.16])

    with col_tab:
        html_tabela = styler.to_html()
        st.markdown(
            f'<div style="overflow-x:auto;border:1px solid #e0ddd6;border-radius:10px 0 0 10px;">'
            f'{html_tabela}</div>',
            unsafe_allow_html=True,
        )

    with col_status:
        # Cabecalho da coluna Status (alinhado com o thead da tabela)
        st.markdown(
            f'<div style="background:{VERDE};color:white;font-weight:600;font-size:0.73rem;'
            f'text-transform:uppercase;letter-spacing:0.5px;padding:11px 10px;'
            f'border-radius:0 10px 0 0;white-space:nowrap;border-bottom:none;">STATUS</div>',
            unsafe_allow_html=True,
        )
        # Botao por linha
        for _, row in pagina_dados.iterrows():
            caso_id   = int(row["id"])
            status    = row["status"]
            cor       = CORES_STATUS.get(status, {"bg": "#f0f0f0", "cor": "#666"})
            # CSS escopado por caso_id para colorir o botao
            st.markdown(f"""
            <style>
            div[data-testid="stButton"].btn-status-{caso_id} > button {{
                background-color: {cor['bg']} !important;
                color: {cor['cor']} !important;
                border: none !important;
                font-weight: 600 !important;
                font-size: 0.72rem !important;
                border-radius: 10px !important;
                padding: 4px 6px !important;
                height: 38px !important;
                width: 100% !important;
                margin: 1px 0 !important;
            }}
            </style>
            <div class="btn-status-{caso_id}" data-testid="stButton">
            """, unsafe_allow_html=True)
            if st.button(status, key=f"btn_{caso_id}", use_container_width=True):
                modal_editar_status(caso_id, row["nome_do_caso"], status)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Navegacao de paginas ───────────────────────────────
    if total_paginas > 1:
        nav1, nav2, nav3 = st.columns([1, 2, 1])
        with nav1:
            if st.button("‹ Anterior", disabled=(pag == 0), use_container_width=True):
                st.session_state.pagina_tabela -= 1
                st.rerun()
        with nav2:
            st.markdown(
                f'<p style="text-align:center;color:#777;font-size:0.83rem;padding-top:6px;">'
                f'Página {pag + 1} de {total_paginas} — {len(dados)} casos</p>',
                unsafe_allow_html=True,
            )
        with nav3:
            if st.button("Próximo ›", disabled=(pag >= total_paginas - 1), use_container_width=True):
                st.session_state.pagina_tabela += 1
                st.rerun()

    # ── Exportar CSV ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    csv = dados.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Exportar CSV", csv, "casos.csv", "text/csv")
