from flask import Flask, request, jsonify, render_template
from config import Config
from utils.db import init_db, close_db, execute_query
from utils.helpers import generate_token
from models import User
from blueprints.auth import auth_bp
from blueprints.hospital import hospital_bp

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    init_db()

app.teardown_appcontext(close_db)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(hospital_bp, url_prefix='/hospital')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users/<int:user_id>')
def show_user(user_id):
    user = User.get_by_id(user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON format'}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.get_by_username(username)

    if user and user.password == password:
        token = generate_token(user.id, fake=False)
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON format'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.get_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username, email, password)
    new_user.save()

    return jsonify({'message': 'User created'}), 201


@app.route('/products')
def list_products():
    query = "SELECT * FROM products"
    rows = execute_query(query, fetchall=True)
    return jsonify([dict(row) for row in rows])


@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    query = "SELECT * FROM products WHERE name LIKE ?"
    search_term = f"%{keyword}%"
    rows = execute_query(query, (search_term,), fetchall=True)
    return jsonify([dict(row) for row in rows])


@app.route('/config')
def show_config():
    return jsonify({
        'secret_key': app.config['SECRET_KEY'],
        'api_key': app.config.get('API_KEY', Config.API_KEY),
        'admin_password': Config.ADMIN_PASSWORD
    })


@app.route('/admin')
def admin_panel():
    return 'Admin panel - anyone can access'


@app.route('/bug')
def bug():
    x = request.args.get('x', '0')
    y = request.args.get('y', '0')
    try:
        result = int(x) / int(y)
        return str(result)
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero occurred'}), 500
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
