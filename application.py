import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # add up shares belonging to a similar company
    rows = db.execute("""
    SELECT symbol, SUM(shares) as all_shares
        FROM transactions
        WHERE user_id = :user_id
        GROUP BY symbol
        HAVING all_shares > 0;
        """, user_id = session['user_id'])
    # store the results of your query in a dictionary called holdings.
    # holdings will contain data to be displayed at the home page
    holdings = []
    grand_total = 0
    for row in rows:
        stock = lookup(row['symbol'])
        holdings.append({
            "symbol": stock['symbol'],
             "name": stock['name'],
             "shares": row['all_shares'],
             "price": usd(stock['price']),
             "total": usd(stock['price'] * row['all_shares'])
        })
        grand_total += stock["price"] * row["all_shares"]
    rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session["user_id"])
    cash = rows[0]["cash"]
    grand_total += cash

    return render_template("index.html", holdings = holdings, cash = usd(cash), grand_total = usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == 'POST':
        # ensure user provides a symbol and quantity
        if not request.form.get('symbol'):
            return apology("provide a symbol", 403)

        if not request.form.get('quantity'):
            return apology("Provide number of shares to buy")

        # ensure provided quantity is a whole number
        if not request.form.get('quantity').isdigit():
            return apology("Number of shares must be a positive whole number")

        symbol = request.form.get('symbol').upper()
        quantity = request.form.get('quantity')
        user_id = session["user_id"]


        #search for the stock
        stock = lookup(symbol)

        if not stock:
            return apology("Share not found, check if symbol is correct")

        # compute cost of shares to be bought
        total_cost = float(stock["price"]) * float(quantity)

        # check current cash balance
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)

        cash = rows[0]["cash"]

        if cash < total_cost:
            return apology("You don't have sufficient funds to buy the stocks")

        # update database with the new transaction
        updated_cash = cash - total_cost

        db.execute("UPDATE users SET cash = :updated_cash WHERE id = :user_id",
                    updated_cash = updated_cash, user_id = user_id)

        # insert the transactions in your transactions history
        db.execute("""
              INSERT INTO transactions
                (user_id, symbol, shares, price)
              VALUES(:user_id, :symbol, :shares, :price)
              """,
              user_id = user_id,
              symbol = stock['symbol'],
              shares = quantity,
              price = stock['price'])

        flash("Bought!")

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # extract data from transactions table to display to the user
    transactions = db.execute("""
        SELECT symbol, shares, price, transacted
        FROM transactions where user_id = :user_id;
        """, user_id = session["user_id"])
    # convert prices to USD using the usd function
    for i in range(len(transactions)):
        transactions[i]["price"] = usd(transactions[i]["price"])

    return render_template("history.html", transactions = transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    #for a post request via a form
    if request.method == "POST":
        if not request.form.get('symbol'):
            return apology('You must provide a symbol', 403)

        symbol = request.form.get('symbol')
        quote = lookup(symbol)

        if not quote:
            return apology('could not find stock')

        quote['price'] = usd(quote['price'])

        return render_template('quoted.html', quote = quote)

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must retype password", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        #check if user exists already
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        if len(rows) >= 1:
            return apology("User already exists")

        #add the user to the database once they pass all the above checks
        new_user = db.execute("INSERT INTO users(username, hash) VALUES  (:username, :hash)",
                    username = request.form.get("username"),
                    hash = generate_password_hash(request.form.get("password")))

        session['user_id'] = new_user

        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == 'POST':
        # ensure user provides a symbol and quantity
        if not request.form.get('symbol'):
            return apology("provide a symbol", 403)

        if not request.form.get('quantity'):
            return apology("Provide number of shares to sell")

        # ensure provided quantity is a whole number
        if not request.form.get('quantity').isdigit():
            return apology("Number of shares must be a positive whole number")

        symbol = request.form.get('symbol').upper()
        quantity = int(request.form.get('quantity'))
        user_id = session["user_id"]


        #search for the stock
        stock = lookup(symbol)

        if not stock:
            return apology("Share not found, check if symbol is correct")

        # compute cost of shares to be bought
        total_cost = float(stock["price"]) * float(quantity)
        # check number of shares held for every symbol
        rows = db.execute("""
            SELECT symbol, SUM(shares) as totalShares
            FROM transactions
            WHERE user_id = :user_id
            GROUP BY symbol
            HAVING totalShares > 0;
            """, user_id = session["user_id"])
        # handle the possibility that a user tries to sell more than they hold
        for row in rows:
            if row["symbol"] == symbol:
                if quantity > row["totalShares"]:
                    return apology("Can't sell more shares than you hold")

        # check current cash balance
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)

        cash = rows[0]["cash"]

       # update database with the new transaction
        updated_cash = cash + total_cost

        db.execute("UPDATE users SET cash = :updated_cash WHERE id = :user_id",
                    updated_cash = updated_cash, user_id = user_id)

        # insert the transactions in your transactions history
        db.execute("""
              INSERT INTO transactions
                (user_id, symbol, shares, price)
              VALUES(:user_id, :symbol, :shares, :price)
              """,
              user_id = user_id,
              symbol = stock['symbol'],
              shares = -1 * quantity,
              price = stock['price'])

        flash("Sold!")

        return redirect("/")
    # submitting a GET request
    # display to the user symbols of shares that they own
    else:
        rows = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id = :user_id
            GROUP BY symbol
            HAVING SUM(shares) > 0;
            """, user_id = session["user_id"])

        return render_template("sell.html", symbols = [ row["symbol"] for row in rows ])


@app.route("/wallet", methods = ["GET", "POST"])
@login_required
def wallet():
    if request.method == "POST":
        amount = request.form.get("cash")
        user_id = session["user_id"]

        # refill your wallet
        db.execute("""
            UPDATE users SET cash = cash + :amount
            WHERE id = :user_id
            """, amount = amount, user_id = user_id)

        flash("Refilled Wallet")
        return redirect("/")


    else:
        # check current balance
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session["user_id"])
        cash = usd(rows[0]["cash"])
        return render_template('wallet.html', cash = cash)





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
