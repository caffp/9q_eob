import pandas as pd
import numpy as np
import io
from typing import Tuple, Optional

def read_excel_file(file) -> Tuple[Optional[pd.DataFrame], str]:
    """Read Excel file and return DataFrame with error handling."""
    try:
        df = pd.read_excel(file)
        if df.empty:
            return None, "The uploaded file is empty."
        return df, "Success"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def filter_dataframe(df: pd.DataFrame, selected_columns: list, start_row: int, end_row: int) -> pd.DataFrame:
    """Filter dataframe based on selected columns and row range."""
    if not selected_columns:
        return df.iloc[start_row:end_row+1]
    return df.loc[start_row:end_row, selected_columns]

def group_by_depot(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by Depot column and calculate specific metrics."""
    if 'Depot' not in df.columns:
        raise ValueError("Depot column not found in the dataset")
    
    required_cols = ['DeliveryCases', 'OnTimePct']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    
    grouped = df.groupby('Depot').agg({
        'DeliveryCases': 'sum',
        'Depot': 'count',
        'OnTimePct': 'mean'
    }).reset_index()
    
    # Rename columns
    grouped.columns = ['Depot', 'Delivery_Cases', 'Routes', 'On_Time_Pct']
    
    # Round On-Time percentage to nearest integer
    grouped['On_Time_Pct'] = grouped['On_Time_Pct'].round().astype(int)
    
    # Add Delivery Hours (assuming it's a direct value from the dataframe)
    if 'DeliveryHours' in df.columns:
        delivery_hours = df.groupby('Depot')['DeliveryHours'].sum().reset_index()
        grouped = grouped.merge(delivery_hours, on='Depot', how='left')
        grouped.rename(columns={'DeliveryHours': 'Delivery_Hours'}, inplace=True)
    
    return grouped

def pivot_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transpose the dataframe and reset index."""
    pivoted_df = df.transpose().reset_index()
    pivoted_df.columns = ['Field'] + [f'Value_{i+1}' for i in range(len(pivoted_df.columns)-1)]
    return pivoted_df

def filter_metrics(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Filter metrics based on specified thresholds."""
    filtered_df = df.copy()
    
    for column, threshold in filters.items():
        if column in df.columns:
            if isinstance(threshold, dict):
                if 'min' in threshold:
                    filtered_df = filtered_df[filtered_df[column] >= threshold['min']]
                if 'max' in threshold:
                    filtered_df = filtered_df[filtered_df[column] <= threshold['max']]
            else:
                filtered_df = filtered_df[filtered_df[column] >= threshold]
    
    return filtered_df

def generate_download_link(df: pd.DataFrame, file_format: str) -> Tuple[bytes, str]:
    """Generate downloadable file in specified format."""
    if file_format == "csv":
        output = df.to_csv(index=False)
        return output.encode(), "text/csv"
    elif file_format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        raise ValueError("Unsupported file format")