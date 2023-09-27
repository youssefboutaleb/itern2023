#!/usr/bin/python
# -*- coding: utf-8 -*-
# import flask dependencies for web GUI
import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging ,jsonify
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
from flask import send_file
from hashlib import sha256
# web3 libs
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address
import csv




#import other functions and classes
from sqlhelpers import *
from forms import *

#other dependencies
import time

#initialize the app
app = Flask(__name__, template_folder='templates')


#configure mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'google178'
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_UNIX_SOCKET'] = '/var/run/mysqld/mysqld.sock'  
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Configure web3 provider

web3_provider = Web3.HTTPProvider("HTTP://127.0.0.1:7545") #local : HTTP://127.0.0.1:7545
web3 = Web3(web3_provider)


#initialize mysql
mysql = MySQL(app)

#wrap to define if the user is currently logged in from session
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login.", "danger")
            return redirect(url_for('login'))
    return wrap

#log in the user by updating session
def log_in_user(username):
    users = Table("users", "name", "username", "email", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')
    session['address'] = user.get('address')  # Store Metamask address in session

#Registration page
@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users","address","name", "email", "username", "password")

    #if form is submitted
    if request.method == 'POST' and form.validate():
        #collect form data
        username = form.username.data
        email = form.email.data
        name = form.name.data

        #make sure user does not already exist
        if isnewuser(username):
            #add the user to mysql and log them in
            account = Account.create()
            #private_key = account.private_Key.hex()
            address = to_checksum_address(account.address)
            password = sha256_crypt.encrypt(form.password.data)
            users.insert(address,name,email,username,password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)






#Login page
@app.route("/login", methods = ['GET', 'POST'])
def login():

    #if form is submitted
    if request.method == 'POST':
        #collect form data
        username = request.form['username']
        candidate = request.form['password']

        #access users table to get the user's actual password
        users = Table("users", "name", "username", "email", "password")
        user = users.getone("username", username)
        accPass = user.get('password')

        #if the password cannot be found, the user does not exist
        if accPass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            #verify that the password entered matches the actual password
            if sha256_crypt.verify(candidate, accPass):
                #log in the user and redirect to Dashboard page
                log_in_user(username)
                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                #if the passwords do not match
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')

#Profil page
@app.route("/Profil", methods = ['GET', 'POST'])
@is_logged_in
def profil():
    form = ProfilForm(request.form)
    balance = sum(get_consommation(session.get('username'))[1])

    #if form is submitted
    if request.method == 'POST':
        try:
            #attempt to execute the transaction
            update_profil(session.get('username'), form.start.data, form.end.data)
            flash(" profile updated successfully !", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('Profil.html', balance=balance, form=form, page='Profil')

#Transaction page
@app.route("/Transact", methods = ['GET', 'POST'])
@is_logged_in
def transact():
    form = TransactForm(request.form)
    users = Table("users","address","name", "email", "username", "password")
    username=session.get('username')
    user = users.getone("username", username)

    address =user.get('address')
    balance = sum(get_consommation(username)[1])

    if request.method == 'POST':
        #attempt to transact amount
        try:
            send_amount_contract(address, int(form.amount.data))
            flash("Transaction Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('Transact.html', balance=balance, form=form, page='Transact')

@app.route("/MultipleTransact", methods=['GET', 'POST'])
@is_logged_in
def MultipleTransact():
    form = MultiTransactForm(request.form)
    users = Table("users", "address", "name", "email", "username", "password")
    username = session.get('username')
    user = users.getone("username", username)

    address = user.get('address')
    balance = sum(get_consommation(username)[1])

    if request.method == 'POST':
        # attempt to transact amounts from the CSV
        try:
            times = [int(time) for time in form.times.data.split(",")]
            amounts = [int(amount) for amount in form.amounts.data.split(",")]

            if len(times) != len(amounts):
                raise ValueError("Timestamps and amounts must have the same number of elements.")

            send_amounts_contract(address, times, amounts)
            flash("Transactions Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('MultipleTransact.html', balance=balance, form=form, page='MultipleTransact')





# New route to handle file upload and perform transactions


@app.route("/Transact_CSV", methods=['GET', 'POST'])
def transact_csv():
    print("hello")
    form = TransactcsvForm(request.form)
    users = Table("users", "address", "name", "email", "username", "password")
    username = session.get('username')
    user = users.getone("username", username)

    address = user.get('address')
    balance = sum(get_consommation(username)[1])

    if request.method == 'POST' :
        csv_file = request.files['csv_file']
        print("enter")

        times = []
        amounts = []

        with csv_file.stream as file_stream:
            csv_reader = csv.DictReader(file_stream.read().decode('utf-8').splitlines())

            for row in csv_reader:
                times.append(int(row['times']))
                amounts.append(int(row['amounts']))
        print(times,amounts)
        send_amounts_contract(address, times, amounts)
        flash("Transactions Successful!", "success")

        return redirect(url_for('dashboard'))

    return render_template('Transact_CSV.html', balance=balance, form=form, page='Transact_CSV')

#anomaly page
@app.route("/anomaly", methods = ['GET', 'POST'])
@is_logged_in
def anomaly():
    users = Table("users","address","name", "email", "username", "password")
    username=session.get('username')
    user = users.getone("username", username)
    address =user.get('address')     
    
    balance = sum(get_consommation(username)[1])
    l=[]
    if request.method == 'POST':
        #attempt to transact amount
        try:
            l= anomaly_detection(address)
            flash("anomaly detection  Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        #return redirect(url_for('dashboard'))

    return render_template('anomaly.html', balance=balance, l=l, page='anomaly',datetime=datetime)




# Route for downloading anomaly detection results as a .txt file
@app.route("/download_anomaly_results", methods=['POST'])
@is_logged_in
def download_anomaly_results():
    users = Table("users", "address", "name", "email", "username", "password")
    username = session.get('username')
    user = users.getone("username", username)
    address = user.get('address')
    l = anomaly_detection(address)

    if not l:
        flash("No anomaly detected.", "danger")
        return redirect(url_for('anomaly'))

    # Create a .txt file with the anomaly detection results
    filename = f"anomaly_results_{username}.txt"
    file_path = os.path.join(app.root_path, filename)

    with open(file_path, 'w') as file:
        for detection in l:
            file.write(f"{datetime.fromtimestamp(detection)}\n")

    # Send the .txt file as a response for download
    return send_file(file_path, as_attachment=True)





#logout the user. Ends current session
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout success", "success")
    return redirect(url_for('login'))


#Dashboard page
@app.route("/dashboard")
@is_logged_in
def dashboard():
    times, amounts = get_consommation(session.get('username'))
    

    ct = time.strftime("%I:%M %p")
    if not web3.is_connected():
        flash("Ethereum node is not connected", "danger")
    else :
        flash("Ethereum node is  connected", "success")
    return render_template('dashboard.html', balance=sum(amounts), session=session, ct=ct, amounts=amounts,timelist=times,zip=zip, page='dashboard')

#Index page
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

#Run app
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.debug = True
    app.run()


