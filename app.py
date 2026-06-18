import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from PIL import Image, ImageDraw
# Import OpenAI for the chatbot integration
from openai import OpenAI

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

# Initialize session state lists for data if they don't exist
if "income_records" not in st.session_state:
    st.session_state["income_records"] = []
if "expense_records" not in st.session_state:
    st.session_state["expense_records"] = []
if "saving_records" not in st.session_state:
    st.session_state["saving_records"] = []

# Initialize Chat History for the Chatbot
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hello! I am your AI Financial Advisor. Ask me anything about your current income, expenses, savings goals, or general investing strategies."}
    ]

# 2. Sidebar Settings & Forms
st.sidebar.header(":material/public: Global Settings")
currency_symbol = st.sidebar.selectbox("Select Currency:", ["$", "₹", "€", "£", "¥"], index=0)

# Securely pull API Key from sidebar or environment variable
api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password", help="Needed to power the AI Advisor Chatbot")

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
    
    # Row 1: High Level Metrics
    st.subheader(":material/grid_view: Financial Status Cards")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Income", f"{currency_symbol}{total_income:,.2f}")
    kpi_col2.metric("Total Expenses", f"{currency_symbol}{total_expenses:,.2f}")
    kpi_col3.metric("Total Saved", f"{currency_symbol}{total_savings:,.2f}")
    kpi_col4.metric("Wallet Balance", f"{currency_symbol}{remaining_cash:,.2f}")

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
        fig_compare.update_layout(barmode='group', height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with chart_col2:
        st.write("#### Resource Distribution Matrix")
        combined_outflows = pd.concat([df_exp, df_sav], ignore_index=True) if (not df_exp.empty or not df_sav.empty) else pd.DataFrame()
        if not combined_outflows.empty:
            bw_blue_sequence = ['#000000', '#0052CC', '#4C9AFF', '#B3D4FF', '#E6F0FF']
            fig_donut = px.pie(combined_outflows, values='Amount', names='Category', hole=0.4, color_discrete_sequence=bw_blue_sequence)
            fig_donut.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("Awaiting outflows data mapping.")

    # Row 3: Chatbot Integration & Financial Suggestions Split Matrix
    st.markdown("---")
    
    bot_col1, bot_col2 = st.columns([1, 1])
    
    with bot_col1:
        st.subheader(":material/smart_toy: AI Financial Advisor Chatbot")
        
        if not api_key:
            st.warning("Please enter an OpenAI API Key in the sidebar settings to communicate with your AI Advisor.")
        else:
            # Display chat history container
            chat_container = st.container(height=320)
            with chat_container:
                for message in st.session_state["chat_history"]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # User Input Box
            if user_prompt := st.chat_input("Ask a question (e.g., 'Am I spending too much on Wants?')"):
                # Append user query
                st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(user_prompt)
                        
                # Formulate system instruction containing the exact real-time financial tracking numbers and return interest rates
system_instruction = f"""
You are an expert, highly analytical personal wealth optimization AI. 
Your purpose is to answer user queries comprehensively regarding income, expenses, savings strategies, and investment parameters.

Active Financial Ledger Values to Use in Calculations:
- Currency Base: {currency_symbol}
- Total Income Inflow: {currency_symbol}{total_income:,.2f}
- Current Expenses Outflow: {currency_symbol}{total_expenses:,.2f} (Needs: {currency_symbol}{actual_needs:,.2f} vs Target: {currency_symbol}{target_needs:,.2f} | Wants: {currency_symbol}{actual_wants:,.2f} vs Target: {currency_symbol}{target_wants:,.2f})
- Total Allocated Savings: {currency_symbol}{total_savings:,.2f} (Target allocation setup: {currency_symbol}{target_savings_total:,.2f})
- Free Wallet Cash Balance: {currency_symbol}{remaining_cash:,.2f}

Fixed Baseline Return Interest Rates:
1. High-Yield Cash Savings (HYSA): {HYSA_RATE*100:.2f}% APY
2. Market Equity / Index Fund Multiplier: {MARKET_RATE*100:.2f}% CAGR

Analytical Directives:
- If asked about savings or investments, project potential wealth creation out 1-year, 5-years, or 10-years using the active interest rates provided above.
- Provide actionable recommendations derived exactly from the data gaps between their Target Matrix allocations and Actual performance.
- Respond with extreme precision using bullet points and tables where appropriate. Keep it concise but deeply informative.
"""
                    # Prepare message list for API call
                    api_messages = [{"role": "system", "content": system_instruction}] + [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]
                    ]
                    
                    # Generate response
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=api_messages,
                        temperature=0.5
                    )
                    
                    bot_reply = response.choices[0].message.content
                    
                    # Append bot response
                    st.session_state["chat_history"].append({"role": "assistant", "content": bot_reply})
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(bot_reply)
                            
                except Exception as e:
                    st.error(f"Failed to communicate with AI: {str(e)}")

    with bot_col2:
        st.subheader(":material/account_balance_wallet: Strategic Optimization Metrics")
        
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.info(f"**High-Yield Cash Return:** `{HYSA_RATE*100:.2f}% APY` \n\nSecure foundation for your rainy-day reserves.", icon=":material/account_balance:")
        with sub_col2:
            st.success(f"**Market Wealth Multiplier:** `{MARKET_RATE*100:.2f}% CAGR` \n\nTarget long-term inflation-beating portfolios.", icon=":material/trending_up:")

        st.markdown(f"**Target Allocations Based on Matrix Calculations:**")
        st.markdown(f"### :material/shield: Cash Safety Net: **{currency_symbol}{suggested_cash_savings:,.2f}**")
        st.markdown(f"Projected 1-Year Baseline Interest: `+{currency_symbol}{suggested_cash_savings * HYSA_RATE:,.2f}`")
        
        st.markdown(f"### :material/rocket_launch: Compound Investments: **{currency_symbol}{suggested_investments:,.2f}**")
        st.markdown(f"Projected 10-Year Compounded Matrix: `{currency_symbol}{suggested_investments * ((1 + MARKET_RATE)**10):,.2f}`")

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
