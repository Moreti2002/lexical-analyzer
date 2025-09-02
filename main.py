#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa Principal - Analisador Léxico e Gerador Assembly para Expressões RPN
Trabalho de Compiladores

Autores: [Nome dos alunos em ordem alfabética + usuário GitHub]
Grupo: [Nome do grupo no Canvas]
"""

import sys
import os
from src.lexer import parse_expressao, LexerError, salvar_tokens
from src.executor import executar_expressao, ExecutorError
from src.assembly_generator import gerar_assembly, AssemblyError
from utils.util import ler_arquivo


def processar_arquivo(nome_arquivo):
    """
    Processa um arquivo de expressões RPN gerando tokens, executando e criando Assembly
    
    Args:
        nome_arquivo (str): Nome do arquivo a ser processado
    """
    try:
        linhas = ler_arquivo(nome_arquivo)
        
        print(f"Processando arquivo: {nome_arquivo}")
        print(f"Total de linhas: {len(linhas)}")
        print("="*60)
        
        todos_tokens = []
        todos_assemblies = []
        sucessos = 0
        erros = 0
        historico_global = []
        memoria_global = {}
        
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            
            if not linha:  # Ignora linhas vazias
                continue
                
            print(f"\nLinha {i}: {linha}")
            print("-" * 40)
            
            try:
                # Análise léxica
                tokens = parse_expressao(linha)
                print("✓ ANÁLISE LÉXICA BEM-SUCEDIDA")
                print("Tokens reconhecidos:")
                for j, token in enumerate(tokens):
                    print(f"  {j+1:2d}. {token['tipo']:18} -> '{token['valor']}'")
                
                todos_tokens.extend(tokens)
                
                # Execução
                resultado, historico_global, memoria_global = executar_expressao(
                    tokens, historico_global, memoria_global
                )
                print(f"✓ EXECUÇÃO BEM-SUCEDIDA: {resultado}")
                
                # Geração de Assembly
                assembly_code, _, _ = gerar_assembly(tokens, historico_global, memoria_global)
                print("✓ ASSEMBLY GERADO COM SUCESSO")
                
                todos_assemblies.append(f"; Linha {i}: {linha}")
                todos_assemblies.append(assembly_code)
                todos_assemblies.append("")  # linha vazia entre expressões
                
                sucessos += 1
                
            except LexerError as e:
                erros += 1
                print(f"✗ ERRO LÉXICO: {e}")
                
            except ExecutorError as e:
                erros += 1
                print(f"✗ ERRO DE EXECUÇÃO: {e}")
                
            except AssemblyError as e:
                erros += 1
                print(f"✗ ERRO DE GERAÇÃO ASSEMBLY: {e}")
            
            except Exception as e:
                erros += 1
                print(f"✗ ERRO INESPERADO: {e}")
        
        # Resumo final
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"Linhas processadas: {sucessos + erros}")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros}")
        print(f"Total de tokens gerados: {len(todos_tokens)}")
        
        # Salvar arquivos de saída
        if todos_tokens:
            salvar_tokens(todos_tokens, "tokens.txt")
            print(f"\n✓ Tokens salvos em 'tokens.txt'")
        
        if todos_assemblies:
            salvar_assembly_completo(todos_assemblies, "programa_completo.s")
            print(f"✓ Assembly completo salvo em 'programa_completo.s'")
        
        # Salvar resultados finais
        if historico_global:
            salvar_resultados(historico_global, memoria_global)
            print(f"✓ Resultados salvos em 'resultados.txt'")
        
        return sucessos == len([l for l in linhas if l.strip()])
        
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{nome_arquivo}' não encontrado.")
        return False
    except Exception as e:
        print(f"ERRO ao processar arquivo: {e}")
        return False

def salvar_assembly_completo(assemblies, nome_arquivo):
    """
    Salva código Assembly completo em um arquivo .s
    
    Args:
        assemblies (list): lista de códigos assembly das expressões
        nome_arquivo (str): nome do arquivo de saída
    """
    try:
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write("; ====================================================\n")
            arquivo.write("; Código Assembly completo gerado automaticamente\n")
            arquivo.write("; Processador de Expressões RPN para Arduino Uno\n")
            arquivo.write("; ATmega328p - Trabalho de Compiladores\n")
            arquivo.write("; ====================================================\n\n")
            
            # Usar o cabeçalho correto do assembly_generator
            from src.assembly_generator import gerar_cabecalho_assembly, gerar_finalizacao_assembly
            arquivo.write(gerar_cabecalho_assembly())
            arquivo.write("\n")
            
            # Escrever apenas o código das expressões (sem cabeçalhos duplicados)
            for assembly in assemblies:
                if assembly.strip() and not assembly.startswith(';'):
                    # Filtrar apenas linhas de código, ignorar comentários de linha
                    linhas = assembly.split('\n')
                    for linha in linhas:
                        linha = linha.strip()
                        if linha and not linha.startswith(';') and linha != '':
                            arquivo.write(linha + "\n")
            
            # Finalização única
            arquivo.write(gerar_finalizacao_assembly())
            
    except Exception as e:
        print(f"Erro ao salvar assembly completo: {e}")

def salvar_resultados(historico, memoria):
    """
    Salva resultados da execução em arquivo texto
    
    Args:
        historico (list): histórico de resultados
        memoria (dict): estado da memória
    """
    try:
        with open("resultados.txt", 'w') as arquivo:
            arquivo.write("Resultados da Execução - Expressões RPN\n")
            arquivo.write("="*50 + "\n\n")
            
            arquivo.write(f"Total de expressões processadas: {len(historico)}\n\n")
            
            arquivo.write("Histórico de Resultados:\n")
            arquivo.write("-" * 30 + "\n")
            for i, resultado in enumerate(historico, 1):
                arquivo.write(f"  {i:2d}. {resultado}\n")
            
            arquivo.write(f"\nEstado da Memória:\n")
            arquivo.write("-" * 30 + "\n")
            if memoria:
                for var, valor in memoria.items():
                    arquivo.write(f"  {var}: {valor}\n")
            else:
                arquivo.write("  (nenhuma variável armazenada)\n")
                
    except Exception as e:
        print(f"Erro ao salvar resultados: {e}")

def mostrar_ajuda():
    """Mostra informações de uso do programa"""
    print("Analisador Léxico e Gerador Assembly para Expressões RPN")
    print("Uso: python main.py <arquivo_expressoes>")
    print("\nExemplo:")
    print("  python main.py expressoes.txt")
    print("\nO arquivo deve conter expressões RPN, uma por linha.")
    print("Formato suportado: (A B op) onde A,B são números e op é um operador.")
    print("\nOperadores suportados: + - * / % ^")
    print("Comandos especiais: RES, identificadores em maiúsculas (MEM)")
    print("\nSaídas geradas:")
    print("  - tokens.txt: tokens da última execução")
    print("  - programa_completo.s: código Assembly completo")
    print("  - resultados.txt: resultados da execução")

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
    
    historico = []
    memoria = {}
    
    for caso in casos_teste:
        print(f"\nTestando: {caso}")
        try:
            tokens = parse_expressao(caso)
            print(f"✓ Léxico: {len(tokens)} tokens")
            
            resultado, historico, memoria = executar_expressao(tokens, historico, memoria)
            print(f"✓ Execução: {resultado}")
            
            assembly, _, _ = gerar_assembly(tokens, historico, memoria)
            print(f"✓ Assembly: {len(assembly.split('n'))} linhas")
            
        except (LexerError, ExecutorError, AssemblyError) as e:
            print(f"✗ Erro esperado: {e}")

def main():
    """Função principal do programa"""
    print("Processador de Expressões RPN - Trabalho de Compiladores")
    print("Análise Léxica + Execução + Geração Assembly")
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
        print("\nArquivos gerados:")
        print("  - tokens.txt: tokens da análise léxica")
        print("  - programa_completo.s: código Assembly para Arduino")
        print("  - resultados.txt: resultados da execução")
        print("  - programa_gerado.s: último Assembly individual")
        
        print("\nPara compilar o Assembly:")
        print("  avr-gcc -mmcu=atmega328p -o programa.elf programa_completo.s")
        print("  avr-objcopy -O ihex -R .eeprom programa.elf programa.hex")
        print("  avrdude -c arduino -p m328p -P /dev/ttyUSB0 -b 115200 -U flash:w:programa.hex")
        
        sys.exit(0)
    else:
        print("\n✗ Processamento concluído com erros.")
        sys.exit(1)

if __name__ == "__main__":
    main()