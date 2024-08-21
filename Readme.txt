Websocket Chatroom
 Joseph Nov 14,2022
=========

[Installation]
pip install -r requirements.txt

[Directory layout]
tree /F

├─appmain.py
│─db.py
│─sql_cmd.py
│─sqllite_utils.py
├─Readme.txt
├─requirements.txt
│
├─templates/
│      html5_camera_1.html
│      index.html
│      viewreport.html
│
└─upload/
        20221114-190224.png
        20221114-190431.png


[Run Flask]
python appmain.py


[Test it]



#main function

http://127.0.0.1:3000

#send a camera image (base64)

http://127.0.0.1:3000/video



#Referencs docs
[Flask User’s Guide]
https://flask.palletsprojects.com/en/2.2.x/
