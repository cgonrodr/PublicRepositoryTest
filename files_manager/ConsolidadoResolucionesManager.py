"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Consolidado de Resoluciones File Manager
 """

import pandas as pd
from utils.Constants import FILENAME_REGIONES_PROYECTOS_CONCEPTOS, FOLDERNAME_TEMP, \
    FILENAME_TEMP_CR, FILENAME_INVALID_REG_DEP, FILENAME_INVALID_PROYECTOS, \
    FILENAME_INVALID_CONCEPTOS, FILENAME_INVALID_LLAVES, FOLDERNAME_FAIL_FILES
from files_manager.RegionalesProyectosCfManager import RegionalesProyectosCfManager
from utils.Utils import Utils


class ConsolidadoResolucionesManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder

    def standardize_file(self, cr_filename):
        """Standasdize File Consolidado Resoluciones

        Return 'Successful' if process finished OK

        Parameters
        ----------
        cr_filename : string
            consolidado resoluciones file name

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        print("Standardize Consolidado Resoluciones File")
        # Open Regionales Proyectos File manager for read strandarize data
        regionales_proyectos_manager = RegionalesProyectosCfManager(self.root_source_folder)

        # Read File Consolidación de Resololuciones cierre
        cr_cierre_df = pd.read_excel(self.root_source_folder + cr_filename, 'Administrativa', index_col=None,
                                     converters={'COD REG': str, 'SUB UNID': str, 'CUENTA CATALOGO': str,
                                                 'CODIGO ORDINAL': str}, skiprows=[0, 1], na_values=['NA'])

        # Add Column number
        cr_cierre_df['Fila'] = cr_cierre_df.index + 4

        # Create Column 'C. REGIONAL'= 'COD REG' column validate 00X format
        cr_cierre_df['C. REGIONAL'] = cr_cierre_df['COD REG'].map(
            lambda cod: cod if "-" in str(cod) else ("00" + str(int(cod)))[-3:], na_action='ignore')

        # Generate 'COD DEP' column from the first four digits of 'DEPE SIIF' column
        cr_cierre_df['COD DEP'] = cr_cierre_df['DEPE SIIF'].map(lambda cod: str(cod)[:4], na_action='ignore')

        # Read Regiones y Proyectos file reference
        regiones_centros_df = regionales_proyectos_manager.read_regionales_centros_data()
        # Merge cr_cierre_df and regiones_centros_df Dataframes for check 'REGIONAL','NOMBRE DEPENDENCIA' Columns orthography
        cr_cierre_df[['N. REGIONAL', 'N. DEPENDENCIA']] = pd.merge(cr_cierre_df[['C. REGIONAL', 'COD DEP']],
                                                                   regiones_centros_df, how='left',
                                                                   left_on=['C. REGIONAL', 'COD DEP'],
                                                                   right_on=['COD REG.1', 'COD DEP.'])[
            ['REGIONAL', 'NOMBRE DEPENDENCIA']]

        # Read Proyetos list
        proyectos_df = regionales_proyectos_manager.read_proyectos_data()
        # Get Project name from NaN codes from proyectos_df Dataframe
        nan_code_project = proyectos_df.loc[proyectos_df['COD. PROYECTO'].isnull()].PROYECTOS.values.any()
        # Get the upper year found in columns RUBRO LEY SIIF_*year*
        columnname_decreto_ley = Utils.get_columnname_by_upper_year('CODIGO DECRETO LEY {}', cr_cierre_df.columns)
        # Generate 'Proyecto' Column from 'CODIGO DECRETO LEY 2020' Column where mached, for nan values set nan_code_project value by default
        cr_cierre_df['PROYECTO'] = pd.merge(cr_cierre_df[columnname_decreto_ley], proyectos_df, how='left',
                                            left_on=[columnname_decreto_ley],
                                            right_on=['COD. PROYECTO']).PROYECTOS.fillna(nan_code_project)

        # Read Concepto interno GPO list
        concepto_interno_df = regionales_proyectos_manager.read_concepto_interno_gpo_data()
        concepto_interno_df['CONCEPTOS INTERNOS SENA APERTURA'] = concepto_interno_df[
            'CONCEPTOS INTERNOS SENA APERTURA'].fillna(concepto_interno_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Update 'NOMBRE CONCEPTO INTERNO SENA' Column from concepto interno df Dataframe for check orthography
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by adjusting on concept_interno_df
        conceptos_adjust_df = pd.merge(cr_cierre_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(), concepto_interno_df,
                                       how='left', left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                       right_on=['CONCEPTOS INTERNOS SENA APERTURA'])
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
        conceptos_ok_spelling_df = pd.merge(cr_cierre_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(),
                                            concepto_interno_df, how='left', left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                            right_on=['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
        conceptos_internos_df = conceptos_adjust_df['CONCEPTOS INTERNOS SENA REPORTES GPO'].fillna(
            conceptos_ok_spelling_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        cr_cierre_df['CONCEPTO INTERNO SENA GPO'] = conceptos_internos_df

        # Validate standardize columns
        # Check 'REGIONAL' and 'NOMBRE DEPENDENCIA' with NaN values from 'COD REG' and 'COD DEP'
        if cr_cierre_df.loc[cr_cierre_df['N. REGIONAL'].isnull()].size > 0:
            invalid_reg_dep_df = cr_cierre_df[['Fila', 'COD REG', 'COD DEP', 'REGIONAL', 'NOMBRE DEPENDENCIA']].loc[
                cr_cierre_df['N. REGIONAL'].isnull()]
            invalid_reg_dep_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_REG_DEP + FILENAME_TEMP_CR, index=False)
        # Check 'PROYECTO'  with NaN values from 'CODIGO DECRETO LEY'
        if cr_cierre_df.loc[cr_cierre_df['PROYECTO'].isnull()].size > 0:
            invalid_proyecto_df = cr_cierre_df[['Fila', columnname_decreto_ley, 'PROYECTO']].loc[
                cr_cierre_df['PROYECTO'].isnull()]
            invalid_proyecto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_PROYECTOS + FILENAME_TEMP_CR, index=False)
        # Check 'REGIONAL' and 'NOMBRE DEPENDENCIA' with NaN values from 'COD REG' and 'COD DEP'
        if cr_cierre_df.loc[cr_cierre_df['CONCEPTO INTERNO SENA GPO'].isnull()].size > 0:
            invalid_concepto_df = cr_cierre_df[['Fila', 'NOMBRE CONCEPTO INTERNO SENA', 'CONCEPTO INTERNO SENA GPO']].loc[
                    cr_cierre_df['CONCEPTO INTERNO SENA GPO'].isnull()]
            invalid_concepto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_CONCEPTOS + FILENAME_TEMP_CR, index=False)

        # Save standardized Consolidacion de Resoluciones File
        cr_cierre_df.to_excel(self.root_source_folder + FOLDERNAME_TEMP + FILENAME_TEMP_CR, index=False)

        # return True indicating good execution
        print("Result: Successful")
        return "Successful"

    def build_llaves(self):
        """Build LLAVES Consolidado Resoluciones

        Return 'Successful' if process finished OK

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        
        print("Build Consolidado Resoluciones LLAVES")
        # Read standardized consolidacion_resoluciones_cierre
        cr_cierre_df = pd.read_excel(
            self.root_source_folder + FOLDERNAME_TEMP + FILENAME_TEMP_CR,
            0, converters={'C. REGIONAL': str, 'SUB UNID': str, 'DEPE SIIF': str,
                            'COD DEP SIIF': str, 'CUENTA CATALOGO': str, 'CODIGO ORDINAL': str,
                            'RECURSO': str}, na_values=['NA'])

        # Define if exist the nan values ​​in columns required for build KEYS
        invalid_llaves_df = cr_cierre_df.loc[
            cr_cierre_df['C. REGIONAL'].isnull() | cr_cierre_df['DEPE SIIF'].isnull() | cr_cierre_df[
                'POSICION CATALOGO DEL GASTO'].isnull() | cr_cierre_df['RECURSO'].isnull() | cr_cierre_df[
                'CONCEPTO INTERNO SENA GPO'].isnull()][
            ['Fila', 'C. REGIONAL', 'DEPE SIIF', 'POSICION CATALOGO DEL GASTO', 'RECURSO', 'CONCEPTO INTERNO SENA GPO']]
        invalid_llaves_df.to_excel(
            self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_LLAVES + FILENAME_TEMP_CR, index=False)

        # Drop invalid values for create LLAVES
        cr_cierre_df = cr_cierre_df.dropna(
            subset=['C. REGIONAL', 'DEPE SIIF', 'POSICION CATALOGO DEL GASTO', 'RECURSO',
                    'CONCEPTO INTERNO SENA GPO'])

        # Generate 'LLAVE' Column concatenating 'COD REG', 'DEPE SIIF', 'POSICION CATALOGO DEL GASTO', 'RECURSO' y 'CONCEPTO INTERNO SENA GPO'
        cr_cierre_df['LLAVE'] = cr_cierre_df['C. REGIONAL'] + cr_cierre_df[
            'DEPE SIIF'] + cr_cierre_df['POSICION CATALOGO DEL GASTO'] + cr_cierre_df['RECURSO'] + \
                                cr_cierre_df['CONCEPTO INTERNO SENA GPO']

        print(cr_cierre_df[
                    ['LLAVE', 'C. REGIONAL', 'DEPE SIIF', 'POSICION CATALOGO DEL GASTO', 'RECURSO',
                    'CONCEPTO INTERNO SENA GPO']])

        # Return build file
        return cr_cierre_df
        


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    cr_filename = "Consolidado Resoluciones.xlsx"
    sheet_name_cr = 'Administrativa'
    cr_manager = ConsolidadoResolucionesManager(root_source_folder)
    standardize_file_result = cr_manager.standardize_file(cr_filename)
    print(standardize_file_result)
