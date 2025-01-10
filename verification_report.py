import streamlit as st
import pandas as pd
import os

# Set the page layout
st.set_page_config(page_title="File Processing App", page_icon="📁", layout="wide")

# Title of the application
st.title("Interactive File Import and Export App")
st.markdown("Upload your CSV or Excel files for processing and export the results!")

# File uploader for CSV and Excel
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['xlsx', 'csv'])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1]

    # Load the file based on its type
    if file_type == 'xlsx':
        df = pd.read_excel(uploaded_file)
    elif file_type == 'csv':
        df = pd.read_csv(uploaded_file)

    st.write("### Data Preview")
    st.dataframe(df.head())  # Display the first few rows of the data

    # Add 'Date' column by extracting from 'Verification DateTime'
    if 'Verification DateTime' in df.columns:
        df['Date'] = df['Verification DateTime'].str[:10]

    # Rename 'Passed' to 'Verified' in 'Verification Result' column
    if 'Verification Result' in df.columns:
        df['Verification Result'] = df['Verification Result'].replace('Passed', 'Verified')

    # Add 'Verified_Preference' column
    if 'Verification Result' in df.columns:
        df['Verified_Preference'] = df['Verification Result'].apply(lambda x: 1 if x == 'Verified' else 0)

    # Perform the sorting and filtering logic
    if all(col in df.columns for col in ['Roll No', 'Verified_Preference', 'Type']):
        df_sorted1 = df.sort_values(by=['Roll No', 'Verified_Preference', 'Type'], ascending=[True, False, True])
        df_sorted1 = df_sorted1.drop(columns=['Verified_Preference'])
        df_sorted = df_sorted1.sort_values(by=['Roll No', 'Verification Result', 'Date', 'Type'],
                                           ascending=[True, False, False, True])
        df_filtered = df_sorted.drop_duplicates(subset=['Roll No', 'Date','Exam Code'], keep='first')

        st.write("### Processed Data")
        st.dataframe(df_filtered.head())  # Show the processed data

        # Let the user select which columns to export
        st.write("### Export Options")
        columns_to_export = st.multiselect("Select columns to export", df_filtered.columns.tolist(),
                                           default=df_filtered.columns.tolist())

        # Input for the export path
        export_path = st.text_input("Enter the path to save the processed file", "")
        if export_path:
            export_file_name = st.text_input("Enter the file name for the exported file", "processed_file.xlsx")
            save_path = os.path.join(export_path, export_file_name)

            # Button to export the file
            if st.button("Export"):
                with st.spinner("Exporting file..."):
                    df_filtered[columns_to_export].to_excel(save_path, index=False)
                    st.success(f"File exported successfully to {save_path}")
    else:
        st.warning("Required columns not found: 'Roll No', 'Verification Result', 'Type'")
