"""
testes para o executador de expressões RPN
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.executor import executar_expressao, ExecutorError
from src.lexer import parse_expressao

def teste_operacao_simples():
    """teste operação básica de adição"""
    tokens = parse_expressao("(3 7 +)")
    resultado, historico, memoria = executar_expressao(tokens)
    assert resultado == 10.0
    assert len(historico) == 1

def teste_todos_operadores():
    """teste todos os operadores aritméticos"""
    operacoes = [
        ("(8 2 +)", 10.0),
        ("(8 2 -)", 6.0),
        ("(8 2 *)", 16.0),
        ("(8 2 /)", 4.0),
        ("(8 3 %)", 2.0),
        ("(2 3 ^)", 8.0)
    ]
    
    for expressao, esperado in operacoes:
        tokens = parse_expressao(expressao)
        resultado, _, _ = executar_expressao(tokens)
        assert resultado == esperado

def teste_expressao_aninhada():
    """teste expressão com aninhamento"""
    tokens = parse_expressao("((2 3 *) (4 2 /) /)")
    resultado, _, _ = executar_expressao(tokens)
    assert resultado == 3.0  # (6 / 2) = 3.0

def teste_formatacao_resultado():
    """teste formatação com duas casas decimais"""
    tokens = parse_expressao("(1 3 /)")
    resultado, _, _ = executar_expressao(tokens)
    assert resultado == 0.33

def teste_comando_memoria():
    """teste comando de armazenar na memória"""
    tokens = parse_expressao("(42.5 MEM)")
    resultado, historico, memoria = executar_expressao(tokens)
    assert resultado == 42.5
    assert memoria['MEM'] == 42.5

def teste_recuperar_memoria():
    """teste comando de recuperar da memória"""
    memoria_inicial = {'MEM': 42.5}
    tokens = parse_expressao("(MEM)")
    resultado, _, _ = executar_expressao(tokens, memoria=memoria_inicial)
    assert resultado == 42.5

def teste_memoria_nao_inicializada():
    """teste memória não inicializada retorna 0.0"""
    tokens = parse_expressao("(VAR)")
    resultado, _, _ = executar_expressao(tokens)
    assert resultado == 0.0

def teste_comando_res():
    """teste comando RES"""
    historico_inicial = [10.0, 20.0, 30.0]
    tokens = parse_expressao("(2 RES)")
    resultado, _, _ = executar_expressao(tokens, historico_inicial)
    assert resultado == 20.0  # 2 linhas anteriores

def teste_res_primeira_linha():
    """teste RES da primeira linha"""
    historico_inicial = [10.0, 20.0]
    tokens = parse_expressao("(2 RES)")
    resultado, _, _ = executar_expressao(tokens, historico_inicial)
    assert resultado == 10.0  # 2 linhas anteriores

def teste_sequencia_operacoes():
    """teste sequência de operações com persistência"""
    historico = []
    memoria = {}
    
    # primeira operação
    tokens1 = parse_expressao("(3 5 +)")
    resultado1, historico, memoria = executar_expressao(tokens1, historico, memoria)
    
    # armazena na memória
    tokens2 = parse_expressao("(10 VAR)")
    resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
    
    # usa RES e memória
    tokens3 = parse_expressao("((2 RES) VAR *)")
    resultado3, historico, memoria = executar_expressao(tokens3, historico, memoria)
    
    assert resultado1 == 8.0
    assert resultado2 == 10.0
    assert resultado3 == 80.0  # 8.0 * 10.0

def teste_erro_divisao_zero():
    """teste erro de divisão por zero"""
    tokens = parse_expressao("(5 0 /)")
    try:
        executar_expressao(tokens)
        assert False, "deveria ter dado erro"
    except ExecutorError:
        pass

def teste_erro_res_invalido():
    """teste erro RES inválido"""
    tokens = parse_expressao("(5 RES)")
    try:
        executar_expressao(tokens, [1.0, 2.0])  # só 2 elementos no histórico
        assert False, "deveria ter dado erro"
    except ExecutorError:
        pass

def teste_erro_operandos_insuficientes():
    """teste erro operandos insuficientes"""
    tokens = parse_expressao("(5 +)")  # falta um operando
    try:
        executar_expressao(tokens)
        assert False, "deveria ter dado erro"
    except ExecutorError:
        pass

class TestExecutor(unittest.TestCase):
    """testes para o executador de expressões"""
    
    def teste_operacao_simples(self):
        teste_operacao_simples()
    
    def teste_todos_operadores(self):
        teste_todos_operadores()
    
    def teste_expressao_aninhada(self):
        teste_expressao_aninhada()
    
    def teste_formatacao_resultado(self):
        teste_formatacao_resultado()
    
    def teste_comando_memoria(self):
        teste_comando_memoria()
    
    def teste_recuperar_memoria(self):
        teste_recuperar_memoria()
    
    def teste_memoria_nao_inicializada(self):
        teste_memoria_nao_inicializada()
    
    def teste_comando_res(self):
        teste_comando_res()
    
    def teste_res_primeira_linha(self):
        teste_res_primeira_linha()
    
    def teste_sequencia_operacoes(self):
        teste_sequencia_operacoes()
    
    def teste_erro_divisao_zero(self):
        teste_erro_divisao_zero()
    
    def teste_erro_res_invalido(self):
        teste_erro_res_invalido()
    
    def teste_erro_operandos_insuficientes(self):
        teste_erro_operandos_insuficientes()

if __name__ == '__main__':
    unittest.main()