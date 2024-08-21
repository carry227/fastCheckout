# -*- coding: utf-8 -*-
"""
@author: joseph@艾鍗學院
'''

SQL commands

#create a table

CREATE TABLE "Class2PID" (
	"class_id"	integer,
	"p_id"	integer NOT NULL,
	"label_name"	text NOT NULL,
	PRIMARY KEY("class_id")
	FOREIGN KEY(p_id) REFERENCES PRODUCTS (p_id)
)


CREATE TABLE PRODUCTS (
    p_id integer primary key,
    p_category text not null,
    p_name text not null,
    p_price integer default 0
)



#insert a record

INSERT INTO Class2PID VALUES (67, 10, 'cell phone')

#browse a table

SELECT * from Class2PID

SELECT Class2PID.p_id,p_name,p_price FROM Class2PID JOIN PRODUCTS ON Class2PID.p_id = PRODUCTS.p_id WHERE Class2PID.class_id = 67


'''

"""
import sqlite3
from datetime import datetime
import json
from sql_cmd import *
from sqlite_utils import *

DataBase='database/example.db'   
db = sqlite3.connect(DataBase)
print('open database:',DataBase)



def run_sql(db,sql,arg=None):
    cursorObj = db.cursor()
    if arg:
        cursorObj.execute(sql,arg)
    else:
        cursorObj.execute(sql)
        
    db.commit()
    
    return cursorObj


def create_tables(db):
    
    cursor=run_sql(db,create_member_table)
    cursor=run_sql(db,create_transaction_table)
    cursor=run_sql(db,create_room_status_table)


def insert_default_data(db):
    
    for _ in range(3):
        cursor=run_sql(db,insert_default_data_to_member)
        cursor=run_sql(db,insert_default_data_to_trans_table)
        cursor=run_sql(db,insert_default_data_to_room_status)    
    

def read_one_table(db,table,conditions_dict=None):
    #read one table
    return fetch_data(db,[table],conditions_dict)    

def fetch_data(db,tables,conditions_dict=None,join_on=None):
   
    # Construct the WHERE clause dynamically if conditions are provided
    where_clause = ''
    values=None
    if conditions_dict:
        conditions = ' AND '.join(f"{key} = ?" for key in conditions_dict.keys())
        where_clause = f"WHERE {conditions}"
        values = tuple(conditions_dict.values())
        
        
    # If there's more than one table and a join condition is specified
    if len(tables) > 1 and join_on:
        table_sql = f"{tables[0]} JOIN {tables[1]} ON {join_on[0]} = {join_on[1]}"
    else:
        table_sql = ', '.join(tables)

    sql = f"SELECT * FROM {table_sql} {where_clause}"
    
   
    #print(sql)
    
    cursor=run_sql(db,sql,values)
   
    return table2dict(cursor)


def fetch_column(db,table):
    # Fetch column names for the desired table
    
    rows=run_sql(db,f"PRAGMA table_info({table})").fetchall()
    # Extract column names
    columns = [column[1] for column in rows]
    return columns
    


def table2dict(cursor):
    # Convert rows into a dictionary

    # Fetch column names
    columns = [description[0] for description in cursor.description]
    # Fetch all rows as dictionaries
    rows_as_dicts = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # use first column (usually PRIMARY key) as a key to dictionary
    rows_as_dicts={ row[columns[0]]:row  for row in rows_as_dicts}
    
    return rows_as_dicts


def insert_data(db, table, data_dict):
    """
    Insert data into a SQLite table from a dictionary.

    """
    # Create the SQL statement dynamically based on the data_dict keys and values
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join('?' for _ in data_dict)
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    
    run_sql(db,sql, tuple(data_dict.values()))
       
def del_data(db,table,conditions_dict):
    """
    Delete a entry from the table based on data_dict(PRIMARY key).

    """
    #delete DELETE FROM member WHERE birthdate = ? AND sex = ?
    conditions = ' AND '.join(f"{key} = ?" for key in conditions_dict.keys())
    sql = f"DELETE FROM {table} WHERE {conditions}" 
    #print(sql)
    run_sql(db,sql, tuple(conditions_dict.values()))
    
#INSERT ORDER
def insert_order(db, items:list):
    sql_orderno = 'select ((case when max(o_id) is null then 0 else max(o_id) end)+1) as new_o_id from order_m'
    get_Orderno = query_db(db, sql_orderno)[0][0]
    #INS Order Detail
    total = 0
    for no, item in enumerate(items, 1):
        p_id = int(item['productId'])
        p_name = item['name']
        p_price = int(item['price'])
        p_qty = int(item['quantity'])
        total += p_price * p_qty
        sql_ins_d = f'INSERT INTO ORDER_D VALUES ({get_Orderno},{no},{p_id},"{p_name}",{p_price},{p_qty})'
        run_sql(db,sql_ins_d)

    #INS ORDER M
    now = datetime.now()
    sql_ins_m = f'INSERT INTO ORDER_M VALUES ({get_Orderno},{now.strftime("%Y%m%d")},{total})'
    run_sql(db,sql_ins_m)
 

    return 0


if __name__ == "__main__":
    
    #create_tables(db)
    #insert_default_data(db)          
    query_data=fetch_data(db,['PRODUCTS'],{'p_category':'Drink'}) #,'sex':'F'
    print(f" query_data 共讀取 {len(query_data)} 筆資料")
    print(query_data)
    query_data=read_one_table(db,'PRODUCTS')
    
   
    print(f" query_data 共讀取 {len(query_data)} 筆資料")
    print(query_data)
  
    print('-------join -------------------')
    
    tables = ['PRODUCTS', 'Class2PID']
    conditions = {
    'PRODUCTS.p_category': 'object',
    'Class2PID.class_id': 67
    }
    
    join_condition = ('Class2PID.p_id', 'PRODUCTS.p_id') 
    
    query_data = fetch_data(db, tables, conditions, join_condition)
    
    print(f" query_data 共讀取 {len(query_data)} 筆資料")
    print(query_data)
    
    insert_order(db,  [{'productId': '3', 'name': '加州蘋果', 'quantity': 1, 'price': 30}, {'productId': '2', 'name': '杏仁巧克力酥片', 'quantity': 1, 'price': 50}, {'productId': '2', 'name': '杏仁巧克力酥片', 'quantity': 1, 'price': 50}, {'productId': '2', 'name': '杏仁巧克力酥片', 'quantity': 1, 'price': 50}])


    '''
    
    del_data_cond={'customer_no': 9}
    del_data(db,'member',{'customer_no': 9})
    del_data_cond={'birthdate': '2020-12-22', 'sex': 'M'}
    #del_data(db,'member',del_data_cond)
    
   

    
    guest_temp={'name': 'joseph',
     'sex': 'M',
     'birthdate': '2020-12-22',
     'email': 'joseph@gmail.com',
     'phone': '12345678',
     'address': 'Taipei',
     'password': '0000',
     'picture': 'pic/joseph.jpg',
     'face_embedding': 'embedd0ing/joseph.npy',
     'create_date': datetime.now().strftime("%Y-%m-%d"),
     'comments': 'dummy data'}
    
    insert_data(db,'member',guest_temp)
    
    trans_temp={'customer_no': 1,
      'room_no': 'R003',
      'credit_card_no': '1234567890',
      'checkin_date': '2023-1-22',
      'checkout_date': '2023-1-24',
      'trans_date':  datetime.now().strftime("%Y-%m-%d"),
      'comments': 'good deal'}
    
    insert_data(db,'trans_table',trans_temp)
    
    room_temp={'room_no': 'R003',
    'room_passwd': 'test@ittraining.com.tw',
    'trans_no': 1,
    'status': 'valid',
    'comments': 'yes!'}
 
    insert_data(db,'room_status',room_temp)
    '''


  