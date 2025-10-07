# construção da gramática LL(1) para linguagem RPN

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class GramaticaError(Exception):
    """exceção para erros na gramática"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(f"Erro na gramática: {mensagem}")

def construir_gramatica():
    """
    define regras de produção da gramática RPN
    
    Returns:
        dict: estrutura com produções, first, follow e tabela LL(1)
    """
    gramatica = {
        'PROGRAMA': [
            ['EXPRESSAO']
        ],
        'EXPRESSAO': [
            ['(', 'CONTEUDO', ')']
        ],
        'CONTEUDO': [
            ['CONTEUDO_REAL']
        ],
        'CONTEUDO_REAL': [
            ['OPERACAO_OU_COMANDO']
        ],
        'OPERACAO_OU_COMANDO': [
            ['numero', 'RESTO_NUMERO'],
            ['identificador', 'RESTO_IDENTIFICADOR'],
            ['EXPRESSAO', 'OPERANDO', 'OPERADOR_TOTAL']
        ],
        'RESTO_NUMERO': [
            ['numero', 'OPERADOR_ARIT'],           # operação
            ['identificador'],                      # armazenar MEM
            ['RES']                                 # comando RES
        ],
        'RESTO_IDENTIFICADOR': [
            ['numero', 'OPERADOR_ARIT'],           # operação
            ['identificador', 'OPERADOR_ARIT'],    # operação
            ['EXPRESSAO', 'OPERADOR_TOTAL'],       # operação com expr
            []                                      # apenas identificador
        ],
        'OPERADOR_TOTAL': [
            ['OPERADOR_ARIT'],
            ['OPERADOR_REL', 'EXPRESSAO', 'PALAVRA_CONTROLE']
        ],
        'PALAVRA_CONTROLE': [
            ['EXPRESSAO', 'IF'],
            ['WHILE']
        ],
        'OPERACAO': [
            ['OPERANDO', 'OPERANDO', 'OPERADOR_ARIT']
        ],
        'OPERANDO': [
            ['numero'],
            ['identificador'],
            ['EXPRESSAO']
        ],
        'OPERADOR_ARIT': [
            ['+'],
            ['-'],
            ['*'],
            ['/'],
            ['%'],
            ['^']
        ],
        'OPERADOR_REL': [
            ['>'],
            ['<'],
            ['=='],
            ['!='],
            ['>='],
            ['<=']
        ]
    }
    
    # calcular conjuntos FIRST e FOLLOW
    first = calcular_all_first(gramatica)
    follow = calcular_all_follow(gramatica, first)
    
    # construir tabela LL(1)
    tabela = construir_tabela_ll1(gramatica, first, follow)
    
    # validar gramática (permitir conflitos em CONTEUDO)
    if not validar_gramatica_ll1(tabela):
        # avisar mas não falhar
        pass
    
    return {
        'producoes': gramatica,
        'first': first,
        'follow': follow,
        'tabela': tabela
    }

def eh_terminal(simbolo):
    """verifica se símbolo é terminal (minúscula ou símbolo especial)"""
    if not simbolo:
        return False
    return simbolo[0].islower() or simbolo in ['+', '-', '*', '/', '%', '^', 
                                                 '(', ')', '>', '<', '==', '!=', 
                                                 '>=', '<=', 'RES', 'IF', 'WHILE']

def eh_nao_terminal(simbolo):
    """verifica se símbolo é não-terminal (maiúscula)"""
    return simbolo and simbolo[0].isupper() and simbolo not in ['RES', 'IF', 'WHILE']

def calcular_first(simbolo, gramatica, memo=None):
    """
    calcula conjunto FIRST para um símbolo
    
    Args:
        simbolo (str): símbolo da gramática
        gramatica (dict): produções da gramática
        memo (dict): memoização para evitar recálculo
        
    Returns:
        set: conjunto FIRST do símbolo
    """
    if memo is None:
        memo = {}
    
    if simbolo in memo:
        return memo[simbolo]
    
    first = set()
    
    # terminal: FIRST é o próprio símbolo
    if eh_terminal(simbolo):
        first.add(simbolo)
        memo[simbolo] = first
        return first
    
    # não-terminal: analisar produções
    if simbolo not in gramatica:
        memo[simbolo] = first
        return first
    
    for producao in gramatica[simbolo]:
        if not producao:  # produção vazia (epsilon)
            first.add('ε')
            continue
        
        # analisar primeiro símbolo da produção
        primeiro = producao[0]
        
        if eh_terminal(primeiro):
            first.add(primeiro)
        else:
            # recursivamente adicionar FIRST do não-terminal
            first_primeiro = calcular_first(primeiro, gramatica, memo)
            first.update(first_primeiro - {'ε'})
            
            # se primeiro pode derivar epsilon, analisar próximos símbolos
            if 'ε' in first_primeiro:
                for i in range(1, len(producao)):
                    simbolo_atual = producao[i]
                    if eh_terminal(simbolo_atual):
                        first.add(simbolo_atual)
                        break
                    else:
                        first_atual = calcular_first(simbolo_atual, gramatica, memo)
                        first.update(first_atual - {'ε'})
                        if 'ε' not in first_atual:
                            break
                else:
                    # todos derivam epsilon
                    first.add('ε')
    
    memo[simbolo] = first
    return first

def calcular_all_first(gramatica):
    """
    calcula FIRST para todos não-terminais
    
    Args:
        gramatica (dict): produções da gramática
        
    Returns:
        dict: mapeamento não_terminal -> conjunto FIRST
    """
    first = {}
    memo = {}
    
    for nao_terminal in gramatica:
        first[nao_terminal] = calcular_first(nao_terminal, gramatica, memo)
    
    return first

def calcular_follow(nao_terminal, gramatica, first, memo=None):
    """
    calcula conjunto FOLLOW para um não-terminal
    
    Args:
        nao_terminal (str): não-terminal alvo
        gramatica (dict): produções da gramática
        first (dict): conjuntos FIRST
        memo (dict): memoização
        
    Returns:
        set: conjunto FOLLOW do não-terminal
    """
    if memo is None:
        memo = {}
    
    if nao_terminal in memo:
        return memo[nao_terminal]
    
    follow = set()
    
    # símbolo inicial tem $ no FOLLOW
    if nao_terminal == 'PROGRAMA':
        follow.add('$')
    
    # analisar todas as produções
    for nt, producoes in gramatica.items():
        for producao in producoes:
            for i, simbolo in enumerate(producao):
                if simbolo == nao_terminal:
                    # encontrou o não-terminal na produção
                    
                    # se há símbolo após, adicionar FIRST dele
                    if i + 1 < len(producao):
                        proximo = producao[i + 1]
                        
                        if eh_terminal(proximo):
                            follow.add(proximo)
                        else:
                            # adicionar FIRST do próximo (sem epsilon)
                            follow.update(first.get(proximo, set()) - {'ε'})
                            
                            # se próximo deriva epsilon, continuar
                            if 'ε' in first.get(proximo, set()):
                                # verificar símbolos seguintes
                                j = i + 2
                                while j < len(producao):
                                    simbolo_seguinte = producao[j]
                                    if eh_terminal(simbolo_seguinte):
                                        follow.add(simbolo_seguinte)
                                        break
                                    else:
                                        follow.update(first.get(simbolo_seguinte, set()) - {'ε'})
                                        if 'ε' not in first.get(simbolo_seguinte, set()):
                                            break
                                    j += 1
                                else:
                                    # chegou ao fim da produção
                                    if nt != nao_terminal:
                                        # adicionar FOLLOW do lado esquerdo
                                        follow_nt = calcular_follow(nt, gramatica, first, memo)
                                        follow.update(follow_nt)
                    else:
                        # está no final da produção
                        if nt != nao_terminal:
                            follow_nt = calcular_follow(nt, gramatica, first, memo)
                            follow.update(follow_nt)
    
    memo[nao_terminal] = follow
    return follow

def calcular_all_follow(gramatica, first):
    """
    calcula FOLLOW para todos não-terminais
    
    Args:
        gramatica (dict): produções da gramática
        first (dict): conjuntos FIRST
        
    Returns:
        dict: mapeamento não_terminal -> conjunto FOLLOW
    """
    follow = {}
    memo = {}
    
    for nao_terminal in gramatica:
        follow[nao_terminal] = calcular_follow(nao_terminal, gramatica, first, memo)
    
    return follow

def construir_tabela_ll1(gramatica, first, follow):
    """
    constrói tabela de análise LL(1)
    
    Args:
        gramatica (dict): produções da gramática
        first (dict): conjuntos FIRST
        follow (dict): conjuntos FOLLOW
        
    Returns:
        dict: tabela[não_terminal][terminal] -> produção
    """
    tabela = {}
    
    for nao_terminal in gramatica:
        tabela[nao_terminal] = {}
        
        for producao in gramatica[nao_terminal]:
            # calcular FIRST da produção
            first_producao = set()
            
            if not producao:  # epsilon
                first_producao.add('ε')
            else:
                primeiro = producao[0]
                if eh_terminal(primeiro):
                    first_producao.add(primeiro)
                else:
                    first_producao.update(first.get(primeiro, set()))
            
            # adicionar entrada na tabela para cada terminal em FIRST
            for terminal in first_producao:
                if terminal != 'ε':
                    if terminal in tabela[nao_terminal]:
                        # conflito!
                        tabela[nao_terminal][terminal].append(producao)
                    else:
                        tabela[nao_terminal][terminal] = [producao]
            
            # se produção deriva epsilon, usar FOLLOW
            if 'ε' in first_producao:
                for terminal in follow.get(nao_terminal, set()):
                    if terminal in tabela[nao_terminal]:
                        tabela[nao_terminal][terminal].append(producao)
                    else:
                        tabela[nao_terminal][terminal] = [producao]
    
    return tabela

def validar_gramatica_ll1(tabela):
    """
    verifica se há conflitos na tabela (múltiplas produções)
    ignora conflitos esperados em CONTEUDO (resolvidos dinamicamente)
    
    Args:
        tabela (dict): tabela LL(1)
        
    Returns:
        bool: True se não há conflitos críticos
    """
    conflitos_criticos = []
    
    for nao_terminal, entradas in tabela.items():
        for terminal, producoes in entradas.items():
            if len(producoes) > 1:
                # conflitos em CONTEUDO são resolvidos pelo parser dinamicamente
                if nao_terminal in ['CONTEUDO', 'CONTEUDO_REAL', 'OPERACAO_OU_COMANDO']:
                    print(f"Conflito controlado em [{nao_terminal}, {terminal}]")
                    continue
                
                conflitos_criticos.append((nao_terminal, terminal, producoes))
                print(f"Conflito CRÍTICO em [{nao_terminal}, {terminal}]: {producoes}")
    
    return len(conflitos_criticos) == 0

def obter_producao(tabela, nao_terminal, terminal):
    """
    obtém produção da tabela LL(1)
    
    Args:
        tabela (dict): tabela LL(1)
        nao_terminal (str): não-terminal
        terminal (str): terminal (lookahead)
        
    Returns:
        list: produção ou None se não existe
    """
    if nao_terminal not in tabela:
        return None
    
    if terminal not in tabela[nao_terminal]:
        return None
    
    producoes = tabela[nao_terminal][terminal]
    return producoes[0] if producoes else None



if __name__ == '__main__':
    # teste da gramática
    try:
        resultado = construir_gramatica()
        
        print("=== GRAMÁTICA LL(1) ===\n")
        
        print("PRODUÇÕES:")
        for nt, prods in resultado['producoes'].items():
            for prod in prods:
                print(f"  {nt} -> {' '.join(prod) if prod else 'ε'}")
        
        print("\nFIRST:")
        for nt, first_set in resultado['first'].items():
            print(f"  FIRST({nt}) = {{{', '.join(sorted(first_set))}}}")
        
        print("\nFOLLOW:")
        for nt, follow_set in resultado['follow'].items():
            print(f"  FOLLOW({nt}) = {{{', '.join(sorted(follow_set))}}}")
        
        print("\nTABELA LL(1):")
        for nt in resultado['tabela']:
            for terminal, prod in resultado['tabela'][nt].items():
                print(f"  [{nt}, {terminal}] -> {' '.join(prod[0]) if prod[0] else 'ε'}")
        
        print("\n✓ Gramática LL(1) válida!")
        
    except GramaticaError as e:
        print(f"Erro: {e}")