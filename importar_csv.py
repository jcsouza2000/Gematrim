import csv
import sqlite3
import os
import sys

def importar_csv_para_db(arquivo_csv, arquivo_db="gematria.db"):
    """
    Importa dados de um arquivo CSV para o banco de dados da aplicação Gematria.
    
    O arquivo CSV deve ter os seguintes cabeçalhos:
    texto,reduzido,ordinal,hebraico,quadrado_reduzido,quadrado_ordinal,trigonal,criacao,quantidade_letras
    
    Args:
        arquivo_csv (str): Caminho para o arquivo CSV a ser importado
        arquivo_db (str): Caminho para o banco de dados SQLite
    """
    
    # Verificar se o arquivo CSV existe
    if not os.path.exists(arquivo_csv):
        print(f"Erro: Arquivo CSV '{arquivo_csv}' não encontrado.")
        return False
    
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
        
        # Obter contagem de registros antes da importação
        cursor.execute("SELECT COUNT(*) FROM registros")
        registros_antes = cursor.fetchone()[0]
        print(f"Registros no banco de dados antes da importação: {registros_antes}")
        
        # Limpando o arquivo CSV para corrigir problemas comuns
        print("Verificando e corrigindo problemas de formatação no CSV...")
        
        # Criar arquivo temporário corrigido
        arquivo_temp = arquivo_csv + ".temp"
        
        # Ler o arquivo original e corrigir problemas
        with open(arquivo_csv, 'rb') as file_in:
            # Verificar e remover BOM
            conteudo = file_in.read()
            if conteudo.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                conteudo = conteudo[3:]
                print("BOM UTF-8 detectado e removido.")
            
            # Decodificar para texto
            texto = conteudo.decode('utf-8')
            
            # Dividir em linhas
            linhas = texto.split('\n')
            
            # Corrigir cabeçalhos e linhas
            if linhas:
                # Corrigir cabeçalho
                cabecalho = linhas[0].strip()
                if cabecalho.endswith(','):
                    cabecalho = cabecalho[:-1]
                
                # Escrever arquivo corrigido
                with open(arquivo_temp, 'w', encoding='utf-8', newline='') as file_out:
                    file_out.write(cabecalho + '\n')
                    
                    # Processar demais linhas
                    for linha in linhas[1:]:
                        linha = linha.strip()
                        if not linha:  # Pular linhas vazias
                            continue
                        # Remover vírgula extra no final, se existir
                        if linha.endswith(','):
                            linha = linha[:-1]
                        file_out.write(linha + '\n')
        
        print("Arquivo temporário corrigido criado.")
        
        # Mapear cabeçalhos customizados se necessário
        mapeamento_colunas = {
            '\ufefftexto': 'texto',  # Correção para BOM
            'texto': 'texto',
            'reduzido': 'reduzido',
            'ordinal': 'ordinal',
            'hebraico': 'hebraico',
            'quadrado_reduzido': 'quadrado_reduzido',
            'quadrado_ordinal': 'quadrado_ordinal',
            'trigonal': 'trigonal',
            'criacao': 'criacao',
            'quantidade_letras': 'quantidade_letras'
        }
        
        # Ler arquivo CSV corrigido
        with open(arquivo_temp, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # Verificar cabeçalhos obrigatórios
            campos_obrigatorios = [
                'texto', 'reduzido', 'ordinal', 'hebraico', 
                'quadrado_reduzido', 'quadrado_ordinal', 'trigonal', 
                'criacao', 'quantidade_letras'
            ]
            
            if not csv_reader.fieldnames:
                print("Erro: Não foi possível ler os cabeçalhos do arquivo CSV.")
                conn.close()
                os.remove(arquivo_temp)
                return False
            
            print(f"Cabeçalhos encontrados: {csv_reader.fieldnames}")
            
            # Verificar se há campos em falta ou com nomes alternativos
            campos_faltando = []
            for campo in campos_obrigatorios:
                campo_encontrado = False
                
                # Verificar o campo diretamente ou em nosso mapeamento
                for cabecalho in csv_reader.fieldnames:
                    if cabecalho == campo or mapeamento_colunas.get(cabecalho) == campo:
                        campo_encontrado = True
                        break
                
                if not campo_encontrado:
                    campos_faltando.append(campo)
            
            if campos_faltando:
                print(f"Erro: As seguintes colunas obrigatórias não foram encontradas: {campos_faltando}")
                conn.close()
                os.remove(arquivo_temp)
                return False
            
            # Inserir registros
            registros_inseridos = 0
            registros_atualizados = 0
            registros_ignorados = 0
            
            for linha in csv_reader:
                try:
                    # Usar mapeamento para acessar valores com cabeçalhos corretos
                    def obter_valor(campo):
                        # Tentar obter diretamente
                        if campo in linha:
                            return linha[campo]
                        # Tentar através do mapeamento
                        for key, value in mapeamento_colunas.items():
                            if value == campo and key in linha:
                                return linha[key]
                        return None
                    
                    # Preparar dados para inserção
                    texto_valor = obter_valor('texto')
                    if not texto_valor:
                        print("Aviso: Texto vazio ou ausente. Linha ignorada.")
                        registros_ignorados += 1
                        continue
                    
                    texto = texto_valor.strip()
                    
                    # Verificar se texto não está vazio
                    if not texto:
                        registros_ignorados += 1
                        continue
                    
                    # Converter campos numéricos para inteiros
                    try:
                        dados = (
                            texto,
                            int(obter_valor('reduzido') or 0),
                            int(obter_valor('ordinal') or 0),
                            int(obter_valor('hebraico') or 0),
                            int(obter_valor('quadrado_reduzido') or 0),
                            int(obter_valor('quadrado_ordinal') or 0),
                            int(obter_valor('trigonal') or 0),
                            int(obter_valor('criacao') or 0),
                            int(obter_valor('quantidade_letras') or 0)
                        )
                    except ValueError as ve:
                        print(f"Aviso: Valor numérico inválido na linha para texto '{texto}': {ve}")
                        print(f"Valores da linha: {linha}")
                        registros_ignorados += 1
                        continue
                    
                    # Verificar se o registro já existe
                    cursor.execute("SELECT id FROM registros WHERE texto=?", (texto,))
                    registro_existente = cursor.fetchone()
                    
                    if registro_existente:
                        # Atualizar registro existente
                        cursor.execute("""
                            UPDATE registros SET 
                            reduzido=?, ordinal=?, hebraico=?, 
                            quadrado_reduzido=?, quadrado_ordinal=?, trigonal=?,
                            criacao=?, quantidade_letras=?
                            WHERE texto=?
                        """, (
                            int(obter_valor('reduzido') or 0),
                            int(obter_valor('ordinal') or 0),
                            int(obter_valor('hebraico') or 0),
                            int(obter_valor('quadrado_reduzido') or 0),
                            int(obter_valor('quadrado_ordinal') or 0),
                            int(obter_valor('trigonal') or 0),
                            int(obter_valor('criacao') or 0),
                            int(obter_valor('quantidade_letras') or 0),
                            texto
                        ))
                        registros_atualizados += 1
                    else:
                        # Inserir novo registro
                        cursor.execute("""
                            INSERT INTO registros (
                                texto, reduzido, ordinal, hebraico, 
                                quadrado_reduzido, quadrado_ordinal, trigonal,
                                criacao, quantidade_letras
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, dados)
                        registros_inseridos += 1
                    
                    # Commit a cada 100 registros para evitar perda em caso de erro
                    if (registros_inseridos + registros_atualizados) % 100 == 0:
                        conn.commit()
                        print(f"Progresso: {registros_inseridos + registros_atualizados} registros processados...")
                    
                except Exception as e:
                    print(f"Erro ao processar registro para '{texto}': {str(e)}")
                    registros_ignorados += 1
            
            # Commit final das alterações
            conn.commit()
            
            # Obter contagem de registros após importação
            cursor.execute("SELECT COUNT(*) FROM registros")
            registros_depois = cursor.fetchone()[0]
            
            # Mostrar resumo da importação
            print("\nResumo da importação:")
            print(f"Registros inseridos: {registros_inseridos}")
            print(f"Registros atualizados: {registros_atualizados}")
            print(f"Registros ignorados: {registros_ignorados}")
            print(f"Total de registros no banco de dados: {registros_depois}")
            print(f"Diferença após a importação: {registros_depois - registros_antes}")
            
            # Remover arquivo temporário
            os.remove(arquivo_temp)
            print("Arquivo temporário removido.")
            
            return True
            
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro não esperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def criar_template_csv(arquivo_saida="template_gematria.csv"):
    """Cria um arquivo CSV de exemplo com os cabeçalhos corretos."""
    try:
        with open(arquivo_saida, 'w', encoding='utf-8', newline='') as csv_file:
            campos = [
                'texto', 'reduzido', 'ordinal', 'hebraico', 
                'quadrado_reduzido', 'quadrado_ordinal', 'trigonal', 
                'criacao', 'quantidade_letras'
            ]
            
            writer = csv.DictWriter(csv_file, fieldnames=campos)
            writer.writeheader()
            
            # Adicionar alguns exemplos
            writer.writerow({
                'texto': 'Exemplo',
                'reduzido': 23,
                'ordinal': 95,
                'hebraico': 410,
                'quadrado_reduzido': 179,
                'quadrado_ordinal': 3025,
                'trigonal': 285,
                'criacao': 665,
                'quantidade_letras': 7
            })
            
            writer.writerow({
                'texto': 'Teste',
                'reduzido': 13,
                'ordinal': 67,
                'hebraico': 360,
                'quadrado_reduzido': 45,
                'quadrado_ordinal': 1175,
                'trigonal': 135,
                'criacao': 335,
                'quantidade_letras': 5
            })
        
        print(f"Template CSV criado com sucesso: {arquivo_saida}")
        return True
    
    except Exception as e:
        print(f"Erro ao criar template CSV: {str(e)}")
        return False


if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--template":
            # Criar template CSV
            nome_arquivo = "template_gematria.csv"
            if len(sys.argv) > 2:
                nome_arquivo = sys.argv[2]
            criar_template_csv(nome_arquivo)
        else:
            # Importar arquivo CSV especificado
            arquivo_csv = sys.argv[1]
            importar_csv_para_db(arquivo_csv)
    else:
        print("Uso:")
        print("  Para importar dados: python importar_csv.py arquivo.csv")
        print("  Para criar template: python importar_csv.py --template [nome_arquivo.csv]") 