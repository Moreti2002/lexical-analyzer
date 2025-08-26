# Analisador léxico com autômato finito determinístico

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class LexerError(Exception):
    """exceção para erros do analisador léxico"""
    def __init__(self, mensagem, posicao=None):
        self.mensagem = mensagem
        self.posicao = posicao
        super().__init__(f"Erro léxico{' na posição ' + str(posicao) if posicao else ''}: {mensagem}")

def criar_contexto():
    """
    cria o contexto inicial para análise léxica
    
    Returns:
        dict: contexto com estado inicial
    """
    return {
        'tokens': [],
        'buffer': '',
        'posicao': 0,
        'contador_parenteses': 0,
        'estado_atual': 'inicial'
    }

def adicionar_token_ao_contexto(contexto, tipo, valor):
    """
    adiciona um token ao contexto
    
    Args:
        contexto (dict): contexto da análise
        tipo (str): tipo do token
        valor (str): valor do token
    """
    token = criar_token(tipo, valor, contexto['posicao'] - len(valor))
    contexto['tokens'].append(token)

def limpar_buffer(contexto):
    """limpa o buffer do contexto"""
    contexto['buffer'] = ''

# Estados do AFD implementados como funções

def estado_inicial(char, contexto):
    """
    estado inicial - decide qual estado seguir baseado no caractere
    
    Args:
        char (str): caractere atual
        contexto (dict): contexto da análise
        
    Returns:
        str: próximo estado
    """
    if eh_espaco(char):
        return 'inicial'  # Ignora espaços
    elif eh_digito(char):
        contexto['buffer'] += char
        return 'numero'
    elif eh_letra_maiuscula(char):
        contexto['buffer'] += char
        return 'identificador'
    elif eh_operador_valido(char):
        adicionar_token_ao_contexto(contexto, OPERADOR, char)
        return 'inicial'
    elif eh_parentese_abre(char):
        contexto['contador_parenteses'] += 1
        adicionar_token_ao_contexto(contexto, PARENTESE_ABRE, char)
        return 'inicial'
    elif eh_parentese_fecha(char):
        if contexto['contador_parenteses'] <= 0:
            raise LexerError("Parêntese de fechamento sem abertura correspondente", contexto['posicao'])
        contexto['contador_parenteses'] -= 1
        adicionar_token_ao_contexto(contexto, PARENTESE_FECHA, char)
        return 'inicial'
    else:
        raise LexerError(f"Caractere inválido: '{char}'", contexto['posicao'])

def estado_numero(char, contexto):
    """
    estado para reconhecimento de números
    
    Args:
        char (str): caractere atual
        contexto (dict): contexto da análise
        
    Returns:
        str: próximo estado
    """
    if eh_digito(char):
        contexto['buffer'] += char
        return 'numero'
    elif eh_ponto_decimal(char):
        if '.' in contexto['buffer']:
            raise LexerError(f"Número malformado: múltiplos pontos decimais em '{contexto['buffer'] + char}'", 
                           contexto['posicao'] - len(contexto['buffer']))
        contexto['buffer'] += char
        return 'numero_decimal'
    else:
        # Finaliza o número inteiro
        adicionar_token_ao_contexto(contexto, NUMERO, contexto['buffer'])
        limpar_buffer(contexto)
        
        # Processa o caractere atual no estado inicial
        return processar_char_no_estado(char, contexto, 'inicial')

def estado_numero_decimal(char, contexto):
    """
    estado para números após o ponto decimal
    
    Args:
        char (str): caractere atual
        contexto (dict): contexto da análise
        
    Returns:
        str: próximo estado
    """
    if eh_digito(char):
        contexto['buffer'] += char
        return 'numero_decimal'
    elif eh_ponto_decimal(char):
        raise LexerError(f"Número malformado: múltiplos pontos decimais em '{contexto['buffer'] + char}'", 
                       contexto['posicao'] - len(contexto['buffer']))
    else:
        # Verifica se tem dígitos após o ponto
        if contexto['buffer'].endswith('.'):
            raise LexerError(f"Número malformado: ponto decimal sem dígitos subsequentes em '{contexto['buffer']}'", 
                           contexto['posicao'] - len(contexto['buffer']))
        
        # Finaliza o número decimal
        adicionar_token_ao_contexto(contexto, NUMERO, contexto['buffer'])
        limpar_buffer(contexto)
        
        # Processa o caractere atual no estado inicial
        return processar_char_no_estado(char, contexto, 'inicial')

def estado_identificador(char, contexto):
    """
    estado para reconhecimento de identificadores e palavras reservadas
    
    Args:
        char (str): caractere atual
        contexto (dict): contexto da análise
        
    Returns:
        str: próximo estado
    """
    if eh_letra_maiuscula(char):
        contexto['buffer'] += char
        return 'identificador'
    else:
        # Finaliza o identificador
        if eh_palavra_reservada(contexto['buffer']):
            adicionar_token_ao_contexto(contexto, PALAVRA_RESERVADA, contexto['buffer'])
        else:
            adicionar_token_ao_contexto(contexto, IDENTIFICADOR, contexto['buffer'])
        
        limpar_buffer(contexto)
        
        # Processa o caractere atual no estado inicial
        return processar_char_no_estado(char, contexto, 'inicial')

def processar_char_no_estado(char, contexto, estado):
    """
    processa um caractere em um estado específico
    
    Args:
        char (str): caractere a processar
        contexto (dict): contexto da análise
        estado (str): estado atual
        
    Returns:
        str: próximo estado
    """
    estados = {
        'inicial': estado_inicial,
        'numero': estado_numero,
        'numero_decimal': estado_numero_decimal,
        'identificador': estado_identificador
    }
    
    return estados[estado](char, contexto)

def finalizar_analise(contexto):
    """
    finaliza a análise léxica e valida o estado final
    
    Args:
        contexto (dict): contexto da análise
    """
    # Se há conteúdo no buffer, processa o token final
    if contexto['buffer']:
        if contexto['estado_atual'] == 'numero':
            adicionar_token_ao_contexto(contexto, NUMERO, contexto['buffer'])
        elif contexto['estado_atual'] == 'numero_decimal':
            if contexto['buffer'].endswith('.'):
                raise LexerError(f"Número malformado: ponto decimal sem dígitos subsequentes em '{contexto['buffer']}'")
            adicionar_token_ao_contexto(contexto, NUMERO, contexto['buffer'])
        elif contexto['estado_atual'] == 'identificador':
            if eh_palavra_reservada(contexto['buffer']):
                adicionar_token_ao_contexto(contexto, PALAVRA_RESERVADA, contexto['buffer'])
            else:
                adicionar_token_ao_contexto(contexto, IDENTIFICADOR, contexto['buffer'])
    
    # Verifica balanceamento de parênteses
    if contexto['contador_parenteses'] != 0:
        raise LexerError(f"Parênteses não balanceados: {contexto['contador_parenteses']} parênteses não fechados")

def validar_estrutura_rpn(tokens):
    """
    validação adicional para verificar estrutura básica de RPN
    
    Args:
        tokens (list): lista de tokens
    """
    if not tokens:
        raise LexerError("Expressão vazia")
    
    # Deve começar com parêntese de abertura
    if tokens[0]['tipo'] != PARENTESE_ABRE:
        raise LexerError("Expressão RPN deve começar com parêntese de abertura")
    
    # Deve terminar com parêntese de fechamento
    if tokens[-1]['tipo'] != PARENTESE_FECHA:
        raise LexerError("Expressão RPN deve terminar com parêntese de fechamento")

def parse_expressao(linha):
    """
    função principal do analisador léxico
    analisa uma linha RPN usando Autômato Finito Determinístico
    
    Args:
        linha (str): linha contendo expressão RPN
        
    Returns:
        list: lista de tokens reconhecidos
        
    Raises:
        LexerError: em caso de erro léxico
    """
    if not linha or not linha.strip():
        raise LexerError("Linha vazia ou apenas espaços")
    
    contexto = criar_contexto()
    
    try:
        # Processa cada caractere da linha
        for i, char in enumerate(linha):
            contexto['posicao'] = i + 1
            contexto['estado_atual'] = processar_char_no_estado(char, contexto, contexto['estado_atual'])
        
        # Finaliza a análise
        finalizar_analise(contexto)
        
        # Validação adicional da estrutura RPN
        validar_estrutura_rpn(contexto['tokens'])
        
        return contexto['tokens']
        
    except LexerError:
        raise
    except Exception as e:
        raise LexerError(f"Erro interno do analisador: {str(e)}")

def salvar_tokens(tokens, nome_arquivo="tokens.txt"):
    """
    salva os tokens gerados em um arquivo de texto
    
    Args:
        tokens (list): lista de tokens
        nome_arquivo (str): nome do arquivo de saída
    """
    try:
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write("Tokens gerados pelo analisador léxico:\n")
            arquivo.write("="*50 + "\n\n")
            
            for i, token in enumerate(tokens):
                arquivo.write(f"Token {i+1}:\n")
                arquivo.write(f"  Tipo: {token['tipo']}\n")
                arquivo.write(f"  Valor: {token['valor']}\n")
                if 'posicao' in token:
                    arquivo.write(f"  Posição: {token['posicao']}\n")
                arquivo.write("\n")
                
    except Exception as e:
        print(f"Erro ao salvar tokens: {e}")