import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Page & State Configuration
st.set_page_config(page_title="Dynamic Finance Tracker", layout="wide")
st.title("💰 Personal Finance Dashboard")
st.markdown("Log your financial data dynamically and track your target allocations.")

# Initialize session state lists for user entries if they don't exist yet
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []

# 2. Sidebar Global Controls (Currency & Setup)
st.sidebar.header("🌍 Global Settings")
currency_symbol = st.sidebar.selectbox(
    "Select Currency Symbol:",
    ["$", "₹", "€", "£", "¥", "₱", "₨"],
    index=0
)

st.sidebar.markdown("---")

# 3. Data Entry Forms (Expander Panels)
st.sidebar.header("📝 Add New Records")

# FORM A: INCOME
with st.sidebar.expander("💵 Add Income Source", expanded=False):
    with st.form("income_form", clear_on_submit=True):
        inc_date = st.date_input("Date Received", value=datetime.today(), key="inc_date")
        inc_desc = st.text_input("Source/Description", placeholder="e.g., Monthly Salary")
        inc_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        submit_inc = st.form_submit_button("Add Income")
        
        if submit_inc and inc_amt > 0:
            st.session_state["income_records"].append({
                "Date": pd.to_datetime(inc_date), "Description": inc_desc, "Amount": inc_amt
            })
            st.toast("Income added successfully!")

# FORM B: EXPENSE
with st.sidebar.expander("💸 Add Expense", expanded=False):
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input("Date Paid", value=datetime.today(), key="exp_date")
        exp_desc = st.text_input("Item/Description", placeholder="e.g., Groceries")
        exp_cat = st.selectbox("Category", ["Housing", "Food", "Utilities", "Entertainment", "Transport", "Health", "Other"])
        exp_type = st.selectbox("Budget Type", ["Needs", "Wants"])
        exp_amt = st.number_input("Amount", min_value=0.0, step=5.0, format="%.2f")
        submit_exp = st.form_submit_button("Add Expense")
        
        if submit_exp and exp_amt > 0:
            st.session_state["expense_records"].append({
                "Date": pd.to_datetime(exp_date), "Description": exp_desc, 
                "Category": exp_cat, "Budget Type": exp_type, "Amount": exp_amt
            })
            st.toast("Expense added successfully!")

# FORM C: SAVINGS
with st.sidebar.expander("🐷 Add Savings Deposit", expanded=False):
    with st.form("savings_form", clear_on_submit=True):
        sav_date = st.date_input("Date Saved", value=datetime.today(), key="sav_date")
        sav_desc = st.text_input("Goal/Fund Name", placeholder="e.g., Emergency Fund")
        sav_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        submit_sav = st.form_submit_button("Add Savings")
        
        if submit_sav and sav_amt > 0:
            st.session_state["saving_records"].append({
                "Date": pd.to_datetime(sav_date), "Description": sav_desc, 
                "Category": "Savings", "Budget Type": "Savings", "Amount": sav_amt
            })
            st.toast("Savings recorded!")

# 4. Process Data State into Pandas DataFrames
df_inc = pd.DataFrame(st.session_state["income_records"])
df_exp = pd.DataFrame(st.session_state["expense_records"])
df_sav = pd.DataFrame(st.session_state["saving_records"])

# Calculate Totals safely depending on empty states
total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
total_savings = df_sav["Amount"].sum() if not df_sav.empty else 0.0
remaining_cash = total_income - total_expenses - total_savings

# Target Metrics based on 50/30/20 Rule of actual income entered
target_needs = total_income * 0.50
target_wants = total_income * 0.30
target_savings = total_income * 0.20

# Actual tracking metrics grouped by 50/30/20 definitions
actual_needs = df_exp[df_exp["Budget Type"] == "Needs"]["Amount"].sum() if not df_exp.empty else 0.0
actual_wants = df_exp[df_exp["Budget Type"] == "Wants"]["Amount"].sum() if not df_exp.empty else 0.0
actual_savings = total_savings

# 5. Dashboard View Logic
if total_income == 0 and total_expenses == 0 and total_savings == 0:
    st.info("👋 Welcome! Use the tools in the left sidebar to add your first Income, Expense, or Savings record.")
else:
    # Row 1: KPI Summary Cards
    st.subheader("📌 Overall Status Summary")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric(label="Total Income Logged", value=f"{currency_symbol}{total_income:,.2f}")
    with kpi_col2:
        st.metric(label="Total Expenses Logged", value=f"{currency_symbol}{total_expenses:,.2f}")
    with kpi_col3:
        st.metric(label="Total Savings Built", value=f"{currency_symbol}{total_savings:,.2f}")
    with kpi_col4:
        st.metric(label="Unallocated Cash Left", value=f"{currency_symbol}{remaining_cash:,.2f}")

    st.markdown("---")
    
    # Row 2: Charts Section
    st.subheader("📊 Target Allocations vs. Your Activity")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("#### 50/30/20 Rule Comparison")
        categories = ['Needs (50% Target)', 'Wants (30% Target)', 'Savings (20% Target)']
        targets = [target_needs, target_wants, target_savings]
        actuals = [actual_needs, actual_wants, actual_savings]
        
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name='Ideal Allocation Target', x=categories, y=targets, marker_color='#A6C8FF'))
        fig_compare.add_trace(go.Bar(name='Your Actual Logged', x=categories, y=actuals, marker_color='#1E3A8A'))
        fig_compare.update_layout(barmode='group', height=330, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        st.write("#### Spending Breakdown by Category")
        # Combine expenses and savings dataframes into a master itemized table for a clean total overview
        combined_outflows = pd.concat([df_exp, df_sav], ignore_index=True) if (not df_exp.empty or not df_sav.empty) else pd.DataFrame()
        
        if not combined_outflows.empty:
            fig_donut = px.pie(
                combined_outflows, 
                values='Amount', 
                names='Category', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.YlGnBu_r
            )
            fig_donut.update_layout(height=330, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("No outgoing expenses or savings logged to display distribution charts.")

    st.markdown("---")

    # Row 3: Filterable Data Tables
    st.subheader("📑 Itemized Ledgers")
    table_tabs = st.tabs(["Expenses Ledger", "Savings Records", "Income Records"])
    
    with table_tabs[0]:
        if not df_exp.empty:
            st.dataframe(df_exp.sort_values(by="Date", ascending=False).style.format({"Amount": f"{currency_symbol}{{:,.2f}} "}), use_container_width=True)
        else:
            st.caption("No expenses logged.")
            
    with table_tabs[1]:
        if not df_sav.empty:
            st.dataframe(df_sav.sort_values(by="Date", ascending=False).style.format({"Amount": f"{currency_symbol}{{:,.2f}} "}), use_container_width=True)
        else:
            st.caption("No savings records logged.")
            
    with table_tabs[2]:
        if not df_inc.empty:
            st.dataframe(df_inc.sort_values(by="Date", ascending=False).style.format({"Amount": f"{currency_symbol}{{:,.2f}} "}), use_container_width=True)
        else:
            st.caption("No income records logged.")
