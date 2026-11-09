import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. セキュリティ設定
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "fallback-dev-secret-key"
)

# 2. データベース接続の切り替え設定（ローカルはSQLite、本番はSupabase/PostgreSQL）
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
  database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///recipes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 3. データベースの初期化
db = SQLAlchemy(app)


# --- モデル（テーブル定義） ---
class Recipe(db.Model):
  __tablename__ = "recipes"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  ingredients = db.Column(db.Text, nullable=False)
  instructions = db.Column(db.Text, nullable=False)
  budget = db.Column(db.Integer)

  def __repr__(self):
    return f"<Recipe {self.title}>"


# --- アプリ起動時の自動セットアップ ---
with app.app_context():
  db.create_all()

  if Recipe.query.count() == 0:
    sample_recipes = [
        Recipe(
            title="キャベツと豚肉のスタミナ炒め",
            ingredients="キャベツ, 豚肉, ニンニク, 醤油",
            instructions=(
                "1. キャベツと豚肉を一口大に切る。\n2."
                " フライパンで豚肉を炒め、火が通ったらキャベツを入れる。\n3."
                " 醤油とニンニクで味付けして完成！"
            ),
            budget=180,
        ),
        Recipe(
            title="もやしと卵の絶品スープ",
            ingredients="もやし, 卵, 中華だし, 塩コショウ",
            instructions=(
                "1. 鍋にお湯を沸かし、中華だしともやしを入れる。\n2."
                " ひと煮立ちさせたら、溶き卵を回し入れる。\n3."
                " 塩コショウで味を整えて完成！"
            ),
            budget=80,
        ),
        Recipe(
            title="ツナと豆腐の和風サラダ",
            ingredients="ツナ缶, 豆腐, レタス, ポン酢",
            instructions=(
                "1. レタスをちぎり、豆腐を食べやすい大きさに切る。\n2."
                " 器に盛り付け、油を切ったツナを乗せる。\n3."
                " ポン酢を回しかけて完成！"
            ),
            budget=120,
        ),
    ]
    db.session.bulk_save_objects(sample_recipes)
    db.session.commit()
    print("テスト用データを3件登録しました！")


# --- ルート（機能の実装） ---
@app.route("/")
def index():
  """トップページ"""
  return render_template("index.html")


@app.route("/list")
def item_list():
  """レシピ一覧表示 ＆ キーワード・予算上限での絞り込み検索"""
  keyword = request.args.get("keyword", "")
  max_cost = request.args.get("max_cost", type=int)

  query = Recipe.query

  # キーワード検索（タイトルまたは材料に含まれる場合）
  if keyword:
    query = query.filter(
        (Recipe.title.like(f"%{keyword}%"))
        | (Recipe.ingredients.like(f"%{keyword}%"))
    )

  # 予算上限での絞り込み
  if max_cost is not None:
    query = query.filter(Recipe.budget <= max_cost)

  recipes = query.all()

  return render_template(
      "list.html",
      recipes=recipes,
      keyword=keyword,
      max_cost=max_cost if max_cost is not None else "",
  )


@app.route("/recipe/<int:id>")
def item_detail(id):
  """レシピ個別詳細表示"""
  recipe = Recipe.query.get_or_404(id)
  return render_template("detail.html", recipe=recipe)


@app.route("/add", methods=["GET", "POST"])
def add_recipe():
  """新規レシピ追加"""
  if request.method == "POST":
    title = request.form.get("title")
    ingredients = request.form.get("ingredients")
    instructions = request.form.get("instructions")
    budget = request.form.get("budget", type=int)

    if title and ingredients:
      new_recipe = Recipe(
          title=title,
          ingredients=ingredients,
          instructions=instructions,
          budget=budget,
      )
      db.session.add(new_recipe)
      db.session.commit()
      return redirect(url_for("item_list"))

  return render_template("add.html")


@app.route("/recipe/<int:id>/edit", methods=["GET", "POST"])
def edit_recipe(id):
  """レシピの編集・更新"""
  recipe = Recipe.query.get_or_404(id)

  if request.method == "POST":
    recipe.title = request.form.get("title")
    recipe.ingredients = request.form.get("ingredients")
    recipe.instructions = request.form.get("instructions")
    recipe.budget = request.form.get("budget", type=int)

    db.session.commit()
    return redirect(url_for("item_detail", id=recipe.id))

  return render_template("edit.html", recipe=recipe)


@app.route("/recipe/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
  """レシピの削除"""
  recipe = Recipe.query.get_or_404(id)
  db.session.delete(recipe)
  db.session.commit()
  return redirect(url_for("item_list"))


# --- アプリの起動 ---
if __name__ == "__main__":
  debug_mode = os.environ.get("FLASK_DEBUG", "True") == "True"
  app.run(host="0.0.0.0", port=5000, debug=debug_mode)