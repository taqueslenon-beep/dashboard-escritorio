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
    "LENON": {"bg": "#e0e0e0", "cor": "#333333"},
    "GILBERTO": {"bg": "#f0f0f0", "cor": "#888888"},
}

st.set_page_config(page_title="Escritorio", page_icon="\u2696\ufe0f", layout="wide")

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}

    /* Fundo off-white geral */
    .stApp {{ background-color: {OFF_WHITE}; }}
    .block-container {{ padding: 1.5rem 2.5rem; max-width: 100%; }}
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

    /* Sidebar option-menu — forcar fundo transparente */
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
    st.markdown("## Casos")

    # ── Filtros (dentro da pagina Casos) ─────────────────────
    with st.expander("Filtros", expanded=False):
        col_busca, col_nucleo, col_resp, col_prio, col_status = st.columns(5)

        with col_busca:
            busca = st.text_input("Buscar", placeholder="Nome ou cliente...")
        with col_nucleo:
            nucleo = st.multiselect(
                "Nucleo", sorted(df["nucleo"].dropna().unique()),
                default=sorted(df["nucleo"].dropna().unique())
            )
        with col_resp:
            responsavel = st.multiselect(
                "Responsavel", sorted(df["responsavel"].dropna().unique()),
                default=sorted(df["responsavel"].dropna().unique())
            )
        with col_prio:
            prioridade = st.multiselect(
                "Prioridade", sorted(df["prioridade"].dropna().unique()),
                default=sorted(df["prioridade"].dropna().unique())
            )
        with col_status:
            status_filtro = st.multiselect(
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

    st.caption(f"{len(dados)} de {len(df)} casos filtrados")

    # ── Sub-abas: Tabela e Status ─────────────────────────────
    tab_tabela, tab_status = st.tabs(["Tabela", "Editar Status"])

    with tab_tabela:
        # ── Funcao para gerar badge HTML ─────────────────────
        def badge_html(texto, cores_mapa):
            estilo = cores_mapa.get(texto, {"bg": "#f0f0f0", "cor": "#666"})
            return (
                f'<span style="background:{estilo["bg"]};color:{estilo["cor"]};'
                f'padding:4px 10px;border-radius:12px;font-size:0.78rem;'
                f'font-weight:600;white-space:nowrap;">{texto}</span>'
            )

        # ── Montar tabela HTML ───────────────────────────────
        linhas_html = ""
        for _, row in dados.iterrows():
            linhas_html += f"""<tr>
                <td>{row['cliente']}</td>
                <td style="font-weight:700;">{row['nome_do_caso']}</td>
                <td>{row['nucleo']}</td>
                <td>{badge_html(row['responsavel'], CORES_RESPONSAVEL)}</td>
                <td>{badge_html(row['prioridade'], CORES_PRIORIDADE)}</td>
                <td>{badge_html(row['status'], CORES_STATUS)}</td>
            </tr>"""

        tabela_html = f"""
        <div style="max-height:600px;overflow-y:auto;border:1px solid #e0ddd6;border-radius:10px;">
        <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif;font-size:0.85rem;">
            <thead>
                <tr style="background:{CREME};position:sticky;top:0;z-index:1;">
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Cliente</th>
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Caso</th>
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Nucleo</th>
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Responsavel</th>
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Prioridade</th>
                    <th style="padding:12px 14px;text-align:left;border-bottom:2px solid #ddd8cf;color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">Status</th>
                </tr>
            </thead>
            <tbody>
                {linhas_html}
            </tbody>
        </table>
        </div>
        """

        # CSS para linhas da tabela
        st.markdown("""
        <style>
            table tbody tr { border-bottom: 1px solid #eae6df; }
            table tbody tr:hover { background-color: #faf8f5; }
            table tbody td { padding: 10px 14px; color: #333; vertical-align: middle; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(tabela_html, unsafe_allow_html=True)

        csv = dados.to_csv(index=False).encode("utf-8")
        st.download_button("\u2b07 Exportar CSV", csv, "casos.csv", "text/csv")

    with tab_status:
        st.markdown("#### Gerenciar Status")
        st.caption("Altere o status de qualquer caso \u2014 a mudanca e salva automaticamente.")

        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            prio_filter = st.selectbox("Filtrar prioridade", ["Todas", "P1", "P2", "P3", "P4"])

        dados_status = dados if prio_filter == "Todas" else dados[dados["prioridade"] == prio_filter]

        for _, caso in dados_status.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1.5])
                with col1:
                    st.markdown(f"**{caso['nome_do_caso']}**")
                    st.caption(f"{caso['nucleo']}  \u00b7  {caso['responsavel']}  \u00b7  {caso['prioridade']}")
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
                        st.toast(f"\u2705 Status atualizado: {novo}")
                        st.rerun()
                st.divider()
