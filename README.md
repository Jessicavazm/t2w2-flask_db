# t2w2-flask_db

## Flask and API

First import flask and request, import SQLAlchemy to connect database to API and Marshmallow to convert the data objects to Python understandable objects.

* Connect database to API
* Since you table is empty, you first need to create the TABLES and the way to create and define the table is using MODEL. For each MODEL you need to create a SCHEMA. Schemas are made to fetch/ dump info from and to database. Schemas convert DB values into Python understandable format. This is essential to send response back to be displayed at the front end.
* Create CLI CUSTOM commands since you are working with Python language instead of SQL language. CLI commands are created for you to create and insert values into the tables. "CREATE", "SEED", "DROP" common commands.
* Create ROUTES, this is the most important thing in API(Application programming interface), this creates functions(operations) that will be processed accordingly to HTTPS request (GET, POST, PUT, PATCH and DELETE requests)

Steps to define ROUTES
* Define statement first using `stmt = `
* Execute the statement
* If it's a POST request, you need to ADD() and COMMIT()
* If it's the other requests such as UPDATE or DELETE you just need to COMMIT(), since you already fetch info from DB.
* RETURN something using schemas(made from Marshmallow library) to DUMP, this convert the schema value into Python understandable format (Sends the VALUE back to FRONTEND).

## Authentication  

Steps
* Create objects for B.crypt and for JWT 
* Create a class USER, have attributes can be used for Authorization purposes = Boolean value
* Encrypt password using b.crypt (sensitive data)
* Create UserSchema and define fields under meta class
* Create Schema objects to fetch a singular or multiple values, exclude = password in user/users_schemas
* Create a register route, when user register you hash their password and stores the hashed value in the DT.
* When user logins in, you check hashed values and ID, if it matches you create the TOKEN and returns the values.