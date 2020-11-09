"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Apertura File Manager
 """

import pandas as pd
from utils.Constants import APERTURA_TEMP_FILENAME, TEMP_FOLDERNAME


class AperturaManager:

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year
        pass

    def standardize_file(self, apertura_filename, sheet_name_apertura):
        try:
            print("standardize_file")
            # Read File Apertura File
            apertura_df = pd.read_excel(self.root_source_folder + apertura_filename, sheet_name_apertura,
                                        index_col=None,
                                        converters={'COD REG': str, 'SUB UNID': str, 'COD SUB': str,
                                                    'COD DEP SIIF': str, 'FUENTE RECUR': str,
                                                    'SITUACIÓN DE FONDOS': str, 'TIPO DOC (RES)': str,
                                                    'No. RESOL': str}, skiprows=[0, 1, 2], na_values=['NA'])

            # Save standardized Apertura File
            apertura_df.to_excel(self.root_source_folder + TEMP_FOLDERNAME + APERTURA_TEMP_FILENAME, index=False)

            # EN EL ARCHIVO DE SALIDA SE ENCUENTRAN LAS COLUMNAS 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA', 'CONCEPTO INTERNO SENA GPO' Y 'PROYECTO'
            # SEMEJANTES A LAS ESTANDARIZADAS EN CONSOLIDADO DE RESOLUCIONES, AQUI TAMBIEN SE REALIZA LA ESTANDARIZACION?

            # return True indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError

    def build_file(self):
        try:
            print("build_file")
            # Read standardized apertura_year
            apertura_df = pd.read_excel(APERTURA_TEMP_FILENAME, 'Sheet1',
                                        converters={'COD REG': str, 'SUB UNID': str, 'COD SUB': str,
                                                    'COD DEP SIIF': str,
                                                    'FUENTE RECUR': str, 'SITUACIÓN DE FONDOS': str,
                                                    'TIPO DOC (RES)': str,
                                                    'No. RESOL': str, 'DEPE SIIF': str,
                                                    'REC {}'.format(self.current_year): str},
                                        na_values=['NA'])

            # Generate 'LLAVE' Column concatenating 'COD REG', 'DEPE SIIF', 'POSICION DEL GASTO', 'REC {year}' y 'NOMBRE CONCEPTO INTERNO SENA'
            apertura_df['LLAVE'] = apertura_df['COD REG'] + apertura_df['DEPE SIIF'] + apertura_df[
                'POSICION DEL GASTO'] + apertura_df['REC {}'.format(self.current_year)] + apertura_df[
                                       'NOMBRE CONCEPTO INTERNO SENA']

            # Return build file
            return apertura_df
        except ValueError:
            print(ValueError)
            return ValueError


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    apertura_filename = "APERTURA FUNCIONAMIENTO-INVERSIÓN 2020.xlsx"
    sheet_name_apertura = 'APERTURA FUNC-GASTOS 2020'
    apertura_manager = AperturaManager(root_source_folder)
    standardize_file_result = apertura_manager.standardize_file(apertura_filename, sheet_name_apertura)
    print(standardize_file_result)
