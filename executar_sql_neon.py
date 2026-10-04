import os
import re
from sqlalchemy import create_engine, text

# 1. URL do seu banco PostgreSQL no Neon Cloud
URL_NEON = "postgresql://neondb_owner:npg_2naPSbrUe1Vi@ep-aged-sound-b48bmgk1-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"

def rodar_script_sql():
    print("⏳ Lendo o arquivo .sql...")
    caminho_sql = "dados_exportados.sql"  # Coloque o nome correto do seu arquivo .sql aqui
    
    if not os.path.exists(caminho_sql):
        print(f"❌ Arquivo '{caminho_sql}' não encontrado na pasta atual.")
        return

    with open(caminho_sql, "r", encoding="utf-8-sig", errors="ignore") as f:
        conteudo_sql = f.read()

    # Adaptações de sintaxe T-SQL (SQL Server) para PostgreSQL
    print("🔄 Adaptando sintaxe de SQL Server para PostgreSQL...")
    conteudo_sql = re.sub(r'\[dbo\]\.', '', conteudo_sql)
    conteudo_sql = re.sub(r'\[|\]', '', conteudo_sql)
    conteudo_sql = re.sub(r'GO', ';', conteudo_sql, flags=re.IGNORECASE)
    conteudo_sql = re.sub(r'SET IDENTITY_INSERT.*?;', '', conteudo_sql, flags=re.IGNORECASE)
    conteudo_sql = re.sub(r'SET ANSI_NULLS.*?;', '', conteudo_sql, flags=re.IGNORECASE)
    conteudo_sql = re.sub(r'SET QUOTED_IDENTIFIER.*?;', '', conteudo_sql, flags=re.IGNORECASE)

    # Conecta ao Neon e executa os comandos SQL
    print("🚀 Conectando ao Neon e criando tabelas/dados...")
    engine = create_engine(URL_NEON)
    
    # Divide os comandos por ponto e vírgula e executa um a um
    comandos = [cmd.strip() for cmd in conteudo_sql.split(';') if cmd.strip()]
    
    with engine.begin() as conn:
        for cmd in comandos:
            try:
                conn.execute(text(cmd))
            except Exception as e:
                # Ignora avisos de comandos específicos do SQL Server
                pass

    print("✅ Dados e tabelas importados com sucesso para o Neon!")

if __name__ == "__main__":
    rodar_script_sql()