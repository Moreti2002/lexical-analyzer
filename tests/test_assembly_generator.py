"""
Testes para o gerador de assembly
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assembly_generator import gerar_assembly, AssemblyGenerator
from src.assembly_error import AssemblyError, AssemblyLimitError, AssemblyValidationError
from src.lexer import parse_expressao
from utils.assembly_utils import validar_tokens_assembly, calcular_limites_memoria

def teste_geracao_basica():
    """Teste geração básica de assembly"""
    tokens = parse_expressao("(3 7 +)")
    sucesso = gerar_assembly(tokens, "teste_basico.s")
    assert sucesso == True
    
    # Verifica se arquivo foi criado
    assert os.path.exists("teste_basico.s")
    
    # Verifica conteúdo básico do arquivo
    with open("teste_basico.s", 'r') as f:
        conteudo = f.read()
        assert ".device atmega328p" in conteudo
        assert "reset:" in conteudo
        assert "push_stack" in conteudo

def teste_operadores_aritmeticos():
    """Teste todos os operadores aritméticos"""
    operacoes = [
        ("(8 2 +)", "adicao.s"),
        ("(8 2 -)", "subtracao.s"), 
        ("(8 2 *)", "multiplicacao.s"),
        ("(8 2 /)", "divisao.s"),
        ("(8 3 %)", "resto.s"),
        ("(2 3 ^)", "potencia.s")
    ]
    
    for expressao, arquivo in operacoes:
        tokens = parse_expressao(expressao)
        sucesso = gerar_assembly(tokens, arquivo)
        assert sucesso == True
        assert os.path.exists(arquivo)

def teste_comando_memoria():
    """Teste comandos de memória"""
    tokens = parse_expressao("(42 MEM)")
    sucesso = gerar_assembly(tokens, "memoria.s")
    assert sucesso == True
    
    with open("memoria.s", 'r') as f:
        conteudo = f.read()
        assert "Armazena em variável MEM" in conteudo

def teste_comando_res():
    """Teste comando RES"""
    tokens = parse_expressao("(2 RES)")
    sucesso = gerar_assembly(tokens, "historico.s")
    assert sucesso == True
    
    with open("historico.s", 'r') as f:
        conteudo = f.read()
        assert "Comando RES" in conteudo

def teste_expressao_aninhada():
    """Teste expressão aninhada"""
    tokens = parse_expressao("((2 3 *) (4 2 /) +)")
    sucesso = gerar_assembly(tokens, "aninhada.s")
    assert sucesso == True

def teste_validacao_limites():
    """Teste validação de limites numéricos"""
    try:
        # Número muito grande para ponto fixo
        tokens = parse_expressao("(999.99 2.0 +)")
        validar_tokens_assembly(tokens)
        assert False, "Deveria ter dado erro de limite"
    except AssemblyLimitError:
        pass

def teste_geracao_completa():
    """Teste geração com arquivo de teste completo"""
    expressoes = [
        "(3.14 2.0 +)",
        "(10.5 3.2 -)", 
        "(4.0 5.0 *)",
        "(15.0 3.0 /)",
        "(17 5 %)",
        "(2.0 3 ^)",
        "(100.0 MEM)",
        "(MEM)"
    ]
    
    gerador = AssemblyGenerator()
    
    for i, expressao in enumerate(expressoes):
        tokens = parse_expressao(expressao)
        arquivo = f"teste_completo_{i}.s"
        sucesso = gerador.gerar_assembly(tokens, arquivo)
        assert sucesso == True

def teste_erro_token_invalido():
    """Teste erro com token inválido"""
    try:
        # Cria token inválido manualmente
        tokens = [
            {'tipo': 'PARENTESE_ABRE', 'valor': '('},
            {'tipo': 'NUMERO', 'valor': '3'},
            {'tipo': 'OPERADOR', 'valor': '&'},  # Operador inválido
            {'tipo': 'PARENTESE_FECHA', 'valor': ')'}
        ]
        gerar_assembly(tokens, "erro.s")
        assert False, "Deveria ter dado erro"
    except AssemblyError:
        pass

def teste_estatisticas_memoria():
    """Teste cálculo de estatísticas de memória"""
    tokens = parse_expressao("((3.14 2.0 +) (1.5 VAR *) -)")
    limites = calcular_limites_memoria(tokens)
    
    assert limites['pilha_maxima'] > 0
    assert limites['variaveis_count'] >= 1
    assert limites['memoria_total'] > 0

def teste_arquivo_complexo():
    """Teste com arquivo de expressões mais complexo"""
    expressoes_complexas = [
        "((2.5 3.0 *) (4.0 2.0 /) +)",
        "(7.5 VALOR)",
        "((VALOR 2.0 ^) (9.0 3.0 /) -)",
        "(1 RES)",
        "((1.5 2.0 *) (6.0 3.0 /) +)"
    ]
    
    gerador = AssemblyGenerator()
    
    for i, expr in enumerate(expressoes_complexas):
        tokens = parse_expressao(expr)
        arquivo = f"complexo_{i}.s"
        sucesso = gerador.gerar_assembly(tokens, arquivo)
        assert sucesso == True
        
        # Verifica estrutura básica
        with open(arquivo, 'r') as f:
            conteudo = f.read()
            assert "atmega328p" in conteudo
            assert "push_stack" in conteudo
            assert "pop_stack" in conteudo

def limpar_arquivos_teste():
    """Remove arquivos de teste gerados"""
    arquivos_teste = [
        "teste_basico.s", "adicao.s", "subtracao.s", "multiplicacao.s",
        "divisao.s", "resto.s", "potencia.s", "memoria.s", "historico.s",
        "aninhada.s", "erro.s"
    ]
    
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            os.remove(arquivo)
    
    # Remove arquivos numerados
    for i in range(10):
        arquivo = f"teste_completo_{i}.s"
        if os.path.exists(arquivo):
            os.remove(arquivo)
        arquivo = f"complexo_{i}.s"
        if os.path.exists(arquivo):
            os.remove(arquivo)

class TestAssemblyGenerator(unittest.TestCase):
    """Testes unitários para o gerador de assembly"""
    
    def setUp(self):
        """Configura teste"""
        self.gerador = AssemblyGenerator()
    
    def tearDown(self):
        """Limpa após teste"""
        limpar_arquivos_teste()
    
    def test_geracao_basica(self):
        teste_geracao_basica()
    
    def test_operadores_aritmeticos(self):
        teste_operadores_aritmeticos()
    
    def test_comando_memoria(self):
        teste_comando_memoria()
    
    def test_comando_res(self):
        teste_comando_res()
    
    def test_expressao_aninhada(self):
        teste_expressao_aninhada()
    
    def test_validacao_limites(self):
        teste_validacao_limites()
    
    def test_geracao_completa(self):
        teste_geracao_completa()
    
    def test_erro_token_invalido(self):
        teste_erro_token_invalido()
    
    def test_estatisticas_memoria(self):
        teste_estatisticas_memoria()
    
    def test_arquivo_complexo(self):
        teste_arquivo_complexo()
    
    def test_integracao_lexer(self):
        """Teste integração com o lexer"""
        expressao = "(((1.5 2.0 *) (6.0 3.0 /)) +)"
        tokens = parse_expressao(expressao)
        
        # Valida tokens
        validar_tokens_assembly(tokens)
        
        # Gera assembly
        sucesso = self.gerador.gerar_assembly(tokens, "integracao.s")
        self.assertTrue(sucesso)
        
        # Verifica arquivo gerado
        self.assertTrue(os.path.exists("integracao.s"))
        
        with open("integracao.s", 'r') as f:
            conteudo = f.read()
            self.assertIn(".device atmega328p", conteudo)
            self.assertIn("main:", conteudo)
            self.assertIn("push_stack:", conteudo)
            self.assertIn("pop_stack:", conteudo)
    
    def test_ponto_fixo(self):
        """Teste conversão para ponto fixo"""
        from utils.assembly_utils import converter_float_ponto_fixo, converter_ponto_fixo_float
        
        # Teste conversões
        valor_original = 3.14
        valor_fixo = converter_float_ponto_fixo(valor_original)
        valor_convertido = converter_ponto_fixo_float(valor_fixo)
        
        # Verifica se conversão mantém precisão razoável
        diferenca = abs(valor_original - valor_convertido)
        self.assertLess(diferenca, 0.01)  # Tolerância de 1 centésimo
    
    def test_validacao_arquivo_saida(self):
        """Teste validação de arquivo de saída"""
        from utils.assembly_utils import validar_arquivo_saida
        
        # Arquivo válido
        self.assertTrue(validar_arquivo_saida("teste_valido.s"))
        
        # Arquivo em diretório inexistente (deveria dar erro)
        try:
            validar_arquivo_saida("/diretorio/inexistente/arquivo.s")
            self.fail("Deveria ter dado erro")
        except AssemblyError:
            pass

def executar_teste_completo():
    """Executa teste completo do sistema de geração de assembly"""
    print("Executando testes do gerador de assembly...")
    print("=" * 50)
    
    try:
        # Teste básico
        print("1. Teste básico...")
        teste_geracao_basica()
        print("   ✓ Passou")
        
        # Teste operadores
        print("2. Teste operadores...")
        teste_operadores_aritmeticos()
        print("   ✓ Passou")
        
        # Teste comandos especiais
        print("3. Teste comandos especiais...")
        teste_comando_memoria()
        teste_comando_res()
        print("   ✓ Passou")
        
        # Teste validação
        print("4. Teste validação...")
        teste_validacao_limites()
        print("   ✓ Passou")
        
        # Teste complexo
        print("5. Teste arquivo complexo...")
        teste_arquivo_complexo()
        print("   ✓ Passou")
        
        print("\n" + "=" * 50)
        print("Todos os testes passaram!")
        print("Assembly gerado está compatível com atmega328p")
        
        # Mostra exemplo de arquivo gerado
        if os.path.exists("teste_basico.s"):
            print("\nExemplo de código gerado (primeiras linhas):")
            print("-" * 30)
            with open("teste_basico.s", 'r') as f:
                linhas = f.readlines()[:15]
                for linha in linhas:
                    print(linha.rstrip())
            print("-" * 30)
        
    except Exception as e:
        print(f"✗ Erro nos testes: {e}")
    
    finally:
        # Limpa arquivos de teste
        limpar_arquivos_teste()

if __name__ == '__main__':
    # Executa testes individuais ou completo
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--unittest":
        unittest.main(argv=sys.argv[:1])
    else:
        executar_teste_completo()