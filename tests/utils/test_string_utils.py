"""
单词反转函数的pytest测试套件
测试reverse_words函数的各种场景
"""
import pytest
import sys
import os

# 添加父目录到Python路径，以便导入utils模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestReverseWords:
    """测试reverse_words函数的基础功能"""
    
    def test_single_word(self):
        """测试单个单词反转"""
        from utils.string_utils import reverse_words
        assert reverse_words("hello") == "hello"
        assert reverse_words("Python") == "Python"
    
    def test_two_words(self):
        """测试两个单词反转"""
        from utils.string_utils import reverse_words
        assert reverse_words("hello world") == "world hello"
        assert reverse_words("Python programming") == "programming Python"
    
    def test_multiple_words(self):
        """测试多个单词反转"""
        from utils.string_utils import reverse_words
        assert reverse_words("this is a test") == "test a is this"
        assert reverse_words("Python is a great language") == "language great a is Python"
    
    def test_with_punctuation(self):
        """测试带标点符号的句子"""
        from utils.string_utils import reverse_words
        # 注意：简单实现可能不完美处理标点，这是测试边界
        assert reverse_words("Hello, world!") == "world! Hello,"
        assert reverse_words("Python is great!") == "great! is Python"
    
    def test_preserve_case(self):
        """测试大小写保持"""
        from utils.string_utils import reverse_words
        assert reverse_words("Hello World") == "World Hello"
        assert reverse_words("PYTHON Programming") == "Programming PYTHON"


class TestEdgeCases:
    """测试边界条件"""
    
    def test_empty_string(self):
        """测试空字符串"""
        from utils.string_utils import reverse_words
        assert reverse_words("") == ""
    
    def test_single_character(self):
        """测试单个字符"""
        from utils.string_utils import reverse_words
        assert reverse_words("a") == "a"
        assert reverse_words("!") == "!"
    
    def test_only_spaces(self):
        """测试只有空格"""
        from utils.string_utils import reverse_words
        assert reverse_words("   ") == ""
        assert reverse_words("  \t  \n  ") == ""
    
    def test_leading_trailing_spaces(self):
        """测试前导和尾随空格"""
        from utils.string_utils import reverse_words
        # 简单实现可能会trim空格，这是可接受的行为
        assert reverse_words("  hello world  ") == "world hello"
        assert reverse_words("\thello\tworld\n") == "world hello"
    
    def test_multiple_spaces_between_words(self):
        """测试单词间多个空格"""
        from utils.string_utils import reverse_words
        # 简单实现可能会规范化空格，这是可接受的行为
        assert reverse_words("hello    world") == "world hello"
        assert reverse_words("Python  is  great") == "great is Python"


class TestUnicodeAndSpecialCharacters:
    """测试Unicode和特殊字符"""
    
    def test_chinese_text(self):
        """测试中文文本"""
        from utils.string_utils import reverse_words
        assert reverse_words("你好 世界") == "世界 你好"
        assert reverse_words("Python 编程 语言") == "语言 编程 Python"
    
    def test_emoji(self):
        """测试表情符号"""
        from utils.string_utils import reverse_words
        assert reverse_words("😀 🐍 Python") == "Python 🐍 😀"
        assert reverse_words("Hello 🌍 World") == "World 🌍 Hello"
    
    def test_mixed_languages(self):
        """测试混合语言"""
        from utils.string_utils import reverse_words
        assert reverse_words("Hello 世界 Python") == "Python 世界 Hello"
        assert reverse_words("Python 编程 is fun") == "fun is 编程 Python"
    
    def test_special_symbols(self):
        """测试特殊符号"""
        from utils.string_utils import reverse_words
        assert reverse_words("@username #tag") == "#tag @username"
        assert reverse_words("$100 €90") == "€90 $100"


class TestPerformance:
    """性能测试"""
    
    def test_long_string(self):
        """测试长字符串"""
        from utils.string_utils import reverse_words
        # 创建包含100个单词的长字符串
        long_text = "word " * 100
        result = reverse_words(long_text.strip())
        # 验证结果包含相同数量的单词
        assert len(result.split()) == 100
    
    def test_repeated_words(self):
        """测试重复单词"""
        from utils.string_utils import reverse_words
        text = "test " * 50
        result = reverse_words(text.strip())
        # 反转后应该还是相同的单词序列
        assert result == text.strip()


class TestErrorHandling:
    """错误处理测试"""
    
    def test_none_input(self):
        """测试None输入"""
        from utils.string_utils import reverse_words
        with pytest.raises(TypeError):
            reverse_words(None)
    
    def test_integer_input(self):
        """测试整数输入"""
        from utils.string_utils import reverse_words
        with pytest.raises(TypeError):
            reverse_words(123)
    
    def test_list_input(self):
        """测试列表输入"""
        from utils.string_utils import reverse_words
        with pytest.raises(TypeError):
            reverse_words(["hello", "world"])
    
    def test_dict_input(self):
        """测试字典输入"""
        from utils.string_utils import reverse_words
        with pytest.raises(TypeError):
            reverse_words({"text": "hello world"})


# 参数化测试示例
@pytest.mark.parametrize("input_text,expected_output", [
    ("hello world", "world hello"),
    ("a b c", "c b a"),
    ("Python", "Python"),
    ("", ""),
    ("  test  ", "test"),
])
def test_parametrized_reverse_words(input_text, expected_output):
    """参数化测试示例"""
    from utils.string_utils import reverse_words
    assert reverse_words(input_text) == expected_output


if __name__ == "__main__":
    """直接运行测试（不使用pytest时）"""
    # 简单运行所有测试
    import unittest
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestReverseWords))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestUnicodeAndSpecialCharacters))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n测试结果: {result.testsRun}个测试运行")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")