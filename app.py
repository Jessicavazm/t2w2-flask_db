# Import 
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Create an object from 'Flask' class
app = Flask(__name__)

# Connect to Database                   DBMS        DB_DRIVER DB_USER DB_PASS  URL      PORT DB_NAME 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://apr_stds:123456@localhost:5432/t2w2"


# Create an OBJ for SQLalchemy
# Create an OBJ for Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create a model of a table, start with class (define db table, constrains)
class Product(db.Model):
    # Define the name of the table
    __tablename__ = "products"
    # Define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # Define other attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

# Creating a Schema
class ProductSchema(ma.Schema):
    class Meta:
        # Fields
        fields = ("id", "name", "description", "price", "stock")

# Create this to handle multiple products
products_schema = ProductSchema(many=True)

#Create this to handle a single entry
product_schema = ProductSchema()


# Controllers are the definitions
# CLI Commands - Custom 
@app.cli.command("create")
def create_tables():
    db.create_all()
    print("Create all the tables")


# Create another command to seed values to the table
@app.cli.command("seed")
def seed_tables():
    # Create a product object, there's two ways
    # 1
    product1 = Product(
        name = "Fruits",
        description = "Fresh Fruits",
        price = 15.99,
        stock = 100
    )

    # Second way
    product2 = Product()
    product2.name = "Vegetables"
    product2.description = "Fresh Vegetables"
    product2.price = 10.99
    product2.stock = 200

    # products = [product1, product2]
    
    # Add everything to session
    # db.session.add_all(products)
    
    # Add to session individually
    db.session.add(product1)
    db.session.add(product2)

    # Commit 
    db.session.commit()
    print("Table seeded")


# To drop the tables
@app.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped successfully.")


# Work with routes
# Define routes
@app.route("/products")
def get_products():
    # SELECT * FROM products;
    # Create a statement object 
    stmt = db.select(Product)

    products_list = db.session.scalars(stmt)
    # Serialisation
    data = products_schema.dump(products_list)
    return data


# Dynamic routing
# This handles requests from different types of products, 
@app.route("/products/<int:product_id>")
def get_product(product_id):
    # SELECT * FROM products WHERE id = product_id
    stmt = db.select(Product).filter_by(id=product_id)

    product = db.session.scalar(stmt)

    if product:
        data = product_schema.dump(product)
        return data
    else:
        return {"error": f"Product with id {product_id} does not exist"}, 404

## RECAP
# /products, GET => Getting all products
# /products/id, GET => Getting a specific product
# /products, POST => Adding a product
# /products/id, PUT/ PATCH => Edit a product
# /products/id, DELETE => Delete a specific product

# CREATE OR ADD ITEM
@app.route("/products", methods=["POST"])
def add_product():
    product_fields = request.get_json()

    new_product = Product(
        name = product_fields.get("name"),
        description = product_fields.get("description"),
        price = product_fields.get("price"),
        stock = product_fields.get("stock"),
    )

    db.session.add(new_product)
    db.session.commit()
    return product_schema.dump(new_product), 201

# UPDATE
# Use dynamic routes 
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    # Find the product from the database with the specific id, product_id
    stmt = db.select(Product).filter_by(id=product_id) # Create the function
    product = db.session.scalar(stmt)                   # Execute the function
    # Retrieve the data from the body of the request
    body_data = request.get_json()
    # Update
    if product:
        product.name = body_data.get("name") or product.name
        product.description = body_data.get("description") or product.description
        product.price = body_data.get("price") or product.price
        product.stock = body_data.get("stock") or product.stock
        # Commit and return back
        db.session.commit()
        return product_schema.dump(product)
    else:
        return {"error": f"Product with id {product_id} doesn't exist"}, 404
    
# DELETE
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id) # create the stmt 
    product = db.session.scalar(stmt) # execute the statement

    if product:
        db.session.delete(product)
        db.session.commit()
        return {"message": f"Product with id {product_id} is removed."}
    else:
        return {"error": f"Product with id {product_id} doesn't exist"}, 404
        
