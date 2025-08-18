from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI()

# 定义一个"路由" (route)
# 当有人访问我们网站的根目录 ("/") 时，就执行下面的函数
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# 模拟商品数据库
fake_items_db = {
    1: {"name": "苹果"},
    2: {"name": "香蕉"},
    3: {"name": "橙子"}
}

# 路径参数 - 让 API 动起来
@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id in fake_items_db:
        return fake_items_db[item_id]
    return {"error": "Item not found"}

# 查询参数 - 更灵活的筛选
# /add?x=5&y=10
@app.get("/add")
def add_numbers(x: int = 0, y: int = 0):
    result = x + y
    return {"x": x, "y": y, "result": result}
