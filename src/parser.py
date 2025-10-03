# analisador sintático descendente recursivo LL(1)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class ParserError(Exception):
    """exceção para erros sintáticos"""
    def __init__(self, mensagem, linha=None, posicao=None):
        self.mensagem = mensagem
        self.linha = linha
        self.posicao = posicao
        contexto = f" [linha {linha}]" if linha else ""
        contexto += f" [pos {posicao}]" if posicao else ""
        super().__init__(f"Erro sintático{contexto}: {mensagem}")

def criar_contexto_parser(tokens):
    """
    inicializa contexto do parser
    
    Args:
        tokens (list): lista de tokens
        
    Returns:
        dict: contexto com buffer, posição e pilha
    """
    return {
        'tokens': tokens,
        'posicao': 0,
        'pilha': [],
        'derivacao': []
    }

def token_atual(contexto):
    """
    retorna token atual sem avançar
    
    Args:
        contexto (dict): contexto do parser
        
    Returns:
        dict: token atual ou None se fim
    """
    pos = contexto['posicao']
    if pos < len(contexto['tokens']):
        return contexto['tokens'][pos]
    return None

def avancar_token(contexto):
    """
    avança para próximo token
    
    Args:
        contexto (dict): contexto do parser
    """
    contexto['posicao'] += 1

def match(tipo_esperado, contexto):
    """
    verifica se token atual é do tipo esperado e avança
    
    Args:
        tipo_esperado (str): tipo esperado do token
        contexto (dict): contexto do parser
        
    Returns:
        dict: token consumido
        
    Raises:
        ParserError: se token não corresponde
    """
    token = token_atual(contexto)
    
    if token is None:
        raise ParserError(f"Esperado {tipo_esperado}, encontrado fim de arquivo")
    
    if token['tipo'] != tipo_esperado:
        raise ParserError(
            f"Esperado {tipo_esperado}, encontrado {token['tipo']} ('{token['valor']}')",
            posicao=token.get('posicao')
        )
    
    avancar_token(contexto)
    return token

def match_valor(valor_esperado, contexto):
    """
    verifica se valor do token atual corresponde e avança
    
    Args:
        valor_esperado (str): valor esperado
        contexto (dict): contexto do parser
        
    Returns:
        dict: token consumido
        
    Raises:
        ParserError: se valor não corresponde
    """
    token = token_atual(contexto)
    
    if token is None:
        raise ParserError(f"Esperado '{valor_esperado}', encontrado fim de arquivo")
    
    if token['valor'] != valor_esperado:
        raise ParserError(
            f"Esperado '{valor_esperado}', encontrado '{token['valor']}'",
            posicao=token.get('posicao')
        )
    
    avancar_token(contexto)
    return token

def parsear(tokens, tabela_ll1):
    """
    função principal do parser LL(1)
    
    Args:
        tokens (list): lista de tokens
        tabela_ll1 (dict): tabela de análise LL(1)
        
    Returns:
        dict: estrutura de derivação
        
    Raises:
        ParserError: em caso de erro sintático
    """
    if not tokens:
        raise ParserError("Lista de tokens vazia")
    
    contexto = criar_contexto_parser(tokens)
    
    try:
        # inicia análise pelo símbolo inicial
        derivacao = parse_programa(contexto, tabela_ll1)
        
        # verifica se consumiu todos os tokens
        if token_atual(contexto) is not None:
            token = token_atual(contexto)
            raise ParserError(
                f"Tokens excedentes após expressão válida: '{token['valor']}'",
                posicao=token.get('posicao')
            )
        
        return {
            'derivacao': derivacao,
            'valido': True
        }
        
    except ParserError:
        raise
    except Exception as e:
        raise ParserError(f"Erro interno do parser: {str(e)}")

def parse_programa(contexto, tabela):
    """
    analisa PROGRAMA -> EXPRESSAO
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    return parse_expressao(contexto, tabela)

def parse_expressao(contexto, tabela):
    """
    analisa EXPRESSAO -> ( CONTEUDO )
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    match(PARENTESE_ABRE, contexto)
    
    conteudo = parse_conteudo(contexto, tabela)
    
    match(PARENTESE_FECHA, contexto)
    
    return {
        'tipo': 'EXPRESSAO',
        'conteudo': conteudo
    }

def parse_conteudo(contexto, tabela):
    """
    analisa CONTEUDO -> OPERACAO | COMANDO_MEM | COMANDO_RES | ESTRUTURA_CONTROLE
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    token = token_atual(contexto)
    
    if token is None:
        raise ParserError("Token esperado, encontrado fim de arquivo")
    
    # verificar tipo de conteúdo pelo lookahead
    
    # comando RES: (N RES)
    if token['tipo'] == NUMERO:
        # olhar próximo token
        pos_backup = contexto['posicao']
        avancar_token(contexto)
        proximo = token_atual(contexto)
        contexto['posicao'] = pos_backup  # voltar
        
        if proximo and proximo['tipo'] == PALAVRA_RESERVADA and proximo['valor'] == 'RES':
            return parse_comando_res(contexto, tabela)
        elif proximo and proximo['tipo'] == IDENTIFICADOR:
            # comando memória: (V MEM)
            return parse_comando_memoria(contexto, tabela)
        else:
            # operação aritmética
            return parse_operacao(contexto, tabela)
    
    # comando memória: (MEM)
    elif token['tipo'] == IDENTIFICADOR:
        # verificar se é só identificador ou operação
        pos_backup = contexto['posicao']
        avancar_token(contexto)
        proximo = token_atual(contexto)
        contexto['posicao'] = pos_backup
        
        if proximo and proximo['tipo'] == PARENTESE_FECHA:
            # apenas (MEM)
            return parse_comando_memoria(contexto, tabela)
        else:
            # operação com identificador
            return parse_operacao(contexto, tabela)
    
    # expressão aninhada ou estrutura de controle
    elif token['tipo'] == PARENTESE_ABRE:
        # pode ser operação com expressão aninhada ou estrutura de controle
        return parse_operacao_ou_estrutura(contexto, tabela)
    
    else:
        raise ParserError(
            f"Token inesperado no início de conteúdo: {token['tipo']} ('{token['valor']}')",
            posicao=token.get('posicao')
        )

def parse_operacao_ou_estrutura(contexto, tabela):
    """
    decide entre operação com expressão aninhada ou estrutura de controle
    """
    # salvar posição para backtracking se necessário
    # tentar analisar como operação primeiro
    return parse_operacao(contexto, tabela)

def parse_operacao(contexto, tabela):
    """
    analisa OPERACAO -> OPERANDO OPERANDO OPERADOR_ARIT
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    operando1 = parse_operando(contexto, tabela)
    operando2 = parse_operando(contexto, tabela)
    
    # verificar se é operador aritmético ou relacional
    token = token_atual(contexto)
    if token is None:
        raise ParserError("Esperado operador, encontrado fim de arquivo")
    
    if token['tipo'] == OPERADOR:
        operador = match(OPERADOR, contexto)
        return {
            'tipo': 'OPERACAO',
            'operador': operador['valor'],
            'operando1': operando1,
            'operando2': operando2
        }
    elif token['tipo'] == OPERADOR_RELACIONAL:
        # é uma condição, não operação aritmética
        operador = match(OPERADOR_RELACIONAL, contexto)
        
        # agora deve vir estruturas de controle
        # ler blocos e palavra reservada
        bloco1 = parse_expressao(contexto, tabela)
        
        token_estrutura = token_atual(contexto)
        if token_estrutura and token_estrutura['valor'] == 'IF':
            bloco2 = parse_expressao(contexto, tabela)
            match_valor('IF', contexto)
            return {
                'tipo': 'DECISAO',
                'condicao': {
                    'operando1': operando1,
                    'operando2': operando2,
                    'operador': operador['valor']
                },
                'bloco_verdadeiro': bloco1,
                'bloco_falso': bloco2
            }
        elif token_estrutura and token_estrutura['valor'] == 'WHILE':
            match_valor('WHILE', contexto)
            return {
                'tipo': 'LACO',
                'condicao': {
                    'operando1': operando1,
                    'operando2': operando2,
                    'operador': operador['valor']
                },
                'bloco': bloco1
            }
        else:
            raise ParserError(f"Esperado IF ou WHILE após condição, encontrado {token_estrutura}")
    else:
        raise ParserError(
            f"Esperado operador, encontrado {token['tipo']}",
            posicao=token.get('posicao')
        )

def parse_operando(contexto, tabela):
    """
    analisa OPERANDO -> numero | identificador | EXPRESSAO
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    token = token_atual(contexto)
    
    if token is None:
        raise ParserError("Esperado operando, encontrado fim de arquivo")
    
    if token['tipo'] == NUMERO:
        numero = match(NUMERO, contexto)
        return {
            'tipo': 'NUMERO',
            'valor': numero['valor']
        }
    
    elif token['tipo'] == IDENTIFICADOR:
        identificador = match(IDENTIFICADOR, contexto)
        return {
            'tipo': 'IDENTIFICADOR',
            'valor': identificador['valor']
        }
    
    elif token['tipo'] == PARENTESE_ABRE:
        # expressão aninhada
        return parse_expressao(contexto, tabela)
    
    else:
        raise ParserError(
            f"Esperado operando, encontrado {token['tipo']} ('{token['valor']}')",
            posicao=token.get('posicao')
        )

def parse_comando_memoria(contexto, tabela):
    """
    analisa COMANDO_MEM -> numero identificador | identificador
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    token = token_atual(contexto)
    
    if token['tipo'] == NUMERO:
        # armazenar: (V MEM)
        numero = match(NUMERO, contexto)
        identificador = match(IDENTIFICADOR, contexto)
        
        return {
            'tipo': 'COMANDO_ARMAZENAR',
            'valor': numero['valor'],
            'identificador': identificador['valor']
        }
    
    elif token['tipo'] == IDENTIFICADOR:
        # recuperar: (MEM)
        identificador = match(IDENTIFICADOR, contexto)
        
        return {
            'tipo': 'COMANDO_RECUPERAR',
            'identificador': identificador['valor']
        }
    
    else:
        raise ParserError(
            f"Esperado número ou identificador no comando de memória",
            posicao=token.get('posicao')
        )

def parse_comando_res(contexto, tabela):
    """
    analisa COMANDO_RES -> numero RES
    
    Args:
        contexto (dict): contexto do parser
        tabela (dict): tabela LL(1)
        
    Returns:
        dict: nó da derivação
    """
    numero = match(NUMERO, contexto)
    match_valor('RES', contexto)
    
    return {
        'tipo': 'COMANDO_RES',
        'n': numero['valor']
    }

if __name__ == '__main__':
    # teste do parser
    from src.lexer import parse_expressao as tokenizar
    from src.grammar import construir_gramatica
    
    try:
        # construir gramática
        gramatica_info = construir_gramatica()
        tabela = gramatica_info['tabela']
        
        # testar expressões
        expressoes_teste = [
            "(3 5 +)",
            "((2 3 *) (4 2 /) /)",
            "(42 MEM)",
            "(MEM)",
            "(1 RES)",
        ]
        
        print("=== TESTE DO PARSER ===\n")
        
        for expr in expressoes_teste:
            print(f"Expressão: {expr}")
            try:
                tokens = tokenizar(expr)
                resultado = parsear(tokens, tabela)
                print(f"  ✓ Válida")
                print(f"  Derivação: {resultado['derivacao']}")
            except ParserError as e:
                print(f"  ✗ Erro: {e}")
            print()
        
    except Exception as e:
        print(f"Erro: {e}")