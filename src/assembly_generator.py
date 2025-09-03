# Gerador de código Assembly para Arduino ATmega328P
# Compatível com PlatformIO/avr-gcc - Corrigido baseado no guia de compatibilidade

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_types import *

class AssemblyError(Exception):
    """Exceção para erros do gerador de assembly"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(f"Erro no gerador de assembly: {mensagem}")

def gerar_cabecalho_assembly():
    """
    Gera o cabeçalho do código assembly com configurações iniciais
    Compatível com PlatformIO/avr-gcc
    
    Returns:
        str: código assembly do cabeçalho
    """
    cabecalho = """#include <avr/io.h>

; === CONSTANTES ===
; Stack pointer para ATmega328P (RAMEND = 0x08FF)
.equ STACK_LOW, 0xFF
.equ STACK_HIGH, 0x08
.equ SPL_ADDR, 0x3D
.equ SPH_ADDR, 0x3E

; === UART CONSTANTES ===
.equ UCSR0A_ADDR, 0xC0
.equ UCSR0B_ADDR, 0xC1
.equ UCSR0C_ADDR, 0xC2
.equ UBRR0L_ADDR, 0xC4
.equ UBRR0H_ADDR, 0xC5
.equ UDR0_ADDR, 0xC6
.equ UDRE0_BIT, 5
.equ TXEN0_VAL, 8         ; Valor pré-calculado (1<<3)
.equ FORMAT_8N1, 6        ; Valor pré-calculado (1<<2)|(1<<1)
.equ BAUD_9600, 103       ; Para 9600 baud @ 16MHz

; === CÓDIGO ===
.section .text
.global main

main:
    rjmp start_program

start_program:
    ; Configurar stack pointer
    ldi r16, STACK_LOW
    out SPL_ADDR, r16
    ldi r16, STACK_HIGH
    out SPH_ADDR, r16
    
    ; Configurar UART 9600 baud @ 16MHz
    ldi r16, BAUD_9600
    sts UBRR0L_ADDR, r16
    ldi r16, 0
    sts UBRR0H_ADDR, r16
    
    ; Habilitar transmissão UART
    ldi r16, TXEN0_VAL
    sts UCSR0B_ADDR, r16
    
    ; Configurar formato: 8N1
    ldi r16, FORMAT_8N1
    sts UCSR0C_ADDR, r16
    
    ; Executar operação RPN
    call executar_rpn
    
loop_forever:
    rjmp loop_forever

"""
    return cabecalho

def gerar_funcao_serial_print():
    """
    Gera função para enviar dados via serial
    Com lógica condicional correta para impressão decimal
    
    Returns:
        str: código assembly para transmissão serial
    """
    codigo = """
; Função para transmitir um caractere via UART
; Entrada: r16 contém o caractere a ser enviado
uart_transmit:
    push r17
uart_wait:
    lds r17, UCSR0A_ADDR
    sbrs r17, UDRE0_BIT
    rjmp uart_wait
    
    sts UDR0_ADDR, r16
    pop r17
    ret

; Função para enviar um número de 8 bits como decimal via serial
; Entrada: r16 contém o número (0-255)
; Implementa lógica condicional correta
print_number:
    push r16
    push r17
    push r18
    push r19
    push r20
    
    mov r20, r16  ; Backup do número original
    
    ; Centenas
    ldi r17, 100
    call div_r16_r17  ; r16 / r17, resultado em r18, resto em r16
    cpi r18, 0
    breq check_tens   ; Pula centenas se zero
    
    ; Imprimir centenas
    ldi r17, 48       ; ASCII '0'
    add r18, r17
    mov r16, r18
    call uart_transmit
    ldi r19, 1        ; Flag indicando que já imprimiu algo
    rjmp print_tens_always
    
check_tens:
    ldi r19, 0        ; Flag indicando que não imprimiu centenas
    
print_tens_always:
    ; Dezenas  
    ldi r17, 10
    call div_r16_r17  ; r18 = quociente, r16 = resto
    
    ; Se não imprimiu centenas e dezenas = 0, pula
    cpi r19, 0
    brne print_tens   ; Se já imprimiu centenas, sempre imprime dezenas
    cpi r18, 0
    breq print_units  ; Se não imprimiu centenas e dezenas=0, vai para unidades
    
print_tens:
    ldi r17, 48       ; ASCII '0'
    add r18, r17
    mov r16, r18
    call uart_transmit
    
print_units:
    ; Unidades (sempre imprime)
    ldi r17, 48       ; ASCII '0'
    add r16, r17
    call uart_transmit
    
    ; Nova linha
    ldi r16, 13       ; Carriage return
    call uart_transmit
    ldi r16, 10       ; Line feed
    call uart_transmit
    
    pop r20
    pop r19
    pop r18
    pop r17
    pop r16
    ret

; Divisão: r16 / r17, quociente em r18, resto permanece em r16
div_r16_r17:
    ldi r18, 0
div_loop:
    cp r16, r17
    brlo div_done
    sub r16, r17
    inc r18
    rjmp div_loop
div_done:
    ret

"""
    return codigo

def gerar_operacao_soma(operando1, operando2):
    """
    Gera código assembly para soma de dois números inteiros
    
    Args:
        operando1 (int): primeiro operando
        operando2 (int): segundo operando
        
    Returns:
        str: código assembly para a operação
    """
    codigo = f"""
executar_rpn:
    ; Carregar operandos da expressão RPN
    ldi r20, {operando1}  ; primeiro operando
    ldi r21, {operando2}  ; segundo operando
    
    ; Executar soma
    add r20, r21
    
    ; Resultado está em r20, mover para r16 para impressão
    mov r16, r20
    call print_number
    
    ret

"""
    return codigo

def gerar_assembly_simples(tokens, nome_arquivo="codigo.s"):
    """
    Gera código assembly simples para uma operação de soma
    Compatível com PlatformIO/avr-gcc
    
    Args:
        tokens (list): lista de tokens da expressão RPN
        nome_arquivo (str): nome do arquivo de saída
        
    Returns:
        bool: True se geração foi bem-sucedida
    """
    try:
        # Validar se é uma soma simples: (NUM NUM +)
        if len(tokens) != 5:  # (, NUM, NUM, +, )
            raise AssemblyError("Suporte apenas para operação de soma simples: (A B +)")
            
        if (tokens[0]['tipo'] != PARENTESE_ABRE or 
            tokens[1]['tipo'] != NUMERO or
            tokens[2]['tipo'] != NUMERO or 
            tokens[3]['tipo'] != OPERADOR or tokens[3]['valor'] != '+' or
            tokens[4]['tipo'] != PARENTESE_FECHA):
            raise AssemblyError("Formato inválido. Use: (número número +)")
        
        # Extrair operandos (convertendo para inteiros)
        operando1 = int(float(tokens[1]['valor']))
        operando2 = int(float(tokens[2]['valor']))
        
        # Verificar limites (0-255 para simplicidade)
        if operando1 < 0 or operando1 > 255 or operando2 < 0 or operando2 > 255:
            raise AssemblyError("Operandos devem estar entre 0 e 255")
            
        if operando1 + operando2 > 255:
            raise AssemblyError("Resultado da soma excede 255")
        
        # Gerar código assembly completo
        codigo_completo = ""
        codigo_completo += gerar_cabecalho_assembly()
        codigo_completo += gerar_operacao_soma(operando1, operando2)
        codigo_completo += gerar_funcao_serial_print()
        
        # Salvar arquivo
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write(codigo_completo)
        
        resultado_esperado = operando1 + operando2
        print(f"✅ Assembly gerado com sucesso: {nome_arquivo}")
        print(f"📊 Operação: {operando1} + {operando2} = {resultado_esperado}")
        print(f"🔧 Compatível com PlatformIO/avr-gcc")
        
        return True
        
    except Exception as e:
        raise AssemblyError(f"Erro ao gerar assembly: {str(e)}")

if __name__ == '__main__':
    # Teste simples seguindo as correções
    from src.lexer import parse_expressao
    
    try:
        # Teste com soma simples
        expressao = "(5 3 +)"
        tokens = parse_expressao(expressao)
        
        print(f"🔍 Processando: {expressao}")
        print(f"🎯 Tokens: {[t['valor'] for t in tokens]}")
        
        sucesso = gerar_assembly_simples(tokens, "teste_soma.s")
        
        if sucesso:
            print("\n" + "="*50)
            print("✅ CÓDIGO ASSEMBLY GERADO COM SUCESSO!")
            print("="*50)
            print("📋 Para testar no Arduino:")
            print("1. Copie 'teste_soma.s' para 'src/main.s'")
            print("2. Configure platformio.ini conforme o guia")
            print("3. Execute: pio run --target upload")
            print("4. Abra monitor serial: pio device monitor")
            print("5. Resultado esperado: '8' no serial")
            print("="*50)
            
    except Exception as e:
        print(f"❌ Erro: {e}")