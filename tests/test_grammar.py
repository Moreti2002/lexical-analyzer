"""
testes para a gramática LL(1)
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.grammar import (
    construir_gramatica,
    calcular_first,
    calcular_follow,
    construir_tabela_ll1,
    validar_gramatica_ll1,
    obter_producao,
    GramaticaError
)

class TestGrammar(unittest.TestCase):
    """testes para a gramática"""
    
    @classmethod
    def setUpClass(cls):
        """configuração inicial"""
        cls.gramatica_info = construir_gramatica()
        cls.gramatica = cls.gramatica_info['producoes']
        cls.first = cls.gramatica_info['first']
        cls.follow = cls.gramatica_info['follow']
        cls.tabela = cls.gramatica_info['tabela']
    
    def teste_construir_gramatica(self):
        """teste construção da gramática"""
        self.assertIsNotNone(self.gramatica)
        self.assertIn('PROGRAMA', self.gramatica)
        self.assertIn('EXPRESSAO', self.gramatica)
        self.assertIn('OPERACAO', self.gramatica)
    
    def teste_first_numero(self):
        """teste FIRST de terminal"""
        first_numero = calcular_first('numero', self.gramatica)
        self.assertIn('numero', first_numero)
    
    def teste_first_programa(self):
        """teste FIRST de PROGRAMA"""
        self.assertIn('PROGRAMA', self.first)
        self.assertIn('(', self.first['PROGRAMA'])
    
    def teste_first_expressao(self):
        """teste FIRST de EXPRESSAO"""
        self.assertIn('EXPRESSAO', self.first)
        self.assertIn('(', self.first['EXPRESSAO'])
    
    def teste_first_operacao(self):
        """teste FIRST de OPERACAO"""
        self.assertIn('OPERACAO', self.first)
        # operação começa com operando, que pode ser numero, identificador ou (
        self.assertTrue(
            'numero' in self.first['OPERACAO'] or
            'identificador' in self.first['OPERACAO'] or
            '(' in self.first['OPERACAO']
        )
    
    def teste_follow_programa(self):
        """teste FOLLOW de PROGRAMA"""
        self.assertIn('PROGRAMA', self.follow)
        self.assertIn('$', self.follow['PROGRAMA'])
    
    def teste_follow_conteudo(self):
        """teste FOLLOW de CONTEUDO"""
        self.assertIn('CONTEUDO', self.follow)
        self.assertIn(')', self.follow['CONTEUDO'])
    
    def teste_tabela_ll1_construida(self):
        """teste construção da tabela LL(1)"""
        self.assertIsNotNone(self.tabela)
        self.assertIn('PROGRAMA', self.tabela)
        self.assertIn('EXPRESSAO', self.tabela)
    
    def teste_tabela_ll1_programa(self):
        """teste entrada da tabela para PROGRAMA"""
        self.assertIn('PROGRAMA', self.tabela)
        self.assertIn('(', self.tabela['PROGRAMA'])
    
    def teste_tabela_ll1_expressao(self):
        """teste entrada da tabela para EXPRESSAO"""
        self.assertIn('EXPRESSAO', self.tabela)
        self.assertIn('(', self.tabela['EXPRESSAO'])
    
    def teste_validar_gramatica_ll1(self):
        """teste validação LL(1) - não deve ter conflitos"""
        self.assertTrue(validar_gramatica_ll1(self.tabela))
    
    def teste_obter_producao(self):
        """teste obtenção de produção da tabela"""
        producao = obter_producao(self.tabela, 'EXPRESSAO', '(')
        self.assertIsNotNone(producao)
        self.assertIsInstance(producao, list)
    
    def teste_obter_producao_invalida(self):
        """teste obtenção de produção inválida"""
        producao = obter_producao(self.tabela, 'EXPRESSAO', 'invalido')
        self.assertIsNone(producao)
    
    def teste_first_todos_nao_terminais(self):
        """teste FIRST para todos os não-terminais"""
        for nt in self.gramatica.keys():
            self.assertIn(nt, self.first)
            self.assertIsInstance(self.first[nt], set)
    
    def teste_follow_todos_nao_terminais(self):
        """teste FOLLOW para todos os não-terminais"""
        for nt in self.gramatica.keys():
            self.assertIn(nt, self.follow)
            self.assertIsInstance(self.follow[nt], set)
    
    def teste_producoes_operador_arit(self):
        """teste produções de OPERADOR_ARIT"""
        self.assertIn('OPERADOR_ARIT', self.gramatica)
        operadores = ['+', '-', '*', '/', '%', '^']
        
        producoes = self.gramatica['OPERADOR_ARIT']
        operadores_na_gramatica = [p[0] for p in producoes]
        
        for op in operadores:
            self.assertIn(op, operadores_na_gramatica)
    
    def teste_producoes_operador_rel(self):
        """teste produções de OPERADOR_REL"""
        self.assertIn('OPERADOR_REL', self.gramatica)
        operadores_rel = ['>', '<', '==', '!=', '>=', '<=']
        
        producoes = self.gramatica['OPERADOR_REL']
        operadores_na_gramatica = [p[0] for p in producoes]
        
        for op in operadores_rel:
            self.assertIn(op, operadores_na_gramatica)

def teste_construir_gramatica():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    
    assert gramatica_info is not None
    assert 'producoes' in gramatica_info
    assert 'first' in gramatica_info
    assert 'follow' in gramatica_info
    assert 'tabela' in gramatica_info
    
    print("✓ teste_construir_gramatica passou")

def teste_calcular_first():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    
    first = gramatica_info['first']
    
    assert 'PROGRAMA' in first
    assert '(' in first['PROGRAMA']
    
    print("✓ teste_calcular_first passou")

def teste_calcular_follow():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    
    follow = gramatica_info['follow']
    
    assert 'PROGRAMA' in follow
    assert '$' in follow['PROGRAMA']
    
    print("✓ teste_calcular_follow passou")

def teste_validar_ll1():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    tabela = gramatica_info['tabela']
    
    valida = validar_gramatica_ll1(tabela)
    
    assert valida
    print("✓ teste_validar_ll1 passou")

def executar_testes_standalone():
    """executa todos os testes standalone"""
    print("=== TESTES DA GRAMÁTICA ===\n")
    
    try:
        teste_construir_gramatica()
        teste_calcular_first()
        teste_calcular_follow()
        teste_validar_ll1()
        
        print("\n✓ Todos os testes passaram!")
        
    except AssertionError as e:
        print(f"\n✗ Teste falhou: {e}")
    except Exception as e:
        print(f"\n✗ Erro: {e}")

if __name__ == '__main__':
    # executar testes standalone se chamado diretamente
    if len(sys.argv) > 1 and sys.argv[1] == '--standalone':
        executar_testes_standalone()
    else:
        # executar testes unitários
        unittest.main()