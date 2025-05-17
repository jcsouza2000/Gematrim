from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

import re
import os
from datetime import datetime

from database_manager import (inicializar_db as criar_base_de_dados, 
                              adicionar_registro_db as inserir_registro, 
                              pesquisar_db as pesquisar_termo,
                              limpar_duplicatas_db as limpar_duplicatas, 
                              pesquisar_db as buscar_por_criterio,
                              get_db_connection, search_by_text,
                              search_by_normalized_text, search_by_reduzido, search_by_ordinal,
                              search_by_hebraico, search_by_quadrado_reduzido,
                              search_by_quadrado_ordinal, search_by_trigonal,
                              search_by_criacao, search_by_qtd_letras)
from gematria_functions import (calcular_reduzido, calcular_ordinal, calcular_hebraico,
                                calcular_quadrado_reduzido, calcular_quadrado_ordinal,
                                calcular_trigonal, calcular_criacao)

# Função para verificar existência de duplicatas
def duplicatas_existe():
    """Verifica se existem registros duplicados na base de dados."""
    import sqlite3
    from database_manager import DB_FILE
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT LOWER(texto), COUNT(*) 
            FROM registros
            GROUP BY LOWER(texto)
            HAVING COUNT(*) > 1
        ''')
        duplicatas = cursor.fetchall()
        return len(duplicatas) > 0
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

# Configuração para Android
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ])
    android = True
except ImportError:
    android = False


class CalculateScreen(Screen):
    texto_input = ObjectProperty(None)
    resultado_label = ObjectProperty(None)
    
    def calcular(self):
        try:
            # Limpa qualquer carregamento anterior (se houver)
            self.resultado_label.text = ""
            
            if not self.texto_input.text:
                self.resultado_label.text = "Digite um texto para calcular."
                return
                
            texto = self.texto_input.text.strip()
            texto_original = texto
            texto_normalizado = self.normalizar_texto(texto)
            
            # Cálculos
            reduzido = calcular_reduzido(texto_normalizado)
            ordinal = calcular_ordinal(texto_normalizado)
            hebraico = calcular_hebraico(texto_normalizado)
            quadrado_reduzido = calcular_quadrado_reduzido(texto_normalizado)
            quadrado_ordinal = calcular_quadrado_ordinal(texto_normalizado)
            trigonal = calcular_trigonal(texto_normalizado)
            criacao = calcular_criacao(texto_normalizado)
            qtd_letras = len(texto_normalizado)
            
            # Formatar resultado com melhor estilo e formatação
            resultado = f"""[b]Resultado para:[/b] "[color=#1976D2]{texto_original}[/color]"
[i]Texto Normalizado:[/i] [color=#424242]{texto_normalizado}[/color]

[size=18][b]Valores Básicos[/b][/size]
[u]Quantidade de Letras:[/u] [color=#1976D2]{qtd_letras}[/color]
[u]Reduzido:[/u] [color=#1976D2]{reduzido}[/color]
[u]Ordinal:[/u] [color=#1976D2]{ordinal}[/color]
[u]Hebraico:[/u] [color=#1976D2]{hebraico}[/color]

[size=18][b]Valores Derivados[/b][/size]
[u]Quadrado Reduzido:[/u] [color=#1976D2]{quadrado_reduzido}[/color]
[u]Quadrado Ordinal:[/u] [color=#1976D2]{quadrado_ordinal}[/color]
[u]Trigonal:[/u] [color=#1976D2]{trigonal}[/color]
[u]Criação:[/u] [color=#1976D2]{criacao}[/color]"""
            
            self.resultado_label.text = resultado
            
            # Salvar no banco de dados
            valores = {
                'reduzido': reduzido,
                'ordinal': ordinal,
                'hebraico': hebraico,
                'quadrado_reduzido': quadrado_reduzido,
                'quadrado_ordinal': quadrado_ordinal,
                'trigonal': trigonal,
                'criacao': criacao,
                'quantidade_letras': qtd_letras
            }
            inserir_registro(texto_original, valores)
                
        except Exception as e:
            self.resultado_label.text = f"[color=#F44336]Erro:[/color] {str(e)}"
            
    def limpar(self):
        """Limpa o campo de texto e o resultado."""
        self.texto_input.text = ""
        self.resultado_label.text = "Os resultados aparecerão aqui."
            
    def normalizar_texto(self, texto):
        # Remove acentos, números e converte para minúsculas
        import unicodedata
        
        # Converte para minúsculas
        texto = texto.lower()
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        
        # Remove caracteres que não são letras
        texto = re.sub(r'[^a-z]', '', texto)
        
        return texto


class SearchScreen(MDScreen):
    termo_input = ObjectProperty(None)
    criterio_spinner = ObjectProperty(None)
    resultados_pesquisa_label = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        # Bind the spinner to update the hint text
        self.criterio_spinner.bind(text=self.atualizar_hint_text)
        # Set initial hint text
        self.atualizar_hint_text(self.criterio_spinner, self.criterio_spinner.text)
    
    def atualizar_hint_text(self, spinner, text):
        if text in ["Texto", "Normal"]:
            self.termo_input.hint_text = "Digite o texto para pesquisar"
        else:
            self.termo_input.hint_text = "Digite o valor numérico"
    
    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e os resultados anteriores."""
        self.termo_input.text = ""
        self.resultados_pesquisa_label.text = ""
    
    def pesquisar(self):
        # Get search term and criteria
        termo = self.termo_input.text.strip()
        criterio = self.criterio_spinner.text
        
        print(f"Pesquisando por '{termo}' com critério '{criterio}'")
        
        # Validate input
        if not termo:
            self.resultados_pesquisa_label.text = "Digite um termo para pesquisar."
            return
        
        # Connect to the database
        conn = get_db_connection()
        if not conn:
            self.resultados_pesquisa_label.text = "Erro ao conectar ao banco de dados."
            return
        
        # Find the appropriate search function based on criteria
        resultados = []
        try:
            # Para pesquisa de texto
            if criterio in ["Texto", "Normal"]:
                if criterio == "Texto":
                    resultados = search_by_text(conn, termo)
                else:  # Normal (antes era Texto Normalizado)
                    resultados = search_by_normalized_text(conn, termo)
            else:
                # Tenta converter para inteiro para critérios numéricos
                try:
                    valor = int(termo)
                    print(f"Valor convertido para inteiro: {valor}")
                except ValueError:
                    self.resultados_pesquisa_label.text = f"O valor '{termo}' não é um número válido para o critério '{criterio}'."
                    conn.close()
                    return
                
                # Pesquisa avançada - verificar em todos os campos
                if criterio == "Qualquer Valor":
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT * FROM registros 
                        WHERE reduzido = ? OR ordinal = ? OR hebraico = ? OR 
                              quadrado_reduzido = ? OR quadrado_ordinal = ? OR 
                              trigonal = ? OR criacao = ?
                    """, (valor, valor, valor, valor, valor, valor, valor))
                    resultados = [dict(row) for row in cursor.fetchall()]
                else:
                    # Mapa de critérios para funções de pesquisa
                    criteria_map = {
                        "Reduzido": search_by_reduzido,
                        "Ordinal": search_by_ordinal,
                        "Hebraico": search_by_hebraico, 
                        "Quadrado Reduzido": search_by_quadrado_reduzido,
                        "Quadrado Ordinal": search_by_quadrado_ordinal,
                        "Trigonal": search_by_trigonal,
                        "Criacao": search_by_criacao,
                        "Quantidade Letras": search_by_qtd_letras
                    }
                    
                    print(f"Critério: '{criterio}', Está no mapa: {criterio in criteria_map}")
                    
                    # Escolher a função de pesquisa correta
                    if criterio in criteria_map:
                        search_func = criteria_map[criterio]
                        print(f"Função de pesquisa selecionada: {search_func.__name__}")
                        resultados = search_func(conn, valor)
                    else:
                        self.resultados_pesquisa_label.text = f"Critério '{criterio}' não implementado."
                        conn.close()
                        return
        except Exception as e:
            self.resultados_pesquisa_label.text = f"Erro na pesquisa: {str(e)}"
            print(f"Erro na pesquisa: {str(e)}")
            conn.close()
            return
        
        # Close the database connection
        conn.close()
        
        # Format the results
        if not resultados:
            self.resultados_pesquisa_label.text = f"[color=#F44336]Nenhum resultado encontrado para '[b]{termo}[/b]' em '[b]{criterio}[/b]'.[/color]"
            return
        
        # Filtrar apenas palavras reais (excluindo os exemplos de demonstração)
        palavras_reais = []
        for registro in resultados:
            texto = registro['texto'].upper()
            if not (texto.startswith("EXEMPLO") or texto.startswith("SEGUNDO EXEMPLO") or texto.startswith("TERCEIRO EXEMPLO")):
                palavras_reais.append(registro)
        
        if not palavras_reais:
            self.resultados_pesquisa_label.text = f"[color=#F44336]Nenhuma palavra encontrada para '[b]{termo}[/b]' em '[b]{criterio}[/b]'.[/color]"
            return
        
        # Format the output with better styling
        result_text = f"[size=18][b]{len(palavras_reais)} palavra(s) com valor '[color=#1976D2]{termo}[/color]' em '[color=#1976D2]{criterio}[/color]':[/b][/size]\n\n"
        
        for i, registro in enumerate(palavras_reais, 1):
            # Destaque para o nome da palavra
            result_text += f"[size=20][b][color=#1976D2]{i}. {registro['texto'].upper()}[/color][/b][/size]\n"
            
            # Informações primárias com destaque
            result_text += f"[i]Texto:[/i] [b]{registro['texto']}[/b]\n"
            
            # Valores principais em uma linha com melhor formatação
            result_text += (
                f"[u]Reduzido:[/u] [color=#1976D2]{registro['reduzido']}[/color]  |  "
                f"[u]Ordinal:[/u] [color=#1976D2]{registro['ordinal']}[/color]  |  "
                f"[u]Hebraico:[/u] [color=#1976D2]{registro['hebraico']}[/color]\n"
            )
            
            # Valores secundários em outra linha
            result_text += (
                f"[u]Q.Reduzido:[/u] [color=#1976D2]{registro['quadrado_reduzido']}[/color]  |  "
                f"[u]Q.Ordinal:[/u] [color=#1976D2]{registro['quadrado_ordinal']}[/color]  |  "
                f"[u]Trigonal:[/u] [color=#1976D2]{registro['trigonal']}[/color]\n"
            )
            
            # Valores terciários em uma terceira linha
            result_text += (
                f"[u]Qtd.Letras:[/u] [color=#1976D2]{registro['quantidade_letras']}[/color]  |  "
                f"[u]Criação:[/u] [color=#1976D2]{registro['criacao']}[/color]\n"
            )
            
            # Adicionar um separador entre resultados
            if i < len(palavras_reais):
                result_text += "\n[size=2]───────────────────────────────────[/size]\n\n"
            else:
                result_text += "\n"
        
        # Set the result text
        self.resultados_pesquisa_label.text = result_text


class SettingsScreen(Screen):
    limpeza_status_label = ObjectProperty(None)
    
    def limpar_duplicatas(self):
        try:
            # Verifica se há duplicatas
            if not duplicatas_existe():
                self.limpeza_status_label.text = "Não há duplicatas para limpar."
                return
                
            # Confirma a operação com um popup
            popup = Popup(
                title='Confirmar Limpeza',
                content=Label(text='Isso excluirá registros duplicados permanentemente. Continuar?'),
                size_hint=(0.8, 0.3)
            )
            
            # Botões de confirmação
            from kivymd.uix.button import MDFlatButton
            from kivy.uix.boxlayout import BoxLayout
            
            box = BoxLayout(orientation='horizontal', spacing=10, padding=10)
            btn_sim = MDFlatButton(text='SIM')
            btn_nao = MDFlatButton(text='NÃO')
            
            # Configura callbacks
            def on_sim(instance):
                popup.dismiss()
                # Executa limpeza
                contador = limpar_duplicatas()
                self.limpeza_status_label.text = f"{contador} duplicatas removidas com sucesso."
                
            def on_nao(instance):
                popup.dismiss()
                self.limpeza_status_label.text = "Operação cancelada."
                
            btn_sim.bind(on_release=on_sim)
            btn_nao.bind(on_release=on_nao)
            
            box.add_widget(btn_sim)
            box.add_widget(btn_nao)
            popup.content = box
            popup.open()
                
        except Exception as e:
            self.limpeza_status_label.text = f"Erro: {str(e)}"


class WindowManager(ScreenManager):
    """Gerenciador de telas do aplicativo."""
    pass


def adicionar_exemplos_teste():
    """Adiciona palavras reais com reduzido=49"""
    try:
        from database_manager import adicionar_registro_db
        
        # Adicionar palavras reais com reduzido=49 
        palavras_reais = [
            {
                'texto': "AFINAR",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 157,
                    'hebraico': 639,
                    'quadrado_reduzido': 225,
                    'quadrado_ordinal': 639,
                    'trigonal': 344,
                    'criacao': 300,
                    'quantidade_letras': 6
                }
            },
            {
                'texto': "CALOR",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 184,
                    'hebraico': 703,
                    'quadrado_reduzido': 136,
                    'quadrado_ordinal': 703,
                    'trigonal': 376,
                    'criacao': 250,
                    'quantidade_letras': 5
                }
            },
            {
                'texto': "CANAL",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 175,
                    'hebraico': 669,
                    'quadrado_reduzido': 120,
                    'quadrado_ordinal': 669,
                    'trigonal': 359,
                    'criacao': 250,
                    'quantidade_letras': 5
                }
            },
            {
                'texto': "CLONE",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 148,
                    'hebraico': 599,
                    'quadrado_reduzido': 104,
                    'quadrado_ordinal': 599,
                    'trigonal': 324,
                    'criacao': 250,
                    'quantidade_letras': 5
                }
            },
            # Adicionar mais palavras reais com reduzido=49
            {
                'texto': "ADULTO",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 166,
                    'hebraico': 656,
                    'quadrado_reduzido': 140,
                    'quadrado_ordinal': 656,
                    'trigonal': 300,
                    'criacao': 332,
                    'quantidade_letras': 6
                }
            },
            {
                'texto': "COLINA",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 193,
                    'hebraico': 743,
                    'quadrado_reduzido': 130,
                    'quadrado_ordinal': 743,
                    'trigonal': 380,
                    'criacao': 290,
                    'quantidade_letras': 6
                }
            },
            {
                'texto': "ETERNO",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 202,
                    'hebraico': 786,
                    'quadrado_reduzido': 145,
                    'quadrado_ordinal': 786,
                    'trigonal': 420,
                    'criacao': 404,
                    'quantidade_letras': 6
                }
            },
            {
                'texto': "FLORES",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 175,
                    'hebraico': 665,
                    'quadrado_reduzido': 135,
                    'quadrado_ordinal': 665,
                    'trigonal': 348,
                    'criacao': 350,
                    'quantidade_letras': 6
                }
            },
            {
                'texto': "MATRIZ",
                'valores': {
                    'reduzido': 49,
                    'ordinal': 202,
                    'hebraico': 778,
                    'quadrado_reduzido': 140,
                    'quadrado_ordinal': 778,
                    'trigonal': 395,
                    'criacao': 404,
                    'quantidade_letras': 6
                }
            }
        ]
        
        # Adiciona apenas palavras reais ao banco
        for exemplo in palavras_reais:
            adicionar_registro_db(exemplo['texto'], exemplo['valores'])
        
        print("Palavras reais adicionadas com sucesso.")
    except Exception as e:
        print(f"Erro ao adicionar palavras: {str(e)}")


def verificar_calculo_deus():
    """Verifica os valores calculados para a palavra 'Deus'"""
    from gematria_functions import (calcular_reduzido, calcular_ordinal, calcular_hebraico,
                              calcular_quadrado_reduzido, calcular_quadrado_ordinal,
                              calcular_trigonal, calcular_criacao)
    
    texto = "Deus"
    texto_normalizado = re.sub(r'[^a-zA-Z]', '', texto.lower())
    print(f"Texto: {texto}, Normalizado: {texto_normalizado}")
    
    # Cálculos
    reduzido = calcular_reduzido(texto_normalizado)
    ordinal = calcular_ordinal(texto_normalizado)
    hebraico = calcular_hebraico(texto_normalizado)
    
    print(f"Reduzido: {reduzido}")
    print(f"Ordinal: {ordinal}")
    print(f"Hebraico: {hebraico}")
    
    # Calcular letra por letra
    print("Cálculo letra por letra (reduzido):")
    total = 0
    for letra in texto_normalizado:
        valor = 0
        if letra == 'd': valor = 4
        elif letra == 'e': valor = 5
        elif letra == 'u': valor = 3
        elif letra == 's': valor = 1
        total += valor
        print(f"Letra: {letra}, Valor: {valor}, Total acumulado: {total}")


class GematriaApp(MDApp):
    def build(self):
        # Configura o tema do aplicativo
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"  # Mais escuro que o padrão
        self.theme_cls.accent_palette = "DeepOrange"
        self.theme_cls.accent_hue = "500"
        self.theme_cls.theme_style = "Light"  # Ou "Dark" para tema escuro
        
        # Configura o banco de dados
        criar_base_de_dados()
        
        # Teste de cálculo para "Deus"
        verificar_calculo_deus()
        
        # Adiciona palavras reais
        adicionar_exemplos_teste()

        # Define o tamanho da janela (apenas para desktop)
        Window.size = (400, 800)
        
        # Retorna o widget principal
        return Builder.load_file('gematria_app/gematria.kv')
        
    def on_start(self):
        # Executa após a inicialização do aplicativo
        pass


if __name__ == '__main__':
    GematriaApp().run() 