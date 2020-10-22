from flask import *
import requests
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "ahfghjtttytytyr"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
url = "https://gpbankapi.pythonanywhere.com/"


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/enter', methods=['POST'])
def enter():
    email = request.form.get('inemail')
    password = request.form.get('inpassword')
    details = {
        "email": email,
        "password": password
    }
    res = requests.post(f'{url}/api/customer/login', json=details)
    status = res.json()
    cid = status['id']
    if status['message'] == "success":
        res2 = requests.get(f'{url}/api/customer/{cid}')
        cust = res2.json()

        for k, v in cust.items():
            if v['status'] == "not-verified":
                flash(v['status'], "orange lighten-5")
                return redirect(url_for('login'))
            elif v['activation'] == "deactivated":
                flash(v['activation'], "orange lighten-5")
                return redirect(url_for('login'))
            else:
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('custid', cid, max_age=60*60*24*7)
                return resp


@app.route('/register', methods=['POST'])
def register():
    name = request.form.get("name")
    address = request.form.get("address")
    email = request.form.get("email")
    password = request.form.get("password")
    dob = request.form.get("dob")
    phone = request.form.get("phone")

    data = {
        "name": name,
        "address": address,
        "email": email,
        "dob": dob,
        "password": password,
        "phone": phone
    }
    res = requests.post(f'{url}/api/customer', json=data)
    status = res.json()
    flash("Customer Created Successfully; waiting to be authenticated-please check your mail", "warning")
    return redirect(url_for('login'))


@app.route('/')
def index():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res2 = requests.get(f'{url}/api/customer/{cid}')
        data = res2.json()
        cus = []
        for _, v in data.items():
            cus.append(v)
        return render_template('index.html', cus=cus)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if (request.cookies.get('custid')):
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('custid', expires=0)
        return resp


@app.route('/profile')
def profile():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res2 = requests.get(f'{url}/api/customer/{cid}')
        data = res2.json()
        cus = []
        for _, v in data.items():
            cus.append(v)
        colors = ['blue', 'orange', 'pink', 'red',
                  'purple', 'cyan', 'yellow darken-3', 'teal']
        return render_template('profile.html', cus=cus, color=colors, total=zip(cus, colors))
    else:
        return redirect(url_for('login'))


@app.route('/delprofile')
def delprofile():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res2 = requests.delete(f'{url}/api/customer/{cid}')
        data = res2.json()
        flash(data['message'])
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('custid', expires=0)
        return resp


@app.route('/checkAccounts')
def checkAccounts():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res = requests.get(f'{url}/api/account')
        data = res.json()
        res2 = requests.get(f'{url}/api/customer/{cid}')
        data2 = res2.json()
        accountsD = []
        accounts = []
        cus = []
        for _, v in data2.items():
            cus.append(v)

        for _, v in data.items():
            if v['customerId'] == cid and v['status'] == "" and v['activation'] == "activated":
                accounts.append(v)
            elif v['customerId'] == cid and v['status'] == "" and v['activation'] == "deactivated":
                accountsD.append(v)
        # print(accountsD)

        colors = ['blue', 'orange', 'pink', 'red',
                  'purple', 'cyan', 'yellow darken-3', 'teal']
        return render_template('checkAccount.html', cus=cus, colors=colors, total=zip(accounts, colors))
    else:
        return redirect(url_for('login'))


@app.route('/deleteAccount')
def deleteAccount():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        cid = request.cookies.get('custid')
        res = requests.get(f'{url}/api/account')
        data = res.json()
        res2 = requests.get(f'{url}/api/customer/{cid}')
        data2 = res2.json()
        accounts = []
        cus = []
        aid = []
        for _, v in data2.items():
            cus.append(v)

        for k, v in data.items():
            if v['customerId'] == cid and v['status'] == "" and v['activation'] == 'activated':
                accounts.append(v)
                aid.append(k)

        colors = ['blue', 'orange', 'pink', 'red',
                  'purple', 'cyan', 'yellow darken-3', 'teal']
        return render_template('deleteAccount.html', cus=cus, accounts=accounts, colors=colors, aid=aid, total=zip(accounts, colors, aid))
    else:
        return redirect(url_for('login'))


@app.route('/delAccount/<aid>', methods=['POST'])
def delAccount(aid):
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res = requests.post(f'{url}/api/account/{cid}/{aid}')
        status = res.json()
        flash(status['message'])
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/addAccount')
def addAccount():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        res2 = requests.get(f'{url}/api/customer/{cid}')
        data = res2.json()
        cus = []
        res = requests.get(f'{url}/api/bank/branches')
        branches = res.json()

        for _, v in data.items():
            cus.append(v)

        return render_template('addAccount.html', cus=cus, branches=branches)
    else:
        return redirect(url_for('login'))


@app.route('/registerAccount', methods=['POST'])
def registerAccount():
    if (request.cookies.get('custid')):
        cid = request.cookies.get('custid')
        bankId = request.form.get('branch')
        accType = request.form.get('accType')
        data = {
            'customerId': cid,
            'bankId': bankId,
            'accountType': accType
        }
        res = requests.post(f'{url}/api/account', json=data)
        status = res.json()

        flash(status['message'])
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
