from flask import Flask, render_template, send_file, request, url_for
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime
import json
import cv2
from ultralytics import YOLO
from PIL import Image
from gevent.pywsgi import WSGIServer
import pandas as pd
from db import *
from sqlite_utils import *
import os

#names: {0: 'Lollipop', 1: 'cookie', 2: 'fruit', 3: 'noodles'}
app = Flask(__name__)
# http://127.0.0.1:3000

@app.route('/')
def index():
   return render_template('index.html')
#    return app.send_static_file('index.html')

#定點結帳    
@app.route('/video')
def goto_video():
    return render_template('html5_camera_1.html')

#流動線結帳
@app.route('/video2')
def goto_video2():
    return render_template('html5_camera_2.html')

#訂單名細查詢    
@app.route('/item')
def get_item():
  return render_template('viewreport.html')

#Get all prods
@app.route('/prods', methods=['GET'])
def get_prods():
    sql = 'Select * from PRODUCTS Order by p_id ASC'
    return render_template('prods.html', prods = run_sql(db, sql))

#Get prod
@app.route('/prods/<int:pid>', methods=['Get'])
def get_prod(pid):
    sql = f"SELECT * from PRODUCTS where p_id='{pid}'"   
    return render_template('prods.html', prods = run_sql(db, sql))
#Create prod
#Update prod
#Del prod
@app.route('/delprod/<int:pid>', methods=['DELETE'])
def del_prod(pid):
    sql = f"Delete from PRODUCTS where p_id='{pid}'"
    run_sql(db, sql)
    return url_for('/prods')

#load YOLO model
model = YOLO('model/best-m401.pt')

#偵測圖片是否有訓練類別
def detecte_objects(image_path):
    # Load image
    image = cv2.imread(image_path)
    
    results = model.predict(image, conf=0.5) 
    rectangles=results[0].boxes.xyxy.tolist()
    cls=results[0].boxes.cls.tolist()
    conf=results[0].boxes.conf.tolist()
    # Add rectangles to the plot
    detected_objs={}
    objs_index=0
    
    for rect,c,prob in zip(rectangles,cls,conf):
        print('-->',rect,c,prob)
        if int(c) not in class_product_tbl.keys() :  #not in the table 
            print('class id ',int(c),' is not included')
            continue
        
        detected_objs[objs_index]={'label':class_product_tbl[int(c)]['label_name'],'conf':prob,\
        'p_id':class_product_tbl[int(c)]['p_id'],'p_name':class_product_tbl[int(c)]['p_name'],'p_price':class_product_tbl[int(c)]['p_price']}        
        
        if c==0:
            color=(0, 255, 0)
        elif c==1:
            color=(0, 0, 255)
        elif c==2:
            color=(255, 0, 0)
        else:
            color=(0, 255, 255)
            
        x1,y1,x2,y2= list(map(int,rect))

        #print(x1,y1,x2,y2)
        cv2.rectangle(image,(x1, y1), (x2, y2), color,2)
        objs_index+=1
    
    # Encode image to JPEG format
    _, buffer = cv2.imencode('.jpg', image)
    # Convert to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64,detected_objs

#-------------websocket------------------------    
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# 以目前時間為檔名存檔
def save_img(msg):
    filename=datetime.now().strftime("%Y%m%d-%H%M%S")+'.png'
    base64_img_bytes = msg.encode('utf-8')
    with open('./upload/'+filename, "wb") as save_file:
        save_file.write(base64.decodebytes(base64_img_bytes))
    return './upload/'+filename

#user defined event 'client_event'
@socketio.on('client_event')
def client_msg(msg):
    #print('received from client:',msg['data'])
    emit('server_response', {'data': msg['data']}, broadcast=False) #include_self=False

#user defined event 'connect_event'
@socketio.on('connect_event')   
def connected_msg(msg):
    print('received connect_event')
    emit('server_response', {'data': msg['data']})
    
#user defined event 'capture_event'
@socketio.on('capture_event')   
def handle_capture_event(msg):
    print('received capture_event')
    #print(msg)
    filepath=save_img(msg)
    
    img_base64,objs=detecte_objects(filepath)
    
    #here we just send back the original image to browser.
    #maybe, you can do image processinges before sending back 
    emit('object_detection_event', img_base64, broadcast=False)
    emit('detected_objects',  {'objs': json.dumps(objs)}, broadcast=False)
    
#------SQLite stuff-----------------
from sqlite_utils import *

@socketio.on('new_item_from_pos')
def form_pos(classid):
    pos_item = [{'p_id': class_product_tbl[int(classid)]['p_id'],
                 'p_name': class_product_tbl[int(classid)]['p_name'],
                 'p_price': class_product_tbl[int(classid)]['p_price']}]
    
    emit('new_item_event', {'data': json.dumps(pos_item) }, broadcast=True)

#carter add
# 接收前端皆漲的資料F
@socketio.on('checkout_event')
def handle_checkout(data):
    items = data['items']
    print("接收到的購物明细：", items)
    print('共給筆：',len(items))
    # 进行数据库存储或其他操作
    #insert_order(db, items:list)
    insert_order(db, items)
    emit('order_saved', {'status': '訂單已成功存檔！'}, broadcast=True)
    
#carter add
@app.route('/download', methods=['GET'])
def download():
    global current_order_details
    if not current_order_details:
        return "No order details available to download.", 400
    
    try:
        order_id = current_order_details['order_id']
        order_date = current_order_details['order_date']
        details_df = current_order_details['details']
        total_amount = current_order_details['total_amount']
        
        filename = f"order_{order_id}.xlsx"
        filepath = os.path.join('downloads', filename)
        
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('OrderDetails')
            
            # Format for bold text
            bold = workbook.add_format({'bold': True})
            
            # Write order ID and date
            worksheet.write(0, 0, f'訂單編號: {order_id}', bold)
            worksheet.write(1, 0, f'訂單日期: {order_date}', bold)
            
            # Write the dataframe to the worksheet, starting from row 3 to avoid overlap
            details_df.to_excel(writer, sheet_name='OrderDetails', startrow=3, index=False)
            
            # Format the header row
            for col_num, value in enumerate(details_df.columns.values):
                worksheet.write(3, col_num, value, bold)
            
            # Write the total amount
            worksheet.write(len(details_df) + 4, 0, '結帳金額', bold)
            worksheet.write(len(details_df) + 4, 1, total_amount)
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        print(f"Error generating Excel file: {e}")
        return f"Error generating Excel file: {e}", 500

@socketio.on('search')
def handle_search(data):
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    conn = sqlite3.connect(DataBase)
    query = '''
        SELECT 
            M.o_id, M.o_date, M.o_total
        FROM 
            ORDER_M M
        WHERE
            M.o_date BETWEEN ? AND ?
        ORDER BY M.o_date desc, M.o_id desc
    '''
    try:
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        
        df.columns = ['訂單編號', '訂單日期', '金額']
        
        if df.empty:
            emit('search_results', {'results': []})
        else:
            orders = df.to_dict('records')
            emit('search_results', {'results': orders})
    except Exception as e:
        print(f"Error executing query: {e}")
        emit('search_results', {'results': f"Error executing query: {e}"})
    finally:
        conn.close()
current_order_details = {}
@socketio.on('get_order_details')
def handle_order_details(data):
    global current_order_details
    o_id = data['o_id']
    conn = sqlite3.connect(DataBase)
    query = '''
        SELECT p_id, p_name, p_price, SUM(p_qty) as total_qty
        FROM ORDER_D
        WHERE o_id = ?
        GROUP BY p_id, p_name, p_price
    '''
    try:
        df = pd.read_sql_query(query, conn, params=(o_id,))
        df['商品序號'] = df.index + 1  # Adding a new column for '商品序號'
        df['金額'] = df['p_price'] * df['total_qty']  # Calculating the amount for each item
        total_amount = df['金額'].sum()
        
        df = df[['商品序號', 'p_id', 'p_name', 'p_price', 'total_qty', '金額']]  # Reordering columns
        
        df.columns = ['商品序號', '商品編號', '商品名稱', '商品單價', '商品數量', '金額']  # Renaming columns
        
        if df.empty:
            emit('order_details', {'details': 'No data found.'})
        else:
            details_html = df.to_html(index=False)
            details_html += f'<p>結帳金額: {total_amount}</p>'
            # Fetching order date
            order_query = 'SELECT o_date FROM ORDER_M WHERE o_id = ?'
            order_date = pd.read_sql_query(order_query, conn, params=(o_id,)).iloc[0, 0]
            current_order_details = {'order_id': o_id, 'order_date': order_date, 'details': df, 'total_amount': total_amount}
            emit('order_details', {'details': details_html, 'order_id': o_id, 'order_date': order_date})
    except Exception as e:
        print(f"Error executing query: {e}")  # Debug line
        emit('order_details', {'details': f"Error executing query: {e}"})
    finally:
        conn.close()

if __name__ == '__main__':

    #socketio.run(app, debug=True, host='127.0.0.1', port=3000)
    class_product_tbl = fetch_data(db, tables=['Class2PID','PRODUCTS'], conditions_dict=None,join_on=('Class2PID.p_id', 'PRODUCTS.p_id') )
    # print(f" query_data 共讀取 {len(class_product_tbl)} 筆資料")
    
    http_server = WSGIServer(('0.0.0.0', 5000), socketio.run(app, debug=True, host='0.0.0.0', port=3000))
    http_server.serve_forever()
    