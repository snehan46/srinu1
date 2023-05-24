from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
import matplotlib.pyplot as plt
from flask_cors import CORS
from sklearn.metrics import mean_absolute_error, mean_squared_error

app = Flask(__name__)
CORS(app)

@app.route('/forecast', methods=['POST'])
def forecast(): 
    # Get the CSV file from the frontend
    file = request.files['csvFile']
    df = pd.read_csv(file)

    # Check that the CSV file contains the required columns
    if not all(col in df.columns for col in ['date', 'sales']):
        return jsonify({'error': 'CSV file must contain columns "date" and "sales"'})

    # Get the periodicity and time period inputs from the Angular frontend
    periodicity = request.form['periodicity']
    time_period = int(request.form['timePeriod'])
    df['date'] = pd.to_datetime(df['date'])

    # Create a date range based on the time period and periodicity inputs Accordingly
    if periodicity == 'daily':
        date_range = pd.date_range(df['date'].max(), periods=time_period, freq='D')
    elif periodicity == 'weekly':
        date_range = pd.date_range(df['date'].max(), periods=time_period, freq='W')
    elif periodicity == 'monthly':
        date_range = pd.date_range(df['date'].max(), periods=time_period, freq='M')
    elif periodicity == 'yearly':
        date_range = pd.date_range(df['date'].max(), periods=time_period, freq='Y')

    # Train a linear regression model on the historical sales data
    X_train = np.array(df['date'].astype(np.int64)).reshape((-1, 1))
    y_train = np.array(df['sales'])
    model = LinearRegression().fit(X_train, y_train)

    # Predict future sales using the trained model and the date range
    X_test = np.array(date_range.astype(np.int64)).reshape((-1, 1))
    y_pred = model.predict(X_test)

    # Calculate MAE and RMSE Accuracy metrics
    mae = mean_absolute_error(y_train, model.predict(X_train))
    rmse = np.sqrt(mean_squared_error(y_train, model.predict(X_train)))

    # Create a dataframe with the predicted sales and date range
    pred_df = pd.DataFrame({'date': date_range, 'sales': y_pred})

    # Save the predicted sales to a CSV file
    pred_df.to_csv('predicted_sales.csv', index=False)

    # Create a plot of the predicted sales
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(df['date'], df['sales'], label='Actual Sales')
    ax.plot(pred_df['date'], pred_df['sales'], label='Predicted Sales')
    ax.legend()
    plt.title('Predicted Sales')
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.savefig('predicted_sales.png')
    plt.show()
    

    # Return the predicted sales and the path to the plot as a JSON object
    return jsonify({'date': list(pred_df['date'].astype(str)), 
                    'sales': list(pred_df['sales']), 
                    'plotPath': 'predicted_sales.png', 
                    'mae': mae, 
                    'rmse': rmse})

if __name__ == '__main__':
    app.run(debug=True)