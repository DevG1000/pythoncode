import requests
import json
import time

BASE_URL = "http://localhost:5000"

def quick_test():
    """快速测试API基本功能"""
    print("=" * 60)
    print("快速API测试")
    print("=" * 60)
    
    try:
        # 1. 测试健康检查
        print("\n1. 测试健康检查...")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 2. 测试主页
        print("\n2. 测试主页...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   消息: {response.json().get('message', 'N/A')}")
        
        # 3. 测试无效注册
        print("\n3. 测试无效注册（短密码）...")
        payload = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short"  # 密码太短
        }
        response = requests.post(f"{BASE_URL}/api/register", json=payload, timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   错误: {response.json().get('error', 'N/A')}")
        
        # 4. 测试有效注册
        print("\n4. 测试有效注册...")
        timestamp = int(time.time())
        payload = {
            "email": f"test_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "SecurePass123!"
        }
        response = requests.post(f"{BASE_URL}/api/register", json=payload, timeout=5)
        print(f"   状态: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   消息: {data.get('message', 'N/A')}")
            print(f"   用户ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   邮箱已发送: {data.get('email_sent', 'N/A')}")
            
            # 5. 测试重新发送验证邮件
            print("\n5. 测试重新发送验证邮件...")
            resend_payload = {"email": f"test_{timestamp}@example.com"}
            response = requests.post(f"{BASE_URL}/api/resend-verification", json=resend_payload, timeout=5)
            print(f"   状态: {response.status_code}")
            print(f"   消息: {response.json().get('message', 'N/A')}")
        else:
            print(f"   错误: {response.json().get('error', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n注意：")
        print("1. 邮箱验证功能需要配置正确的邮箱设置")
        print("2. 查看 .env.example 文件了解如何配置邮箱")
        print("3. 数据库文件: users.db")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器")
        print("请确保API服务器正在运行：")
        print("   python app.py")
    except Exception as e:
        print(f"\n✗ 测试错误: {e}")

if __name__ == "__main__":
    quick_test()