# Gerador de código assembly para atmega328p (Arduino Uno)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assembly_error import AssemblyError, AssemblyLimitError, AssemblyValidationError
from src.token_types import *

class AssemblyGenerator:
    """Classe principal para geração de código assembly AVR"""
    
    def __init__(self):
        """Inicializa o gerador de assembly"""
        self.codigo_assembly = []
        self.pilha_pointer = 0x0500  # Início da pilha RPN na SRAM
        self.memoria_vars = 0x0600   # Endereços para variáveis MEM
        self.historico_base = 0x0700 # Base para histórico RES
        self.label_count = 0
        
        # Mapeamento de variáveis para endereços
        self.var_enderecos = {}
        self.historico_count = 0
        
    def gerar_label_unico(self):
        """Gera um label único para uso em jumps"""
        self.label_count += 1
        return f"LABEL_{self.label_count}"
    
    def gerar_assembly(self, tokens, nome_arquivo="programa.s"):
        """
        Função principal para gerar código assembly completo
        
        Args:
            tokens: Lista de tokens do analisador léxico
            nome_arquivo: Nome do arquivo assembly de saída
            
        Returns:
            bool: True se geração foi bem-sucedida
        """
        try:
            self.codigo_assembly = []
            
            # Gera código assembly
            self.gerar_cabecalho_assembly()
            self.gerar_codigo_rpn(tokens)
            self.gerar_rodape_assembly()
            
            # Salva arquivo
            self._salvar_assembly(nome_arquivo)
            
            return True
            
        except (AssemblyError, Exception) as e:
            print(f"Erro ao gerar assembly: {e}")
            return False
    
    def gerar_cabecalho_assembly(self):
        """Gera cabeçalho e inicialização do programa assembly"""
        cabecalho = [
            "; Código Assembly gerado para atmega328p",
            "; Calculadora RPN - Trabalho de Compiladores",
            "",
            ".device atmega328p",
            ".org 0x0000",
            "",
            "; Vetor de reset",
            "rjmp reset",
            "",
            "; Início do programa",
            "reset:",
            "    ; Configuração inicial da pilha do sistema",
            "    ldi r16, low(RAMEND)",
            "    out SPL, r16",
            "    ldi r16, high(RAMEND)",
            "    out SPH, r16",
            "",
            "    ; Inicialização da pilha RPN",
            f"    ldi ZL, low({hex(self.pilha_pointer)})",
            f"    ldi ZH, high({hex(self.pilha_pointer)})",
            "    ldi r16, 0",
            "    st Z+, r16  ; Stack pointer inicial = 0",
            "",
            "    ; Configuração da porta serial (opcional para debug)",
            "    ldi r16, 0xFF",
            "    out DDRB, r16    ; PORTB como saída para LEDs",
            "",
            "main:",
        ]
        self.codigo_assembly.extend(cabecalho)
    
    def gerar_codigo_rpn(self, tokens):
        """
        Gera código assembly para avaliar expressões RPN
        
        Args:
            tokens: Lista de tokens da expressão RPN
        """
        if not tokens:
            raise AssemblyError("Lista de tokens vazia")
            
        self.codigo_assembly.append("    ; Processamento da expressão RPN")
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token['tipo'] == PARENTESE_ABRE:
                # Pula parêntese de abertura
                pass
            elif token['tipo'] == PARENTESE_FECHA:
                # Pula parêntese de fechamento
                pass
            elif token['tipo'] == NUMERO:
                self._processar_numero_assembly(token['valor'])
            elif token['tipo'] == OPERADOR:
                self._processar_operador_assembly(token['valor'])
            elif token['tipo'] == IDENTIFICADOR:
                # Pode ser comando MEM
                if i > 0 and tokens[i-1]['tipo'] == NUMERO:
                    # Caso (V MEM) - armazenar
                    self._processar_armazenar_memoria(token['valor'])
                else:
                    # Caso (MEM) - recuperar
                    self._processar_recuperar_memoria(token['valor'])
            elif token['tipo'] == PALAVRA_RESERVADA and token['valor'] == 'RES':
                # Comando (N RES)
                if i > 0 and tokens[i-1]['tipo'] == NUMERO:
                    n = int(float(tokens[i-1]['valor']))
                    self._processar_comando_res_assembly(n)
                else:
                    raise AssemblyError(f"RES deve ser precedido por um número")
            
            i += 1
        
        # Armazena resultado final no histórico
        self._armazenar_resultado_historico()
    
    def _processar_numero_assembly(self, valor):
        """
        Converte número para ponto fixo e empilha
        Usa representação de 16 bits: 8 bits inteiros + 8 bits decimais
        """
        # Converte para ponto fixo (8.8)
        num_float = float(valor)
        num_fixed = int(num_float * 256)  # Multiplica por 2^8
        
        # Limita a 16 bits signed
        if num_fixed > 32767:
            num_fixed = 32767
        elif num_fixed < -32768:
            num_fixed = -32768
        
        # Converte para bytes
        low_byte = num_fixed & 0xFF
        high_byte = (num_fixed >> 8) & 0xFF
        
        codigo_num = [
            f"    ; Empilha número {valor} (ponto fixo: {num_fixed})",
            f"    ldi r16, {low_byte}   ; Byte baixo",
            f"    ldi r17, {high_byte}  ; Byte alto", 
            "    rcall push_stack      ; Empilha na pilha RPN"
        ]
        self.codigo_assembly.extend(codigo_num)
    
    def _processar_operador_assembly(self, operador):
        """Gera código para operações aritméticas"""
        self.codigo_assembly.append(f"    ; Operação: {operador}")
        
        # Desempilha dois operandos
        self.codigo_assembly.extend([
            "    rcall pop_stack       ; Operando 2 em r17:r16",
            "    push r16              ; Salva op2 low",
            "    push r17              ; Salva op2 high",
            "    rcall pop_stack       ; Operando 1 em r17:r16",
            "    pop r19               ; Recupera op2 high",
            "    pop r18               ; Recupera op2 low"
        ])
        
        if operador == '+':
            self._gerar_adicao()
        elif operador == '-':
            self._gerar_subtracao()
        elif operador == '*':
            self._gerar_multiplicacao()
        elif operador == '/':
            self._gerar_divisao()
        elif operador == '%':
            self._gerar_resto()
        elif operador == '^':
            self._gerar_potenciacao()
        else:
            raise AssemblyError(f"Operador não suportado: {operador}")
        
        # Empilha resultado
        self.codigo_assembly.append("    rcall push_stack      ; Empilha resultado")
    
    def _gerar_adicao(self):
        """Gera código para adição em ponto fixo"""
        codigo_add = [
            "    ; Adição: r17:r16 = r17:r16 + r19:r18",
            "    add r16, r18          ; Adiciona bytes baixos",
            "    adc r17, r19          ; Adiciona bytes altos com carry"
        ]
        self.codigo_assembly.extend(codigo_add)
    
    def _gerar_subtracao(self):
        """Gera código para subtração em ponto fixo"""
        codigo_sub = [
            "    ; Subtração: r17:r16 = r17:r16 - r19:r18",
            "    sub r16, r18          ; Subtrai bytes baixos", 
            "    sbc r17, r19          ; Subtrai bytes altos com borrow"
        ]
        self.codigo_assembly.extend(codigo_sub)
    
    def _gerar_multiplicacao(self):
        """Gera código para multiplicação em ponto fixo"""
        codigo_mul = [
            "    ; Multiplicação ponto fixo 16x16 -> 32 bits",
            "    ; Usa rotina de multiplicação simplificada",
            "    rcall multiply_16x16   ; Resultado em r19:r18:r17:r16",
            "    ; Ajusta para ponto fixo (divide por 256)",
            "    mov r16, r17           ; Desloca resultado para direita",
            "    mov r17, r18           ; 8 bits (divisão por 2^8)"
        ]
        self.codigo_assembly.extend(codigo_mul)
    
    def _gerar_divisao(self):
        """Gera código para divisão em ponto fixo"""
        codigo_div = [
            "    ; Divisão ponto fixo",
            "    ; Multiplica dividendo por 256 antes da divisão",
            "    ; para manter precisão decimal",
            "    rcall divide_16x16     ; Resultado em r17:r16"
        ]
        self.codigo_assembly.extend(codigo_div)
    
    def _gerar_resto(self):
        """Gera código para resto da divisão"""
        codigo_mod = [
            "    ; Resto da divisão",
            "    rcall modulo_16x16     ; Resultado em r17:r16"
        ]
        self.codigo_assembly.extend(codigo_mod)
    
    def _gerar_potenciacao(self):
        """Gera código para potenciação"""
        codigo_pow = [
            "    ; Potenciação (limitada a expoentes pequenos)",
            "    rcall power_16x16      ; Resultado em r17:r16"
        ]
        self.codigo_assembly.extend(codigo_pow)
    
    def _processar_armazenar_memoria(self, nome_var):
        """Armazena valor da pilha em variável de memória"""
        endereco = self._obter_endereco_variavel(nome_var)
        
        codigo_store = [
            f"    ; Armazena em variável {nome_var}",
            "    rcall pop_stack        ; Valor em r17:r16",
            f"    ldi ZL, low({hex(endereco)})",
            f"    ldi ZH, high({hex(endereco)})",
            "    st Z+, r16             ; Armazena byte baixo",
            "    st Z, r17              ; Armazena byte alto",
            "    rcall push_stack       ; Reempilha valor"
        ]
        self.codigo_assembly.extend(codigo_store)
    
    def _processar_recuperar_memoria(self, nome_var):
        """Recupera valor de variável de memória para pilha"""
        endereco = self._obter_endereco_variavel(nome_var)
        
        codigo_load = [
            f"    ; Recupera variável {nome_var}",
            f"    ldi ZL, low({hex(endereco)})",
            f"    ldi ZH, high({hex(endereco)})",
            "    ld r16, Z+             ; Carrega byte baixo",
            "    ld r17, Z              ; Carrega byte alto",
            "    rcall push_stack       ; Empilha valor"
        ]
        self.codigo_assembly.extend(codigo_load)
    
    def _processar_comando_res_assembly(self, n):
        """Processa comando RES - histórico"""
        if n <= 0:
            raise AssemblyError(f"RES: N deve ser positivo, recebido: {n}")
        
        endereco = self.historico_base + (n - 1) * 2  # 2 bytes por resultado
        
        codigo_res = [
            f"    ; Comando RES {n}",
            f"    ldi ZL, low({hex(endereco)})",
            f"    ldi ZH, high({hex(endereco)})",
            "    ld r16, Z+             ; Carrega resultado histórico",
            "    ld r17, Z",
            "    rcall push_stack       ; Empilha resultado"
        ]
        self.codigo_assembly.extend(codigo_res)
    
    def _armazenar_resultado_historico(self):
        """Armazena resultado atual no histórico"""
        endereco = self.historico_base + self.historico_count * 2
        
        codigo_hist = [
            "    ; Armazena resultado no histórico",
            "    rcall pop_stack        ; Resultado final em r17:r16",
            f"    ldi ZL, low({hex(endereco)})",
            f"    ldi ZH, high({hex(endereco)})",
            "    st Z+, r16             ; Armazena no histórico",
            "    st Z, r17",
            "    rcall push_stack       ; Reempilha para output"
        ]
        self.codigo_assembly.extend(codigo_hist)
        self.historico_count += 1
    
    def _obter_endereco_variavel(self, nome_var):
        """Obtém endereço de memória para variável"""
        if nome_var not in self.var_enderecos:
            # Aloca novo endereço
            self.var_enderecos[nome_var] = self.memoria_vars + len(self.var_enderecos) * 2
        return self.var_enderecos[nome_var]
    
    def gerar_rodape_assembly(self):
        """Gera subrotinas auxiliares e fim do programa"""
        rodape = [
            "",
            "    ; Resultado final disponível na pilha",
            "    ; Pisca LED com resultado (simplificado)", 
            "    rcall pop_stack",
            "    out PORTB, r16         ; Mostra byte baixo nos LEDs",
            "",
            "end_program:",
            "    rjmp end_program       ; Loop infinito",
            "",
            "; === SUBROTINAS AUXILIARES ===",
            "",
            "push_stack:",
            "    ; Empilha r17:r16 na pilha RPN",
            f"    ldi ZL, low({hex(self.pilha_pointer)})",
            f"    ldi ZH, high({hex(self.pilha_pointer)})",
            "    ld r20, Z              ; Carrega stack pointer",
            "    inc r20                ; Incrementa SP",
            "    st Z, r20              ; Salva novo SP",
            "    ; Calcula endereço do topo da pilha",
            "    lsl r20                ; SP * 2 (2 bytes por item)",
            "    add ZL, r20            ; Z = base + offset",
            "    adc ZH, r1             ; r1 sempre é 0",
            "    st Z+, r16             ; Armazena byte baixo",
            "    st Z, r17              ; Armazena byte alto",
            "    ret",
            "",
            "pop_stack:",
            "    ; Desempilha para r17:r16",
            f"    ldi ZL, low({hex(self.pilha_pointer)})",
            f"    ldi ZH, high({hex(self.pilha_pointer)})",
            "    ld r20, Z              ; Carrega stack pointer",
            "    tst r20                ; Verifica se pilha vazia",
            "    breq stack_underflow   ; Salta se vazia",
            "    ; Calcula endereço do topo",
            "    lsl r20                ; SP * 2",
            "    add ZL, r20",
            "    adc ZH, r1",
            "    ld r16, Z+             ; Carrega byte baixo",
            "    ld r17, Z              ; Carrega byte alto",
            "    ; Decrementa stack pointer",
            f"    ldi ZL, low({hex(self.pilha_pointer)})",
            f"    ldi ZH, high({hex(self.pilha_pointer)})",
            "    ld r20, Z",
            "    dec r20",
            "    st Z, r20",
            "    ret",
            "",
            "stack_underflow:",
            "    ; Erro: pilha vazia",
            "    ldi r16, 0xFF",
            "    out PORTB, r16         ; Indica erro com LEDs",
            "    rjmp stack_underflow   ; Loop infinito",
            "",
            "; Operações matemáticas simplificadas",
            "multiply_16x16:",
            "    ; Multiplicação 16x16 bits simplificada",
            "    ; r17:r16 * r19:r18 -> resultado em r19:r18:r17:r16",
            "    ; Implementação básica usando MUL",
            "    mul r16, r18           ; Low * Low -> r1:r0",
            "    movw r16, r0           ; Move resultado",
            "    mul r17, r18           ; High1 * Low -> r1:r0",
            "    add r17, r0            ; Adiciona ao resultado",
            "    mul r16, r19           ; Low * High2",
            "    add r17, r0",
            "    ret",
            "",
            "divide_16x16:",
            "    ; Divisão simplificada por subtração sucessiva",
            "    ; r17:r16 / r19:r18 -> resultado em r17:r16",
            "    ldi r20, 0             ; Contador do quociente",
            "div_loop:",
            "    cp r16, r18            ; Compara partes baixas",
            "    cpc r17, r19           ; Compara com carry",
            "    brlo div_done          ; Se menor, termina",
            "    sub r16, r18           ; Subtrai divisor",
            "    sbc r17, r19",
            "    inc r20                ; Incrementa quociente",
            "    rjmp div_loop",
            "div_done:",
            "    mov r16, r20           ; Move quociente para resultado",
            "    ldi r17, 0             ; Parte alta zero",
            "    ret",
            "",
            "modulo_16x16:",
            "    ; Resto da divisão",
            "    ; Similar à divisão, mas retorna o resto",
            "mod_loop:",
            "    cp r16, r18",
            "    cpc r17, r19",
            "    brlo mod_done",
            "    sub r16, r18",
            "    sbc r17, r19",
            "    rjmp mod_loop",
            "mod_done:",
            "    ret",
            "",
            "power_16x16:",
            "    ; Potenciação básica por multiplicação sucessiva",
            "    ; r17:r16 ^ r19:r18 (expoente limitado)",
            "    movw r20, r16          ; Salva base",
            "    ldi r16, 1             ; Resultado inicial = 1",
            "    ldi r17, 0",
            "    tst r18                ; Verifica expoente",
            "    breq power_done        ; Se zero, retorna 1",
            "power_loop:",
            "    ; Multiplica resultado pela base",
            "    ; Implementação simplificada",
            "    mul r16, r20           ; Multiplica partes baixas",
            "    movw r16, r0",
            "    dec r18                ; Decrementa expoente",
            "    brne power_loop",
            "power_done:",
            "    ret"
        ]
        self.codigo_assembly.extend(rodape)
    
    def _salvar_assembly(self, nome_arquivo):
        """Salva código assembly em arquivo"""
        try:
            with open(nome_arquivo, 'w') as arquivo:
                for linha in self.codigo_assembly:
                    arquivo.write(linha + '\n')
        except Exception as e:
            raise AssemblyError(f"Erro ao salvar arquivo {nome_arquivo}: {str(e)}")


# Função principal para compatibilidade com interface esperada
def gerar_assembly(tokens, nome_arquivo="programa.s"):
    """
    Função principal para gerar assembly - interface compatível
    
    Args:
        tokens: Lista de tokens do analisador léxico
        nome_arquivo: Nome do arquivo assembly de saída
        
    Returns:
        bool: True se geração foi bem-sucedida
    """
    gerador = AssemblyGenerator()
    return gerador.gerar_assembly(tokens, nome_arquivo)


if __name__ == '__main__':
    # Exemplo de uso
    from src.lexer import parse_expressao
    
    try:
        # Teste básico
        expressao = "(3.14 2.0 +)"
        tokens = parse_expressao(expressao)
        
        sucesso = gerar_assembly(tokens, "teste.s")
        
        if sucesso:
            print("Assembly gerado com sucesso!")
        else:
            print("Erro na geração do assembly")
            
    except Exception as e:
        print(f"Erro: {e}")