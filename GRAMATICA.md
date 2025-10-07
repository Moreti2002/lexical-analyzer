# Documentação da Gramática LL(1)

## Regras de Produção

```
PROGRAMA → EXPRESSAO
EXPRESSAO → ( CONTEUDO )
CONTEUDO → CONTEUDO_REAL
CONTEUDO_REAL → OPERACAO_OU_COMANDO
OPERACAO_OU_COMANDO → numero RESTO_NUMERO
OPERACAO_OU_COMANDO → identificador RESTO_IDENTIFICADOR
OPERACAO_OU_COMANDO → EXPRESSAO OPERANDO OPERADOR_TOTAL
RESTO_NUMERO → numero OPERADOR_ARIT
RESTO_NUMERO → identificador
RESTO_NUMERO → RES
RESTO_IDENTIFICADOR → numero OPERADOR_ARIT
RESTO_IDENTIFICADOR → identificador OPERADOR_ARIT
RESTO_IDENTIFICADOR → EXPRESSAO OPERADOR_TOTAL
RESTO_IDENTIFICADOR → ε
OPERADOR_TOTAL → OPERADOR_ARIT
OPERADOR_TOTAL → OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE
PALAVRA_CONTROLE → EXPRESSAO IF
PALAVRA_CONTROLE → WHILE
OPERACAO → OPERANDO OPERANDO OPERADOR_ARIT
OPERANDO → numero
OPERANDO → identificador
OPERANDO → EXPRESSAO
OPERADOR_ARIT → +
OPERADOR_ARIT → -
OPERADOR_ARIT → *
OPERADOR_ARIT → /
OPERADOR_ARIT → %
OPERADOR_ARIT → ^
OPERADOR_REL → >
OPERADOR_REL → <
OPERADOR_REL → ==
OPERADOR_REL → !=
OPERADOR_REL → >=
OPERADOR_REL → <=
```

## Conjuntos FIRST

| Não-Terminal | FIRST |
|--------------|-------|
| CONTEUDO | { (, identificador, numero } |
| CONTEUDO_REAL | { (, identificador, numero } |
| EXPRESSAO | { ( } |
| OPERACAO | { (, identificador, numero } |
| OPERACAO_OU_COMANDO | { (, identificador, numero } |
| OPERADOR_ARIT | { %, *, +, -, /, ^ } |
| OPERADOR_REL | { !=, <, <=, ==, >, >= } |
| OPERADOR_TOTAL | { !=, %, *, +, -, /, <, <=, ==, >, >=, ^ } |
| OPERANDO | { (, identificador, numero } |
| PALAVRA_CONTROLE | { (, WHILE } |
| PROGRAMA | { ( } |
| RESTO_IDENTIFICADOR | { (, identificador, numero, ε } |
| RESTO_NUMERO | { RES, identificador, numero } |

## Conjuntos FOLLOW

| Não-Terminal | FOLLOW |
|--------------|--------|
| CONTEUDO | { ) } |
| CONTEUDO_REAL | { ) } |
| EXPRESSAO | { !=, $, %, (, *, +, -, /, <, <=, ==, >, >=, IF, WHILE, ^, identificador, numero } |
| OPERACAO | {  } |
| OPERACAO_OU_COMANDO | { ) } |
| OPERADOR_ARIT | { ) } |
| OPERADOR_REL | { ( } |
| OPERADOR_TOTAL | { ) } |
| OPERANDO | { !=, %, (, *, +, -, /, <, <=, ==, >, >=, ^, identificador, numero } |
| PALAVRA_CONTROLE | { ) } |
| PROGRAMA | { $ } |
| RESTO_IDENTIFICADOR | { ) } |
| RESTO_NUMERO | { ) } |

## Tabela de Análise LL(1)

| Não-Terminal | Terminal | Produção |
|--------------|----------|----------|
| CONTEUDO | ( | CONTEUDO_REAL |
| CONTEUDO | identificador | CONTEUDO_REAL |
| CONTEUDO | numero | CONTEUDO_REAL |
| CONTEUDO_REAL | ( | OPERACAO_OU_COMANDO |
| CONTEUDO_REAL | identificador | OPERACAO_OU_COMANDO |
| CONTEUDO_REAL | numero | OPERACAO_OU_COMANDO |
| EXPRESSAO | ( | ( CONTEUDO ) |
| OPERACAO | ( | OPERANDO OPERANDO OPERADOR_ARIT |
| OPERACAO | identificador | OPERANDO OPERANDO OPERADOR_ARIT |
| OPERACAO | numero | OPERANDO OPERANDO OPERADOR_ARIT |
| OPERACAO_OU_COMANDO | ( | EXPRESSAO OPERANDO OPERADOR_TOTAL |
| OPERACAO_OU_COMANDO | identificador | identificador RESTO_IDENTIFICADOR |
| OPERACAO_OU_COMANDO | numero | numero RESTO_NUMERO |
| OPERADOR_ARIT | % | % |
| OPERADOR_ARIT | * | * |
| OPERADOR_ARIT | + | + |
| OPERADOR_ARIT | - | - |
| OPERADOR_ARIT | / | / |
| OPERADOR_ARIT | ^ | ^ |
| OPERADOR_REL | != | != |
| OPERADOR_REL | < | < |
| OPERADOR_REL | <= | <= |
| OPERADOR_REL | == | == |
| OPERADOR_REL | > | > |
| OPERADOR_REL | >= | >= |
| OPERADOR_TOTAL | != | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | % | OPERADOR_ARIT |
| OPERADOR_TOTAL | * | OPERADOR_ARIT |
| OPERADOR_TOTAL | + | OPERADOR_ARIT |
| OPERADOR_TOTAL | - | OPERADOR_ARIT |
| OPERADOR_TOTAL | / | OPERADOR_ARIT |
| OPERADOR_TOTAL | < | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | <= | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | == | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | > | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | >= | OPERADOR_REL EXPRESSAO PALAVRA_CONTROLE |
| OPERADOR_TOTAL | ^ | OPERADOR_ARIT |
| OPERANDO | ( | EXPRESSAO |
| OPERANDO | identificador | identificador |
| OPERANDO | numero | numero |
| PALAVRA_CONTROLE | ( | EXPRESSAO IF |
| PALAVRA_CONTROLE | WHILE | WHILE |
| PROGRAMA | ( | EXPRESSAO |
| RESTO_IDENTIFICADOR | ( | EXPRESSAO OPERADOR_TOTAL |
| RESTO_IDENTIFICADOR | ) | ε |
| RESTO_IDENTIFICADOR | identificador | identificador OPERADOR_ARIT |
| RESTO_IDENTIFICADOR | numero | numero OPERADOR_ARIT |
| RESTO_NUMERO | RES | RES |
| RESTO_NUMERO | identificador | identificador |
| RESTO_NUMERO | numero | numero OPERADOR_ARIT |

## Exemplo de Árvore Sintática

Expressão: `(3RES)`

```
EXPRESSAO
  └─ COMANDO_RES
    └─ NUMERO: 3
```

Árvore completa salva em: `arvore_sintatica.json`
