import time
import cProfile
import pstats
import io
import sys
import os
from datetime import datetime

def analyze_line2card_performance():
    """分析Line2Card.py的性能"""
    print("=" * 60)
    print("Line2Card.py 性能分析")
    print("=" * 60)
    
    try:
        # 导入模块
        sys.path.append('.')
        from Line2Card import create_business_card, add_business_cards_to_excel
        
        # 模拟测试数据
        test_data = {
            'name': '张三',
            'title': '高级工程师',
            'company': 'ABC科技有限公司',
            'phone': '13800138000',
            'email': 'zhangsan@example.com',
            'address': '北京市海淀区中关村大街1号'
        }
        
        print("\n1. 测试单张名片生成性能:")
        start = time.time()
        for i in range(50):  # 减少测试数量
            img = create_business_card(test_data)
        end = time.time()
        print(f"   生成50张名片耗时: {end - start:.3f}秒")
        print(f"   平均每张: {(end - start) * 20:.1f}毫秒")
        
    except ImportError as e:
        print(f"   无法导入模块: {e}")
        print("   请确保已安装 openpyxl 和 pillow")
    except Exception as e:
        print(f"   测试过程中出现错误: {e}")
    
    print("\n2. 分析Excel处理性能瓶颈:")
    print("   潜在问题:")
    print("   - 每次循环都重新加载字体文件")
    print("   - 图像保存到内存字节流")
    print("   - Excel行高调整操作")
    print("   - 大量小文件I/O操作")
    
    print("\n3. 内存使用分析:")
    print("   - 每张图像约400x250像素，RGB格式")
    print("   - 单张图像内存: 400 * 250 * 3 ≈ 300KB")
    print("   - 100张图像同时处理: 约30MB")
    print("   - BytesIO缓冲区增加额外内存开销")

def analyze_api_performance():
    """分析API性能"""
    print("\n" + "=" * 60)
    print("用户注册API性能分析")
    print("=" * 60)
    
    print("\n1. 数据库操作瓶颈:")
    print("   - 用户查询: User.query.filter_by(email=email).first()")
    print("   - 用户名查询: User.query.filter_by(username=username).first()")
    print("   - 缺少索引优化")
    print("   - 事务处理可能成为瓶颈")
    
    print("\n2. 密码加密性能:")
    print("   - bcrypt哈希计算是CPU密集型操作")
    print("   - 默认工作因子: 12 (2^12次迭代)")
    print("   - 单次哈希约100-500毫秒")
    print("   - 高并发时可能成为瓶颈")
    
    print("\n3. 邮箱发送性能:")
    print("   - SMTP连接建立耗时")
    print("   - 网络延迟影响")
    print("   - 同步发送阻塞请求")
    print("   - 缺少重试机制和队列")
    
    print("\n4. 令牌生成和验证:")
    print("   - itsdangerous序列化/反序列化")
    print("   - 加密操作有一定开销")
    print("   - 数据库查询验证令牌")

def analyze_memory_usage():
    """分析内存使用"""
    print("\n" + "=" * 60)
    print("内存使用分析")
    print("=" * 60)
    
    print("\n1. Line2Card.py 内存问题:")
    print("   - 图像处理使用PIL库，内存占用较高")
    print("   - 大量图像同时处理可能导致内存溢出")
    print("   - BytesIO缓冲区未及时清理")
    print("   - Excel文件加载到内存")
    
    print("\n2. API 内存问题:")
    print("   - Flask应用本身内存占用")
    print("   - SQLAlchemy会话管理")
    print("   - 请求/响应数据序列化")
    print("   - 缺少连接池管理")

def analyze_io_bottlenecks():
    """分析I/O瓶颈"""
    print("\n" + "=" * 60)
    print("I/O瓶颈分析")
    print("=" * 60)
    
    print("\n1. 文件I/O:")
    print("   - Excel文件读取/写入")
    print("   - 字体文件检查 (os.path.exists)")
    print("   - 数据库文件访问 (SQLite)")
    print("   - 同步磁盘操作")
    
    print("\n2. 网络I/O:")
    print("   - 邮箱SMTP连接")
    print("   - API请求/响应")
    print("   - 缺少连接复用")
    print("   - 同步网络调用")
    
    print("\n3. 数据库I/O:")
    print("   - SQLite单文件数据库")
    print("   - 并发访问锁竞争")
    print("   - 缺少连接池")
    print("   - 事务管理开销")

def analyze_concurrent_issues():
    """分析并发问题"""
    print("\n" + "=" * 60)
    print("并发性能分析")
    print("=" * 60)
    
    print("\n1. Line2Card.py 并发问题:")
    print("   - 单线程处理Excel")
    print("   - 无法利用多核CPU")
    print("   - 大量数据时响应慢")
    print("   - 缺少进度反馈")
    
    print("\n2. API 并发问题:")
    print("   - Flask开发服务器单线程")
    print("   - SQLite写锁限制")
    print("   - bcrypt计算阻塞")
    print("   - 邮箱发送同步阻塞")

def profile_line2card():
    """使用cProfile分析Line2Card性能"""
    print("\n" + "=" * 60)
    print("cProfile 性能分析")
    print("=" * 60)
    
    try:
        # 创建性能分析器
        pr = cProfile.Profile()
        pr.enable()
        
        # 运行测试代码
        sys.path.append('.')
        from Line2Card import create_business_card
        
        test_data = {
            'name': '测试用户',
            'title': '测试职位',
            'company': '测试公司',
            'phone': '1234567890',
            'email': 'test@example.com',
            'address': '测试地址'
        }
        
        for i in range(20):  # 减少测试数量
            create_business_card(test_data)
        
        pr.disable()
        
        # 输出分析结果
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(15)
        
        print("Top 15 耗时函数:")
        print(s.getvalue())
    except Exception as e:
        print(f"   cProfile分析失败: {e}")

def generate_recommendations():
    """生成优化建议"""
    print("\n" + "=" * 60)
    print("性能优化建议")
    print("=" * 60)
    
    print("\n1. Line2Card.py 优化:")
    print("   [优化] 缓存字体加载，避免重复检查")
    print("   [优化] 使用生成器处理大数据集")
    print("   [优化] 添加进度反馈和取消功能")
    print("   [优化] 优化图像处理参数")
    print("   [优化] 使用多进程处理大量数据")
    
    print("\n2. API 优化:")
    print("   [优化] 添加数据库索引")
    print("   [优化] 使用异步任务处理邮箱发送")
    print("   [优化] 实现连接池和缓存")
    print("   [优化] 优化bcrypt工作因子")
    print("   [优化] 添加API限流和监控")
    
    print("\n3. 内存优化:")
    print("   [优化] 及时释放资源")
    print("   [优化] 使用流式处理")
    print("   [优化] 优化数据结构")
    print("   [优化] 添加内存监控")
    
    print("\n4. I/O 优化:")
    print("   [优化] 使用异步I/O")
    print("   [优化] 实现批处理")
    print("   [优化] 添加缓存层")
    print("   [优化] 优化数据库查询")
    
    print("\n5. 并发优化:")
    print("   [优化] 使用多进程/线程")
    print("   [优化] 实现任务队列")
    print("   [优化] 优化锁策略")
    print("   [优化] 添加负载均衡")

def main():
    """主分析函数"""
    print("项目性能瓶颈分析报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    
    try:
        analyze_line2card_performance()
        analyze_api_performance()
        analyze_memory_usage()
        analyze_io_bottlenecks()
        analyze_concurrent_issues()
        
        # 可选：运行cProfile分析（可能需要较长时间）
        # profile_line2card()
        
        generate_recommendations()
        
        print("\n" + "=" * 60)
        print("总结")
        print("=" * 60)
        print("\n主要性能瓶颈:")
        print("1. Line2Card: 图像处理和Excel操作")
        print("2. API: bcrypt加密和邮箱发送")
        print("3. 内存: 大量图像处理")
        print("4. I/O: 文件操作和网络请求")
        print("5. 并发: 单线程处理")
        
        print("\n建议优先优化:")
        print("[优先] 1. 缓存字体加载 (Line2Card)")
        print("[优先] 2. 异步邮箱发送 (API)")
        print("[优先] 3. 添加数据库索引 (API)")
        print("[优先] 4. 优化内存使用 (Line2Card)")
        
    except Exception as e:
        print(f"\n分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()