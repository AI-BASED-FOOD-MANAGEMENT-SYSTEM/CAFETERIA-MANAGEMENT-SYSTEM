# CAFETERIA-MANAGEMENT-SYSTEM

This project predicts student attendance at a cafeteria using a trained
machine‑learning model. The original implementation relied on an Excel sheet for
historical data; the system has now been extended to use a PostgreSQL database
for both training and runtime operations. A lightweight Flask API serves the
front‑end and performs predictions.

## Database

The application expects a PostgreSQL instance reachable at the following
defaults:

- **DB_NAME**: `forecast`
- **DB_USER**: `postgres`
- **DB_PASSWORD**: `postgres`
- **DB_HOST**: `localhost`

(You may override any of these by setting the corresponding environment
variable before starting the server.)

Two important tables are used:

1. `historical_data` – contains historical operational data previously stored in
   Excel; the training script will populate this table automatically the first
time it runs if it detects the Excel file in `model/data/raw`.
2. `predictions` – keeps a record of every prediction request and its result.
   A companion `actuals` table stores observed attendance data entered via the
   UI.

A simple utility module (`model/models/db_utils.py`) handles connection creation
and table creation. The Flask app invokes the helper on startup, so no manual
SQL is required unless you prefer to pre‑load the data yourself.

### Initializing the database

If you already have the Excel spreadsheet, one way to seed the database is to
run the training script once:

```powershell
cd model
python models/attendance_model.py
```

That will read the local Excel file, write its contents into `historical_data`,
and train a `RandomForestRegressor` which is saved as
`attendance_model.pkl`. Alternatively, you can load the spreadsheet into your
Postgres instance with `psql` or a GUI such as pgAdmin/PhpMyAdmin (PhpMyAdmin
works with MySQL/MariaDB but not PostgreSQL; consider using pgAdmin or
DBeaver).

## Running the server

Activate the virtual environment, install requirements, and start Flask:

```powershell
& .venv\Scripts\Activate.ps1
pip install -r requirements.txt   # if not already done
python model/run.py
```

Visit `http://localhost:5000/predict.html` in your browser to open the
demand‑prediction page.

## How it works

- The backend loads the training data from the `historical_data` table and
  retrains the model when `attendance_model.py` is executed.
- User input from the prediction form is posted to `/api/predict`.
  - The server makes a prediction using the serialized model,
  - stores the input and output in the `predictions` table,
  - and returns the results as JSON.
- The front end then queries `/api/predictions/last` so that the displayed
  numbers are always read back from the database rather than from ephemeral
  variables.
- Users can also submit actual attendance/quantity information, which is
  recorded in the `actuals` table and can be used for future retraining.

## Notes

* The current example uses `psycopg2` and SQLAlchemy for database operations.
* Adjust the database connection information in environment variables or
  in `model/models/db_utils.py` as needed for your deployment.

---

Feel free to explore or extend the repository further!
