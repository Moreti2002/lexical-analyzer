import sys
from src.assembly_generator import gerar_assembly_completo, AssemblyError

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <nome_arquivo_saida.s>")
        sys.exit(1)
    nome_arquivo = sys.argv[1]
    try:
        if gerar_assembly_completo(nome_arquivo):
            print(f"Arquivo assembly '{nome_arquivo}' gerado com sucesso.")
    except AssemblyError as e:
        print(e)
        sys.exit(2)

if __name__ == "__main__":
    main()