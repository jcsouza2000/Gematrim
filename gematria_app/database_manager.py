import sqlite3
import os # Manteremos os para verificar a existência do DB, se necessário

# Tabela de valores Gematria (copiada de gematria.py)
GEMATRIA_TABLE = {
    "Reduzido": {
        "A": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "B": 2,
        "C": 3, "ç": 3,
        "D": 4,
        "E": 5, "é": 5, "ê": 5,
        "F": 6,
        "G": 7,
        "H": 8,
        "I": 9, "í": 9,
        "J": 1,
        "K": 2,
        "L": 3,
        "M": 4,
        "N": 5, "ñ": 5,
        "O": 6, "ó": 6, "ô": 6, "õ": 6, "ö": 6,
        "P": 7,
        "Q": 8,
        "R": 9,
        "S": 1,
        "T": 2,
        "U": 3, "ú": 3, "ü": 3,
        "V": 4,
        "W": 5,
        "X": 6,
        "Y": 7,
        "Z": 8
    },
    "Ordinal": {
        "A": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "B": 2,
        "C": 3, "ç": 3,
        "D": 4,
        "E": 5, "é": 5, "ê": 5,
        "F": 6,
        "G": 7,
        "H": 8,
        "I": 9, "í": 9,
        "J": 10,
        "K": 11,
        "L": 12,
        "M": 13,
        "N": 14, "ñ": 14,
        "O": 15, "ó": 15, "ô": 15, "õ": 15, "ö": 15,
        "P": 16,
        "Q": 17,
        "R": 18,
        "S": 19,
        "T": 20,
        "U": 21, "ú": 21, "ü": 21,
        "V": 22,
        "W": 23,
        "X": 24,
        "Y": 25,
        "Z": 26
    },
    "Hebraico": {
        "A": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "B": 2,
        "C": 3, "ç": 3,
        "D": 4,
        "E": 5, "é": 5, "ê": 5,
        "F": 6,
        "G": 7,
        "H": 8,
        "I": 9, "í": 9,
        "J": 10,
        "K": 20,
        "L": 30,
        "M": 40,
        "N": 50, "ñ": 50,
        "O": 60, "ó": 60, "ô": 60, "õ": 60, "ö": 60,
        "P": 70,
        "Q": 80,
        "R": 90,
        "S": 100,
        "T": 200,
        "U": 300, "ú": 300, "ü": 300,
        "V": 400,
        "W": 500,
        "X": 600,
        "Y": 700,
        "Z": 800
    }
}

# Função de cálculo (copiada de gematria.py - sem alterações necessárias aqui)
def calcular_gematria(texto):
    texto_original = texto 
    texto = texto.upper() 
    
    resultados = {}
    letras_valores = []

    for metodo in ["Reduzido", "Ordinal", "Hebraico"] :
        total = 0
        valores_letra = []
        for char in texto:
            # Se precisar remover acentos ou caracteres não-letra para o cálculo,
            # a lógica de normalização iria aqui antes do get.
            # Ex: char = unidecode.unidecode(char) se usar a biblioteca unidecode
            valor = GEMATRIA_TABLE[metodo].get(char, 0)
            total += valor
            # Apenas adiciona valor se for maior que 0 (ou seja, letra válida na tabela)
            if valor > 0:
                valores_letra.append(valor) 
        resultados[f"{metodo.lower()}"] = total
        letras_valores.append(valores_letra)

    reduzido_letras, ordinal_letras, hebraico_letras = letras_valores

    resultados["quadrado_reduzido"] = sum([v**2 for v in reduzido_letras])
    resultados["quadrado_ordinal"] = sum([v**2 for v in ordinal_letras])
    resultados["trigonal"] = sum([n*(n+1)//2 for n in ordinal_letras])
    
    quantidade_letras_sem_espaco = sum(1 for char in texto_original if not char.isspace() and char.isalpha()) # Refinado para contar apenas letras
    resultados["quantidade_letras"] = quantidade_letras_sem_espaco

    if resultados["quantidade_letras"] > 0: 
        resultados["criacao"] = (resultados["ordinal"] * resultados["quantidade_letras"]) + resultados["quantidade_letras"]
    else:
        resultados["criacao"] = 0 

    return resultados

# --- Funções do Banco de Dados (a serem implementadas) ---

DB_FILE = "gematria.db" # Alterado para ficar no diretório atual, não em um subdiretório

def inicializar_db():
    """Cria a tabela 'registros' no banco de dados SQLite se ela não existir."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Cria a tabela com todas as colunas necessárias
        # Usamos INTEGER PRIMARY KEY para o id autoincrementável
        # Usamos TEXT para o texto (com COLLATE NOCASE para buscas case-insensitive)
        # Usamos INTEGER para todos os valores numéricos de Gematria
        # Adicionamos um índice UNIQUE na coluna texto (case-insensitive) para
        # facilitar a verificação de duplicatas e otimizar buscas por texto.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY,
                texto TEXT UNIQUE COLLATE NOCASE,
                reduzido INTEGER,
                ordinal INTEGER,
                hebraico INTEGER,
                quadrado_reduzido INTEGER,
                quadrado_ordinal INTEGER,
                trigonal INTEGER,
                criacao INTEGER,
                quantidade_letras INTEGER
            )
        ''')
        
        # Adicional: Criar índices para colunas frequentemente pesquisadas pode otimizar
        # cursor.execute('CREATE INDEX IF NOT EXISTS idx_ordinal ON registros (ordinal)')
        # cursor.execute('CREATE INDEX IF NOT EXISTS idx_reduzido ON registros (reduzido)')
        # ... (outros índices se necessário)
        
        conn.commit()
        conn.close()
        print(f"Banco de dados inicializado em {DB_FILE}") # Mensagem para confirmação
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o DB: {e}")
        if conn:
            conn.close()

def adicionar_registro_db(texto, valores):
    """Insere um novo registro ou atualiza um existente com base no texto (case-insensitive)."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Prepara os dados para inserção/atualização
        # A ordem deve corresponder às colunas da tabela (exceto id)
        dados_para_sql = (
            texto,
            valores.get('reduzido'),
            valores.get('ordinal'),
            valores.get('hebraico'),
            valores.get('quadrado_reduzido'),
            valores.get('quadrado_ordinal'),
            valores.get('trigonal'),
            valores.get('criacao'),
            valores.get('quantidade_letras')
        )
        
        # SQL para inserir ou atualizar em caso de conflito na coluna 'texto'
        # Mantém o ID original e atualiza os outros campos.
        sql = '''
            INSERT INTO registros (texto, reduzido, ordinal, hebraico, quadrado_reduzido, quadrado_ordinal, trigonal, criacao, quantidade_letras)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(texto) DO UPDATE SET
                reduzido=excluded.reduzido,
                ordinal=excluded.ordinal,
                hebraico=excluded.hebraico,
                quadrado_reduzido=excluded.quadrado_reduzido,
                quadrado_ordinal=excluded.quadrado_ordinal,
                trigonal=excluded.trigonal,
                criacao=excluded.criacao,
                quantidade_letras=excluded.quantidade_letras;
        '''
        
        cursor.execute(sql, dados_para_sql)
        conn.commit()
        # print(f"Registro para '{texto}' adicionado/atualizado com sucesso.") # Mensagem opcional
        return True # Indica sucesso
        
    except sqlite3.Error as e:
        print(f"Erro ao adicionar/atualizar registro no DB: {e}")
        # Poderia fazer rollback aqui se necessário: conn.rollback()
        return False # Indica falha
    finally:
        if conn:
            conn.close()

def pesquisar_db(criterio, termo):
    """Pesquisa registros no banco de dados com base em um critério e termo.

    Args:
        criterio (str): O nome da coluna do banco de dados para pesquisar.
        termo (str/int): O valor a ser pesquisado.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um registro encontrado.
              Retorna uma lista vazia se nenhum resultado for encontrado ou em caso de erro.
    """
    conn = None
    resultados = []
    
    # Lista de colunas válidas (para segurança e validação)
    colunas_validas = [
        "id", "texto", "reduzido", "ordinal", "hebraico", "quadrado_reduzido", 
        "quadrado_ordinal", "trigonal", "criacao", "quantidade_letras"
    ]
    
    if criterio not in colunas_validas:
        print(f"Erro: Critério de pesquisa inválido '{criterio}'")
        return resultados # Retorna lista vazia

    try:
        print(f"Conectando ao banco de dados: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        # Configura row_factory para retornar dicionários em vez de tuplas
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # Verificar se a tabela existe e se tem registros
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='registros'")
        if cursor.fetchone()[0] == 0:
            print("A tabela 'registros' não existe")
            return resultados
            
        cursor.execute("SELECT COUNT(*) FROM registros")
        qtd_registros = cursor.fetchone()[0]
        print(f"Quantidade de registros na tabela: {qtd_registros}")
        
        # Se não houver registros, retornar lista vazia
        if qtd_registros == 0:
            print("Nenhum registro na tabela")
            return resultados
        
        sql = f"SELECT * FROM registros WHERE "
        params = ()
        
        if criterio == "texto":
            # Busca textual (contém) - usa LIKE e % para wildcard
            # COLLATE NOCASE já está na definição da tabela, mas LIKE pode precisar
            sql += f"{criterio} LIKE ? COLLATE NOCASE"
            params = (f'%{termo}%',)
            print(f"SQL para busca textual: {sql} com parâmetro: {params}")
        else:
            # Busca exata para campos numéricos (ou ID)
            # Compara o valor diretamente.
            sql += f"{criterio} = ?"
            params = (termo,)
            print(f"SQL para busca numérica: {sql} com parâmetro: {params}")
            
        cursor.execute(sql, params)
        rows = cursor.fetchall() # Pega todas as linhas que correspondem
        print(f"Consulta retornou {len(rows)} linhas")
        
        # Converte as linhas (sqlite3.Row) em dicionários padrão
        for row in rows:
            resultados.append(dict(row))
            
    except sqlite3.Error as e:
        print(f"Erro ao pesquisar no DB: {e}")
    finally:
        if conn:
            conn.close()
            
    return resultados

def limpar_duplicatas_db():
    """Remove registros duplicados (mesmo texto, case-insensitive),
       mantendo apenas o registro com o maior ID para cada texto.

    Returns:
        int: O número de registros duplicados removidos, ou -1 em caso de erro.
    """
    conn = None
    registros_removidos = 0
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Primeiro, obtenha a contagem total de registros
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_antes = cursor.fetchone()[0]
        print(f"Registros totais antes da limpeza: {total_antes}")
        
        # Verificar se existe algum texto duplicado (ignorando case)
        cursor.execute('''
            SELECT LOWER(texto), COUNT(*) 
            FROM registros
            GROUP BY LOWER(texto)
            HAVING COUNT(*) > 1
        ''')
        
        duplicatas = cursor.fetchall()
        if duplicatas:
            print(f"Encontradas {len(duplicatas)} palavras com duplicatas:")
            for texto, contagem in duplicatas:
                print(f"  '{texto}' aparece {contagem} vezes")
        else:
            print("Não foram encontradas duplicatas na análise prévia.")
            print("Isso provavelmente acontece porque a tabela tem restrição UNIQUE na coluna texto.")
        
        # SQL para deletar registros onde o ID não é o máximo ID 
        # para aquele grupo de texto (case-insensitive)
        sql = '''
            DELETE FROM registros
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM registros
                GROUP BY LOWER(texto)
            );
        '''
        
        cursor.execute(sql)
        registros_removidos = cursor.rowcount # Verifica quantos registros foram afetados
        conn.commit()
        
        # Verifique a contagem após a limpeza
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_depois = cursor.fetchone()[0]
        print(f"Registros totais após a limpeza: {total_depois}")
        print(f"Diferença na contagem: {total_antes - total_depois}")
        
        if registros_removidos > 0:
            print(f"{registros_removidos} registro(s) duplicado(s) removido(s) do banco de dados.")
            print("Otimizando banco de dados...")
            cursor.execute('VACUUM;')
            conn.commit()
            print("Otimização concluída.")
        else:
            print("Nenhum registro duplicado removido.")
            msg = """
            Nota: Não foram encontradas duplicatas porque a tabela foi criada com restrição UNIQUE
            na coluna 'texto' com COLLATE NOCASE, o que impede a inserção de textos duplicados
            independentemente de maiúsculas/minúsculas. Quando você tenta salvar um texto já existente,
            o SQLite atualiza o registro em vez de criar um novo.
            """
            print(msg)
            
        return registros_removidos

    except sqlite3.Error as e:
        print(f"Erro ao limpar duplicatas no DB: {e}")
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
        return -1 # Indica erro
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Returns a connection to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def search_by_text(conn, termo):
    """Search by text content (case insensitive)"""
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM registros WHERE texto LIKE ? COLLATE NOCASE"
        cursor.execute(sql, (f'%{termo}%',))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by text: {e}")
        return []

def search_by_normalized_text(conn, termo):
    """Search by normalized text (removing accents and special chars)"""
    try:
        cursor = conn.cursor()
        # This is a simplification - ideally you'd use a normalized column
        # or a proper SQL function to normalize text for comparison
        sql = "SELECT * FROM registros WHERE texto LIKE ? COLLATE NOCASE"
        cursor.execute(sql, (f'%{termo}%',))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by normalized text: {e}")
        return []

def search_by_reduzido(conn, valor):
    """Search by 'reduzido' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE reduzido = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by reduzido: {e}")
        return []

def search_by_ordinal(conn, valor):
    """Search by 'ordinal' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE ordinal = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by ordinal: {e}")
        return []

def search_by_hebraico(conn, valor):
    """Search by 'hebraico' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE hebraico = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by hebraico: {e}")
        return []

def search_by_quadrado_reduzido(conn, valor):
    """Search by 'quadrado_reduzido' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE quadrado_reduzido = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by quadrado_reduzido: {e}")
        return []

def search_by_quadrado_ordinal(conn, valor):
    """Search by 'quadrado_ordinal' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE quadrado_ordinal = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by quadrado_ordinal: {e}")
        return []

def search_by_trigonal(conn, valor):
    """Search by 'trigonal' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE trigonal = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by trigonal: {e}")
        return []

def search_by_criacao(conn, valor):
    """Search by 'criacao' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE criacao = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by criacao: {e}")
        return []

def search_by_qtd_letras(conn, valor):
    """Search by 'quantidade_letras' value"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE quantidade_letras = ?", (valor,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error searching by quantidade_letras: {e}")
        return []

# Adicione aqui outras funções relacionadas ao DB conforme necessário 