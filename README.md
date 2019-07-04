# Food-Tracker
- A food tracker app to record your daily calories intake. 
- Without using any Flask extensions like SQLAlchemy.


## Installation
1. Create a virtual environment and install the dependencies.
```
pip install -r requirements.txt
```
2. Run the following code in your terminal r and input your database's name in <database's name>.
```
sqlite3 <database's name> < food_tracker.sql
```
3. Open db.py and replace food_log.db to your database's name in connect_db function.
```
sql = sqlite3.connect(os.path.join(os.path.dirname(__name__), os.path.abspath('food_log.db')))
```
4. Run app.py
