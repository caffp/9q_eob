import streamlit as st
import pandas as pd
from utils import read_excel_file, filter_dataframe, generate_download_link, group_by_depot

def main():
    # Page configuration
    st.set_page_config(
        page_title="UMOS Data Processor",
        page_icon="📊",
        layout="wide"
    )

    # Load custom CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Title and description
    st.title("📊 UMOS Data Processor")
    st.markdown("""
    <div class="instructions">
        <h4>Instructions:</h4>
        <ol>
            <li>Upload your Excel file using the upload section below</li>
            <li>Preview your data and select the columns you want to keep</li>
            <li>Specify the row range to include</li>
            <li>Download the processed data in your preferred format</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
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
            st.info(f"Total rows: {len(df)}, Total columns: {len(df.columns)}")

            # Column selection
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Column Selection")
                all_columns = df.columns.tolist()
                selected_columns = st.multiselect(
                    "Select columns to include",
                    options=all_columns,
                    default=all_columns
                )

            # Row range selection
            with col2:
                st.subheader("Row Range")
                row_range = st.slider(
                    "Select row range",
                    0, len(df)-1,
                    (0, min(len(df)-1, 100)),
                    step=1
                )

            # Filter data
            filtered_df = filter_dataframe(
                df,
                selected_columns,
                row_range[0],
                row_range[1]
            )

            # Grouping options
            st.subheader("Data Grouping")
            show_depot_grouping = st.checkbox("Group by Depot", value=False)
            
            # Preview section
            st.subheader("Data Preview")
            st.markdown('<div class="data-preview">', unsafe_allow_html=True)
            
            if show_depot_grouping:
                try:
                    grouped_df = group_by_depot(filtered_df)
                    st.dataframe(grouped_df, use_container_width=True)
                    # Update filtered_df for download
                    filtered_df = grouped_df
                except ValueError as e:
                    st.error(str(e))
                    st.dataframe(filtered_df.head(10), use_container_width=True)
            else:
                st.dataframe(filtered_df.head(10), use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

            # Download section
            st.subheader("Download Processed Data")
            col1, col2 = st.columns(2)
            
            with col1:
                file_format = st.selectbox(
                    "Select output format",
                    options=["csv", "excel"],
                    index=0
                )

            with col2:
                if st.button("Download Processed Data"):
                    try:
                        file_content, mime_type = generate_download_link(
                            filtered_df,
                            file_format
                        )
                        
                        st.download_button(
                            label="Click to Download",
                            data=file_content,
                            file_name=f"processed_data.{file_format}",
                            mime=mime_type
                        )
                    except Exception as e:
                        st.error(f"Error generating download: {str(e)}")

        else:
            st.error(message)

if __name__ == "__main__":
    main()
