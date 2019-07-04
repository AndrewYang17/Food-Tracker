from flask import Flask, render_template, g, request
from datetime import datetime
from db import get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        date = datetime.strptime(date, '%Y-%m-%d')
        date = datetime.strftime(date, '%Y%m%d')

        db.execute('INSERT INTO log_date (entry_date) VALUES (?)', [date])
        db.commit()

    cursor = db.execute('''SELECT log_date.entry_date, sum(food.protein) as protein, 
                            sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, 
                            sum(food.calories) as calories FROM log_date 
                            LEFT JOIN food_date ON food_date.log_date_id = log_date.id 
                            LEFT JOIN food on food.id = food_date.food_id 
                            GROUP BY log_date.id 
                            ORDER BY log_date.entry_date DESC''')
    results = cursor.fetchall()

    display_results = []

    for item in results:
        date = {
            'date': item['entry_date'],
            'protein': item['protein'],
            'carbohydrates': item['carbohydrates'],
            'fat': item['fat'],
            'calories': item['calories']
        }
        d = datetime.strptime(str(item['entry_date']), '%Y%m%d')
        date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
        display_results.append(date)

    return render_template('home.html', results=display_results)


@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    # Connect db
    db = get_db()

    # Get id and date from the date input
    date_cursor = db.execute('SELECT id, entry_date FROM log_date WHERE entry_date=?', [date])
    date_results = date_cursor.fetchone()

    # If user add new food, we insert it into food_date table with its food id and date id
    if request.method == 'POST':
        db.execute('INSERT INTO food_date (food_id, log_date_id) VALUES (?, ?)',
                   [request.form['food-select'], date_results['id']])
        db.commit()

    # Display the date
    if not date_results:
        return '<h1>Please add a new date</h1>'
    else:
        d = datetime.strptime(str(date_results['entry_date']), '%Y%m%d')
        display_date = datetime.strftime(d, '%B %d, %Y')

    # Get food from database to display in options
    food_cursor = db.execute('SELECT id, name FROM food')
    food_results = food_cursor.fetchall()

    log_cursor = db.execute('''SELECT food.name, food.protein, food.carbohydrates, food.fat, food.calories FROM log_date 
                                JOIN food_date ON food_date.log_date_id = log_date.id 
                                JOIN food ON food.id = food_date.food_id 
                                WHERE log_date.entry_date = ?''', [date])
    log_results = log_cursor.fetchall()

    totals = {
        'protein': 0,
        'carbohydrates': 0,
        'fat': 0,
        'calories': 0
    }

    for item in log_results:
        totals['protein'] += item['protein']
        totals['carbohydrates'] += item['carbohydrates']
        totals['fat'] += item['fat']
        totals['calories'] += item['calories']

    return render_template('day.html', display_date=display_date, date=date_results['entry_date'],
                           food_results=food_results, log_results=log_results, totals=totals)


@app.route('/food', methods=['POST', 'GET'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrates * 4 + fat * 9
        db.execute('INSERT INTO food (name, protein, carbohydrates, fat , calories) VALUES (?, ?, ?, ?, ?)',
                   [name, protein, carbohydrates, fat, calories])
        db.commit()

    cursor = db.execute('SELECT * FROM food')
    results = cursor.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run()
