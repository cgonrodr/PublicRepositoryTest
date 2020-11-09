"""
* Autor: Cesar M. Gonzalez R.
 * Company: Everis
 * CreateAt: 16/04/20
 * Formatter XL
 """
import openpyxl


class FormatterXL:

    def __init__(self):
        pass

    def format_informe(self):
        try:
            print("format_informe")
            # Give the location of the file
            file_path = "C:\\Users\\cgonrodr\\Documents\\PruebaPythonExcel\\Templates\\"
            informe_temp_filename = "InformeTemplate.xlsx"
            informe_filename = "Informe.xlsx"

            # to open the workbook
            # workbook object is created
            wb_obj = openpyxl.load_workbook(file_path + informe_temp_filename)
            print(wb_obj)
            sheet_obj = wb_obj.active
            wb_obj.save(file_path + informe_filename)

            # return True indicating good execution
            return "Successful"
        except ValueError:
            print(ValueError)
            return ValueError


if __name__ == "__main__":
    formatter_xl = FormatterXL()
    formatter_xl.format_informe()
    pass
