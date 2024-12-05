import streamlit as st
import pandas as pd
from datetime import datetime
from utils import read_excel_file, generate_download_link, group_by_depot, pivot_dataframe, process_trailer_weights

def main():
    # Page configuration
    st.set_page_config(
        page_title="9Q Routing EOB",
        page_icon="📊",
        layout="wide"
    )

    # Load custom CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Title and description
    st.title("📊 9Q Routing EOB")
    st.markdown("""
    <div class="instructions">
        <h4>Instructions:</h4>
        <ol>
            <li>Upload your qryRouteSummary.xlsx file</li>
            <li>View the processed metrics by depot</li>
            <li>Download the processed data in your preferred format</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        # Validate file name
        if uploaded_file.name != "qryRouteSummary.xlsx":
            st.error("Please upload a file named 'qryRouteSummary.xlsx'")
            return

        # Read the Excel file
        df, message = read_excel_file(uploaded_file)
        
        if df is not None:
            # Display file info
            st.success(f"File uploaded successfully: {uploaded_file.name}")
            
            try:
                # Create tabs for different views
                delivery_tab, trailer_tab = st.tabs(["Delivery Metrics", "Trailer Weights"])
                
                with delivery_tab:
                    # First group the data
                    grouped_df = group_by_depot(df)
                    
                    # Then pivot the grouped data
                    final_df = pivot_dataframe(grouped_df)
                    
                    # Format Delivery_Cases as integers
                    for col in final_df.columns:
                        if col != 'Metric':  # Skip the Metric column
                            final_df.loc[final_df['Metric'] == 'Delivery Cases', col] = final_df.loc[final_df['Metric'] == 'Delivery Cases', col].astype(int)
                    
                    # Display metrics
                    st.markdown("### Metrics by Depot")
                    st.dataframe(final_df, use_container_width=True)
                    
                    # Display summary statistics
                    st.markdown("### Summary Statistics")
                    summary_cols = st.columns(4)
                    with summary_cols[0]:
                        st.metric("Total Routes", int(grouped_df['Routes'].sum()))
                    with summary_cols[1]:
                        st.metric("Total Delivery Cases", f"{int(grouped_df['Delivery Cases'].sum())}")
                    with summary_cols[2]:
                        st.metric("Average On-Time %", f"{round(grouped_df['On-time %'].mean())}%")
                    with summary_cols[3]:
                        st.metric("Total Delivery Hours", f"{grouped_df['Delivery Hours'].sum():.2f}")
                    
                    # Download section for delivery metrics
                    st.subheader("Download Delivery Metrics")
                    col1, col2 = st.columns(2)
                    with col1:
                        delivery_format = st.selectbox(
                            "Select output format",
                            options=["csv", "excel"],
                            index=0,
                            key="delivery_format"
                        )
                    with col2:
                        if st.button("Download Delivery Metrics"):
                            try:
                                file_content, mime_type = generate_download_link(
                                    final_df,
                                    delivery_format
                                )
                                current_date = datetime.now().strftime("%m_%d_%Y")
                                st.download_button(
                                    label="Click to Download",
                                    data=file_content,
                                    file_name=f"umos_{current_date}.{delivery_format}",
                                    mime=mime_type
                                )
                            except Exception as e:
                                st.error(f"Error generating download: {str(e)}")
                
                with trailer_tab:
                    st.markdown('''
                    ### Trailer Weight Analysis
                    This tab analyzes route-specific delivery weights. The input file must contain:
                    - ROUTE_ID (Route identifier)
                    - DESCRIPTION (Route description)
                    - DeliveryWeight (Weight in specified units)
                    ''')
                    
                    try:
                        route_weights = process_trailer_weights(df)
                        st.dataframe(route_weights, use_container_width=True)
                        
                        # Download section for trailer weights
                        st.subheader("Download Trailer Weights")
                        col1, col2 = st.columns(2)
                        with col1:
                            trailer_format = st.selectbox(
                                "Select output format",
                                options=["csv", "excel"],
                                index=0,
                                key="trailer_format"
                            )
                        with col2:
                            if st.button("Download Trailer Weights"):
                                try:
                                    file_content, mime_type = generate_download_link(
                                        route_weights,
                                        trailer_format
                                    )
                                    current_date = datetime.now().strftime("%m_%d_%Y")
                                    st.download_button(
                                        label="Click to Download",
                                        data=file_content,
                                        file_name=f"trailer_weights_{current_date}.{trailer_format}",
                                        mime=mime_type
                                    )
                                except Exception as e:
                                    st.error(f"Error generating download: {str(e)}")
                        
                    except ValueError as e:
                        st.warning(str(e))
                        st.info("Please upload a file that contains the required columns to view the weight analysis.")
                
            except ValueError as e:
                st.error(str(e))
        else:
            st.error(message)

if __name__ == "__main__":
    main()