# Sight Order Dashboard

Simple two-tab Streamlit app to track eyewear ("sight") orders.

- **Dashboard tab**: add a new order (name, mobile number, age, sight, entry date, price) and view/manage active (Ordered) orders. Click "Mark Delivered" to move an order into History.
- **History tab**: view all delivered orders plus a pie chart of delivered counts by month and a bar chart of revenue by month.

## Setup

```powershell
cd sight-dashboard
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

Data is stored locally in `orders.db` (SQLite), created automatically on first run.
