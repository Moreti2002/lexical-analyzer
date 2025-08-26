# Analisador Léxico e Executador RPN - Fase 1

## Descrição

Projeto implementa um **analisador léxico** baseado em **autômato finito determinístico (AFD)** e um **executador** que processa expressões matemáticas em **notação polonesa reversa (RPN)**. O sistema reconhece tokens válidos, detecta erros léxicos e executa operações matemáticas com comandos especiais de memória.

### Características:

- **AFD implementado com funções**: cada estado do autômato é representado por uma função
- **Executador RPN**: avalia expressões usando pilha com precisão IEEE 754
- **Tokens suportados**: números reais, operadores aritméticos, parênteses, palavras reservadas e identificadores
- **Comandos especiais**: gerenciamento de memória e histórico de resultados
- **Detecção de erros**: números malformados, parênteses desbalanceados, divisão por zero

## Estrutura do Projeto

```
├── src/
│   ├── lexer.py          # Analisador léxico principal (AFD)
│   ├── executor.py       # Executador de expressões RPN
│   └── token_types.py    # Definições de tipos de tokens
├── tests/
│   ├── test_lexer.py     # Testes unitários do analisador léxico
│   └── test_executor.py  # Testes unitários do executador
├── utils/
│   └── util.py           # Utilitários auxiliares
├── main.py               # Programa principal
├── expressoes.txt        # Arquivo de teste com expressões RPN
├── texto1.txt            # Arquivos de teste adicionais
├── texto2.txt
├── texto3.txt
├── tokens.txt            # Tokens gerados na última execução
└── README.md
```

## Operadores e Comandos Suportados

### Operadores aritméticos
- **Adição**: `+` → `(A B +)`
- **Subtração**: `-` → `(A B -)`
- **Multiplicação**: `*` → `(A B *)`
- **Divisão**: `/` → `(A B /)`
- **Resto da divisão**: `%` → `(A B %)`
- **Potenciação**: `^` → `(A B ^)`

### Comandos especiais
- **`(N RES)`**: Retorna resultado N linhas anteriores
- **`(V MEM)`**: Armazena valor V na memória MEM
- **`(MEM)`**: Recupera valor da memória MEM (retorna 0.0 se não inicializada)

### Formatos numéricos
- **Inteiros**: `5`, `10`, `42`
- **Decimais**: `3.14`, `2.0`, `15.75` (duas casas decimais)
- **Identificadores**: `MEM`, `VAR`, `CONTADOR` (letras maiúsculas)

## Como executar

### Execução principal
```bash
# Processar arquivo de expressões
python main.py expressoes.txt
```

### Execução de testes
```bash
# Testar analisador léxico
python tests/test_lexer.py

# Testar executador
python tests/test_executor.py
```

## Exemplos de uso

### Operações básicas
```
(3 7 +)         # Resultado: 10.0
(7 7 *)         # Resultado: 49.0
(18 9 /)        # Resultado: 2.0
```

### Expressões aninhadas
```
((2 3 *) (4 2 /) /)     # (6 / 2) = 3.0
((1.5 2.0 *) (6.0 3.0 /) +)  # 3.0 + 2.0 = 5.0
```

### Comandos especiais
```
(42.5 MEM)      # Armazena 42.5 na memória MEM
(MEM)           # Recupera valor: 42.5
(2 RES)         # Resultado 2 linhas anteriores
(3 VAR)         # Armazena 3.0 na variável VAR
(VAR 2 +)       # Soma VAR + 2 = 5.0
```

## Funcionalidades do Executador

### Gerenciamento de memória
- **Múltiplas variáveis**: MEM, VAR, CONTADOR, etc.
- **Persistência**: Valores mantidos durante execução do arquivo
- **Inicialização automática**: Variáveis não inicializadas retornam 0.0

### Histórico de resultados
- **Comando RES**: Acesso a resultados anteriores
- **Indexação relativa**: N linhas para trás no histórico
- **Validação**: Verifica se o resultado solicitado existe

### Precisão numérica
- **IEEE 754**: Operações em ponto flutuante
- **Formatação**: Resultados com duas casas decimais
- **Tratamento de erros**: Divisão por zero, overflow

## Tratamento de erros

### Erros léxicos
```
(3.14 2.0 &)      # Operador inválido
(3.14.5 2.0 +)    # Número malformado
((3.14 2.0 +)     # Parênteses desbalanceados
```

### Erros de execução
```
(5 0 /)           # Divisão por zero
(10 RES)          # RES inválido (histórico insuficiente)
(5 +)             # Operandos insuficientes
```

## Arquivos gerados

### tokens.txt
Arquivo com tokens da última execução do analisador léxico:
```
Tokens gerados pelo analisador léxico:
==================================================

Token 1:
  Tipo: PARENTESE_ABRE
  Valor: (
  Posição: 1
...
```

## Implementação técnica

### Analisador léxico (AFD)
- **Estados**: inicial, numero, numero_decimal, identificador  
- **Validação em tempo real**: erros detectados durante tokenização
- **Balanceamento**: parênteses validados automaticamente

### Executador RPN
- **Algoritmo de pilha**: avaliação eficiente de expressões
- **Contexto de execução**: histórico e memória compartilhados
- **Recursividade**: suporte a expressões aninhadas

## Contribuições
@Moreti2002