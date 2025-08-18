# 课后小任务

讲座中，我们已经成功创建了自己的第一个后端 API，现在是时候通过一些练习，巩固我们的知识，探索一些更有意思的功能了。

这个任务分为三个部分，预计总共花费3-5小时。请按照顺序完成，它们之间是层层递进的。

请打开我们在课上创建的 main.py 项目，它在本项目的 `src/hello_backend/main.py`，我们将在它的基础上继续构建。

## Task 1: 实现一个 POST 接口

在课堂上，我们用 GET 方法来“获取”数据。现在，我们要学习使用 POST 方法来“创建”新的数据。

当客户端（比如网页或App）想向服务器提交一个“复杂”的数据（比如用户注册信息、一篇文章的内容），通常会使用 POST 请求。这些数据会放在“请求体”（Request Body）里，而不是像路径参数或查询参数那样放在URL里。

为了让 FastAPI 知道我们期望接收什么样的数据，我们会用到一个名为 Pydantic 的库（它已经随 FastAPI 一起安装好了）来创建一个“数据模型”。这就像是定义一个“表格”，告诉 FastAPI：“我需要的数据必须包含姓名、价格这些字段”。

### 步骤

- 导入 BaseModel
- 在 main.py 文件的顶部，从 pydantic 导入 BaseModel。

```python
from fastapi import FastAPI
from pydantic import BaseModel # 导入这行
```

#### 定义你的数据模型

创建一个类(class)，让它继承自 BaseModel。这就是我们的数据模型，它就叫 Item。在这个类里，定义你希望接收的字段和它们的数据类型。

在你的代码中加入这一行：

```Python
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
```

这段代码定义了一个叫 `Item` 的模型，它有三个字段：`name` (必须是字符串), `description` (可以是字符串 `str`，也可以没有), `price` (必须是浮点数, 即带小数点的数)。

#### 创建 POST 路由

POST 是一个 HTTP 方法。我们之前实现了 GET 接口，GET 同样是 HTTP 方法。

使用 `@app.post()` 装饰器来创建一个新的接口。函数的参数就是我们刚刚定义的 `Item` 模型。

```python
# 把它添加到你的 main.py 文件中
@app.post("/items/")
def create_item(item: Item):
    # 这里的 item 参数就是 FastAPI 根据你定义的 Item 模型，
    # 自动从请求体中解析并验证好的数据。
    print(f"成功接收到新物品: {item.name}")
    return {"message": f"成功添加物品: {item.name}", "item_data": item}
```

### 运行和测试

- 按下 F5，或者干脆在终端运行 `uvicorn main:app --reload`。

- 打开浏览器，访问 <http://127.0.0.1:8000/docs>。

你会看到一个新的 POST /items/ 接口。点开它，点击 "Try it out"。你会发现一个可以直接编辑的JSON输入框，这就是根据你的 Item 模型自动生成的！

修改输入框里的内容，然后点击 "Execute"。观察下方返回的成功信息。

试一试：故意把 `price` 的值改成一个字符串（比如 "abc"），再点击 "Execute"，看看 FastAPI 是如何自动帮你处理错误，并返回一个清晰的 `Validation Error` 的。

## Task 2: 数据持久化

### 目标

目前我们的数据都只存在内存里，每次重启服务器，新添加的物品就消失了。现在我们要把数据保存到一个 JSON 文件里，实现“持久化”。

### 背景知识

JSON 文件是一种轻量级的、人类易于阅读的文本文件，经常用来存储结构化数据。Python 内置了 json 模块，可以轻松地读取和写入 JSON 文件。

更规范的做法是使用数据库，但对于我们的小练习，JSON 文件已经足够了，并且能让你理解数据持久化的核心思想。

### 实现步骤

- 导入 json 模块: 在 main.py 顶部添加 `import json`。

- 创建读写函数: 为了方便管理，我们创建两个函数：一个用来从文件加载数据，一个用来把数据保存到文件。

```python
DB_FILE = "items_db.json"

def load_db():
    """从 JSON 文件加载数据，如果文件不存在则返回一个空字典"""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(db):
    """将数据写入 JSON 文件"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
```

提示：可以直接复制粘贴这两段代码到你的 main.py 文件里。

#### 在程序启动时加载数据

修改我们之前课堂上写的 fake_items_db，让它从 load_db() 函数初始化。

```python
fake_items_db = load_db()
```

修改 POST 接口以保存数据
在 create_item 函数里，当接收到新物品后，把它存入我们的 fake_items_db 字典，并调用 save_db() 函数。

```python

@app.post("/items/")
def create_item(item: Item):
    # 为了简单，我们用物品名称作为ID
    item_id = item.name 
    if item_id in fake_items_db:
         # (我们将在 Task 3 处理这个错误)
        return {"error": "Item already exists"}

    fake_items_db[item_id] = item.dict()
    save_db(fake_items_db) # <-- 关键步骤：保存到文件

    return fake_items_db[item_id]
```

#### 修改 GET 接口以读取新数据

确保你之前写的 GET /items/{item_id} 接口能从 fake_items_db 中正确读取数据。

### 测试

启动服务器。

使用 /docs 的 POST 接口添加几个新物品。

按 Ctrl + ` 在 VSCode 打开终端。在终端按 Ctrl+C 停止服务器，然后再重新启动服务器(也就是在 vscode 按 F5)。

使用我们最开始写的 GET /items/{item_id} 接口（或者写一个新的 GET /items/ 来获取所有物品），看看你刚才添加的物品是不是还在。如果在了，恭喜你，我们的数据成功的持久化保存了！

## Task 3: 为你的API添加两个有趣的“小功能”

我们的API已经像一个“仓库”了，可以存东西（Task 1 & 2）。现在，我们不去做复杂的搜索，而是为这个“仓库”增加两个简单又实用的小功能：一个是随机抽取一件“幸运商品”，另一个是实时统计商品总数。

API 不仅仅是“增删改查”。它还可以提供各种各样的“工具”或“信息服务”

### 抽奖 API

创建一个 GET /items/random 接口，每次调用它，都会随机返回数据库中的一件商品。

- 导入`random`模块：Python 有一个内置的 random 模块，专门用来处理随机的事情。我们先在 main.py 顶部导入它。

```python
import random
```

- 创建 `/random` 路由

这个接口不需要任何参数，因为它只是随机返回。

```python
@app.get("/items/random")
def get_random_item():
    # fake_items_db 是我们的商品字典
    # .values() 获取所有的商品信息，并用 list() 转换成一个列表
    all_items = list(fake_items_db.values())

    # 如果仓库是空的，就返回一个提示
    if not all_items:
        raise HTTPException(status_code=404, detail="No items in the database")

    # 从列表中随机选择一个
    random_item = random.choice(all_items)

    return random_item
```

打开 `/docs` 页面，找到并点开 `GET /items/random` 接口。

点击 "Try it out"，然后反复点击 "Execute"。

### 总数统计

创建一个 GET /items/count 接口，它会告诉我们当前数据库里一共有多少件商品。

这个接口也非常简单，不需要参数。

```python
@app.get("/items/count")
def get_items_count():
    # len() 是 Python 内置的函数，可以计算出列表或字典的长度
    count = len(fake_items_db)
    return {"total_items": count}
```

`len()` 函数是 Python 中最基础的函数之一。这个任务的核心就是调用它，然后把结果包装在一个JSON里返回。

刷新 `/docs` 页面，找到新的 `GET /items/count` 接口。

先调用一次 `/items/count`，看看现在的商品总数是多少。

去 `POST /items/` 接口，添加一件新商品。

再回来调用一次 `/items/count`，看看总数是不是加了1？

## 拓展阅读

如果你完成了以上所有任务，恭喜你！你已经成功构建了一个具备核心功能的、数据驱动的API。你已经打开了后端领域的大门！

在继续深入学习后端之前，或许你会想要先补齐一下后端所需的编程基础。这里我们推荐一门神课：CS61A 。

如果你已经熟悉了基础的编程，想正式踏上后端学习旅程，我们在下面列出了一些你可能感兴趣的学习资源：

- [MDN Web Doc - HTTP](https://developer.mozilla.org/zh-CN/docs/Web/HTTP) 权威的 HTTP 讲解。
- [MDN Web Doc - Server-side](https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Extensions/Server-side) 浅显易懂，涵盖后端全貌，业界权威。
- [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN) 图形化的 Git 工具学习。今后的开发中，Git 是你不可或缺的工具。
- [freeCodeCamp](https://www.freecodecamp.org/chinese/) 有很多不错的免费教程。
- [SQL Bolt](https://sqlbolt.com/) 交互式 SQL 教学，很有趣，很推荐。
