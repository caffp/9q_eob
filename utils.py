import pandas as pd
import numpy as np
import io
from typing import Tuple, Optional

DEPOT_ORDER = [
    'D9Q00001', 'D9Q00002', 'D9Q00003', 'D9Q00004', 'D9Q00005', 'D9Q00006',
    'D9Q00007', 'D9Q00017', 'D9Q00030', 'D9Q00040', 'D9Q00041', 'D9Q00043'
]

DEPOT_NAMES = {
    'D9Q00001': 'Spokane',
    'D9Q00002': 'Pasco',
    'D9Q00003': 'Kalispell',
    'D9Q00004': 'Moses Lake',
    'D9Q00005': 'Missoula',
    'D9Q00006': 'Lewiston',
    'D9Q00007': 'Malott',
    'D9Q00017': 'Walla Walla',
    'D9Q00030': 'Sandpoint',
    'D9Q00040': 'Yakima',
    'D9Q00041': 'Ellensburg',
    'D9Q00043': 'St. Regis'
}


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
        raise ValueError(
            f"Missing required columns: {', '.join(missing_cols)}")

    grouped = df.groupby('Depot').agg({
        'DeliveryCases': ['sum', 'count'],  # Delivery Cases and Routes
        'TotalTime': 'sum',  # Delivery Hours
        'OnTimePct': 'mean'  # On-Time %
    }).reset_index()

    # Flatten multi-level columns
    grouped.columns = [
        'Depot', 'Delivery Cases', 'Routes', 'Delivery Hours', 'On-time %'
    ]

    # Convert Delivery Hours to integer
    grouped['Delivery Hours'] = grouped['Delivery Hours'].astype(int)

    # Convert On-time percentage to whole percentage
    grouped['On-time %'] = (grouped['On-time %'] * 100).round()

    return grouped


def pivot_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the dataframe to show metrics as rows and depots as columns."""
    # Create empty DataFrame with all depots
    all_depots_df = pd.DataFrame({'Depot': DEPOT_ORDER})

    # Merge with actual data, keeping all depots
    merged_df = pd.merge(all_depots_df, df, on='Depot', how='left')

    # Fill missing values with 0
    merged_df = merged_df.fillna(0)

    # Set Depot as columns in specified order
    pivot_df = merged_df.set_index('Depot').transpose()

    # Reset index to make metrics names as a column
    pivot_df = pivot_df.reset_index()

    # Rename columns using the DEPOT_NAMES mapping
    new_columns = ['Metric'] + [DEPOT_NAMES[depot] for depot in DEPOT_ORDER]
    pivot_df.columns = new_columns

    return pivot_df


def process_trailer_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Process trailer weight data and return individual route weights."""
    missing_columns = []
    required_columns = {
        'ROUTE_ID': 'Route ID',
        'DESCRIPTION': 'Route Description',
        'DeliveryWeight': 'Delivery Weight'
    }
    
    for col, display_name in required_columns.items():
        if col not in df.columns:
            missing_columns.append(display_name)
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    route_weights = df[['ROUTE_ID', 'DESCRIPTION', 'DeliveryWeight']].copy()
    route_weights = route_weights.sort_values('ROUTE_ID')
    return route_weights


def generate_download_link(df: pd.DataFrame, file_format: str) -> Tuple[bytes, str]:
    """Generate downloadable file in specified format with side-by-side layout for Excel."""
    if file_format == "csv":
        output = df.to_csv(index=False)
        return output.encode(), "text/csv"
    elif file_format == "excel":
        output = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Calculate split point
            total_rows = len(df)
            mid_point = total_rows // 2
            
            # Split dataframe
            df1 = df.iloc[:mid_point]
            df2 = df.iloc[mid_point:]
            
            # Write first half (including headers)
            df1.to_excel(writer, index=False, startrow=0, startcol=0)
            
            # Write second half (starting at row 2, column E)
            df2.to_excel(writer, index=False, startrow=1, startcol=4, header=False)
        
        return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        raise ValueError("Unsupported file format")
