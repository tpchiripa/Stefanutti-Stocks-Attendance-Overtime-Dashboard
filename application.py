import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Stefanutti Stocks: Attendance & Overtime Dashboard", layout="wide")
st.title("📊 Stefanutti Stocks: Attendance & Overtime Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload your attendance CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset loaded successfully!")
        
        # Show columns for debugging
        st.write("Columns in dataset:", df.columns.tolist())

        # Required columns
        required_columns = ['EmployeeNumber', 'Name', 'Company', 'Project', 'OvertimeHours', 'AttendanceDate']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"❌ Missing columns in the uploaded CSV: {', '.join(missing_columns)}")
        else:
            # Filters
            companies = df['Company'].unique()
            selected_company = st.selectbox("Select Company", options=companies)
            df_company = df[df['Company'] == selected_company]

            projects = df_company['Project'].unique()
            selected_project = st.selectbox("Select Project", options=projects)
            df_filtered = df_company[df_company['Project'] == selected_project]

            # Show filtered data
            st.subheader("Filtered Attendance Data")
            st.dataframe(df_filtered)

            # Overtime summary chart
            st.subheader("Overtime Summary per Project")
            overtime_summary = df_filtered.groupby('Project')['OvertimeHours'].sum().reset_index()
            st.bar_chart(overtime_summary.set_index('Project'))

            # Optional: attendance metrics
            st.subheader("Attendance Summary")
            attendance_count = df_filtered.groupby('Project')['EmployeeNumber'].nunique().reset_index()
            attendance_count.rename(columns={'EmployeeNumber': 'Unique Employees'}, inplace=True)
            st.table(attendance_count)

    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
