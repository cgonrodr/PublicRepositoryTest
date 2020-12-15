"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Apertura File Manager
 """

import pandas as pd
from utils.Constants import FILENAME_TEMP_APERTURA, FOLDERNAME_TEMP, FILENAME_REGIONES_PROYECTOS_CONCEPTOS, \
    FILENAME_INVALID_REG_DEP, FILENAME_INVALID_PROYECTOS, FILENAME_INVALID_CONCEPTOS, FILENAME_INVALID_LLAVES, \
    FOLDERNAME_FAIL_FILES
from files_manager.RegionalesProyectosCfManager import RegionalesProyectosCfManager


class AperturaManager:

    def __init__(self, root_source_folder, current_year):
        self.root_source_folder = root_source_folder
        self.current_year = current_year

    def standardize_file(self, apertura_filename):
        """Standasdize File Apertura

        Return 'Successful' if process finished OK

        Parameters
        ----------
        apertura_filename : string
            apertura file name

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        print("Standardize Apertura File")
        # Open Regionales Proyectos File manager for read strandarize data
        regionales_proyectos_manager = RegionalesProyectosCfManager(self.root_source_folder)

        # Read File Apertura File
        apertura_df = pd.read_excel(self.root_source_folder + apertura_filename,
                                    'APERTURA FUNC-GASTOS {}'.format(str(self.current_year)), index_col=None,
                                    converters={'COD REG': str, 'SUB UNID': str, 'COD SUB': str,
                                                'COD DEP SIIF': str, 'FUENTE RECUR': str,
                                                'SITUACIÓN DE FONDOS': str, 'TIPO DOC (RES)': str,
                                                'No. RESOL': str}, skiprows=[0, 1, 2], na_values=['NA'])

        # Add Column number
        apertura_df['Fila'] = apertura_df.index + 5

        # Update 'Cod Regional' column validate ; 00X format
        apertura_df['C. REGIONAL'] = apertura_df['COD REG'].map(
            lambda cod: cod if "-" in str(cod) else ("00" + str(int(cod)))[-3:], na_action='ignore')

        # Generate 'COD DEP' column from the first four digits of 'DEPE SIIF' column
        apertura_df['COD DEP'] = apertura_df['DEPE SIIF'].map(lambda cod: str(cod)[:4], na_action='ignore')

        # Read Regiones y Proyectos file reference
        regiones_centros_df = regionales_proyectos_manager.read_regionales_centros_data()
        # Merge apertura_df and regiones_centros_df Dataframes for check 'REGIONAL','NOMBRE DEPENDENCIA' Columns orthography
        apertura_df[['N. REGIONAL', 'N. DEPENDENCIA']] = pd.merge(apertura_df[['C. REGIONAL', 'COD DEP']],
                                                                  regiones_centros_df, how='left',
                                                                  left_on=['C. REGIONAL', 'COD DEP'],
                                                                  right_on=['COD REG.1', 'COD DEP.'])[
            ['REGIONAL', 'NOMBRE DEPENDENCIA']]

        # Read Proyetos list
        proyectos_df = regionales_proyectos_manager.read_proyectos_data()
        # Get Project name from NaN codes from proyectos_df Dataframe
        nan_code_project = proyectos_df.loc[proyectos_df['COD. PROYECTO'].isnull()].PROYECTOS.values.any()
        # Get the upper year found in columns RUBRO LEY SIIF_year
        upper_column_year = self.current_year
        while 'RUBRO LEY SIIF_{}'.format(upper_column_year) not in apertura_df.columns and self.current_year - 5 < upper_column_year:
            upper_column_year -= 1
        columnname_rublo_ley = 'RUBRO LEY SIIF_{}'.format(upper_column_year)
        # Generate 'Proyecto' Column from 'CODIGO DECRETO LEY 2020' Column where mached, for nan values set nan_code_project value by default
        apertura_df['PROYECTO'] = pd.merge(apertura_df[columnname_rublo_ley], proyectos_df, how='left', left_on=[columnname_rublo_ley],
                                           right_on=['COD. PROYECTO']).PROYECTOS.fillna(nan_code_project)

        # Read Concepto interno GPO list
        concepto_interno_df = regionales_proyectos_manager.read_concepto_interno_gpo_data()
        concepto_interno_df['CONCEPTOS INTERNOS SENA APERTURA'] = concepto_interno_df[
            'CONCEPTOS INTERNOS SENA APERTURA'].fillna(concepto_interno_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Update 'NOMBRE CONCEPTO INTERNO SENA' Column from concepto interno df Dataframe for check orthography
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by adjusting on concept_interno_df
        conceptos_adjust_df = pd.merge(apertura_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(), concepto_interno_df,
                                       how='left', left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                       right_on=['CONCEPTOS INTERNOS SENA APERTURA'])
        # Check the spelling of the column 'SENA INTERNAL CONCEPT NAME' of the file by finding on concept_interno_df
        conceptos_ok_spelling_df = pd.merge(apertura_df['NOMBRE CONCEPTO INTERNO SENA'].str.strip(),
                                            concepto_interno_df, how='left', left_on=['NOMBRE CONCEPTO INTERNO SENA'],
                                            right_on=['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        # Generate 'Valor Obligado' Column from the difference between 'Valor Actual' and 'Saldo por Obligar' Columns
        cen_compromisos_df = conceptos_adjust_df['CONCEPTOS INTERNOS SENA REPORTES GPO'].fillna(
            conceptos_ok_spelling_df['CONCEPTOS INTERNOS SENA REPORTES GPO'])
        apertura_df['CONCEPTO INTERNO SENA GPO'] = cen_compromisos_df

        # Validate standardize columns
        # Check 'REGIONAL' and 'NOMBRE DEPENDENCIA' with NaN values from 'COD REG' and 'COD DEP'
        if apertura_df.loc[apertura_df['N. REGIONAL'].isnull()].size > 0:
            invalid_reg_dep_df = apertura_df[['Fila', 'COD REG', 'COD DEP', 'REGIONAL', 'NOMBRE DEPENDENCIA']].loc[
                apertura_df['N. REGIONAL'].isnull()]
            invalid_reg_dep_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_REG_DEP + FILENAME_TEMP_APERTURA, index=False)
        # Check 'PROYECTO'  with NaN values from 'CODIGO DECRETO LEY'
        if apertura_df.loc[apertura_df['PROYECTO'].isnull()].size > 0:
            invalid_proyecto_df = apertura_df[['Fila', columnname_rublo_ley, 'PROYECTO']].loc[
                apertura_df['PROYECTO'].isnull()]
            invalid_proyecto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_PROYECTOS + FILENAME_TEMP_APERTURA, index=False)
        # Check 'CONCEPTO INTERNO SENA GPO' 
        if apertura_df.loc[apertura_df['CONCEPTO INTERNO SENA GPO'].isnull()].size > 0:
            invalid_concepto_df = apertura_df[['Fila', 'NOMBRE CONCEPTO INTERNO SENA', 'CONCEPTO INTERNO SENA GPO']].loc[
                    apertura_df['CONCEPTO INTERNO SENA GPO'].isnull()]
            invalid_concepto_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_CONCEPTOS + FILENAME_TEMP_APERTURA, index=False)

        # Save standardized Apertura File
        apertura_df.to_excel(self.root_source_folder + FOLDERNAME_TEMP + FILENAME_TEMP_APERTURA, index=False)

        # return True indicating good execution
        print("Result: Successful")
        return "Successful"

    def build_llaves(self):
        """Build LLAVES Apertura

        Return 'Successful' if process finished OK

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        try:
            print("Build Apertura LLAVES")
            # Read standardized apertura_year
            apertura_df = pd.read_excel(self.root_source_folder + FOLDERNAME_TEMP + FILENAME_TEMP_APERTURA, 0,
                                        converters={'C. REGIONAL': str, 'COD DEP': str, 'COD SUB': str,
                                                    'SUB UNID': str, 'DEPE SIIF': str, 'POSICION DEL GASTO': str},
                                        na_values=['NA'])

            # Get the upper REC year Column
            upper_column_year = self.current_year
            while "REC {}".format(upper_column_year) not in apertura_df.columns and self.current_year - 5 < upper_year:
                upper_column_year -= 1
            columnname_rec = "REC {}".format(upper_column_year)

            # Define if exist the nan values ​​in columns required for build KEYS
            invalid_llaves_df = apertura_df.loc[
                apertura_df['C. REGIONAL'].isnull() | apertura_df['DEPE SIIF'].isnull() | apertura_df[
                    'POSICION DEL GASTO'].isnull() | apertura_df[columnname_rec].isnull() | apertura_df[
                    'CONCEPTO INTERNO SENA GPO'].isnull()][
                ['Fila', 'C. REGIONAL', 'DEPE SIIF', 'POSICION DEL GASTO', 'CONCEPTO INTERNO SENA GPO']]
            invalid_llaves_df.to_excel(
                self.root_source_folder + FOLDERNAME_FAIL_FILES + FILENAME_INVALID_LLAVES + FILENAME_TEMP_APERTURA, index=False)

            # Drop invalid values for create LLAVES
            apertura_df = apertura_df.dropna(
                subset=['C. REGIONAL', 'DEPE SIIF', 'POSICION DEL GASTO', columnname_rec, 'CONCEPTO INTERNO SENA GPO'])

            # Generate 'LLAVE' Column concatenating 'COD REG', 'DEPE SIIF', 'POSICION DEL GASTO', 'REC {year}' y 'CONCEPTO INTERNO SENA GPO'
            apertura_df['LLAVE'] = apertura_df['C. REGIONAL'] + apertura_df['DEPE SIIF'] + apertura_df[
                'POSICION DEL GASTO'] + \
                                   apertura_df[columnname_rec].astype(int).astype(str) + apertura_df[
                                       'CONCEPTO INTERNO SENA GPO']

            print(apertura_df[
                      ['LLAVE', 'C. REGIONAL', 'DEPE SIIF', 'POSICION DEL GASTO', columnname_rec,
                       'CONCEPTO INTERNO SENA GPO']])

            # Return Apertura DataFrame and LLAVES
            return apertura_df
        except ValueError:
            print(ValueError)
            return ValueError


if __name__ == "__main__":
    root_source_folder = 'C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\'
    # apertura_filename = "APERTURA FUNCIONAMIENTO-INVERSIÓN 2020.xlsx"
    # sheet_name_apertura = 'APERTURA FUNC-GASTOS 2020'
    # apertura_manager = AperturaManager(root_source_folder)
    # standardize_file_result = apertura_manager.standardize_file(apertura_filename, sheet_name_apertura)
    # print(standardize_file_result)

    apertura_manager = AperturaManager(root_source_folder)
    apertura_manager.build_llaves()
