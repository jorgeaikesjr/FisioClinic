import pandas as pd
import sqlite3
import uuid
from datetime import date

def import_patients():
    excel_path = 'Old_data/pacientes.xls'
    db_path = 'fisioclinic.db'
    default_birth_date = '1926-01-01'
    
    print(f"Lendo dados de {excel_path}...")
    try:
        # Lendo o arquivo Excel (.xls)
        df = pd.read_excel(excel_path)
        print("Colunas encontradas no Excel:", df.columns.tolist())
        
        # Mapeando as colunas conforme a estrutura do banco
        # Esperado no Excel: 'nome', 'contato', 'sexo'
        # Estrutura no banco: name, contact, sex
        
        column_mapping = {
            'PACIENTE': 'name',
            'CONTATO': 'contact',
            'SEXO': 'sex'
        }
        
        # Renomear colunas
        df = df.rename(columns=column_mapping)
        
        # Garantir que as colunas mapeadas existem no DF final
        for col in ['name', 'contact', 'sex']:
            if col not in df.columns:
                print(f"Aviso: Coluna {col} não encontrada no DataFrame após mapeamento.")
                df[col] = None
        
        # Adicionar colunas faltantes
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        df['birth_date'] = default_birth_date
        df['is_active'] = 1  # SQLite usa 1 para True
        df['guardian'] = None
        df['anamnesis'] = None
        
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        
        # Inserir os dados na tabela 'patients'
        # Usamos to_sql mas precisamos garantir que a ordem das colunas e os tipos estejam corretos
        # Ou simplesmente percorrer o dataframe para maior controle
        
        print(f"Importando {len(df)} pacientes...")
        
        cursor = conn.cursor()
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO patients (id, name, contact, guardian, sex, birth_date, anamnesis, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['id'], 
                    row['name'], 
                    row['contact'], 
                    row.get('guardian'), 
                    row.get('sex'), 
                    row['birth_date'], 
                    row.get('anamnesis'), 
                    row['is_active']
                ))
            except sqlite3.Error as e:
                print(f"Erro ao inserir paciente {row['name']}: {e}")
                
        conn.commit()
        conn.close()
        print("Importação concluída com sucesso!")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo {excel_path} não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    import_patients()
