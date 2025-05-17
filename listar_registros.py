import sqlite3

def listar_registros():
    """Lista todos os registros do banco de dados com todas as gematrias"""
    try:
        conn = sqlite3.connect('gematria.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registros')
        rows = cursor.fetchall()
        
        print(f"\nTotal de registros: {len(rows)}\n")
        
        # Cabeçalho completo
        print("ID | Texto | Reduz | Ord | Hebr | Q.Red | Q.Ord | Trig | Criacao | Letras")
        print("-" * 90)
        
        # Formatação mais compacta para caber todas as gematrias
        for row in rows:
            print(f"{row['id']:2} | {row['texto'][:15]:<15} | {row['reduzido']:4} | {row['ordinal']:3} | {row['hebraico']:4} | {row['quadrado_reduzido']:5} | {row['quadrado_ordinal']:5} | {row['trigonal']:4} | {row['criacao']:6} | {row['quantidade_letras']:2}")
        
        conn.close()
    except Exception as e:
        print(f"Erro ao listar registros: {e}")

if __name__ == "__main__":
    listar_registros() 