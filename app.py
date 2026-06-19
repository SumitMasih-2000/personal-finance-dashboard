import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw

# 1. Page Configuration & Custom Theme Overrides
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# Custom CSS to transition away from default light grey backgrounds
# Custom CSS to transition away from default light grey backgrounds and enforce pure white text
st.markdown("""
    <style>
        /* Main App Background and base text */
        .stApp {
            background-color: #0E131F;
            color: #FFFFFF !important;
        }
        /* Enforce header and standard markdown text color tags */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: #FFFFFF !important;
        }
        /* Sidebar container adjustment */
        section[data-testid="stSidebar"] {
            background-color: #151C2C !important;
        }
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #FFFFFF !important;
        }
        /* Highlight value metrics beautifully */
        div[data-testid="stMetricValue"] {
            color: #4C9AFF !important;
            font-weight: bold;
        }
        /* Style expanding input forms nicely */
        .stExpander {
            background-color: #1A233A !important;
            border: 1px solid #2D3748 !important;
        }
    </style>
""", unsafe_allow_html=True)
# Helper function to generate a backup logo if the file is missing
def get_dashboard_logo():
    img_path = "financial_advisor.png"
    if os.path.exists(img_path):
        try:
            return Image.open(img_path)
        except Exception:
            pass
    
    img = Image.new("RGB", (200, 200), color="#0F172A") 
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 40, 160, 160], fill="#0052CC") 
    draw.rectangle([70, 90, 90, 140], fill="#FFFFFF") 
    draw.rectangle([100, 70, 120, 140], fill="#E6F0FF") 
    return img

# Initialize session state structures
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []
if "financial_goals" not in st.session_state:
    # Seed default baseline goals
    st.session_state["financial_goals"] = [
        {"Goal Name": "Emergency Safety Net", "Target": 5000.0, "Current": 1200.0},
        {"Goal Name": "Wealth Investment Milestone", "Target": 25000.0, "Current": 4500.0}
    ]

# 2. Sidebar Settings & Forms

# VERTICAL ACCENT 1: Global Settings
st.sidebar.markdown(
    """
    <div style="border-left: 5px solid #0052CC; padding-left: 10px; margin-bottom: 15px;">
        <h3 style="margin:0; padding:0; font-size: 1.15rem; color: #FFFFFF;">🌍 Global Settings</h3>
    </div>
    """, 
    unsafe_allow_html=True
)
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)

HYSA_RATE = 0.0425  
MARKET_RATE = 0.090  

st.sidebar.markdown("---")

# VERTICAL ACCENT 2: Add New Records
st.sidebar.markdown(
    """
    <div style="border-left: 5px solid #0052CC; padding-left: 10px; margin-bottom: 15px;">
        <h3 style="margin:0; padding:0; font-size: 1.15rem; color: #FFFFFF;">📝 Operational Ledger</h3>
    </div>
    """, 
    unsafe_allow_html=True
)

# FORM A: INCOME
with st.sidebar.expander("Add Income Source", expanded=False):
    with st.form("income_form", clear_on_submit=True):
        st.markdown("#### :material/input: Log Income")
        inc_date = st.date_input("Date Received", value=datetime.today(), key="inc_date")
        inc_desc = st.text_input("Source", placeholder="e.g., Monthly Salary")
        inc_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        is_recurring_inc = st.checkbox("Recurring Monthly Cycle")
        if st.form_submit_button("Add Income") and inc_amt > 0:
            st.session_state["income_records"].append({
                "Date": pd.to_datetime(inc_date), "Description": inc_desc, 
                "Amount": inc_amt, "Type": "Recurring" if is_recurring_inc else "One-Time"
            })
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
        is_recurring_exp = st.checkbox("Recurring Monthly Cycle")
        if st.form_submit_button("Add Expense") and exp_amt > 0:
            st.session_state["expense_records"].append({
                "Date": pd.to_datetime(exp_date), "Description": exp_desc, 
                "Category": exp_cat, "Budget Type": exp_type, "Amount": exp_amt,
                "Type": "Recurring" if is_recurring_exp else "One-Time"
            })
            st.toast("Expense added successfully!", icon=":material/check_circle:")

# FORM C: SAVINGS & INVESTMENTS
with st.sidebar.expander("Add Savings/Investment", expanded=False):
    with st.form("savings_form", clear_on_submit=True):
        st.markdown("#### :material/savings: Log Savings")
        sav_date = st.date_input("Date Saved", value=datetime.today(), key="sav_date")
        sav_desc = st.text_input("Goal/Fund Name", placeholder="e.g., Index Fund")
        sav_cat = st.selectbox("Type", ["HYSA/Cash Savings", "Stock Market/ETF", "Insurance/Retirement"])
        sav_amt = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add Savings") and sav_amt > 0:
            st.session_state["saving_records"].append({
                "Date": pd.to_datetime(sav_date), "Description": sav_desc, 
                "Category": sav_cat, "Budget Type": "Savings", "Amount": sav_amt
            })
            st.toast("Savings recorded!", icon=":material/check_circle:")

# FORM D: GOAL SETTER
with st.sidebar.expander("🎯 Define Milestone Goals", expanded=False):
    with st.form("goal_form", clear_on_submit=True):
        goal_name = st.text_input("Goal Name", placeholder="e.g., House Downpayment")
        goal_target = st.number_input("Target Amount Target", min_value=1.0, value=1000.0)
        goal_initial = st.number_input("Currently Saved Allocation", min_value=0.0, value=0.0)
        if st.form_submit_button("Create Goal"):
            st.session_state["financial_goals"].append({"Goal Name": goal_name, "Target": goal_target, "Current": goal_initial})
            st.toast("New Objective Initialized!")

# RESET SYSTEM
st.sidebar.markdown("---")
st.sidebar.header(":material/settings:")
if st.sidebar.button("Reset Dashboard Data", type="primary"):
    st.session_state.clear()
    st.toast("All data reset!")
    st.rerun()

# 3. Data Processing Engines
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

if total_income > 0:
    retention_rate = ((total_savings + max(0.0, remaining_cash)) / total_income) * 100
    health_score = min(100.0, max(0.0, retention_rate))
else:
    health_score = 0.0

logo_image = get_dashboard_logo()

# 4. Dashboard Main View Layout
if total_income == 0:
    welcome_col1, welcome_col2 = st.columns([1, 6])
    with welcome_col1:
        st.image(logo_image, use_container_width=True)
    with welcome_col2:
        st.title("Smart Personal Finance Hub")
        st.info("Welcome! Please log an **Income Source** in the sidebar to populate your financial engine dashboard.", icon=":material/info:")
else:
    title_col1, title_col2 = st.columns([1, 6]) 
    with title_col1:
        st.image(logo_image, use_container_width=True) 
    with title_col2:
        st.title("Smart Personal Finance Hub")
        st.markdown("### *Active Wealth Optimization & Forward Projections*")
    
    st.markdown("---")
    
    # Row 1: Status Cards & Gauge Visualizer
    kpi_col1, kpi_col2 = st.columns([3, 1])
    
    with kpi_col1:
        st.subheader(":material/grid_view: Financial Liquidity Cards")
        metric_sub_col1, metric_sub_col2 = st.columns(2)
        metric_sub_col1.metric("Total Income Inflow", f"{currency_symbol}{total_income:,.2f}")
        metric_sub_col1.metric("Total Expenses Outflow", f"{currency_symbol}{total_expenses:,.2f}")
        metric_sub_col2.metric("Total Capital Saved", f"{currency_symbol}{total_savings:,.2f}")
        metric_sub_col2.metric("Available Liquidity", f"{currency_symbol}{remaining_cash:,.2f}")
        
    with kpi_col2:
        st.markdown("<h4 style='text-align: center; margin-bottom: -10px;'>Health Score Matrix</h4>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#E2E8F0"},
                'bar': {'color': "#0052CC"},
                'bgcolor': "#1A233A",
                'steps': [
                    {'range': [0, 20], 'color': '#4A151B'},     
                    {'range': [20, 50], 'color': '#2C3E50'},    
                    {'range': [50, 100], 'color': '#114B3E'}    
                ],
            }
        ))
        fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # FEATURE A: Dynamic Goals Ledger
    st.subheader("🎯 Active Milestone Goals Progression Tracker")
    goal_cols = st.columns(len(st.session_state["financial_goals"]))
    for idx, goal in enumerate(st.session_state["financial_goals"]):
        with goal_cols[idx % len(goal_cols)]:
            # Dynamic matching optimization
            if total_savings > 0 and idx == 0:
                # Add real ledger additions incrementally to goal one
                current_allocation = goal["Current"] + total_savings
            else:
                current_allocation = goal["Current"]
                
            progress_pct = min(1.0, current_allocation / goal["Target"])
            st.markdown(f"**{goal['Goal Name']}**")
            st.progress(progress_pct)
            st.caption(f"{currency_symbol}{current_allocation:,.2f} of {currency_symbol}{goal['Target']:,.2f} ({progress_pct*100:.1f}%)")

    st.markdown("---")

    # Visualizations Matrix & Dynamic Forecasting
    st.subheader(":material/analytics: Analytical Matrix Models")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("#### Budget Allocations vs. Outflows")
        categories = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name='Target Target Matrix', x=categories, y=[target_needs, target_wants, target_savings_total], marker_color='#1E293B'))
        fig_compare.add_trace(go.Bar(name='Actual Activity', x=categories, y=[actual_needs, actual_wants, total_savings], marker_color='#0052CC'))
        fig_compare.update_layout(barmode='group', height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E2E8F0"))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        # FEATURE B: Predictive Modeling Visualization
        st.write("#### 12-Month Predictive Net Worth Forward Projection")
        months = [datetime.today().strftime('%b %y')]
        projected_wealth = [remaining_cash + total_savings]
        
        # Calculate velocity trend metrics
        monthly_velocity = total_income - total_expenses
        
        for m in range(1, 13):
            future_date = datetime.today() + timedelta(days=30 * m)
            months.append(future_date.strftime('%b %y'))
            # Factor compound growth interest metrics dynamically over 12 months
            compounded_step = (projected_wealth[-1] + monthly_velocity) * (1 + (MARKET_RATE / 12))
            projected_wealth.append(compounded_step)
            
        fig_trend = px.line(x=months, y=projected_wealth, markers=True, labels={'x': 'Timeline Horizon', 'y': 'Capital Base'})
        fig_trend.update_traces(line_color='#4C9AFF', fill='tozeroy', fillcolor='rgba(76, 154, 255, 0.1)')
        fig_trend.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E2E8F0"))
        st.plotly_chart(fig_trend, use_container_width=True)

    # Statements Ledger Breakdown
    st.markdown("---")
    st.subheader(":material/table_chart: Itemized Statement Ledgers")
    
    table_tabs = st.tabs(["Expense Inflow Statements", "Savings Assets", "Income Inflows"])
    with table_tabs[0]:
        if not df_exp.empty: st.dataframe(df_exp.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[1]:
        if not df_sav.empty: st.dataframe(df_sav.sort_values(by="Date", ascending=False), use_container_width=True)
    with table_tabs[2]:
        if not df_inc.empty: st.dataframe(df_inc.sort_values(by="Date", ascending=False), use_container_width=True)
