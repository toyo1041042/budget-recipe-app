from flask import Flask, render_template


#=================
#インスタンス生成
#=================
app = Flask(__name__)

#=================
#ルーティング
#=================
@app.route('/')
def index(): 
    return render_template('top.html')

#一覧
@app.route('/list')
def item_list(): 
    return render_template('list.html')

#詳細
@app.route('/detail/<int:id>')
def item_detail(id):
    return render_template('detail.html', show_id=id)
#render_templateで値を渡す
@app.route("/multiple")
def show_jinja_multiple():
    word1 = "テンプレートエンジン"
    word2 = "神社"
    return render_template('jinja/show1.html', temp=word1, jinja=word2)

#=================
#実行
#=================
if __name__ == '__main__':
    app.run()
    