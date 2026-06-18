import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from PIL import Image, ImageDraw

# 1. Page Configuration
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# Helper function to generate a backup logo if the file is missing
def get_dashboard_logo():
    img_path = "financial_advisor.png"
    # Check if the file actually exists on the server
    if os.path.exists(img_path):
        try:
            return Image.open(img_path)
        except Exception:
            pass
    
    # Fallback: Create a clean, professional geometric logo using code
    img = Image.new("RGB", (200, 200), color="#1E3A8A") # Dark blue background
    draw = ImageDraw.Draw(img)
    # Draw a stylized gold/yellow coin/chart representation
    draw.ellipse([40, 40, 160, 160], fill="#FBBF24") # Gold circle
    draw.rectangle([70, 90, 90, 140], fill="#1E3A8A") # Chart Bar 1
    draw.rectangle([100, 70, 120, 140], fill="#1E3A8A") # Chart Bar 2
    return img

# Initialize session state lists for user entries if they don't exist yet
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []

# 2. Sidebar Settings & Forms
st.sidebar.header(":material/public: Global Settings")
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)

# Current Market Rates (Baseline for 2026)
HYSA_RATE = 0.0425  
MARKET_RATE = 0.090  

st.sidebar.markdown("---")
st.sidebar.header(":material/edit_note: Add New Records")

# FORM A: INCOME
with st.sidebar.expander("Add Income Source", expanded=False):
    with st.form("income_form", clear_on_submit=True):
        st.markdown("#### :material/input: Log Income")
        inc_date = st.date_input("Date Received", value=datetime.today(), key="inc_date")
        inc_desc = st.text_input("Source", placeholder="e.g., Monthly Salary")
        inc_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Income") and inc_amt > 0:
            st.session_state["income_records"].append({"Date": pd.to_datetime(inc_date), "Description": inc_desc, "Amount": inc_amt})
            st.toast("Income added successfully!", icon=":material/check_circle:")

# FORM B: EXPENSE
with st.sidebar.expander("Add Expense", expanded=False):
    with st.form("expense_form", clear_on_submit=True):
        st.markdown("#### :material/receipt: Log Expense")
        exp_date = st.date_input("Date Paid", value=datetime.today(), key="exp_date")
        exp_desc = st.text_input("Item", placeholder="e.g., Groceries")
        exp_cat = st.selectbox("Category", ["Housing", "Food", "Utilities", "Entertainment", "Transport", "Health", "Other"])
        exp_type = st.selectbox("Budget Type", ["Needs", "Wants"])
        exp_amt = st.number_input("Amount", min_value=0.0, step=5.0, format="%.2f")
        if st.form_submit_button("Add Expense") and exp_amt > 0:
            st.session_state["expense_records"].append({"Date": pd.to_datetime(exp_date), "Description": exp_desc, "Category": exp_cat, "Budget Type": exp_type, "Amount": exp_amt})
            st.toast("Expense added successfully!", icon=":material/check_circle:")

# FORM C: SAVINGS & INVESTMENTS
with st.sidebar.expander("Add Savings/Investment", expanded=False):
    with st.form("savings_form", clear_on_submit=True):
        st.markdown("#### :material/savings: Log Savings/Investment")
        sav_date = st.date_input("Date Saved", value=datetime.today(), key="sav_date")
        sav_desc = st.text_input("Goal/Fund Name", placeholder="e.g., Index Fund")
        sav_cat = st.selectbox("Type", ["HYSA/Cash Savings", "Stock Market/ETF", "Insurance/Retirement"])
        sav_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Savings") and sav_amt > 0:
            st.session_state["saving_records"].append({"Date": pd.to_datetime(sav_date), "Description": sav_desc, "Category": sav_cat, "Budget Type": "Savings", "Amount": sav_amt})
            st.toast("Savings recorded!", icon=":material/check_circle:")

# RESET SYSTEM
st.sidebar.markdown("---")
st.sidebar.header(":material/settings:")
if st.sidebar.button("Reset Dashboard Data", type="primary"):
    st.session_state.clear()
    st.toast("All data reset!")
    st.rerun()

# 3. Data Processing
df_inc = pd.DataFrame(st.session_state["income_records"])
df_exp = pd.DataFrame(st.session_state["expense_records"])
df_sav = pd.DataFrame(st.session_state["saving_records"])

total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
total_savings = df_sav["Amount"].sum() if not df_sav.empty else 0.0
remaining_cash = total_income - total_expenses - total_savings

# 50/30/20 Calculations
target_needs = total_income * 0.50
target_wants = total_income * 0.30
target_savings_total = total_income * 0.20

suggested_cash_savings = target_savings_total * 0.30
suggested_investments = target_savings_total * 0.70

actual_needs = df_exp[df_exp["Budget Type"] == "Needs"]["Amount"].sum() if not df_exp.empty else 0.0
actual_wants = df_exp[df_exp["Budget Type"] == "Wants"]["Amount"].sum() if not df_exp.empty else 0.0

# Load the logo object safely
logo_image = get_dashboard_logo()

# 4. Dashboard Main View
if total_income == 0:
    welcome_col1, welcome_col2 = st.columns([1, 6])
    with welcome_col1:
        st.image(logo_image, use_container_width=True)
    with welcome_col2:
        st.title("Smart Personal Finance Hub")
        st.info("Welcome! Please log an **Income Source** in the sidebar to populate your financial dashboard.", icon=":material/info:")
else:
    # Title Header with your custom graphic
    title_col1, title_col2 = st.columns([1, 6]) 
    with title_col1:
        st.image(logo_image, use_container_width=True) 
    with title_col2:
        st.title("Smart Personal Finance Hub")
        st.markdown("### *Active Wealth Optimization & Market Analysis*")
    
    st.markdown("---")
    
    # Row 1: High Level Metrics
    st.subheader(":material/grid_view: Financial Status Cards")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Income", f"{currency_symbol}{total_income:,.2f}")
    kpi_col2.metric("Total Expenses", f"{currency_symbol}{total_expenses:,.2f}")
    kpi_col3.metric("Total Saved", f"{currency_symbol}{total_savings:,.2f}")
    kpi_col4.metric("Wallet Balance", f"{currency_symbol}{remaining_cash:,.2f}")

    st.markdown("---")

    # Advisor Suggestions
    st.subheader(":material/account_balance_wallet: Financial Advisor Suggestions")
    market_col1, market_col2 = st.columns(2)
    with market_col1:
        st.info(f"**High-Yield Cash Return:** `{HYSA_RATE*100:.2f}% APY` \n\nSecure foundation for your rainy-day reserves.", icon=":material/account_balance:")
    with market_col2:
        st.success(f"**Market Wealth Multiplier:** `{MARKET_RATE*100:.2f}% CAGR` \n\nTarget long-term inflation-beating portfolios.", icon=":material/trending_up:")

    st.write(f"Based on your income, your optimized **:material/balance: 50/30/20 Budget Target** allocations look like this:")

    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        st.markdown(f"### :material/shield: Cash Safety Net: **{currency_symbol}{suggested_cash_savings:,.2f}**")
        st.markdown(f"""
        * **Vehicle:** Liquid Premium Bank Account / Money Market.
        * **Projected 1-Year Returns:** `+{currency_symbol}{suggested_cash_savings * HYSA_RATE:,.2f}`
        """)
    with adv_col2:
        st.markdown(f"### :material/rocket_launch: Compound Investments: **{currency_symbol}{suggested_investments:,.2f}**")
        st.markdown(f"""
        * **Vehicle:** Globally Diversified Equity Index ETFs.
        * **Projected 10-Year Compounded Matrix:** `{currency_symbol}{suggested_investments * ((1 + MARKET_RATE)**10):,.2f}`
        """)

    st.markdown("---")
    
    # Row 3: Charts
    st.subheader(":material/analytics: Visualizations Matrix")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("#### Target Matrix vs. Actual Performance")
        categories = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name='Target Matrix', x=categories, y=[target_needs, target_wants, target_savings_total], marker_color='#A6C8FF'))
        fig_compare.add_trace(go.Bar(name='Your Outflows', x=categories, y=[actual_needs, actual_wants, total_savings], marker_color='#1E3A8A'))
        fig_compare.update_layout(barmode='group', height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        st.write("#### Resource Distribution Matrix")
        combined_outflows = pd.concat([df_exp, df_sav], ignore_index=True) if (not df_exp.empty or not df_sav.empty) else pd.DataFrame()
        if not combined_outflows.empty:
            fig_donut = px.pie(combined_outflows, values='Amount', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.YlGnBu_r)
            fig_donut.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("Awaiting outflows data mapping.")

    # Row 4: Ledgers
    st.markdown("---")
    st.subheader(":material/table_chart: Itemized Statement Ledgers")
    table_tabs = st.tabs(["Expense Statements", "Savings Assets", "Income Inflows"])
    with table_tabs[0]:
        if not df_exp.empty: st.dataframe(df_exp.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[1]:
        if not df_sav.empty: st.dataframe(df_sav.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[2]:
        if not df_inc.empty: st.dataframe(df_inc.sort_values(by="Date", ascending=False), use_container_width=True)
