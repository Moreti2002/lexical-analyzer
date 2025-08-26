"""
testes para o analisador léxico
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import parse_expressao, LexerError
from src.token_types import *

def assert_tokens_iguais(tokens_obtidos, tokens_esperados):
    """Compara listas de tokens ignorando posição"""
    assert len(tokens_obtidos) == len(tokens_esperados)
    for obtido, esperado in zip(tokens_obtidos, tokens_esperados):
        assert obtido['tipo'] == esperado['tipo']
        assert obtido['valor'] == esperado['valor']

def teste_expressao_simples():
    """teste básico de expressão simples"""
    tokens = parse_expressao("(3.14 2.0 +)")
    esperados = [
        {'tipo': PARENTESE_ABRE, 'valor': '('},
        {'tipo': NUMERO, 'valor': '3.14'},
        {'tipo': NUMERO, 'valor': '2.0'},
        {'tipo': OPERADOR, 'valor': '+'},
        {'tipo': PARENTESE_FECHA, 'valor': ')'}
    ]
    assert_tokens_iguais(tokens, esperados)

def teste_todos_operadores():
    """teste com todos os operadores"""
    for op in ['+', '-', '*', '/', '%', '^']:
        tokens = parse_expressao(f"(1 2 {op})")
        assert tokens[3]['tipo'] == OPERADOR
        assert tokens[3]['valor'] == op

def teste_numeros():
    """teste com diferentes tipos de números"""
    tokens = parse_expressao("(5 3.14 +)")
    assert tokens[1]['valor'] == '5'
    assert tokens[2]['valor'] == '3.14'

def teste_palavra_reservada():
    """teste palavra reservada RES"""
    tokens = parse_expressao("(5 RES)")
    assert tokens[2]['tipo'] == PALAVRA_RESERVADA
    assert tokens[2]['valor'] == 'RES'

def teste_identificador():
    """teste identificadores"""
    tokens = parse_expressao("(10.5 MEM)")
    assert tokens[2]['tipo'] == IDENTIFICADOR
    assert tokens[2]['valor'] == 'MEM'

def teste_expressao_aninhada():
    """teste expressão aninhada"""
    tokens = parse_expressao("((1.5 2.0 *) (3.0 4.0 *) /)")
    assert len(tokens) == 13
    assert tokens[0]['tipo'] == PARENTESE_ABRE
    assert tokens[-1]['tipo'] == PARENTESE_FECHA

def teste_erro_operador_invalido():
    """teste operador inválido"""
    try:
        parse_expressao("(3.14 2.0 &)")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

def teste_erro_numero_malformado():
    """teste número malformado"""
    try:
        parse_expressao("(3.14.5 2.0 +)")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

def teste_erro_parenteses_desbalanceados():
    """teste parênteses desbalanceados"""
    try:
        parse_expressao("((3.14 2.0 +)")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

def teste_erro_linha_vazia():
    """teste linha vazia"""
    try:
        parse_expressao("")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

def teste_erro_virgula_decimal():
    """teste vírgula no lugar do ponto"""
    try:
        parse_expressao("(3,45 2.0 +)")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

def teste_erro_numero_termina_ponto():
    """teste número terminado em ponto"""
    try:
        parse_expressao("(3. 2.0 +)")
        assert False, "Deveria ter dado erro"
    except LexerError:
        pass

class TesteLexer(unittest.TestCase):
    """testes para o analisador léxico"""
    
    def teste_expressao_simples(self):
        teste_expressao_simples()
    
    def teste_todos_operadores(self):
        teste_todos_operadores()
    
    def teste_numeros(self):
        teste_numeros()
    
    def teste_palavra_reservada(self):
        teste_palavra_reservada()
    
    def teste_identificador(self):
        teste_identificador()
    
    def teste_expressao_aninhada(self):
        teste_expressao_aninhada()
    
    def teste_erro_operador_invalido(self):
        teste_erro_operador_invalido()
    
    def teste_erro_numero_malformado(self):
        teste_erro_numero_malformado()
    
    def teste_erro_parenteses_desbalanceados(self):
        teste_erro_parenteses_desbalanceados()
    
    def teste_erro_linha_vazia(self):
        teste_erro_linha_vazia()
    
    def teste_erro_virgula_decimal(self):
        teste_erro_virgula_decimal()
    
    def teste_erro_numero_termina_ponto(self):
        teste_erro_numero_termina_ponto()

if __name__ == '__main__':
    unittest.main()