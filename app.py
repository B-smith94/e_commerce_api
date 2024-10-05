from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Umbr3lla4850@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.route("/")
def home():
    return "Welcome to the E-Commerce API!"

class CustomerSchema(ma.Schema):
    name = fields.String(required = True)
    email = fields.String(required = True)
    phone = fields.String()
    id = fields.Integer()

    class Meta:
        fields = ("name", "email", "phone", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class OrderSchema(ma.Schema):
    id = fields.Integer()
    date = fields.Date()
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("id", "date", "customer_id")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

class CustomerAccountSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer()
    class Meta:
        fields = ("id", "username", "password", "customer_id")

account_schema = CustomerAccountSchema()
accounts_schema = CustomerAccountSchema(many=True)

class ProductSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True, vaildate=validate.Length(min=1))
    price = fields.Float(requried=True, validate=validate.Range(min=0))
    class Meta:
        fields = ("id", "name", "price")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.Schema):
    id = fields.Integer()
    date = fields.String()
    customer_id = fields.Integer()
    expected_delivery = fields.Date()
    products = fields.List(fields.Nested(products_schema))
    class Meta:
        fields = ("id", "date", "customer_id", "expected_delivery", "products")
    

class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    order = db.relationship('Order', backref = 'customer')

class CustomerAccount(db.Model):
    __tablename__ = "customer_accounts"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

order_product = db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True))

class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    expected_delivery = db.Column(db.Date)
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders'))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

#Customer Routes
@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def search_customer(id):
    Customer.query.get_or_404(id)
    customer = Customer.query.filter_by(id=id)
    return customers_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route("/customers/<int:id>", methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

#Customer Account Routes
@app.route("/customers/<int:id>", methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}), 200

@app.route("/customer_accounts", methods=["GET"])
def get_all_accounts():
    customer_account = CustomerAccount.query.all()
    return accounts_schema.jsonify(customer_account)

@app.route("/customer_accounts/<int:id>", methods=["GET"])
def get_customer_account(id):
    CustomerAccount.query.get_or_404(id)
    customer_account = CustomerAccount.query.get(id)
    return account_schema.jsonify(customer_account)

@app.route("/customer_accounts", methods=["POST"])
def create_customer_account():
    try:
        customer_account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer_account = CustomerAccount(username=customer_account_data['username'], password=customer_account_data['password'], customer_id=customer_account_data['customer_id'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message": "New customer account created successfully"}), 201

@app.route("/customer_accounts/<int:id>", methods=["PUT"])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_account.username = account_data['username']
    customer_account.password = account_data['password']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route("/customer_accounts/<int:id>", methods=["DELETE"])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "Customer account removed successfully"}), 200

#Product Routes
@app.route("/products", methods=["GET"])
def get_all_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route("/products/<int:id>", methods=["GET"])
def search_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product details updated successfully"})

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product removed successfully"}), 200

@app.route("/orders", methods=["POST"])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(order_date=order_data['order_date'], customer_id=order_data['customer_id'], expected_delivery=order_data['expected_delivery'])
    product_query = select(Product).where(Product.id==order_data['product_id'])
    product_result = db.session.execute(product_query).scalars.first()

    new_order.products.append(product_result)

@app.route("/orders", methods=["GET"])
def get_all_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)

@app.route("/orders/<int:id>", methods=["GET"])
def search_order(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)

@app.route("/orders/<int:id>", methods=["GET"])
def order_dates(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order['order_date'], order['expected_delivery']) 

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)