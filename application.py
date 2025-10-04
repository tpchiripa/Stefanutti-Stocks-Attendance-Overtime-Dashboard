import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stefanutti Stocks: Attendance & Overtime Dashboard", layout="wide")

st.title("📊 Stefanutti Stocks: Attendance & Overtime Dashboard")
uploaded_file = st.file_uploader("Upload your attendance CSV", type=["csv"])

if uploaded_file:
    # Load dataset
    df = pd.read_csv(uploaded_file)
    st.success("✅ Dataset loaded successfully!")

    # Check required columns
    required_cols = ['EmployeeName', 'Date', 'TotalHours', 'Normal Time Hours', 'Company', 'Region', 'Occupation', 'EmployeeNumber']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing columns in the uploaded CSV: {', '.join(missing_cols)}")
    else:
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Sidebar filters
        st.sidebar.header("Filters")
        company_filter = st.sidebar.multiselect("Select Company", options=df['Company'].unique(), default=df['Company'].unique())
        region_filter = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
        occupation_filter = st.sidebar.multiselect("Select Occupation", options=df['Occupation'].unique(), default=df['Occupation'].unique())
        date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

        # Apply filters
        filtered_df = df[
            (df['Company'].isin(company_filter)) &
            (df['Region'].isin(region_filter)) &
            (df['Occupation'].isin(occupation_filter)) &
            (df['Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
        ]

        # KPI cards
        total_employees = filtered_df['EmployeeNumber'].nunique()
        total_normal_hours = filtered_df['Normal Time Hours'].sum()
        total_overtime = filtered_df['TotalHours'].sum() - total_normal_hours
        avg_overtime = total_overtime / total_employees if total_employees > 0 else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Employees", total_employees)
        kpi2.metric("Total Normal Hours", round(total_normal_hours,2))
        kpi3.metric("Total Overtime Hours", round(total_overtime,2))
        kpi4.metric("Average Overtime per Employee", round(avg_overtime,2))

        # Show filtered dataframe
        st.subheader("Filtered Attendance Data")
        st.dataframe(filtered_df)

        # Download filtered CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered CSV", csv, "filtered_attendance.csv", "text/csv")

        # --- VISUALIZATIONS ---
        st.subheader("Visual Summary")

        # 1️⃣ Bar chart: Overtime by Employee
        filtered_df['OvertimeHours'] = filtered_df['TotalHours'] - filtered_df['Normal Time Hours']
        overtime_per_employee = filtered_df.groupby('EmployeeName')['OvertimeHours'].sum().reset_index()
        fig_bar = px.bar(overtime_per_employee, x='EmployeeName', y='OvertimeHours', 
                         title="Overtime Hours per Employee", text='OvertimeHours')
        st.plotly_chart(fig_bar, use_container_width=True)

        # 2️⃣ Line chart: Total Hours over Time
        hours_over_time = filtered_df.groupby('Date')['TotalHours'].sum().reset_index()
        fig_line = px.line(hours_over_time, x='Date', y='TotalHours', 
                           title="Total Hours Worked Over Time", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
