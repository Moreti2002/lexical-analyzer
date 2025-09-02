; ========================================
; Gerador RPN para Arduino - Assembly AVR
; Fase 1 - Trabalho de Compiladores
; ========================================

.include "m328pdef.inc"          ; Definições para ATmega328P
.device ATmega328P

; Configuração da memória
.cseg                            ; Segmento de código
.org 0x0000                      ; Endereço inicial

; Configuração inicial
setup:
    ; Configurar Stack Pointer
    ldi r28, low(RAMEND)         ; Parte baixa do endereço final da RAM
    ldi r29, high(RAMEND)        ; Parte alta do endereço final da RAM
    out SPL, r28                 ; Stack Pointer Low
    out SPH, r29                 ; Stack Pointer High
    
    ; Inicializar registradores
    clr r0                       ; Zero register
    clr r1                       ; Usado para operações
    
    ; Configurar pilha RPN (usando registradores R16-R25)
    ldi r30, 16                  ; Stack pointer para pilha RPN (começa no R16)
    
    ; Inicializar memórias (simuladas em SRAM)
    ldi r16, 0                   ; Inicializar variáveis de memória
    sts memoria_mem, r16         ; MEM = 0
    sts memoria_var, r16         ; VAR = 0  
    sts memoria_contador, r16    ; CONTADOR = 0
    
    ; Inicializar histórico RES (primeiros 10 resultados)
    ldi r16, 10                  ; Contador para loop
    ldi r30, low(historico_res)  ; Ponteiro para área de histórico
    ldi r31, high(historico_res)
init_hist_loop:
    st Z+, r0                    ; Limpar posição do histórico
    dec r16
    brne init_hist_loop

main:
    ; Início do processamento das expressões RPN
    ; O código gerado para cada expressão será inserido aqui


    ; Processando expressão RPN
    ; Empilhar número 3.14
    ldi r16, 58
    ldi r26, 1
    ; Empilhar número 2.0
    ldi r17, 200
    ldi r27, 0
    ; Operação +
    ; Operando1: r16:r26, Operando2: r17:r27
    call adicao

    ; Salvar resultado no histórico
    call salvar_resultado
    ; Resultado final em r16:r26


; ========================================
; SUB-ROTINAS PARA OPERAÇÕES ARITMÉTICAS
; ========================================
; Convenção: operandos em pilha, resultado em R16:R26

adicao:
    ; Soma dois valores de 16 bits
    ; Operando1: pilha topo-1, Operando2: pilha topo
    add r16, r17          ; Soma byte baixo
    adc r26, r27          ; Soma byte alto com carry
    ret

subtracao:
    ; Subtração de dois valores de 16 bits  
    ; R16:R26 = Operando1 - Operando2
    sub r16, r17          ; Subtrai byte baixo
    sbc r26, r27          ; Subtrai byte alto com borrow
    ret

multiplicacao:
    ; Multiplicação simplificada de 16 bits
    ; Para implementação completa seria necessário mais código
    call mult16           ; Chama rotina auxiliar de multiplicação
    ret

divisao:
    ; Divisão de 16 bits com verificação de zero
    ; Verifica se divisor é zero
    cp r17, r0
    cpc r27, r0
    breq div_zero_error
    call div16            ; Chama rotina auxiliar de divisão
    ret

div_zero_error:
    ; Tratamento de erro de divisão por zero
    ldi r16, 0xFF         ; Valor de erro
    ldi r26, 0xFF
    ret

resto:
    ; Resto da divisão de 16 bits
    cp r17, r0
    cpc r27, r0
    breq div_zero_error
    call mod16            ; Chama rotina auxiliar de módulo
    ret

potencia:
    ; Potenciação simplificada
    call pow16            ; Chama rotina auxiliar de potência
    ret

; ========================================
; SUB-ROTINAS AUXILIARES PARA ARITMÉTICA
; ========================================

mult16:
    ; Multiplicação de 16 bits (simplificada)
    ; Por simplicidade, usar shift e add para casos pequenos
    mov r18, r16          ; Backup operando1
    mov r19, r26
    clr r16               ; Resultado = 0
    clr r26
mult_loop:
    cp r17, r0            ; Operando2 == 0?
    cpc r27, r0
    breq mult_end
    add r16, r18          ; Resultado += operando1
    adc r26, r19
    subi r17, 1           ; operando2--
    sbci r27, 0
    rjmp mult_loop
mult_end:
    ret

div16:
    ; Divisão de 16 bits (algoritmo simplificado)
    ; Implementação básica usando subtração sucessiva
    clr r18               ; Contador (quociente)
    clr r19
div_loop:
    cp r16, r17           ; Operando1 < operando2?
    cpc r26, r27
    brlo div_end
    sub r16, r17          ; operando1 -= operando2
    sbc r26, r27
    inc r18               ; quociente++
    brne div_loop
    inc r19
    rjmp div_loop
div_end:
    mov r16, r18          ; Resultado = quociente
    mov r26, r19
    ret

mod16:
    ; Resto de 16 bits
    ; Similar à divisão, mas retorna o resto
mod_loop:
    cp r16, r17
    cpc r26, r27
    brlo mod_end          ; Se operando1 < operando2, resto = operando1
    sub r16, r17
    sbc r26, r27
    rjmp mod_loop
mod_end:
    ; Resto já está em R16:R26
    ret

pow16:
    ; Potenciação simplificada (base^expoente)
    ; Base em R16:R26, expoente em R17:R27
    mov r18, r16          ; Backup da base
    mov r19, r26
    ldi r16, 1            ; Resultado inicial = 1
    ldi r26, 0
pow_loop:
    cp r17, r0            ; Expoente == 0?
    cpc r27, r0
    breq pow_end
    ; Multiplicar resultado pela base (simplificado)
    call mult_base
    subi r17, 1           ; expoente--
    sbci r27, 0
    rjmp pow_loop
pow_end:
    ret

mult_base:
    ; Multiplica resultado atual pela base (auxiliar para potência)
    ; Implementação simplificada
    ret

; ========================================
; SUB-ROTINAS PARA COMANDOS ESPECIAIS
; ========================================

salvar_resultado:
    ; Salva resultado atual no histórico RES
    ; Resultado em R16:R26
    ; Implementação: circular buffer nos primeiros 10 slots
    lds r20, indice_historico    ; Carrega índice atual
    inc r20                      ; Próxima posição
    cpi r20, 10                  ; Overflow?
    brne save_no_wrap
    ldi r20, 0                   ; Volta ao início
save_no_wrap:
    sts indice_historico, r20    ; Salva novo índice
    
    ; Calcular endereço no histórico
    ldi r30, low(historico_res)
    ldi r31, high(historico_res)
    add r30, r20                 ; Adicionar offset
    adc r31, r0
    add r30, r20                 ; *2 (cada entrada tem 2 bytes)
    adc r31, r0
    
    ; Salvar resultado
    st Z+, r16                   ; Byte baixo
    st Z, r26                    ; Byte alto
    ret

recuperar_res:
    ; Recupera resultado N linhas atrás
    ; N em R16:R26, resultado retorna em R16:R26
    lds r20, indice_historico    ; Índice atual
    sub r20, r16                 ; Voltar N posições
    brpl rec_no_wrap             ; Se positivo, não precisa ajustar
    addi r20, 10                 ; Wrap around
rec_no_wrap:
    cpi r20, 10                  ; Verificar bounds
    brlo rec_valid
    ldi r16, 0                   ; Erro: retorna 0
    ldi r26, 0
    ret
rec_valid:
    ; Calcular endereço
    ldi r30, low(historico_res)
    ldi r31, high(historico_res)
    add r30, r20
    adc r31, r0
    add r30, r20                 ; *2
    adc r31, r0
    
    ; Carregar resultado
    ld r16, Z+                   ; Byte baixo
    ld r26, Z                    ; Byte alto
    ret

; ========================================
; ÁREA DE DADOS
; ========================================
.dseg                            ; Segmento de dados
memoria_mem:      .byte 2        ; Variável MEM (16 bits)
memoria_var:      .byte 2        ; Variável VAR (16 bits)
memoria_contador: .byte 2        ; Variável CONTADOR (16 bits)
historico_res:    .byte 20       ; Histórico RES (10 entradas x 2 bytes)
indice_historico: .byte 1        ; Índice circular do histórico


; ========================================
; FINALIZAÇÃO DO PROGRAMA
; ========================================
end_program:
    ; Loop infinito (programa Arduino típico)
    rjmp end_program

