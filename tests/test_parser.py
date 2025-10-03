"""
testes para o analisador sintático
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import parsear, ParserError
from src.grammar import construir_gramatica
from src.lexer import parse_expressao

class TestParser(unittest.TestCase):
    """testes para o parser LL(1)"""
    
    @classmethod
    def setUpClass(cls):
        """configuração inicial - constrói gramática uma vez"""
        gramatica_info = construir_gramatica()
        cls.tabela = gramatica_info['tabela']
    
    def teste_expressao_simples(self):
        """teste expressão aritmética simples"""
        tokens = parse_expressao("(3 5 +)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['tipo'], 'EXPRESSAO')
        self.assertEqual(resultado['derivacao']['conteudo']['tipo'], 'OPERACAO')
        self.assertEqual(resultado['derivacao']['conteudo']['operador'], '+')
    
    def teste_expressao_aninhada(self):
        """teste expressão com aninhamento"""
        tokens = parse_expressao("((2 3 *) (4 2 /) /)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['tipo'], 'EXPRESSAO')
    
    def teste_todos_operadores(self):
        """teste todos os operadores aritméticos"""
        operadores = ['+', '-', '*', '/', '%', '^']
        
        for op in operadores:
            with self.subTest(operador=op):
                tokens = parse_expressao(f"(5 3 {op})")
                resultado = parsear(tokens, self.tabela)
                
                self.assertTrue(resultado['valido'])
                self.assertEqual(resultado['derivacao']['conteudo']['operador'], op)
    
    def teste_comando_memoria_armazenar(self):
        """teste comando de armazenar na memória"""
        tokens = parse_expressao("(42 MEM)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['conteudo']['tipo'], 'COMANDO_ARMAZENAR')
        self.assertEqual(resultado['derivacao']['conteudo']['valor'], '42')
        self.assertEqual(resultado['derivacao']['conteudo']['identificador'], 'MEM')
    
    def teste_comando_memoria_recuperar(self):
        """teste comando de recuperar da memória"""
        tokens = parse_expressao("(MEM)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['conteudo']['tipo'], 'COMANDO_RECUPERAR')
        self.assertEqual(resultado['derivacao']['conteudo']['identificador'], 'MEM')
    
    def teste_comando_res(self):
        """teste comando RES"""
        tokens = parse_expressao("(1 RES)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['conteudo']['tipo'], 'COMANDO_RES')
        self.assertEqual(resultado['derivacao']['conteudo']['n'], '1')
    
    def teste_operacao_com_identificadores(self):
        """teste operação com identificadores"""
        tokens = parse_expressao("(VAR1 VAR2 +)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['conteudo']['tipo'], 'OPERACAO')
    
    def teste_erro_parenteses_desbalanceados(self):
        """teste erro de parênteses desbalanceados"""
        with self.assertRaises(Exception):
            tokens = parse_expressao("(3 5 +")
            parsear(tokens, self.tabela)
    
    def teste_erro_operandos_insuficientes(self):
        """teste erro de operandos insuficientes"""
        with self.assertRaises(ParserError):
            tokens = parse_expressao("(5 +)")
            parsear(tokens, self.tabela)
    
    def teste_erro_operador_faltando(self):
        """teste erro de operador faltando"""
        with self.assertRaises(ParserError):
            tokens = parse_expressao("(3 5)")
            parsear(tokens, self.tabela)
    
    def teste_aninhamento_profundo(self):
        """teste expressão com aninhamento profundo"""
        tokens = parse_expressao("(((2 3 +) (4 5 *) -) ((6 2 /) (8 4 %) +) ^)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
    
    def teste_numero_decimal(self):
        """teste operação com números decimais"""
        tokens = parse_expressao("(3.14 2.71 +)")
        resultado = parsear(tokens, self.tabela)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['derivacao']['conteudo']['operando1']['valor'], '3.14')
        self.assertEqual(resultado['derivacao']['conteudo']['operando2']['valor'], '2.71')

def teste_expressao_simples():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    tabela = gramatica_info['tabela']
    
    tokens = parse_expressao("(3 5 +)")
    resultado = parsear(tokens, tabela)
    
    assert resultado['valido']
    print("✓ teste_expressao_simples passou")

def teste_expressao_aninhada():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    tabela = gramatica_info['tabela']
    
    tokens = parse_expressao("((2 3 *) (4 2 /) /)")
    resultado = parsear(tokens, tabela)
    
    assert resultado['valido']
    print("✓ teste_expressao_aninhada passou")

def teste_comando_memoria():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    tabela = gramatica_info['tabela']
    
    tokens = parse_expressao("(42 MEM)")
    resultado = parsear(tokens, tabela)
    
    assert resultado['valido']
    assert resultado['derivacao']['conteudo']['tipo'] == 'COMANDO_ARMAZENAR'
    print("✓ teste_comando_memoria passou")

def teste_comando_res():
    """função de teste standalone"""
    gramatica_info = construir_gramatica()
    tabela = gramatica_info['tabela']
    
    tokens = parse_expressao("(1 RES)")
    resultado = parsear(tokens, tabela)
    
    assert resultado['valido']
    assert resultado['derivacao']['conteudo']['tipo'] == 'COMANDO_RES'
    print("✓ teste_comando_res passou")

def executar_testes_standalone():
    """executa todos os testes standalone"""
    print("=== TESTES DO PARSER ===\n")
    
    try:
        teste_expressao_simples()
        teste_expressao_aninhada()
        teste_comando_memoria()
        teste_comando_res()
        
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