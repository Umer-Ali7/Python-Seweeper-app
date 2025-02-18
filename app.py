#Imports            
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import altair as alt

# App Configuration
st.set_page_config(page_title="💿 Data Sweeper", layout='wide')
st.title("💿 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# File Uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        # Read File Based on Extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue
        
        # File Information
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        
        # Display Data Preview
        st.write("🔍 Preview the Head of the DataFrame")
        st.dataframe(df.head())
        
        # Data Cleaning Options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")
            
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")
        
        # Column Selection
        st.subheader("🎯 Select Columns to Convert")
        selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]
        
        # Data Visualization
        st.subheader("📊 Data Visualization")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) >= 2:
            if st.checkbox(f"Show Visualization for {file.name}"):
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X(numeric_cols[0], title=numeric_cols[0]),
                    y=alt.Y(numeric_cols[1], title=numeric_cols[1]),
                    tooltip=numeric_cols[:2]
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Not enough numeric columns for visualization.")
        
        # File Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)
            
            # Download Button
            st.download_button(
                label=f"⬇ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("🎉 All Files Processed!")
