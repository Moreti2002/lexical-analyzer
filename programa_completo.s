; ====================================================
; Código Assembly completo gerado automaticamente
; Processador de Expressões RPN para Arduino Uno
; ATmega328p - Trabalho de Compiladores
; ====================================================

; Código Assembly gerado para Arduino Uno (ATmega328p)
; Processador de expressões RPN
; Sintaxe AVR-GCC

.org 0x0000

; Vetor de interrupção
rjmp reset

; Definições de constantes
.equ RAMEND, 0x08FF    ; Fim da SRAM
.equ SPL, 0x3D         ; Stack Pointer Low
.equ SPH, 0x3E         ; Stack Pointer High
.equ SREG, 0x3F        ; Status Register

; Endereços de memória para variáveis
.equ MEM_START, 0x0100 ; Início da área de memória
.equ HIST_START, 0x0200 ; Início do histórico

; Registradores para operações de ponto flutuante
; r16-r19: primeiro operando
; r20-r23: segundo operando  
; r24-r27: resultado
; r28-r29: ponteiro Y para pilha
; r30-r31: ponteiro Z para memória

reset:
    ; Configurar stack pointer
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, high(RAMEND)
    out SPH, r16
    
    ; Inicializar ponteiros
    ldi r28, low(MEM_START)
    ldi r29, high(MEM_START)
    ldi r30, low(HIST_START)
    ldi r31, high(HIST_START)
    
    ; Limpar registradores de trabalho
    clr r16
    clr r17
    clr r18
    clr r19
    clr r20
    clr r21
    clr r22
    clr r23
    clr r24
    clr r25
    clr r26
    clr r27
    
    rjmp main

main:
ldi r16, 71  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_add
st Y+, r24
st Y+, r25
ldi r16, 64  ; byte 0
ldi r17, 73  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 102  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_sub
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 68  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 69  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_mul
st Y+, r24
st Y+, r25
ldi r16, 128  ; byte 0
ldi r17, 75  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_div
st Y+, r24
st Y+, r25
ldi r16, 64  ; byte 0
ldi r17, 76  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 69  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_mod
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_pow
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 60  ; byte 1
st Y+, r16
st Y+, r17
ldi r30, low(0x0212)
ldi r31, high(0x0212)
ld r16, Z+
ld r17, Z+
ld r18, -Y  ; remove N byte 0
ld r18, -Y  ; remove N byte 1
st Y+, r16  ; empilha resultado byte 0
st Y+, r17  ; empilha resultado byte 1
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_mul
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 68  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_div
st Y+, r24
st Y+, r25
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_sub
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ldi r30, low(0x0214)
ldi r31, high(0x0214)
ld r16, Z+
ld r17, Z+
ld r18, -Y  ; remove N byte 0
ld r18, -Y  ; remove N byte 1
st Y+, r16  ; empilha resultado byte 0
st Y+, r17  ; empilha resultado byte 1
ldi r16, 0  ; byte 0
ldi r17, 62  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 64  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_mul
st Y+, r24
st Y+, r25
ldi r16, 0  ; byte 0
ldi r17, 70  ; byte 1
st Y+, r16
st Y+, r17
ldi r16, 0  ; byte 0
ldi r17, 66  ; byte 1
st Y+, r16
st Y+, r17
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_div
st Y+, r24
st Y+, r25
ld r21, -Y  ; operando2 byte 1
ld r20, -Y  ; operando2 byte 0
ld r19, -Y  ; operando1 byte 1
ld r18, -Y  ; operando1 byte 0
rcall float_add
st Y+, r24
st Y+, r25

    ; Finalização do programa
    ; Resultado final está no topo da pilha
    ld r24, -Y
    ld r25, -Y
    
    ; Armazenar resultado no histórico
    ldi r30, low(HIST_START)
    ldi r31, high(HIST_START)
    
    ; Loop infinito (Arduino não termina)
loop_infinito:
    rjmp loop_infinito

; Rotinas matemáticas IEEE 754 16-bit
; Implementação simplificada para o trabalho

; Adição de ponto flutuante
float_add:
    push r0
    push r1
    
    ; Mover operandos para posição correta
    mov r24, r18
    mov r25, r19
    
    ; Implementação simplificada - soma direta dos bits
    add r24, r20
    adc r25, r21
    
    ; Limitar overflow básico
    brcc float_add_fim
    ldi r24, 0xFF
    ldi r25, 0xFF
    
float_add_fim:
    pop r1
    pop r0
    ret

; Subtração de ponto flutuante
float_sub:
    push r0
    push r1
    
    mov r24, r18
    mov r25, r19
    
    ; Implementação simplificada - subtração direta
    sub r24, r20
    sbc r25, r21
    
    pop r1
    pop r0
    ret

; Multiplicação de ponto flutuante
float_mul:
    push r0
    push r1
    push r2
    push r3
    
    ; Implementação muito simplificada
    ; Multiplica apenas a parte baixa
    mul r18, r20
    mov r24, r0
    mov r25, r1
    
    pop r3
    pop r2
    pop r1
    pop r0
    ret

; Divisão de ponto flutuante
float_div:
    push r0
    push r1
    
    ; Verificar divisão por zero
    cpi r20, 0
    breq div_por_zero
    cpi r21, 0
    breq div_por_zero
    
    ; Implementação simplificada
    mov r24, r18
    mov r25, r19
    
    rjmp float_div_fim
    
div_por_zero:
    ldi r24, 0xFF
    ldi r25, 0xFF
    
float_div_fim:
    pop r1
    pop r0
    ret

; Resto da divisão (módulo)
float_mod:
    push r0
    push r1
    
    ; Verificar divisão por zero
    cpi r20, 0
    breq mod_por_zero
    cpi r21, 0
    breq mod_por_zero
    
    ; Implementação simplificada usando AND
    mov r24, r18
    mov r25, r19
    and r24, r20
    and r25, r21
    
    rjmp float_mod_fim
    
mod_por_zero:
    ldi r24, 0xFF
    ldi r25, 0xFF
    
float_mod_fim:
    pop r1
    pop r0
    ret

; Potenciação (implementação básica)
float_pow:
    push r0
    push r1
    push r16
    
    ; Por simplicidade, implementar apenas quadrado
    ; operando1^operando2 aproximado como operando1 * operando1
    
    mov r20, r18
    mov r21, r19
    
    rcall float_mul
    
    pop r16
    pop r1
    pop r0
    ret

.end