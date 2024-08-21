快速結帳 YOLO check object
 Carry Aug 21,2024
=========

[Installation]
pip install -r requirements.txt

[Directory layout]

└─client/
|      pos.py
└─database/
|      example.db
└─model/
|      set your yolo model
└─static/css/
|      style.css
├─templates/
|      base.html
│      html5_camera_1.html
│      html5_camera_2.html
│      index.html
│      prods.html
│      viewreport.html
└─upload/
├─appmain.py
│─db.py
│─sql_cmd.py
│─sqllite_utils.py
├─Readme.txt
├─requirements.txt
├─Dockerfile
│

[Run Flask]
python appmain.py
python ./client/pos.py (for 結帳線)

[Test]
#main function
http://127.0.0.1:3000

#send a camera image (base64)
http://127.0.0.1:3000/
