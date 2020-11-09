"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Cen Compromisos File Manager
 """

import pandas as pd
from utils.Constants import REGIONES_PROYECTOS_CONCEPTOS_FILENAME, CEN_COMPROMISOS_TEMP_FILENAME, TEMP_FOLDERNAME


class CenCompromisosManager:

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year
        pass

    def standardize_file(self, cen_compromisos_filename, sheet_name_cc):
        try:
            # EL ARCHIVO SIEMPRE LLEGA CON FORMATO xlsb?
            print("standardize_file")
            # Read File Cen de Compromisos cierre
            # Get the header like a row because pandas can't get the header directly, after get dataset replace header
            cen_compromisos_df = pd.read_excel(self.root_source_folder + cen_compromisos_filename, sheet_name_cc,
                                               index_col=None, skiprows=[0, 1, 3, 4, 5], na_values=['NA'],
                                               engine='pyxlsb')
            header_row = 0
            cen_compromisos_df.columns = cen_compromisos_df.iloc[header_row]
            cen_compromisos_df = cen_compromisos_df.drop(header_row)

            # Update 'Cod Regional' column validate ; 00X format
            cen_compromisos_df['Cod Regional'] = cen_compromisos_df['Cod Regional'].map(
                lambda cod: cod if "-" in str(cod) else ("00" + str(int(cod)))[-3:], na_action='ignore')

            # Concepto interno SENA GPO QUE AUN NO SE SABE PORQUE ALGUNAS COSAS SI CAZAN Y OTRAS NO
            # Read Concepto interno GPO list
            concepto_interno_df = pd.read_excel(self.root_source_folder + REGIONES_PROYECTOS_CONCEPTOS_FILENAME,
                                                'Concepto interno GPO',
                                                usecols='C,E', skiprows=[0], index_col=None, na_values=['NA'])
            concepto_interno_df['CONCEPTOS INTERNOS SENA APERTURA'] = concepto_interno_df[
                'CONCEPTOS INTERNOS SENA APERTURA'].fillna(concepto_interno_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])

            # Update 'NOMBRE CONCEPTO INTERNO SENA' Column from concepto interno df Dataframe for check orthography
            column_nombre_rublo = 'Nombre Rubro Presupuestal {}'.format(self.current_year)
            # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by adjusting on concept_interno_df
            conceptos_adjust_df = pd.merge(cen_compromisos_df[column_nombre_rublo].str.strip(), concepto_interno_df,
                                           how='left', left_on=[column_nombre_rublo],
                                           right_on=['CONCEPTOS INTERNOS SENA APERTURA'])
            # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
            conceptos_finded_df = pd.merge(cen_compromisos_df[column_nombre_rublo].str.strip(), concepto_interno_df,
                                           how='left', left_on=[column_nombre_rublo],
                                           right_on=['CONCEPTOS INTERNOS SENA REPORTES GPO'])

            # ALGUNOS CONCEPTOS DE SENA NO TIENEN CORRECCION ORTOGRAFICA NI VALIDOS NI INVALIDOS, NO APARECEN
            # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
            conceptos_ok_spelling_df = conceptos_adjust_df['CONCEPTOS INTERNOS SENA REPORTES GPO'].fillna(
                conceptos_finded_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
            cen_compromisos_df[column_nombre_rublo] = conceptos_ok_spelling_df

            # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
            cen_compromisos_df['Valor obligado'] = cen_compromisos_df['Valor Actual'] - cen_compromisos_df[
                'Saldo por Obligar']

            # FALTAN LAS COLUMNAS 'Fecha de Registro', 'Fecha de Creacion' Y 'Fecha de Documento Soporte' DE DONDE SALEN?
            # LAS COLUMNAS 'BPIN 2018 Registro' Y 'BPIN 2019 Registro' HACEN REFERNCIA A UN HISTORICO ANUAL, ESTE ARCHIVO CRECE A TRAVES DE LOS AÑOS? O SE REEMPLAZA CON LOS DOS AÑOS PREVIOS?
            # SUCEDE LO MISMO CON 'Nombre Rubro Presupuestal 2018' Y 'BPIN 2018'
            # EN EL ARCHIVO DE RESULTADO ESTAN LAS COLUMNAS 'Estado' Y 'Objeto de CDP' PERO NO SE ENCUENTRAN EN EL ARCHIVO DE ORIGEN

            # Save standardized Cen de Compromisos File
            cen_compromisos_df.to_excel(self.root_source_folder + TEMP_FOLDERNAME + CEN_COMPROMISOS_TEMP_FILENAME,
                                        index=False)

            # return True indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError

    def build_file(self):
        try:
            print("build_file")
            # Read standardized cen_compromisos
            cen_compromisos_df = pd.read_excel(CEN_COMPROMISOS_TEMP_FILENAME, 'Sheet1',
                                               converters={'Cod Regional': str}, na_values=['NA'])

            # Generate 'LLAVE' Column concatenating 'Cod Regional', 'Código Dependencia Gasto', 'Posicion del Gasto', 'REC' y 'Nombre Rubro Presupuestal {year}'
            cen_compromisos_df['LLAVE'] = cen_compromisos_df['Cod Regional'] + cen_compromisos_df[
                'Código Dependencia Gasto'] + cen_compromisos_df['Posicion del Gasto'] + cen_compromisos_df['REC'] + \
                                          cen_compromisos_df['Nombre Rubro Presupuestal {}'.format(self.current_year)]

            # LA COLUMNA 'Nombre Rubro Presupuestal 2018' CAMBIA CON EL AÑO ??? 2020???

            # Return build file
            return cen_compromisos_df
        except ValueError:
            print(ValueError)
            return ValueError


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    cc_filename = "CEN COMPROMISOS CONS NAL A 30 SEPT 2020_CIERRE_01102020 - Homologado.xlsb"
    sheet_name_cc = 'CEN COMPR CONSNAL A 30SEPT20_C '
    year = 2018
    cc_manager = CenCompromisosManager(root_source_folder, year)
    standardize_file_result = cc_manager.standardize_file(cc_filename, sheet_name_cc)
    print(standardize_file_result)
