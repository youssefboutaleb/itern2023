from app import mysql, session
from blockchain import Block, Blockchain
import time
from datetime import datetime
#custom exceptions for transaction errors
class InvalidTransactionException(Exception): pass
class InsufficientFundsException(Exception): pass

#what a mysql table looks like. Simplifies access to the database 'crypto'
class Table():
    #specify the table name and columns
    #EXAMPLE table:
    #               blockchain
    # number    hash    previous   data    nonce
    # -data-   -data-    -data-   -data-  -data-
    #
    #EXAMPLE initialization: ...Table("blockchain", "number", "hash", "previous", "data", "nonce")
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
    #EXAMPLE using blockchain: ...getone("hash","00003f73gh93...")
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
def send_amount(username,address, amount):
    #verify that the amount is an integer or floating value
    try: amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.")

    #verify that the user has enough money to send (exception if it is the BANK)
    if  1000< amount < 0:
        raise InsufficientFundsException("the amount should be in 0 , 1000")

    #verify that the user is not sending money to themselves or amount is less than or 0
    #elif sender == recipient or amount <= 0.00:
    #    raise InvalidTransactionException("Invalid Transaction.")

    #verify that the recipient exists
    elif isnewuser(username):
        raise InvalidTransactionException("User Does Not Exist.")

    #update the blockchain and sync to mysql
    blockchain = get_blockchain()[0]
    number = len(blockchain.chain) + 1
    data = "%s-->%s" %(address, amount)
    blockchain.mine(Block(number, data=data))
    sync_blockchain(blockchain)
def update_profil(username,start,end):
    #verify that the user exists
    if isnewuser(username):
        raise InvalidTransactionException("User Does Not Exist.")
    users = Table("users","profil","address")
    user = users.getone("username", username)
    address =user.get('address') 
    blockchain,timelist=get_blockchain()
    chain=blockchain.chain
    l=[]
    for index,time in enumerate(timelist):
        if start<time.date()<end:
            datablock=chain[index].data.split('-->')
            if datablock[0]==address:
                l.append(float(datablock[1]))
    if l !=[]:
        mean_consommation= sum(l) / len(l)
        if mean_consommation>50:
            #sql_raw
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET profil = 'high' WHERE username = %s", (username,))
            mysql.connection.commit()
            cur.close()


        

    #update the blockchain and sync to mysql
    blockchain = get_blockchain()[0]
    number = len(blockchain.chain) + 1
    data = "%s-->%s" %(start, end)
    blockchain.mine(Block(number, data=data))
    sync_blockchain(blockchain)

#get the balance of a user
def get_consommation(username):
    users = Table("users","address","name", "email", "username", "password")
    user = users.getone("username", username)
    address =user.get('address') 
    consommation = 0.00
    blockchain = get_blockchain()[0]

    #loop through the blockchain and update balance
    for block in blockchain.chain:
        data = block.data.split("-->")
        if address == data[0]:
            consommation += float(data[1])
        
    return consommation

#get the blockchain from mysql and convert to Blockchain object
def get_blockchain():
    blockchain = Blockchain()
    timelist=[]
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce","timestamp_column")
    for b in blockchain_sql.getall():
        blockchain.add(Block(int(b.get('number')), b.get('previous'), b.get('data'), int(b.get('nonce'))))
        timelist.append(b.get('timestamp_column'))
    return blockchain,timelist

#update blockchain in mysql table
def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce","timestamp_column")
    #blockchain_sql.deleteall()

    #for block in blockchain.chain:
    #    blockchain_sql.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)
    block=blockchain.chain[-1]
    blockchain_sql.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce,datetime.fromtimestamp(time.time()))
