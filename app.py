import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Page & State Configuration
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")
st.title("💰 Smart Personal Finance Dashboard")
st.markdown("Log your finances and get AI-driven investment suggestions based on current market rates.")

# Initialize session state lists
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []

# 2. Sidebar Settings & Forms
st.sidebar.header("🌍 Global Settings")
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)

# Current Market Rates (Simulated live baseline for 2026)
HYSA_RATE = 0.0425  # 4.25% High-Yield Savings Account 
MARKET_RATE = 0.090  # 9.0% Broad Market Index Fund average

st.sidebar.markdown("---")
st.sidebar.header("📝 Add New Records")

# FORM A: INCOME
with st.sidebar.expander("💵 Add Income Source", expanded=False):
    with st.form("income_form", clear_on_submit=True):
        inc_date = st.date_input("Date Received", value=datetime.today(), key="inc_date")
        inc_desc = st.text_input("Source", placeholder="e.g., Monthly Salary")
        inc_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Income") and inc_amt > 0:
            st.session_state["income_records"].append({"Date": pd.to_datetime(inc_date), "Description": inc_desc, "Amount": inc_amt})
            st.toast("Income added!")

# FORM B: EXPENSE
with st.sidebar.expander("💸 Add Expense", expanded=False):
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input("Date Paid", value=datetime.today(), key="exp_date")
        exp_desc = st.text_input("Item", placeholder="e.g., Groceries")
        exp_cat = st.selectbox("Category", ["Housing", "Food", "Utilities", "Entertainment", "Transport", "Health", "Other"])
        exp_type = st.selectbox("Budget Type", ["Needs", "Wants"])
        exp_amt = st.number_input("Amount", min_value=0.0, step=5.0, format="%.2f")
        if st.form_submit_button("Add Expense") and exp_amt > 0:
            st.session_state["expense_records"].append({"Date": pd.to_datetime(exp_date), "Description": exp_desc, "Category": exp_cat, "Budget Type": exp_type, "Amount": exp_amt})
            st.toast("Expense added!")

# FORM C: SAVINGS
with st.sidebar.expander("🐷 Add Savings/Investment", expanded=False):
    with st.form("savings_form", clear_on_submit=True):
        sav_date = st.date_input("Date Saved", value=datetime.today(), key="sav_date")
        sav_desc = st.text_input("Goal/Fund Name", placeholder="e.g., Index Fund")
        sav_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Savings") and sav_amt > 0:
            st.session_state["saving_records"].append({"Date": pd.to_datetime(sav_date), "Description": sav_desc, "Category": "Savings", "Budget Type": "Savings", "Amount": sav_amt})
            st.toast("Savings recorded!")

# 3. Data Processing
df_inc = pd.DataFrame(st.session_state["income_records"])
df_exp = pd.DataFrame(st.session_state["expense_records"])
df_sav = pd.DataFrame(st.session_state["saving_records"])

total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
total_savings = df_sav["Amount"].sum() if not df_sav.empty else 0.0
remaining_cash = total_income - total_expenses - total_savings

# 50/30/20 Targets
target_needs = total_income * 0.50
target_wants = total_income * 0.30
target_savings_total = total_income * 0.20

# Smart Breakdown of the 20% Savings Target based on market rates
suggested_cash_savings = target_savings_total * 0.30  # 30% of savings to liquid cash
suggested_investments = target_savings_total * 0.70   # 70% of savings to index funds

actual_needs = df_exp[df_exp["Budget Type"] == "Needs"]["Amount"].sum() if not df_exp.empty else 0.0
actual_wants = df_exp[df_exp["Budget Type"] == "Wants"]["Amount"].sum() if not df_exp.empty else 0.0

# 4. Dashboard Main View
if total_income == 0:
    st.info("👋 Welcome! Please add an **Income Source** in the sidebar to generate your custom savings and market investment plan.")
else:
    # Row 1: High Level Metrics
    st.subheader("📌 Financial Overview")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Income", f"{currency_symbol}{total_income:,.2f}")
    kpi_col2.metric("Total Expenses", f"{currency_symbol}{total_expenses:,.2f}")
    kpi_col3.metric("Total Saved/Invested", f"{currency_symbol}{total_savings:,.2f}")
    kpi_col4.metric("Unallocated Cash", f"{currency_symbol}{remaining_cash:,.2f}")

    st.markdown("---")

    # NEW SECTION: Market-Based Suggestions
    st.subheader("💡 Market-Based Investment Advisor")
    
    # Displaying current market conditions metrics
    market_col1, market_col2 = st.columns(2)
    with market_col1:
        st.info(f"**Current Safe Cash Rate (HYSA/CD):** `{HYSA_RATE*100:.2f}% API` \n\nBest for short-term emergency funds.")
    with market_col2:
        st.success(f"**Estimated Market Return (Index Funds):** `{MARKET_RATE*100:.2f}% CAGR` \n\nBest for long-term wealth building.")

    st.write(f"Based on your monthly income of **{currency_symbol}{total_income:,.2f}**, your ideal target is to set aside **{currency_symbol}{target_savings_total:,.2f}** (20%). Here is how you should optimize it right now:")

    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        st.markdown(f"### 🏦 Liquid Cash Savings: **{currency_symbol}{suggested_cash_savings:,.2f}**")
        st.markdown(f"""
        * **Where to put it:** High-Yield Savings Account or Money Market Funds.
        * **Why:** At current **{HYSA_RATE*100:.1f}%** rates, your cash keeps up with inflation while staying 100% safe. 
        * **Estimated 1-Year Growth on this month's cash:** `+{currency_symbol}{suggested_cash_savings * HYSA_RATE:,.2f}`
        """)

    with adv_col2:
        st.markdown(f"### 📈 Long-Term Investments: **{currency_symbol}{suggested_investments:,.2f}**")
        st.markdown(f"""
        * **Where to put it:** Broad-market equity ETFs (like an S&P 500 or Total World index fund).
        * **Why:** Equities historically outperform cash. Compounding at a conservative **{MARKET_RATE*100:.1f}%** market rate is critical for building long-term wealth.
        * **Estimated 10-Year Value (Compounded):** `{currency_symbol}{suggested_investments * ((1 + MARKET_RATE)**10):,.2f}`
        """)

    st.markdown("---")
    
    # Row 3: Charts
    st.subheader("📊 Target Allocations vs. Current Spending")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        categories = ['Needs (50%)', 'Wants (30%)', 'Savings/Investments (20%)']
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name='Target Budget', x=categories, y=[target_needs, target_wants, target_savings_total], marker_color='#A6C8FF'))
        fig_compare.add_trace(go.Bar(name='Your Progress', x=categories, y=[actual_needs, actual_wants, total_savings], marker_color='#1E3A8A'))
        fig_compare.update_layout(barmode='group', height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        combined_outflows = pd.concat([df_exp, df_sav], ignore_index=True) if (not df_exp.empty or not df_sav.empty) else pd.DataFrame()
        if not combined_outflows.empty:
            fig_donut = px.pie(combined_outflows, values='Amount', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.YlGnBu_r)
            fig_donut.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("No transactions logged yet.")

    # Row 4: Ledgers
    st.subheader("📑 Itemized Ledgers")
    table_tabs = st.tabs(["Expenses Ledger", "Savings & Investments", "Income Ledger"])
    with table_tabs[0]:
        if not df_exp.empty: st.dataframe(df_exp.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[1]:
        if not df_sav.empty: st.dataframe(df_sav.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[2]:
        if not df_inc.empty: st.dataframe(df_inc.sort_values(by="Date", ascending=False), use_container_width=True)
