"""
Testes para o executador de expressões RPN
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.executor import executar_expressao, ExecutorError
from src.lexer import parse_expressao
from src.token_types import *

def assert_resultado_aproximado(obtido, esperado, tolerancia=0.01):
    """compara resultados com tolerância para números de ponto flutuante"""
    assert abs(obtido - esperado) < tolerancia, f"Esperado {esperado}, obtido {obtido}"

def teste_operacoes_basicas():
    """teste de todas as operações aritméticas básicas"""
    testes = [
        ("(3.5 2.0 +)", 5.5),
        ("(10.0 4.0 -)", 6.0),
        ("(3.0 4.0 *)", 12.0),
        ("(15.0 3.0 /)", 5.0),
        ("(17 5 %)", 2.0),
        ("(2.0 3 ^)", 8.0)
    ]
    
    for expressao, esperado in testes:
        tokens = parse_expressao(expressao)
        resultado, _, _ = executar_expressao(tokens)
        assert_resultado_aproximado(resultado, esperado)

def teste_operacao_adicao():
    """teste específico da adição"""
    tokens = parse_expressao("(7.25 2.75 +)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 10.0)

def teste_operacao_subtracao():
    """teste específico da subtração"""
    tokens = parse_expressao("(15.5 3.5 -)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 12.0)

def teste_operacao_multiplicacao():
    """teste específico da multiplicação"""
    tokens = parse_expressao("(2.5 4.0 *)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 10.0)

def teste_operacao_divisao():
    """teste específico da divisão"""
    tokens = parse_expressao("(20.0 4.0 /)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 5.0)

def teste_operacao_resto():
    """teste específico do resto da divisão"""
    tokens = parse_expressao("(23 7 %)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 2.0)

def teste_operacao_potencia():
    """teste específico da potenciação"""
    tokens = parse_expressao("(3.0 4 ^)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 81.0)

def teste_comando_memoria_armazenar():
    """teste do comando de armazenamento em memória"""
    tokens = parse_expressao("(42.5 MEM)")
    resultado, historico, memoria = executar_expressao(tokens)
    
    assert_resultado_aproximado(resultado, 42.5)
    assert memoria['MEM'] == 42.5
    assert len(historico) == 1

def teste_comando_memoria_recuperar():
    """teste do comando de recuperação da memória"""
    # primeiro armazenar
    tokens1 = parse_expressao("(100.0 VAR)")
    resultado1, historico, memoria = executar_expressao(tokens1)
    
    # depois recuperar
    tokens2 = parse_expressao("(VAR)")
    resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
    
    assert_resultado_aproximado(resultado2, 100.0)

def teste_comando_memoria_nao_inicializada():
    """teste de recuperação de memória não inicializada"""
    tokens = parse_expressao("(INEXISTENTE)")
    resultado, _, memoria = executar_expressao(tokens)
    
    assert_resultado_aproximado(resultado, 0.0)

def teste_comando_res():
    """teste do comando RES"""
    # primeiro algumas operações para criar histórico
    tokens1 = parse_expressao("(10.0 5.0 +)")
    resultado1, historico, memoria = executar_expressao(tokens1)
    
    tokens2 = parse_expressao("(20.0 3.0 *)")
    resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
    
    # agora testar RES
    tokens3 = parse_expressao("(1 RES)")  # último resultado
    resultado3, historico, memoria = executar_expressao(tokens3, historico, memoria)
    
    assert_resultado_aproximado(resultado3, 60.0)  # 20.0 * 3.0
    
    tokens4 = parse_expressao("(2 RES)")  # penúltimo resultado
    resultado4, historico, memoria = executar_expressao(tokens4, historico, memoria)
    
    assert_resultado_aproximado(resultado4, 15.0)  # 10.0 + 5.0

def teste_expressao_aninhada_simples():
    """teste de expressão com um nível de aninhamento"""
    tokens = parse_expressao("((2.0 3.0 +) 4.0 *)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 20.0)  # (5.0) * 4.0

def teste_expressao_aninhada_complexa():
    """teste de expressão com múltiplos níveis de aninhamento"""
    # ((1.5 2.0 *) (3.0 1.0 +) +) = (3.0 + 4.0) = 7.0
    tokens = parse_expressao("((1.5 2.0 *) (3.0 1.0 +) +)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 7.0)

def teste_expressao_triplo_aninhamento():
    """teste de expressão com três níveis de aninhamento"""
    # (((2.0 3.0 +) (4.0 1.0 -)) *) = ((5.0) (3.0)) *) = 15.0
    tokens = parse_expressao("(((2.0 3.0 +) (4.0 1.0 -)) *)")
    resultado, _, _ = executar_expressao(tokens)
    assert_resultado_aproximado(resultado, 15.0)

def teste_precisao_ieee754():
    """teste da precisão com duas casas decimais"""
    tokens = parse_expressao("(10.0 3.0 /)")
    resultado, _, _ = executar_expressao(tokens)
    
    # deve ser 3.33 (duas casas decimais)
    assert abs(resultado - 3.33) < 0.01

def teste_erro_divisao_por_zero():
    """teste de erro de divisão por zero"""
    try:
        tokens = parse_expressao("(5.0 0 /)")
        executar_expressao(tokens)
        assert False, "Deveria ter dado erro de divisão por zero"
    except ExecutorError as e:
        assert "divisão por zero" in str(e).lower()

def teste_erro_resto_por_zero():
    """teste de erro de resto por zero"""
    try:
        tokens = parse_expressao("(10 0 %)")
        executar_expressao(tokens)
        assert False, "Deveria ter dado erro de resto por zero"
    except ExecutorError as e:
        assert "divisão por zero" in str(e).lower()

def teste_erro_res_invalido():
    """teste de erro com RES inválido"""
    try:
        tokens = parse_expressao("(5 RES)")
        executar_expressao(tokens)  # sem histórico
        assert False, "Deveria ter dado erro de RES inválido"
    except ExecutorError as e:
        assert "res" in str(e).lower()

def teste_erro_res_negativo():
    """teste de erro com N negativo em RES"""
    try:
        tokens = parse_expressao("(-1 RES)")
        executar_expressao(tokens)
        assert False, "Deveria ter dado erro de N negativo"
    except ExecutorError as e:
        assert "não negativo" in str(e).lower()

def teste_erro_operandos_insuficientes():
    """teste de erro com operandos insuficientes"""
    try:
        tokens = parse_expressao("(5.0 +)")  # só um operando
        executar_expressao(tokens)
        assert False, "Deveria ter dado erro de operandos insuficientes"
    except ExecutorError as e:
        assert "insuficientes" in str(e).lower()

def teste_integracao_memoria_res():
    """teste de integração entre comandos de memória e RES"""
    # armazenar valor
    tokens1 = parse_expressao("(50.0 TEMP)")
    resultado1, historico, memoria = executar_expressao(tokens1)
    
    # usar valor armazenado em operação
    tokens2 = parse_expressao("(TEMP 10.0 +)")
    resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
    
    # usar resultado anterior via RES
    tokens3 = parse_expressao("(1 RES 5.0 *)")
    resultado3, historico, memoria = executar_expressao(tokens3, historico, memoria)
    
    assert_resultado_aproximado(resultado3, 300.0)  # 60.0 * 5.0

def teste_sequencia_operacoes():
    """teste de sequência de operações mantendo estado"""
    historico = []
    memoria = {}
    
    # operação 1
    tokens1 = parse_expressao("(10.0 2.0 +)")
    resultado1, historico, memoria = executar_expressao(tokens1, historico, memoria)
    
    # operação 2 usando resultado anterior
    tokens2 = parse_expressao("(1 RES 3.0 *)")
    resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
    
    # operação 3 armazenando em memória
    tokens3 = parse_expressao("(1 RES RESULTADO)")
    resultado3, historico, memoria = executar_expressao(tokens3, historico, memoria)
    
    # verificações
    assert_resultado_aproximado(resultado1, 12.0)
    assert_resultado_aproximado(resultado2, 36.0)
    assert_resultado_aproximado(resultado3, 36.0)
    assert memoria['RESULTADO'] == 36.0
    assert len(historico) == 3

class TesteExecutor(unittest.TestCase):
    """classe para executar testes com unittest"""
    
    def test_operacoes_basicas(self):
        teste_operacoes_basicas()
    
    def test_operacao_adicao(self):
        teste_operacao_adicao()
    
    def test_operacao_subtracao(self):
        teste_operacao_subtracao()
    
    def test_operacao_multiplicacao(self):
        teste_operacao_multiplicacao()
    
    def test_operacao_divisao(self):
        teste_operacao_divisao()
    
    def test_operacao_resto(self):
        teste_operacao_resto()
    
    def test_operacao_potencia(self):
        teste_operacao_potencia()
    
    def test_comando_memoria_armazenar(self):
        teste_comando_memoria_armazenar()
    
    def test_comando_memoria_recuperar(self):
        teste_comando_memoria_recuperar()
    
    def test_comando_memoria_nao_inicializada(self):
        teste_comando_memoria_nao_inicializada()
    
    def test_comando_res(self):
        teste_comando_res()
    
    def test_expressao_aninhada_simples(self):
        teste_expressao_aninhada_simples()
    
    def test_expressao_aninhada_complexa(self):
        teste_expressao_aninhada_complexa()
    
    def test_expressao_triplo_aninhamento(self):
        teste_expressao_triplo_aninhamento()
    
    def test_precisao_ieee754(self):
        teste_precisao_ieee754()
    
    def test_erro_divisao_por_zero(self):
        teste_erro_divisao_por_zero()
    
    def test_erro_resto_por_zero(self):
        teste_erro_resto_por_zero()
    
    def test_erro_res_invalido(self):
        teste_erro_res_invalido()
    
    def test_erro_res_negativo(self):
        teste_erro_res_negativo()
    
    def test_erro_operandos_insuficientes(self):
        teste_erro_operandos_insuficientes()
    
    def test_integracao_memoria_res(self):
        teste_integracao_memoria_res()
    
    def test_sequencia_operacoes(self):
        teste_sequencia_operacoes()

if __name__ == '__main__':
    unittest.main()