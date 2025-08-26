#!/usr/bin/env python3
"""
Debug do problema com palavra reservada RES
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import parse_expressao
from src.token_types import *

def debug_tokenizacao():
    """debugar como está sendo tokenizada a expressão (5 RES)"""
    expressao = "(5 RES)"
    print(f"Debugando expressão: {expressao}")
    print("-" * 40)
    
    try:
        tokens = parse_expressao(expressao)
        
        print(f"Total de tokens: {len(tokens)}")
        print()
        
        for i, token in enumerate(tokens):
            print(f"Token {i}:")
            print(f"  Tipo: {token['tipo']}")
            print(f"  Valor: '{token['valor']}'")
            if 'posicao' in token:
                print(f"  Posição: {token['posicao']}")
            print()
            
        # verificar especificamente o token RES
        if len(tokens) >= 3:
            token_res = tokens[2]
            print("Análise do token RES:")
            print(f"  Esperado: tipo={PALAVRA_RESERVADA}, valor='RES'")
            print(f"  Obtido: tipo={token_res['tipo']}, valor='{token_res['valor']}'")
            print(f"  Correto? {token_res['tipo'] == PALAVRA_RESERVADA and token_res['valor'] == 'RES'}")
            
    except Exception as e:
        print(f"Erro durante tokenização: {e}")

def debug_palavra_reservada():
    """testar a função eh_palavra_reservada diretamente"""
    print("Testando função eh_palavra_reservada:")
    print("-" * 40)
    
    from src.token_types import eh_palavra_reservada, PALAVRAS_RESERVADAS
    
    print(f"PALAVRAS_RESERVADAS = {PALAVRAS_RESERVADAS}")
    print(f"eh_palavra_reservada('RES') = {eh_palavra_reservada('RES')}")
    print(f"eh_palavra_reservada('MEM') = {eh_palavra_reservada('MEM')}")
    print(f"eh_palavra_reservada('TESTE') = {eh_palavra_reservada('TESTE')}")

def teste_simples():
    """teste simples para isolar o problema"""
    print("Teste simples de tokenização:")
    print("-" * 40)
    
    testes = [
        "(RES)",
        "(5 RES)", 
        "(RES 5)",
        "(MEM)",
        "(TEST)"
    ]
    
    for expr in testes:
        try:
            tokens = parse_expressao(expr)
            print(f"{expr} -> ", end="")
            for token in tokens:
                if token['tipo'] not in [PARENTESE_ABRE, PARENTESE_FECHA]:
                    print(f"{token['tipo']}:'{token['valor']}'", end=" ")
            print()
        except Exception as e:
            print(f"{expr} -> ERRO: {e}")

if __name__ == '__main__':
    debug_palavra_reservada()
    print("\n" + "="*50 + "\n")
    debug_tokenizacao() 
    print("\n" + "="*50 + "\n")
    teste_simples()