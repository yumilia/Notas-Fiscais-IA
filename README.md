# Agente de IA para Processamento de Notas Fiscais

Este projeto implementa um agente inteligente para extrair dados de imagens de Notas Fiscais Eletrônicas (NF-e) e estruturá-los de acordo com o modelo da biblioteca PyNfe.

A solução utiliza a API multimodal do Google Gemini para realizar o Reconhecimento Óptico de Caracteres (OCR) e a extração de entidades em uma única etapa, eliminando a necessidade de ferramentas de OCR tradicionais como o Tesseract.

Estrutura do Projeto
extractor.py: Contém a classe GeminiExtractor, responsável por enviar a imagem da NF-e para a API do Gemini e receber os dados em formato JSON.

mapper.py: Contém a classe JsonToPyNfeMapper, que converte o dicionário JSON retornado pela API em um objeto estruturado compatível com a biblioteca PyNfe.

main.py: Script principal que orquestra o fluxo de trabalho: carrega uma imagem, extrai os dados e os mapeia.

tests/: Contém os testes unitários para o JsonToPyNfeMapper, garantindo a robustez da conversão de dados.

requirements.txt: Lista as dependências do projeto.

Como Configurar e Executar
1. Pré-requisitos
Python 3.8 ou superior

Uma chave de API do Google AI Studio (para o Gemini).

2. Instalação
Clone o repositório e instale as dependências:bash git clone <url-do-seu-repositorio> cd notas_fiscais pip install -r requirements.txt


### 3. Configuração da Chave de API

Você precisa configurar sua chave de API do Google como uma variável de ambiente.

**No Linux ou macOS:**

```bash
export GOOGLE_API_KEY="SUA_CHAVE_API_AQUI"
No Windows (prompt de comando):

Bash

set GOOGLE_API_KEY="SUA_CHAVE_API_AQUI"
4. Executando o Processamento
Para processar uma imagem de NF-e, execute o script main.py passando o caminho da imagem como argumento:

Bash

python main.py /caminho/para/sua/nota_fiscal.png
O script irá imprimir o objeto NFe mapeado no console se o processo for bem-sucedido.

5. Executando os Testes
Para garantir que o mapeador de dados está funcionando corretamente, você pode executar a suíte de testes com pytest:

Bash

pytest

Com todos esses arquivos, você tem uma base sólida e bem estruturada para a Fase 1 do projeto, seguindo as melhores práticas de desenvolvimento e testes.