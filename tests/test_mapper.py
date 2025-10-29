# Arquivo: tests/test_mapper.py
import sys
from pathlib import Path

# Adiciona raiz do projeto ao path para o import do mapper funcionar
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
import json
# Certifique-se de não repetir a importação de Path abaixo
# from pathlib import Path  # removido (já importado acima)

from mapper import JsonToPyNfeMapper, MappingError

# Define o caminho base para a pasta de dados de teste
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture
def valid_nfe_json():
    """Carrega um JSON de NF-e válido de um arquivo para os testes."""
    with open(TEST_DATA_DIR / "valid_nfe.json", 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def incomplete_nfe_json():
    """Carrega um JSON de NF-e com um campo obrigatório faltando."""
    with open(TEST_DATA_DIR / "incomplete_nfe.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def test_map_success_on_valid_json(valid_nfe_json):
    """
    Testa o 'caminho feliz': mapeamento bem-sucedido com um JSON completo e válido.
    """
    mapper = JsonToPyNfeMapper()
    nfe_obj = mapper.map(valid_nfe_json)

    # Asserções para verificar o mapeamento
    assert nfe_obj is not None
    assert nfe_obj.infNFe.ide.nNF == "12345"
    assert nfe_obj.infNFe.emit.xNome == "EMPRESA EMITENTE LTDA"
    assert nfe_obj.infNFe.dest.xNome == "EMPRESA DESTINATARIO SA"
    assert nfe_obj.infNFe.total.ICMSTot.vNF == 150.00
    assert nfe_obj.infNFe.Id == "NFe43211011222333000144550010000123451000000001"
    
    # Verifica a lista de itens (SINTAXE CORRIGIDA)
    assert len(nfe_obj.infNFe.det) == 2
    assert nfe_obj.infNFe.det[0].prod.xProd == "PRODUTO DE TESTE 1"
    assert nfe_obj.infNFe.det[0].prod.qCom == 2.0
    # AQUI ESTÁ A CORREÇÃO PRINCIPAL: de det.[1] para det[1]
    assert nfe_obj.infNFe.det[1].prod.xProd == "PRODUTO DE TESTE 2"
    assert nfe_obj.infNFe.det[1].prod.qCom == 1.0

def test_map_handles_missing_optional_fields(incomplete_nfe_json):
    """
    Testa se o mapeador lida com JSONs incompletos sem quebrar,
    atribuindo None aos campos ausentes.
    """
    mapper = JsonToPyNfeMapper()
    nfe_obj = mapper.map(incomplete_nfe_json)

    assert nfe_obj is not None
    assert nfe_obj.infNFe.emit.xNome == "EMPRESA SEM CNPJ"
    # O mapper usa.get(), então campos ausentes devem ser None
    assert nfe_obj.infNFe.emit.CNPJ is None
    assert nfe_obj.infNFe.total.ICMSTot.vNF is None

def test_map_handles_empty_item_list_gracefully(valid_nfe_json):
    """
    Testa se o mapeador funciona corretamente quando a lista de 'itens' está vazia.
    """
    mapper = JsonToPyNfeMapper()
    valid_nfe_json['itens'] = []# Modifica o JSON de teste para não ter itens
    
    nfe_obj = mapper.map(valid_nfe_json)
    
    assert nfe_obj is not None
    assert len(nfe_obj.infNFe.det) == 0

def test_map_raises_error_for_non_dict_input():
    """
    Testa se o mapeador levanta um erro se a entrada não for um dicionário.
    """
    mapper = JsonToPyNfeMapper()
    
    with pytest.raises(MappingError, match="Os dados de entrada para o mapeamento devem ser um dicionário."):
        mapper.map("isto não é um dicionário")