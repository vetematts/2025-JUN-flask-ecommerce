from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#                                       database+driver://username:password@server:port/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://jun_user:123456@localhost:5432/jun_ecommerce"

db = SQLAlchemy(app)

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