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

def group_by_depot(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by Depot column and calculate specific metrics."""
    if 'Depot' not in df.columns:
        raise ValueError("Depot column not found in the dataset")
    
    required_cols = ['DeliveryCases', 'TotalTime', 'OnTimePct']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    
    grouped = df.groupby('Depot').agg({
        'DeliveryCases': ['sum', 'count'],  # Delivery Cases and Routes
        'TotalTime': 'sum',                 # Delivery Hours
        'OnTimePct': 'mean'                 # On-Time %
    }).reset_index()
    
    # Flatten multi-level columns
    grouped.columns = ['Depot', 'Delivery Cases', 'Routes', 'Delivery Hours', 'On-time %']
    
    # Convert Delivery Hours to integer
    grouped['Delivery Hours'] = grouped['Delivery Hours'].astype(int)
    
    # Convert On-time percentage to whole percentage
    grouped['On-time %'] = (grouped['On-time %'] * 100).round()
    
    return grouped

def pivot_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the dataframe to show metrics as rows and depots as columns."""
    # Set Depot as columns
    pivot_df = df.set_index('Depot').transpose()
    
    # Reset index to make metrics names as a column
    pivot_df = pivot_df.reset_index()
    pivot_df.columns = ['Metric'] + list(pivot_df.columns[1:])
    
    return pivot_df

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
