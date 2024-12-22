from flask import Flask, render_template, redirect, url_for, request, abort, g
import sqlite3
import datetime
import dateutil.relativedelta
import re


DATABASE = "tracker.db"

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def clean_registration_form(request_form):
    validation_re = {
        "member_id": r"^\d+$",
        "transaction_date": r"^\d{4}-\d{1,2}-\d{1,2}$",
        "category_id": r"^\d+$",
        "description": "",
        "amount": r"^\d+(\.\d{1,2})?$",
    }
    errors = set()
    form = {}
    for field, pattern in validation_re.items():
        form[field] = request_form.get(field, "")
        if not re.match(pattern, form[field]):
            errors.add(field)
        elif field == "transaction_date":
            try:
                form["transaction_date"] = datetime.datetime.strptime(form["transaction_date"], "%Y-%m-%d").date()
            except ValueError:
                errors.add("transaction_date")
        elif field.endswith("_id"):
            form[field] = int(form[field])
    return form, errors


@app.route("/")
def index():
    start_date = datetime.date.today() - dateutil.relativedelta.relativedelta(days=30)
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT sum(amount) AS income_total FROM income
        WHERE transaction_date >= ?
        """,
        (start_date,)
    )
    income_total = cursor.fetchone()["income_total"]
    cursor.execute(
        """
        SELECT sum(amount) AS expense_total FROM expense
        WHERE transaction_date >= ?
        """,
        (start_date,)
    )
    expense_total = cursor.fetchone()["expense_total"]
    return render_template("index.html", income_total=income_total, expense_total=expense_total)


@app.route("/add/expense", methods=["GET", "POST"])
def add_expense():
    db = get_db()
    form = {"transaction_date": datetime.date.today()}
    errors = set()
    if request.method == "POST":
        form, errors = clean_registration_form(request.form)
        if not errors:
            try:
                db.cursor().execute(
                    "INSERT INTO expense(member_id, transaction_date, category_id, description, amount) VALUES (?, ?, ?, ?, ?)",
                    (form["member_id"], form["transaction_date"], form["category_id"], form["description"], form["amount"])
                )
                db.commit()
                return redirect(url_for("overview_month", year=form["transaction_date"].year, month=form["transaction_date"].month))
            except sqlite3.Error as e:
                if e.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
                    errors.add("__fk__")
    member_cursor = db.cursor()
    member_cursor.execute("SELECT id, name FROM member")
    category_cursor = db.cursor()
    category_cursor.execute("SELECT id, title FROM expense_category")
    return render_template("add_expense.html", form=form, errors=errors, members=member_cursor, categories=category_cursor)


@app.route("/add/income", methods=["GET", "POST"])
def add_income():
    db = get_db()
    form = {"transaction_date": datetime.date.today()}
    errors = set()
    if request.method == "POST":
        form, errors = clean_registration_form(request.form)
        if not errors:
            try:
                db.cursor().execute(
                    "INSERT INTO income(member_id, transaction_date, category_id, description, amount) VALUES (?, ?, ?, ?, ?)",
                    (form["member_id"], form["transaction_date"], form["category_id"], form["description"], form["amount"])
                )
                db.commit()
                return redirect(url_for("overview_month", year=form["transaction_date"].year, month=form["transaction_date"].month))
            except sqlite3.Error as e:
                if e.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
                    errors.add("__fk__")
    member_cursor = db.cursor()
    member_cursor.execute("SELECT id, name FROM member")
    category_cursor = db.cursor()
    category_cursor.execute("SELECT id, title FROM income_category")
    return render_template("add_income.html", form=form, errors=errors, members=member_cursor, categories=category_cursor)


@app.route("/overview/month/")
@app.route("/overview/month/<int:year>/<int:month>")
def overview_month(year=None, month=None):
    if year is None or month is None:
        today = datetime.date.today()
        year = today.year
        month = today.month
    month_start = datetime.date(year, month, 1)
    prev_month_start = datetime.date(year, month - 1, 1) if month > 1 else datetime.date(year - 1, 12, 1)
    next_month_start = datetime.date(year, month + 1, 1) if month < 12 else datetime.date(year + 1, 1, 1)

    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT SUM(amount) AS amount
        FROM income
        WHERE transaction_date >= ? AND transaction_date < ?
        """,
        (month_start, next_month_start)
    )
    income_total = cursor.fetchone()["amount"]
    cursor.execute(
        """
        SELECT SUM(amount) AS amount
        FROM expense
        WHERE transaction_date >= ? AND transaction_date < ?
        """,
        (month_start, next_month_start)
    )
    expense_total = cursor.fetchone()["amount"]
    cursor.execute(
        """
        SELECT title, SUM(amount) AS amount
        FROM income
        JOIN income_category ON income.category_id=income_category.id
        WHERE transaction_date >= ? AND transaction_date < ?
        GROUP BY income_category.id
        ORDER BY title
        """,
        (month_start, next_month_start)
    )
    income_summary = cursor.fetchall()  # The number of categories is small
    income_summary_titles = [row["title"] for row in income_summary]
    income_summary_amounts = [row["amount"] for row in income_summary]
    cursor.execute(
        """
        SELECT title, SUM(amount) AS amount
        FROM expense
        JOIN expense_category ON expense.category_id=expense_category.id
        WHERE transaction_date >= ? AND transaction_date < ?
        GROUP BY expense_category.id
        ORDER BY title
        """,
        (month_start, next_month_start)
    )
    expense_summary = cursor.fetchall()  # The number of categories is small
    expense_summary_titles = [row["title"] for row in expense_summary]
    expense_summary_amounts = [row["amount"] for row in expense_summary]
    cursor.execute(
        """
        SELECT transaction_date, name, title AS category_title, description, amount as income, NULL as expense
        FROM income
        JOIN member ON member.id=income.member_id
        JOIN income_category ON income.category_id=income_category.id
        WHERE transaction_date >= ? AND transaction_date < ?
        UNION ALL
        SELECT transaction_date, name, title AS category_title, description, NULL as income, amount as expense
        FROM expense
        JOIN member ON member.id=expense.member_id
        JOIN expense_category ON expense.category_id=expense_category.id
        WHERE transaction_date >= ? AND transaction_date < ?
        ORDER BY transaction_date
        """,
        (month_start, next_month_start, month_start, next_month_start)
    )
    return render_template(
        "overview_month.html",
        month_start=month_start,
        prev_month_start=prev_month_start,
        next_month_start=next_month_start,
        transactions=cursor,
        income_total=income_total,
        expense_total=expense_total,
        income_summary=income_summary,
        income_summary_titles=income_summary_titles,
        income_summary_amounts=income_summary_amounts,
        expense_summary=expense_summary,
        expense_summary_titles=expense_summary_titles,
        expense_summary_amounts=expense_summary_amounts
    )
if __name__ == "__main__":
    app.run(debug=True, port=8080)
