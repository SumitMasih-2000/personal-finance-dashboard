import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")
st.markdown("Enter your monthly income to see your ideal allocation and track your actual spending.")

# 2. Mock Data Creation (Simulating your backend database/CSV)
@st.cache_data
def load_mock_data():
    data = {
        "Date": ["2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05", "2026-06-10", "2026-06-12"],
        "Description": ["Rent", "Groceries", "Movie Night", "Electric Bill", "Stock Investment", "Coffee", "Gym Membership"],
        "Category": ["Housing", "Food", "Entertainment", "Utilities", "Savings", "Food", "Health"],
        "Budget Type": ["Needs", "Needs", "Wants", "Needs", "Savings", "Wants", "Needs"],
        "Amount": [1200.00, 150.00, 45.00, 90.00, 500.00, 7.50, 50.00]
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df_expenses = load_mock_data()

# 3. Sidebar Inputs & Filters
st.sidebar.header("📥 Dashboard Inputs")

# Main Income Input
income = st.sidebar.number_input(
    label="Enter Monthly Income ($):",
    min_value=0.0,
    value=4000.0,
    step=100.0,
    help="This will dynamically recalculate your 50/30/20 target distribution."
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

# Interactive Category Filter
available_types = ["All"] + list(df_expenses["Budget Type"].unique())
selected_type = st.sidebar.selectbox("Filter Expense Type:", available_types)

# Filter Dataframe based on selection
if selected_type != "All":
    filtered_df = df_expenses[df_expenses["Budget Type"] == selected_type]
else:
    filtered_df = df_expenses

# 4. Calculation Logic (50/30/20 Rule)
target_needs = income * 0.50
target_wants = income * 0.30
target_savings = income * 0.20

actual_needs = df_expenses[df_expenses["Budget Type"] == "Needs"]["Amount"].sum()
actual_wants = df_expenses[df_expenses["Budget Type"] == "Wants"]["Amount"].sum()
actual_savings = df_expenses[df_expenses["Budget Type"] == "Savings"]["Amount"].sum()
total_actual_spent = actual_needs + actual_wants + actual_savings
remaining_balance = income - total_actual_spent

# 5. Dashboard Row 1: KPI Metric Cards
st.subheader("📌 Allocation & Tracking Metrics")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(label="Total Income Input", value=f"${income:,.2f}")
with kpi_col2:
    st.metric(label="Actual Total Spent", value=f"${total_actual_spent:,.2f}", delta=f"-${total_actual_spent:,.2f}", delta_color="inverse")
with kpi_col3:
    st.metric(label="Remaining Balance", value=f"${remaining_balance:,.2f}", delta=f"${remaining_balance:,.2f}" if remaining_balance >= 0 else f"${remaining_balance:,.2f}")
with kpi_col4:
    # Quick health indicator
    status = "Under Budget" if total_actual_spent <= income else "Over Budget!"
    st.metric(label="Budget Status", value=status)

# 6. Dashboard Row 2: Visualizations
st.markdown("---")
st.subheader("📊 Visualizations")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("#### Target (50/30/20) vs. Actual Spending")
    
    # Prepare comparison data
    categories = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
    targets = [target_needs, target_wants, target_savings]
    actuals = [actual_needs, actual_wants, actual_savings]
    
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(name='Target Budget', x=categories, y=targets, marker_color='#A6C8FF'))
    fig_compare.add_trace(go.Bar(name='Actual Spent', x=categories, y=actuals, marker_color='#1E3A8A'))
    
    fig_compare.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_compare, use_container_width=True)

with chart_col2:
    st.write("#### Actual Expenses by Category")
    
    # Donut Chart for detailed breakdown
    fig_donut = px.pie(
        filtered_df, 
        values='Amount', 
        names='Category', 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.YlGnBu_r
    )
    fig_donut.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_donut, use_container_width=True)

# 7. Dashboard Row 3: Filtered Data Ledger
st.markdown("---")
st.subheader("📑 Filtered Expense Ledger")
st.markdown(f"Showing transactions matching filter: **{selected_type}**")
st.dataframe(filtered_df.style.format({"Amount": "${:,.2f}"}), use_container_width=True)
