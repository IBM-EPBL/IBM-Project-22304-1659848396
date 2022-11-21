# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 14:27:20 2022

@author: user
"""


from flask import Flask,render_template, request,redirect,url_for,session
import ibm_db
import re

app=Flask(__name__)
app.secret_key= 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nms09877;PWD=0AEuG3bImXTyoxfU",'','')


@app.route('/')
def home():
    return render_template('home.html') 


@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['user']
        password = request.form['passw']
        sql = "SELECT * FROM user WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account['USERNAME']
            userid=  account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'Logged in successfully !'
            return render_template('display.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

        

   
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone']
        city = request.form['city']
        covid_status = request.form['infect']
        blood_group = request.form['blood']
        password = request.form['passw']
        sql = "SELECT * FROM user WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO  user VALUES (?, ?, ?, ? , ? , ? , ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, phone_number)
            ibm_db.bind_param(prep_stmt, 4, city)
            ibm_db.bind_param(prep_stmt, 5, covid_status)
            ibm_db.bind_param(prep_stmt, 6, blood_group)
            ibm_db.bind_param(prep_stmt, 7, password)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/display', methods =['GET', 'POST'])
def display():
    if request.method == 'POST':
        blood_group = request.form['blood']
        city = request.form['city']
        sql ="SELECT * FROM user WHERE blood_group = '{}' and city = '{}';".format(blood_group,city)
        prep_stmt = ibm_db.exec_immediate(conn, sql)
        # prep_stmt = ibm_db.prepare(conn, sql)
        # ibm_db.bind_param(prep_stmt, 1, blood_group)
        # ibm_db.bind_param(prep_stmt, 2, city)
        # ibm_db.execute(prep_stmt)
        data = []
        while ibm_db.fetch_row(prep_stmt) != False:
            print ("The Employee number is : ",  ibm_db.result(prep_stmt, "USERNAME"))
            print ("The last name is : ", ibm_db.result(prep_stmt, "PHONE_NUMBER") )
            data.append([ibm_db.result(prep_stmt, "USERNAME"),ibm_db.result(prep_stmt, "PHONE_NUMBER")])
        print("datadisplay",data)
        msg = 'Data Fetch successful'
        return render_template('display.html',data = data)
    return render_template('display.html')



@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('login.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0')
    
    