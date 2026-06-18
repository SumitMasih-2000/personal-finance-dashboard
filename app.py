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

# 3. Data Processing
df_inc = pd.DataFrame(st.session_state["income_records"])
df_exp = pd.DataFrame(st.session_state["expense_records"])
df_sav = pd.DataFrame(st.session_state["saving_records"])

total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
total_savings = df_sav["Amount"].sum() if not df_sav.empty else 0.0
remaining_cash = total_income - total_expenses - total_savings
