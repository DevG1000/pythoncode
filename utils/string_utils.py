"""
字符串处理工具模块
包含单词反转函数及其相关功能
"""
from typing import Any


def reverse_words(text: str) -> str:
    """
    反转句子中的单词顺序。
    
    这个函数接受一个字符串，将其按空格分割成单词，
    然后反转单词的顺序并重新组合成字符串。
    
    示例:
        >>> reverse_words("hello world")
        'world hello'
        >>> reverse_words("Python is great")
        'great is Python'
        >>> reverse_words("")
        ''
    
    注意:
        - 多个连续空格会被视为一个分隔符
        - 前导和尾随空格会被移除
        - 标点符号会保留在原始单词中
    
    Args:
        text: 要处理的输入字符串
        
    Returns:
        单词顺序反转后的字符串
        
    Raises:
        TypeError: 如果输入不是字符串类型
        
    >>> reverse_words("hello world")
    'world hello'
    >>> reverse_words("a b c")
    'c b a'
    >>> reverse_words("")
    ''
    """
    # 输入验证
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    # 最小实现：使用Python内置方法
    # 1. 使用split()分割单词（默认按任意空白字符分割）
    # 2. 使用reversed()反转单词列表
    # 3. 使用join()重新组合成字符串
    
    words = text.split()
    reversed_words = list(reversed(words))
    return ' '.join(reversed_words)


def reverse_string(text: str) -> str:
    """
    反转整个字符串（字符级别）。
    
    示例:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
    
    Args:
        text: 要反转的字符串
        
    Returns:
        反转后的字符串
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    return text[::-1]


def count_words(text: str) -> int:
    """
    计算字符串中的单词数量。
    
    示例:
        >>> count_words("hello world")
        2
        >>> count_words("")
        0
    
    Args:
        text: 输入字符串
        
    Returns:
        单词数量
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    return len(text.split())


def _validate_string_input(value: Any, param_name: str = "text") -> None:
    """
    验证字符串输入的内部辅助函数。
    
    Args:
        value: 要验证的值
        param_name: 参数名称（用于错误消息）
        
    Raises:
        TypeError: 如果值不是字符串
    """
    if not isinstance(value, str):
        raise TypeError(f"{param_name} must be a string, got {type(value).__name__}")


# 模块级别的文档测试
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    
    # 简单演示
    print("=" * 50)
    print("字符串工具模块演示")
    print("=" * 50)
    
    test_cases = [
        "hello world",
        "Python programming",
        "this is a test",
        "",
        "   multiple   spaces   ",
    ]
    
    for test in test_cases:
        print(f"输入: '{test}'")
        print(f"  单词反转: '{reverse_words(test)}'")
        print(f"  字符串反转: '{reverse_string(test)}'")
        print(f"  单词数量: {count_words(test)}")
        print()