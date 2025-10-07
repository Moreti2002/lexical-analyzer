#!/usr/bin/env python3
# script para executar todos os testes do projeto

import sys
import os
import subprocess

def detectar_python():
    """detecta comando python disponível"""
    for cmd in ['python3', 'python']:
        try:
            subprocess.run([cmd, '--version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         check=True)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

PYTHON_CMD = detectar_python()

if PYTHON_CMD is None:
    print("Erro: Python não encontrado no sistema")
    sys.exit(1)

def imprimir_secao(titulo):
    """imprime cabeçalho de seção"""
    print("\n" + "="*60)
    print(titulo)
    print("="*60 + "\n")

def executar_comando(comando, descricao):
    """executa comando e reporta resultado"""
    # substituir python por PYTHON_CMD
    comando = comando.replace('python ', f'{PYTHON_CMD} ')
    
    print(f"► {descricao}")
    print(f"  Comando: {comando}\n")
    
    resultado = os.system(comando)
    
    if resultado == 0:
        print(f"  ✓ {descricao} - PASSOU\n")
        return True
    else:
        print(f"  ✗ {descricao} - FALHOU\n")
        return False

def main():
    """função principal"""
    print("="*60)
    print("SUITE DE TESTES - FASE 2")
    print("Parser LL(1) para Linguagem RPN")
    print("="*60)
    
    resultados = {
        'total': 0,
        'passou': 0,
        'falhou': 0
    }
    
    # testes de módulos individuais
    imprimir_secao("1. TESTES DE MÓDULOS INDIVIDUAIS")
    
    testes_modulos = [
        ("python src/grammar.py", "Gramática LL(1)"),
        ("python src/lexer.py", "Analisador Léxico"),
        ("python src/parser.py", "Parser"),
        ("python src/syntax_tree.py", "Árvore Sintática"),
        ("python src/control_structures.py", "Estruturas de Controle")
    ]
    
    for comando, descricao in testes_modulos:
        resultados['total'] += 1
        if executar_comando(comando, descricao):
            resultados['passou'] += 1
        else:
            resultados['falhou'] += 1
    
    # testes unitários
    imprimir_secao("2. TESTES UNITÁRIOS")
    
    testes_unitarios = [
        ("python tests/test_grammar.py --standalone", "Testes da Gramática"),
        ("python tests/test_parser.py --standalone", "Testes do Parser")
    ]
    
    for comando, descricao in testes_unitarios:
        resultados['total'] += 1
        if executar_comando(comando, descricao):
            resultados['passou'] += 1
        else:
            resultados['falhou'] += 1
    
    # testes de integração
    imprimir_secao("3. TESTES DE INTEGRAÇÃO")
    
    arquivos_teste = ["test1.txt", "test2.txt", "test3.txt"]
    
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            resultados['total'] += 1
            if executar_comando(f"python main_parser.py {arquivo}", f"Processar {arquivo}"):
                resultados['passou'] += 1
            else:
                resultados['falhou'] += 1
        else:
            print(f"⚠ Arquivo {arquivo} não encontrado - pulando\n")
    
    # verificar arquivos gerados
    imprimir_secao("4. VERIFICAÇÃO DE SAÍDAS")
    
    arquivos_saida = [
        ("GRAMATICA.md", "Documentação da gramática"),
        ("arvore_sintatica.json", "Árvore sintática em JSON")
    ]
    
    for arquivo, descricao in arquivos_saida:
        resultados['total'] += 1
        if os.path.exists(arquivo):
            print(f"✓ {descricao} gerado: {arquivo}")
            resultados['passou'] += 1
        else:
            print(f"✗ {descricao} NÃO encontrado: {arquivo}")
            resultados['falhou'] += 1
        print()
    
    # resumo final
    imprimir_secao("RESUMO DOS TESTES")
    
    print(f"Total de testes: {resultados['total']}")
    print(f"Passou: {resultados['passou']}")
    print(f"Falhou: {resultados['falhou']}")
    
    porcentagem = (resultados['passou'] / resultados['total'] * 100) if resultados['total'] > 0 else 0
    print(f"Taxa de sucesso: {porcentagem:.1f}%")
    
    if resultados['falhou'] == 0:
        print("\n✓ TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n⚠ {resultados['falhou']} teste(s) falharam")
        return 1

if __name__ == '__main__':
    sys.exit(main())