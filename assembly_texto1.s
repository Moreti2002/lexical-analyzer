#include <avr/io.h>

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

; === CÓDIGO INICIAL ===
.section .text
.global main

main:
    ; Garantir que r0 = 0 (usado em várias operações adc)
    clr r0
    
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
    
    ; Executar expressões RPN do arquivo
    call executar_rpn
    
loop_forever:
    rjmp loop_forever

; === ÁREA DE DADOS SRAM ===
.section .data

; Área para variáveis de usuário (MEM, VAR, etc.)
memoria_vars:
    .space 26         ; 26 slots para A-Z (identificadores)

; Histórico de resultados (últimos 10 resultados)
historico_resultados:
    .space 10         ; Buffer circular para histórico

historico_index:
    .byte 0           ; Índice atual no histórico

; === FUNÇÕES (continuação da seção .text) ===
.section .text

executar_rpn:
    ; Inicializar memória (zero fill)
    call init_memory
    
    ; === Expressão 1: (3.142.0+) ===
    ; Operação (3 2 +)
    ldi r20, 3
    ldi r21, 2
    add r20, r21
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 2: (10.53.2-) ===
    ; Operação (10 3 -)
    ldi r20, 10
    ldi r21, 3
    sub r20, r21
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 3: (4.05.0*) ===
    ; Operação (4 5 *)
    ldi r20, 4
    ldi r21, 5
    call multiply_r20_r21
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 4: (15.03.0/) ===
    ; Operação (15 3 /)
    ldi r20, 15
    ldi r21, 3
    mov r16, r20
    mov r17, r21
    call div_r16_r17
    mov r20, r18             ; Quociente em r20
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 5: (175%) ===
    ; Operação (17 5 %)
    ldi r20, 17
    ldi r21, 5
    mov r16, r20
    mov r17, r21
    call div_r16_r17        ; Resto fica em r16
    mov r20, r16
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 6: (2.03^) ===
    ; Operação (2 3 ^)
    ldi r20, 2
    ldi r21, 3
    call power_r20_r21
    mov r16, r20
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 7: (100.0MEM) ===
    ; Comando (100 MEM) - armazenar valor
    ldi r16, 100             ; Valor a armazenar
    ldi r17, 'M'     ; Primeiro caractere do identificador
    push r16                     ; Salvar valor
    call char_to_index           ; Converter para índice em r17
    pop r16                      ; Restaurar valor
    call store_variable          ; Armazenar
    call add_to_history          ; Adicionar ao histórico
    call print_number            ; Imprimir valor armazenado

    ; === Expressão 8: (1RES) ===
    ; Comando (1 RES) - recuperar resultado anterior
    ldi r16, 1
    call get_from_history        ; Resultado em r16
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 9: (MEM) ===
    ; Comando (MEM) - recuperar variável MEM
    ldi r16, 'M'     ; Primeiro caractere do identificador
    call char_to_index           ; Converter para índice em r17
    call load_variable           ; Carregar valor em r16
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 10: (12.5VALOR) ===
    ; Comando (12 VALOR) - armazenar valor
    ldi r16, 12             ; Valor a armazenar
    ldi r17, 'V'     ; Primeiro caractere do identificador
    push r16                     ; Salvar valor
    call char_to_index           ; Converter para índice em r17
    pop r16                      ; Restaurar valor
    call store_variable          ; Armazenar
    call add_to_history          ; Adicionar ao histórico
    call print_number            ; Imprimir valor armazenado

    ; === Expressão 11: (2RES) ===
    ; Comando (2 RES) - recuperar resultado anterior
    ldi r16, 2
    call get_from_history        ; Resultado em r16
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ; === Expressão 12: (VALOR) ===
    ; Comando (MEM) - recuperar variável VALOR
    ldi r16, 'V'     ; Primeiro caractere do identificador
    call char_to_index           ; Converter para índice em r17
    call load_variable           ; Carregar valor em r16
    call add_to_history          ; Adicionar ao histórico
    call print_number

    ret

; Função para inicializar área de memória
init_memory:
    push ZL
    push ZH
    push r16
    push r17
    
    ; Limpar área de variáveis
    ldi ZL, lo8(memoria_vars)
    ldi ZH, hi8(memoria_vars)
    ldi r17, 26              ; 26 variáveis
    ldi r16, 0               ; Valor inicial
    
init_vars_loop:
    st Z+, r16
    dec r17
    brne init_vars_loop
    
    ; Limpar histórico
    ldi ZL, lo8(historico_resultados)
    ldi ZH, hi8(historico_resultados)
    ldi r17, 10              ; 10 slots de histórico
    
init_history_loop:
    st Z+, r16
    dec r17
    brne init_history_loop
    
    ; Inicializar índice do histórico
    sts historico_index, r16  ; r16 = 0
    
    pop r17
    pop r16
    pop ZH
    pop ZL
    ret

; === FUNÇÕES DE GERENCIAMENTO DE MEMÓRIA ===

; Função para armazenar valor na memória de uma variável
; Entrada: r16 = valor, r17 = índice da variável (0-25 para A-Z)
store_variable:
    push ZL
    push ZH
    push r16
    
    ; Calcular endereço base + offset
    ldi ZL, lo8(memoria_vars)
    ldi ZH, hi8(memoria_vars)
    add ZL, r17
    adc ZH, r0           ; r0 sempre é zero
    
    ; Armazenar valor
    st Z, r16
    
    pop r16
    pop ZH
    pop ZL
    ret

; Função para carregar valor da memória de uma variável
; Entrada: r17 = índice da variável (0-25 para A-Z)
; Saída: r16 = valor (0 se não inicializada)
load_variable:
    push ZL
    push ZH
    
    ; Calcular endereço base + offset
    ldi ZL, lo8(memoria_vars)
    ldi ZH, hi8(memoria_vars)
    add ZL, r17
    adc ZH, r0           ; r0 sempre é zero
    
    ; Carregar valor
    ld r16, Z
    
    pop ZH
    pop ZL
    ret

; Função para adicionar resultado ao histórico
; Entrada: r16 = resultado
add_to_history:
    push ZL
    push ZH
    push r17
    push r18
    
    ; Carregar índice atual
    lds r17, historico_index
    
    ; Calcular endereço no histórico
    ldi ZL, lo8(historico_resultados)
    ldi ZH, hi8(historico_resultados)
    add ZL, r17
    adc ZH, r0
    
    ; Armazenar resultado
    st Z, r16
    
    ; Incrementar índice (circular, módulo 10)
    inc r17
    cpi r17, 10
    brlo history_index_ok
    ldi r17, 0           ; Reset para 0 se chegou a 10
    
history_index_ok:
    sts historico_index, r17
    
    pop r18
    pop r17
    pop ZH
    pop ZL
    ret

; Função para recuperar resultado do histórico
; Entrada: r16 = N (linhas anteriores, 1-10)
; Saída: r16 = resultado (0 se inválido)
get_from_history:
    push ZL
    push ZH
    push r17
    push r18
    
    ; Verificar se N está no range válido (1-10)
    cpi r16, 1
    brlo history_invalid
    cpi r16, 11
    brsh history_invalid
    
    ; Carregar índice atual
    lds r17, historico_index
    
    ; Calcular posição: (índice_atual - N) mod 10
    sub r17, r16
    brpl history_calc_done   ; Se positivo, está ok
    
    ; Se negativo, adicionar 10 para fazer módulo
    ldi r18, 10
    add r17, r18
    
history_calc_done:
    ; Calcular endereço no histórico
    ldi ZL, lo8(historico_resultados)
    ldi ZH, hi8(historico_resultados)
    add ZL, r17
    adc ZH, r0
    
    ; Carregar resultado
    ld r16, Z
    rjmp history_done
    
history_invalid:
    ldi r16, 0               ; Retorna 0 se inválido
    
history_done:
    pop r18
    pop r17
    pop ZH
    pop ZL
    ret

; Função para converter identificador para índice (A=0, B=1, ..., Z=25)
; Entrada: r16 = primeiro caractere do identificador
; Saída: r17 = índice (0-25)
char_to_index:
    push r18
    
    ; Converter de ASCII para índice (A=65, Z=90)
    ldi r18, 65              ; ASCII 'A'
    sub r16, r18
    mov r17, r16
    
    ; Limitar ao range 0-25
    cpi r17, 26
    brlo char_index_ok
    ldi r17, 0               ; Default para 0 se inválido
    
char_index_ok:
    pop r18
    ret

; === FUNÇÕES DE COMUNICAÇÃO SERIAL (CORRIGIDA) ===

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
; VERSÃO CORRIGIDA DO COPILOT - FUNCIONAL
print_number:
    push r16
    push r17
    push r18
    push r19
    push r20
    
    mov r19, r16  ; Backup do número original
    
    ; Centenas
    ldi r17, 100
    call div_r16_r17  ; r18 = centenas, r16 = resto após centenas
    mov r20, r16      ; Salvar resto (dezenas+unidades) em r20
    
    ; Imprimir centenas se != 0
    cpi r18, 0
    breq skip_hundreds
    ldi r16, 48       ; ASCII '0'
    add r16, r18      ; Converte para ASCII
    call uart_transmit
    
skip_hundreds:
    ; Dezenas  
    mov r16, r20      ; Restaurar resto (dezenas+unidades)
    ldi r17, 10
    call div_r16_r17  ; r18 = dezenas, r16 = unidades
    mov r20, r16      ; Salvar unidades em r20
    
    ; Imprimir dezenas se centenas foi impressa OU dezenas != 0
    cpi r19, 100      ; Se número original >= 100
    brsh print_tens
    cpi r18, 0        ; Se dezenas = 0 e número < 100
    breq print_units
    
print_tens:
    ldi r16, 48       ; ASCII '0'  
    add r16, r18      ; Converte dezenas para ASCII
    call uart_transmit
    
print_units:
    ; Unidades (sempre imprime)
    mov r16, r20      ; Restaurar unidades salvas
    ldi r17, 48       ; ASCII '0'
    add r16, r17      ; Converte unidades para ASCII
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

; === FUNÇÕES MATEMÁTICAS ===

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

