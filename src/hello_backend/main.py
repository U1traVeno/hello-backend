from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import random

# 创建一个 FastAPI 应用实例
app = FastAPI()

# Task 1: 定义数据模型

# TODO: YOUR_CODE_HERE

# Task 2: 数据持久化相关
DB_FILE = "items_db.json"

def load_db():
    """从 JSON 文件加载数据，如果文件不存在则返回一个空字典"""
    # TODO: YOUR_CODE_HERE

def save_db(db):
    """将数据写入 JSON 文件"""
    # TODO: YOUR_CODE_HERE

# 定义一个"路由" (route)
# 当有人访问我们网站的根目录 ("/") 时，就执行下面的函数
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# 模拟商品数据库 - 从持久化文件加载
fake_items_db = load_db()

# Task 3.1: 随机抽取商品（必须在通用路径参数之前）
@app.get("/items/random")
def get_random_item():
    
    # TODO: YOUR_CODE_HERE

    return NotImplementedError

# Task 3.2: 商品总数统计（必须在通用路径参数之前）
@app.get("/items/count")
def get_items_count():

    # TODO: YOUR_CODE_HERE

    return NotImplementedError

# 路径参数 - 让 API 动起来（通用路径参数放在最后）
@app.get("/items/{item_id}")
def read_item(item_id: str):
    if item_id in fake_items_db:
        return fake_items_db[item_id]
    return {"error": "Item not found"}

# 查询参数 - 更灵活的筛选
# /add?x=5&y=10
@app.get("/add")
def add_numbers(x: int = 0, y: int = 0):
    result = x + y
    return {"x": x, "y": y, "result": result}

# Task 1: POST 接口 - 创建新物品
@app.post("/items/")
def create_item():

    # TODO: YOUR_CODE_HERE

    return NotImplementedError
