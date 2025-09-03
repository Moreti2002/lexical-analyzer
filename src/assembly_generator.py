# Gerador de código Assembly para Arduino ATmega328P
# Compatível com PlatformIO/avr-gcc - Versão Completa Corrigida
# Executa TODAS as operações RPN em sequência

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
    
    ; Executar operações RPN
    call executar_rpn
    
loop_forever:
    rjmp loop_forever

"""
    return cabecalho

def gerar_todas_operacoes_rpn():
    """
    Gera código assembly para executar TODAS as operações RPN em sequência
    Conforme especificado: (5 3 +), (10 4 -), (7 6 *), (20 4 /), (17 5 %), (3 4 ^)
    
    Returns:
        str: código assembly para todas as operações
    """
    codigo = """
executar_rpn:
    ; === (5 3 +) - Soma: 5 + 3 = 8 ===
    ldi r20, 5
    ldi r21, 3
    add r20, r21
    mov r16, r20
    call print_number
    
    ; === (10 4 -) - Subtração: 10 - 4 = 6 ===
    ldi r20, 10
    ldi r21, 4
    sub r20, r21
    mov r16, r20
    call print_number
    
    ; === (7 6 *) - Multiplicação: 7 * 6 = 42 ===
    ldi r20, 7
    ldi r21, 6
    call multiply_r20_r21
    mov r16, r20
    call print_number
    
    ; === (20 4 /) - Divisão: 20 / 4 = 5 ===
    ldi r16, 20
    ldi r17, 4
    call div_r16_r17  ; Quociente em r18
    mov r16, r18
    call print_number
    
    ; === (17 5 %) - Resto: 17 % 5 = 2 ===
    ldi r16, 17
    ldi r17, 5
    call div_r16_r17  ; Resto em r16
    call print_number
    
    ; === (3 4 ^) - Potenciação: 3 ^ 4 = 81 ===
    ldi r20, 3
    ldi r21, 4
    call power_r20_r21
    mov r16, r20
    call print_number
    
    ret

"""
    return codigo

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
; CORRIGIDA para evitar corrupção de registradores
print_number:
    push r16
    push r17
    push r18
    push r19
    push r20
    
    mov r20, r16  ; Backup do número original
    
    ; Centenas
    ldi r17, 100
    call div_r16_r17  ; r18 = centenas, r16 = resto
    cpi r18, 0
    breq check_tens   ; Pula centenas se zero
    
    ; Imprimir centenas
    ldi r17, 48       ; ASCII '0'
    add r18, r17
    mov r16, r18
    call uart_transmit
    
    ; Restaurar e recalcular para dezenas
    mov r16, r20      ; Restaurar número original
    ldi r17, 100
    call div_r16_r17  ; Pegar resto das centenas
    ldi r19, 1        ; Flag: já imprimiu centenas
    rjmp calc_tens
    
check_tens:
    ldi r19, 0        ; Flag: não imprimiu centenas
    mov r16, r20      ; Restaurar número original
    
calc_tens:
    ldi r17, 10
    call div_r16_r17  ; r18 = dezenas, r16 = unidades
    
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
    
    ; Restaurar para calcular unidades corretamente
    mov r16, r20      ; Restaurar número original
    ldi r17, 10
    call div_r16_r17  ; r16 agora contém unidades corretas
    
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

; Multiplicação: r20 * r21, resultado em r20
; CORRIGIDA conforme especificação
multiply_r20_r21:
    push r22
    mov r22, r20      ; Backup de r20 (multiplicando)
    ldi r20, 0        ; Resultado = 0
    cpi r21, 0        ; Se multiplicador = 0
    breq mult_done
mult_loop:
    add r20, r22      ; Soma r22 ao resultado
    dec r21           ; Decrementa contador
    brne mult_loop    ; Continua se não chegou a zero
mult_done:
    pop r22
    ret

; Potenciação: r20 ^ r21, resultado em r20
; CORRIGIDA conforme especificação
power_r20_r21:
    push r22
    push r23
    mov r22, r20      ; Base
    mov r23, r21      ; Backup do expoente
    ldi r20, 1        ; Resultado inicial = 1
    cpi r23, 0        ; Se expoente = 0
    breq power_done   ; Resultado = 1
power_loop:
    push r21
    mov r21, r22      ; Base como multiplicador
    call multiply_r20_r21  ; r20 = r20 * r21
    pop r21
    dec r23           ; Decrementa expoente
    brne power_loop   ; Continua se não chegou a zero
power_done:
    pop r23
    pop r22
    ret

"""
    return codigo

def gerar_assembly_completo(nome_arquivo="todas_operacoes.s"):
    """
    Gera código assembly completo executando TODAS as operações RPN:
    (5 3 +), (10 4 -), (7 6 *), (20 4 /), (17 5 %), (3 4 ^)
    
    Args:
        nome_arquivo (str): nome do arquivo de saída
        
    Returns:
        bool: True se geração foi bem-sucedida
    """
    try:
        print("Gerando código assembly para TODAS as operações RPN...")
        print("Operações: (5 3 +), (10 4 -), (7 6 *), (20 4 /), (17 5 %), (3 4 ^)")
        
        # Gerar código assembly completo
        codigo_completo = ""
        codigo_completo += gerar_cabecalho_assembly()
        codigo_completo += gerar_todas_operacoes_rpn()
        codigo_completo += gerar_funcao_serial_print()
        
        # Salvar arquivo
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write(codigo_completo)
        
        print(f"Assembly gerado com sucesso: {nome_arquivo}")
        print("Resultados esperados no monitor serial:")
        print("8   (5+3)")
        print("6   (10-4)")
        print("42  (7*6)")
        print("5   (20/4)")
        print("2   (17%5)")
        print("81  (3^4)")
        print("Compatível com PlatformIO/avr-gcc")
        
        return True
        
    except Exception as e:
        raise AssemblyError(f"Erro ao gerar assembly completo: {str(e)}")

if __name__ == '__main__':
    # Teste com TODAS as operações RPN conforme especificado
    
    print("=" * 70)
    print("GERADOR DE ASSEMBLY RPN - VERSÃO COMPLETA CORRIGIDA")
    print("=" * 70)
    print("Executando TODAS as operações em sequência:")
    print("• (5 3 +)    → Soma: 8")
    print("• (10 4 -)   → Subtração: 6") 
    print("• (7 6 *)    → Multiplicação: 42")
    print("• (20 4 /)   → Divisão: 5")
    print("• (17 5 %)   → Resto: 2")
    print("• (3 4 ^)    → Potenciação: 81")
    print("=" * 70)
    
    try:
        # Gerar código assembly com TODAS as operações
        sucesso = gerar_assembly_completo("todas_operacoes.s")
        
        if sucesso:
            print("\n" + "=" * 70)
            print("CÓDIGO ASSEMBLY GERADO COM SUCESSO!")
            print("=" * 70)
            print("Arquivo: todas_operacoes.s")
            print("Correções aplicadas:")
            print("• Executa todas as 6 operações RPN em sequência")
            print("• Função print_number corrigida (sem corrupção)")
            print("• Funções auxiliares implementadas corretamente")
            print("• Compatível com PlatformIO/avr-gcc")
            print()
            print("PARA TESTAR NO ARDUINO:")
            print("1. cp todas_operacoes.s src/main.s")
            print("2. pio run --target upload")
            print("3. pio device monitor")
            print()
            print("SAÍDA ESPERADA NO MONITOR SERIAL:")
            print("8")
            print("6") 
            print("42")
            print("5")
            print("2")
            print("81")
            print("=" * 70)
            
    except Exception as e:
        print(f"ERRO: {e}")