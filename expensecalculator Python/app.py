from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In-memory database (for simplicity)
expenses = []
categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Rent', 'Utilities', 'Other']

@app.route('/')
def index():
    filter_category = request.args.get('category', '')
    filter_date = request.args.get('date', '')

    # Filter expenses based on category and date
    filtered_expenses = [
        expense for expense in expenses
        if (not filter_category or expense['category'] == filter_category) and
           (not filter_date or expense['date'].split('T')[0] == filter_date)
    ]

    # Group expenses by category
    grouped_expenses = {}
    for expense in filtered_expenses:
        category = expense['category']
        if category not in grouped_expenses:
            grouped_expenses[category] = []
        grouped_expenses[category].append(expense)

    # Calculate total expense
    total_expense = sum(expense['amount'] for expense in filtered_expenses)

    # Generate summary by category
    summary = {}
    for category, items in grouped_expenses.items():
        summary[category] = sum(item['amount'] for item in items)

    return render_template(
        'index.html',
        expenses=grouped_expenses,
        total_expense=total_expense,
        categories=categories,
        filter_category=filter_category,
        filter_date=filter_date,
        summary=summary
    )

@app.route('/add', methods=['POST'])
def add_expense():
    name = request.form['name']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']

    # Add new expense to the list
    expenses.append({
        'name': name,
        'amount': amount,
        'category': category,
        'date': date
    })
    
    return redirect(url_for('index'))

@app.route('/remove/<int:expense_index>')
def remove_expense(expense_index):
    if 0 <= expense_index < len(expenses):
        del expenses[expense_index]
    return redirect(url_for('index'))

@app.route('/export')
def export_to_csv():
    import csv
    from io import StringIO

    # Generate CSV content
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Amount', 'Category', 'Date'])
    for expense in expenses:
        writer.writerow([expense['name'], expense['amount'], expense['category'], expense['date']])

    # Prepare CSV for download
    output.seek(0)
    response = app.response_class(
        response=output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=expenses.csv'}
    )
    return response

if __name__ == '__main__':
    app.run(debug=True)
