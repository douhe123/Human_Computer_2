import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
from io import BytesIO
import calendar
import yfinance as yf
from sklearn.linear_model import LinearRegression

# CONFIGURATION 
st.set_page_config(
    page_title="Personal Finance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# dark and light mode (is not ready yet it dosen't work properly as it should)
def apply_custom_styling(dark_mode=False):
    """styling with dark/light mode"""
    if dark_mode:
        # Dark mode
        st.markdown("""
        <style>
            /*main styling */
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            .main {
                background-color: #0e1117;
                padding-top: 2rem;
            }
            
            /*metric cards */
            .metric-container {
                background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: #fafafa;
                text-align: center;
                margin-bottom: 1rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                border: 1px solid #374151;
            }
            
            /*sidebar */
            .css-1d391kg {
                background: #1f2937;
            }
            
            /*buttons */
            .stButton > button {
                background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
                color: #fafafa;
                border: 1px solid #6b7280;
            }
            
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode
        st.markdown("""
        <style>
            /*main styling */
            .stApp {
                background-color: #ffffff;
                color: #1f2937;
            }
            
            .main {
                background-color: #f8f9fa;
                padding-top: 2rem;
            }
            
            /* metric cards */
            .metric-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 1rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            /* sidebar */
            .css-1d391kg {
                background: #f8f9fa;
            }
            
            /* buttons */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
            }
            
        </style>
        """, unsafe_allow_html=True)
    
    # Common styles it's going to help me to improve time
    st.markdown("""
    <style>
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .stButton > button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: transform 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
    </style>
    """, unsafe_allow_html=True)

# session start
def initialize_session_state():
    """variables"""
    if "transactions" not in st.session_state:
        st.session_state.transactions = pd.DataFrame()
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "recurring" not in st.session_state:
        st.session_state.recurring = []
    if "show_tutorial" not in st.session_state:
        st.session_state.show_tutorial = True
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

initialize_session_state()

# current mode (light or dark)
apply_custom_styling(st.session_state.dark_mode)

# functions
@st.cache_data
def load_sample_data():
    """sample financial data"""
    np.random.seed(42)  # sample data generator
    
    # Create date for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Categorys and description for the data
    expense_categories = {
        "Food & Dining": ["Groceries", "Restaurant", "Coffee Shop", "Fast Food", "Delivery"],
        "Transportation": ["Gas", "Public Transit", "Uber/Lyft", "Parking", "Car Maintenance"],
        "Housing": ["Rent", "Utilities", "Internet", "Phone", "Home Supplies"],
        "Entertainment": ["Movies", "Streaming", "Games", "Concert", "Sports"],
        "Healthcare": ["Doctor Visit", "Pharmacy", "Gym Membership", "Dental"],
        "Shopping": ["Clothing", "Electronics", "Books", "Personal Care", "Gifts"]
    }
    
    income_sources = ["Salary", "Freelancing", "Investment Returns", "Side Hustle"]
    
    transactions = []
    
    for date in dates:
        # Generate aleatory transactions each day
        if np.random.random() < 0.7: # 70% chance of transaction
            num_transactions = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
            
            for _ in range(num_transactions):
                # 15% chance of income
                if np.random.random() < 0.15:
                    description = np.random.choice(income_sources)
                    category = "Income"
                    amount = round(np.random.uniform(500, 4000), 2)
                    trans_type = "Income"
                else:
                    category = np.random.choice(list(expense_categories.keys()))
                    description = np.random.choice(expense_categories[category])
                    amount = -round(np.random.uniform(5, 150), 2)
                    trans_type = "Expense"
                
                transactions.append({
                    "Date": date.strftime("%Y-%m-%d"),
                    "Description": description,
                    "Category": category,
                    "Amount": amount,
                    "Type": trans_type
                })
    
    return pd.DataFrame(transactions)

def fetch_exchange_rates(base_currency="USD"):
    """current exchange rates """
    try:
        # Using a free API as I was told
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json().get("rates", {})
    except:
        pass
    
    # Only if API fails
    return {
        "USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0, 
        "CAD": 1.25, "AUD": 1.35, "CHF": 0.92, "CNY": 6.45
    }

def fetch_stock_data(tickers):
    """stock prices and changes"""
    stock_data = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if len(hist) >= 2:
                current_price = hist["Close"].iloc[-1]
                previous_price = hist["Close"].iloc[-2]
                change = current_price - previous_price
                change_pct = (change / previous_price) * 100
                
                stock_data[ticker] = {
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                }
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {str(e)}")
    
    return stock_data

def create_custom_metric(label, value, delta=None, help_text=None):
    """metric card"""
    # Create and display a simple metric
    metric_html = f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """
    
    st.markdown(metric_html, unsafe_allow_html=True)
    
    # Show delta and help text for user frendly advice
    if delta:
        st.caption(f"📊 {delta}")
    if help_text:
        st.caption(f"ℹ️ {help_text}")

def generate_financial_report(df, currency):
    """Generate financial health report"""
    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expenses = abs(df[df["Amount"] < 0]["Amount"].sum())
    net_balance = total_income - total_expenses
    
    # Calculate key ratios
    savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
    
    # Get top expense categories
    top_expenses = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().abs().nlargest(3)
    
    report = f"""
    ## 📊 Financial Health Report
    
    ### Summary
    - **Total Income:** {total_income:,.2f} {currency}
    - **Total Expenses:** {total_expenses:,.2f} {currency}
    - **Net Balance:** {net_balance:,.2f} {currency}
    - **Savings Rate:** {savings_rate:.1f}%
    
    ### Top Expense Categories
    """
    
    for category, amount in top_expenses.items():
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        report += f"- **{category}:** {amount:,.2f} {currency} ({percentage:.1f}%)\n"
    
    # Recommendations
    report += "\n### 💡 Recommendations\n"
    
    if savings_rate < 10:
        report += "- Consider increasing your savings rate to at least 10-20% of income\n"
    elif savings_rate > 30:
        report += "- Excellent savings rate! Consider investing excess savings\n"
    
    if total_expenses > 0:
        largest_expense = top_expenses.index[0]
        report += f"- Review your **{largest_expense}** expenses for potential savings\n"
    
    return report

# Sidebar
with st.sidebar:
    st.title("⚙️ Dashboard Settings")
    
    # Dark Mode
    st.session_state.dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
        help="Switch between light and dark themes"
    )
    
    # Apply styling when mode changes (add this to the dashboard)
    apply_custom_styling(st.session_state.dark_mode)
    
    st.divider()
    
    # Tutorial
    if st.session_state.show_tutorial:
        st.info("""
        👋 **Welcome to your Finance Dashboard!**
        
        1. Upload your transaction data (CSV/Excel)
        2. Set your currency and budget
        3. Explore your financial insights
        4. Set financial goals and track progress
        5. Have a wonderful day :-)
        """)
        
        if st.button("Hide Tutorial :-("):
            st.session_state.show_tutorial = False
            st.rerun()
    
    st.divider()
    
    # Data Upload Section
    st.subheader("📁 Data Import")
    uploaded_file = st.file_uploader(
        "Upload Transaction Data", 
        type=["csv", "xlsx"],
        help="Upload a CSV or Excel file with columns: Date, Description, Category, Amount"
    )
    
    if st.button("Use Sample Data"):
        st.session_state.transactions = load_sample_data()
        st.success("Sample data loaded!")
        st.rerun()
    
    st.divider()
    
    # Financial Settings
    st.subheader("💱 Financial Settings")
    currency = st.selectbox(
        "Currency", 
        ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"],
        help="Select your preferred currency"
    )
    
    monthly_budget = st.number_input(
        "Monthly Budget", 
        min_value=0, 
        value=3000,
        help="Set your monthly spending budget"
    )
    
    st.divider()
    
    # Investment Tracking
    st.subheader("📈 Investment Tracking")
    default_tickers = "AAPL,MSFT,GOOGL,TSLA"
    investment_tickers = st.text_input(
        "Stock Tickers", 
        value=default_tickers,
        help="Enter stock symbols separated by commas"
    )

# dashboard
st.title("💰 Personal Finance Dashboard")

# Load and process data
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # validate this require colummns
        required_cols = ["Date", "Amount"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            st.stop()
        
        st.success(f"Successfully loaded {len(df)} transactions!")
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        df = load_sample_data()
else:
    df = st.session_state.transactions
    if df.empty:
        df = load_sample_data()
        st.info("📊 Showing sample data. Upload your own data to get started!")

# Area for dta preprocessing
if not df.empty:
    # date column
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Add Type column
    if "Type" not in df.columns:
        df["Type"] = df["Amount"].apply(lambda x: "Income" if x > 0 else "Expense")
    
    # Add Category 
    if "Category" not in df.columns:
        df["Category"] = df["Type"]
    
    # Apply currency conversion (not working?)
    if currency != "USD":
        rates = fetch_exchange_rates()
        conversion_rate = rates.get(currency, 1)
        df["Amount"] = df["Amount"] * conversion_rate

# Overview
if not df.empty:
    st.subheader("📊 Financial Overview")
    
    # Calculate key metrics
    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expenses = abs(df[df["Amount"] < 0]["Amount"].sum())
    net_balance = total_income - total_expenses
    avg_monthly_expense = total_expenses / 12 if total_expenses > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_custom_metric(
            "Total Income", 
            f"{total_income:,.0f} {currency}",
            help_text="All income in the selected period"
        )
    
    with col2:
        create_custom_metric(
            "Total Expenses", 
            f"{total_expenses:,.0f} {currency}",
            help_text="All expenses in the selected period"
        )
    
    with col3:
        delta_color = "🟢" if net_balance >= 0 else "🔴"
        create_custom_metric(
            "Net Balance", 
            f"{net_balance:,.0f} {currency}",
            delta=f"{delta_color} {'Profit' if net_balance >= 0 else 'Loss'}"
        )
    
    with col4:
        create_custom_metric(
            "Avg Monthly Expense", 
            f"{avg_monthly_expense:,.0f} {currency}",
            help_text="Average monthly spending"
        )
    
    # Budget progress
    if monthly_budget > 0:
        st.subheader("🎯 Budget Progress")
        budget_used = min(avg_monthly_expense / monthly_budget, 1.0)
        budget_pct = budget_used * 100
        
        # progress bar
        progress_col1, progress_col2 = st.columns([3, 1])
        
        with progress_col1:
            st.progress(budget_used)
            
        with progress_col2:
            status = "🔴 Over Budget" if budget_pct > 100 else "🟡 Close to Budget" if budget_pct > 80 else "🟢 On Track"
            st.metric("Budget Used", f"{budget_pct:.1f}%", delta=status)
    
    # show to the costummer
    st.subheader("📈 Financial Analysis")
    
    #Tabs for different views (easy to comprenhend for the user)
    tab1, tab2, tab3, tab4 = st.tabs(["💸 Spending Analysis", "📊 Income vs Expenses", "📅 Monthly Trends", "🎯 Category Breakdown"])
    
    with tab1:
        if not df[df["Amount"] < 0].empty:
            # Spending by category
            spending_by_category = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().abs()
            
            fig = px.pie(
                values=spending_by_category.values,
                names=spending_by_category.index,
                title="Spending Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Monthly income vs expenses
        monthly_data = df.groupby([pd.Grouper(key='Date', freq='M'), 'Type'])['Amount'].sum().unstack(fill_value=0)
        monthly_data['Expense'] = monthly_data['Expense'].abs()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_data.index.strftime('%Y-%m'),
            y=monthly_data.get('Income', 0),
            name='Income',
            marker_color='lightgreen'
        ))
        fig.add_trace(go.Bar(
            x=monthly_data.index.strftime('%Y-%m'),
            y=monthly_data.get('Expense', 0),
            name='Expenses',
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title="Monthly Income vs Expenses",
            xaxis_title="Month",
            yaxis_title=f"Amount ({currency})",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Net balance trend
        monthly_net = df.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].sum()
        
        fig = px.line(
            x=monthly_net.index,
            y=monthly_net.values,
            title="Monthly Net Balance Trend",
            labels={'x': 'Month', 'y': f'Net Balance ({currency})'}
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Top spending categories
        top_categories = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().abs().nlargest(10)
        
        fig = px.bar(
            x=top_categories.values,
            y=top_categories.index,
            orientation='h',
            title="Top 10 Spending Categories",
            labels={'x': f'Amount ({currency})', 'y': 'Category'}
        )
        fig.update_traces(marker_color='lightblue')
        st.plotly_chart(fig, use_container_width=True)
    
    # tracking investment cool feature but not easy to implement
    if investment_tickers.strip():
        st.subheader("📈 Investment Portfolio")
        
        tickers = [t.strip().upper() for t in investment_tickers.split(",")]
        stock_data = fetch_stock_data(tickers)
        
        if stock_data:
            inv_cols = st.columns(min(len(stock_data), 4))
            
            for i, (ticker, data) in enumerate(stock_data.items()):
                col_idx = i % 4
                with inv_cols[col_idx]:
                    change_color = "🟢" if data["change"] >= 0 else "🔴"
                    st.metric(
                        ticker,
                        f"${data['price']:.2f}",
                        delta=f"{change_color} {data['change']:+.2f} ({data['change_pct']:+.2f}%)"
                    )
    
    # table
    st.subheader("💼 Recent Transactions")
    
    # filters
    with st.expander("🔍 Filter Transactions"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            date_filter = st.date_input(
                "Date Range",
                value=[df["Date"].min().date(), df["Date"].max().date()],
                key="transaction_date_filter"
            )
        
        with filter_col2:
            category_filter = st.multiselect(
                "Categories",
                options=sorted(df["Category"].unique()),
                default=sorted(df["Category"].unique()),
                key="transaction_category_filter"
            )
        
        with filter_col3:
            type_filter = st.multiselect(
                "Transaction Type",
                options=["Income", "Expense"],
                default=["Income", "Expense"],
                key="transaction_type_filter"
            )
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_filter) == 2:
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= date_filter[0]) & 
            (filtered_df["Date"].dt.date <= date_filter[1])
        ]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
    
    if type_filter:
        filtered_df = filtered_df[filtered_df["Type"].isin(type_filter)]
    
    # show filtered
    display_df = filtered_df.sort_values("Date", ascending=False).head(100)
    
    display_df_formatted = display_df.copy()
    display_df_formatted["Date"] = display_df_formatted["Date"].dt.strftime("%Y-%m-%d")
    display_df_formatted["Amount"] = display_df_formatted["Amount"].apply(
        lambda x: f"{x:,.2f} {currency}"
    )
    
    st.dataframe(
        display_df_formatted[["Date", "Description", "Category", "Type", "Amount"]],
        use_container_width=True,
        hide_index=True
    )
    
    # Exports
    st.subheader("📤 Export & Reports")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📊 Generate Financial Report"):
            report = generate_financial_report(df, currency)
            st.markdown(report)
    
    with export_col2:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with export_col3:
        if st.button("📧 Email Report"):
            st.info("Email functionality would be implemented here not ready yet")

else:
    st.warning("No transaction data available. Please upload a file or use sample data.")

# --- FOOTER --- Need help is a future implementation
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    Built this with Streamlit: Douglas Colina| 
    <a href="#" style="color: #667eea;">Need Help?</a>
</div>
""", unsafe_allow_html=True)