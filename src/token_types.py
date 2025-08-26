# definições de tipos de tokens e funções auxiliares para o analisador léxico

# constantes para tipos de tokens
NUMERO = "NUMERO"
OPERADOR = "OPERADOR"
PARENTESE_ABRE = "PARENTESE_ABRE"
PARENTESE_FECHA = "PARENTESE_FECHA"
PALAVRA_RESERVADA = "PALAVRA_RESERVADA"
IDENTIFICADOR = "IDENTIFICADOR"

# conjuntos de caracteres válidos
OPERADORES_VALIDOS = {'+', '-', '*', '/', '%', '^'}
PALAVRAS_RESERVADAS = {'RES'}

def criar_token(tipo, valor, posicao=None):
    """
    cria um novo token
    
    Args:
        tipo (str): tipo do token
        valor (str): valor do token
        posicao (int, optional): posição do token no texto
        
    Returns:
        dict: dicionário representando o token
    """
    token = {
        'tipo': tipo,
        'valor': valor
    }
    if posicao is not None:
        token['posicao'] = posicao
    return token

def eh_operador_valido(char):
    """verifica se o caractere é um operador válido"""
    return char in OPERADORES_VALIDOS

def eh_palavra_reservada(palavra):
    """verifica se a palavra é uma palavra reservada"""
    return palavra.upper() in PALAVRAS_RESERVADAS

def eh_letra_maiuscula(char):
    """verifica se o caractere é uma letra maiúscula"""
    return char.isupper() and char.isalpha()

def eh_digito(char):
    """verifica se o caractere é um dígito"""
    return char.isdigit()

def eh_ponto_decimal(char):
    """verifica se o caractere é um ponto decimal"""
    return char == '.'

def eh_espaco(char):
    """verifica se o caractere é um espaço em branco"""
    return char.isspace()

def eh_parentese_abre(char):
    """verifica se o caractere é parêntese de abertura"""
    return char == '('

def eh_parentese_fecha(char):
    """verifica se o caractere é parêntese de fechamento"""
    return char == ')'