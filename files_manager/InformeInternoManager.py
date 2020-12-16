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


class InformeInternoManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder

    def build_informe(self, cr_llaves_df, cc_llaves_df, apertura_llaves_df):
        print("Build Informe")

        # For Apertura Dataframe define the 'Presupuesto' sum by each Llaves Group and assign to informe interno DataFrame
        columnname_presupuesto = Utils.get_columnname_by_upper_year('Presupuesto {}', apertura_llaves_df.columns)
        apertura_presupuesto_df = apertura_llaves_df[['LLAVE', columnname_presupuesto]].groupby(
            ['LLAVE']).sum().reset_index()
        print(apertura_presupuesto_df)

        # For Consolidado Resoluciones Dataframe define the 'Adición' and 'Disminución' sum by each Llaves Group and assign to informe interno DataFrame
        cr_add_dism_df = cr_llaves_df[['LLAVE', 'ASIGNACION', 'DISMINUCION']].groupby(['LLAVE']).agg(
            {'DISMINUCION': 'sum', 'ASIGNACION': 'sum'}).reset_index()
        print(cr_add_dism_df)

        # For Cen Compromisos Dataframe define the 'Valor Actual' and 'Valor obligado' sum by each Llaves Group and assign to informe interno DataFrame
        cc_valor_df = cc_llaves_df[['LLAVE', 'Valor Actual', 'Valor obligado']].groupby(['LLAVE']).agg(
            {'Valor Actual': 'sum', 'Valor obligado': 'sum'}).reset_index()
        print(cc_valor_df)

        # Merger all DataFrames by LLAVE apertura_presupuesto_df, cr_add_dism_df and cc_valor_df
        apertura_cr_merge_df = pd.merge(apertura_presupuesto_df, cr_add_dism_df, how='outer', left_on='LLAVE',
                                        right_on='LLAVE')
        cc_apertura_cr_merge_df = pd.merge(apertura_cr_merge_df, cc_valor_df, how='outer', left_on='LLAVE',
                                           right_on='LLAVE')
        print(cc_apertura_cr_merge_df)

        # Create the pandas DataFrame
        informe_interno_df = cc_apertura_cr_merge_df.rename(
            columns={columnname_presupuesto: 'ASIGNACIÓN', 'ASIGNACION': 'ADICIÓN', 'DISMINUCION': 'DISMINUCIÓN',
                     'Valor Actual': 'COMPROMISO', 'Valor obligado': 'OBLIGADO'})
        print(informe_interno_df)
        # New column 'VIGENTE' equal 'ASIGNACIÓN' + 'ADICIÓN' - 'DISMINUCIÓN'
        informe_interno_df['VIGENTE'] = informe_interno_df['ASIGNACIÓN'] + informe_interno_df['ADICIÓN'] - \
                                        informe_interno_df['DISMINUCIÓN']
        # New column 'DISPONIBLE' equal 'VIGENTE'- 'COMPROMISO'
        informe_interno_df['DISPONIBLE'] = informe_interno_df['VIGENTE'] - informe_interno_df['COMPROMISO']

        # Merge Dataframes for find remaining columns {COD. REG, COD. DEP, NOMBRE DEPENDENCIA, etc...}
        # Define the 'TABLA' column by each Dataframe
        cr_llaves_df['TABLA'] = 'DIN CR'  # COLUMNAS TIENEN MES Y NO MESES IGUALES
        cc_llaves_df['TABLA'] = 'DIN CC'  # COLUMNAS TIENEN MES Y NO MESES IGUALES
        apertura_llaves_df['TABLA'] = 'DIN APERTURA'

        # Merge informe_interno_df with apertura_llaves_df for find remaining columns
        informe_interno_df = pd.merge(informe_interno_df, apertura_llaves_df[
            ['LLAVE', 'TABLA', 'C. REGIONAL', 'N. REGIONAL', 'COD DEP', 'N. DEPENDENCIA', 'POSICION DEL GASTO', 'PROYECTO',
             'CONCEPTO INTERNO SENA GPO', 'DEPE SIIF']], how='left', left_on=['LLAVE'], right_on=['LLAVE'])

        informe_interno_df.fillna(value=values)

        print(informe_interno_df)

        # return Successful indicating good execution
        return "Successful"


if __name__ == "__main__":
    pass
