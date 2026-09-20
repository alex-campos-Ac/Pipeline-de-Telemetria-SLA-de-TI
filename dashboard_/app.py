import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="Pipeline de Telemetria & SLA de TI", 
    page_icon="🖥️", 
    layout="wide"
)

# 2. CSS Customizado para Design Moderno (Dark Mode Refinado)
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
        color: #8B949E !important; /* Cinza Suave */
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #58A6FF !important; /* Azul Ciano */
        font-size: 26px !important;
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

    /* Estilização da Barra Lateral (Sidebar) */
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
    </style>
""", unsafe_allow_html=True)

st.title("🖥️ Dashboard de Telemetria & SLA de TI")
st.markdown("---")

# 3. Conexão com o SQL Server Local
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
aba1, aba2 = st.tabs(["📊 Gestão de Incidentes (SLAs)", "⚡ Telemetria de Servidores (CPU & Memória)"])

# ==============================================================================
# --- ABA 1: CHAMADOS DE TI & SLA ---
# ==============================================================================
with aba1:
    st.subheader("📌 Performance de Atendimento e Cumprimento de SLA")
    try:
        # Query Consolidada de Chamados em T-SQL
        query_chamados = """
        SELECT 
            prioridade,
            COUNT(*) AS total_chamados,
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
        
        # Display de KPIs em Colunas
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Chamados", int(df_chamados["total_chamados"].sum()))
        kpi2.metric("Chamados em Aberto", int(df_chamados["em_aberto"].sum()))
        kpi3.metric("Fora do Prazo (SLA)", int(df_chamados["fora_prazo"].sum()))
        kpi4.metric("Tempo Médio de Resolução", f"{df_chamados['media_horas'].mean():.1f}h")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_graf, col_tb = st.columns([1.2, 1])
        
        with col_graf:
            st.markdown("##### Cumulative SLA Status por Prioridade")
            # Gráfico de Barras Empilhadas via Plotly
            fig_sla = px.bar(
                df_chamados, 
                x="prioridade", 
                y=["no_prazo", "fora_prazo", "em_aberto"],
                title="Status de Atendimento por Prioridade",
                labels={"value": "Quantidade de Incidentes", "prioridade": "Prioridade"},
                color_discrete_map={"no_prazo": "#238636", "fora_prazo": "#DA3633", "em_aberto": "#D29922"},
                template="plotly_dark"
            )
            fig_sla.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
            st.plotly_chart(fig_sla, use_container_width=True)
            
        with col_tb:
            st.markdown("##### Resumo Analítico por Nível de Prioridade")
            st.dataframe(df_chamados, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados de chamados: {e}")

# ==============================================================================
# --- ABA 2: TELEMETRIA DE SERVIDORES ---
# ==============================================================================
with aba2:
    st.subheader("⚡ Monitoramento de Infraestrutura e Capacidade")
    try:
        # Query de Telemetria com Window Functions (LAG e Média Móvel)
        query_servidores = """
        SELECT 
            data_registro,
            servidor,
            cpu_pct,
            memoria_pct,
            LAG(cpu_pct, 1) OVER(PARTITION BY servidor ORDER BY data_registro) AS cpu_dia_anterior,
            AVG(cpu_pct) OVER(
                PARTITION BY servidor 
                ORDER BY data_registro 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) AS media_movel_3dias
        FROM servidores_metrics;
        """
        df_servidores = carregar_dados_sql(query_servidores)
        
        # Filtro de Servidores na Barra Lateral (Sidebar)
        servidores_unicos = df_servidores["servidor"].unique()
        servidor_selecionado = st.sidebar.selectbox("🖥️ Selecione o Servidor:", servidores_unicos)
        
        # Dataset Filtrado
        df_filtrado = df_servidores[df_servidores["servidor"] == servidor_selecionado]
        
        # Cálculo de Métricas do Servidor Selecionado
        media_cpu = df_filtrado["cpu_pct"].mean()
        media_mem = df_filtrado["memoria_pct"].mean()
        picos_criticos = (df_filtrado["cpu_pct"] > 80).sum()
        
        # Cartões de KPI do Servidor
        c1, c2, c3 = st.columns(3)
        c1.metric("Uso Médio de CPU", f"{media_cpu:.1f}%")
        c2.metric("Uso Médio de Memória", f"{media_mem:.1f}%")
        c3.metric("Picos Críticos de CPU (>80%)", f"{picos_criticos} dias")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico Temporal de CPU x Média Móvel (Plotly)
        st.markdown(f"##### Tendência do Processador - {servidor_selecionado}")
        fig_cpu = go.Figure()
        fig_cpu.add_trace(go.Scatter(x=df_filtrado["data_registro"], y=df_filtrado["cpu_pct"], mode='lines+markers', name='CPU Diária (%)', line=dict(color='#58A6FF', width=1.5)))
        fig_cpu.add_trace(go.Scatter(x=df_filtrado["data_registro"], y=df_filtrado["media_movel_3dias"], mode='lines', name='Média Móvel (3 Dias)', line=dict(color='#F0883E', width=2.5, dash='dash')))
        fig_cpu.update_layout(template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", xaxis_title="Data", yaxis_title="Carga da CPU (%)")
        st.plotly_chart(fig_cpu, use_container_width=True)
        
        # Alerta Diagnóstico: Servidores com Carga Média > 50%
        st.markdown("##### ⚠️ Diagnóstico de Capacidade: Servidores com Carga Médio de CPU > 50%")
        query_alerta = """
        SELECT 
            servidor,
            ROUND(AVG(cpu_pct), 2) AS media_cpu_pct,
            ROUND(AVG(memoria_pct), 2) AS media_memoria_pct
        FROM servidores_metrics
        GROUP BY servidor
        HAVING AVG(cpu_pct) > 50;
        """
        df_alerta = carregar_dados_sql(query_alerta)
        st.dataframe(df_alerta, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados de servidores: {e}")