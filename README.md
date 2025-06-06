# Personal Finance Dashboard

My proyect for Project 2 - UI/UX Design with Streamlit Douglas Colina

## Features

### Core Functionality
- **Transaction Analysis**: Track income and expenses with detailed categorization
- **Financial Overview**: Key metrics including total income, expenses, and net balance
- **Budget Tracking**: Compare spending against monthly budget goals
- **Visual Reporting**: Interactive charts for spending patterns and trends
- **Investment Tracking**: Monitor stock performance with real-time data


## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-finance-dashboard.git
   cd personal-finance-dashboard
   ```

2. Create and activate a virtual environment (as usual):
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Start the Streamlit server:
```bash
streamlit run app.py
```

The application will launch in your default browser at `http://localhost:8501`.

## Data Requirements

### Supported File Formats
- CSV
- Excel (xlsx)

### Required Columns
- `Date`: Transaction date (YYYY-MM-DD format)
- `Amount`: Transaction amount (positive for income, negative for expenses)
- `Description`: Transaction description (optional)
- `Category`: Transaction category (optional)

## Workflow

1. **Data Import**:
   - Upload your transaction data via the sidebar
   - Or use the built-in sample data for demonstration

2. **Configuration**:
   - Set your preferred currency
   - Define your monthly budget
   - Add stock tickers for investment tracking

3. **Analysis**:
   - View key financial metrics in the overview section
   - Explore interactive charts in the analysis tabs
   - Filter transactions by date, category, and type

4. **Reporting**:
   - Generate financial health reports
   - Export data as CSV
   - (Future) Email reports directly from the app

## File Structure

```
personal-finance-dashboard/
├── Personal_Finance.py   # Main application file
├── README.md             # This documentation
└── requirements.txt      # Python dependencies
```

## Dependencies

- streamlit
- pandas
- numpy
- requests
- plotly
- yfinance
- scikit-learn
- fpdf

## Future Enhancements

- User authentication
- Database integration for persistent storage
- Recurring transaction tracking
- Mobile app integration
- Advanced forecasting models