import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ------------------- Page Setup -------------------
st.set_page_config(
    page_title="Stefanutti Stocks Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Stefanutti Stocks: Attendance & Overtime Dashboard")

# ------------------- File Upload -------------------
uploaded_file = st.file_uploader(
    "Upload your attendance CSV",
    type=["csv"],
    help="Drag and drop your CSV file here"
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset loaded successfully!")

        # ------------------- Sidebar Filters -------------------
        st.sidebar.header("🔍 Filters")
        regions = ["All"] + sorted(df['Region'].dropna().unique().tolist())
        disciplines = ["All"] + sorted(df['Discipline'].dropna().unique().tolist())
        projects = ["All"] + sorted(df['Project'].dropna().unique().tolist())
        employees = ["All"] + sorted(df['Employee'].dropna().unique().tolist())
        companies = ["All"] + sorted(df['Company'].dropna().unique().tolist())

        selected_region = st.sidebar.selectbox("Region", regions)
        selected_discipline = st.sidebar.selectbox("Discipline", disciplines)
        selected_project = st.sidebar.selectbox("Project", projects)
        selected_employee = st.sidebar.selectbox("Employee", employees)
        selected_company = st.sidebar.selectbox("Company", companies)

        df_filtered = df.copy()
        if selected_region != "All":
            df_filtered = df_filtered[df_filtered['Region'] == selected_region]
        if selected_discipline != "All":
            df_filtered = df_filtered[df_filtered['Discipline'] == selected_discipline]
        if selected_project != "All":
            df_filtered = df_filtered[df_filtered['Project'] == selected_project]
        if selected_employee != "All":
            df_filtered = df_filtered[df_filtered['Employee'] == selected_employee]
        if selected_company != "All":
            df_filtered = df_filtered[df_filtered['Company'] == selected_company]

        # ------------------- KPI Cards -------------------
        st.subheader("📈 Key Metrics")
        total_hours = df_filtered['Hours Worked'].sum() if 'Hours Worked' in df_filtered.columns else 0
        total_overtime = (df_filtered['Hours Worked'] - df_filtered['Standard Hours']).clip(lower=0).sum() if 'Standard Hours' in df_filtered.columns else 0
        avg_hours = df_filtered['Hours Worked'].mean() if 'Hours Worked' in df_filtered.columns else 0
        avg_overtime = (df_filtered['Hours Worked'] - df_filtered['Standard Hours']).clip(lower=0).mean() if 'Standard Hours' in df_filtered.columns else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Hours Worked", f"{total_hours:,.1f}")
        col2.metric("Total Overtime", f"{total_overtime:,.1f}")
        col3.metric("Average Hours", f"{avg_hours:,.1f}")
        col4.metric("Average Overtime", f"{avg_overtime:,.1f}")

        # ------------------- Dataset Preview -------------------
        st.subheader("📋 Dataset Preview")
        st.dataframe(df_filtered.head(10))

        # ------------------- Missing Values -------------------
        st.subheader("🛑 Missing Values Summary")
        st.dataframe(df_filtered.isna().sum())

        # ------------------- Graphical Analysis -------------------
        st.subheader("📊 Graphical Analysis")

        if 'Hours Worked' in df_filtered.columns:
            fig1 = px.histogram(df_filtered, x='Hours Worked', color='Company', nbins=20,
                                title="Distribution of Hours Worked by Company", color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(fig1, use_container_width=True)

        if 'Overtime' in df_filtered.columns or ('Hours Worked' in df_filtered.columns and 'Standard Hours' in df_filtered.columns):
            df_filtered['Overtime'] = (df_filtered['Hours Worked'] - df_filtered['Standard Hours']).clip(lower=0)
            fig2 = px.box(df_filtered, x='Company', y='Overtime', color='Company',
                          title="Overtime Comparison by Company", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2, use_container_width=True)

        # ------------------- Predictive Analysis -------------------
        st.subheader("📈 Predictive Analysis: Estimated Hours")
        target_col = 'Hours Worked'
        if target_col in df_filtered.columns:
            X = df_filtered.select_dtypes(include=np.number).drop(columns=[target_col], errors='ignore')
            y = df_filtered[target_col].fillna(df_filtered[target_col].mean())
            X = X.fillna(0)

            if not X.empty:
                model = LinearRegression()
                model.fit(X, y)
                df_filtered['Estimated Hours'] = model.predict(X)
                st.dataframe(df_filtered[['Employee', 'Hours Worked', 'Estimated Hours']].head(10))
            else:
                st.warning("Not enough numeric data for predictive analysis.")

    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
