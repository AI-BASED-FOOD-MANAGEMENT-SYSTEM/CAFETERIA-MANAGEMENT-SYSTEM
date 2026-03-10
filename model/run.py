from flask import Flask, render_template, request, jsonify
import psycopg2  

# configure Flask to use the `frontend` directory for templates and
# static assets; this allows us to keep the HTML/JS/CSS alongside the
# rest of the project without duplicating files.

app = Flask(
    __name__,
    static_folder="../frontend",      # serve JS/images/css
    template_folder="../frontend"     # load HTML files as templates
)

DB_NAME = "forecast"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"

# bring in helpers for working with the Postgres database
from model.models.db_utils import get_connection, ensure_predictions_table, ensure_actuals_table

@app.route('/')
def index():
    return render_template('index.html')

# make sure our storage tables exist before any requests hit the API
ensure_predictions_table()
ensure_actuals_table()

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # mirror the behaviour of the JSON API so the traditional form works too
        day = request.form['day']
        meal_type = request.form['meal_type']
        food_item = request.form['food_item']
        try:
            popularity_index = float(request.form.get('popularity_index', 0.5))
        except (TypeError, ValueError):
            popularity_index = 0.5

        from model.models.predict import predict_attendance, calculate_serving_strategy
        estimated_students = predict_attendance(day, meal_type, food_item, popularity_index)
        suggested_quantity, risk_level = calculate_serving_strategy(estimated_students)

        # persist the prediction
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions(day_of_week, meal_type, food_item, popularity_index, predicted_students, suggested_quantity, waste_risk) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (day, meal_type, food_item, popularity_index, estimated_students, suggested_quantity, risk_level)
        )
        conn.commit()
        cur.close()
        conn.close()

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
    from model.models.predict import predict_attendance, calculate_serving_strategy

    students = predict_attendance(day, meal_type, food_item, popularity_index)
    quantity, risk = calculate_serving_strategy(students)

    # save prediction to database for auditing/training feedback
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO predictions(day_of_week, meal_type, food_item, popularity_index, predicted_students, suggested_quantity, waste_risk) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (day, meal_type, food_item, popularity_index, students, quantity, risk)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        'students': students,
        'quantity': quantity,
        'risk': risk,
    })


@app.route('/api/predictions/last', methods=['GET'])
def api_last_prediction():
    """Return the most recent prediction record from the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT day_of_week, meal_type, food_item, popularity_index, predicted_students, suggested_quantity, waste_risk, created_at FROM predictions ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        (dow, mt, fi, pi, students, qty, risk, ts) = row
        return jsonify({
            'day': dow,
            'meal_type': mt,
            'food_item': fi,
            'popularity_index': pi,
            'students': students,
            'quantity': qty,
            'risk': risk,
            'timestamp': ts.isoformat(),
        })
    else:
        return jsonify({}), 404


@app.route('/api/actuals', methods=['POST'])
def api_actuals():
    """Store actual attendance/quantity data submitted from the frontend."""
    data = request.get_json(force=True) or {}
    date = data.get('date')
    meal_type = data.get('mealType')
    food_item = data.get('foodItem')
    try:
        actual_students = int(data.get('actualStudents', 0))
    except (TypeError, ValueError):
        actual_students = None
    try:
        actual_quantity = float(data.get('actualQuantity', 0))
        quantity_wasted = float(data.get('quantityWasted', 0))
        quantity_sold = float(data.get('quantitySold', 0))
    except (TypeError, ValueError):
        actual_quantity = quantity_wasted = quantity_sold = None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO actuals(date, meal_type, food_item, actual_students, actual_quantity, quantity_wasted, quantity_sold)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (date, meal_type, food_item, actual_students, actual_quantity, quantity_wasted, quantity_sold),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True)
