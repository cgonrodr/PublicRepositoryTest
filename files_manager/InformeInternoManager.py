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
from utils.Utils import Utils
from utils.Constants import FOLDERNAME_FINAL_FILES, FILENAME_FINAL_INFORME_INTERNO
from openpyxl import load_workbook


class InformeInternoManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder

    def build_informe(self, cr_llaves_df, cc_llaves_df, apertura_llaves_df):
        print("Build Informe")

        # Add 'TABLA' Column indicating were data come from
        # Define the 'TABLA' column by each Dataframe
        cr_llaves_df['TABLA'] = 'DIN CR'                                # COLUMNAS TIENEN MES Y NO MESES IGUALES
        cc_llaves_df['TABLA'] = 'DIN CC'                                # COLUMNAS TIENEN MES Y NO MESES IGUALES
        apertura_llaves_df['TABLA'] = 'DIN APERTURA'

        # For Apertura Dataframe define the 'Presupuesto' sum by each Llaves Group and assign to informe interno DataFrame
        columnname_presupuesto = Utils.get_columnname_by_upper_year('Presupuesto {}', apertura_llaves_df.columns)
        apertura_merge_df = apertura_llaves_df[
            ['LLAVE', columnname_presupuesto, 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA',
             'POSICION DEL GASTO', 'PROYECTO', 'CONCEPTO INTERNO SENA GPO']].groupby(
            ['LLAVE']).agg(
            {columnname_presupuesto: 'sum', 'TABLA': 'first', 'C. REGIONAL': 'first', 'N. REGIONAL': 'first', 'COD DEP': 'first',
             'N. DEPENDENCIA': 'first', 'POSICION DEL GASTO': 'first', 'PROYECTO': 'first', 'CONCEPTO INTERNO SENA GPO': 'first'}).reset_index()

        # For Consolidado Resoluciones Dataframe define the 'Adición' and 'Disminución' sum by each Llaves Group and assign to informe interno DataFrame
        cr_merge_df = cr_llaves_df[
            ['LLAVE', 'ASIGNACION', 'DISMINUCION', 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA',
             'POSICION CATALOGO DEL GASTO', 'PROYECTO', 'CONCEPTO INTERNO SENA GPO']].groupby(['LLAVE']).agg(
            {'DISMINUCION': 'sum', 'ASIGNACION': 'sum', 'TABLA': 'first',  'C. REGIONAL': 'first', 'N. REGIONAL': 'first',
             'COD DEP': 'first', 'N. DEPENDENCIA': 'first', 'POSICION CATALOGO DEL GASTO': 'first',
             'PROYECTO': 'first', 'CONCEPTO INTERNO SENA GPO': 'first'}).reset_index()
        cr_merge_df = cr_merge_df.rename(columns={'POSICION CATALOGO DEL GASTO': 'POSICION DEL GASTO'})

        # For Cen Compromisos Dataframe define the 'Valor Actual' and 'Valor obligado' sum by each Llaves Group and assign to informe interno DataFrame
        cc_merge_df = cc_llaves_df[
            ['LLAVE', 'Valor Actual', 'Valor obligado', 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA',
             'Posicion del Gasto', 'PROYECTO', 'CONCEPTO INTERNO SENA GPO']].groupby(['LLAVE']).agg(
            {'Valor Actual': 'sum', 'Valor obligado': 'sum', 'TABLA': 'first', 'C. REGIONAL': 'first', 'N. REGIONAL': 'first',
             'COD DEP': 'first', 'N. DEPENDENCIA': 'first', 'Posicion del Gasto': 'first',
             'PROYECTO': 'first', 'CONCEPTO INTERNO SENA GPO': 'first'}).reset_index()
        cc_merge_df = cc_merge_df.rename(columns={'Posicion del Gasto': 'POSICION DEL GASTO'})

        # Merger all DataFrames by LLAVE; apertura_merge_df, cr_merge_df and cc_merge_df
        apertura_cr_merge_df = pd.merge(apertura_merge_df, cr_merge_df[['LLAVE', 'DISMINUCION', 'ASIGNACION']],
                                        how='outer', left_on='LLAVE',
                                        right_on='LLAVE')
        cc_apertura_cr_merge_df = pd.merge(apertura_cr_merge_df,
                                           cc_merge_df[['LLAVE', 'Valor Actual', 'Valor obligado']], how='outer',
                                           left_on='LLAVE',
                                           right_on='LLAVE')

        # Get complete first informe Dataframe secction defined by Apertura merge
        apertura_informe_df = cc_apertura_cr_merge_df.loc[
            ~cc_apertura_cr_merge_df['C. REGIONAL'].isnull() & ~cc_apertura_cr_merge_df['COD DEP'].isnull()]

        # Define remaining rows without 'C.REGIONAL' and 'COD DEP' defined
        remaning_nan_rows_df = cc_apertura_cr_merge_df.loc[
            cc_apertura_cr_merge_df['C. REGIONAL'].isnull() & cc_apertura_cr_merge_df['COD DEP'].isnull()]

        # Define remaining rows without 'C.REGIONAL' and 'COD DEP' defined result of remaning_nan_rows_df and cr_merge_df merge
        remaning_nan_cr_merge_df = pd.merge(remaning_nan_rows_df[
                                                ['LLAVE', 'Presupuesto 2020', 'DISMINUCION', 'ASIGNACION',
                                                 'Valor Actual', 'Valor obligado']], cr_merge_df[
                                                ['LLAVE', 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA',
                                                 'POSICION DEL GASTO', 'PROYECTO', 'CONCEPTO INTERNO SENA GPO']],
                                                how='left', left_on='LLAVE', right_on='LLAVE')

        # Get complete second informe Dataframe secction defined by Consolidado Resoluciones merge
        cr_informe_df = remaning_nan_cr_merge_df.loc[
            ~remaning_nan_cr_merge_df['C. REGIONAL'].isnull() & ~remaning_nan_cr_merge_df['COD DEP'].isnull()]

        # Define remaining rows without 'C.REGIONAL' and 'COD DEP' defined
        remaning_nan_rows_df = remaning_nan_cr_merge_df.loc[
            remaning_nan_cr_merge_df['C. REGIONAL'].isnull() & remaning_nan_cr_merge_df['COD DEP'].isnull()]

        # Get complete third informe Dataframe secction defined by Cen de Compromisos merge
        cc_informe_df = pd.merge(remaning_nan_rows_df[
                                     ['LLAVE', 'Presupuesto 2020', 'DISMINUCION', 'ASIGNACION', 'Valor Actual',
                                      'Valor obligado']], cc_merge_df[
                                     ['LLAVE', 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA',
                                      'POSICION DEL GASTO', 'PROYECTO', 'CONCEPTO INTERNO SENA GPO']],
                                     how='left', left_on='LLAVE', right_on='LLAVE')

        # Merge all informes Dataframe Sections
        informe_interno_df = apertura_informe_df.append(cr_informe_df).append(cc_informe_df)

        # Rename columns informe
        informe_interno_df = informe_interno_df.rename(
            columns={columnname_presupuesto: 'ASIGNACIÓN', 'ASIGNACION': 'ADICIÓN', 'DISMINUCION': 'DISMINUCIÓN',
                     'Valor Actual': 'COMPROMISO', 'Valor obligado': 'OBLIGADO'})

        # New column 'VIGENTE' equal 'ASIGNACIÓN' + 'ADICIÓN' - 'DISMINUCIÓN'
        informe_interno_df['VIGENTE'] = informe_interno_df['ASIGNACIÓN'] + informe_interno_df['ADICIÓN'] - \
                                        informe_interno_df['DISMINUCIÓN']

        # New column 'DISPONIBLE' equal 'VIGENTE'- 'COMPROMISO'
        informe_interno_df['DISPONIBLE'] = informe_interno_df['VIGENTE'] - informe_interno_df['COMPROMISO']

        # Order Dataframe Columns for write in Informe Interno File
        informe_interno_df = informe_interno_df[
            ['LLAVE', 'ASIGNACIÓN', 'ADICIÓN', 'DISMINUCIÓN', 'VIGENTE', 'COMPROMISO', 'DISPONIBLE', 'TABLA',
             'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA', 'POSICION DEL GASTO', 'PROYECTO',
             'CONCEPTO INTERNO SENA GPO']]

        # Read Informes Internos Template
        book = load_workbook(self.root_source_folder + FOLDERNAME_FINAL_FILES + FILENAME_FINAL_INFORME_INTERNO)
        writer = pd.ExcelWriter(self.root_source_folder + FOLDERNAME_FINAL_FILES + FILENAME_FINAL_INFORME_INTERNO, engine='openpyxl')
        writer.book = book

        # Write Informes Conceptos Internos final File
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        informe_interno_df.to_excel(writer, "INFORME", index = False, header = False, na_rep = '-', startrow = 7)
        writer.save()

        print(informe_interno_df)

        # return Successful indicating good execution
        return "Successful"


if __name__ == "__main__":
    pass
