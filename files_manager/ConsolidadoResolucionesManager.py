"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Consolidado de Resoluciones File Manager
 """

import pandas as pd
from utils.Constants import REGIONES_PROYECTOS_CONCEPTOS_FILENAME, CCONSOLIDADO_RESOLICIONES_TEMP_FILENAME, \
    TEMP_FOLDERNAME


class ConsolidadoResolucionesManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder
        pass

    def standardize_file(self, cr_filename, sheet_name_cr):
        try:
            # Read File Consolidación de Resololuciones cierre
            cr_cierre_df = pd.read_excel(self.root_source_folder + cr_filename, sheet_name_cr, index_col=None,
                                         converters={'COD REG': str, 'SUB UNID': str, 'CUENTA CATALOGO': str,
                                                     'CODIGO ORDINAL': str}, skiprows=[0, 1], na_values=['NA'])

            # Update 'COD REG' column validate ; 00X format
            cr_cierre_df['COD REG'] = cr_cierre_df['COD REG'].map(
                lambda cod: cod if "-" in str(cod) else ("00" + str(int(cod)))[-3:], na_action='ignore')

            # Generate 'COD DEP' column from the first four digits of 'DEPE SIIF' column
            cr_cierre_df['COD DEP'] = cr_cierre_df['DEPE SIIF'].map(lambda cod: str(cod)[:4], na_action='ignore')

            # Read Regiones y Proyectos file reference
            regiones_centros_df = pd.read_excel(self.root_source_folder + REGIONES_PROYECTOS_CONCEPTOS_FILENAME,
                                                'Regionales y Centros', usecols='B:F', skiprows=[0, 1], index_col=None,
                                                na_values=['NA'], converters={'COD REG.1': str, 'COD DEP.': str})

            # Merge cr_cierre_df and regiones_centros_df Dataframes for check 'REGIONAL','NOMBRE DEPENDENCIA' Columns orthography
            cr_cierre_df[['REGIONAL', 'NOMBRE DEPENDENCIA']] = pd.merge(cr_cierre_df[['COD REG', 'COD DEP']],
                                                                        regiones_centros_df, how='left',
                                                                        left_on=['COD REG', 'COD DEP'],
                                                                        right_on=['COD REG.1', 'COD DEP.'])[
                ['REGIONAL', 'NOMBRE DEPENDENCIA']]

            # ALGUNOS CODIGOS NO SE ENCUENTRAN, LE CODIGO ESPECIAL 36-02-00 NO SE ENCUENTRA EN LOS ARCHIVOS DE REFERENCIA APESAR DE QUE EN EL ARCHIVO DE MUESTRA SU NOMBRE DE DEPENDENCIA ES 'DIRECCIÓN JURÍDICA' Y 'DESPACHO DIRECCIÓN'
            # SUCEDE IGUAL 'CON COD REG'=001 Y 'COD DEP'=1010 APESAR DE QUE EN EL ARCHIVO DE MUESTRA SU NOMBRE DE DEPENDENCIA ES 'DESPACHO DIRECCIÓN '
            # SUCEDE IGUAL 'CON COD REG'=001 Y 'COD DEP'=2029 APESAR DE QUE EN EL ARCHIVO DE MUESTRA SU NOMBRE DE DEPENDENCIA ES 'SECRETARÍA GENERAL'

            # Read Proyetos list
            proyectos_df = pd.read_excel(self.root_source_folder + REGIONES_PROYECTOS_CONCEPTOS_FILENAME, 'Proyectos',
                                         usecols='B:C', skiprows=[0, 1], index_col=None, na_values=['NA'])

            # Get Project name from NaN codes from proyectos_df Dataframe
            nan_code_project = proyectos_df.loc[proyectos_df['COD. PROYECTO'].isnull()].PROYECTOS.values.any()

            # ESTA COLUMNA 'CODIGO DECRETO LEY 2020' CAMBIA CON EL AÑO?
            # Generate 'Proyecto' Column from 'CODIGO DECRETO LEY 2020' Column where mached, for nan values set nan_code_project value by default
            cr_cierre_df['PROYECTO'] = pd.merge(cr_cierre_df['CODIGO DECRETO LEY 2020'], proyectos_df, how='left',
                                                left_on=['CODIGO DECRETO LEY 2020'],
                                                right_on=['COD. PROYECTO']).PROYECTOS.fillna(nan_code_project)

            # Read Concepto interno GPO list
            concepto_interno_df = pd.read_excel(self.root_source_folder + REGIONES_PROYECTOS_CONCEPTOS_FILENAME,
                                                'Concepto interno GPO', usecols='C,E', skiprows=[0], index_col=None,
                                                na_values=['NA'])
            concepto_interno_df['CONCEPTOS INTERNOS SENA APERTURA'] = concepto_interno_df[
                'CONCEPTOS INTERNOS SENA APERTURA'].fillna(concepto_interno_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])

            # Update 'NOMBRE CONCEPTO INTERNO SENA' Column from concepto interno df Dataframe for check orthography
            # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by adjusting on concept_interno_df
            conceptos_adjust_df = pd.merge(cr_cierre_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(),
                                           concepto_interno_df,
                                           how='left', left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                           right_on=['CONCEPTOS INTERNOS SENA APERTURA'])

            # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
            conceptos_ok_spelling_df = pd.merge(cr_cierre_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(),
                                                concepto_interno_df, how='left',
                                                left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                                right_on=['CONCEPTOS INTERNOS SENA REPORTES GPO'])

            # ALGUNOS CONCEPTOS DE SENA NO TIENEN CORRECCION ORTOGRAFICA
            # cr_cierre_df[['COD REG', 'COD DEP']].iloc[161]

            # ALGUNOS CONCEPTOS DE SENA NO TIENEN CORRECCION ORTOGRAFICA NI VALIDOS NI INVALIDOS, NO APARECEN
            # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
            cen_compromisos_df = conceptos_adjust_df['CONCEPTOS INTERNOS SENA REPORTES GPO'].fillna(
                conceptos_ok_spelling_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
            cr_cierre_df['NOMBRE CONCEPTO INTERNO SENA'] = cen_compromisos_df

            # Change Columns names
            cr_cierre_df = cr_cierre_df.rename(
                columns={'COD REG': 'C. REGIONAL', 'REGIONAL': 'N. REGIONAL', 'NOMBRE DEPENDENCIA': 'N. DEPENDENCIA',
                         'NOMBRE CONCEPTO INTERNO SENA': 'CONCEPTO INTERNO SENA GPO'})

            # Save standardized Consolidacion de Resoluciones File
            cr_cierre_df.to_excel(self.root_source_folder + TEMP_FOLDERNAME + CCONSOLIDADO_RESOLICIONES_TEMP_FILENAME,
                                  index=False)

            # return True indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError

    def build_file(self):
        try:
            print("build_file")
            # Read standardized consolidacion_resoluciones_cierre
            consolidado_resoluciones_df = pd.read_excel(CCONSOLIDADO_RESOLICIONES_TEMP_FILENAME, 'Sheet1',
                                                        converters={'C. REGIONAL': str, 'SUB UNID': str,
                                                                    'DEPE SIIF': str, 'COD DEP SIIF': str,
                                                                    'CUENTA CATALOGO': str, 'CODIGO ORDINAL': str,
                                                                    'RECURSO': str}, na_values=['NA'])

            # Generate 'LLAVE' Column concatenating 'C. REGIONAL', 'DEPE SIIF', 'POSICION CATALOGO DEL GASTO', 'RECURSO' y 'CONCEPTO INTERNO SENA GPO'
            consolidado_resoluciones_df['LLAVE'] = consolidado_resoluciones_df['C. REGIONAL'] + \
                                                   consolidado_resoluciones_df['DEPE SIIF'] + \
                                                   consolidado_resoluciones_df['POSICION CATALOGO DEL GASTO'] + \
                                                   consolidado_resoluciones_df['RECURSO'] + consolidado_resoluciones_df[
                                                       'CONCEPTO INTERNO SENA GPO']

            # Return build file
            return consolidado_resoluciones_df
        except ValueError:
            print(ValueError)
            return ValueError


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    cr_filename = "Consolidado Resoluciones.xlsx"
    sheet_name_cr = 'Administrativa'
    cr_manager = ConsolidadoResolucionesManager(root_source_folder)
    standardize_file_result = cr_manager.standardize_file(cr_filename, sheet_name_cr)
    print(standardize_file_result)
