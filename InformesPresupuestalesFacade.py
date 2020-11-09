"""
Provide a unified interface to a set of interfaces in a subsystem.
Facade defines a higher-level interface that makes the subsystem easier
to use.
"""

from files_manager.AperturaManager import AperturaManager
from files_manager.CenCompromisosManager import CenCompromisosManager
from files_manager.ConsolidadoResolucionesManager import ConsolidadoResolucionesManager


class InformesPresupuestalesFacade:
    """
    Know which subsystem classes are responsible for a request.
    Delegate client requests to appropriate subsystem objects.
    """

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year

    def standardize_root_files(self, apertura_filename, cr_filename, cc_filename):
        # Init standardize results list
        standardize_results = []

        # Standardize Apertura File
        sheet_name_apertura = 'APERTURA FUNC-GASTOS 2020'
        apertura_manager = AperturaManager(self.root_source_folder, self.current_year)
        standardize_results.append(apertura_manager.standardize_file(apertura_filename, sheet_name_apertura))

        # Standardize Consolidado de Resoluciones File
        sheet_name_cr = 'Administrativa'
        cr_manager = ConsolidadoResolucionesManager(root_source_folder)
        standardize_results.append(cr_manager.standardize_file(cr_filename, sheet_name_cr))

        # Standardize Cen de Compromisos File
        sheet_name_cc = 'CEN COMPR CONSNAL A 30SEPT20_C '
        cc_manager = CenCompromisosManager(root_source_folder, self.current_year)
        standardize_results.append(cc_manager.standardize_file(cc_filename, sheet_name_cc))

        # Return standardize results list
        return standardize_results

    def build_informe_general(self):
        pass
        # self._subsystem_1.operation1()
        # self._subsystem_1.operation2()
        # self._subsystem_2.operation1()
        # self._subsystem_2.operation2()

    def build_informe_rublos(self):
        pass
        # self._subsystem_1.operation1()
        # self._subsystem_1.operation2()
        # self._subsystem_2.operation1()
        # self._subsystem_2.operation2()


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    current_year = 2018
    informes_presupuestales_facade = InformesPresupuestalesFacade(root_source_folder, current_year)
    apertura_filename = "APERTURA FUNCIONAMIENTO-INVERSIÓN 2020.xlsx"
    sheet_name_apertura = 'APERTURA FUNC-GASTOS 2020'
    cr_filename = "Consolidado Resoluciones.xlsx"
    sheet_name_cr = 'Administrativa'
    cc_filename = "CEN COMPROMISOS CONS NAL A 30 SEPT 2020_CIERRE_01102020 - Homologado.xlsb"
    sheet_name_cc = 'CEN COMPR CONSNAL A 30SEPT20_C '
    standardize_results = informes_presupuestales_facade.standardize_root_files(apertura_filename, cr_filename, cc_filename)
    print(standardize_results)