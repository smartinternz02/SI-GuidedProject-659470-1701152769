import re
import os
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config,ClientError


app = Flask(__name__)
app.secret_key =os.urandom(24)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=swd16809;PWD=YwKdLfC6EXVpoXtw;", '', '')

print("connected")

COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "Jf5e7IWW1w-MECWEjSeO8h7JDyxpTa16-QQ0KPyBx8_3"
COS_INSTANCE_CRN ="crn:v1:bluemix:public:cloud-object-storage:global:a/a0de583e4eb64401b18b468751515222:7761627b-6d34-48c4-a04c-9771c3f8e625:bucket:ibm-skillbuildtest"

# cos = ibm_boto3.client("s3",
#                        ibm_api_key_id=COS_API_KEY_ID,
#                        ibm_service_instance_id = COS_INSTANCE_CRN,
#                        config=Config(signature_version="oauth"),
#                        endpoing_url=COS_ENDPOINT)

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
    if 'id' in session:
        return redirect('/Home')
    else:
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
            session['id'] = account['USERID']
            userid = account['USERNAME']
            session['USERNAME'] = account['USERNAME']
            msg = 'Logged in Successfully'
            return render_template('home.html',msg=msg,userid=userid)
        else:
            msg = 'Incorrect Username/Password'
        return render_template('Login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('userid',None)
    return redirect('/')


@app.route('/co2calculator')
def co2():
    if 'id' in session:
        return render_template("co2calculator.html")         
    else:
        return redirect('/')
    
@app.route('/ride_booking',methods=['POST','GET'])
def ride():
    data = []
    if 'id' in session:
        try:
            if request.method == 'GET' and 'lev_form' in request.args:
                # Handle search form submission
                leaving_from = request.args.get('lev_form')
                going_to = request.args.get('going_to')
                sel_date = request.args.get('sel_date')

                sql = "SELECT FULLNAME, PHONENUMBER, LOCATION, DESTINATION, NUMBEROFPEOPLE FROM RIDEPUBLISH WHERE LOCATION=? AND DESTINATION=? AND DATETIME=?"
                stmt = ibm_db.prepare(conn, sql)
                ibm_db.bind_param(stmt, 1, leaving_from)
                ibm_db.bind_param(stmt, 2, going_to)
                ibm_db.bind_param(stmt, 3, sel_date)
                ibm_db.execute(stmt)
                while True:
                    row = ibm_db.fetch_assoc(stmt)
                    if not row:
                        break  # Exit the loop when there are no more rows
                    data.append(row)
                    data = data if data else []
                    return render_template("ride_booking.html",data=data)
            else:
                sql = "SELECT FULLNAME, PHONENUMBER, LOCATION, DESTINATION, NUMBEROFPEOPLE FROM RIDEPUBLISH"
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.execute(stmt)
                data = []
                while True:
                    row = ibm_db.fetch_assoc(stmt)
                    if not row:
                        break  # Exit the loop when there are no more rows
                    data.append(row)
                data = data if data else []
                # print(type(data))
                # print(data)
                return render_template("ride_booking.html",data=data)
        except Exception as e:
            # Handle any exceptions that may occur during database operations
            return f"An error occurred: {str(e)}"
            return render_template("ride_booking.html",data=data)
    else:
            return redirect('/')  




@app.route("/publishDetails1")
def publishing():
    if 'id' in session:
        return render_template("publish.html")
    else:
        return redirect('/')

@app.route("/publish", methods=['POST','GET'])
def publishing1():
    global ProfilePic

    if 'id' in session:        

        sql = "SELECT * FROM REGISTER WHERE USERID="+str(session['id'])
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if request.method == 'POST':
                # ProfilePic = request.files['ProfilePic']
                FullName = request.form['FullName']
                PhoneNumber = request.form['PhoneNumber']
                Email = request.form['Email']
                Password = request.form['Password']
                Location = request.form['Location']
                Destination = request.form['Destination']
                DateTime = request.form['DateTime']
                NumberofPeople = request.form['NumberofPeople']
                insert_sql = "INSERT INTO RIDEPUBLISH VALUES (?,?,?,?,?,?,?,?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt,1,FullName)
                ibm_db.bind_param(prep_stmt,2,PhoneNumber)
                ibm_db.bind_param(prep_stmt,3,Email)
                ibm_db.bind_param(prep_stmt,4,Password)
                ibm_db.bind_param(prep_stmt,5,Location)
                ibm_db.bind_param(prep_stmt,6,Destination)
                ibm_db.bind_param(prep_stmt,7,DateTime)
                ibm_db.bind_param(prep_stmt,8,NumberofPeople)
                ibm_db.bind_param(prep_stmt,9,account['USERID'])
                ibm_db.execute(prep_stmt)
                return redirect('/ride_booking')
    else:
            return redirect('/')
    


        # basepath = os.path.dirname(__file__)

        # filepath = os.path.join(basepath,'profilepic','.jpg')

        # ProfilePic.save(filepath)
        # cos.upload_file(Filenmae=filepath,
        #                 Bucket='profilepictures27', Key=FullName + '.jpg')
        
        # print(ProfilePic)
        # sql = "SELECT * FROM RIDEPUBLISH WHERE USERID="+ str(session['USERID'])
        # stmt = ibm_db.prepare(conn,sql)
        # ibm_db.execute(stmt)
        # row = []
        # while True:
        #     date = ibm_db.fetch_assoc(stmt)
        #     if not data:
        #         break
        #     else:
        #         data['USERID'] = str(data['USERID'])
        #         row.append(data)
        #     print('rows: ',row)
    
    


        

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)