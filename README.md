# Customer Order service.

This is a simple customer and order service. 
It allows you to add new customers and create new orders.
When a new order is place, a notification is sent to the customer via sms.

This repository contains the code for the following Backend technical challenge:

```
1. Create a simple Python or Go service
2. Design a simple customers and orders database (keep it simple)
3. Add a REST or GraphQL API to input / upload customers and orders:
- Customers have simple details e.g., name and code.
- Orders have simple details e.g., item, amount, and time.
4. Implement authentication and authorization via OpenID Connect
5. When an order is added, send the customer an SMS alerting them (you can use the
Africa’s Talking SMS gateway and sandbox)
6. Write unit tests (with coverage checking) and set up CI + automated CD. You can deploy
to any PAAS/FAAS/IAAS of your choice
7. Write a README for the project and host it on your GitHub
```

## Getting Started.
- To run this project, you need to have python3 and pip installed.
- Clone this repository.
- Start a vitual environment with the commadnd below
` python3 -m venv venv `
- Activate the virtual environment with the command below
` source venv/bin/activate `
- Install the requirements with the command below
` pip install -r requirements.txt `

## Setting up the postgres database.

Create a .env file in the root directory of the project and copy the contents of the .env.example file into it. Add the database credentials to the .env file.

- Create a database with the name `customer_order_db`
then run the command below to create the tables.

or

run the command below to create the database and tables.
` python3 customer_order_db.py `


## Running the application

Run the application with the command below to start the FASTAPI server.

`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Next go to the location of the project and open the customer_orders.html file in your browser. 
The file is found in the static folder.
This should redirect you to the login page.

You can then interact with the application after registering and logging in.

## Running the tests

The tests are found in the test directory. To run the tests, run the command below. Replace file.py with the actual name of the file you want to test.

`python3 -m unnittest unittest test/<file.py>`
