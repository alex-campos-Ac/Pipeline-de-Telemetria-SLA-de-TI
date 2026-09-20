# Qual é o uso médio de CPU e de Memória para cada um dos servidores?
SELECT 
servidor,
AVG(cpu_pct) as media_cpu,
AVG(memoria_pct) AS media_memoria
FROM servidores_metrics
GROUP BY servidor

#visualizar apenas os servidores que possuem uso médio de CPU superior a 50%
SELECT 
	servidor,
	AVG(cpu_pct) as media_cpu
FROM servidores_metrics
GROUP BY servidor
HAVING AVG(cpu_pct) > 50


-- Divide os valores por 100 para voltar às casas decimais corretas (ex: 6814 virar 68.14)
UPDATE servidores_metrics
SET cpu_pct = cpu_pct / 100,
    memoria_pct = memoria_pct / 100;


# Quantos dias/registros cada servidor teve com pico crítico de CPU acima de 80%?
SELECT
	servidor,
	COUNT(*)
FROM servidores_metrics
WHERE cpu_pct > 80
GROUP BY servidor


# cada dia e servidor, o uso de CPU do dia atual lado a lado com o uso de CPU do dia anterior
SELECT
  data_registro AS Data_de_Registro,
  servidor AS Servidor,
  cpu_pct AS Process_CPU,
  LAG (cpu_pct)	OVER (PARTITION BY servidor ORDER BY data_registro)	 AS Servidor_dia_anterior

FROM servidores_metrics


# picos diários e calcular a média de CPU do dia atual somada aos 2 dias anteriores (janela móvel de 3 dias)
SELECT
  data_registro AS Data_de_Registro,
  servidor AS Servidor,
  cpu_pct,
  AVG(cpu_pct) OVER (
  PARTITION BY servidor ORDER BY data_registro 
  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)	 AS media_movel_3dias

FROM servidores_metrics
----------------------------------------------------------------------------
Chamados_ti
# Tempo em minutos da abertura do chamado para o fechado.
SELECT
id_chamado,
data_abertura,
data_fechamento,
DATEDIFF(hour, data_abertura, data_fechamento)	AS horas_de_atendimento

FROM chamados_ti


# Média de Tempo de Resolução por Prioridade
SELECT

prioridade,
AVG (DATEDIFF(hour, data_abertura, data_fechamento))	AS horas_de_atendimento

FROM chamados_ti

GROUP BY prioridade
ORDER BY horas_de_atendimento DESC

# Define que qualquer chamado resolvido em até 24 horas está dentro do prazo (No Prazo), e acima disso está Fora do Prazo.
SELECT
chamados_ti.id_chamado AS Chamado,
chamados_ti.prioridade	AS Prioridade,
DATEDIFF (hour, data_abertura, data_fechamento) AS horas_atendimento,


CASE
	WHEN DATEDIFF (hour, data_abertura, data_fechamento) <= 24 THEN 'No prazo'
	ELSE 'Fora do prazo'
END AS status_SLA


FROM chamados_ti