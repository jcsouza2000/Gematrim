import csv
import sqlite3
import os
import sys
from datetime import datetime

def exportar_db_para_csv(arquivo_db="gematria.db", arquivo_csv=None):
    """
    Exporta dados do banco de dados da aplicação Gematria para um arquivo CSV.
    
    Args:
        arquivo_db (str): Caminho para o banco de dados SQLite
        arquivo_csv (str): Caminho para o arquivo CSV de saída (opcional)
    """
    
    # Se o nome do arquivo CSV não for especificado, gerar um nome com a data atual
    if not arquivo_csv:
        data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_csv = f"gematria_export_{data_atual}.csv"
    
    # Verificar se o banco de dados existe
    if not os.path.exists(arquivo_db):
        print(f"Erro: Banco de dados '{arquivo_db}' não encontrado.")
        return False
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(arquivo_db)
        cursor = conn.cursor()
        
        # Verificar se a tabela 'registros' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registros'")
        if not cursor.fetchone():
            print("Erro: Tabela 'registros' não encontrada no banco de dados.")
            conn.close()
            return False
        
        # Obter contagem de registros
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_registros = cursor.fetchone()[0]
        print(f"Total de registros no banco de dados: {total_registros}")
        
        if total_registros == 0:
            print("Aviso: O banco de dados não contém registros para exportar.")
            conn.close()
            return False
        
        # Obter todos os registros
        cursor.execute("""
            SELECT texto, reduzido, ordinal, hebraico, 
                   quadrado_reduzido, quadrado_ordinal, trigonal,
                   criacao, quantidade_letras
            FROM registros
            ORDER BY texto
        """)
        
        registros = cursor.fetchall()
        
        # Definir os cabeçalhos do CSV
        campos = [
            'texto', 'reduzido', 'ordinal', 'hebraico', 
            'quadrado_reduzido', 'quadrado_ordinal', 'trigonal', 
            'criacao', 'quantidade_letras'
        ]
        
        # Escrever no arquivo CSV
        with open(arquivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            
            # Escrever cabeçalhos
            writer.writerow(campos)
            
            # Escrever registros
            writer.writerows(registros)
        
        print(f"Exportação concluída com sucesso! Arquivo: {arquivo_csv}")
        print(f"Total de registros exportados: {len(registros)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro não esperado: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        # Exportar para o arquivo CSV especificado
        arquivo_csv = sys.argv[1]
        exportar_db_para_csv(arquivo_csv=arquivo_csv)
    else:
        # Exportar para um arquivo com nome padrão
        exportar_db_para_csv() 