import pandas as pd
import openpyxl 

class XlsxExport:
    """
    Handles the export of analytical results to multi-sheet Excel workbooks.
    """

    def save(self, data: pd.Series, file_path: str) -> tuple[bool, str]:
        """
        Exports the dataset to Excel, splitting views into Percentage and Absolute Revenue sheets.

        This method automatically handles Excel constraints (such as 31-character 
        sheet name limits) and prepares data for specific chart types.

        Args:
            data (pd.Series): The data to export. The Series name is used for sheet naming.
            file_path (str): The destination path for the .xlsx file.

        Returns:
            tuple[bool, str]: A tuple containing:
                - Success flag (True/False)
                - Status message or error description
        """
        try:
            base_name = str(data.name) if data.name else "Data"
            
            total = data.sum()
            
            if total != 0:
                df_pie = ((data / total) * 100).round(1).to_frame(name="Percentage")
            else:
                df_pie = data.to_frame(name="Percentage")
            
            df_bar = data.to_frame(name="Revenue")
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Excel restricts sheet names to 31 characters
                sheet_name_pie = f"{base_name} Pie"[:31]
                sheet_name_bar = f"{base_name} Bar"[:31]
                
                df_pie.to_excel(writer, sheet_name=sheet_name_pie)
                df_bar.to_excel(writer, sheet_name=sheet_name_bar)
                
            return True, "File saved successfully."
            
        except Exception as e:
            return False, str(e)