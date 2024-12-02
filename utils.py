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

def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate specific metrics for the UMOS data."""
    if 'Depot' not in df.columns:
        raise ValueError("Depot column not found in the dataset")

    # Required columns validation
    required_cols = ['Depot', 'Hours', 'Cost', 'Distance']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Calculate metrics
    metrics = df.groupby('Depot').agg({
        'Hours': ['sum', 'mean', 'count'],
        'Cost': ['sum', 'mean'],
        'Distance': ['sum', 'mean']
    }).reset_index()

    # Flatten column names
    metrics.columns = [
        'Depot',
        'Total_Hours', 'Average_Hours', 'Route_Count',
        'Total_Cost', 'Average_Cost',
        'Total_Distance', 'Average_Distance'
    ]

    # Calculate additional metrics
    metrics['Cost_Per_Hour'] = metrics['Total_Cost'] / metrics['Total_Hours']
    metrics['Cost_Per_Route'] = metrics['Total_Cost'] / metrics['Route_Count']
    metrics['Distance_Per_Hour'] = metrics['Total_Distance'] / metrics['Total_Hours']

    # Round numeric columns to 2 decimal places
    numeric_cols = metrics.select_dtypes(include=[np.number]).columns
    metrics[numeric_cols] = metrics[numeric_cols].round(2)

    return metrics

def group_by_depot(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by Depot column and calculate comprehensive metrics."""
    return calculate_metrics(df)

def pivot_dataframe(df: pd.DataFrame) -> pd.DataFrame:

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
    """Transpose the dataframe and reset index."""
    pivoted_df = df.transpose().reset_index()
    pivoted_df.columns = ['Field'] + [f'Value_{i+1}' for i in range(len(pivoted_df.columns)-1)]
    return pivoted_df

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
