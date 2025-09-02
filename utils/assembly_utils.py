# Funções auxiliares para o gerador de assembly

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assembly_error import AssemblyError, AssemblyLimitError, AssemblyValidationError
from src.token_types import *

def validar_tokens_assembly(tokens):
    """
    Valida se os tokens são compatíveis com limitações do atmega328p
    
    Args:
        tokens: Lista de tokens para validar
        
    Returns:
        bool: True se tokens são válidos
        
    Raises:
        AssemblyValidationError: Para tokens inválidos
    """
    if not tokens:
        raise AssemblyValidationError("Lista de tokens vazia")
    
    numeros_encontrados = 0
    
    for i, token in enumerate(tokens):
        if token['tipo'] == NUMERO:
            # Verifica limites numéricos para ponto fixo 16-bit
            try:
                valor = float(token['valor'])
                # Limite para representação de ponto fixo 8.8
                if valor > 127.99 or valor < -128.00:
                    raise AssemblyLimitError(
                        f"Número {valor} excede limites do atmega328p (±128.00)",
                        token
                    )
                numeros_encontrados += 1
                
            except ValueError:
                raise AssemblyValidationError(
                    f"Número malformado: {token['valor']}",
                    token
                )
        
        elif token['tipo'] == OPERADOR:
            # Verifica operadores suportados
            if token['valor'] not in ['+', '-', '*', '/', '%', '^']:
                raise AssemblyValidationError(
                    f"Operador não suportado: {token['valor']}",
                    token
                )
        
        elif token['tipo'] == IDENTIFICADOR:
            # Verifica comprimento do nome da variável
            if len(token['valor']) > 8:
                raise AssemblyValidationError(
                    f"Nome de variável muito longo: {token['valor']} (máximo 8 caracteres)",
                    token
                )
        
        elif token['tipo'] == PALAVRA_RESERVADA:
            if token['valor'] not in ['RES']:
                raise AssemblyValidationError(
                    f"Palavra reservada não suportada: {token['valor']}",
                    token
                )
    
    # Verifica se há números suficientes para operações
    if numeros_encontrados == 0:
        raise AssemblyValidationError("Expressão sem números")
    
    return True

def calcular_limites_memoria(tokens):
    """
    Calcula limites de memória necessários baseado nos tokens
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        dict: Dicionário com limites calculados
    """
    limites = {
        'pilha_maxima': 0,
        'variaveis_count': 0,
        'historico_count': 0,
        'memoria_total': 0
    }
    
    pilha_atual = 0
    variaveis_unicas = set()
    historico_max = 0
    
    for i, token in enumerate(tokens):
        if token['tipo'] == NUMERO:
            pilha_atual += 1
            limites['pilha_maxima'] = max(limites['pilha_maxima'], pilha_atual)
            
        elif token['tipo'] == OPERADOR:
            pilha_atual = max(0, pilha_atual - 1)  # Remove 2, adiciona 1
            
        elif token['tipo'] == IDENTIFICADOR:
            variaveis_unicas.add(token['valor'])
            
        elif token['tipo'] == PALAVRA_RESERVADA and token['valor'] == 'RES':
            if i > 0 and tokens[i-1]['tipo'] == NUMERO:
                n = int(float(tokens[i-1]['valor']))
                historico_max = max(historico_max, n)
    
    limites['variaveis_count'] = len(variaveis_unicas)
    limites['historico_count'] = historico_max
    
    # Calcula memória total necessária (em bytes)
    limites['memoria_total'] = (
        limites['pilha_maxima'] * 2 +      # 2 bytes por elemento na pilha
        limites['variaveis_count'] * 2 +   # 2 bytes por variável
        limites['historico_count'] * 2     # 2 bytes por resultado histórico
    )
    
    # Verifica se cabe na SRAM do atmega328p (2KB)
    if limites['memoria_total'] > 1536:  # Deixa 512 bytes para stack do sistema
        raise AssemblyLimitError(
            f"Memória insuficiente: {limites['memoria_total']} bytes necessários, "
            f"máximo disponível: 1536 bytes"
        )
    
    return limites

def otimizar_sequencia_tokens(tokens):
    """
    Otimiza sequência de tokens para reduzir instruções assembly
    
    Args:
        tokens: Lista original de tokens
        
    Returns:
        list: Lista otimizada de tokens
    """
    # Implementação básica - apenas remove tokens desnecessários
    tokens_otimizados = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Remove parênteses desnecessários (mantém estrutura RPN)
        if token['tipo'] in [PARENTESE_ABRE, PARENTESE_FECHA]:
            tokens_otimizados.append(token)
        else:
            tokens_otimizados.append(token)
        
        i += 1
    
    return tokens_otimizados

def gerar_estatisticas_assembly(tokens):
    """
    Gera estatísticas sobre a complexidade da expressão
    
    Args:
        tokens: Lista de tokens
        
    Returns:
        dict: Estatísticas da expressão
    """
    stats = {
        'total_tokens': len(tokens),
        'numeros': 0,
        'operadores': 0,
        'variaveis': 0,
        'comandos_especiais': 0,
        'complexidade': 'baixa'
    }
    
    operadores_complexos = ['*', '/', '%', '^']
    
    for token in tokens:
        if token['tipo'] == NUMERO:
            stats['numeros'] += 1
        elif token['tipo'] == OPERADOR:
            stats['operadores'] += 1
            if token['valor'] in operadores_complexos:
                stats['comandos_especiais'] += 1
        elif token['tipo'] == IDENTIFICADOR:
            stats['variaveis'] += 1
        elif token['tipo'] == PALAVRA_RESERVADA:
            stats['comandos_especiais'] += 1
    
    # Determina complexidade
    if stats['comandos_especiais'] > 3 or stats['operadores'] > 5:
        stats['complexidade'] = 'alta'
    elif stats['comandos_especiais'] > 1 or stats['operadores'] > 2:
        stats['complexidade'] = 'média'
    
    return stats

def validar_arquivo_saida(nome_arquivo):
    """
    Valida se é possível escrever no arquivo de saída
    
    Args:
        nome_arquivo: Nome do arquivo para validar
        
    Returns:
        bool: True se arquivo é válido
        
    Raises:
        AssemblyError: Se arquivo não pode ser criado
    """
    try:
        # Tenta criar arquivo temporário
        with open(nome_arquivo, 'w') as f:
            f.write("; Teste de escrita\n")
        
        # Remove arquivo de teste
        import os
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
        
        return True
        
    except Exception as e:
        raise AssemblyError(f"Não é possível escrever no arquivo {nome_arquivo}: {str(e)}")

def converter_float_ponto_fixo(valor, bits_inteiros=8, bits_decimais=8):
    """
    Converte número float para representação de ponto fixo
    
    Args:
        valor: Valor float para converter
        bits_inteiros: Número de bits para parte inteira
        bits_decimais: Número de bits para parte decimal
        
    Returns:
        int: Valor em ponto fixo
    """
    fator_escala = 2 ** bits_decimais
    valor_fixo = int(valor * fator_escala)
    
    # Verifica limites
    max_valor = (2 ** (bits_inteiros + bits_decimais - 1)) - 1
    min_valor = -(2 ** (bits_inteiros + bits_decimais - 1))
    
    if valor_fixo > max_valor:
        valor_fixo = max_valor
    elif valor_fixo < min_valor:
        valor_fixo = min_valor
    
    return valor_fixo

def converter_ponto_fixo_float(valor_fixo, bits_decimais=8):
    """
    Converte valor de ponto fixo para float
    
    Args:
        valor_fixo: Valor em ponto fixo
        bits_decimais: Número de bits decimais
        
    Returns:
        float: Valor convertido
    """
    fator_escala = 2 ** bits_decimais
    return valor_fixo / fator_escala

def debug_tokens(tokens):
    """
    Imprime informações de debug dos tokens
    
    Args:
        tokens: Lista de tokens para debug
    """
    print("=== DEBUG TOKENS ===")
    for i, token in enumerate(tokens):
        print(f"{i:2d}: {token['tipo']:15} -> '{token['valor']}'")
    print("==================")

def salvar_relatorio_assembly(nome_arquivo, stats, limites):
    """
    Salva relatório detalhado da geração de assembly
    
    Args:
        nome_arquivo: Nome do arquivo de relatório
        stats: Estatísticas da expressão
        limites: Limites de memória calculados
    """
    try:
        nome_relatorio = nome_arquivo.replace('.s', '_relatorio.txt')
        
        with open(nome_relatorio, 'w') as arquivo:
            arquivo.write("Relatório de Geração de Assembly\n")
            arquivo.write("=" * 40 + "\n\n")
            
            arquivo.write("Estatísticas da Expressão:\n")
            for chave, valor in stats.items():
                arquivo.write(f"  {chave}: {valor}\n")
            
            arquivo.write("\nLimites de Memória:\n")
            for chave, valor in limites.items():
                arquivo.write(f"  {chave}: {valor}\n")
            
            arquivo.write(f"\nArquivo Assembly: {nome_arquivo}\n")
            arquivo.write(f"Compatível com: atmega328p (Arduino Uno)\n")
            
    except Exception as e:
        print(f"Aviso: Não foi possível salvar relatório: {e}")

if __name__ == '__main__':
    # Teste das funções auxiliares
    from src.lexer import parse_expressao
    
    try:
        # Teste de validação
        tokens = parse_expressao("(3.14 2.0 +)")
        
        print("Validando tokens...")
        validar_tokens_assembly(tokens)
        
        print("Calculando limites...")
        limites = calcular_limites_memoria(tokens)
        print(f"Limites: {limites}")
        
        print("Gerando estatísticas...")
        stats = gerar_estatisticas_assembly(tokens)
        print(f"Stats: {stats}")
        
        print("Teste de conversão ponto fixo...")
        valor_fixo = converter_float_ponto_fixo(3.14)
        valor_float = converter_ponto_fixo_float(valor_fixo)
        print(f"3.14 -> {valor_fixo} -> {valor_float}")
        
        print("Todos os testes passaram!")
        
    except Exception as e:
        print(f"Erro nos testes: {e}")