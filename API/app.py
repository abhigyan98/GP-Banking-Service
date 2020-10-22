from flask import Flask, render_template, redirect, request, url_for, jsonify
import json
import os
import uuid
import requests
import smtplib
import generator
import organizer

app = Flask(__name__, static_url_path='')
app.secret_key = 'thebankingprojectapi'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

ADMIN_EMAIL = "gangpayee@gmail.com"
ADMIN_EMAIL_PASSWORD = "GangPayee@gcetts"


@app.route("/")
def index():
    return render_template("404.html")


# Bank Section

# route ->> "/api/bank"
# POST -> create new bank details
# GET -> get all bank details
@app.route("/api/bank", methods=["GET", "POST"])
def bank():
    if(request.method == "POST"):
        name = request.json["name"]
        ifsc = request.json["ifsc"]
        address = request.json["address"]
        branch = request.json["branch"]
        email = request.json["email"]
        phone = request.json["phone"]
        bankId = str(uuid.uuid4())
        bank = {
            bankId: {
                "name": name,
                "ifsc": ifsc,
                "address": address,
                "branch": branch,
                "email": email,
                "phone": phone
            }
        }
        json_file = open(APP_ROOT+"/models/bank.json", "r")
        banks = json.load(json_file)
        json_file.close()
        banks.update(bank)
        json_file = open(APP_ROOT+"/models/bank.json", "w")
        json_file.seek(0)
        json.dump(banks, json_file)
        json_file.close()
        response = {
            "staus": "success"
        }
        organizer.organize()
        return jsonify(response)
    else:
        json_file = open(APP_ROOT+"/models/bank.json", "r")
        banks = json.load(json_file)
        json_file.close()
        return jsonify(banks)


# route ->> "/api/bank/branches"
# GET -> get all branches of all banks
@app.route("/api/bank/branches")
def getBranches():
    json_file = open(APP_ROOT+"/models/branch.json", "r")
    branches = json.load(json_file)
    json_file.close()

    return jsonify(branches)


# route ->> "/api/bank/<id>"
# GET -> get details of a particular bank
@app.route("/api/bank/<bid>")
def particularBank(bid):
    bank = {}
    json_file = open(APP_ROOT+"/models/bank.json", "r")
    banks = json.load(json_file)
    json_file.close()
    for key, value in banks.items():
        if(str(key) == str(bid)):
            bank.update({key: value})
    return jsonify(bank)


# Executive Section

# route ->> "/api/executive"
# POST -> create new executive details
@app.route("/api/executive", methods=["POST"])
def createExecutive():
    execId = str(uuid.uuid4())
    name = request.json["name"]
    email = request.json["email"]
    password = request.json["password"]
    employeeId = request.json["employeeId"]
    bankId = request.json["bankId"]
    status = "not-verified"

    executive = {
        execId: {
            "name": name,
            "email": email,
            "password": password,
            "employeeId": employeeId,
            "bankId": bankId,
            "status": status
        }
    }

    json_file = open(APP_ROOT+"/models/executive.json", "r")
    executives = json.load(json_file)
    json_file.close()

    executives.update(executive)

    json_file = open(APP_ROOT+"/models/executive.json", "w")
    json_file.seek(0)
    json.dump(executives, json_file)
    json_file.close()

    response = {
        "status": "success"
    }

    json_file = open(APP_ROOT+"/models/bank.json", "r")
    banks = json.load(json_file)
    json_file.close()

    for key, value in banks.items():
        if(str(key) == str(bankId)):
            bankEmail = value["email"]

    message = f"""
        An Executive has registered with our services using your Bank. His/Her details are :\n
        Name: {name},
        EmployeeId: {employeeId},
        Email: {email}\n\n
        To verify his/her identity, click the link below
        http://127.0.0.1:2000/executive/{execId}/verify_identity
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    server.sendmail('gangpayee@gmail.com', bankEmail, message)
    server.close()

    return jsonify(response)


# route ->> "/executive/<execId>/verify_identity"
# GET -> redirect to change verification route of a particular Executive
# redirection route -> "/api/executive/<execId>/verify_identity"
@app.route("/executive/<execId>/verify_identity")
def redirectToVerification(execId):
    redirectUrl = f"/api/executive/{execId}/verify_identity"
    return redirect(redirectUrl)


# route ->> "/api/executive/<execId>/verify_identity"
# GET -> verify an Executive's Identity
@app.route("/api/executive/<execId>/verify_identity")
def verifyExecutive(execId):
    json_file = open(APP_ROOT+"/models/executive.json", "r")
    executives = json.load(json_file)
    json_file.close()
    executiveEmail = ""
    for key, value in executives.items():
        if(str(key) == str(execId)):
            value["status"] = "verified"
            executiveEmail = value["email"]

    json_file = open(APP_ROOT+"/models/executive.json", "w")
    json_file.seek(0)
    json.dump(executives, json_file)
    json_file.close()

    response = {
        "status": "executive verified successfully"
    }

    message = f"""
        Your Bank has verified your identity.
        You can now login using your provided 'EMAIL' and 'PASSWORD' in
        http://127.0.0.1:2000/executive/login
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    server.sendmail('gangpayee@gmail.com', executiveEmail, message)
    server.close()

    return jsonify(response)


# route ->> "/api/executive/login"
# POST -> verify customer credentials for customer login
@app.route("/api/executive/login", methods=["POST"])
def executiveLogin():
    email = request.json["email"]
    password = request.json["password"]

    json_file = open(APP_ROOT+"/models/executive.json", "r")
    executives = json.load(json_file)
    json_file.close()

    response = {}

    for key, value in executives.items():
        if((value["email"] == email) and (value["password"] == password)):
            response.update({
                "id": key,
                "message": "success"
            })
            return jsonify(response)

    response.update({
        "message": "failure"
    })

    return jsonify(response)


# route ->> "/api/executive/<execId>"
# GET -> get a particular executive details
@app.route("/api/executive/<execId>")
def executive(execId):
    json_file = open(APP_ROOT+"/models/executive.json", "r")
    executives = json.load(json_file)
    json_file.close()
    executive = {}
    for key, value in executives.items():
        if(str(key) == str(execId)):
            executive.update({key: value})

    return jsonify(executive)


# route ->> "/api/executive/<bankId>/getverifications"
# GET -> get a particular executive details
@app.route("/api/executive/<bankId>/getverifications")
def getVerifications(bankId):
    json_file = open(APP_ROOT+"/models/verification.json", "r")
    verifications = json.load(json_file)
    json_file.close()

    pendingVerifications = {}

    for key, value in verifications.items():
        if(str(key) == str(bankId)):
            pendingVerifications.update({key: value})

    return jsonify(pendingVerifications)


# Customer Section

# route ->> "/api/customer"
# POST -> create new customer
@app.route("/api/customer", methods=["POST"])
def createCustomer():
    customerId = str(uuid.uuid4())
    name = request.json["name"]
    address = request.json["address"]
    email = request.json["email"]
    dob = request.json["dob"]
    password = request.json["password"]
    phone = request.json["phone"]

    customer = {
        customerId: {
            "name": name,
            "address": address,
            "email": email,
            "dob": dob,
            "password": password,
            "phone": phone,
            "status": "not-verified",
            "activation": "activated"
        }
    }

    json_file = open(APP_ROOT+"/models/customer.json", "r")
    customers = json.load(json_file)
    json_file.close()

    customers.update(customer)

    json_file = open(APP_ROOT+"/models/customer.json", "w")
    json_file.seek(0)
    json.dump(customers, json_file)
    json_file.close()

    response = {
        "status": "success"
    }

    message = f"""
        To verify your Email, click the link below
        http://127.0.0.1:2000/api/customer/{customerId}/verify_email
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    server.sendmail('gangpayee@gmail.com', email, message)
    server.close()

    return jsonify(response)


# route ->> "/api/customer/<customerId>/verify_email"
# GET -> verify customers email address
@app.route("/api/customer/<customerId>/verify_email")
def verifyCustomerEmail(customerId):
    json_file = open(APP_ROOT+"/models/customer.json", "r")
    customers = json.load(json_file)
    json_file.close()

    for key, value in customers.items():
        if(str(key) == str(customerId)):
            value["status"] = "verified"

    json_file = open(APP_ROOT+"/models/customer.json", "w")
    json_file.seek(0)
    json.dump(customers, json_file)
    json_file.close()

    response = {
        "message": "customer email verified"
    }

    return jsonify(response)


# route ->> "/api/customer/login"
# POST -> verify customer credentials for customer login
@app.route("/api/customer/login", methods=["POST"])
def customerLogin():
    email = request.json["email"]
    password = request.json["password"]

    json_file = open(APP_ROOT+"/models/customer.json", "r")
    customers = json.load(json_file)
    json_file.close()

    response = {}

    for key, value in customers.items():
        if((value["email"] == email) and (value["password"] == password)):
            response.update({
                "id": key,
                "message": "success"
            })
            return jsonify(response)

    response.update({
        "message": "failure"
    })

    return jsonify(response)


# route ->> "/api/customer/<customerId>"
# GET -> get particular customer details
# POST -> update particular customer details ( Deprecated for now )
# DELETE -> deactivate a particular customer
@app.route("/api/customer/<customerId>", methods=["GET", "DELETE"])
def customer(customerId):
    if(request.method == "POST"):
        pass
    elif(request.method == "DELETE"):
        json_file = open(APP_ROOT+"/models/customer.json", "r")
        customers = json.load(json_file)
        json_file.close()

        for key, value in customers.items():
            if(str(key) == str(customerId)):
                value["activation"] = "deactivated"

        json_file = open(APP_ROOT+"/models/customer.json", "w")
        json_file.seek(0)
        json.dump(customers, json_file)
        json_file.close()

        response = {
            "message": "customer account deactivated"
        }

        return jsonify(response)
    else:
        json_file = open(APP_ROOT+"/models/customer.json", "r")
        customers = json.load(json_file)
        json_file.close()

        for key, value in customers.items():
            if(str(key) == str(customerId)):
                return jsonify({key: value})

        response = {
            "message": "customer not found"
        }

        return jsonify(response)


# Account Section

# rourte ->> "/api/account"
# GET -> get all bank accounts
# POST -> create new account for a customer with a particular account
@app.route("/api/account", methods=["POST", "GET"])
def createAccount():
    if (request.method == "POST"):
        accountId = str(uuid.uuid4())
        customerId = request.json["customerId"]
        bankId = request.json["bankId"]
        accountType = request.json["accountType"]
        balance = 0
        activation = "deactivated"

        json_file = open(APP_ROOT+"/models/bank.json", "r")
        banks = json.load(json_file)
        json_file.close()

        for key, value in banks.items():
            if(str(bankId) == str(key)):
                bankIfsc = value["ifsc"]

        accountNumber = str(generator.createAccountNumber(bankIfsc))

        json_file = open(APP_ROOT+"/models/bank.json", "r")
        banks = json.load(json_file)
        json_file.close()

        for key, value in banks.items():
            if(str(key) == str(bankId)):
                bankName = value["name"]
                bankIfsc = value["ifsc"]
                bankAddress = value["address"]
                bankBranch = value["branch"]

        account = {
            accountId: {
                "accountNumber": accountNumber,
                "customerId": customerId,
                "bankId": bankId,
                "bankName": bankName,
                "bankIfsc": bankIfsc,
                "bankAddress": bankAddress,
                "bankBranch": bankBranch,
                "accountType": accountType,
                "balance": str(balance),
                "activation": activation,
                "status": ""
            }
        }

        json_file = open(APP_ROOT+"/models/account.json", "r")
        accounts = json.load(json_file)
        json_file.close()

        accounts.update(account)

        json_file = open(APP_ROOT+"/models/account.json", "w")
        json_file.seek(0)
        json.dump(accounts, json_file)
        json_file.close()

        json_file = open(APP_ROOT+"/models/customer.json", "r")
        customers = json.load(json_file)
        json_file.close()

        for key, value in customers.items():
            if(str(key) == str(customerId)):
                customerName = value["name"]

        verification = {
            bankId: {
                "accountId": accountId,
                "accountNumber": accountNumber,
                "customerName": customerName,
                "accountType": accountType
            }
        }

        json_file = open(APP_ROOT+"/models/verification.json", "r")
        verifications = json.load(json_file)
        json_file.close()

        verifications.update(verification)

        json_file = open(APP_ROOT+"/models/verification.json", "w")
        json_file.seek(0)
        json.dump(verifications, json_file)
        json_file.close()

        response = {
            "message": "account successfully created and sent for verification"
        }

        return jsonify(response)

    else:
        json_file = open(APP_ROOT+"/models/account.json", "r")
        accounts = json.load(json_file)
        json_file.close()

        return jsonify(accounts)


# route ->> "/api/accounts/pending_verifications"
# GET -> get all pending verifications for executive
@app.route("/api/accounts/pending_verifications")
def getPendingVerifications():
    json_file = open(APP_ROOT+"/models/verification.json", "r")
    pendingVerifications = json.load(json_file)
    json_file.close()

    return jsonify(pendingVerifications)


# route ->> "/api/account/<accountId>/verify"
# GET -> verify a particular account by Executive using "accountId"
@app.route("/api/account/<accountId>/verify")
def verifyAccount(accountId):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    for key, value in accounts.items():
        if(str(key) == str(accountId)):
            value["activation"] = "activated"

    json_file = open(APP_ROOT+"/models/account.json", "w")
    json_file.seek(0)
    json.dump(accounts, json_file)
    json_file.close()

    json_file = open(APP_ROOT+"/models/verification.json", "r")
    pendingVerifications = json.load(json_file)
    json_file.close()

    verifications = {}

    for key, value in pendingVerifications.items():
        if(str(value["accountId"]) != str(accountId)):
            verifications.update({
                key: value
            })

    json_file = open(APP_ROOT+"/models/verification.json", "w")
    json_file.seek(0)
    json.dump(verifications, json_file)
    json_file.close()

    response = {
        "message": "customer account successfully verified"
    }

    return jsonify(response)


# route -> "/api/account/<accountId>"
# GET -> get a particular account details
@app.route("/api/account/<accountId>")
def accountDetails(accountId):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    account = {}

    for key, value in accounts.items():
        if(str(key) == str(accountId)):
            return jsonify({
                "message": "success",
                "accountNumber": value["accountNumber"],
                "customerId": value["customerId"],
                "bankId": value["bankId"],
                "accountType": value["accountType"],
                "balance": value["balance"],
                "activation": value["activation"],
                "status": ""
            })

    account.update({
        "message": "failure"
    })

    return jsonify(account)


# route -> "/api/account/<accountNumber>/get"
# GET -> get a particular account details using "account number"
@app.route("/api/account/<accountNumber>/get")
def getAccountDetails(accountNumber):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    account = {}

    for key, value in accounts.items():
        if(str(value["accountNumber"]) == str(accountNumber)):
            return jsonify({
                "message": "success",
                "accountNumber": value["accountNumber"],
                "customerId": value["customerId"],
                "bankId": value["bankId"],
                "accountType": value["accountType"],
                "balance": value["balance"],
                "activation": value["activation"],
                "status": ""
            })

    account.update({
        "message": "failure"
    })

    return jsonify(account)


# route ->> "/api/account/<customerId>/<accountId>"
# POST -> delete / deactivate a particular account
@app.route("/api/account/<customerId>/<accountId>", methods=["POST"])
def deleteAccount(customerId, accountId):
    success = False

    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    response = {}

    for key, value in accounts.items():
        if(str(key) == str(accountId)):
            if(str(customerId) == str(value["customerId"])):
                value["status"] = "deleted"
                success = True

    json_file = open(APP_ROOT+"/models/account.json", "w")
    json_file.seek(0)
    json.dump(accounts, json_file)
    json_file.close()

    if(success):
        response.update({
            "message": "account successfully deleted"
        })
        return jsonify(response)
    else:
        response.update({
            "message": "authorization failed"
        })
        return jsonify(response)


# Transaction Section


# route ->> "/api/transactions"
# GET -> get all transactions
@app.route("/api/transactions")
def transactions():
    json_file = open(APP_ROOT+"/models/transaction.json", "r")
    transactions = json.load(json_file)
    json_file.close()

    return jsonify(transactions)


# route ->> "/api/<accountNumber>/view_balance"
# GET -> get balance and type of a particular account
@app.route("/api/<accountNumber>/view_balance")
def getBalance(accountNumber):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    account = {}

    for key, value in accounts.items():
        if(str(value["accountNumber"]) == str(accountNumber)):
            account.update({
                "accountType": value["accountType"],
                "balance": int(value["balance"])
            })

    return jsonify(account)


# route ->> "/api/<accountNumber>/debit/<amount>"
# GET -> debit balance from a particular account
@app.route("/api/<accountNumber>/debit/<amount>")
def debitBalance(accountNumber, amount):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    response = {
        "message": "failure"
    }

    for _, value in accounts.items():
        if(str(value["accountNumber"]) == str(accountNumber)):
            if((int(value["balance"]) - int(amount)) < 0):
                response.update({
                    "message": "not enough balance in account"
                })
            else:
                value["balance"] = str(int(value["balance"]) - int(amount))
                response.update({
                    "message": "success",
                    "balance": value["balance"]
                })

                transactionId = str(uuid.uuid4())

                transaction = {
                    transactionId: {
                        "transactionType": "Debit",
                        "accountNumber": accountNumber,
                        "amount": amount,
                        "customerId": value["customerId"],
                        "currentBalance": value["balance"]
                    }
                }

                json_file = open(APP_ROOT+"/models//transaction.json", "r")
                transactions = json.load(json_file)
                json_file.close()

                transactions.update(transaction)

                json_file = open(APP_ROOT+"/models/transaction.json", "w")
                json_file.seek(0)
                json.dump(transactions, json_file)
                json_file.close()

                json_file = open(APP_ROOT+"/models/customer.json", "r")
                customers = json.load(json_file)
                json_file.close()

                for key, value2 in customers.items():
                    if(str(key) == str(value["customerId"])):
                        customerEmail = value2["email"]

                message = f"""
                    GP-ATM Transaction Details:\n
                    Transaction Type : Debit,
                    Account Number : {accountNumber},
                    Amount : {amount},
                    Current Balance : {value["balance"]}
                """
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
                server.sendmail('gangpayee@gmail.com', customerEmail, message)
                server.close()

    json_file = open(APP_ROOT+"/models/account.json", "w")
    json_file.seek(0)
    json.dump(accounts, json_file)
    json_file.close()

    return jsonify(response)


# route ->> "/api/<accountNumber>/credit/<amount>"
# GET -> credit balance to a particular account
@app.route("/api/<accountNumber>/credit/<amount>")
def creditBalance(accountNumber, amount):
    json_file = open(APP_ROOT+"/models/account.json", "r")
    accounts = json.load(json_file)
    json_file.close()

    response = {
        "message": "failure"
    }

    for _, value in accounts.items():
        if(str(value["accountNumber"]) == str(accountNumber)):
            if((int(value["balance"]) + int(amount)) < 0):
                response.update({
                    "message": "not enough balance in account"
                })
            else:
                value["balance"] = str(int(value["balance"]) + int(amount))
                response.update({
                    "message": "success",
                    "balance": value["balance"]
                })

                transactionId = str(uuid.uuid4())

                transaction = {
                    transactionId: {
                        "transactionType": "Credit",
                        "accountNumber": accountNumber,
                        "amount": amount,
                        "customerId": value["customerId"],
                        "currentBalance": value["balance"]
                    }
                }

                json_file = open(APP_ROOT+"/models//transaction.json", "r")
                transactions = json.load(json_file)
                json_file.close()

                transactions.update(transaction)

                json_file = open(APP_ROOT+"/models/transaction.json", "w")
                json_file.seek(0)
                json.dump(transactions, json_file)
                json_file.close()

                json_file = open(APP_ROOT+"/models/customer.json", "r")
                customers = json.load(json_file)
                json_file.close()

                for key, value2 in customers.items():
                    if(str(key) == str(value["customerId"])):
                        customerEmail = value2["email"]

                message = f"""

                    GP-ATM Transaction Details:\n
                    Transaction Type : Credit,
                    Account Number : {accountNumber},
                    Amount : {amount},
                    Current Balance : {value["balance"]}
                """
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
                server.sendmail('gangpayee@gmail.com', customerEmail, message)
                server.close()

    json_file = open(APP_ROOT+"/models/account.json", "w")
    json_file.seek(0)
    json.dump(accounts, json_file)
    json_file.close()

    return jsonify(response)


if __name__ == '__main__':
    app.run(port=2000, debug=True)
