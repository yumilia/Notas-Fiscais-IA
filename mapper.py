# Arquivo: mapper.py

# ======================================================================================
# NOTA IMPORTANTE: CLASSES MOCK (SIMULADAS)
# Como não podemos instanciar objetos reais da `pynfe` sem um ambiente completo
# (certificado digital, etc.), criamos classes de simulação (mocks) abaixo.
# Elas têm a mesma estrutura e nomes de atributos que as classes reais da `pynfe`.
# No seu projeto final, você deve REMOVER estas classes e importar as reais:
# from pynfe.processamento import NFe
# from pynfe.entidades.nfe import Ide, Emit, Dest, Det, Total, etc.
# ======================================================================================

class MockPyNFeObject:
    """Classe base para simular a estrutura de objetos da pynfe."""
    def __repr__(self):
        # Gera uma representação legível do objeto e seus atributos
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith('_'))
        return f"{self.__class__.__name__}({attrs})"

class Ide(MockPyNFeObject): pass
class Emit(MockPyNFeObject): pass
class Dest(MockPyNFeObject): pass
class Prod(MockPyNFeObject): pass
class Imposto(MockPyNFeObject): pass
class ICMS(MockPyNFeObject): pass
class IPI(MockPyNFeObject): pass
class PIS(MockPyNFeObject): pass
class COFINS(MockPyNFeObject): pass
class Det(MockPyNFeObject):
    def __init__(self):
        self.prod = Prod()
        self.imposto = Imposto()
        self.imposto.ICMS = ICMS()
        self.imposto.IPI = IPI()
        self.imposto.PIS = PIS()
        self.imposto.COFINS = COFINS()
class ICMSTot(MockPyNFeObject): pass
class Total(MockPyNFeObject):
    def __init__(self):
        self.ICMSTot = ICMSTot()
class Transp(MockPyNFeObject): pass
class InfNFe(MockPyNFeObject):
    def __init__(self):
        self.ide = Ide()
        self.emit = Emit()
        self.dest = Dest()
        self.det = []  # Inicializa como lista vazia
        self.total = Total()
        self.transp = Transp()
class NFe(MockPyNFeObject):
    def __init__(self):
        self.infNFe = InfNFe()

# ======================================================================================
# FIM DAS CLASSES MOCK - Início da lógica do Mapper
# ======================================================================================

class MappingError(Exception):
    """Exceção customizada para erros que ocorrem durante o mapeamento."""
    pass

class JsonToPyNfeMapper:
    """
    Responsável por converter um dicionário JSON (extraído pelo Gemini)
    em um objeto NFe estruturado, compatível com a biblioteca PyNfe.
    """

    def map(self, json_data: dict) -> NFe:
        """
        Método principal que orquestra o mapeamento do JSON para o objeto NFe.

        Args:
            json_data: Dicionário com os dados extraídos da NF-e.

        Returns:
            Uma instância do objeto NFe (ou MockNFe) preenchida.

        Raises:
            MappingError: Se um campo obrigatório estiver ausente ou ocorrer um erro.
        """
        if not isinstance(json_data, dict):
            raise MappingError("Os dados de entrada para o mapeamento devem ser um dicionário.")

        print("Iniciando mapeamento do JSON para o objeto NFe.")
        try:
            nfe_obj = NFe()
            infNFe = nfe_obj.infNFe

            # Mapeia cada grupo da NF-e usando métodos auxiliares
            self._map_ide(json_data.get('ide', {}), infNFe.ide)
            self._map_emit(json_data.get('emitente', {}), infNFe.emit)
            self._map_dest(json_data.get('destinatario', {}), infNFe.dest)
            
            # Mapeia a lista de itens
            infNFe.det = [self._map_item(item_json) for item_json in json_data.get('itens', [])]
            
            self._map_total(json_data.get('totais', {}), infNFe.total)
            self._map_transp(json_data.get('transporte', {}), infNFe.transp)

            # Adiciona a chave de acesso ao nível correto
            infNFe.Id = f"NFe{json_data.get('chave_acesso', '')}"
            
            print("Mapeamento concluído com sucesso.")
            return nfe_obj
        except KeyError as e:
            raise MappingError(f"Campo obrigatório ausente no JSON durante o mapeamento: {e}")
        except Exception as e:
            # Captura outras exceções para fornecer um contexto claro
            raise MappingError(f"Erro inesperado durante o mapeamento: {e}")

    def _map_ide(self, data: dict, ide_obj: Ide):
        """Mapeia o grupo de Identificação da NF-e (ide)."""
        ide_obj.nNF = data.get('numero_nf')
        ide_obj.serie = data.get('serie')
        ide_obj.dEmi = data.get('data_emissao')
        # Adicione outros campos do grupo 'ide' aqui conforme necessário

    def _map_emit(self, data: dict, emit_obj: Emit):
        """Mapeia o grupo do Emitente (emit)."""
        emit_obj.xNome = data.get('nome')
        emit_obj.CNPJ = data.get('cnpj')
        # Adicione outros campos do grupo 'emit' aqui

    def _map_dest(self, data: dict, dest_obj: Dest):
        """Mapeia o grupo do Destinatário (dest)."""
        dest_obj.xNome = data.get('nome')
        dest_obj.CNPJ_CPF = data.get('cnpj_cpf') # O nome do campo pode variar na PyNfe
        # Adicione outros campos do grupo 'dest' aqui

    def _map_item(self, data: dict) -> Det:
        """Mapeia um único item (produto) da NF-e para um objeto Det."""
        item_obj = Det()
        
        # Mapeia os dados do produto
        item_obj.prod.cProd = data.get('codigo_produto')
        item_obj.prod.xProd = data.get('descricao')
        item_obj.prod.NCM = data.get('ncm')
        item_obj.prod.CFOP = data.get('cfop')
        item_obj.prod.uCom = data.get('unidade')
        item_obj.prod.qCom = data.get('quantidade')
        item_obj.prod.vUnCom = data.get('valor_unitario')
        item_obj.prod.vProd = data.get('valor_total')

        # Mapeia os dados de impostos do item
        item_obj.imposto.ICMS.vBC = data.get('base_calculo_icms')
        item_obj.imposto.ICMS.vICMS = data.get('valor_icms')
        item_obj.imposto.ICMS.pICMS = data.get('aliquota_icms')
        item_obj.imposto.IPI.vIPI = data.get('valor_ipi')
        
        return item_obj

    def _map_total(self, data: dict, total_obj: Total):
        """Mapeia o grupo de Totais da NF-e."""
        icms_tot = total_obj.ICMSTot
        icms_tot.vBC = data.get('base_calculo_icms')
        icms_tot.vICMS = data.get('valor_icms')
        icms_tot.vProd = data.get('valor_total_produtos')
        icms_tot.vFrete = data.get('valor_frete')
        icms_tot.vSeg = data.get('valor_seguro')
        icms_tot.vOutro = data.get('outras_despesas')
        icms_tot.vIPI = data.get('valor_total_ipi')
        icms_tot.vNF = data.get('valor_total_nf')

    def _map_transp(self, data: dict, transp_obj: Transp):
        """Mapeia o grupo de Transporte."""
        transp_obj.modFrete = data.get('modalidade_frete')
        # Adicione outros campos de transporte aqui