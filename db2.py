import re
import os
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import requests

app = Flask(__name__)
app.secret_key =os.urandom(24)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=swd16809;PWD=YwKdLfC6EXVpoXtw;", '', '')

print("connected")

@app.route('/')
def login():
    if 'id' in session:
        return render_template("home.html")
    else:
        return render_template("Login.html")

@app.route('/Home')
def home():
    if 'id' in session:
        return render_template("home.html")
    else:
        return redirect('/')

@app.route('/register')
def register():
    return render_template("register.html")
    
@app.route('/submit',methods=['GET','POST'])
def register1():
    msg = ''
    if request.method == 'POST':
        Username = request.form['Username']
        Email = request.form['Email']
        Password = request.form['Password']
        MobileNo = request.form['MobileNo']

        sql = "SELECT * FROM REGISTER WHERE Username =?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,Username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',Email):
            msg = 'Invaild email address!'
        else:
            sql = "SELECT count(*) FROM REGISTER"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO  REGISTER VALUES (?,?, ?, ?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, Username)
            ibm_db.bind_param(prep_stmt, 3, Email)
            ibm_db.bind_param(prep_stmt, 4, Password)
            ibm_db.bind_param(prep_stmt, 5, MobileNo)
            ibm_db.execute(prep_stmt)
            return render_template('Login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill the form!'
    return render_template('register.html', msg=msg)

    
@app.route('/submit1',methods=['POST','GET'])
def login1():
    global userid
    msg =''

    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']
        sql = "SELECT * FROM REGISTER WHERE Email=? AND Password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,Email)
        ibm_db.bind_param(stmt,2,Password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin'] = True
            session['userid']=account['USERID']
            session['id'] = account['USERID']
            userid = account['USERNAME']
            session['USERNAME'] = account['USERNAME']
            msg = 'Logged in Successfully'
            return render_template('home.html',msg=msg)
        else:
            msg = 'Incorrect Username/Password'
        return render_template('Login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('userid',None)
    return render_template('Login.html')


@app.route('/co2calculator')
def co2():
    if 'id' in session:
        return render_template("co2calculator.html")
    else:
        return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)