"""
testes para o gerador de assembly AVR
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assembly_generator import gerar_assembly, AssemblyError
from src.lexer import parse_expressao
from utils.assembly_utils import float_para_ieee754_16bit, validar_assembly

def teste_geracao_basica():
    """teste geração de assembly para operação simples"""
    tokens = parse_expressao("(3 7 +)")
    codigo_assembly, historico, memoria = gerar_assembly(tokens)
    
    # verificar se contém elementos essenciais
    assert ".device atmega328p" in codigo_assembly
    assert ".org 0x0000" in codigo_assembly
    assert "rjmp reset" in codigo_assembly
    assert "float_add" in codigo_assembly

def teste_operacoes_aritmeticas():
    """teste geração de assembly para diferentes operadores"""
    operacoes = [
        ("(8 2 +)", "float_add"),
        ("(8 2 -)", "float_sub"),
        ("(8 2 *)", "float_mul"),
        ("(8 2 /)", "float_div"),
        ("(8 3 %)", "float_mod"),
        ("(2 3 ^)", "float_pow")
    ]
    
    for expressao, rotina_esperada in operacoes:
        tokens = parse_expressao(expressao)
        codigo_assembly, _, _ = gerar_assembly(tokens)
        assert rotina_esperada in codigo_assembly

def teste_comando_memoria():
    """teste geração para comandos de memória"""
    tokens = parse_expressao("(42.5 MEM)")
    codigo_assembly, historico, memoria = gerar_assembly(tokens)
    
    # verificar se contém código de armazenamento
    assert "Armazenar em MEM" in codigo_assembly
    assert "ldi r30, low(" in codigo_assembly
    assert "ldi r31, high(" in codigo_assembly

def teste_recuperacao_memoria():
    """teste recuperação da memória"""
    memoria_inicial = {'MEM': 0x0100}
    tokens = parse_expressao("(MEM)")
    codigo_assembly, _, _ = gerar_assembly(tokens, memoria=memoria_inicial)
    
    assert "Recuperar MEM" in codigo_assembly

def teste_memoria_nao_inicializada():
    """teste memória não inicializada retorna 0.0"""
    tokens = parse_expressao("(VAR)")
    codigo_assembly, _, _ = gerar_assembly(tokens)
    
    assert "não inicializada = 0.0" in codigo_assembly
    assert "clr r16" in codigo_assembly
    assert "clr r17" in codigo_assembly

def teste_comando_res():
    """teste comando RES"""
    historico_inicial = [10.0, 20.0, 30.0]
    tokens = parse_expressao("(2 RES)")
    codigo_assembly, _, _ = gerar_assembly(tokens, historico_inicial)
    
    assert "Comando 2 RES" in codigo_assembly

def teste_conversao_ieee754():
    """teste conversão para IEEE 754 16-bit"""
    # teste valores conhecidos
    assert float_para_ieee754_16bit(0.0) == [0x00, 0x00]
    
    # teste valor positivo
    bytes_result = float_para_ieee754_16bit(1.0)
    assert len(bytes_result) == 2
    assert all(isinstance(b, int) and 0 <= b <= 255 for b in bytes_result)

def teste_validacao_assembly():
    """teste validação de código assembly"""
    # código válido básico
    codigo_valido = """
.device atmega328p
.org 0x0000
rjmp reset

reset:
    ldi r16, 0xFF
    ret
"""
    
    is_valid, erros = validar_assembly(codigo_valido)
    assert is_valid, f"Código deveria ser válido, erros: {erros}"
    
    # código inválido - sem device
    codigo_invalido = """
.org 0x0000
rjmp reset
"""
    
    is_valid, erros = validar_assembly(codigo_invalido)
    assert not is_valid
    assert any("device" in erro.lower() for erro in erros)

def teste_erro_operandos_insuficientes():
    """teste erro de operandos insuficientes"""
    tokens = parse_expressao("(5 +)")  # falta um operando
    
    try:
        gerar_assembly(tokens)
        assert False, "deveria ter dado erro"
    except AssemblyError:
        pass

def teste_arquivo_gerado():
    """teste se arquivo .s é gerado"""
    tokens = parse_expressao("(3.14 2.0 +)")
    gerar_assembly(tokens)
    
    # verificar se arquivo foi criado
    assert os.path.exists("programa_gerado.s")
    
    # verificar conteúdo
    with open("programa_gerado.s", "r") as arquivo:
        conteudo = arquivo.read()
        assert ".device atmega328p" in conteudo
        assert "float_add" in conteudo
    
    # limpar arquivo de teste
    if os.path.exists("programa_gerado.s"):
        os.remove("programa_gerado.s")

def teste_expressao_complexa():
    """teste expressão com aninhamento"""
    tokens = parse_expressao("((2 3 *) (4 2 /) +)")
    codigo_assembly, _, _ = gerar_assembly(tokens)
    
    # verificar se contém múltiplas operações
    assert "float_mul" in codigo_assembly
    assert "float_div" in codigo_assembly
    assert "float_add" in codigo_assembly

def teste_sequencia_operacoes():
    """teste sequência de operações com persistência"""
    historico = []
    memoria = {}
    
    # primeira operação
    tokens1 = parse_expressao("(3 5 +)")
    codigo1, historico, memoria = gerar_assembly(tokens1, historico, memoria)
    
    # armazena na memória
    tokens2 = parse_expressao("(10 VAR)")
    codigo2, historico, memoria = gerar_assembly(tokens2, historico, memoria)
    
    # verifica se memória foi mantida
    assert 'VAR' in memoria

def teste_estrutura_assembly():
    """teste estrutura geral do assembly gerado"""
    tokens = parse_expressao("(1.5 2.5 *)")
    codigo_assembly, _, _ = gerar_assembly(tokens)
    
    linhas = codigo_assembly.split('\n')
    
    # verificar seções principais
    tem_cabecalho = any(".device atmega328p" in linha for linha in linhas)
    tem_reset = any("reset:" in linha for linha in linhas)
    tem_main = any("main:" in linha for linha in linhas)
    tem_rotinas = any("float_mul:" in linha for linha in linhas)
    
    assert tem_cabecalho, "Falta cabeçalho com device"
    assert tem_reset, "Falta label reset"
    assert tem_main, "Falta label main"
    assert tem_rotinas, "Falta rotinas matemáticas"

class TestAssemblyGenerator(unittest.TestCase):
    """testes para o gerador de assembly"""
    
    def test_geracao_basica(self):
        teste_geracao_basica()
    
    def test_operacoes_aritmeticas(self):
        teste_operacoes_aritmeticas()
    
    def test_comando_memoria(self):
        teste_comando_memoria()
    
    def test_recuperacao_memoria(self):
        teste_recuperacao_memoria()
    
    def test_memoria_nao_inicializada(self):
        teste_memoria_nao_inicializada()
    
    def test_comando_res(self):
        teste_comando_res()
    
    def test_conversao_ieee754(self):
        teste_conversao_ieee754()
    
    def test_validacao_assembly(self):
        teste_validacao_assembly()
    
    def test_erro_operandos_insuficientes(self):
        teste_erro_operandos_insuficientes()
    
    def test_arquivo_gerado(self):
        teste_arquivo_gerado()
    
    def test_expressao_complexa(self):
        teste_expressao_complexa()
    
    def test_sequencia_operacoes(self):
        teste_sequencia_operacoes()
    
    def test_estrutura_assembly(self):
        teste_estrutura_assembly()

if __name__ == '__main__':
    unittest.main()