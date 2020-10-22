from flask import *
import os
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "ahfghj"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    if (request.cookies.get('email')):
        return render_template('login.html')

@app.route('/enter', methods=['POST'])
def enter():
    email = request.form.get('email')
    password = request.form.get('password')
    if email == "gangpayee@gmail.com" and password == "GangPayee@gcetts":
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('email', email, max_age=60*60*24*7)
        return resp
    else:
        flash("Unknown Credentials", "danger")
        return redirect(url_for('login'))

@app.route('/')
def index():
    if (request.cookies.get('email')):
        return render_template('addBank.html')
    else:
        return redirect(url_for('login'))

@app.route('/addBank')
def addBank():
    if (request.cookies.get('email')):
        return render_template('addBank.html')
    else:
        return redirect(url_for('login'))

@app.route('/registerBank', methods=['POST'])
def registerBank():
    if (request.cookies.get('email')):
        name=request.form['name']
        ifsc=request.form['ifsc']
        address=request.form['address']
        branch=request.form['branch']
        bemail=request.form['bemail']
        phone=request.form['phone']
        data={
            'name':name,
            "ifsc": ifsc,
            "address": address,
            "branch": branch,
            "email": bemail,
            "phone": phone
        }
        res=requests.post('http://127.0.0.1:2000/api/bank',json=data)
        status = res.json()
        flash("Bank registered successfully")
        return redirect(url_for('addBank'))
    else:
        return redirect(url_for('login'))

@app.route('/getBank')
def getBank():
    if (request.cookies.get('email')):
        banks = []
        res = requests.get('http://127.0.0.1:2000/api/bank')
        data = res.json()
        for key, value in data.items():
            banks.append(value)
        return render_template('getBank.html',banks=banks)

    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
