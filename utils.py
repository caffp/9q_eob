import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
import io

def read_excel_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
    """Read an Excel file and return a dataframe and status message."""
    try:
        df = pd.read_excel(uploaded_file)
        if df.empty:
            return None, "The uploaded file is empty."
        return df, "Success"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def filter_dataframe(
    df: pd.DataFrame,
    selected_columns: List[str],
    start_row: int,
    end_row: int
) -> pd.DataFrame:
    """Filter dataframe based on selected columns and rows."""
    if not selected_columns:
        return df.iloc[start_row:end_row+1]
    return df.loc[start_row:end_row, selected_columns]

def group_by_depot(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by Depot column and calculate aggregates."""
    if 'Depot' not in df.columns:
        raise ValueError("Depot column not found in the dataset")
    
    grouped = df.groupby('Depot').agg({
        'Route': 'count',
        'Mileage': 'sum',
        'Time': 'sum'
    }).reset_index()
    
    grouped.columns = ['Depot', 'Total Routes', 'Total Mileage', 'Total Time']
    return grouped

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
