# Analisador Léxico para Expressões RPN - Fase 1

## Descrição

Esse projeto implementa um **analisador léxico** baseado em **autômato finito determinístico (AFD)** que processa expressões matemáticas em **notação polonesa reversa (RPN)**
O analisador reconhece tokens válidos e detecta erros léxicos.

### Características:

- **AFD implementado com funções**: cada estado do autômato é representado por uma função
- **Tokens suportados**: números reais, operadores aritméticos, parênteses, palavras reservadas e identificadores
- **Detecção de erros**: números malformados, parênteses desbalanceados, caracteres inválidos
- **Validação estrutural**: verifica formato básico de expressões RPN

## Estrutura do Projeto

```
├── src/
│   ├── lexer.py          # Analisador léxico principal (AFD)
│   └── token_types.py    # Definições de tipos de tokens
├── tests/
│   └── test_lexer.py     # Testes unitários completos
├── main.py               # Programa principal
├── expressoes.txt        # Arquivo de teste com expressões RPN
├── tokens.txt            # Tokens gerados
└── README.md
```

## Tokens Suportados

### Números
- **Inteiros**: `5`, `10`, `42`
- **Decimais**: `3.14`, `2.0`, `15.75`
- **Formato**: Usa ponto como separador decimal

### Operadores aritméticos
- **Adição**: `+`
- **Subtração**: `-`
- **Multiplicação**: `*`
- **Divisão**: `/`
- **Resto da divisão**: `%`
- **Potenciação**: `^`

### Símbolos estruturais
- **Parênteses**: `(` e `)`

### Palavras reservadas
- **RES**: Referência a resultado anterior

### Identificadores
- **Formato**: Sequências de letras maiúsculas (`MEM`, `CONTADOR`, `VAR`)

## Instalação e configuração

### Requisitos
- Python 3.x

## Como executar

### Execução principal
```bash
# Processar arquivo
python main.py texto1.txt
```

### Execução de testes
```bash
# Executar todos os testes unitários
cd tests
python test_lexer.py
```

## Exemplos de expressões válids

```
(3.14 2.0 +)                    # Adição simples
(10.5 5.2 -)                    # Subtração
((4.5 2.0 +) (3.0 1.5 -) *)     # Expressão aninhada
(5 RES)                         # Comando especial RES
(8.5 RESULTADO)                 # Armazenamento em memória
(CONTADOR)                      # Recuperação da memória
```

## Exemplos de erros detectados

```
(3.14 2.0 &)      # Operador inválido
(3.14.5 2.0 +)    # Número malformado
((3.14 2.0 +)     # Parênteses desbalanceados
(3,45 2.0 +)      # Vírgula no lugar do ponto
(3. 2.0 +)        # Número terminado em ponto
```

## Arquivos gerados

### tokens.txt
Arquivo gerado automaticamente contendo todos os tokens da última execução:
```
Tokens gerados pelo analisador léxico:
==================================================

Token 1:
  Tipo: PARENTESE_ABRE
  Valor: (
  Posição: 1

Token 2:
  Tipo: NUMERO
  Valor: 3.14
  Posição: 2
...
```

## Implementação do AFD

### Estados do Autômato
- `estado_inicial`: Ponto de partida, decide próximo estado
- `estado_numero`: Reconhece dígitos
- `estado_numero_decimal`: Processa parte decimal
- `estado_identificador`: Reconhece letras maiúsculas

### Características técnicas
- **Detecção de erros em tempo real**: Erros são detectados durante a análise
- **Balanceamento de parênteses**: Validado durante a tokenização
- **Buffer de tokens**: Constrói tokens character-by-character
- **Posicionamento**: Registra posição de cada token

## Testes implementados

### Casos válidos
- Expressões simples com todos os operadores
- Expressões aninhadas complexas
- Números inteiros e decimais
- Comandos especiais (RES, MEM)
- Expressões com espaços extras

### Casos Inválidos
- Operadores inexistentes
- Números malformados
- Parênteses desbalanceados
- Caracteres inválidos
- Identificadores com minúsculas
- Linhas vazias

## Estrutura dos Tokens
Cada token é representado como um dicionário:
```python
{
    'tipo': 'NUMERO',        # Tipo do token
    'valor': '3.14',         # Valor original
    'posicao': 2            # Posição na string
}
```

## Tratamento de erros

O sistema lança `LexerError` em caso de erro, incluindo:
- Mensagem descritiva
- Posição do erro (quando disponível)
- Contexto do problema

## Contribuições
@Moreti2002