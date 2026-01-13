import pandas as pd

class CsvImport:
    """
    Handles data ingestion from CSV sources with robust format detection.
    """

    def load(self, path: str) -> pd.DataFrame:
        """
        Loads a CSV file into a pandas DataFrame.

        This method uses the Python parsing engine to automatically infer the 
        field separator (e.g., comma, semicolon, tab) based on the file content.

        Args:
            path (str): The absolute or relative file path to the CSV dataset.

        Returns:
            pd.DataFrame: A DataFrame containing the loaded data.
        
        Raises:
            FileNotFoundError: If the provided path does not exist.
            pd.errors.ParserError: If the file content cannot be parsed.
        """
        return pd.read_csv(path, sep=None, engine='python')