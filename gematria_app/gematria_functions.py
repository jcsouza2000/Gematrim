import re

# Tabela de valores Gematria baseada nas definições de gematria.py
GEMATRIA_TABLE = {
    "Reduzido": {
        "a": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "b": 2,
        "c": 3, "ç": 3,
        "d": 4,
        "e": 5, "é": 5, "ê": 5,
        "f": 6,
        "g": 7,
        "h": 8,
        "i": 9, "í": 9,
        "j": 1,
        "k": 2,
        "l": 3,
        "m": 4,
        "n": 5, "ñ": 5,
        "o": 6, "ó": 6, "ô": 6, "õ": 6, "ö": 6,
        "p": 7,
        "q": 8,
        "r": 9,
        "s": 1,
        "t": 2,
        "u": 3, "ú": 3, "ü": 3,
        "v": 4,
        "w": 5,
        "x": 6,
        "y": 7,
        "z": 8
    },
    "Ordinal": {
        "a": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "b": 2,
        "c": 3, "ç": 3,
        "d": 4,
        "e": 5, "é": 5, "ê": 5,
        "f": 6,
        "g": 7,
        "h": 8,
        "i": 9, "í": 9,
        "j": 10,
        "k": 11,
        "l": 12,
        "m": 13,
        "n": 14, "ñ": 14,
        "o": 15, "ó": 15, "ô": 15, "õ": 15, "ö": 15,
        "p": 16,
        "q": 17,
        "r": 18,
        "s": 19,
        "t": 20,
        "u": 21, "ú": 21, "ü": 21,
        "v": 22,
        "w": 23,
        "x": 24,
        "y": 25,
        "z": 26
    },
    "Hebraico": {
        "a": 1, "á": 1, "â": 1, "ã": 1, "à": 1, "ä": 1,
        "b": 2,
        "c": 3, "ç": 3,
        "d": 4,
        "e": 5, "é": 5, "ê": 5,
        "f": 6,
        "g": 7,
        "h": 8,
        "i": 9, "í": 9,
        "j": 10,
        "k": 20,
        "l": 30,
        "m": 40,
        "n": 50, "ñ": 50,
        "o": 60, "ó": 60, "ô": 60, "õ": 60, "ö": 60,
        "p": 70,
        "q": 80,
        "r": 90,
        "s": 100,
        "t": 200,
        "u": 300, "ú": 300, "ü": 300,
        "v": 400,
        "w": 500,
        "x": 600,
        "y": 700,
        "z": 800
    }
}

def calcular_reduzido(texto):
    """Calcula o valor reduzido usando a tabela de valores definida."""
    resultado = 0
    valores_letra = []
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Reduzido"].get(char, 0)
        resultado += valor
        if valor > 0:  # Só armazena valores de letras válidas
            valores_letra.append(valor)
    
    return resultado

def calcular_ordinal(texto):
    """Calcula o valor ordinal usando a tabela de valores definida."""
    resultado = 0
    valores_letra = []
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Ordinal"].get(char, 0)
        resultado += valor
        if valor > 0:  # Só armazena valores de letras válidas
            valores_letra.append(valor)
    
    return resultado

def calcular_hebraico(texto):
    """Calcula o valor hebraico usando a tabela de valores definida."""
    resultado = 0
    valores_letra = []
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Hebraico"].get(char, 0)
        resultado += valor
        if valor > 0:  # Só armazena valores de letras válidas
            valores_letra.append(valor)
    
    return resultado

def calcular_quadrado_reduzido(texto):
    """Calcula o valor quadrado reduzido (soma dos quadrados dos valores reduzidos)."""
    total = 0
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Reduzido"].get(char, 0)
        if valor > 0:  # Só considera letras válidas
            total += valor * valor
    
    return total

def calcular_quadrado_ordinal(texto):
    """Calcula o valor quadrado ordinal (soma dos quadrados dos valores ordinais)."""
    total = 0
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Ordinal"].get(char, 0)
        if valor > 0:  # Só considera letras válidas
            total += valor * valor
    
    return total

def calcular_trigonal(texto):
    """Calcula o valor trigonal (soma dos triangulares dos valores ordinais)."""
    total = 0
    
    for char in texto.lower():
        valor = GEMATRIA_TABLE["Ordinal"].get(char, 0)
        if valor > 0:  # Só considera letras válidas
            triangular = (valor * (valor + 1)) // 2
            total += triangular
    
    return total

def calcular_criacao(texto):
    """Calcula o valor de criação: (Ordinal * Qtd.Letras) + Qtd.Letras."""
    ordinal = calcular_ordinal(texto)
    qtd_letras = sum(1 for char in texto if char.isalpha())
    
    if qtd_letras > 0:
        return (ordinal * qtd_letras) + qtd_letras
    else:
        return 0 