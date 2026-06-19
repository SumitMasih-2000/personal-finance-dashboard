import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw

# 1. Page Configuration & Custom Theme Overrides
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0E131F; color: #FFFFFF !important; }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #FFFFFF !important; }
        section[data-testid="stSidebar"] { background-color: #151C2C !important; }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label { color: #FFFFFF !important; }
        div[data-testid="stMetricValue"] { color: #4C9AFF !important; font-weight: bold; }
        .stExpander { background-color: #1A233A !important; border: 1px solid #2D3748 !important; }
    </style>
""", unsafe_allow_html=True)

# File Paths for Local CSV Persistence
INC_FILE = "ledger_income.csv"
EXP_FILE = "ledger_expenses.csv"
SAV_FILE = "ledger_savings.csv"

# Helper to load persistent local records safely
def load_local_ledger(file_path, column_schema):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                return df
        except Exception:
            pass
    return pd.DataFrame(columns=column_schema)

# Data Schema configurations
income_columns = ["Date", "Description", "Account", "Amount", "Type"]
expense_columns = ["Date", "Description", "Category", "Budget Type", "Account", "Amount", "Type"]
savings_columns = ["Date", "Description", "Category", "Account", "Budget Type", "Amount"]

# Initializing Session State with Data from local files instead of memory lists
if "income_df" not in st.session_state:
    st.session_state["income_df"] = load_local_ledger(INC_FILE, income_columns)
if "expense_df" not in st.session_state:
    st.session_state["expense_df"] = load_local_ledger(EXP_FILE, expense_columns)
if "saving_df" not in st.session_state:
    st.session_state["saving_df"] = load_local_ledger(SAV_FILE, savings_columns)

if "financial_goals" not in st.session_state:
    st.session_state["financial_goals"] = [
        {"Goal Name": "Emergency Safety Net", "Target": 5000.0, "Current": 1200.0},
        {"Goal Name": "Wealth Investment Milestone", "Target": 25000.0, "Current": 4500.0}
    ]

def save_ledger_to_disk(df, file_path):
    df.to_csv(file_path, index=False)

def get_dashboard_logo():
    img_path = "financial_advisor.png"
    if os.path.exists(img_path):
        try: return Image.open(img_path)
        except Exception: pass
    img = Image.new("RGB", (200, 200), color="#0F172A") 
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 40, 160, 160], fill="#0052CC") 
    draw.rectangle([70, 90, 90, 140], fill="#FFFFFF") 
    draw.rectangle([100, 70, 120, 140], fill="#E6F0FF") 
    return img

# 2. Sidebar Setup & Transaction Inputs
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)
account_options = ["Checking Account", "Savings Vault", "Cash Wallet", "Credit Card"]

HYSA_RATE, MARKET_RATE = 0.0425, 0.090  
st.sidebar.markdown("---")

st.sidebar.markdown(
    """<div style="border-left: 5px solid #0052CC; padding-left: 10px; margin-bottom: 15px;">
        <h3 style="margin:0; padding:0; font-size: 1.15rem; color: #FFFFFF;">Operational Ledger</h3>
    </div>""", unsafe_allow_html=True
)

# FORM A: INCOME
with st.sidebar.expander("Add Income Source", expanded=False):
    with st.form("income_form", clear_on_submit=True):
        st.markdown("#### Log Income")
        inc_date = st.date_input("Date Received", value=datetime.today(), key="inc_date")
        inc_desc = st.text_input("Source", placeholder="e.g., Salary")
        inc_acc = st.selectbox("Destination Account", account_options, key="inc_acc")
        inc_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        is_recurring_inc = st.checkbox("Recurring Monthly Cycle")
        if st.form_submit_button("Add Income") and inc_amt > 0:
            new_row = pd.DataFrame([{
                "Date": pd.to_datetime(inc_date), "Description": inc_desc, "Account": inc_acc,
                "Amount": inc_amt, "Type": "Recurring" if is_recurring_inc else "One-Time"
            }])
            st.session_state["income_df"] = pd.concat([st.session_state["income_df"], new_row], ignore_index=True)
            save_ledger_to_disk(st.session_state["income_df"], INC_FILE)
            st.toast("Income saved securely to database!")
            st.rerun()

# FORM B: EXPENSE
with st.sidebar.expander("Add Expense", expanded=False):
    with st.form("expense_form", clear_on_submit=True):
        st.markdown("#### Log Expense")
        exp_date = st.date_input("Date Paid", value=datetime.today(), key="exp_date")
        exp_desc = st.text_input("Item", placeholder="e.g., Groceries")
        exp_cat = st.selectbox("Category", ["Housing", "Food", "Utilities", "Entertainment", "Transport", "Health", "Other"])
        exp_type = st.selectbox("Budget Type", ["Needs", "Wants"])
        exp_acc = st.selectbox("Source Account", account_options, key="exp_acc")
        exp_amt = st.number_input("Amount", min_value=0.0, step=5.0, format="%.2f")
        is_recurring_exp = st.checkbox("Recurring Monthly Cycle")
        if st.form_submit_button("Add Expense") and exp_amt > 0:
            new_row = pd.DataFrame([{
                "Date": pd.to_datetime(exp_date), "Description": exp_desc, "Category": exp_cat, 
                "Budget Type": exp_type, "Account": exp_acc, "Amount": exp_amt, "Type": "Recurring" if is_recurring_exp else "One-Time"
            }])
            st.session_state["expense_df"] = pd.concat([st.session_state["expense_df"], new_row], ignore_index=True)
            save_ledger_to_disk(st.session_state["expense_df"], EXP_FILE)
            st.toast("Expense saved securely to database!")
            st.rerun()

# FORM C: SAVINGS
with st.sidebar.expander("Add Savings/Investment", expanded=False):
    with st.form("savings_form", clear_on_submit=True):
        st.markdown("#### Log Savings")
        sav_date = st.date_input("Date Saved", value=datetime.today(), key="sav_date")
        sav_desc = st.text_input("Goal Name", placeholder="e.g., ETF Index")
        sav_cat = st.selectbox("Asset Type", ["HYSA/Cash Savings", "Stock Market/ETF", "Insurance/Retirement"])
        sav_acc = st.selectbox("Staging Account", account_options, key="sav_acc")
        sav_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Savings") and sav_amt > 0:
            new_row = pd.DataFrame([{
                "Date": pd.to_datetime(sav_date), "Description": sav_desc, "Category": sav_cat, 
                "Account": sav_acc, "Budget Type": "Savings", "Amount": sav_amt
            }])
            st.session_state["saving_df"] = pd.concat([st.session_state["saving_df"], new_row], ignore_index=True)
            save_ledger_to_disk(st.session_state["saving_df"], SAV_FILE)
            st.toast("Savings updated securely!")
            st.rerun()

# SYSTEM RESET
st.sidebar.markdown("---")
if st.sidebar.button("Reset Dashboard Data", type="primary"):
    for f in [INC_FILE, EXP_FILE, SAV_FILE]:
        if os.path.exists(f): os.remove(f)
    st.session_state.clear()
    st.toast("Database tables cleared!")
    st.rerun()

# 3. Calculations & Month-Over-Month Performance Matrix Engine
df_inc, df_exp, df_sav = st.session_state["income_df"], st.session_state["expense_df"], st.session_state["saving_df"]

total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
total_savings = df_sav["Amount"].sum() if not df_sav.empty else 0.0
remaining_cash = total_income - total_expenses - total_savings

# Extract time frames to construct baseline delta changes (Current Month vs Previous)
today = datetime.today()
this_month_start = pd.to_datetime(today.replace(day=1, hour=0, minute=0, second=0))
prev_month_start = pd.to_datetime((this_month_start - timedelta(days=1)).replace(day=1))

def get_monthly_sum(df, start_date, end_date):
    if df.empty: return 0.0
    mask = (df["Date"] >= start_date) & (df["Date"] < end_date)
    return df.loc[mask, "Amount"].sum()

cur_inc = get_monthly_sum(df_inc, this_month_start, today + timedelta(days=1))
prev_inc = get_monthly_sum(df_inc, prev_month_start, this_month_start)
inc_delta = cur_inc - prev_inc

cur_exp = get_monthly_sum(df_exp, this_month_start, today + timedelta(days=1))
prev_exp = get_monthly_sum(df_exp, prev_month_start, this_month_start)
exp_delta = cur_exp - prev_exp

target_needs, target_wants, target_savings_total = total_income * 0.50, total_income * 0.30, total_income * 0.20
actual_needs = df_exp[df_exp["Budget Type"] == "Needs"]["Amount"].sum() if not df_exp.empty else 0.0
actual_wants = df_exp[df_exp["Budget Type"] == "Wants"]["Amount"].sum() if not df_exp.empty else 0.0

health_score = min(100.0, max(0.0, ((total_savings + max(0.0, remaining_cash)) / total_income) * 100)) if total_income > 0 else 0.0
logo_image = get_dashboard_logo()

# 4. View Presentation Layer
title_col1, title_col2 = st.columns([1, 6]) 
with title_col1: st.image(logo_image, use_container_width=True) 
with title_col2:
    st.title("Smart Personal Finance Hub")
    st.markdown("### *Active Wealth Optimization & Persistent Local Database*")

if total_income == 0:
    st.info("Welcome! Database data records look empty. Log financial events in the sidebar panel to see automated updates.")

st.markdown("---")

# Row 1: Advanced Metric Cards & Health Gauges
kpi_col1, kpi_col2 = st.columns([3, 1])
with kpi_col1:
    st.subheader("Financial Liquidity Cards")
    m_sub1, m_sub2 = st.columns(2)
    m_sub1.metric("Income", f"{currency_symbol}{total_income:,.2f}", f"{currency_symbol}{inc_delta:+.2f} vs last month")
    m_sub1.metric("Expense", f"{currency_symbol}{total_expenses:,.2f}", f"{currency_symbol}{exp_delta:+.2f} vs last month", delta_color="inverse")
    m_sub2.metric("Saving", f"{currency_symbol}{total_savings:,.2f}")
    m_sub2.metric("Available Balance", f"{currency_symbol}{remaining_cash:,.2f}")
    
with kpi_col2:
    st.markdown("<h4 style='text-align: center; margin-bottom: -10px;'>Health Score Matrix</h4>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = health_score, domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#E2E8F0"}, 'bar': {'color': "#0052CC"}, 'bgcolor': "#1A233A",
            'steps': [{'range': [0, 20], 'color': '#4A151B'}, {'range': [20, 50], 'color': '#2C3E50'}, {'range': [50, 100], 'color': '#114B3E'}]
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# Multi-Account Allocation Split View Mini-Table
st.subheader("Liquidity Allocation by Financial Account")
acc_breakdowns = []
for acc in account_options:
    acc_inc = df_inc[df_inc["Account"] == acc]["Amount"].sum() if not df_inc.empty else 0.0
    acc_exp = df_exp[df_exp["Account"] == acc]["Amount"].sum() if not df_exp.empty else 0.0
    acc_sav = df_sav[df_sav["Account"] == acc]["Amount"].sum() if not df_sav.empty else 0.0
    acc_breakdowns.append({"Financial Destination/Account": acc, "Net Held Liquidity": f"{currency_symbol}{(acc_inc - acc_exp - acc_sav):,.2f}"})
st.table(pd.DataFrame(acc_breakdowns))

st.markdown("---")

st.subheader("Active Milestone Goals Progression Tracker")
goal_cols = st.columns(len(st.session_state["financial_goals"]))
for idx, goal in enumerate(st.session_state["financial_goals"]):
    with goal_cols[idx % len(goal_cols)]:
        current_allocation = goal["Current"] + total_savings if (total_savings > 0 and idx == 0) else goal["Current"]
        progress_pct = min(1.0, current_allocation / goal["Target"])
        st.markdown(f"**{goal['Goal Name']}**")
        st.progress(progress_pct)
        st.caption(f"{currency_symbol}{current_allocation:,.2f} of {currency_symbol}{goal['Target']:,.2f} ({progress_pct*100:.1f}%)")

st.markdown("---")

# Row 3: Data Charts & Forward Forecasting Projections
st.subheader("Analytical Matrix Models")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("#### Budget Allocations vs. Outflows")
    categories = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(name='Target Matrix', x=categories, y=[target_needs, target_wants, target_savings_total], marker_color='#1E293B'))
    fig_compare.add_trace(go.Bar(name='Actual Activity', x=categories, y=[actual_needs, actual_wants, total_savings], marker_color='#0052CC'))
    fig_compare.update_layout(barmode='group', height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E2E8F0"))
    st.plotly_chart(fig_compare, use_container_width=True)
    
with chart_col2:
    st.write("#### 12-Month Predictive Net Worth Forward Projection")
    months, projected_wealth = [today.strftime('%b %y')], [remaining_cash + total_savings]
    monthly_velocity = total_income - total_expenses
    
    for m in range(1, 13):
        future_date = today + timedelta(days=30 * m)
        months.append(future_date.strftime('%b %y'))
        compounded_step = (projected_wealth[-1] + monthly_velocity) * (1 + (MARKET_RATE / 12))
        projected_wealth.append(compounded_step)
        
    fig_trend = px.line(x=months, y=projected_wealth, markers=True, labels={'x': 'Timeline Horizon', 'y': 'Capital Base'})
    fig_trend.update_traces(line_color='#4C9AFF', fill='tozeroy', fillcolor='rgba(76, 154, 255, 0.1)')
    fig_trend.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E2E8F0"))
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")
st.subheader("Itemized Statement Ledgers")

table_tabs = st.tabs(["Expense Inflow Statements", "Savings Assets", "Income Inflows"])
with table_tabs[0]:
    st.dataframe(df_exp.sort_values(by="Date", ascending=False) if not df_exp.empty else pd.DataFrame(columns=expense_columns), use_container_width=True)
with table_tabs[1]:
    st.dataframe(df_sav.sort_values(by="Date", ascending=False) if not df_sav.empty else pd.DataFrame(columns=savings_columns), use_container_width=True)
with table_tabs[2]:
    st.dataframe(df_inc.sort_values(by="Date", ascending=False) if not df_inc.empty else pd.DataFrame(columns=income_columns), use_container_width=True)
