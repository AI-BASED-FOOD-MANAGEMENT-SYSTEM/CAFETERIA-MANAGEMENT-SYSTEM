from flask import Flask, render_template, request
from models.predict import predict_attendance, calculate_serving_strategy

app = Flask(_name_)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    date = request.form['date']
    meal_type = request.form['meal_type']
    food_item = request.form['food_item']

    predicted = predict_attendance(date, meal_type, food_item)
    portions, risk = calculate_serving_strategy(predicted)

    return render_template(
        "index.html",
        prediction=predicted,
        portions=portions,
        risk=risk
    )

if _name_ == "_main_":
    app.run(debug=True)