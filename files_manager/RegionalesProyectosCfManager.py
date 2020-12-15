"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Apertura File Manager
 """

import pandas as pd
from utils.Constants import FILENAME_REGIONES_PROYECTOS_CONCEPTOS, TABNAME_PROYECTO_REGIONES_PROYECTOS_CONCEPTOS, \
    TABNAME_REGIONAL_CENTROS_REGIONES_PROYECTOS_CONCEPTOS, TABNAME_CONCEPTO_INTERNO_REGIONES_PROYECTOS_CONCEPTOS


class RegionalesProyectosCfManager:

    def __init__(self, root_source_folder):
        self.root_source_folder = root_source_folder

    def read_proyectos_data(self):
        """Read Proyectos from Nombre Regionales y CF - Proyectos - Concepto Interno - GPO file

        Return DataFrame with the SENA projects 

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """

        print("Read Proyectos")
        # Read Proyectos Data
        return pd.read_excel(self.root_source_folder + FILENAME_REGIONES_PROYECTOS_CONCEPTOS,
                             TABNAME_PROYECTO_REGIONES_PROYECTOS_CONCEPTOS,
                             usecols='B:C', skiprows=[0, 1], index_col=None, na_values=['NA'])

    def read_regionales_centros_data(self):
        """Read Regionales y Centros from Nombre Regionales y CF - Proyectos - Concepto Interno - GPO file

        Return DataFrame with the SENA Regionales y Centros 

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """

        print("Read Regionales Centros")
        # Read Regiones y Proyectos file reference
        return pd.read_excel(self.root_source_folder + FILENAME_REGIONES_PROYECTOS_CONCEPTOS,
                             TABNAME_REGIONAL_CENTROS_REGIONES_PROYECTOS_CONCEPTOS, usecols='B:F', skiprows=[0, 1],
                             index_col=None, na_values=['NA'], converters={'COD REG.1': str, 'COD DEP.': str})

    def read_concepto_interno_gpo_data(self):
        """Read Concepto Interno GPO from Nombre Regionales y CF - Proyectos - Concepto Interno - GPO file

        Return DataFrame with the SENA Regionales y Centros 

        Parameters
        ----------

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """

        print("Read Concepto Interno GPO")
        # Read Concepto interno GPO list
        return pd.read_excel(self.root_source_folder + FILENAME_REGIONES_PROYECTOS_CONCEPTOS,
                             TABNAME_CONCEPTO_INTERNO_REGIONES_PROYECTOS_CONCEPTOS, usecols='C,E', skiprows=[0],
                             index_col=None, na_values=['NA'])