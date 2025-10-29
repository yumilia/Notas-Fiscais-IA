import os
import json
import time
import google.generativeai as genai
from PIL import Image

# --- Debug: List available models ---
print("=== Available Models ===")
for model in genai.list_models():
    print(f"Name: {model.name}")
    print(f"Supported methods: {model.supported_generation_methods}")
    print("---")

# --- Configuração da API do Gemini ---
try:
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise KeyError("GOOGLE_API_KEY não definida")
    genai.configure(api_key=api_key)
except KeyError as e:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
    print("Por favor, defina sua chave de API do Google para continuar.")
    exit(1)

# --- Prompt de Engenharia para Extração Estruturada ---
EXTRACTION_PROMPT = """
Você é um especialista em processamento de documentos fiscais brasileiros.
Sua tarefa é analisar a imagem de uma Nota Fiscal Eletrônica (NF-e) fornecida
e extrair as informações solicitadas com a máxima precisão.

Retorne a resposta EXCLUSIVAMENTE como um único objeto JSON válido, sem nenhum
texto, explicação ou formatação markdown adicional (como ```json).

Use a seguinte estrutura para o JSON de saída:
{
  "ide": {
    "numero_nf": "string",
    "serie": "string",
    "data_emissao": "string (formato DD/MM/AAAA)"
  },
  "emitente": {
    "nome": "string",
    "cnpj": "string (apenas números)",
    "endereco": "string",
    "bairro": "string",
    "cep": "string",
    "municipio": "string",
    "uf": "string",
    "telefone": "string",
    "ie": "string (inscrição estadual)"
  },
  "destinatario": {
    "nome": "string",
    "cnpj_cpf": "string (apenas números)",
    "endereco": "string",
    "bairro": "string",
    "cep": "string",
    "municipio": "string",
    "uf": "string",
    "telefone": "string",
    "ie": "string (inscrição estadual)"
  },
  "totais": {
    "base_calculo_icms": "float",
    "valor_icms": "float",
    "valor_total_produtos": "float",
    "valor_frete": "float",
    "valor_seguro": "float",
    "outras_despesas": "float",
    "valor_total_ipi": "float",
    "valor_total_nf": "float"
  },
  "itens": [
    {
      "codigo_produto": "string",
      "descricao": "string",
      "ncm": "string",
      "cst": "string",
      "cfop": "string",
      "unidade": "string",
      "quantidade": "float",
      "valor_unitario": "float",
      "valor_total": "float",
      "base_calculo_icms": "float",
      "valor_icms": "float",
      "aliquota_icms": "float",
      "valor_ipi": "float",
      "aliquota_ipi": "float"
    }
  ],
  "transporte": {
    "modalidade_frete": "string",
    "transportador_nome": "string",
    "transportador_cnpj_cpf": "string",
    "transportador_ie": "string",
    "transportador_endereco": "string",
    "transportador_municipio": "string",
    "transportador_uf": "string",
    "veiculo_placa": "string",
    "veiculo_uf": "string",
    "quantidade_volumes": "integer",
    "especie_volumes": "string",
    "marca_volumes": "string",
    "numeracao_volumes": "string",
    "peso_bruto": "float",
    "peso_liquido": "float"
  },
  "chave_acesso": "string (44 dígitos, apenas números)"
}
"""

class GeminiExtractor:
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        self.max_retries = 3
        self.base_delay = 15  # segundos

    def extract_data_from_image(self, image_path: str) -> dict:
        """
        Carrega uma imagem, envia para a API Gemini com um prompt estruturado
        e retorna os dados extraídos como um dicionário Python.
        """
        print(f"Iniciando extração de dados da imagem: {image_path}")

        try:
            img = Image.open(image_path)
        except FileNotFoundError:
            print(f"Erro: Arquivo de imagem não encontrado em '{image_path}'")
            raise

        for attempt in range(self.max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {self.max_retries}...")
                response = self.model.generate_content(
                    contents=[EXTRACTION_PROMPT, img],
                    generation_config={
                        'temperature': 0.1,
                        'top_p': 1,
                        'top_k': 32,
                        'max_output_tokens': 2048,
                    }
                )
                response.resolve()
                print("Resposta recebida da API.")
                break
            except Exception as e:
                if "429" in str(e):  # Rate limit error
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (attempt + 1)
                        print(f"Limite de taxa atingido. Aguardando {delay} segundos...")
                        time.sleep(delay)
                        continue
                print(f"Erro ao chamar a API do Gemini: {e}")
                raise

        # Limpa a resposta para garantir que seja um JSON puro
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()

        try:
            extracted_data = json.loads(cleaned_response)
            print("Dados extraídos e convertidos para JSON com sucesso.")
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar o JSON da resposta da API: {e}")
            print("--- Resposta Bruta Recebida ---")
            print(response.text)
            print("-----------------------------")
            raise Exception("A resposta da API não é um JSON válido.")

if __name__ == "__main__":
    print("Este módulo deve ser importado, não executado diretamente.")