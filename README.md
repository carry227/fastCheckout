# 目的：
- 視覺化快速結帳。
  
# 系統環境：
-  Code : Python / Html / Css
-  Web : Flask
-  Model : YOLO
   - [roboflow](https://app.roboflow.com/) : 產生圖片，標註的訓練資料。
   - 控制環境變數可減少訓練圖片，例如：固定WEBCAM，距離，背景，各類別張數不可差異太大。
-  Database : Sqlite

# 使用方式：
### python appmain.py
### python ./client/pos.py (for 購買線)
### http://127.0.0.1:3000

# 界面顯示：
- 首頁  
   <img src="/img/index.png" width="640" />  
- 定點結帳  
   <img src="/img/trace1.png" width="640" />  
- 流動線結帳  
   <img src="/img/trace2.png" width="640" />  
- 訂單  
   <img src="/img/order.png" width="640" />  
- 商品  
   <img src="/img/prods.png" width="640" />  
