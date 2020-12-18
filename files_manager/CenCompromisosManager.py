"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Cen Compromisos File Manager
 """

import pandas as pd
from utils.Constants import FOLDERNAME_STANDARDIZE_FILES, FILENAME_TEMP_CC, FILENAME_INVALID_REG_DEP, \
    FILENAME_INVALID_PROYECTOS, FILENAME_INVALID_CONCEPTOS, FOLDERNAME_FAIL_FILES, FILENAME_INVALID_LLAVES
from files_manager.RegionalesProyectosCfManager import RegionalesProyectosCfManager
from utils.Utils import Utils


class CenCompromisosManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder
        pass

    def standardize_file(self, cen_compromisos_filename):
        """Standasdize File Cen de Compromisos

        Return 'Successful' if process finished OK

        Parameters
        ----------
        cen_compromisos_filename : string
            cen de compromisos file name

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        print("Standardize CEN de Compromisos File")
        # Open Regionales Proyectos File manager for read strandarize data
        regionales_proyectos_manager = RegionalesProyectosCfManager(self.root_source_folder)

        # Read File Cen de Compromisos cierre
        # Get the header like a row because pandas can't get the header directly, after get dataset replace header
        cen_compromisos_df = pd.read_excel(self.root_source_folder + cen_compromisos_filename, 0, index_col=None,
                                           skiprows=[0, 1, 3, 4, 5], na_values=['NA'], engine='pyxlsb')

        header_row = 0
        cen_compromisos_df.columns = cen_compromisos_df.iloc[header_row]
        cen_compromisos_df = cen_compromisos_df.drop(header_row)
        cen_compromisos_df = cen_compromisos_df.reset_index()

        # Add Column number
        cen_compromisos_df['Fila'] = cen_compromisos_df.index + 8

        # Update 'Cod Regional' column validate ; 00X format
        cen_compromisos_df['C. REGIONAL'] = cen_compromisos_df['Cod Regional'].map(
            lambda cod: cod if "-" in str(cod) else ("00" + str(int(cod)))[-3:], na_action='ignore')

        # Generate 'Codigo Centro' column from the first four digits of 'Codigo Centro' column
        cen_compromisos_df['COD DEP'] = cen_compromisos_df['Codigo Centro'].map(lambda cod: str(cod)[:4],
                                                                                na_action='ignore')

        # Read Regiones y Proyectos file reference
        regiones_centros_df = regionales_proyectos_manager.read_regionales_centros_data()
        # Merge cen_compromisos_df and regiones_centros_df Dataframes for check 'REGIONAL','NOMBRE DEPENDENCIA' Columns orthography
        cen_compromisos_df[['N. REGIONAL', 'N. DEPENDENCIA']] = pd.merge(cen_compromisos_df[['C. REGIONAL', 'COD DEP']],
                                                                         regiones_centros_df, how='left',
                                                                         left_on=['C. REGIONAL', 'COD DEP'],
                                                                         right_on=['COD REG.1', 'COD DEP.'])[
            ['REGIONAL', 'NOMBRE DEPENDENCIA']]

        # Read Proyetos list
        proyectos_df = regionales_proyectos_manager.read_proyectos_data()
        # Get Project name from NaN codes from proyectos_df Dataframe
        nan_code_project = proyectos_df.loc[proyectos_df['COD. PROYECTO'].isnull()].PROYECTOS.values.any()
        # Get the upper year found in columns Nombre Rubro Presupuestal *year*
        columnname_codigo_decreto_ley = Utils.get_columnname_by_upper_year('Código Decreto Ley {}', cen_compromisos_df.columns)
        # Generate 'Proyecto' Column from 'CODIGO DECRETO LEY 2020' Column where mached, for nan values set nan_code_project value by default
        cen_compromisos_proyectos_df = pd.merge(cen_compromisos_df[columnname_codigo_decreto_ley], proyectos_df,
                                                  how='left', left_on=[columnname_codigo_decreto_ley],
                                                  right_on=['COD. PROYECTO'])
        cen_compromisos_proyectos_df.loc[cen_compromisos_proyectos_df[columnname_codigo_decreto_ley].str.contains('A-', na=False), 'PROYECTOS'] = nan_code_project
        cen_compromisos_df['PROYECTO'] = cen_compromisos_proyectos_df['PROYECTOS']

        # Get the upper year found in columns Nombre Rubro Presupuestal *year*
        columnname_nombre_rublo = Utils.get_columnname_by_upper_year('Nombre Rubro Presupuestal {}', cen_compromisos_df.columns)
        # Read Concepto interno GPO list
        concepto_interno_df = regionales_proyectos_manager.read_concepto_interno_gpo_data()
        concepto_interno_df['CONCEPTOS INTERNOS SENA APERTURA'] = concepto_interno_df[
            'CONCEPTOS INTERNOS SENA APERTURA'].fillna(concepto_interno_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Update 'NOMBRE CONCEPTO INTERNO SENA' Column from concepto interno df Dataframe for check orthography
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by adjusting on concept_interno_df
        conceptos_adjust_df = pd.merge(cen_compromisos_df[columnname_nombre_rublo].str.strip(), concepto_interno_df,
                                       how='left', left_on=[columnname_nombre_rublo],
                                       right_on=['CONCEPTOS INTERNOS SENA APERTURA'])
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
        conceptos_ok_spelling_df = pd.merge(cen_compromisos_df[columnname_nombre_rublo].str.strip(), concepto_interno_df, 
                                            how='left', left_on=[columnname_nombre_rublo],
                                            right_on=['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
        conceptos_internos_df = conceptos_adjust_df[columnname_nombre_rublo].fillna(
            conceptos_ok_spelling_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        cen_compromisos_df['CONCEPTO INTERNO SENA GPO'] = conceptos_internos_df

        # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
        cen_compromisos_df['Valor obligado'] = cen_compromisos_df['Valor Actual'] - cen_compromisos_df['Saldo por Obligar']

        # Validate standardize columns
        # Check 'REGIONAL' and 'NOMBRE DEPENDENCIA' with NaN values from 'COD REG' and 'COD DEP'
        if cen_compromisos_df.loc[cen_compromisos_df['N. REGIONAL'].isnull()].size > 0:
            invalid_reg_dep_df = cen_compromisos_df[['Fila', 'Cod Regional', 'COD DEP', 'Nombre Regional', 'Nombre Centro']].loc[
                    cen_compromisos_df['N. REGIONAL'].isnull()]
            invalid_reg_dep_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_REG_DEP + FILENAME_TEMP_CC, index=False)
        # Check 'PROYECTO'  with NaN values from 'CODIGO DECRETO LEY'
        if cen_compromisos_df.loc[cen_compromisos_df['PROYECTO'].isnull()].size > 0:
            invalid_proyecto_df = cen_compromisos_df[['Fila', columnname_codigo_decreto_ley, 'PROYECTO']].loc[
                cen_compromisos_df['PROYECTO'].isnull()]
            invalid_proyecto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_PROYECTOS + FILENAME_TEMP_CC, index=False)
        # Check 'CONCEPTO INTERNO SENA GPO' 
        if cen_compromisos_df.loc[cen_compromisos_df['CONCEPTO INTERNO SENA GPO'].isnull()].size > 0:
            invalid_concepto_df = cen_compromisos_df[['Fila', columnname_nombre_rublo, 'CONCEPTO INTERNO SENA GPO']].loc[
                    cen_compromisos_df['CONCEPTO INTERNO SENA GPO'].isnull()]
            invalid_concepto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_CONCEPTOS + FILENAME_TEMP_CC, index=False)

        # Save standardized Cen de Compromisos File
        cen_compromisos_df.to_excel(self.root_source_folder + FOLDERNAME_STANDARDIZE_FILES + FILENAME_TEMP_CC, index=False)

        # return True indicating good execution
        print("Result: Successful")
        return "Successful"

    def build_llaves(self):
        """Build LLAVES Cen de Compromisos

        Return 'Successful' if process finished OK

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        print("Build CEN de Compromisos LLAVES")
        # Read standardized cen_compromisos
        cen_compromisos_df = pd.read_excel(
            self.root_source_folder + FOLDERNAME_STANDARDIZE_FILES + FILENAME_TEMP_CC, 0,
            converters={'C. REGIONAL': str, 'Código Dependencia Gasto': str,
                        'Posicion del Gasto': str, 'REC': str}, na_values=['NA'])

        # Define if exist the nan values ​​in columns required for build KEYS
        invalid_llaves_df = cen_compromisos_df.loc[
            cen_compromisos_df['C. REGIONAL'].isnull() | cen_compromisos_df['Código Dependencia Gasto'].isnull() |
            cen_compromisos_df['Posicion del Gasto'].isnull() | cen_compromisos_df['REC'].isnull() | cen_compromisos_df[
                'CONCEPTO INTERNO SENA GPO'].isnull()][
            ['Fila', 'C. REGIONAL', 'Código Dependencia Gasto', 'Posicion del Gasto', 'REC', 'CONCEPTO INTERNO SENA GPO']]
        invalid_llaves_df.to_excel(
            self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_LLAVES + FILENAME_TEMP_CC, index=False)

        # Drop invalid values for create LLAVES
        cen_compromisos_df = cen_compromisos_df.dropna(
            subset=['C. REGIONAL', 'Código Dependencia Gasto', 'Posicion del Gasto', 'REC',
                    'CONCEPTO INTERNO SENA GPO'])

        # Generate 'LLAVE' Column concatenating 'C. REGIONAL', 'Código Dependencia Gasto', 'Posicion del Gasto', 'REC' y 'CONCEPTO INTERNO SENA GPO'
        cen_compromisos_df['LLAVE'] = cen_compromisos_df['C. REGIONAL'] + cen_compromisos_df[
            'Código Dependencia Gasto'] + \
                                        cen_compromisos_df['Posicion del Gasto'] + cen_compromisos_df['REC'] + \
                                        cen_compromisos_df[
                                            'CONCEPTO INTERNO SENA GPO']

        print(cen_compromisos_df[
                    ['LLAVE', 'C. REGIONAL', 'Código Dependencia Gasto', 'Posicion del Gasto', 'REC',
                    'CONCEPTO INTERNO SENA GPO']])

        # Return build file
        return cen_compromisos_df
        

if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    cc_filename = "CEN COMPROMISOS CONS NAL A 30 SEPT 2020_CIERRE_01102020 - Homologado.xlsb"
    sheet_name_cc = 'CEN COMPR CONSNAL A 30SEPT20_C '
    year = 2018
    cc_manager = CenCompromisosManager(root_source_folder, year)
    standardize_file_result = cc_manager.standardize_file(cc_filename, sheet_name_cc)
    print(standardize_file_result)
