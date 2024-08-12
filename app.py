# Import Flask packages to connect DB TO API
# Convert DB Object to Python/Flask understandable objects
# Encrypt password with hash
# Create Token
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

# Create an object from 'Flask' class
app = Flask(__name__)

# Connect to Database                   DBMS        DB_DRIVER DB_USER DB_PASS  URL      PORT DB_NAME 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://apr_stds:123456@localhost:5432/t2w2"
# Define the secret key for JWT
app.config["JWT_SECRET_KEY"] = "secret"

# Create an OBJ for SQLalchemy
# Create an OBJ for Marshmallow
# Create an OBJ for Bcrypt
# Create an OBJ for JWTManager

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt =Bcrypt(app)
jwt = JWTManager(app)

# Create a model of a table, start with class (define db table, constrains)
class Product(db.Model):
    # Define the name of the table
    __tablename__ = "products"
    # Define the primary key, IDs usually are PKs
    id = db.Column(db.Integer, primary_key=True)
    # Define other attributes name + db.Column + type and constraints
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

# Create this to handle a single entry
product_schema = ProductSchema()

# Create an User model for authentication 
class User(db.Model):
    # Define the name of the table, email should be an unique value
    __tablename__ = "users"
    # Attach attributes, name = db.Column + data type + constraints
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    # Attribute based authorization, it has a boolean value and by default value is False
    is_admin = db.Column(db.Boolean, default=False)

# Define an User schema class first and import Marshmallow to inherent the proprieties from Marshmallow
class UserSchema(ma.Schema):
    # Class meta contains a list or tuple of what fields should be included the DB object conversion
    class Meta:
        #Fields
        fields = ("id", "name", "email", "password", "is_admin")

# Create objects for Schema class, one to handle single value and the other to handle multiple values
# Passwords don't need to be converted, since you will be using Tokens
# To handle multiple users, multiple values
users_schema = UserSchema(many=True, exclude=["password"])

# To handle a single user, multiple value
user_schema = UserSchema(exclude=["password"])


# Create route to register users
@app.route ("/auth/register", methods=["POST"])
def register_user():
    try:
        # Body of the request comes in JSON FORMAT that's why you use GET.JSON
        body_data = request.get_json()
        # Extracting the password from the body of the request
        password = body_data.get("password")
        # Hashing the password using B.CRYPT method GENERATE_PASSWORD_HASH
        # Decode method converts the password back to a string
        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
        # Create an user using the User Model, use GET to fetch info from BODY_DATA
        user = User(
            name = body_data.get("name"),
            email = body_data.get("email"),
            password = hashed_password
        )
        # Add it to db.session 
        db.session.add(user)
        # Commit
        db.session.commit()
        # Return something using DUMP to display in JSON format
        return user_schema.dump(user), 201
    except IntegrityError:
        return {"error": "Email address already exist"}, 400
    
# Create a route for LOGIN
@app.route("/auth/login", methods=["POST"])
def login_user():
    # Find the user with that email
    body_data = request.get_json()
    # If the user exists and the password matches, do this using STMT(Steps to execute a function)
    # SELECT * FROM users WHERE email = "user1@gmail.com", email user sends from FrontEnd
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    # Execute the statement using scalar and assigning value to a variable
    user = db.session.scalar(stmt)
    # Validate harsh and create a JWT token
    # If the user exists and the hash password matches is verified by check_password_hash
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # If it matches create a token, expire date is 1 day
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Return the TOKEN
        return {"token": token, "email": user.email, "is_admin": user.is_admin}
    else:
        return {"error": "Invalid email or password"}, 401

    # Return an error message

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

    # Create a list of users including NON ADMIN and ADMIN
    users = [
        User(
            name = "User 2",
            email = "user2@gmail.com",
            password = bcrypt.generate_password_hash("23456").decode('utf8')
        ),
        User(
            email = "admin@gmail.com",
            password = bcrypt.generate_password_hash("abc123").decode('utf8'),
            is_admin = True
        )
    ]
    # ADD users to table
    db.session.add_all(users)

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
        

