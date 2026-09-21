# 🖥️ Pipeline de Telemetria & SLA de TI (Engenharia & Análise)

## 📌 Visão Geral do Projeto
Aplicação web interativa desenvolvida em **Streamlit** e integrada a um banco de dados **SQL Server local**. O projeto simula o monitoramento corporativo de infraestrutura de TI e gestão de incidentes, combinando consultas analíticas avançadas em T-SQL a um painel web dinâmico e moderno.

---

## 🏗️ Arquitetura da Solução
```text
[CSVs / Dados Brutos] ──► [SQL Server Local] ──► [Python / SQLAlchemy] ──► [Streamlit Dashboard]
```

---

## 🛠️ Tech Stack & Ferramentas
* **Banco de Dados:** SQL Server (SSMS) & T-SQL
* **Linguagem & Bibliotecas:** Python, Pandas, SQLAlchemy, pyodbc, Plotly
* **Frontend Web:** Streamlit (Dark Theme / Custom CSS)
* **Ambiente & Versionamento:** VS Code, Virtualenv (`.venv`), Git & GitHub

---

## 🔍 Principais Consultas & Técnicas T-SQL Aplicadas
1. **Gestão de Incidentes (`chamados_ti`):**
   * Cálculo do tempo de resolução em horas via `DATEDIFF(HOUR, ...)`.
   * Classificação condicional de SLA (*No Prazo* $\le$ 24h, *Fora do Prazo* > 24h, *Em Aberto* `IS NULL`) via agregação com `SUM(CASE WHEN ...)`.
   * Ordenação lógica customizada por gravidade de prioridade (Alta $\rightarrow$ Média $\rightarrow$ Baixa).
2. **Telemetria de Servidores (`servidores_metrics`):**
   * Média móvel de 3 dias via Window Function `AVG(cpu_pct) OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.
   * Variação do uso em relação ao dia anterior utilizando `LAG()`.
   * Diagnóstico de capacidade para servidores com média de CPU acima de 50% via `HAVING`.

---

## 📊 Estrutura da Aplicação Web
* **Aba 1 — 📊 Gestão de Incidentes (SLAs):** KPIs globais de atendimento, gráfico de barras empilhadas por status de SLA e tabela analítica por prioridade.
* **Aba 2 — ⚡ Telemetria de Servidores (CPU & Memória):** Filtro dinâmico na barra lateral (sidebar) por servidor, gráfico de linha temporal comparativo (CPU x Média Móvel de 3 dias) e diagnóstico de gargalos de infraestrutura.

---

## 🚀 Como Executar este Projeto Localmente
1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/alex-campos-Ac/infra-metrics-analyzer.git
   cd infra-metrics-analyzer
   ```
2. **Configurar o Ambiente Virtual Python:**
   ```bash
   python -m venv .venv

   # Ativar no Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```
3. **Instalar as dependências:**
   ```bash
   pip install streamlit pandas sqlalchemy pyodbc plotly
   ```
4. **Executar a aplicação Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

## ✉️ Autor
**Alex Campos**  
Analista de Sistemas em transição para Análise de Dados / BI  
* **LinkedIn:** [linkedin.com/in/alex-campos-44bb01349](https://linkedin.com/in/alex-campos-44bb01349)  
* **GitHub:** [github.com/alex-campos-Ac](https://github.com/alex-campos-Ac)