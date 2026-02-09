# 📊 Investment Tracker Web Application

A full-stack investment portfolio tracking platform built with Python Flask, featuring real-time financial data integration, secure authentication, and comprehensive portfolio analytics.

## 🚀 Features

### Core Functionality
- **Portfolio Management**: Track stocks, ETFs, and cryptocurrencies
- **Real-time Data**: Live price updates via Yahoo Finance API
- **Performance Metrics**: Calculate profit/loss, returns, and asset allocation
- **Transaction History**: Complete audit trail of all buy/sell activities
- **Historical Charts**: 6-month price history visualization

### Technical Features
- **Secure Authentication**: Password hashing with Werkzeug
- **CRUD Operations**: Full create, read, update, delete functionality
- **Data Persistence**: SQLite database with proper indexing
- **CSV Import/Export**: Backup and transfer portfolio data
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Graceful degradation for API failures

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask 3.0
- **Database**: SQLite with SQL
- **API Integration**: Yahoo Finance (yfinance)
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualization**: Chart.js
- **Security**: Werkzeug password hashing, Flask sessions
- **Deployment**: Vercel-ready configuration

## 📁 Project Structure

```
investment-tracker/
├── app.py                 # Main Flask application
├── models.py              # Database models and initialization
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── vercel.json           # Vercel deployment config
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_investment.html
│   ├── edit_investment.html
│   ├── transactions.html
│   ├── history.html
│   ├── 404.html
│   └── 500.html
└── static/               # Static assets
    └── style.css
```

## 🏃‍♂️ Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/investment-tracker.git
   cd investment-tracker
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. **Initialize the database**
   ```bash
   python models.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## 📊 Database Schema

### Users Table
```sql
- id (INTEGER, PRIMARY KEY)
- username (TEXT, UNIQUE, NOT NULL)
- password (TEXT, NOT NULL)
- created_at (TIMESTAMP)
```

### Investments Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY)
- symbol (TEXT, NOT NULL)
- category (TEXT, NOT NULL)
- quantity (REAL, NOT NULL)
- buy_price (REAL, NOT NULL)
- purchase_date (TIMESTAMP)
```

### Transactions Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY)
- symbol (TEXT, NOT NULL)
- transaction_type (TEXT, NOT NULL)  -- 'BUY' or 'SELL'
- quantity (REAL, NOT NULL)
- price (REAL, NOT NULL)
- transaction_date (TIMESTAMP)
```

## 🔧 Usage

### Adding Investments
1. Navigate to "Add Investment"
2. Enter stock symbol (e.g., AAPL, TSLA, BTC-USD)
3. Specify category, quantity, and purchase price
4. Click "Add Investment"

### Viewing Portfolio
- Dashboard displays real-time portfolio value
- Color-coded profit/loss indicators
- Asset allocation pie chart
- Individual stock performance metrics

### Exporting Data
- Click "Export CSV" on dashboard
- Save portfolio data as CSV file
- Use for backup or analysis in Excel/Sheets

### Importing Data
- Click "Import CSV" on dashboard
- Select CSV file with columns: symbol, category, quantity, buy_price
- Data automatically imported to portfolio

## 🚀 Deployment

### Deploying to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Set environment variables in Vercel dashboard**
   - `SECRET_KEY`: Your Flask secret key

### Alternative: Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set config vars**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## 🔒 Security Features

- ✅ Password hashing (never stores plain text)
- ✅ Session-based authentication
- ✅ SQL injection protection (parameterized queries)
- ✅ User data isolation (all queries filtered by user_id)
- ✅ Input validation and sanitization
- ✅ CSRF protection via Flask sessions

## 📈 API Integration

The application uses the Yahoo Finance API via the `yfinance` library:

- **Real-time Prices**: Fetches current market prices
- **Historical Data**: Retrieves 6-month price history
- **Stock Info**: Gets company name, sector, currency
- **Error Handling**: Gracefully handles invalid symbols or API downtime

## 🎨 Features Showcase

### Dashboard
- Real-time portfolio valuation
- Total profit/loss calculation
- Percentage return metrics
- Asset allocation visualization
- Quick access to all holdings

### Transaction History
- Complete audit trail
- Buy/sell tracking
- Date and price recording
- Total value calculations

### Price Charts
- Interactive historical charts
- 6-month price trends
- Hover tooltips with details
- Gradient visualization

## 🐛 Troubleshooting

**Issue**: Database not found
- **Solution**: Run `python models.py` to initialize

**Issue**: Yahoo Finance API not responding
- **Solution**: Check internet connection; API may have rate limits

**Issue**: Static files not loading
- **Solution**: Ensure files are in `static/` directory

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built by [Your Name] - [GitHub Profile](https://github.com/yourusername)

## 🙏 Acknowledgments

- Yahoo Finance for providing financial data API
- Flask community for excellent documentation
- Chart.js for visualization capabilities

---

**Note**: This is a portfolio project for educational purposes. Not financial advice. Always do your own research before investing.
