# definição de estruturas de controle em notação pós-fixa

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class ControlStructureError(Exception):
    """exceção para erros nas estruturas de controle"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(f"Erro na estrutura de controle: {mensagem}")

def definir_sintaxe_controle():
    """
    retorna especificação das estruturas de controle
    
    Returns:
        dict: especificação com sintaxe e exemplos
    """
    return {
        'decisao': {
            'nome': 'IF',
            'sintaxe': '(operando1 operando2 operador_rel (bloco_verdadeiro) (bloco_falso) IF)',
            'descricao': 'estrutura de decisão condicional',
            'exemplos': [
                '((A B >) ((A) PRINT) ((B) PRINT) IF)',
                '((X 0 ==) ((0)) ((X)) IF)'
            ]
        },
        'laco': {
            'nome': 'WHILE',
            'sintaxe': '(operando1 operando2 operador_rel (bloco_repeticao) WHILE)',
            'descricao': 'laço de repetição condicional',
            'exemplos': [
                '((CONT 10 <) ((CONT 1 +) CONT) WHILE)',
                '((I 0 >) ((I 1 -) I) WHILE)'
            ]
        },
        'operadores_relacionais': {
            'maior': '>',
            'menor': '<',
            'igual': '==',
            'diferente': '!=',
            'maior_igual': '>=',
            'menor_igual': '<='
        }
    }

def criar_token_decisao(condicao, bloco_verdadeiro, bloco_falso):
    """
    cria token para estrutura IF
    
    Args:
        condicao (dict): estrutura da condição
        bloco_verdadeiro (list): tokens do bloco verdadeiro
        bloco_falso (list): tokens do bloco falso
        
    Returns:
        dict: token da decisão
    """
    if not validar_condicao(condicao):
        raise ControlStructureError("Condição inválida para IF")
    
    if not validar_bloco(bloco_verdadeiro):
        raise ControlStructureError("Bloco verdadeiro inválido")
    
    if not validar_bloco(bloco_falso):
        raise ControlStructureError("Bloco falso inválido")
    
    return {
        'tipo': 'DECISAO',
        'condicao': condicao,
        'bloco_verdadeiro': bloco_verdadeiro,
        'bloco_falso': bloco_falso
    }

def criar_token_laco(condicao, bloco_repeticao):
    """
    cria token para estrutura WHILE
    
    Args:
        condicao (dict): estrutura da condição
        bloco_repeticao (list): tokens do bloco
        
    Returns:
        dict: token do laço
    """
    if not validar_condicao(condicao):
        raise ControlStructureError("Condição inválida para WHILE")
    
    if not validar_bloco(bloco_repeticao):
        raise ControlStructureError("Bloco de repetição inválido")
    
    return {
        'tipo': 'LACO',
        'condicao': condicao,
        'bloco': bloco_repeticao
    }

def validar_condicao(condicao):
    """
    valida estrutura de condição
    
    Args:
        condicao (dict ou list): estrutura da condição
        
    Returns:
        bool: True se válida
    """
    if condicao is None:
        return False
    
    # condição como dict
    if isinstance(condicao, dict):
        if 'operando1' not in condicao or 'operando2' not in condicao:
            return False
        if 'operador' not in condicao:
            return False
        
        # validar operador relacional
        operadores_validos = ['>', '<', '==', '!=', '>=', '<=']
        return condicao['operador'] in operadores_validos
    
    # condição como lista de tokens
    if isinstance(condicao, list):
        if len(condicao) < 3:
            return False
        
        # deve ter: operando operando operador_relacional
        return True
    
    return False

def validar_bloco(bloco):
    """
    valida estrutura de bloco de comandos
    
    Args:
        bloco (list): lista de tokens do bloco
        
    Returns:
        bool: True se válido
    """
    if not isinstance(bloco, list):
        return False
    
    if len(bloco) == 0:
        return False
    
    # bloco deve começar e terminar com parênteses
    if isinstance(bloco, list) and len(bloco) > 0:
        # verificar estrutura básica
        return True
    
    return False

def gerar_exemplo_decisao():
    """
    gera exemplo de estrutura IF
    
    Returns:
        str: exemplo formatado
    """
    sintaxe = definir_sintaxe_controle()
    
    exemplo = f"""
Estrutura de Decisão (IF):
==========================

Sintaxe: {sintaxe['decisao']['sintaxe']}

Descrição: {sintaxe['decisao']['descricao']}

Exemplos:
"""
    
    for i, ex in enumerate(sintaxe['decisao']['exemplos'], 1):
        exemplo += f"{i}. {ex}\n"
    
    return exemplo

def gerar_exemplo_laco():
    """
    gera exemplo de estrutura WHILE
    
    Returns:
        str: exemplo formatado
    """
    sintaxe = definir_sintaxe_controle()
    
    exemplo = f"""
Estrutura de Laço (WHILE):
==========================

Sintaxe: {sintaxe['laco']['sintaxe']}

Descrição: {sintaxe['laco']['descricao']}

Exemplos:
"""
    
    for i, ex in enumerate(sintaxe['laco']['exemplos'], 1):
        exemplo += f"{i}. {ex}\n"
    
    return exemplo

def converter_condicao_para_tokens(operando1, operando2, operador):
    """
    converte condição em lista de tokens
    
    Args:
        operando1 (str): primeiro operando
        operando2 (str): segundo operando
        operador (str): operador relacional
        
    Returns:
        list: tokens da condição
    """
    tokens = []
    
    # determinar tipo do operando1
    if operando1.replace('.', '').replace('-', '').isdigit():
        tokens.append({'tipo': NUMERO, 'valor': operando1})
    else:
        tokens.append({'tipo': IDENTIFICADOR, 'valor': operando1})
    
    # determinar tipo do operando2
    if operando2.replace('.', '').replace('-', '').isdigit():
        tokens.append({'tipo': NUMERO, 'valor': operando2})
    else:
        tokens.append({'tipo': IDENTIFICADOR, 'valor': operando2})
    
    # adicionar operador relacional
    tokens.append({'tipo': OPERADOR_RELACIONAL, 'valor': operador})
    
    return tokens

if __name__ == '__main__':
    # teste das estruturas de controle
    print("=== ESTRUTURAS DE CONTROLE ===\n")
    
    print(gerar_exemplo_decisao())
    print(gerar_exemplo_laco())
    
    # testar validação
    print("\nTeste de Validação:")
    print("==================\n")
    
    # condição válida
    condicao_valida = {
        'operando1': {'tipo': 'NUMERO', 'valor': '5'},
        'operando2': {'tipo': 'NUMERO', 'valor': '10'},
        'operador': '>'
    }
    print(f"Condição válida: {validar_condicao(condicao_valida)}")
    
    # condição inválida
    condicao_invalida = {
        'operando1': {'tipo': 'NUMERO', 'valor': '5'}
    }
    print(f"Condição inválida: {validar_condicao(condicao_invalida)}")
    
    # bloco válido
    bloco_valido = [
        {'tipo': PARENTESE_ABRE, 'valor': '('},
        {'tipo': NUMERO, 'valor': '1'},
        {'tipo': PARENTESE_FECHA, 'valor': ')'}
    ]
    print(f"Bloco válido: {validar_bloco(bloco_valido)}")
    
    # bloco inválido
    bloco_invalido = []
    print(f"Bloco inválido: {validar_bloco(bloco_invalido)}")