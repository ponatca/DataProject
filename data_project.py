# Endpoints
# 1. http://127.0.0.1:5000/count_data
# 2. http://127.0.0.1:5000/compute_std_dev?start=YYYY-MM-DD&end=YYYY-MM-DD
# e.g. http://127.0.0.1:5000/compute_std_dev?start=2023-01-12&end=2023-02-12
# 3. http://127.0.0.1:5000/performance?start=YYYY-MM-DD&end=YYYY-MM-DD
# e.g. http://127.0.0.1:5000/performance?start=2023-01-12&end=2023-02-12

import sqlite3
import pandas as pd
from flask import Flask, jsonify, request
import time as time_module

from datetime import datetime, time

#MySQL: Simulated using an in-memory SQLite database. This simulation serves the purpose of comparing two databases within the Flask application but does not utilize actual MySQL features.



app = Flask(__name__)

# Setup database connections
conn = sqlite3.connect('synthetic_data.db', check_same_thread=False)
mysql_conn = sqlite3.connect(':memory:', check_same_thread=False)

# Create tables
cursor = conn.cursor()
mysql_cursor = mysql_conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS time_series_data (
    time TEXT,
    id INTEGER,
    value_alpha REAL,
    value_beta REAL,
    class_gamma TEXT
);
''')
mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS time_series_data (
    time TEXT,
    id INTEGER,
    value_alpha REAL,
    value_beta REAL,
    class_gamma TEXT
);
''')

# Import the necessary Pandas library for data manipulation and analysis.
import pandas as pd

# Load data section wrapped in a try-except block to handle potential exceptions.
try:
    # Read data from a CSV file named 'synthetic_data.csv' into a Pandas DataFrame.
    df = pd.read_csv('synthetic_data.csv')

    # Load the DataFrame into the SQLite database table 'time_series_data'.
    # If the table exists, replace it with the new data. The index of the DataFrame is not written to the database.
    df.to_sql('time_series_data', conn, if_exists='replace', index=False)

    # Similarly, load the DataFrame into the in-memory SQLite database table 'time_series_data'.
    df.to_sql('time_series_data', mysql_conn, if_exists='replace', index=False)

    # Print a success message if the data is loaded successfully into both databases.
    print("Data loaded successfully into both databases.")
except Exception as e:
    # Print an error message if there is an exception during the data loading process.
    print("Failed to load data:", e)


# Import the necessary Flask module for creating the web application and jsonify for formatting the response as JSON.
from flask import Flask, jsonify

# Assuming the app has been defined elsewhere in your script, e.g., app = Flask(__name__)

# Define a route for '/count_data' that can be accessed using the HTTP GET method.
@app.route('/count_data')
def count_data():
    # Execute a SQL query to count the number of rows in the 'time_series_data' table using the SQLite database connection.
    count = cursor.execute('SELECT COUNT(*) FROM time_series_data').fetchone()[0]

    # Execute the same count query using the in-memory SQLite database connection.
    mysql_count = mysql_cursor.execute('SELECT COUNT(*) FROM time_series_data').fetchone()[0]

    # Return a JSON response that includes the counts from both the SQLite and the in-memory SQLite databases.
    # It seems there was a confusion here, as you intended to use MySQL, adjust this part to use a proper MySQL connection.
    return jsonify({'SQLite Count': count, 'MySQL Count': mysql_count})


# Import the necessary Flask module for creating the web application, jsonify for formatting the response as JSON,
# and request to handle query parameters.
from flask import Flask, jsonify, request

# Assuming the app has been defined elsewhere in your script, e.g., app = Flask(__name__)

# Define a route for '/compute_std_dev' accessible via HTTP GET.
@app.route('/compute_std_dev', methods=['GET'])
def compute_std_dev():
    # Retrieve 'start' and 'end' date parameters from the query string.
    start = request.args.get('start')
    end = request.args.get('end')
    
    # SQL query to calculate the average and variance of the expression (value_alpha + value_beta * 10) 
    # grouped by 'class_gamma' and day, within the provided date range.
    query = """
    SELECT class_gamma, strftime('%Y-%m-%d', time) as day,
           AVG(value_alpha + value_beta * 10) as mean_value,
           (
               SUM(
                   POWER(value_alpha + value_beta * 10 - (SELECT AVG(value_alpha + value_beta * 10) FROM time_series_data WHERE time BETWEEN ? AND ?), 2)
               ) / COUNT(*)
           ) as variance
    FROM time_series_data
    WHERE time BETWEEN ? AND ?
    GROUP BY class_gamma, day;
    """
    
    # Execute the query on SQLite with the provided start and end dates.
    cursor.execute(query, (start, end, start, end))
    results = cursor.fetchall()
    
    # Calculate standard deviation from variance for each result tuple and prepare the final result.
    # Standard deviation is the square root of variance, hence the use of x[3]**0.5.
    results = [(x[0], x[1], (x[2], x[3]**0.5)) for x in results]
    
    # Return the results as a JSON response, where each result includes class, day, mean_value, and standard deviation.
    return jsonify({"Results": results})



# Import necessary modules: Flask for the web application, jsonify for JSON formatting,
# request to access query parameters, and time to measure execution times.
from flask import Flask, jsonify, request
import time as time_module  # Renamed to avoid confusion with SQL 'time' field.

# Assuming the app has been defined elsewhere in your script, e.g., app = Flask(__name__)

# Define a route for '/performance' accessible via HTTP GET.
@app.route('/performance', methods=['GET'])
def performance():
    # Retrieve 'start' and 'end' date parameters from the query string.
    start = request.args.get('start')
    end = request.args.get('end')
    
    # SQL query to calculate the average and variance of the expression (value_alpha + value_beta * 10) 
    # grouped by 'class_gamma' and day, within the provided date range.
    query = """
    SELECT class_gamma, strftime('%Y-%m-%d', time) as day, 
           AVG(value_alpha + value_beta * 10) as mean_value,
           (
               SUM(
                   POWER(value_alpha + value_beta * 10 - (SELECT AVG(value_alpha + value_beta * 10) FROM time_series_data WHERE time BETWEEN ? AND ?), 2)
               ) / COUNT(*)
           ) as variance
    FROM time_series_data
    WHERE time BETWEEN ? AND ?
    GROUP BY class_gamma, day;
    """
    
    # Measure performance on SQLite: Start timer, execute query, fetch results, stop timer.
    start_time = time_module.time()
    cursor.execute(query, (start, end, start, end))
    cursor.fetchall()
    sqlite_time = time_module.time() - start_time
    
    # Measure performance on simulated MySQL: Same steps as above.
    start_time = time_module.time()
    mysql_cursor.execute(query, (start, end, start, end))
    mysql_cursor.fetchall()
    mysql_time = time_module.time() - start_time
    
    # Return the performance times as a JSON response, comparing SQLite and simulated MySQL.
    return jsonify({"SQLite Time": sqlite_time, "MySQL Time": mysql_time})
    
if __name__ == '__main__':
    app.run(debug=True)
