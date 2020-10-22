from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response, flash
import os
import requests
import json
import uuid

app = Flask(__name__, static_url_path='')
app.secret_key = 'thegpatmclient'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

URL = "http://127.0.0.1:2000"


@app.route("/")
def index():
    if(request.cookies.get('gpatmuserid')):
        customerId = request.cookies.get('gpatmuserid')
        response = requests.get(
            f"{URL}/api/customer/{customerId}")
        data = response.json()
        for key, value in data.items():
            customer = value
        return render_template("index.html", customer=customer)
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        data = {
            "email": email,
            "password": password
        }

        response = requests.post(
            f"{URL}/api/customer/login", json=data)
        details = response.json()

        if(details["message"] == "success"):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie(
                'gpatmuserid', details["id"], max_age=60*60*24*365*2)
            return resp
        else:
            return redirect(url_for('login'))


@app.route("/accounts")
def bankAccounts():
    if(request.cookies.get('gpatmuserid')):
        customerId = request.cookies.get('gpatmuserid')
        response = requests.get(
            f"{URL}/api/customer/{customerId}")
        data = response.json()
        for key, value in data.items():
            customer = value

        response = requests.get(f"{URL}/api/account")

        resp = response.json()

        accounts = []

        for key, value in resp.items():
            if((str(customerId) == str(value["customerId"])) and (str(value["activation"]) == "activated") and (str(value["status"]) != "deleted")):
                accounts.append(value)

        return render_template("myAccounts.html", customer=customer, accounts=accounts)
    else:
        return redirect(url_for('login'))


@app.route("/transactions")
def transactions():
    if(request.cookies.get('gpatmuserid')):
        customerId = request.cookies.get('gpatmuserid')
        response = requests.get(
            f"{URL}/api/customer/{customerId}")
        data = response.json()
        for key, value in data.items():
            customer = value

        response = requests.get(f"{URL}/api/transactions")

        resp = response.json()

        transactions = []

        for key, value in resp.items():
            if((str(customerId) == str(value["customerId"]))):
                transactions.append(value)

        return render_template("transactions.html", customer=customer, transactions=transactions)
    else:
        return redirect(url_for('login'))


@app.route("/account/<accountNumber>/credit", methods=["GET", "POST"])
def credit(accountNumber):
    if(request.cookies.get('gpatmuserid')):
        if(request.method == "GET"):
            customerId = request.cookies.get('gpatmuserid')
            response = requests.get(f"{URL}/api/customer/{customerId}")
            data = response.json()
            for key, value in data.items():
                customer = value

            response = requests.get(f"{URL}/api/account/{accountNumber}/get")
            account = response.json()
            return render_template("credit.html", customer=customer, account=account)
        else:
            amount = int(request.form.get("amount"))
            response = requests.get(
                f"{URL}/api/{accountNumber}/credit/{amount}")
            resp = response.json()

            return redirect(f"/account/{accountNumber}/credit")
    else:
        return redirect(url_for('login'))


@app.route("/account/<accountNumber>/debit", methods=["GET", "POST"])
def debit(accountNumber):
    if(request.cookies.get('gpatmuserid')):
        if(request.method == "GET"):
            customerId = request.cookies.get('gpatmuserid')
            response = requests.get(f"{URL}/api/customer/{customerId}")
            data = response.json()
            for key, value in data.items():
                customer = value

            response = requests.get(f"{URL}/api/account/{accountNumber}/get")
            account = response.json()
            return render_template("debit.html", customer=customer, account=account)
        else:
            amount = int(request.form.get("amount"))
            response = requests.get(
                f"{URL}/api/{accountNumber}/debit/{amount}")
            resp = response.json()

            return redirect(f"/account/{accountNumber}/debit")
    else:
        return redirect(url_for('login'))


@app.route("/account/<accountNumber>/transfer", methods=["GET", "POST"])
def transfer(accountNumber):
    if(request.cookies.get('gpatmuserid')):
        if(request.method == "GET"):
            customerId = request.cookies.get('gpatmuserid')
            response = requests.get(f"{URL}/api/customer/{customerId}")
            data = response.json()
            for key, value in data.items():
                customer = value

            response = requests.get(f"{URL}/api/account/{accountNumber}/get")
            account = response.json()
            return render_template("transfer.html", customer=customer, account=account)
        else:
            availableAccounts = []
            response = requests.get(f"{URL}/api/account")
            accounts = response.json()
            for _, value in accounts.items():
                availableAccounts.append(value["accountNumber"])

            receiverAccountNumber = request.form.get("account")
            amount = int(request.form.get("amount"))

            if((str(accountNumber) in availableAccounts) and (str(receiverAccountNumber) in availableAccounts)):
                response1 = requests.get(
                    f"{URL}/api/{accountNumber}/debit/{amount}")
                response2 = requests.get(
                    f"{URL}/api/{receiverAccountNumber}/credit/{amount}")
            else:
                flash("wrong account number!", "danger")

        return redirect(f"/account/{accountNumber}/transfer")

    else:
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('gpatmuserid', expires=0)
    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5550)
