import streamlit as st
import pandas as pd
import os
from io import BytesIO
import altair as alt
import matplotlib.pyplot as plt

# Streamlit App Setup
st.set_page_config(page_title="💿 Data Sweeper", layout='wide')
st.title("💿 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# File Upload
uploaded_files = st.file_uploader("Upload your files (CSV/Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
            
            if df.empty:
                st.error(f"⚠ The file {file.name} is empty! Please upload a valid file.")
                continue
        except Exception as e:
            st.error(f"Error loading file {file.name}: {e}")
            continue

        # Display File Info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")
        
        # Show Data Preview
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
        st.subheader("🎯 Select Columns to Keep")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                chart = alt.Chart(df).mark_bar().encode(
                    x=numeric_cols[0],
                    y=numeric_cols[1]
                ).properties(title=f"Bar Chart of {numeric_cols[0]} vs {numeric_cols[1]}")
                st.altair_chart(chart, use_container_width=True)
                
                # Matplotlib Histogram
                fig, ax = plt.subplots()
                df[numeric_cols[0]].hist(ax=ax, bins=20, color='blue', edgecolor='black')
                ax.set_title(f"Histogram of {numeric_cols[0]}")
                st.pyplot(fig)
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
                    df.to_excel(writer, index=False)
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
            if succ != '':
                st.success(f"📁 File has been converted to !{file.name}")

# st.success("🎉 All Files Processed!")
