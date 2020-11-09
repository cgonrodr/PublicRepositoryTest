"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Informe File Manager
 """

import pandas as pd
from files_manager.AperturaManager import AperturaManager
from files_manager.ConsolidadoResolucionesManager import ConsolidadoResolucionesManager
from files_manager.CenCompromisosManager import CenCompromisosManager

class InformeManager:

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year
        pass

    def build_informe(self):
        try:
            print("build_informe")
            # Get building Apertura File
            apertura_manager=AperturaManager(self.root_source_folder, self.current_year)
            apertura_df = apertura_manager.build_file()

            # Get building Consolidacion de Resoluciones File
            cr_manager = ConsolidadoResolucionesManager(self.root_source_folder)
            consolidado_resoluciones_df = cr_manager.build_file()

            # Get building Cen de Compromisos File
            cc_manager = CenCompromisosManager(self.root_source_folder, self.current_year)
            cen_compromisos_df = cc_manager.build_file()

            # Make crosses



            # return True indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError



if __name__ == "__main__":
    pass
