# programa principal - analisador sintático fase 2
# integra todos os módulos do compilador

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.token_reader import ler_tokens, TokenReaderError
from src.grammar import construir_gramatica, GramaticaError
from src.parser import parsear, ParserError
from src.syntax_tree import gerar_arvore, imprimir_arvore, salvar_arvore, SyntaxTreeError

def processar_arquivo(nome_arquivo):
    """
    processa arquivo de entrada completo
    
    Args:
        nome_arquivo (str): nome do arquivo
        
    Returns:
        dict: resultados do processamento
    """
    resultados = {
        'arquivo': nome_arquivo,
        'expressoes_processadas': 0,
        'expressoes_validas': 0,
        'expressoes_invalidas': 0,
        'arvores': [],
        'erros': []
    }
    
    print(f"Processando arquivo: {nome_arquivo}\n")
    
    try:
        # ler tokens do arquivo
        print("1. Lendo tokens...")
        tokens_lista = ler_tokens(nome_arquivo)
        print(f"   ✓ {len(tokens_lista)} expressões lidas\n")
        
        # construir gramática e tabela LL(1)
        print("2. Construindo gramática LL(1)...")
        gramatica_info = construir_gramatica()
        tabela = gramatica_info['tabela']
        print("   ✓ Gramática construída e validada\n")
        
        # processar cada expressão
        print("3. Analisando expressões:")
        for i, tokens in enumerate(tokens_lista, 1):
            expressao_str = ''.join([t['valor'] for t in tokens])
            
            try:
                # análise sintática
                derivacao = parsear(tokens, tabela)
                
                # gerar árvore
                arvore = gerar_arvore(derivacao['derivacao'])
                
                resultados['arvores'].append({
                    'numero': i,
                    'expressao': expressao_str,
                    'arvore': arvore
                })
                
                resultados['expressoes_validas'] += 1
                print(f"   ✓ Expressão {i}: {expressao_str}")
                
            except (ParserError, SyntaxTreeError) as e:
                resultados['erros'].append({
                    'numero': i,
                    'expressao': expressao_str,
                    'erro': str(e)
                })
                resultados['expressoes_invalidas'] += 1
                print(f"   ✗ Expressão {i}: {str(e)}")
            
            resultados['expressoes_processadas'] += 1
        
        print()
        
        # salvar documentação
        print("4. Gerando documentação...")
        salvar_documentacao(gramatica_info, resultados)
        print("   ✓ GRAMATICA.md gerado\n")
        
        return resultados
        
    except (TokenReaderError, GramaticaError) as e:
        print(f"\nErro fatal: {e}")
        return None

def exibir_resultados(resultados):
    """
    exibe resultados do processamento
    
    Args:
        resultados (dict): resultados
    """
    print("="*60)
    print("RESULTADOS DO PROCESSAMENTO")
    print("="*60)
    
    print(f"\nArquivo: {resultados['arquivo']}")
    print(f"Expressões processadas: {resultados['expressoes_processadas']}")
    print(f"  ✓ Válidas: {resultados['expressoes_validas']}")
    print(f"  ✗ Inválidas: {resultados['expressoes_invalidas']}")
    
    # exibir árvores
    if resultados['arvores']:
        print("\nÁRVORES SINTÁTICAS:")
        print("-"*60)
        
        for item in resultados['arvores']:
            print(f"\nExpressão {item['numero']}: {item['expressao']}")
            print(imprimir_arvore(item['arvore']))
    
    # exibir erros
    if resultados['erros']:
        print("\nERROS ENCONTRADOS:")
        print("-"*60)
        
        for erro in resultados['erros']:
            print(f"\nExpressão {erro['numero']}: {erro['expressao']}")
            print(f"  Erro: {erro['erro']}")
    
    print("\n" + "="*60)

def salvar_documentacao(gramatica_info, resultados):
    """
    gera arquivo GRAMATICA.md com documentação completa
    
    Args:
        gramatica_info (dict): informações da gramática
        resultados (dict): resultados do processamento
    """
    conteudo = "# Documentação da Gramática LL(1)\n\n"
    
    # gramática
    conteudo += "## Regras de Produção\n\n"
    conteudo += "```\n"
    for nt, prods in gramatica_info['producoes'].items():
        for prod in prods:
            producao_str = ' '.join(prod) if prod else 'ε'
            conteudo += f"{nt} → {producao_str}\n"
    conteudo += "```\n\n"
    
    # conjuntos FIRST
    conteudo += "## Conjuntos FIRST\n\n"
    conteudo += "| Não-Terminal | FIRST |\n"
    conteudo += "|--------------|-------|\n"
    for nt, first_set in sorted(gramatica_info['first'].items()):
        first_str = ', '.join(sorted(first_set))
        conteudo += f"| {nt} | {{ {first_str} }} |\n"
    conteudo += "\n"
    
    # conjuntos FOLLOW
    conteudo += "## Conjuntos FOLLOW\n\n"
    conteudo += "| Não-Terminal | FOLLOW |\n"
    conteudo += "|--------------|--------|\n"
    for nt, follow_set in sorted(gramatica_info['follow'].items()):
        follow_str = ', '.join(sorted(follow_set))
        conteudo += f"| {nt} | {{ {follow_str} }} |\n"
    conteudo += "\n"
    
    # tabela LL(1)
    conteudo += "## Tabela de Análise LL(1)\n\n"
    conteudo += "| Não-Terminal | Terminal | Produção |\n"
    conteudo += "|--------------|----------|----------|\n"
    for nt in sorted(gramatica_info['tabela'].keys()):
        for terminal in sorted(gramatica_info['tabela'][nt].keys()):
            prod = gramatica_info['tabela'][nt][terminal][0]
            prod_str = ' '.join(prod) if prod else 'ε'
            conteudo += f"| {nt} | {terminal} | {prod_str} |\n"
    conteudo += "\n"
    
    # exemplo de árvore sintática
    if resultados['arvores']:
        conteudo += "## Exemplo de Árvore Sintática\n\n"
        ultima_arvore = resultados['arvores'][-1]
        conteudo += f"Expressão: `{ultima_arvore['expressao']}`\n\n"
        conteudo += "```\n"
        conteudo += imprimir_arvore(ultima_arvore['arvore'])
        conteudo += "```\n\n"
        
        # salvar árvore em JSON
        salvar_arvore(ultima_arvore['arvore'], "arvore_sintatica.json")
        conteudo += "Árvore completa salva em: `arvore_sintatica.json`\n"
    
    # salvar arquivo
    with open("GRAMATICA.md", 'w', encoding='utf-8') as arquivo:
        arquivo.write(conteudo)

def main():
    """função principal"""
    print("="*60)
    print("ANALISADOR SINTÁTICO - FASE 2")
    print("Parser LL(1) para Linguagem RPN")
    print("="*60)
    print()
    
    # verificar argumentos
    if len(sys.argv) != 2:
        print("Uso: python main_parser.py <arquivo.txt>")
        print("\nExemplo: python main_parser.py expressoes.txt")
        return 1
    
    arquivo_entrada = sys.argv[1]
    
    # verificar se arquivo existe
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado")
        return 1
    
    # processar arquivo
    resultados = processar_arquivo(arquivo_entrada)
    
    if resultados:
        # exibir resultados
        exibir_resultados(resultados)
        
        # indicar sucesso
        if resultados['expressoes_invalidas'] == 0:
            print("\n✓ Todas as expressões são sintaticamente válidas!")
            return 0
        else:
            print(f"\n⚠ {resultados['expressoes_invalidas']} expressão(ões) com erro")
            return 1
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())