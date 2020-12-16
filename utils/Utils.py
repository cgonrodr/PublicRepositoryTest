"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 15/12/20
 * Utils File
 """

import datetime

class Utils:

    @staticmethod
    def get_columnname_by_upper_year(base_columnname, columns_names):
        """Get column name with the upper year

        Return Column name

        Parameters
        ----------
        base_columnname : string
            base column name
        columns_names : list string
            columns names list

        Raises
        ------
        ValueError
            If some error exist, then return Error Message.
        """
        upper_column_year = datetime.datetime.now().year
        while base_columnname.format(upper_column_year) not in columns_names and datetime.datetime.now().year - 5 < upper_column_year:
            upper_column_year -= 1
        return base_columnname.format(upper_column_year) 

    
