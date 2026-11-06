from flask import Flask

#=================
#インスタンス生成
#=================
app = Flask(__name__)

#=================
#ルーティング
#=================
@app.route('/')
def hindex(): 
    return '<h1>HTopページ</H1>'


#一覧
@app.route('/list')
def item_list(): 
    return '<h1>商品一覧ページ</H1>'

#詳細
@app.route('/detail')
def item_detail():
    return '<h1>商品詳細ページ</H1>'

#=================
#実行
#=================

if __name__ == '__main__':
    app.run()
    