"""
Provide a unified interface to a set of interfaces in a subsystem.
Facade defines a higher-level interface that makes the subsystem easier
to use.
"""

from files_manager.AperturaManager import AperturaManager
from files_manager.CenCompromisosManager import CenCompromisosManager
from files_manager.ConsolidadoResolucionesManager import ConsolidadoResolucionesManager
from files_manager.InformeInternoManager import InformeInternoManager
import datetime


class InformesPresupuestalesFacade:
    """
    Know which subsystem classes are responsible for a request.
    Delegate client requests to appropriate subsystem objects.
    """

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder
        self.current_year = datetime.datetime.now().year

    def standardize_root_files(self, apertura_filename, cr_filename, cc_filename):
        print('Start Standardize Files')

        try:
            # Init standardize results list
            standardize_results = []
            
            # Standardize Consolidado de Resoluciones File
            cr_manager = ConsolidadoResolucionesManager(root_source_folder)
            standardize_results.append(cr_manager.standardize_file(cr_filename))

            # Standardize Cen de Compromisos File
            cc_manager = CenCompromisosManager(root_source_folder)
            standardize_results.append(cc_manager.standardize_file(cc_filename))

            # Standardize Apertura File
            apertura_manager = AperturaManager(self.root_source_folder, self.current_year)
            standardize_results.append(apertura_manager.standardize_file(apertura_filename))

            print(standardize_results)

            # Check if all results are 'Successful', return Successful if yes
            if len(set(standardize_results)) == 1 and str(set(standardize_results)) == "{'Successful'}":
                return 'Successful'
            
            # Return the complete errors set
            return str(set(standardize_results))
        
        except Exception as e:
            print(e)
            return e


    def build_informe_report(self):
        print('Build Informes Report')

        try:
            # Standardize Consolidado de Resoluciones File
            cr_manager = ConsolidadoResolucionesManager(self.root_source_folder)
            cr_llaves_df = cr_manager.build_llaves()

            # Standardize Cen de Compromisos File
            cc_manager = CenCompromisosManager(self.root_source_folder)
            cc_llaves_df = cc_manager.build_llaves()

            # Standardize Apertura File
            apertura_manager = AperturaManager(self.root_source_folder, self.current_year)
            apertura_llaves_df = apertura_manager.build_llaves()

            # Build Informe Interno
            informe_interno_manager = InformeInternoManager(self.root_source_folder)
            informe_interno_manager.build_informe(cr_llaves_df, cc_llaves_df, apertura_llaves_df)

            
        except ValueError:
            print(ValueError)
            return ValueError



    def build_informe_rublos(self):
        pass
        # self._subsystem_1.operation1()
        # self._subsystem_1.operation2()
        # self._subsystem_2.operation1()
        # self._subsystem_2.operation2()


if __name__ == "__main__":
    root_source_folder = "C:\\Users\\cgonrodr\\OneDrive - everis\\Documentos\\PruebaPythonExcel\\"
    informes_presupuestales_facade = InformesPresupuestalesFacade(root_source_folder)
    apertura_filename = "APERTURA FUNCIONAMIENTO-INVERSIÓN 2020.xlsx"
    sheet_name_apertura = 'APERTURA FUNC-GASTOS 2020'
    cr_filename = "Consolidado Resoluciones.xlsx"
    sheet_name_cr = 'Administrativa'
    cc_filename = "CEN COMPROMISOS CONS NAL A 30 SEPT 2020_CIERRE_01102020 - Homologado.xlsb"
    sheet_name_cc = 'CEN COMPR CONSNAL A 30SEPT20_C '
    #standardize_results = informes_presupuestales_facade.standardize_root_files(apertura_filename, cr_filename,
    #                                                                            cc_filename)
    #print(standardize_results)

    informes_presupuestales_facade.build_informe_report()                                                                            
    
