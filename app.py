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
    if os.path.exists(img_path):
        try:
            return Image.open(img_path)
        except Exception:
            pass
    
    img = Image.new("RGB", (200, 200), color="#000000") 
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 40, 160, 160], fill="#0052CC") 
    draw.rectangle([70, 90, 90, 140], fill="#FFFFFF") 
    draw.rectangle([100, 70, 120, 140], fill="#E6F0FF") 
    return img

# Initialize session state lists for data if they don't exist yet
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []

# 2. Sidebar Settings & Forms
st.sidebar.header(":material/public: Global Settings")
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)

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

target_needs = total_income * 0.50
target_wants = total_income * 0.30
target_savings_total = total_income * 0.20

suggested_cash_savings = target_savings_total * 0.30
suggested_investments = target_savings_total * 0.70

actual_needs = df_exp[df_exp["Budget Type"] == "Needs"]["Amount"].sum() if not df_exp.empty else 0.0
actual_wants = df_exp[df_exp["Budget Type"] == "Wants"]["Amount"].sum() if not df_exp.empty else 0.0

# Dynamic Health Score: Shows retention rate (Savings + Wallet Cash / Total Income)
if total_income > 0:
    retention_rate = ((total_savings + max(0.0, remaining_cash)) / total_income) * 100
    health_score = min(100.0, max(0.0, retention_rate))
else:
    health_score = 0.0

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
    title_col1, title_col2 = st.columns([1, 6]) 
    with title_col1:
        st.image(logo_image, use_container_width=True) 
    with title_col2:
        st.title("Smart Personal Finance Hub")
        st.markdown("### *Active Wealth Optimization & Market Analysis*")
    
    st.markdown("---")
    
    # Row 1: High Level Metrics + Gauge
    kpi_col1, kpi_col2 = st.columns([3, 1])
    
    with kpi_col1:
        st.subheader(":material/grid_view: Financial Status Cards")
        metric_sub_col1, metric_sub_col2 = st.columns(2)
        metric_sub_col1.metric("Total Income Inflow", f"{currency_symbol}{total_income:,.2f}")
        metric_sub_col1.metric("Total Expenses Outflow", f"{currency_symbol}{total_expenses:,.2f}")
        metric_sub_col2.metric("Total Capital Saved", f"{currency_symbol}{total_savings:,.2f}")
        metric_sub_col2.metric("Available Liquidity", f"{currency_symbol}{remaining_cash:,.2f}")
        
    with kpi_col2:
        st.markdown("<h3 style='text-align: center; margin-bottom: -20px;'>Health Matrix</h3>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#FFFFFF"},
                'bar': {'color': "#0052CC"},
                'bgcolor': "#111111",
                'steps': [
                    {'range': [0, 20], 'color': '#331111'},     # Critical / Over-budget
                    {'range': [20, 40], 'color': '#222222'},    # Low retention
                    {'range': [40, 100], 'color': '#052211'}    # Balanced / High savings
                ],
            }
        ))
        fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # Automated Smart Advisor Alert Matrix
    st.subheader(":material/notifications_active: Automated Guardrail Alerts")
    if actual_wants > target_wants:
        st.error(f"**Budget Overrun:** Your lifestyle desires ('Wants') exceed the recommended 30% threshold by **{currency_symbol}{actual_wants - target_wants:,.2f}**. Consider scaling down non-essential orders.", icon=":material/warning:")
    if total_savings >= target_savings_total:
        st.success(f"**Optimization Target Met:** High performance! You have saved or invested {currency_symbol}{total_savings:,.2f}, hitting your 20% savings objective.", icon=":material/stars")
    else:
        st.warning(f"**Savings deficit:** You are **{currency_symbol}{target_savings_total - total_savings:,.2f}** behind the 20% optimum wealth creation milestone.", icon=":material/trending_down:")

    st.markdown("---")

    # Row 2: Charts & Visualizations
    st.subheader(":material/analytics: Visualizations Matrix")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("#### Target Matrix vs. Actual Performance")
        categories = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name='Target Matrix', x=categories, y=[target_needs, target_wants, target_savings_total], marker_color='#E6F0FF'))
        fig_compare.add_trace(go.Bar(name='Your Outflows', x=categories, y=[actual_needs, actual_wants, total_savings], marker_color='#0052CC'))
        fig_compare.update_layout(barmode='group', height=300, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#FFFFFF"))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        st.write("#### Resource Distribution Matrix")
        combined_outflows = pd.concat([df_exp, df_sav], ignore_index=True) if (not df_exp.empty or not df_sav.empty) else pd.DataFrame()
        if not combined_outflows.empty:
            bw_blue_sequence = ['#001F3F', '#0052CC', '#4C9AFF', '#B3D4FF', '#E6F0FF']
            fig_donut = px.pie(combined_outflows, values='Amount', names='Category', hole=0.4, color_discrete_sequence=bw_blue_sequence)
            fig_donut.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#FFFFFF"))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("Awaiting outflows data mapping.")

    # Row 3: Financial Suggestions 
    st.markdown("---")
    st.subheader(":material/account_balance_wallet: Strategic Optimization Metrics")
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.info(f"**High-Yield Cash Return:** `{HYSA_RATE*100:.2f}% APY` \n\nSecure foundation for your rainy-day reserves.", icon=":material/account_balance:")
    with sub_col2:
        st.success(f"**Market Wealth Multiplier:** `{MARKET_RATE*100:.2f}% CAGR` \n\nTarget long-term inflation-beating portfolios.", icon=":material/trending_up:")

    st.markdown(f"**Target Allocations Based on Matrix Calculations:**")
    
    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        st.markdown(f"### :material/shield: Cash Safety Net: **{currency_symbol}{suggested_cash_savings:,.2f}**")
        st.markdown(f"Projected 1-Year Baseline Interest: `+{currency_symbol}{suggested_cash_savings * HYSA_RATE:,.2f}`")
    with adv_col2:
        st.markdown(f"### :material/rocket_launch: Compound Investments: **{currency_symbol}{suggested_investments:,.2f}**")
        st.markdown(f"Projected 10-Year Compounded Matrix: `{currency_symbol}{suggested_investments * ((1 + MARKET_RATE)**10):,.2f}`")

    # Row 4: Ledgers & Exports
    st.markdown("---")
    ledger_header_col1, ledger_header_col2 = st.columns([5, 1])
    with ledger_header_col1:
        st.subheader(":material/table_chart: Itemized Statement Ledgers")
    
    with ledger_header_col2:
        if not combined_outflows.empty:
            csv_data = combined_outflows.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Ledger CSV",
                data=csv_data,
                file_name=f"financial_statement_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="secondary"
            )

    table_tabs = st.tabs(["Expense Statements", "Savings Assets", "Income Inflows"])
    with table_tabs[0]:
        if not df_exp.empty: st.dataframe(df_exp.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[1]:
        if not df_sav.empty: st.dataframe(df_sav.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[2]:
        if not df_inc.empty: st.dataframe(df_inc.sort_values(by="Date", ascending=False), use_container_width=True)
