from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    Response,
    jsonify,
)
import sqlite3
import csv
from io import StringIO
from datetime import datetime, timedelta
import os

import yfinance as yf
from werkzeug.security import generate_password_hash, check_password_hash

from models import init_db

# ---------------------------------------------------------
# App configuration
# ---------------------------------------------------------
init_db()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Database configuration
DATABASE = "investment.db"


# ---------------------------------------------------------
# Database helper
# ---------------------------------------------------------

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def require_login(f):
    """Decorator to require login for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def get_live_price(symbol):
    """Fetch live price for a symbol with error handling."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
        else:
            # Try alternative method
            info = ticker.info
            return float(info.get("currentPrice", 0.0))
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None


def get_stock_info(symbol):
    """Get additional stock information."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "currency": info.get("currency", "USD"),
        }
    except:
        return {
            "name": symbol,
            "sector": "Unknown",
            "currency": "USD",
        }


# ---------------------------------------------------------
# Routes: Auth & Home
# ---------------------------------------------------------

@app.route("/")
def home():
    """Home page - redirect to dashboard if logged in."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password_raw = request.form.get("password", "")

        # Validation
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("register"))
        
        if not password_raw or len(password_raw) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("register"))

        password = generate_password_hash(password_raw)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users(username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "danger")
        finally:
            conn.close()

        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout."""
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}! You've been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------
# Routes: Dashboard & Portfolio
# ---------------------------------------------------------

@app.route("/dashboard")
@require_login
def dashboard():
    """Main dashboard with portfolio overview."""
    conn = get_db()
    investments = conn.execute(
        "SELECT * FROM investments WHERE user_id = ? ORDER BY symbol",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    total_value = 0.0
    total_cost = 0.0
    updated_investments = []
    
    # Track failed symbols
    failed_symbols = []

    # Calculate live prices and P/L
    for inv in investments:
        symbol = inv["symbol"]
        live_price = get_live_price(symbol)
        
        if live_price is None:
            failed_symbols.append(symbol)
            live_price = 0.0

        quantity = float(inv["quantity"])
        buy_price = float(inv["buy_price"])

        current_value = quantity * live_price
        cost = quantity * buy_price
        profit_loss = current_value - cost
        
        # Calculate percentage return
        pct_return = ((live_price - buy_price) / buy_price * 100) if buy_price > 0 else 0

        total_value += current_value
        total_cost += cost

        updated_investments.append(
            {
                "id": inv["id"],
                "symbol": symbol,
                "category": inv["category"],
                "quantity": quantity,
                "buy_price": buy_price,
                "current_price": round(live_price, 2),
                "value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "pct_return": round(pct_return, 2),
                "purchase_date": inv["purchase_date"],
            }
        )

    total_profit_loss = total_value - total_cost
    total_return_pct = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

    # Asset allocation by category (for pie chart)
    from collections import defaultdict
    category_totals = defaultdict(float)
    for inv in updated_investments:
        category_totals[inv["category"]] += inv["value"]

    category_labels = list(category_totals.keys())
    category_values = list(category_totals.values())
    
    # Show warning for failed symbols
    if failed_symbols:
        flash(f"Warning: Could not fetch prices for: {', '.join(failed_symbols)}", "warning")

    return render_template(
        "dashboard.html",
        investments=updated_investments,
        total_value=round(total_value, 2),
        total_cost=round(total_cost, 2),
        profit_loss=round(total_profit_loss, 2),
        return_pct=round(total_return_pct, 2),
        category_labels=category_labels,
        category_values=category_values,
        has_investments=len(updated_investments) > 0,
    )


@app.route("/add_investment", methods=["GET", "POST"])
@require_login
def add_investment():
    """Add a new investment."""
    if request.method == "POST":
        symbol = request.form.get("symbol", "").strip().upper()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "")
        buy_price = request.form.get("buy_price", "")

        # Validation
        if not symbol or not category:
            flash("Symbol and category are required.", "danger")
            return redirect(url_for("add_investment"))
        
        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
            if quantity <= 0 or buy_price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Quantity and price must be positive numbers.", "danger")
            return redirect(url_for("add_investment"))

        # Verify symbol is valid
        test_price = get_live_price(symbol)
        if test_price is None:
            flash(f"Warning: Could not verify symbol '{symbol}'. It may be invalid.", "warning")

        conn = get_db()
        try:
            # Add to investments table
            conn.execute(
                """
                INSERT INTO investments (user_id, symbol, category, quantity, buy_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session["user_id"], symbol, category, quantity, buy_price),
            )
            
            # Add to transaction history
            conn.execute(
                """
                INSERT INTO transactions (user_id, symbol, transaction_type, quantity, price)
                VALUES (?, ?, 'BUY', ?, ?)
                """,
                (session["user_id"], symbol, quantity, buy_price),
            )
            
            conn.commit()
            flash(f"Successfully added {quantity} shares of {symbol}!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Error adding investment: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect(url_for("add_investment"))

    return render_template("add_investment.html")


@app.route("/edit_investment/<int:id>", methods=["GET", "POST"])
@require_login
def edit_investment(id):
    """Edit an existing investment."""
    conn = get_db()
    investment = conn.execute(
        "SELECT * FROM investments WHERE id = ? AND user_id = ?",
        (id, session["user_id"]),
    ).fetchone()

    if not investment:
        conn.close()
        flash("Investment not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        quantity = request.form.get("quantity", "")
        buy_price = request.form.get("buy_price", "")
        
        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
            if quantity <= 0 or buy_price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Quantity and price must be positive numbers.", "danger")
            conn.close()
            return redirect(url_for("edit_investment", id=id))

        conn.execute(
            "UPDATE investments SET quantity = ?, buy_price = ? WHERE id = ?",
            (quantity, buy_price, id),
        )
        conn.commit()
        conn.close()
        flash("Investment updated successfully!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit_investment.html", investment=investment)


@app.route("/delete_investment/<int:id>", methods=["POST"])
@require_login
def delete_investment(id):
    """Delete an investment."""
    conn = get_db()
    
    # Get investment details before deleting
    investment = conn.execute(
        "SELECT * FROM investments WHERE id = ? AND user_id = ?",
        (id, session["user_id"]),
    ).fetchone()
    
    if investment:
        # Record as SELL transaction
        conn.execute(
            """
            INSERT INTO transactions (user_id, symbol, transaction_type, quantity, price)
            VALUES (?, ?, 'SELL', ?, ?)
            """,
            (session["user_id"], investment["symbol"], investment["quantity"], investment["buy_price"]),
        )
        
        # Delete investment
        conn.execute(
            "DELETE FROM investments WHERE id = ? AND user_id = ?",
            (id, session["user_id"]),
        )
        conn.commit()
        flash(f"Deleted {investment['symbol']} from portfolio.", "success")
    else:
        flash("Investment not found.", "danger")
    
    conn.close()
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------
# Routes: Transaction History
# ---------------------------------------------------------

@app.route("/transactions")
@require_login
def transactions():
    """View transaction history."""
    conn = get_db()
    txns = conn.execute(
        """
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY transaction_date DESC
        LIMIT 100
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()
    
    return render_template("transactions.html", transactions=txns)


# ---------------------------------------------------------
# Routes: CSV Export / Import
# ---------------------------------------------------------

@app.route("/export_csv")
@require_login
def export_csv():
    """Export portfolio to CSV."""
    conn = get_db()
    rows = conn.execute(
        "SELECT symbol, category, quantity, buy_price, purchase_date FROM investments WHERE user_id = ?",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["symbol", "category", "quantity", "buy_price", "purchase_date"])
    for r in rows:
        writer.writerow([r["symbol"], r["category"], r["quantity"], r["buy_price"], r["purchase_date"]])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=portfolio_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@app.route("/import_csv", methods=["POST"])
@require_login
def import_csv():
    """Import portfolio from CSV."""
    file = request.files.get("file")
    if not file:
        flash("No file selected.", "danger")
        return redirect(url_for("dashboard"))

    try:
        stream = StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        conn = get_db()
        imported = 0
        for row in reader:
            if not row.get("symbol"):
                continue
            
            quantity = float(row.get("quantity", 0))
            buy_price = float(row.get("buy_price", 0))
            
            if quantity <= 0 or buy_price <= 0:
                continue
                
            conn.execute(
                """
                INSERT INTO investments (user_id, symbol, category, quantity, buy_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    row["symbol"].strip().upper(),
                    row.get("category", "Other").strip(),
                    quantity,
                    buy_price,
                ),
            )
            imported += 1
        
        conn.commit()
        conn.close()
        flash(f"Successfully imported {imported} investments!", "success")
    except Exception as e:
        flash(f"Error importing CSV: {str(e)}", "danger")

    return redirect(url_for("dashboard"))


# ---------------------------------------------------------
# Routes: Historical price chart
# ---------------------------------------------------------

@app.route("/history/<symbol>")
@require_login
def history(symbol):
    """View price history for a symbol."""
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")

        if hist.empty:
            flash(f"No historical data found for {symbol}.", "warning")
            return redirect(url_for("dashboard"))

        dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        prices = hist["Close"].round(2).tolist()
        
        # Get stock info
        info = get_stock_info(symbol)

        return render_template(
            "history.html",
            symbol=symbol,
            dates=dates,
            prices=prices,
            stock_name=info["name"],
        )
    except Exception as e:
        flash(f"Error fetching history for {symbol}: {str(e)}", "danger")
        return redirect(url_for("dashboard"))


# ---------------------------------------------------------
# Error handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


# ---------------------------------------------------------
# Run app
# ---------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
