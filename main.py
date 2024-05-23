import datetime

from flask import Flask
from flask import request, jsonify
from flask_login import login_user, UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)


# Модель товара
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# Модель клиента
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.Text, nullable=True)


# Модель покупки
class Purchase(db.Model):
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)


@app.route('/api/authorize', methods=['POST'])
def authorize():
    data = request.get_json()
    username = data.get('login').lower()
    print(username)
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'status': 'ok', 'role': user.role}), 200
    else:
        return jsonify({'status': 'error'}), 401


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username').lower()
    password = data.get('password')
    role = data.get('role')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Пользователь с таким именем уже существует'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'status': 'ok', 'message': 'Пользователь успешно зарегистрирован'}), 201


@app.route('/api/user', methods=['GET'])
def get_user():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    return jsonify({'id': user.id, 'username': user.username, 'role': user.role}), 200


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return (jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity
    }), 200)


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity
        })
    return jsonify(result), 200


@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        quantity=data['quantity']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        'id': new_product.id,
        'name': new_product.name,
        'description': new_product.description,
        'price': new_product.price,
        'quantity': new_product.quantity
    }), 201


def create_initial_user():
    User_user = User.query.filter_by(username='Admin').first()
    if not User_user:
        hashed_password = generate_password_hash('Admin')
        new_user = User(username='Admin', password_hash=hashed_password, role='Admin')
        db.session.add(new_user)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        app.secret_key = 'xxxxyyyyyzzzzz'

        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'login'

        db.create_all()
        create_initial_user()
        app.run(debug=True)
