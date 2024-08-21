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



import sqlite3
import json

DataBase='database/example.db'     
db = sqlite3.connect(DataBase,check_same_thread=False)
select_sql="SELECT * FROM PRODUCTS WHERE p_price >= 50"


def run_sql(db,sql):
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    return cursor
    
    
def query_db(db,sql):
    cursor=run_sql(db,sql)
    rows = cursor.fetchall()
    return rows

def query_db_json(db,sql):
    cursor=run_sql(db,sql)
    rows = cursor.fetchall()
    
    
    result=[]
    for row in rows:
   
        print(row)
    '''
        item_template={} 
        item_template['pid']=row[0]
        item_template['p_category']=row[1]
        item_template['p_name']=row[2]
        item_template['p_price']=row[3]
        result.append(item_template)
    '''
    return json.dumps(result) 
    
    return rows

if __name__ == '__main__':
    

    #ret=query_db(db,select_sql)
    #ret=query_db_json(db,select_sql)
    sqlcmd="SELECT Class2PID.p_id,p_name,p_price FROM Class2PID JOIN PRODUCTS ON Class2PID.p_id = PRODUCTS.p_id WHERE Class2PID.class_id = 67"
    
    ret=query_db_json(db,sqlcmd)
    
    
    print(ret)
    
    
    
    