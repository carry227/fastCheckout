# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 12:02:55 2023

@author: joseph@艾鍗學院

PRAGMA table_info(member)

"""
### Create table ########
create_member_table=f'''
     CREATE TABLE IF NOT EXISTS member (  
     customer_no INTEGER PRIMARY KEY AUTOINCREMENT,
     name TEXT,
     sex TEXT,
     birthdate TEXT,
     email TEXT,
     phone TEXT,
     address TEXT,   
     password TEXT,
     picture TEXT,
     face_embedding INTEGER,
     create_date TEXT,
     comments TEXT    
  )'''
         
create_transaction_table=f'''
     CREATE TABLE IF NOT EXISTS trans_table (    
     trans_no INTEGER PRIMARY KEY AUTOINCREMENT,
     customer_no INTEGER NOT NULL,
     room_no TEXT NOT NULL,
     credit_card_no TEXT,
     checkin_date TEXT NOT NULL,
     checkout_date TEXT NOT NULL,
     trans_date TEXT NOT NULL,    
     comments TEXT, 
     FOREIGN KEY(customer_no) REFERENCES member (customer_no)
                                         
  )'''         


                
create_room_status_table=f'''
     CREATE TABLE IF NOT EXISTS room_status (  
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     room_no TEXT,
     room_passwd TEXT,
     trans_no INTEGER,
     status TEXT,      
     comments TEXT,   
     FOREIGN KEY(trans_no) REFERENCES trans_table(trans_no)                
  )'''     
      
######Insert data#############

insert_default_data_to_member=f'''
INSERT INTO member (
name,sex,birthdate,email,phone,address,password,
picture,face_embedding,create_date,comments)
VALUES('it','M','2000-1-22','db@ittraining.com.tw','23167736',
'Taipei','1234','pic/C001.jpg','embedding/C001.npy','2000-1-22','test'
)'''

insert_default_data_to_trans_table=f'''
INSERT INTO trans_table (
customer_no,room_no, credit_card_no, checkin_date,
checkout_date, trans_date, comments)
VALUES(1, 'R001', '1234567890','2023-1-22','2023-1-24','2023-1-20',"good deal"
)'''



insert_default_data_to_room_status=f'''
INSERT INTO room_status (
room_no,room_passwd,trans_no,status,comments)
VALUES('R001', 'db@ittraining.com.tw','1','valid','good!'
)'''


########Query data############
query_member_table=f'''
select * from member
'''

query_with_cond=f'''
SELECT * FROM member WHERE name = 'joseph' AND sex = 'F'
'''

##Join two tables
query_data=f'''
SELECT * FROM member JOIN trans_table 
ON member.customer_no = trans_table.customer_no
WHERE member.customer_no = 2 AND trans_table.room_no = 'R002'
'''