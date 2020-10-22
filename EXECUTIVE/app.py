from flask import *
import os
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "ahfghj"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
url='http://127.0.0.1:2000'

@app.route('/login')
def login():
    res = requests.get(f'{url}/api/bank/branches')
    branches = res.json()
    return render_template('login.html', branches=branches)


@app.route('/enter', methods=['POST'])
def enter():
    email = request.form.get('email')
    password = request.form.get('password')
    details = {
        "email": email,
        "password": password
    }

    res1 = requests.post(
        f'{url}/api/executive/login', json=details)
    loginStatus = res1.json()
    eid = loginStatus['id']

    if loginStatus['message'] == "success":
        res2 = requests.get(f'{url}/api/executive/{eid}')
        exe = res2.json()

        for k, v in exe.items():
            if v['status'] == "not-verified":
                flash(v['status'], "orange lighten-5")
                return redirect(url_for('login'))

        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('id', eid, max_age=60*60*24*7)
        return resp

    else:
        flash(loginStatus['message'], "red lighten-5")
        return redirect(url_for('login'))


@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    employeeId = request.form.get('empid')
    branchId = request.form.get('branch')
    res = requests.get(f'{url}/api/bank')
    banks = res.json()

    for key,_ in banks.items():
        if (str(key) == branchId):
            bankId = str(key)

    data = {
        "name": name,
        "email": email,
        "password": password,
        "employeeId": employeeId,
        "bankId": bankId
    }
    res = requests.post(f'{url}/api/executive', json=data)
    status = res.json()
    flash("Executive Created Successfully; waiting to be verified", "warning")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if (request.cookies.get('id')):
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('id', expires=0)
        return resp


@app.route('/')
def index():
    if (request.cookies.get('id')):
        eid = request.cookies.get('id')
        res2 = requests.get(f'{url}/api/executive/{eid}')
        exe = res2.json()
        return render_template('index.html', exe=exe)
    else:
        return redirect(url_for('login'))


@app.route('/unverified')
def unverified():
    if (request.cookies.get('id')):

        res = requests.get(
            f'{url}/api/accounts/pending_verifications')
        accounts = res.json()

        eid = request.cookies.get('id')
        res2 = requests.get(f'{url}/api/executive/{eid}')
        exe = res2.json()
        unverified = []

        for _,value in exe.items():
            bankId=value['bankId']

        for k,v in accounts.items():
            if k == bankId:
                unverified.append(v)

        return render_template('unverified.html', unverified=unverified, exe=exe)


@app.route('/verified/<aid>')
def verified(aid):
    if (request.cookies.get('id')):
        eid = request.cookies.get('id')
        res2 = requests.get(f'{url}/api/executive/{eid}')
        exe = res2.json()
        res = requests.get(f'{url}/api/account/{aid}/verify')
        verify = res.json()
        flash(verify['message'], "")
        return render_template('index.html', exe=exe)
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
