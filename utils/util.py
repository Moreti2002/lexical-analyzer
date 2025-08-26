def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo) as arquivo:
            linhas = arquivo.readlines()
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        raise e

    return linhas