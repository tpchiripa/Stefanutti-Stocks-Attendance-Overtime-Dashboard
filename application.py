# application.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# --- Page Config ---
st.set_page_config(
    page_title="Stefanutti Stocks: Attendance & Overtime Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='text-align:center; color: navy;'>🕒 Stefanutti Stocks: Attendance & Overtime Dashboard</h1>", unsafe_allow_html=True)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload merged_attendance.csv", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Dataset loaded successfully!")

    # --- Sidebar Filters ---
    companies = ['All'] + sorted(df['Company'].dropna().unique().tolist())
    regions = ['All'] + sorted(df['Region'].dropna().unique().tolist())
    disciplines = ['All'] + sorted(df['Discipline'].dropna().unique().tolist())
    projects = ['All'] + sorted(df['ContractCode'].dropna().unique().tolist())
    employees = ['All'] + sorted(df['EmployeeName'].dropna().unique().tolist())

    company_filter = st.sidebar.selectbox("Select Company", companies)
    region_filter = st.sidebar.selectbox("Select Region", regions)
    discipline_filter = st.sidebar.selectbox("Select Discipline", disciplines)
    project_filter = st.sidebar.selectbox("Select Project", projects)
    employee_filter = st.sidebar.selectbox("Select Employee", employees)

    # --- Apply Filters ---
    df_filtered = df.copy()
    if company_filter != 'All':
        df_filtered = df_filtered[df_filtered['Company'] == company_filter]
    if region_filter != 'All':
        df_filtered = df_filtered[df_filtered['Region'] == region_filter]
    if discipline_filter != 'All':
        df_filtered = df_filtered[df_filtered['Discipline'] == discipline_filter]
    if project_filter != 'All':
        df_filtered = df_filtered[df_filtered['ContractCode'] == project_filter]
    if employee_filter != 'All':
        df_filtered = df_filtered[df_filtered['EmployeeName'] == employee_filter]

    # --- Dataset Preview ---
    st.subheader("📊 Filtered Data Preview")
    st.dataframe(df_filtered.head(20))

    # --- Missing Values Summary ---
    st.subheader("🛑 Missing Values Summary")
    missing_summary = pd.DataFrame({
        'MissingCount': df_filtered.isna().sum(),
        'MissingPercentage': (df_filtered.isna().sum() / len(df_filtered) * 100).round(2)
    })
    st.dataframe(missing_summary)

    # --- Total Hours & Overtime Summary ---
    st.subheader("⏱ Total Hours & Overtime Summary")
    st.write(df_filtered[['TotalHours', 'Normal Time Hours', 'Over Time 1Hours', 'Over Time 2Hours']].describe())

    # --- Scatter Plot: TotalHours vs Overtime ---
    st.subheader("📈 Total Hours vs Over Time 1 Hours")
    fig, ax = plt.subplots(figsize=(10,5))
    sns.scatterplot(
        data=df_filtered,
        x='TotalHours',
        y='Over Time 1Hours',
        hue='Region',
        style='EmployeeType',
        palette='Set2',
        s=100,
        ax=ax
    )
    ax.set_title("Total Hours vs Over Time 1 Hours", fontsize=16)
    st.pyplot(fig)

    # --- Predictive Analysis: Estimate Total Hours ---
    st.subheader("🔮 Predictive Analysis: Estimated Total Hours")
    df_model = df_filtered.dropna(subset=['TotalHours'])  # drop rows with NaN target
    if len(df_model) > 0:
        X = df_model[['Normal Time Hours', 'Over Time 1Hours', 'Over Time 2Hours']]
        y = df_model['TotalHours']
        model = LinearRegression()
        model.fit(X, y)
        df_model['Predicted_TotalHours'] = model.predict(X)
        st.write(df_model[['EmployeeName', 'TotalHours', 'Predicted_TotalHours']].head(20))
    else:
        st.warning("No valid data for predictive analysis after dropping NaNs.")

    # --- Download Filtered Data ---
    st.subheader("💾 Download Filtered Data")
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_attendance.csv',
        mime='text/csv'
    )
