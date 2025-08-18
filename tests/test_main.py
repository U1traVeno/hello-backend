import pytest
import json
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
import tempfile

from src.hello_backend.main import app, load_db, save_db, fake_items_db


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_db_file():
    """创建临时数据库文件用于测试"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    # 清理临时文件
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_empty_db():
    """模拟空数据库"""
    with patch('src.hello_backend.main.fake_items_db', {}):
        yield


@pytest.fixture
def mock_sample_db():
    """模拟包含示例数据的数据库"""
    sample_data = {
        "苹果": {"name": "苹果", "description": "红色的苹果", "price": 5.0},
        "香蕉": {"name": "香蕉", "description": "黄色的香蕉", "price": 3.0},
        "橙子": {"name": "橙子", "description": "橙色的橙子", "price": 4.0}
    }
    with patch('src.hello_backend.main.fake_items_db', sample_data):
        yield sample_data


class TestBasicRoutes:
    """测试基本路由"""
    
    def test_read_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}
    
    def test_add_numbers_default(self, client):
        """测试加法接口 - 默认参数"""
        response = client.get("/add")
        assert response.status_code == 200
        assert response.json() == {"x": 0, "y": 0, "result": 0}
    
    def test_add_numbers_with_params(self, client):
        """测试加法接口 - 带参数"""
        response = client.get("/add?x=5&y=10")
        assert response.status_code == 200
        assert response.json() == {"x": 5, "y": 10, "result": 15}
    
    def test_add_numbers_negative(self, client):
        """测试加法接口 - 负数"""
        response = client.get("/add?x=-5&y=3")
        assert response.status_code == 200
        assert response.json() == {"x": -5, "y": 3, "result": -2}


class TestTask1PostInterface:
    """Task 1: 测试 POST 接口"""
    
    def test_create_item_success(self, client):
        """测试成功创建物品"""
        item_data = {
            "name": "测试物品",
            "description": "这是一个测试物品",
            "price": 10.5
        }
        
        with patch('src.hello_backend.main.save_db') as mock_save:
            with patch('src.hello_backend.main.fake_items_db', {}) as mock_db:
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                
                response_data = response.json()
                assert response_data["name"] == "测试物品"
                assert response_data["description"] == "这是一个测试物品"
                assert response_data["price"] == 10.5
                
                # 验证保存函数被调用
                mock_save.assert_called_once()
    
    def test_create_item_without_description(self, client):
        """测试创建物品 - 不带描述"""
        item_data = {
            "name": "无描述物品",
            "price": 8.0
        }
        
        with patch('src.hello_backend.main.save_db') as mock_save:
            with patch('src.hello_backend.main.fake_items_db', {}) as mock_db:
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                
                response_data = response.json()
                assert response_data["name"] == "无描述物品"
                assert response_data["description"] is None
                assert response_data["price"] == 8.0
    
    def test_create_item_duplicate(self, client):
        """测试创建重复物品"""
        existing_item = {"name": "苹果", "description": "红苹果", "price": 5.0}
        item_data = {
            "name": "苹果",
            "description": "绿苹果",
            "price": 6.0
        }
        
        with patch('src.hello_backend.main.fake_items_db', {"苹果": existing_item}):
            response = client.post("/items/", json=item_data)
            assert response.status_code == 200
            assert response.json() == {"error": "Item already exists"}
    
    def test_create_item_invalid_data(self, client):
        """测试创建物品 - 无效数据"""
        # 缺少必需字段
        response = client.post("/items/", json={"name": "测试"})
        assert response.status_code == 422
        
        # 价格类型错误
        response = client.post("/items/", json={
            "name": "测试",
            "price": "abc"
        })
        assert response.status_code == 422
        
        # 名称类型错误
        response = client.post("/items/", json={
            "name": 123,
            "price": 10.0
        })
        assert response.status_code == 422


class TestTask2DataPersistence:
    """Task 2: 测试数据持久化"""
    
    def test_load_db_file_exists(self, temp_db_file):
        """测试从存在的文件加载数据"""
        test_data = {"item1": {"name": "item1", "price": 10.0}}
        
        with open(temp_db_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with patch('src.hello_backend.main.DB_FILE', temp_db_file):
            result = load_db()
            assert result == test_data
    
    def test_load_db_file_not_exists(self):
        """测试文件不存在时加载数据"""
        with patch('src.hello_backend.main.DB_FILE', 'nonexistent_file.json'):
            result = load_db()
            assert result == {}
    
    def test_save_db(self, temp_db_file):
        """测试保存数据到文件"""
        test_data = {"item1": {"name": "item1", "price": 10.0}}
        
        with patch('src.hello_backend.main.DB_FILE', temp_db_file):
            save_db(test_data)
        
        # 验证文件内容
        with open(temp_db_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            assert saved_data == test_data
    
    def test_read_item_from_persisted_data(self, client):
        """测试从持久化数据中读取物品"""
        test_data = {
            "苹果": {"name": "苹果", "description": "红苹果", "price": 5.0}
        }
        
        with patch('src.hello_backend.main.fake_items_db', test_data):
            response = client.get("/items/苹果")
            assert response.status_code == 200
            assert response.json() == test_data["苹果"]
    
    def test_read_item_not_found(self, client):
        """测试读取不存在的物品"""
        with patch('src.hello_backend.main.fake_items_db', {}):
            response = client.get("/items/不存在的物品")
            assert response.status_code == 200
            assert response.json() == {"error": "Item not found"}


class TestTask3AdditionalFeatures:
    """Task 3: 测试附加功能"""
    
    def test_get_items_count_empty(self, client, mock_empty_db):
        """测试获取物品数量 - 空数据库"""
        response = client.get("/items/count")
        assert response.status_code == 200
        assert response.json() == {"total_items": 0}
    
    def test_get_items_count_with_items(self, client, mock_sample_db):
        """测试获取物品数量 - 有数据"""
        response = client.get("/items/count")
        assert response.status_code == 200
        assert response.json() == {"total_items": 3}
    
    def test_get_random_item_empty_db(self, client, mock_empty_db):
        """测试随机获取物品 - 空数据库"""
        response = client.get("/items/random")
        assert response.status_code == 404
        assert response.json() == {"detail": "No items in the database"}
    
    def test_get_random_item_with_items(self, client, mock_sample_db):
        """测试随机获取物品 - 有数据"""
        response = client.get("/items/random")
        assert response.status_code == 200
        
        # 验证返回的是有效的物品
        response_data = response.json()
        assert "name" in response_data
        assert "price" in response_data
        
        # 验证返回的物品在数据库中
        assert response_data["name"] in ["苹果", "香蕉", "橙子"]
    
    def test_get_random_item_multiple_calls(self, client, mock_sample_db):
        """测试多次调用随机获取物品"""
        results = []
        for _ in range(10):
            response = client.get("/items/random")
            assert response.status_code == 200
            results.append(response.json()["name"])
        
        # 验证所有结果都是有效的
        valid_names = ["苹果", "香蕉", "橙子"]
        for name in results:
            assert name in valid_names


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self, client):
        """测试完整工作流程"""
        with patch('src.hello_backend.main.save_db') as mock_save:
            with patch('src.hello_backend.main.fake_items_db', {}) as mock_db:
                # 1. 检查初始状态
                response = client.get("/items/count")
                assert response.json()["total_items"] == 0
                
                # 2. 尝试获取随机物品（应该失败）
                response = client.get("/items/random")
                assert response.status_code == 404
                
                # 3. 添加第一个物品
                item1 = {"name": "苹果", "description": "红苹果", "price": 5.0}
                response = client.post("/items/", json=item1)
                assert response.status_code == 200
                mock_db["苹果"] = item1
                
                # 4. 检查数量
                response = client.get("/items/count")
                assert response.json()["total_items"] == 1
                
                # 5. 获取随机物品（应该成功）
                response = client.get("/items/random")
                assert response.status_code == 200
                assert response.json()["name"] == "苹果"
                
                # 6. 添加更多物品
                item2 = {"name": "香蕉", "description": "黄香蕉", "price": 3.0}
                response = client.post("/items/", json=item2)
                assert response.status_code == 200
                mock_db["香蕉"] = item2
                
                # 7. 尝试添加重复物品
                response = client.post("/items/", json=item1)
                assert response.json() == {"error": "Item already exists"}
                
                # 8. 最终检查
                response = client.get("/items/count")
                assert response.json()["total_items"] == 2


class TestEdgeCases:
    """边界情况测试"""
    
    def test_item_name_with_special_characters(self, client):
        """测试包含特殊字符的物品名称"""
        item_data = {
            "name": "特殊物品!@#$%^&*()",
            "description": "包含特殊字符的物品",
            "price": 15.99
        }
        
        with patch('src.hello_backend.main.save_db'):
            with patch('src.hello_backend.main.fake_items_db', {}) as mock_db:
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                
                # 尝试读取这个物品
                mock_db[item_data["name"]] = item_data
                response = client.get(f"/items/{item_data['name']}")
                assert response.status_code == 200
    
    def test_zero_price_item(self, client):
        """测试价格为0的物品"""
        item_data = {
            "name": "免费物品",
            "description": "价格为0的物品",
            "price": 0.0
        }
        
        with patch('src.hello_backend.main.save_db'):
            with patch('src.hello_backend.main.fake_items_db', {}):
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                assert response.json()["price"] == 0.0
    
    def test_very_long_item_name(self, client):
        """测试非常长的物品名称"""
        long_name = "a" * 1000
        item_data = {
            "name": long_name,
            "description": "非常长名称的物品",
            "price": 10.0
        }
        
        with patch('src.hello_backend.main.save_db'):
            with patch('src.hello_backend.main.fake_items_db', {}):
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                assert response.json()["name"] == long_name
    
    def test_unicode_characters(self, client):
        """测试Unicode字符"""
        item_data = {
            "name": "🍎苹果🍏",
            "description": "包含emoji的物品描述 😊",
            "price": 5.5
        }
        
        with patch('src.hello_backend.main.save_db'):
            with patch('src.hello_backend.main.fake_items_db', {}):
                response = client.post("/items/", json=item_data)
                assert response.status_code == 200
                assert response.json()["name"] == "🍎苹果🍏"
