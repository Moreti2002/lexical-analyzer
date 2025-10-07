# gerador de árvore sintática abstrata (AST)

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SyntaxTreeError(Exception):
    """exceção para erros na árvore sintática"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(f"Erro na árvore sintática: {mensagem}")

def criar_no(tipo, valor=None, filhos=None):
    """
    cria nó da árvore sintática
    
    Args:
        tipo (str): tipo do nó
        valor (any): valor associado ao nó
        filhos (list): lista de nós filhos
        
    Returns:
        dict: nó da árvore
    """
    no = {
        'tipo': tipo,
        'valor': valor,
        'filhos': filhos if filhos else []
    }
    return no

def gerar_arvore(derivacao):
    """
    constrói árvore sintática a partir da derivação
    
    Args:
        derivacao (dict): estrutura de derivação do parser
        
    Returns:
        dict: raiz da árvore sintática
        
    Raises:
        SyntaxTreeError: em caso de erro
    """
    if not derivacao:
        raise SyntaxTreeError("Derivação vazia")
    
    try:
        return converter_derivacao_para_arvore(derivacao)
    except Exception as e:
        raise SyntaxTreeError(f"Erro ao gerar árvore: {str(e)}")

def converter_derivacao_para_arvore(derivacao):
    """
    converte estrutura de derivação em árvore
    
    Args:
        derivacao (dict): estrutura da derivação
        
    Returns:
        dict: nó da árvore
    """
    tipo = derivacao.get('tipo')
    
    if tipo == 'EXPRESSAO':
        # expressão tem conteúdo
        conteudo = derivacao.get('conteudo')
        filho = converter_derivacao_para_arvore(conteudo) if conteudo else None
        return criar_no('EXPRESSAO', None, [filho] if filho else [])
    
    elif tipo == 'OPERACAO':
        # operação tem operador e dois operandos
        operador = derivacao.get('operador')
        operando1 = converter_derivacao_para_arvore(derivacao.get('operando1'))
        operando2 = converter_derivacao_para_arvore(derivacao.get('operando2'))
        
        return criar_no('OPERACAO', operador, [operando1, operando2])
    
    elif tipo == 'NUMERO':
        # número é folha
        valor = derivacao.get('valor')
        return criar_no('NUMERO', valor, [])
    
    elif tipo == 'IDENTIFICADOR':
        # identificador é folha
        valor = derivacao.get('valor')
        return criar_no('IDENTIFICADOR', valor, [])
    
    elif tipo == 'COMANDO_ARMAZENAR':
        # comando de armazenar memória
        valor = derivacao.get('valor')
        identificador = derivacao.get('identificador')
        
        filho_valor = criar_no('NUMERO', valor, [])
        filho_id = criar_no('IDENTIFICADOR', identificador, [])
        
        return criar_no('COMANDO_ARMAZENAR', None, [filho_valor, filho_id])
    
    elif tipo == 'COMANDO_RECUPERAR':
        # comando de recuperar memória
        identificador = derivacao.get('identificador')
        filho_id = criar_no('IDENTIFICADOR', identificador, [])
        
        return criar_no('COMANDO_RECUPERAR', None, [filho_id])
    
    elif tipo == 'COMANDO_RES':
        # comando RES
        n = derivacao.get('n')
        filho_n = criar_no('NUMERO', n, [])
        
        return criar_no('COMANDO_RES', None, [filho_n])
    
    elif tipo == 'DECISAO':
        # estrutura IF
        condicao = derivacao.get('condicao')
        bloco_v = derivacao.get('bloco_verdadeiro')
        bloco_f = derivacao.get('bloco_falso')
        
        filho_cond = criar_no_condicao(condicao)
        filho_v = converter_derivacao_para_arvore(bloco_v)
        filho_f = converter_derivacao_para_arvore(bloco_f)
        
        return criar_no('DECISAO', 'IF', [filho_cond, filho_v, filho_f])
    
    elif tipo == 'LACO':
        # estrutura WHILE
        condicao = derivacao.get('condicao')
        bloco = derivacao.get('bloco')
        
        filho_cond = criar_no_condicao(condicao)
        filho_bloco = converter_derivacao_para_arvore(bloco)
        
        return criar_no('LACO', 'WHILE', [filho_cond, filho_bloco])
    
    else:
        raise SyntaxTreeError(f"Tipo desconhecido: {tipo}")

def criar_no_condicao(condicao):
    """
    cria nó para condição
    
    Args:
        condicao (dict): estrutura da condição
        
    Returns:
        dict: nó da condição
    """
    operador = condicao.get('operador')
    operando1 = converter_derivacao_para_arvore(condicao.get('operando1'))
    operando2 = converter_derivacao_para_arvore(condicao.get('operando2'))
    
    return criar_no('CONDICAO', operador, [operando1, operando2])

def imprimir_arvore(raiz, nivel=0, prefixo=""):
    """
    imprime árvore formatada
    
    Args:
        raiz (dict): nó raiz
        nivel (int): nível de indentação
        prefixo (str): prefixo para o nó
        
    Returns:
        str: representação textual da árvore
    """
    if not raiz:
        return ""
    
    resultado = ""
    indentacao = "  " * nivel
    
    # imprimir nó atual
    tipo = raiz.get('tipo', 'DESCONHECIDO')
    valor = raiz.get('valor')
    
    if valor is not None:
        resultado += f"{indentacao}{prefixo}{tipo}: {valor}\n"
    else:
        resultado += f"{indentacao}{prefixo}{tipo}\n"
    
    # imprimir filhos
    filhos = raiz.get('filhos', [])
    for i, filho in enumerate(filhos):
        if i == len(filhos) - 1:
            resultado += imprimir_arvore(filho, nivel + 1, "└─ ")
        else:
            resultado += imprimir_arvore(filho, nivel + 1, "├─ ")
    
    return resultado

def salvar_arvore(raiz, nome_arquivo="arvore.json"):
    """
    salva árvore em formato JSON
    
    Args:
        raiz (dict): nó raiz
        nome_arquivo (str): nome do arquivo
    """
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            json.dump(raiz, arquivo, indent=2, ensure_ascii=False)
    except Exception as e:
        raise SyntaxTreeError(f"Erro ao salvar árvore: {str(e)}")

def carregar_arvore(nome_arquivo):
    """
    carrega árvore de arquivo JSON
    
    Args:
        nome_arquivo (str): nome do arquivo
        
    Returns:
        dict: nó raiz
    """
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except Exception as e:
        raise SyntaxTreeError(f"Erro ao carregar árvore: {str(e)}")

def percorrer_pre_ordem(raiz, funcao):
    """
    percorre árvore em pré-ordem aplicando função
    
    Args:
        raiz (dict): nó raiz
        funcao (callable): função a aplicar em cada nó
    """
    if not raiz:
        return
    
    # visitar nó atual
    funcao(raiz)
    
    # visitar filhos
    for filho in raiz.get('filhos', []):
        percorrer_pre_ordem(filho, funcao)

def percorrer_pos_ordem(raiz, funcao):
    """
    percorre árvore em pós-ordem aplicando função
    
    Args:
        raiz (dict): nó raiz
        funcao (callable): função a aplicar em cada nó
    """
    if not raiz:
        return
    
    # visitar filhos primeiro
    for filho in raiz.get('filhos', []):
        percorrer_pos_ordem(filho, funcao)
    
    # visitar nó atual
    funcao(raiz)

def contar_nos(raiz):
    """
    conta número de nós na árvore
    
    Args:
        raiz (dict): nó raiz
        
    Returns:
        int: número de nós
    """
    if not raiz:
        return 0
    
    contador = 1  # conta o nó atual
    
    for filho in raiz.get('filhos', []):
        contador += contar_nos(filho)
    
    return contador

def calcular_altura(raiz):
    """
    calcula altura da árvore
    
    Args:
        raiz (dict): nó raiz
        
    Returns:
        int: altura da árvore
    """
    if not raiz or not raiz.get('filhos'):
        return 0
    
    alturas_filhos = [calcular_altura(filho) for filho in raiz['filhos']]
    
    return 1 + max(alturas_filhos) if alturas_filhos else 0

if __name__ == '__main__':
    # teste da árvore sintática
    print("=== TESTE DA ÁRVORE SINTÁTICA ===\n")
    
    # criar derivação de teste
    derivacao_teste = {
        'tipo': 'EXPRESSAO',
        'conteudo': {
            'tipo': 'OPERACAO',
            'operador': '+',
            'operando1': {
                'tipo': 'NUMERO',
                'valor': '3'
            },
            'operando2': {
                'tipo': 'NUMERO',
                'valor': '5'
            }
        }
    }
    
    try:
        # gerar árvore
        arvore = gerar_arvore(derivacao_teste)
        
        print("Árvore gerada:")
        print(imprimir_arvore(arvore))
        
        print(f"\nNúmero de nós: {contar_nos(arvore)}")
        print(f"Altura: {calcular_altura(arvore)}")
        
        # salvar árvore
        salvar_arvore(arvore, "teste_arvore.json")
        print("\n✓ Árvore salva em teste_arvore.json")
        
        # carregar árvore
        arvore_carregada = carregar_arvore("teste_arvore.json")
        print("✓ Árvore carregada com sucesso")
        
        # percorrer árvore
        print("\nPercurso pré-ordem:")
        percorrer_pre_ordem(arvore, lambda no: print(f"  {no['tipo']}: {no.get('valor', '')}"))
        
        print("\nPercurso pós-ordem:")
        percorrer_pos_ordem(arvore, lambda no: print(f"  {no['tipo']}: {no.get('valor', '')}"))
        
    except SyntaxTreeError as e:
        print(f"Erro: {e}")
    
    finally:
        # limpar arquivo de teste
        if os.path.exists("teste_arvore.json"):
            os.remove("teste_arvore.json")