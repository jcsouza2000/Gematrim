import json
import os

# Caminho do arquivo de dados
DATA_FILE = "gematria_data.json"

# Tabela de valores Gematria baseada no Excel fornecido
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

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Dados iniciais do Excel (exemplo)
        return [
            {"id": 1, "texto": "DNA", "reduzido": 10, "ordinal": 19, "hebraico": 55},
            # Adicione outros registros iniciais aqui conforme o Excel
        ]

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def calcular_gematria(texto):
    texto_original = texto # Preserva o texto original para contagem de letras
    texto = texto.upper() # Converte para maiúsculas para lookup na tabela
    # Idealmente, aqui removeríamos acentos e caracteres não-letra se necessário,
    # mas a tabela atual já inclui acentos.
    
    resultados = {}
    letras_valores = []

    # Calcula Reduzido, Ordinal e Hebraico (base e por letra)
    for metodo in ["Reduzido", "Ordinal", "Hebraico"] :
        total = 0
        valores_letra = []
        for char in texto:
            valor = GEMATRIA_TABLE[metodo].get(char, 0)
            total += valor
            valores_letra.append(valor) # Armazena valor da letra para cálculos futuros
        resultados[f"{metodo.lower()}"] = total
        letras_valores.append(valores_letra)

    # Desempacota os valores por letra
    reduzido_letras, ordinal_letras, hebraico_letras = letras_valores

    # Calcula Quadrado Reduzido (Soma dos quadrados dos valores reduzidos das letras)
    resultados["quadrado_reduzido"] = sum([v**2 for v in reduzido_letras])
    
    # Calcula Quadrado Ordinal (Soma dos quadrados dos valores ordinais das letras)
    resultados["quadrado_ordinal"] = sum([v**2 for v in ordinal_letras])
    
    # Calcula Trigonal (Soma dos T(n) dos valores ordinais das letras)
    resultados["trigonal"] = sum([n*(n+1)//2 for n in ordinal_letras])
    
    # Calcula Quantidade de Letras (ignorando espaços)
    # Conta caracteres no texto original que não são espaços em branco.
    # Se precisar ignorar pontuação também, a lógica precisaria ser expandida (ex: usando isalpha()).
    quantidade_letras_sem_espaco = sum(1 for char in texto_original if not char.isspace())
    resultados["quantidade_letras"] = quantidade_letras_sem_espaco

    # Calcula Criacao usando a fórmula: (Ordinal * QuantLetras) + QuantLetras
    # IMPORTANTE: Esta fórmula corresponde aos exemplos iniciais da planilha.
    # Se o valor 1128 (mencionado pelo usuário) for o correto para um input específico,
    # e a fórmula atual não o produzir, a fórmula precisa ser redefinida com base nesse exemplo.
    # Aguardando informação do usuário sobre qual texto gerou 1410 vs 1128.
    if resultados["quantidade_letras"] > 0: # Evita divisão por zero ou cálculo incorreto se não houver letras
        resultados["criacao"] = (resultados["ordinal"] * resultados["quantidade_letras"]) + resultados["quantidade_letras"]
    else:
        resultados["criacao"] = 0 # Ou outro valor padrão apropriado

    return resultados

def adicionar_registro():
    texto = input("Digite o texto para análise: ").strip()
    if not texto:
        print("Texto não pode ser vazio")
        return
    
    valores = calcular_gematria(texto)
    dados = carregar_dados() # Carrega os dados existentes
    texto_lower = texto.lower() # Converte para minúsculas para comparação
    
    registro_existente = None
    indice_existente = -1
    
    # Verifica se o texto já existe (ignorando caso)
    for i, reg in enumerate(dados):
        if reg.get("texto", "").lower() == texto_lower:
            registro_existente = reg
            indice_existente = i
            break
            
    if registro_existente:
        # Texto encontrado - perguntar se deseja substituir
        print(f"\nO texto \"{registro_existente['texto']}\" (ID: {registro_existente['id']}) já existe.")
        print("Novos valores calculados:")
        for chave, valor in valores.items():
            nome_campo = chave.replace('_', ' ').title()
            print(f"  {nome_campo}: {valor}")
        print("-" * 25)
        
        confirmacao_substituir = input("Deseja substituir o registro existente com os novos valores? (S/N): ").strip().lower()
        
        if confirmacao_substituir == 's':
            # Atualiza o registro existente com os novos valores (mantém ID e texto original)
            registro_existente.update(valores)
            salvar_dados(dados)
            print(f"Registro ID {registro_existente['id']} atualizado com sucesso!")
        else:
            print("Substituição cancelada. Nenhum registro foi alterado.")
            
    else:
        # Texto não encontrado - proceder com adição normal
        print("\n--- Valores Calculados ---")
        print(f"Texto: {texto}")
        for chave, valor in valores.items():
            nome_campo = chave.replace('_', ' ').title()
            print(f"{nome_campo}: {valor}")
        print("--------------------------")
        
        confirmacao_salvar = input("Salvar este novo registro? (S/N): ").strip().lower()
        
        if confirmacao_salvar == 's':
            # Gera novo ID (considera o maior ID existente + 1 para evitar colisões se IDs foram removidos)
            novo_id = max([item.get('id', 0) for item in dados] + [0]) + 1
            novo_registro = {
                "id": novo_id,
                "texto": texto,
                **valores
            }
            dados.append(novo_registro)
            salvar_dados(dados)
            print(f"Registro #{novo_registro['id']} adicionado com sucesso!")
        else:
            print("Registro não foi salvo.")

def limpar_registros_duplicados():
    dados = carregar_dados()
    if not dados:
        print("Arquivo de dados está vazio. Nada para limpar.")
        return

    registros_unicos = {}
    duplicatas_encontradas = 0

    # Itera sobre os dados para encontrar o registro mais recente (maior ID) para cada texto
    for registro in dados:
        texto = registro.get("texto", "")
        if not texto: # Ignora registros sem texto
            continue 
            
        texto_lower = texto.lower()
        id_atual = registro.get("id", 0)
        
        if texto_lower in registros_unicos:
            # Já vimos esse texto, verificar se o ID atual é maior
            if id_atual > registros_unicos[texto_lower].get("id", 0):
                registros_unicos[texto_lower] = registro # Mantém o mais recente
            duplicatas_encontradas += 1
        else:
            # Primeira vez vendo esse texto
            registros_unicos[texto_lower] = registro
            
    if duplicatas_encontradas == 0:
        print("Nenhum registro duplicado encontrado.")
        return
        
    # Lista final com apenas os registros únicos (os valores do dicionário)
    dados_limpos = list(registros_unicos.values())
    # Opcional: Ordenar por ID para manter uma ordem consistente
    dados_limpos.sort(key=lambda x: x.get('id', 0))
    
    print(f"\nForam encontrados {duplicatas_encontradas} registro(s) duplicado(s) (baseado no campo 'texto').")
    print(f"Após a limpeza, restarão {len(dados_limpos)} registro(s) único(s).")
    
    confirmacao = input("Confirmar a remoção dos duplicados? O arquivo será sobrescrito. (S/N): ").strip().lower()
    
    if confirmacao == 's':
        salvar_dados(dados_limpos)
        print("Registros duplicados removidos com sucesso!")
    else:
        print("Limpeza cancelada.")

def pesquisar():
    # Lista de campos válidos para pesquisa
    campos_validos = [
        "texto", "reduzido", "ordinal", "hebraico", "quadrado_reduzido", 
        "quadrado_ordinal", "trigonal", "criacao", "quantidade_letras"
    ]
    
    # 1. Perguntar o Critério Primeiro
    print("\nEscolha o critério de pesquisa:")
    for i, campo in enumerate(campos_validos):
        nome_exibicao = campo.replace('_', ' ').title()
        print(f"{i+1}. {nome_exibicao}")
        
    criterio = None
    nome_criterio_exibicao = None
    while True:
        try:
            escolha = int(input(f"Digite o número do critério (1-{len(campos_validos)}): "))
            if 1 <= escolha <= len(campos_validos):
                criterio = campos_validos[escolha-1]
                nome_criterio_exibicao = criterio.replace('_', ' ').title()
                break
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

    # 2. Perguntar o Termo/Valor depois de escolher o critério
    termo = input(f"Digite o valor para \"{nome_criterio_exibicao}\" a pesquisar: ").strip()
            
    dados = carregar_dados()
    resultados_encontrados = []
    termo_lower = termo.lower() # Converter termo de pesquisa para minúsculas uma vez
    
    for item in dados:
        valor_item = item.get(criterio)
        if valor_item is None:
            continue
            
        valor_item_str_lower = str(valor_item).lower()

        if criterio == "texto":
            if termo_lower in valor_item_str_lower:
                resultados_encontrados.append(item)
        else:
            if valor_item_str_lower == termo_lower:
                resultados_encontrados.append(item)
    
    # Exibição dos resultados (mantida igual)
    if resultados_encontrados:
        print(f"\n--- {len(resultados_encontrados)} Resultado(s) Encontrado(s) para \"{termo}\" em \"{nome_criterio_exibicao}\" ---")
        for i, res in enumerate(resultados_encontrados):
            print(f"\n--- Registro {i+1} ---")
            print(f"  ID: {res.get('id', 'N/A')}")
            print(f"  Texto: {res.get('texto', 'N/A')}")
            max_len_campo = max(len(c.replace('_',' ')) for c in campos_validos[1:]) + 1
            for campo in campos_validos[1:]:
                nome_exibicao_res = campo.replace('_', ' ').title()
                print(f"  {nome_exibicao_res:<{max_len_campo}}: {res.get(campo, 'N/A')}") 
            print("-" * 45)
    else:
        print(f"\nNenhum resultado encontrado para \"{termo}\" em \"{nome_criterio_exibicao}\".")

def listar_todos_registros():
    """Lista todos os registros cadastrados no sistema"""
    dados = carregar_dados()
    
    if not dados:
        print("\nNão há registros cadastrados.")
        return
    
    # Lista de campos para exibição
    campos_validos = [
        "texto", "reduzido", "ordinal", "hebraico", "quadrado_reduzido", 
        "quadrado_ordinal", "trigonal", "criacao", "quantidade_letras"
    ]
    
    print(f"\nTotal de registros: {len(dados)}\n")
    
    # Cabeçalho
    print("ID | Texto | Reduz | Ord | Hebr | Q.Red | Q.Ord | Trig | Criacao | Letras")
    print("-" * 90)
    
    # Formatação compacta para caber todas as gematrias
    for item in dados:
        texto = item.get("texto", "")[:15]  # Limita o tamanho do texto para caber na linha
        texto_formatado = f"{texto:<15}"
        
        # Valores numéricos
        id_valor = item.get("id", "N/A")
        reduzido = item.get("reduzido", "N/A")
        ordinal = item.get("ordinal", "N/A")
        hebraico = item.get("hebraico", "N/A")
        q_reduzido = item.get("quadrado_reduzido", "N/A")
        q_ordinal = item.get("quadrado_ordinal", "N/A")
        trigonal = item.get("trigonal", "N/A")
        criacao = item.get("criacao", "N/A")
        letras = item.get("quantidade_letras", "N/A")
        
        print(f"{id_valor:2} | {texto_formatado} | {reduzido:4} | {ordinal:3} | {hebraico:4} | {q_reduzido:5} | {q_ordinal:5} | {trigonal:4} | {criacao:6} | {letras:2}")
    
    # Aguardar Enter para continuar
    input("\nPressione Enter para continuar...")

def menu_principal():
    while True:
        print("\n" + "="*40)
        print("GESTOR DE GEMATRIA".center(40))
        print("="*40)
        print("1. Adicionar novo registro")
        print("2. Pesquisar registros")
        print("3. Limpar registros duplicados")
        print("4. Listar todos os Registros")
        print("5. Sair")
        opcao = input("> ")
        
        if opcao == "1":
            adicionar_registro()
        elif opcao == "2":
            pesquisar()
        elif opcao == "3":
            limpar_registros_duplicados()
        elif opcao == "4":
            listar_todos_registros()
        elif opcao == "5":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu_principal()