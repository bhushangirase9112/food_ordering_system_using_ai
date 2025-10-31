# config.py
import os
from dotenv import load_dotenv
load_dotenv()

MENU = {
    "chicken_sandwich": {"name": "Chicken Sandwich", "price": 8.99},
    "beef_burger": {"name": "Beef Burger", "price": 9.99},
    "veggie_burger": {"name": "Veggie Burger", "price": 7.99},
    "fries": {"name": "Fries", "price": 3.99},
    "onion_rings": {"name": "Onion Rings", "price": 4.49},
    "caesar_salad": {"name": "Caesar Salad", "price": 6.99},
    "cola": {"name": "Cola", "price": 2.49},
    "lemonade": {"name": "Lemonade", "price": 2.99},
    "milkshake": {"name": "Milkshake", "price": 4.99},
}

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "food_ordering"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
}
