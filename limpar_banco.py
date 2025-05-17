import sqlite3
import os

def limpar_banco_dados():
    """Limpa completamente o banco de dados, removendo todos os registros."""
    
    DB_FILE = "gematria.db"
    
    # Verifica se o arquivo existe
    if not os.path.exists(DB_FILE):
        print(f"Arquivo {DB_FILE} não encontrado.")
        return
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Obtém o total de registros antes da limpeza
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_antes = cursor.fetchone()[0]
        print(f"Total de registros antes da limpeza: {total_antes}")
        
        # Limpa a tabela de registros
        cursor.execute("DELETE FROM registros")
        conn.commit()
        
        # Reinicia o contador de autoincremento
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='registros'")
        conn.commit()
        
        # Verifica quantos registros restaram
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_depois = cursor.fetchone()[0]
        print(f"Total de registros após a limpeza: {total_depois}")
        
        # Otimiza o banco de dados
        print("Otimizando banco de dados...")
        cursor.execute("VACUUM")
        conn.commit()
        print("Banco de dados limpo e otimizado com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro ao limpar banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Confirmação de segurança
    print("ATENÇÃO: Esta operação irá excluir TODOS os registros do banco de dados.")
    confirma = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirma == "CONFIRMAR":
        limpar_banco_dados()
    else:
        print("Operação cancelada.") 