# 第一步：安装库（在终端执行）
# pip install deepseek-sdk

# 第二步：写代码

from openai import OpenAI

client = OpenAI(
    api_key="sk-06731102fb02460ba79ceef9f3a5ced3",           # 替换为真实密钥
    base_url="https://api.deepseek.com/v1"  # DeepSeek 兼容地址
)


response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "用Python写一个斐波那契数列生成器"}
    ]
)

print(response.choices[0].message.content)
