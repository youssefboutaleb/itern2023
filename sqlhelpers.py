import json
import joblib
import numpy as np

from web3 import Web3
from app import mysql, session
from blockchain import Block, Blockchain
import time
from datetime import datetime


web3_provider = Web3.HTTPProvider("HTTP://127.0.0.1:7545")
web3 = Web3(web3_provider)
contract_address = web3.to_checksum_address("0xEbabDe71f37Ce232553f9c4a41E08AA559539482") #local address : 0x3223B1B17eD2155422cb81e191325d083DDbCbe4

#abi = json.loads('[{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"consomations","outputs":[{"internalType":"uint256","name":"time","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getConsomation","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"}],"name":"getProfile","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sendConsomation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"times","type":"uint256[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"sendConsomation_csv","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"},{"internalType":"string","name":"newProfile","type":"string"}],"name":"updateProfile","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"users","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]')
abi = '[{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sendConsomation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"times","type":"uint256[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"sendConsomation_csv","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"},{"internalType":"string","name":"newProfile","type":"string"}],"name":"updateProfile","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"consomations","outputs":[{"internalType":"uint256","name":"time","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getConsomation","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"}],"name":"getProfile","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"users","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'

contract = web3.eth.contract(address=contract_address, abi=abi)



#custom exceptions for transaction errors
class InvalidTransactionException(Exception): pass
class InsufficientFundsException(Exception): pass

#what a mysql table looks like. Simplifies access to the database 'crypto'
class Table():
    #specify the table name and columns
    #EXAMPLE table:
    #               users
    # address  name      username email   password 
    # -data-   -data-    -data-   -data-  -data-
    #
    #EXAMPLE initialization: ...Table("users", "address", "name", "username", "email", "password")
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(%s)" %",".join(args)
        self.columnsList = args

        #if table does not already exist, create it.
        if isnewtable(table_name):
            create_data = ""
            for column in self.columnsList:
                create_data += "%s varchar(100)," %column

            cur = mysql.connection.cursor() #create the table
            cur.execute("CREATE TABLE %s(%s)" %(self.table, create_data[:len(create_data)-1]))
            cur.close()

    #get all the values from the table
    def getall(self):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s" %self.table)
        data = cur.fetchall(); return data

    #get one value from the table based on a column's data
    #EXAMPLE using users: ...getone("username","username_example...")
    def getone(self, search, value):
        data = dict(); cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %(self.table, search, value))
        if result > 0: data = cur.fetchone()
        cur.close(); 
        return data

    #delete a value from the table based on column's data
    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s where %s = \"%s\"" %(self.table, search, value))
        mysql.connection.commit(); cur.close()

    #delete all values from the table.
    def deleteall(self):
        self.drop() #remove table and recreate
        self.__init__(self.table, *self.columnsList)

    #remove table from mysql
    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" %self.table)
        cur.close()

    #insert values into the table
    def insert(self, *args):
        data = ""
        for arg in args: #convert data into string mysql format
            data += "\"%s\"," %(arg)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO %s%s VALUES(%s)" %(self.table, self.columns, data[:len(data)-1]))
        mysql.connection.commit()
        cur.close()

#execute mysql code from python
def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

#check if table already exists
def isnewtable(tableName):
    cur = mysql.connection.cursor()

    try: #attempt to get data from table
        result = cur.execute("SELECT * from %s" %tableName)
        cur.close()
    except:
        return True
    else:
        return False

#check if user already exists
def isnewuser(username):
    #access the users table and get all values from column "username"
    users = Table("users", "name", "username", "email", "password")
    data = users.getall()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True

#send money from one user to another
def send_amount_contract(address,amount):

    # update the blockchain and sync to mysql


    # Specify the 'from' address for the transaction
    web3.eth.default_account = address
    # Build the transaction data
    transaction = contract.functions.sendConsomation(amount).transact()

    # Sign and send the transaction
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction)
    Contract = web3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )

def send_amounts_contract(address, times, amounts):
    # update the blockchain and sync to MySQL

    # Specify the 'from' address for the transaction
    web3.eth.default_account = address

    # Build the transaction data
    contract_function = contract.functions.sendConsomation_csv(times, amounts)
    transaction = contract_function.transact()

    # Sign and send the transaction
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction)
    Contract = web3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )

def anomaly_detection(address):
    web3.eth.default_account = address

    # Build the transaction data
    contract_function = contract.functions.getProfile(address)
    profil = contract_function.call()
    contract_function =contract.functions.getConsomation(address)
    times,amounts=contract_function.call()
    #profil from 0 to 9
    if profil=="high":
        profil=7
    elif profil=="low":
        profil=2
    else : profil =4
    #standard seuil is seuil=50

    l = []
    model = joblib.load('model/logistic_regression_model.pkl')
    for time,amount in zip(times,amounts):
        # Convert timestamp to a datetime object
        dt_object = datetime.fromtimestamp(time)
        # Extract the required features
        hourofday = dt_object.hour
        minuteofhour = dt_object.minute
        dayofweek = dt_object.weekday()  # Monday: 0, Sunday: 6
        dayofmonth = dt_object.day
        monthofyear = dt_object.month
        year = dt_object.year
        dataEntry=[profil,amount/1000,hourofday,minuteofhour,dayofweek,dayofmonth,monthofyear,year-2021]
        dataEntry=np.array([dataEntry])
        prediction = model.predict(dataEntry)
        if prediction==[1]:
            l.append((time,amount))

    return l




        


def update_profil(username,start,end):
    #verify that the user exists
    if isnewuser(username):
        raise InvalidTransactionException("User Does Not Exist.")
    users = Table("users","address")
    user = users.getone("username", username)
    address =user.get('address')
    web3.eth.default_account = address
    l = []
    times, amounts = contract.functions.getConsomation(address).call()

    for i in range(len(times)):
        time = datetime.fromtimestamp(times[i])
        if start < time.date() < end:
            l.append(amounts[i])
    if l !=[]:
        mean_consommation= sum(l) / len(l)
        if mean_consommation>50:
            #execution="UPDATE users SET profil = 'high' WHERE username = %s", (username,)
            #sql_raw(execution)

            # Build the transaction data
            transaction = contract.functions.updateProfile(address,"high").transact()

            # Sign and send the transaction
            tx_receipt = web3.eth.wait_for_transaction_receipt(transaction)
            Contract = web3.eth.contract(
                address=tx_receipt.contractAddress,
                abi=abi
            )

            
            

        

    
#get the consommation of a user
def get_consommation(username):
    users = Table("users","profil","address")
    user = users.getone("username", username)
    address =user.get('address')
    web3.eth.default_account = address
    
    times, amounts = contract.functions.getConsomation(address).call()
        
    return times, amounts

