"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 11/12/20
 * Informes Presupuestales ExeFile
 """

from InformesPresupuestalesFacade import InformesPresupuestalesFacade

def standardize_root_files(root_source_folder, apertura_filename, cr_filename, cc_filename):
    informes_presupuestales_facade = InformesPresupuestalesFacade(root_source_folder)
    return informes_presupuestales_facade.standardize_root_files(apertura_filename, cr_fsilename,cc_filename)
    
    
    