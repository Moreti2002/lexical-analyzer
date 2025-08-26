# Executador de expressões RPN com pilha

import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class ExecutorError(Exception):
    """exceção para erros do executador de expressões"""
    def __init__(self, mensagem, contexto=None):
        self.mensagem = mensagem
        self.contexto = contexto
        super().__init__(f"Erro de execução{' no contexto: ' + str(contexto) if contexto else ''}: {mensagem}")

def criar_contexto_execucao():
    """
    cria o contexto inicial para execução de expressões RPN
    
    Returns:
        dict: contexto com histórico, memória e pilha
    """
    return {
        'historico_resultados': [],
        'memoria': {},
        'pilha': [],
        'resultado_atual': None
    }

def formatar_resultado(valor):
    """
    formata o resultado final com precisão IEEE 754 (duas casas decimais)
    
    Args:
        valor (float): valor a ser formatado
        
    Returns:
        float: valor formatado com duas casas decimais
    """
    return round(float(valor), 2)

def validar_expressao(tokens):
    """
    valida a estrutura básica da expressão RPN antes da execução
    
    Args:
        tokens (list): lista de tokens da expressão
        
    Raises:
        ExecutorError: se a estrutura não for válida
    """
    if not tokens:
        raise ExecutorError("Lista de tokens vazia")
    
    # deve ter pelo menos 3 tokens para operação válida (operando, operando, operador)
    if len(tokens) < 3:
        # exceção para casos especiais como (MEM) ou (N RES)
        if len(tokens) == 3:  # (MEM) ou (N RES)
            if tokens[1]['tipo'] in [IDENTIFICADOR, PALAVRA_RESERVADA]:
                return
        raise ExecutorError("Expressão muito curta para ser válida")

def executar_operacao(operador, operando2, operando1):
    """
    executa uma operação aritmética entre dois operandos
    
    Args:
        operador (str): operador aritmético (+, -, *, /, %, ^)
        operando2 (float): segundo operando (topo da pilha)
        operando1 (float): primeiro operando
        
    Returns:
        float: resultado da operação
        
    Raises:
        ExecutorError: para operações inválidas ou divisão por zero
    """
    try:
        if operador == '+':
            return operando1 + operando2
        elif operador == '-':
            return operando1 - operando2
        elif operador == '*':
            return operando1 * operando2
        elif operador == '/':
            if operando2 == 0:
                raise ExecutorError("Divisão por zero")
            return operando1 / operando2
        elif operador == '%':
            if operando2 == 0:
                raise ExecutorError("Divisão por zero no resto")
            # para números reais, usar fmod
            return operando1 % operando2
        elif operador == '^':
            return pow(operando1, operando2)
        else:
            raise ExecutorError(f"Operador inválido: {operador}")
    except (OverflowError, ValueError) as e:
        raise ExecutorError(f"Erro numérico na operação {operador}: {str(e)}")

def gerenciar_memoria(tokens, indice, memoria):
    """
    gerencia comandos de memória (V MEM) e (MEM)
    
    Args:
        tokens (list): lista de tokens
        indice (int): índice atual na lista de tokens
        memoria (dict): dicionário de memória
        
    Returns:
        tuple: (valor_retornado, novo_indice, memoria_atualizada)
        
    Raises:
        ExecutorError: para comandos de memória inválidos
    """
    # caso (MEM) - recuperar valor
    if indice == len(tokens) - 2:  # penúltimo token
        if tokens[indice]['tipo'] == IDENTIFICADOR:
            nome_mem = tokens[indice]['valor']
            valor = memoria.get(nome_mem, 0.0)  # retorna 0 se não inicializada
            return valor, indice + 1, memoria
    
    # caso (V MEM) - armazenar valor
    elif indice == len(tokens) - 3:  # antepenúltimo token
        if tokens[indice + 1]['tipo'] == IDENTIFICADOR:
            valor = float(tokens[indice]['valor'])
            nome_mem = tokens[indice + 1]['valor']
            memoria[nome_mem] = valor
            return valor, indice + 2, memoria
    
    raise ExecutorError("Comando de memória mal formado")

def gerenciar_resultado(n, historico_resultados):
    """
    gerencia comando RES - retorna resultado N linhas anteriores
    
    Args:
        n (int): número de linhas anteriores
        historico_resultados (list): histórico de resultados
        
    Returns:
        float: resultado da linha N anterior
        
    Raises:
        ExecutorError: para N inválido ou histórico insuficiente
    """
    if n < 0:
        raise ExecutorError("N deve ser não negativo para RES")
    
    if n == 0 or n > len(historico_resultados):
        raise ExecutorError(f"RES: não há resultado {n} linhas atrás")
    
    # N=1 significa resultado imediatamente anterior (índice -1)
    indice = -n
    return historico_resultados[indice]

def avaliar_rpn(tokens, contexto):
    """
    avalia expressão RPN usando algoritmo de pilha
    
    Args:
        tokens (list): tokens da expressão RPN
        contexto (dict): contexto de execução
        
    Returns:
        float: resultado da avaliação
        
    Raises:
        ExecutorError: para expressões mal formadas
    """
    pilha = []
    i = 1  # começa após o parêntese de abertura
    
    while i < len(tokens) - 1:  # para antes do parêntese de fechamento
        token = tokens[i]
        
        if token['tipo'] == NUMERO:
            # empilha número
            pilha.append(float(token['valor']))
            
        elif token['tipo'] == OPERADOR:
            # precisa de pelo menos 2 operandos
            if len(pilha) < 2:
                raise ExecutorError(f"Operandos insuficientes para operador {token['valor']}")
            
            # desempilha dois operandos (ordem importa!)
            operando2 = pilha.pop()
            operando1 = pilha.pop()
            
            # executa operação e empilha resultado
            resultado = executar_operacao(token['valor'], operando2, operando1)
            pilha.append(resultado)
            
        elif token['tipo'] == PALAVRA_RESERVADA and token['valor'] == 'RES':
            # comando (N RES)
            if i == 0 or tokens[i-1]['tipo'] != NUMERO:
                raise ExecutorError("RES deve ser precedido por um número")
            
            n = int(float(tokens[i-1]['valor']))
            resultado = gerenciar_resultado(n, contexto['historico_resultados'])
            
            # remove o número N da pilha e empilha o resultado
            pilha.pop()
            pilha.append(resultado)
            
        elif token['tipo'] == IDENTIFICADOR:
            # pode ser comando MEM
            if i > 0 and tokens[i-1]['tipo'] == NUMERO:
                # caso (V MEM) - armazenar
                valor = pilha.pop()  # remove valor da pilha
                nome_mem = token['valor']
                contexto['memoria'][nome_mem] = valor
                pilha.append(valor)  # reempilha para continuar processamento
            else:
                # caso (MEM) - recuperar
                nome_mem = token['valor']
                valor = contexto['memoria'].get(nome_mem, 0.0)
                pilha.append(valor)
                
        elif token['tipo'] == PARENTESE_ABRE:
            # expressão aninhada - processar recursivamente
            # encontrar parêntese de fechamento correspondente
            contador = 1
            inicio = i
            i += 1
            
            while i < len(tokens) and contador > 0:
                if tokens[i]['tipo'] == PARENTESE_ABRE:
                    contador += 1
                elif tokens[i]['tipo'] == PARENTESE_FECHA:
                    contador -= 1
                i += 1
            
            # extrair subexpressão e avaliar
            subexpressao = tokens[inicio:i]
            resultado = avaliar_rpn(subexpressao, contexto)
            pilha.append(resultado)
            i -= 1  # ajustar porque será incrementado no final do loop
            
        i += 1
    
    # ao final, deve ter exatamente um valor na pilha
    if len(pilha) != 1:
        raise ExecutorError(f"Expressão mal formada: pilha final tem {len(pilha)} elementos")
    
    return pilha[0]

def executar_expressao(tokens, historico_resultados=None, memoria=None):
    """
    função principal para executar uma expressão RPN
    
    Args:
        tokens (list): tokens da expressão RPN
        historico_resultados (list): histórico de resultados anteriores
        memoria (dict): dicionário de memória compartilhada
        
    Returns:
        tuple: (resultado, historico_atualizado, memoria_atualizada)
        
    Raises:
        ExecutorError: para erros durante a execução
    """
    # inicializar contexto se necessário
    if historico_resultados is None:
        historico_resultados = []
    if memoria is None:
        memoria = {}
        
    contexto = {
        'historico_resultados': historico_resultados.copy(),
        'memoria': memoria.copy(),
        'pilha': [],
        'resultado_atual': None
    }
    
    try:
        # validar estrutura básica
        validar_expressao(tokens)
        
        # avaliar expressão RPN
        resultado = avaliar_rpn(tokens, contexto)
        
        # formatar resultado final
        resultado_formatado = formatar_resultado(resultado)
        contexto['resultado_atual'] = resultado_formatado
        
        # adicionar ao histórico
        contexto['historico_resultados'].append(resultado_formatado)
        
        return resultado_formatado, contexto['historico_resultados'], contexto['memoria']
        
    except ExecutorError:
        raise
    except Exception as e:
        raise ExecutorError(f"Erro interno durante execução: {str(e)}")

if __name__ == '__main__':
    # exemplo de uso
    from src.lexer import parse_expressao
    
    try:
        # exemplo básico
        # tokens = parse_expressao("(((1.5 2.0 *) (6.0 3.0 /) +))")
        # resultado, historico, memoria = executar_expressao(tokens)

        # print(f"Resultado: {resultado}")

        historico = []
        memoria = {}

        # expressao1 = "(42.5 MEM)"
        # tokens1 = parse_expressao(expressao1)
        # resultado1, historico, memoria = executar_expressao(tokens1, historico, memoria)
        
        # # Recuperar valor
        # expressao2 = "(MEM)"
        # tokens2 = parse_expressao(expressao2)
        # resultado2, historico, memoria = executar_expressao(tokens2, historico, memoria)
        
        # # Recuperar valor
        # expressao3 = "(77 VAR)"
        # tokens3 = parse_expressao(expressao3)
        # resultado3, historico, memoria = executar_expressao(tokens3, historico, memoria)

        # expressao4 = "(VAR 3 +)"
        # tokens4 = parse_expressao(expressao4)
        # resultado4, historico, memoria = executar_expressao(tokens4, historico,memoria)

        # print(resultado1)
        # print(resultado2)
        # print(resultado3)
        # print(resultado4)

        # print(30*"=")

        # print(memoria)

        from utils.util import ler_arquivo

        linhas = ler_arquivo("expressoes.txt")

        for linha in linhas:
            tokens = parse_expressao(linha)
            resultado, historico, memoria = executar_expressao(tokens, historico, memoria)
            print(historico)
            print(resultado)

    except (ExecutorError, Exception) as e:
        print(f"Erro: {e}")