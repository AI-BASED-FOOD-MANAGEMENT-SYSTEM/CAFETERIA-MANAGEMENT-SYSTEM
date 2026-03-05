from flask import Flask, render_template, request, jsonify
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
        # placeholder values - this route may be retained or removed once API is live
        estimated_students = 120
        suggested_quantity = "10 kg"
        risk_level = "Low"

        return render_template('result.html',
                               day=day,
                               meal_type=meal_type,
                               food_item=food_item,
                               estimated_students=estimated_students,
                               suggested_quantity=suggested_quantity,
                               risk_level=risk_level)

    return render_template('predict.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Return JSON prediction using the trained attendance model."""
    data = request.get_json(force=True) or {}
    day = data.get('day')
    meal_type = data.get('meal_type')
    food_item = data.get('food_item')
    try:
        popularity_index = float(data.get('popularity_index', 0.5))
    except (TypeError, ValueError):
        popularity_index = 0.5

    # import model functions lazily to avoid startup overhead
    from models.predict import predict_attendance, calculate_serving_strategy

    students = predict_attendance(day, meal_type, food_item, popularity_index)
    quantity, risk = calculate_serving_strategy(students)

    return jsonify({
        'students': students,
        'quantity': quantity,
        'risk': risk,
    })

if __name__ == '__main__':
    app.run(debug=True)
