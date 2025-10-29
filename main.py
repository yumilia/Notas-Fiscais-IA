# Arquivo: main.py

import argparse
import sys
from extractor import GeminiExtractor
from mapper import JsonToPyNfeMapper, MappingError

def process_invoice_image(image_path: str):
    """
    Executa o pipeline completo: extrai dados da imagem e mapeia para um objeto NFe.

    Args:
        image_path: Caminho para o arquivo de imagem da NF-e.
    """
    try:
        # Etapa 1: Extrair dados da imagem usando o Gemini
        extractor = GeminiExtractor()
        extracted_json = extractor.extract_data_from_image(image_path)

        # Etapa 2: Mapear o JSON extraído para o modelo PyNfe
        mapper = JsonToPyNfeMapper()
        nfe_object = mapper.map(extracted_json)

        # Etapa 3: Exibir o resultado
        print("\n--- Objeto NFe Mapeado com Sucesso ---")
        # A representação do objeto (usando __repr__) mostrará os dados preenchidos
        print(nfe_object)
        print("\n--- Detalhes do Emitente e Destinatário ---")
        print(f"Emitente: {nfe_object.infNFe.emit.xNome} (CNPJ: {nfe_object.infNFe.emit.CNPJ})")
        print(f"Destinatário: {nfe_object.infNFe.dest.xNome} (CNPJ/CPF: {nfe_object.infNFe.dest.CNPJ_CPF})")
        print("\n--- Processo concluído. ---")

    except FileNotFoundError:
        # Erro tratado no extrator, mas podemos adicionar uma mensagem final aqui
        print("Processo interrompido: o arquivo de imagem não foi encontrado.")
        sys.exit(1)
    except MappingError as e:
        print(f"\nERRO DE MAPEAMENTO: {e}")
        print("Ocorreu um problema ao tentar converter o JSON extraído para o formato NFe.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO INESPERADO: {e}")
        print("Ocorreu um erro crítico durante o processamento.")
        sys.exit(1)


if __name__ == "__main__":
    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description="Processador de NF-e: Extrai dados de uma imagem de NF-e e os mapeia para um objeto PyNfe."
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="O caminho para o arquivo de imagem da NF-e a ser processado."
    )

    args = parser.parse_args()

    # Chama a função principal com o caminho da imagem fornecido
    process_invoice_image(args.image_path)