from flask import Flask, render_template, request
import psycopg2  

app = Flask(__name__)

DB_NAME = "forecast"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        day = request.form['day']
        meal_type = request.form['meal_type']
        food_item = request.form['food_item']

        # MOCK PREDICTION: Replace this with actual model logic later
        estimated_students = 120  # placeholder
        suggested_quantity = "10 kg"  # placeholder
        risk_level = "Low"  # placeholder

        return render_template('result.html',
                               day=day,
                               meal_type=meal_type,
                               food_item=food_item,
                               estimated_students=estimated_students,
                               suggested_quantity=suggested_quantity,
                               risk_level=risk_level)

    return render_template('predict.html')

if __name__ == '__main__':
    app.run(debug=True)
