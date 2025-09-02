# Exceções para o gerador de assembly

class AssemblyError(Exception):
    """exceção para erros do gerador de assembly"""
    def __init__(self, mensagem, token=None, linha=None):
        self.mensagem = mensagem
        self.token = token
        self.linha = linha
        super().__init__(f"Erro de geração de assembly{' na linha ' + str(linha) if linha else ''}{' no token: ' + str(token) if token else ''}: {mensagem}")

class AssemblyLimitError(AssemblyError):
    """exceção para limitações do atmega328p"""
    def __init__(self, mensagem, limitacao=None):
        self.limitacao = limitacao
        super().__init__(f"Limitação do atmega328p: {mensagem}")

class AssemblyValidationError(AssemblyError):
    """exceção para validação de tokens"""
    def __init__(self, mensagem, token_invalido=None):
        self.token_invalido = token_invalido
        super().__init__(f"Token inválido para assembly: {mensagem}")