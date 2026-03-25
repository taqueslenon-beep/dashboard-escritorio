import streamlit as st
import pandas as pd
from supabase import create_client

# ── Configuração ──────────────────────────────────────────────
SUPABASE_URL = "https://tjpasfrzsogdhxnerxhs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqcGFzZnJ6c29nZGh4bmVyeGhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MDIyMTMsImV4cCI6MjA4OTk3ODIxM30.6Mzblk0TNdUjQGQGAsjrRpgfSp4gUB_jSTQxyJpBSqc"

STATUS_OPTIONS = [
    "EM ANDAMENTO", "CONCLUÍDO", "AGUARDANDO CLIENTE",
    "AGUARDANDO TRIBUNAL", "EM RECURSO", "SUSPENSO",
    "ARQUIVADO", "EM MONITORAMENTO", "SUBSTABELECIDO", "SEM STATUS"
]

st.set_page_config(page_title="Escritório", page_icon="⚖️", layout="wide")

# ── CSS Minimalista ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }
    .block-container { padding: 2rem 2.5rem; max-width: 100%; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Métricas */
    [data-testid="stMetric"] {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #2563eb;
    }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] {
        background: transparent; color: #64748b; border-radius: 8px 8px 0 0;
        padding: 10px 20px; font-weight: 500; font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] { background: #2563eb !important; color: white !important; }

    /* Dataframe */
    .stDataFrame { border-radius: 8px; border: 1px solid #e2e8f0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #fafbfc; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

    /* Selectbox */
    .stSelectbox > div > div { font-size: 0.85rem; }

    /* Divider */
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }

    /* Hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .status-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px;
    }
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
    df["cliente"] = df["cliente"].fillna("—")
    return df

def salvar_status(caso_id, novo_status):
    supabase = get_supabase()
    value = None if novo_status == "SEM STATUS" else novo_status
    supabase.table("casos").update({"status": value}).eq("id", caso_id).execute()

# ── Carregar dados ────────────────────────────────────────────
if "dados" not in st.session_state or st.sidebar.button("↻ Atualizar dados", use_container_width=True):
    st.session_state.dados = carregar_dados()

df = st.session_state.dados

# ── Sidebar: Filtros ──────────────────────────────────────────
st.sidebar.markdown("#### Filtros")

busca = st.sidebar.text_input("Buscar", placeholder="Nome ou cliente...")

nucleo = st.sidebar.multiselect(
    "Núcleo", sorted(df["nucleo"].dropna().unique()),
    default=sorted(df["nucleo"].dropna().unique())
)
responsavel = st.sidebar.multiselect(
    "Responsável", sorted(df["responsavel"].dropna().unique()),
    default=sorted(df["responsavel"].dropna().unique())
)
prioridade = st.sidebar.multiselect(
    "Prioridade", sorted(df["prioridade"].dropna().unique()),
    default=sorted(df["prioridade"].dropna().unique())
)
status_filtro = st.sidebar.multiselect(
    "Status", sorted(df["status"].unique()),
    default=sorted(df["status"].unique())
)

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

# ── Header ────────────────────────────────────────────────────
st.markdown(f"## ⚖️ Escritório")
st.caption(f"{len(dados)} de {len(df)} casos")

# ── Métricas ──────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", len(dados))
c2.metric("P1", len(dados[dados["prioridade"] == "P1"]))
c3.metric("Ambiental", len(dados[dados["nucleo"] == "AMBIENTAL"]))
c4.metric("Lenon", len(dados[dados["responsavel"] == "LENON"]))
c5.metric("Gilberto", len(dados[dados["responsavel"] == "GILBERTO"]))

st.markdown("---")

# ── Abas ──────────────────────────────────────────────────────
tab_status, tab_visao, tab_tabela = st.tabs(["✏️ Status", "📊 Visão Geral", "📋 Todos os Casos"])

# ── ABA: STATUS ───────────────────────────────────────────────
with tab_status:
    st.markdown("#### Gerenciar Status")
    st.caption("Altere o status de qualquer caso — a mudança é salva automaticamente no banco.")

    # Filtro rápido de prioridade na aba status
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        prio_filter = st.selectbox("Filtrar prioridade", ["Todas", "P1", "P2", "P3", "P4"])

    dados_status = dados if prio_filter == "Todas" else dados[dados["prioridade"] == prio_filter]

    for _, caso in dados_status.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1.5])
            with col1:
                st.markdown(f"**{caso['nome_do_caso']}**")
                st.caption(f"{caso['nucleo']}  ·  {caso['responsavel']}  ·  {caso['prioridade']}")
            with col2:
                st.caption(f"Cliente: {caso['cliente']}")
            with col3:
                novo = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(caso["status"]) if caso["status"] in STATUS_OPTIONS else len(STATUS_OPTIONS) - 1,
                    key=f"status_{caso['id']}",
                    label_visibility="collapsed"
                )
                if novo != caso["status"]:
                    salvar_status(caso["id"], novo)
                    st.session_state.dados.loc[st.session_state.dados["id"] == caso["id"], "status"] = novo
                    st.toast(f"✅ Status atualizado: {novo}")
                    st.rerun()
            st.divider()

# ── ABA: VISÃO GERAL ─────────────────────────────────────────
with tab_visao:
    import plotly.express as px

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        nucleo_ct = dados["nucleo"].value_counts().reset_index()
        nucleo_ct.columns = ["Núcleo", "Qtd"]
        fig = px.pie(nucleo_ct, values="Qtd", names="Núcleo", hole=0.45,
                     color_discrete_sequence=["#2563eb", "#0f3460", "#7c3aed"])
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", font=dict(size=12))
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        prio_ct = dados["prioridade"].value_counts().sort_index().reset_index()
        prio_ct.columns = ["Prioridade", "Qtd"]
        cores = {"P1": "#ef4444", "P2": "#f59e0b", "P3": "#10b981", "P4": "#94a3b8"}
        fig = px.bar(prio_ct, x="Prioridade", y="Qtd", color="Prioridade",
                     color_discrete_map=cores, text="Qtd")
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=12))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    col_g3, col_g4 = st.columns(2)

    with col_g3:
        status_ct = dados["status"].value_counts().reset_index()
        status_ct.columns = ["Status", "Qtd"]
        fig = px.pie(status_ct, values="Qtd", names="Status", hole=0.45,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", font=dict(size=11))
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

    with col_g4:
        cross = dados.groupby(["responsavel", "nucleo"]).size().reset_index(name="Qtd")
        fig = px.bar(cross, x="responsavel", y="Qtd", color="nucleo", barmode="stack",
                     color_discrete_sequence=["#2563eb", "#0f3460", "#7c3aed"],
                     labels={"responsavel": "Responsável", "nucleo": "Núcleo"})
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=320,
                          paper_bgcolor="rgba(0,0,0,0)", font=dict(size=12),
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

# ── ABA: TABELA ───────────────────────────────────────────────
with tab_tabela:
    st.dataframe(
        dados[["id", "cliente", "nome_do_caso", "nucleo", "responsavel", "prioridade", "status", "grupo"]].rename(
            columns={"id": "ID", "cliente": "Cliente", "nome_do_caso": "Caso",
                     "nucleo": "Núcleo", "responsavel": "Resp.", "prioridade": "Prio",
                     "status": "Status", "grupo": "Grupo"}
        ),
        use_container_width=True,
        height=600,
        hide_index=True
    )

    csv = dados.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Exportar CSV", csv, "casos.csv", "text/csv")
