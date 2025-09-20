from flask import Flask
from flask_cors import CORS
from mv_back.routes import register_teardown#, register_routes
from mv_back.routes_old import register_routes

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000","http://localhost:5000"])

# Підключення маршрутів
register_routes(app)
register_teardown(app)

if __name__ == '__main__':
    app.run(debug=True)
