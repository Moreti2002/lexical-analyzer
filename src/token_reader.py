# leitor de tokens salvos da fase 1

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *
from src.lexer import parse_expressao

class TokenReaderError(Exception):
    """exceção para erros na leitura de tokens"""
    def __init__(self, mensagem, linha=None):
        self.mensagem = mensagem
        self.linha = linha
        contexto = f" [linha {linha}]" if linha else ""
        super().__init__(f"Erro ao ler tokens{contexto}: {mensagem}")

def ler_tokens(nome_arquivo):
    """
    lê arquivo de tokens salvos ou expressões RPN
    
    Args:
        nome_arquivo (str): nome do arquivo
        
    Returns:
        list: lista de listas de tokens (uma lista por linha/expressão)
        
    Raises:
        TokenReaderError: em caso de erro na leitura
    """
    if not os.path.exists(nome_arquivo):
        raise TokenReaderError(f"Arquivo não encontrado: {nome_arquivo}")
    
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
        
        # verificar formato do arquivo
        if eh_arquivo_tokens_salvos(linhas):
            return ler_formato_tokens(linhas)
        else:
            return ler_formato_expressoes(linhas)
            
    except Exception as e:
        raise TokenReaderError(f"Erro ao ler arquivo: {str(e)}")

def eh_arquivo_tokens_salvos(linhas):
    """
    verifica se arquivo está no formato de tokens salvos
    
    Args:
        linhas (list): linhas do arquivo
        
    Returns:
        bool: True se é formato de tokens salvos
    """
    # formato de tokens salvos tem "Token N:" nas linhas
    for linha in linhas[:10]:  # verificar primeiras linhas
        if linha.strip().startswith("Token"):
            return True
    return False

def ler_formato_tokens(linhas):
    """
    lê arquivo no formato de tokens salvos (gerado por salvar_tokens)
    
    Args:
        linhas (list): linhas do arquivo
        
    Returns:
        list: lista de listas de tokens
    """
    tokens_por_expressao = []
    tokens_expressao_atual = []
    token_atual = {}
    
    for linha in linhas:
        linha = linha.strip()
        
        if not linha or linha.startswith("=") or linha.startswith("Tokens gerados"):
            continue
        
        if linha.startswith("Token"):
            # novo token
            if token_atual:
                tokens_expressao_atual.append(token_atual)
                token_atual = {}
            continue
        
        if linha.startswith("Tipo:"):
            tipo = linha.split(":", 1)[1].strip()
            token_atual['tipo'] = tipo
        
        elif linha.startswith("Valor:"):
            valor = linha.split(":", 1)[1].strip()
            token_atual['valor'] = valor
        
        elif linha.startswith("Posição:"):
            posicao = linha.split(":", 1)[1].strip()
            token_atual['posicao'] = int(posicao)
    
    # adicionar último token
    if token_atual:
        tokens_expressao_atual.append(token_atual)
    
    # adicionar expressão
    if tokens_expressao_atual:
        tokens_por_expressao.append(tokens_expressao_atual)
    
    return tokens_por_expressao

def ler_formato_expressoes(linhas):
    """
    lê arquivo com expressões RPN (uma por linha)
    
    Args:
        linhas (list): linhas do arquivo
        
    Returns:
        list: lista de listas de tokens
    """
    tokens_por_expressao = []
    
    for i, linha in enumerate(linhas, 1):
        linha = linha.strip()
        
        # pular linhas vazias ou comentários
        if not linha or linha.startswith('#'):
            continue
        
        try:
            # usar analisador léxico da fase 1
            tokens = parse_expressao(linha)
            tokens_por_expressao.append(tokens)
            
        except Exception as e:
            raise TokenReaderError(f"Erro ao tokenizar expressão: {str(e)}", linha=i)
    
    return tokens_por_expressao

def validar_tokens(tokens_lista):
    """
    validação básica da lista de tokens
    
    Args:
        tokens_lista (list): lista de tokens
        
    Returns:
        bool: True se válido
        
    Raises:
        TokenReaderError: se inválido
    """
    if not tokens_lista:
        raise TokenReaderError("Lista de tokens vazia")
    
    for tokens in tokens_lista:
        if not isinstance(tokens, list):
            raise TokenReaderError("Formato inválido: cada expressão deve ser uma lista")
        
        if len(tokens) < 3:
            raise TokenReaderError("Expressão muito curta")
        
        # verificar balanceamento de parênteses
        contador = 0
        for token in tokens:
            if not isinstance(token, dict):
                raise TokenReaderError("Token inválido: deve ser dicionário")
            
            if 'tipo' not in token or 'valor' not in token:
                raise TokenReaderError("Token sem tipo ou valor")
            
            if token['tipo'] == PARENTESE_ABRE:
                contador += 1
            elif token['tipo'] == PARENTESE_FECHA:
                contador -= 1
        
        if contador != 0:
            raise TokenReaderError("Parênteses não balanceados")
    
    return True

def converter_formato(linha):
    """
    converte linha de texto em dicionário de token
    
    Args:
        linha (str): linha no formato "tipo: valor"
        
    Returns:
        dict: token
    """
    partes = linha.split(":", 1)
    
    if len(partes) != 2:
        return None
    
    chave = partes[0].strip()
    valor = partes[1].strip()
    
    return {chave.lower(): valor}

def salvar_tokens_formato_simples(tokens_lista, nome_arquivo="tokens_simples.txt"):
    """
    salva tokens em formato simples (uma expressão por linha)
    
    Args:
        tokens_lista (list): lista de listas de tokens
        nome_arquivo (str): nome do arquivo de saída
    """
    try:
        with open(nome_arquivo, 'w') as arquivo:
            for i, tokens in enumerate(tokens_lista, 1):
                arquivo.write(f"# Expressão {i}\n")
                
                # reconstruir expressão
                expressao = ''.join([t['valor'] if t['tipo'] in [PARENTESE_ABRE, PARENTESE_FECHA, OPERADOR, OPERADOR_RELACIONAL]
                                    else t['valor'] + ' ' 
                                    for t in tokens])
                
                arquivo.write(expressao.strip() + '\n\n')
                
    except Exception as e:
        raise TokenReaderError(f"Erro ao salvar tokens: {str(e)}")

if __name__ == '__main__':
    # teste do leitor de tokens
    print("=== TESTE DO LEITOR DE TOKENS ===\n")
    
    # criar arquivo de teste
    with open("teste_tokens.txt", 'w') as f:
        f.write("(3 5 +)\n")
        f.write("((2 3 *) (4 2 /) /)\n")
        f.write("(42 MEM)\n")
        f.write("(MEM)\n")
        f.write("(1 RES)\n")
    
    try:
        # ler tokens
        tokens_lista = ler_tokens("teste_tokens.txt")
        
        print(f"Lidas {len(tokens_lista)} expressões\n")
        
        for i, tokens in enumerate(tokens_lista, 1):
            print(f"Expressão {i}:")
            print(f"  Tokens: {len(tokens)}")
            print(f"  Conteúdo: {[t['valor'] for t in tokens]}")
            print()
        
        # validar
        if validar_tokens(tokens_lista):
            print("✓ Todos os tokens são válidos")
        
        # salvar formato simples
        salvar_tokens_formato_simples(tokens_lista, "tokens_simples_saida.txt")
        print("\n✓ Tokens salvos em formato simples")
        
    except TokenReaderError as e:
        print(f"Erro: {e}")
    
    finally:
        # limpar arquivo de teste
        if os.path.exists("teste_tokens.txt"):
            os.remove("teste_tokens.txt")