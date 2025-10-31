import psycopg2
import json

# Update these values if needed
db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "food_ordering",
    "user": "postgres",
    "password": "123456",
}

order_items = [
    {
        "item": "chicken_sandwich",
        "name": "Chicken Sandwich",
        "quantity": 2,
        "unit_price": 8.99,
        "total_price": 17.98,
        "modifications": None
    }
]
user_id = "wer343"
total_cost = 17.98

try:
    conn = psycopg2.connect(**db_config)
    print("Connected to DB:", db_config)
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (user_id, items, total_cost, status)
                VALUES (%s, %s, %s, %s)
                RETURNING id, total_cost
                """,
                (user_id, json.dumps(order_items), total_cost, 'pending')
            )
            result = cur.fetchone()
            print("Inserted order, result:", result)
    # Check all orders for this user
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cur.fetchall()
        print(f"Orders for user_id={user_id}:")
        for row in rows:
            print(row)
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()
