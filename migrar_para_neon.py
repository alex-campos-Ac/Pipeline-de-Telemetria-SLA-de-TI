import os

# ⚠️ OBRIGATÓRIO: Desativa a extensão C do SQLAlchemy ANTES de importar o SQLAlchemy
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# 1. Conexão com SQL Server Local usando pymssql (evita bloqueio de DLLs/ODBC)
# Substitua 'localhost' e 'DB_MONITORAMENTO' se necessário
SERVER = 'localhost' 
DATABASE = 'DB_MONITORAMENTO'

# Se o seu SQL Server usa Autenticação do Windows:
URL_SQL_SERVER = f"mssql+pymssql://{SERVER}/{DATABASE}"

# Nota: Se o seu SQL Server usa usuário/senha, ajuste para:
# URL_SQL_SERVER = f"mssql+pymssql://usuario:senha@{SERVER}/{DATABASE}"

# 2. Conexão com o PostgreSQL do NEON (Nuvem)
URL_NEON = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_2naPSbrUe1Vi@ep-aged-sound-b48bmgk1-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def migrar():
    print("⏳ Conectando ao SQL Server e ao Neon...")
    try:
        engine_sqlserver = create_engine(URL_SQL_SERVER)
        engine_neon = create_engine(URL_NEON)

        tabelas = ["chamados_ti", "servidores_metrics"]

        for tabela in tabelas:
            print(f"\n📦 Lendo '{tabela}' do SQL Server...")
            df = pd.read_sql(f"SELECT * FROM {tabela}", engine_sqlserver)
            
            # Padroniza os nomes das colunas para minúsculas (compatível com o Postgres)
            df.columns = [col.lower() for col in df.columns]
            
            print(f"🚀 Enviando {len(df)} registros para o Neon...")
            df.to_sql(tabela, engine_neon, if_exists="replace", index=False)
            print(f"✅ Tabela '{tabela}' criada e populada na nuvem!")

        print("\n🎉 Migração finalizada com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")

if __name__ == "__main__":
    migrar()