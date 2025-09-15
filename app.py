from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URI = os.getenv("DATABASE_URI")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create a model - Table representation
class Product(db.Model):
    # Define table name
    __tablename__ = "products"
    # define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # define the attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

# Create Marshmallow instances
# To handle multiple products
products_schema = ProductSchema(many=True)

# To handle single product
product_schema = ProductSchema()

# Create commands to manipulate the DB, so it's easier to do some db stuffs

# To create table(s)
@app.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created.")

# To drop table(s)
@app.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables dropped.")

@app.cli.command('seed')
def seed_db():
    # create an instance of products Model

    # Method 1:
    product_1 = Product(
        name = "Product 1",
        description = "New first product",
        price = 12.99,
        stock = 15
    )
    # Method 2:
    product_2 = Product()
    product_2.name = "Telephone"
    
    #  Like git operations, you add
    db.session.add(product_1)
    db.session.add(product_2)
    # then, commit 
    db.session.commit()
    # Acknowledgement message
    print("Table(s) seeded.")

# CRUD Operations on Product
# C - Create - POST
# R - Read - GET
# U - Update - PUT/PATCH
# D - Delete - DELETE

# Read from the Table
# GET /products
@app.route("/products")
def get_products():
    # stmt: SELECT * FROM products;
    # products_list = db.select(Product)
    products_list = Product.query.all()

    # Convert the Python object to JSON serialisable format using Marshmallow
    data = products_schema.dump(products_list)

    return jsonify(data)

# GET a product /products/id
@app.route("/products/<int:product_id>", methods=["GET"])
def get_a_product(product_id):
    # stmt: SELECT * FROM products WHERE id=product_id;
    product = Product.query.get(product_id)

    if product:
        # Serialise it
        data = product_schema.dump(product)
        return jsonify(data)
    else:
        return jsonify({"message": f"Product with id {product_id} does not exist."}), 404

# Create a Product
@app.route("/products", methods=["POST"])
def create_product():
    # Get the data from the request body
    body_data = request.get_json()
    # stmt: INSERT INTO products (id, name, ....) VALUES (1, .....);
    new_product = Product(
        name = body_data.get("name"),
        description = body_data.get("description"),
        price = body_data.get("price"),
        stock = body_data.get("stock")
    )
    # Add to the session
    db.session.add(new_product)
    # Commit
    db.session.commit()
    # Send an acknowledgement message
    data = product_schema.dump(new_product)
    return jsonify(data), 201

# DELETE /products/id
@app.route("/products/<int:product_id>", methods = ["DELETE"])
def delete_product(product_id):
    # stmt: DELETE * FROM products WHERE id = product_id;
    # Find the product with the specific id from the database
    # stmt: SELECT * FROM products WHERE id = product_id;
    # product = Product.query.get(product_id)

    # Method 1
    stmt = db.select(Product).filter_by(id=product_id)
    # Method 2
    # stmt = db.select(Product).where(Product.id == product_id)
    
    # Execute the statement
    product = db.session.scalar(stmt)

    # if the product exists:
    if product:
        # delete it
        db.session.delete(product)
        db.session.commit()
        
        return {"message": f"Product with name '{product.name}' deleted successfully."}
    # else
    else:
        # say, it doesn't exist
        return {"message": f"Product with id '{product_id}' does not exist."}, 404
    

# PUT/PATCH - /products/id
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    # Find the product with the id from the database
    # stmt: SELECT * FROM products WHERE id = product_id;
    product = Product.query.get(product_id)

    # If product exists:
    if product:
        # Get the updated json data from request body
        body_data = request.get_json()
        # Update the product - using Short Circuit
        product.name = body_data.get("name",product.name)
        product.description = body_data.get("description",product.description)
        product.price = body_data.get("price", product.price)
        product.stock = body_data.get("stock", product.stock)
    
        # Save the changes
        db.session.commit()
        # acknowledgement message
        return jsonify(product_schema.dump(product))
    # else:
    else:
        # acknowledgement message 
        return {"message": f"Product with id '{product_id}' does not exist."}, 404 