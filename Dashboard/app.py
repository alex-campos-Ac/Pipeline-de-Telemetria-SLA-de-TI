import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Configuração da Página
st.set_page_config(page_title="Pipeline de Telemetria & SLA de TI", layout="wide")

# 2. CSS Customizado para Estilização Moderna (Dark Theme Refinado)
st.markdown("""
    <style>
    /* Estilização Geral do Fundo */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Estilização dos Cartões de KPI (st.metric) */
    div[data-testid="stMetric"] {
        background-color: #1E222D;
        border: 1px solid #2A2F3D;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] > label {
        color: #8B949E !important; /* Cor do Título do KPI (Cinza Suave) */
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #58A6FF !important; /* Cor dos Números do KPI (Azul Ciano) */
        font-size: 28px !important;
        font-weight: bold !important;
    }

    /* Estilização das Abas (Tabs) */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #8B949E !important;
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #58A6FF !important;
        border-bottom: 3px solid #58A6FF !important;
        background-color: transparent !important;
    }

    /* Estilização do Selectbox de Servidores na Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    div[data-baseweb="select"] > div {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        color: #C9D1D9 !important;
    }
    div[data-baseweb="select"]:hover > div {
        border-color: #58A6FF !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🖥️ Dashboard de Telemetria & SLA de TI")
st.markdown("---")

# 3. Conexão com o SQL Server
SERVER = r'localhost' 
DATABASE = 'DB_MONITORAMENTO'

@st.cache_data
def carregar_dados_sql(query):
    connection_string = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# 4. Estruturação em Abas
aba1, aba2 = st.tabs(["📊 Gestão de Incidentes (SLAs)", "⚡ Telemetria de Servidores (CPU)"])

# --- ABA 1: CHAMADOS DE TI ---
with aba1:
    st.subheader("Indicadores de SLA e Chamados de TI")
    try:
        query_chamados = """
        SELECT 
            prioridade,
            COUNT(*) AS contagem_chamados,
            SUM(CASE WHEN DATEDIFF(HOUR, data_abertura, data_fechamento) <= 24 THEN 1 ELSE 0 END) AS no_prazo,
            SUM(CASE WHEN DATEDIFF(HOUR, data_abertura, data_fechamento) > 24 THEN 1 ELSE 0 END) AS fora_prazo,
            SUM(CASE WHEN data_fechamento IS NULL THEN 1 ELSE 0 END) AS em_aberto,
            AVG(DATEDIFF(HOUR, data_abertura, data_fechamento)) AS media_horas
        FROM chamados_ti
        GROUP BY prioridade
        ORDER BY 
            CASE 
                WHEN prioridade = 'Alta' THEN 1
                WHEN prioridade = 'Média' THEN 2
                WHEN prioridade = 'Baixa' THEN 3
            END;
        """
        df_chamados = carregar_dados_sql(query_chamados)
        
        # KPIs no topo
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Chamados", int(df_chamados["contagem_chamados"].sum()))
        col2.metric("Chamados em Aberto", int(df_chamados["em_aberto"].sum()))
        col3.metric("Média Geral de Resolução", f"{df_chamados['media_horas'].mean():.1f}h")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Resumo por Prioridade")
        st.dataframe(df_chamados, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados de chamados: {e}")

# --- ABA 2: TELEMETRIA DE SERVIDORES ---
with aba2:
    st.subheader("Monitoramento de CPU e Média Móvel (3 Dias)")
    try:
        query_servidores = """
        SELECT 
            data_registro,
            servidor,
            cpu_pct,
            LAG(cpu_pct, 1) OVER(PARTITION BY servidor ORDER BY data_registro) AS cpu_dia_anterior,
            AVG(cpu_pct) OVER(
                PARTITION BY servidor 
                ORDER BY data_registro 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) AS media_movel_3dias
        FROM servidores_metrics;
        """
        df_servidores = carregar_dados_sql(query_servidores)
        
        # Filtro de Servidor na Barra Lateral
        servidores_unicos = df_servidores["servidor"].unique()
        servidor_selecionado = st.sidebar.selectbox("Selecione o Servidor:", servidores_unicos)
        
        # Filtrar o DataFrame para o servidor escolhido
        df_filtrado = df_servidores[df_servidores["servidor"] == servidor_selecionado]
        
        # Exibição de Gráficos de Linha
        st.markdown(f"#### Tendência de Carga - {servidor_selecionado}")
        st.line_chart(df_filtrado.set_index("data_registro")[["cpu_pct", "media_movel_3dias"]])
        
        # Tabela Detalhada
        st.markdown("#### Dados Detalhados do Servidor")
        st.dataframe(df_filtrado, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados de servidores: {e}")