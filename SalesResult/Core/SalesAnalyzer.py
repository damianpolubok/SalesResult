import pandas as pd

class SalesAnalyzer:
    """
    Provides financial aggregation metrics across product and demographic dimensions.
    """

    def get_category_share(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculates total revenue distribution per product category.

        Args:
            df (pd.DataFrame): Sales data containing 'Product_Category' and 'Revenue'.

        Returns:
            pd.Series: Revenue sum indexed by category name.
        """
        return df.groupby('Product_Category')['Revenue'].sum()

    def get_country_share(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculates total revenue distribution per country.

        Args:
            df (pd.DataFrame): Sales data containing 'Country' and 'Revenue'.

        Returns:
            pd.Series: Revenue sum indexed by country name.
        """
        return df.groupby('Country')['Revenue'].sum()

    def get_age_group_share(self, df: pd.DataFrame) -> pd.Series:
        """
        Aggregates revenue by standard demographic age buckets.
        
        Buckets defined as: <25, 25-35, 35-45, 45-55, 55+.

        Args:
            df (pd.DataFrame): Sales data containing 'Revenue'. 'Customer_Age' is optional.

        Returns:
            pd.Series: Revenue sum indexed by age group. Returns an empty Series 
                       if 'Customer_Age' column is missing.
        """
        if 'Customer_Age' not in df.columns:
            return pd.Series()

        df_temp = df.copy()
        bins = [0, 25, 35, 45, 55, 100]
        labels = ['<25', '25-35', '35-45', '45-55', '55+']
        
        df_temp['Age_Group_Calc'] = pd.cut(df_temp['Customer_Age'], bins=bins, labels=labels)

        return df_temp.groupby('Age_Group_Calc', observed=True)['Revenue'].sum()

    def calculate_total_revenue(self, df: pd.DataFrame) -> float:
        """
        Computes the grand total revenue for the provided dataset.

        Args:
            df (pd.DataFrame): Sales data containing a numeric 'Revenue' column.

        Returns:
            float: The sum of all revenue entries.
        """
        return df['Revenue'].sum()