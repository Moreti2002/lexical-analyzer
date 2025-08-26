#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa Principal - Analisador Léxico para Expressões RPN
Fase 1 - Trabalho de Compiladores

Autores: [Nome dos alunos em ordem alfabética + usuário GitHub]
Grupo: [Nome do grupo no Canvas]
"""

import sys
import os
from src.lexer import parse_expressao, LexerError, salvar_tokens
from utils.util import ler_arquivo


def processar_arquivo(nome_arquivo):
    """
    Processa um arquivo de expressões RPN
    
    Args:
        nome_arquivo (str): Nome do arquivo a ser processado
    """
    try:
        linhas = ler_arquivo(nome_arquivo)
        
        print(f"Processando arquivo: {nome_arquivo}")
        print(f"Total de linhas: {len(linhas)}")
        print("="*60)
        
        todos_tokens = []
        sucessos = 0
        erros = 0
        
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            
            if not linha:  # Ignora linhas vazias
                continue
                
            print(f"\nLinha {i}: {linha}")
            print("-" * 40)
            
            try:
                tokens = parse_expressao(linha)
                sucessos += 1
                
                print("✓ ANÁLISE BEM-SUCEDIDA")
                print("Tokens reconhecidos:")
                for j, token in enumerate(tokens):
                    print(f"  {j+1:2d}. {token['tipo']:18} -> '{token['valor']}'")
                
                todos_tokens.extend(tokens)
                
            except LexerError as e:
                erros += 1
                print(f"✗ ERRO LÉXICO: {e}")
            
            except Exception as e:
                erros += 1
                print(f"✗ ERRO INESPERADO: {e}")
        
        # Resumo final
        print("\n" + "="*60)
        print("RESUMO DA ANÁLISE")
        print("="*60)
        print(f"Linhas processadas: {sucessos + erros}")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros}")
        print(f"Total de tokens gerados: {len(todos_tokens)}")
        
        if todos_tokens:
            # Salva todos os tokens da última execução
            salvar_tokens(todos_tokens, "tokens.txt")
            print(f"\n✓ Tokens salvos em 'tokens.txt'")
        
        return sucessos == len([l for l in linhas if l.strip()])
        
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{nome_arquivo}' não encontrado.")
        return False
    except Exception as e:
        print(f"ERRO ao processar arquivo: {e}")
        return False

def mostrar_ajuda():
    """Mostra informações de uso do programa"""
    print("Analisador Léxico para Expressões RPN")
    print("Uso: python main.py <arquivo_expressoes>")
    print("\nExemplo:")
    print("  python main.py expressoes.txt")
    print("\nO arquivo deve conter expressões RPN, uma por linha.")
    print("Formato suportado: (A B op) onde A,B são números e op é um operador.")
    print("\nOperadores suportados: + - * / % ^")
    print("Comandos especiais: RES, identificadores em maiúsculas (MEM)")

def executar_testes_rapidos():
    """Executa alguns testes rápidos para verificar funcionamento"""
    print("Executando testes rápidos...")
    print("="*50)
    
    casos_teste = [
        "(3.14 2.0 +)",        # Válido
        "((1.0 2.0 +) 3.0 *)", # Válido aninhado
        "(5 RES)",             # Comando especial
        "(10.5 CONTADOR)",     # Identificador
        "(3.14 2.0 &)",        # Inválido - operador
        "(3.14.5 2.0 +)"       # Inválido - número
    ]
    
    for caso in casos_teste:
        print(f"\nTestando: {caso}")
        try:
            tokens = parse_expressao(caso)
            print(f"✓ {len(tokens)} tokens reconhecidos")
        except LexerError as e:
            print(f"✗ Erro: {e}")

def main():
    """Função principal do programa"""
    print("Analisador Léxico - Expressões RPN")
    print("Fase 1 - Trabalho de Compiladores")
    print("="*60)
    
    # Verifica argumentos da linha de comando
    if len(sys.argv) != 2:
        print("ERRO: Número incorreto de argumentos.")
        mostrar_ajuda()
        
        # Oferece executar com arquivo padrão se existir
        if os.path.exists("expressoes.txt"):
            resposta = input("\nDeseja processar 'expressoes.txt'? (s/n): ").lower()
            if resposta == 's':
                nome_arquivo = "expressoes.txt"
            else:
                sys.exit(1)
        else:
            print("\nExecutando testes rápidos...")
            executar_testes_rapidos()
            sys.exit(1)
    else:
        nome_arquivo = sys.argv[1]
    
    # Processa o arquivo
    sucesso = processar_arquivo(nome_arquivo)
    
    if sucesso:
        print("\n✓ Processamento concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n✗ Processamento concluído com erros.")
        sys.exit(1)

if __name__ == "__main__":
    main()