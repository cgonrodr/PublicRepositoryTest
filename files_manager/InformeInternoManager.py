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

class InformeInternoManager:

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year

    def build_informe(self, cr_llaves_df, cc_llaves_df, apertura_llaves_df):
        try:
            print("Build Informe")

            #cr_llaves_df


            # return Successful indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError



if __name__ == "__main__":
    pass
