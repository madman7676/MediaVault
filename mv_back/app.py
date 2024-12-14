from flask import Flask, request, send_file
import subprocess
import os
from flask_cors import CORS
from routes import register_routes

app = Flask(__name__)
# CORS(app)
CORS(app, origins=["http://localhost:3000","http://localhost:5000"])  # Замініть на ваш фронтенд-домен

# Підключення маршрутів
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
