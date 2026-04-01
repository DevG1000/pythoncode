# AGENTS.md creation for codebase: build, lint, tests, style guidelines, rules incorporation

**Session ID:** ses_34848935cffeqTsLQgHEEJ5toT
**Created:** 2026/3/4 15:19:37
**Updated:** 2026/3/4 15:22:31

---

## User

Please analyze this codebase and create an AGENTS.md file containing:
1. Build/lint/test commands - especially for running a single test
2. Code style guidelines including imports, formatting, types, naming conventions, error handling, etc.

The file you create will be given to agentic coding agents (such as yourself) that operate in this repository. Make it about 150 lines long.
If there are Cursor rules (in .cursor/rules/ or .cursorrules) or Copilot rules (in .github/copilot-instructions.md), make sure to include them.

If there's already an AGENTS.md, improve it if it's located in /

---

## Assistant (Build · deepseek-chat · 5.8s)

I'll analyze the codebase to understand its structure and create an AGENTS.md file with build/lint/test commands and code style guidelines.

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*"
}
```

**Output:**
```
D:\pythoncode\~$pi-key.rtf
D:\pythoncode\新建 DOCX 文档.docx
D:\pythoncode\deepseekeytest.py
D:\pythoncode\api-key.rtf
D:\pythoncode\Line2Card.py
D:\pythoncode\output.xlsx
D:\pythoncode\input.xlsx
```

---

## Assistant (Build · deepseek-chat · 3.5s)

**Tool: read**

**Input:**
```json
{
  "filePath": "D:\\pythoncode"
}
```

**Output:**
```
<path>D:\pythoncode</path>
<type>directory</type>
<entries>
~$pi-key.rtf
新建 DOCX 文档.docx
api-key.rtf
deepseekeytest.py
input.xlsx
Line2Card.py
output.xlsx

(7 entries)
</entries>
```

---

## Assistant (Build · deepseek-chat · 3.8s)

**Tool: read**

**Input:**
```json
{
  "filePath": "D:\\pythoncode\\deepseekeytest.py"
}
```

**Output:**
```
<path>D:\pythoncode\deepseekeytest.py</path>
<type>file</type>
<content>1: # 第一步：安装库（在终端执行）
2: # pip install deepseek-sdk
3: 
4: # 第二步：写代码
5: 
6: from openai import OpenAI
7: 
8: client = OpenAI(
9:     api_key="sk-06731102fb02460ba79ceef9f3a5ced3",           # 替换为真实密钥
10:     base_url="https://api.deepseek.com/v1"  # DeepSeek 兼容地址
11: )
12: 
13: 
14: response = client.chat.completions.create(
15:     model="deepseek-chat",
16:     messages=[
17:         {"role": "user", "content": "用Python写一个斐波那契数列生成器"}
18:     ]
19: )
20: 
21: print(response.choices[0].message.content)

(End of file - total 21 lines)
</content>
```

---

## Assistant (Build · deepseek-chat · 3.9s)

**Tool: read**

**Input:**
```json
{
  "filePath": "D:\\pythoncode\\Line2Card.py"
}
```

**Output:**
```
<path>D:\pythoncode\Line2Card.py</path>
<type>file</type>
<content>1: import openpyxl
2: from openpyxl.drawing.image import Image as XLImage
3: from openpyxl.utils import get_column_letter
4: from PIL import Image, ImageDraw, ImageFont
5: import io
6: import os
7: 
8: def create_business_card(data, width=400, height=250):
9:     """
10:     根据人员信息生成名片图像
11:     data : dict，包含 name, title, company, phone, email, address
12:     width, height : 图像尺寸（像素）
13:     """
14:     # 创建白色背景图像
15:     img = Image.new('RGB', (width, height), color='white')
16:     draw = ImageDraw.Draw(img)
17: 
18:     # 绘制边框
19:     draw.rectangle([(0, 0), (width-1, height-1)], outline='black', width=2)
20: 
21:     # 设置字体（优先使用中文字体，若找不到则用默认字体）
22:     font_large = ImageFont.load_default()
23:     font_medium = font_large
24:     font_small = font_large
25: 
26: 
27:     try:
28:         # 常见中文字体路径（可根据系统调整）
29:         font_paths = [
30:             'C:/Windows/Fonts/msyh.ttc',          # 微软雅黑 (Windows)
31:             '/System/Library/Fonts/PingFang.ttc', # 苹方 (macOS)
32:             '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf' # Linux
33:         ]
34:         font_file = None
35:         for path in font_paths:
36:             if os.path.exists(path):
37:                 font_file = path 
38:                 break
39:         if font_file:
40:                 font_large = ImageFont.truetype(font_file, 24)
41:                 font_medium = ImageFont.truetype(font_file, 16)
42:                 font_small = ImageFont.truetype(font_file, 12)
43:         else:
44:                 raise FileNotFoundError
45:     except:
46:         # 默认字体（不支持中文）
47:         font_large = ImageFont.load_default()
48:         font_medium = font_large
49:         font_small = font_large
50: 
51:     # 绘制文本
52:     y = 20
53: 
54:     print(data)
55:     print(data.get('name', ''))
56:     print(font_large)
57:     draw.text((20, y), data.get('name', ''), fill='black', font=font_large)
58:     y += 30
59:     draw.text((20, y), data.get('title', ''), fill='gray', font=font_medium)
60:     y += 25
61:     draw.text((20, y), data.get('company', ''), fill='black', font=font_medium)
62:     y += 30
63:     draw.text((20, y), f"电话: {data.get('phone', '')}", fill='black', font=font_small)
64:     y += 20
65:     draw.text((20, y), f"邮箱: {data.get('email', '')}", fill='black', font=font_small)
66:     y += 20
67:     if data.get('address'):
68:         draw.text((20, y), f"地址: {data.get('address', '')}", fill='black', font=font_small)
69: 
70:     return img
71: 
72: def add_business_cards_to_excel(input_file, output_file=None, sheet_name=None,
73:                                 name_col=4, title_col=5, company_col=3,
74:                                 phone_col=6, email_col=8, address_col=9,
75:                                 image_col=10):
76:     """
77:     读取Excel，为每行生成名片并插入到指定列
78:     参数均为列号（从1开始）
79:     """
80:     wb = openpyxl.load_workbook(input_file)
81:     if sheet_name is None:
82:         sheet = wb.active
83:     else:
84:         sheet = wb[sheet_name]
85: 
86:     # 假设第一行为标题行，数据从第2行开始
87:     start_row = 2
88:     max_row = sheet.max_row
89: 
90:     for row in range(start_row, max_row + 1):
91:         # 读取人员信息
92:         name = sheet.cell(row=row, column=name_col).value
93:         if not name:   # 姓名空则跳过该行
94:             continue
95:         title = sheet.cell(row=row, column=title_col).value or ""
96:         company = sheet.cell(row=row, column=company_col).value or ""
97:         phone = sheet.cell(row=row, column=phone_col).value or ""
98:         email = sheet.cell(row=row, column=email_col).value or ""
99:         address = sheet.cell(row=row, column=address_col).value if address_col else ""
100: 
101:         data = {
102:             'name': name,
103:             'title': title,
104:             'company': company,
105:             'phone': phone,
106:             'email': email,
107:             'address': address
108:         }
109: 
110:         # 生成名片图像
111:         pil_img = create_business_card(data)
112: 
113:         # 将图像保存到内存字节流
114:         img_bytes = io.BytesIO()
115:         pil_img.save(img_bytes, format='PNG')
116:         img_bytes.seek(0)
117: 
118:         # 创建openpyxl图像对象
119:         xl_img = XLImage(img_bytes)
120: 
121:         # 可选：缩放图像（若图像太大）
122:         # xl_img.width = 200
123:         # xl_img.height = 125
124: 
125:         # 插入到目标单元格（左上角对齐单元格）
126:         cell = f"{get_column_letter(image_col)}{row}"
127:         sheet.add_image(xl_img, cell)
128: 
129:         # 调整行高以适应图像高度（像素转磅：1像素 ≈ 0.75磅）
130:         img_height_pt = pil_img.height * 0.75
131:         current_height = sheet.row_dimensions[row].height
132:         if current_height is None or current_height < img_height_pt:
133:             sheet.row_dimensions[row].height = img_height_pt
134: 
135:         # 调整列宽（粗略设置，列宽单位≈字符数）
136:         # sheet.column_dimensions[get_column_letter(image_col)].width = 25
137: 
138:     # 保存文件
139:     if output_file is None:
140:         output_file = input_file
141:     wb.save(output_file)
142:     print(f"处理完成，已保存至: {output_file}")
143: 
144: if __name__ == "__main__":
145:     # 使用示例：将 input.xlsx 中的人员信息生成名片，保存为 output.xlsx
146:     add_business_cards_to_excel('D:\pythoncode\input.xlsx', 'D:\pythoncode\output.xlsx')

(End of file - total 146 lines)
</content>
```

---

## Assistant (Build · deepseek-chat · 5.5s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*.md"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 5.1s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/package.json"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 4.8s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/requirements.txt"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 5.1s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/pyproject.toml"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 4.7s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/.cursor/**"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 4.6s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/.cursorrules"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 6.3s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/.github/copilot-instructions.md"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 4.6s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/setup.py"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · deepseek-chat · 3.3s)

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*.py"
}
```

**Output:**
```
D:\pythoncode\deepseekeytest.py
D:\pythoncode\Line2Card.py
```

---

## Assistant (Build · deepseek-chat · 6.1s)

**Tool: bash**

**Input:**
```json
{
  "command": "python --version",
  "description": "Check Python version"
}
```

**Output:**
```
Python 3.14.3

```

---

## Assistant (Build · deepseek-chat · 10.7s)

**Tool: bash**

**Input:**
```json
{
  "command": "pip list",
  "description": "Check installed Python packages"
}
```

**Output:**
```
Package Version
------- -------
pip     25.3

```

---

## Assistant (Build · deepseek-chat · 6.0s)

**Tool: bash**

**Input:**
```json
{
  "command": "python -c \"import openpyxl; print('openpyxl version:', openpyxl.__version__)\"",
  "description": "Check openpyxl version"
}
```

**Output:**
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import openpyxl; print('openpyxl version:', openpyxl.__version__)
    ^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'openpyxl'

```

---

## Assistant (Build · deepseek-chat · 5.2s)

**Tool: bash**

**Input:**
```json
{
  "command": "python -c \"import PIL; print('PIL version:', PIL.__version__)\"",
  "description": "Check PIL version"
}
```

**Output:**
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import PIL; print('PIL version:', PIL.__version__)
    ^^^^^^^^^^
ModuleNotFoundError: No module named 'PIL'

```

---

## Assistant (Build · deepseek-chat · 5.0s)

**Tool: bash**

**Input:**
```json
{
  "command": "python -c \"import openai; print('openai version:', openai.__version__)\"",
  "description": "Check openai version"
}
```

**Output:**
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import openai; print('openai version:', openai.__version__)
    ^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'openai'

```

---

## Assistant (Build · deepseek-chat · 70.8s)

Now I'll create the AGENTS.md file based on my analysis of the codebase:

**Tool: write**

**Input:**
```json
{
  "filePath": "D:\\pythoncode\\AGENTS.md",
  "content": "# AGENTS.md - Python Codebase Guidelines\n\nThis document provides guidelines for agentic coding agents working in this Python codebase.\n\n## Project Overview\n\nThis is a Python project containing:\n- `Line2Card.py`: A business card generator that reads Excel data and creates image-based business cards\n- `deepseekeytest.py`: A test script for DeepSeek API integration\n- Excel files for input/output data processing\n\n## Build, Lint, and Test Commands\n\n### Environment Setup\n```bash\n# Install required dependencies\npip install openpyxl pillow openai\n\n# Verify installation\npython -c \"import openpyxl; import PIL; import openai; print('All packages installed successfully')\"\n```\n\n### Running Code\n```bash\n# Run Line2Card.py (business card generator)\npython Line2Card.py\n\n# Run deepseekeytest.py (API test)\npython deepseekeytest.py\n```\n\n### Testing\n```bash\n# Run all Python files\npython *.py\n\n# Run specific file\npython Line2Card.py\npython deepseekeytest.py\n```\n\n### Code Quality\n```bash\n# Check Python syntax\npython -m py_compile *.py\n\n# Type checking (if using type hints)\npython -m mypy *.py --ignore-missing-imports\n\n# Linting with flake8 (if installed)\npython -m flake8 *.py\n\n# Formatting with black (if installed)\npython -m black *.py\n```\n\n## Code Style Guidelines\n\n### Imports\n```python\n# Standard library imports first\nimport io\nimport os\n\n# Third-party imports next\nfrom openpyxl import load_workbook\nfrom openpyxl.drawing.image import Image as XLImage\nfrom openpyxl.utils import get_column_letter\nfrom PIL import Image, ImageDraw, ImageFont\n\n# Local/application imports last (if any)\n# from . import local_module\n```\n\n### Formatting\n- Use 4 spaces for indentation (no tabs)\n- Maximum line length: 79 characters (PEP 8)\n- Use double quotes for docstrings, single quotes for strings\n- Add blank lines between functions and classes\n- Use descriptive variable names\n\n### Naming Conventions\n- **Functions and variables**: `snake_case`\n- **Constants**: `UPPER_SNAKE_CASE`\n- **Classes**: `PascalCase`\n- **Private functions/variables**: `_leading_underscore`\n\n### Function Definitions\n```python\ndef function_name(param1, param2=None):\n    \"\"\"\n    Brief description of function.\n    \n    Args:\n        param1: Description of first parameter\n        param2: Description of second parameter (default: None)\n    \n    Returns:\n        Description of return value\n    \n    Raises:\n        ExceptionType: When and why this exception is raised\n    \"\"\"\n    # Function body\n    return result\n```\n\n### Error Handling\n```python\n# Use try-except for expected errors\ntry:\n    result = risky_operation()\nexcept SpecificError as e:\n    # Handle specific error\n    logger.error(f\"Operation failed: {e}\")\n    fallback_operation()\nexcept Exception as e:\n    # Catch-all with logging\n    logger.error(f\"Unexpected error: {e}\")\n    raise\n```\n\n### Type Hints (Recommended)\n```python\nfrom typing import Dict, Optional, List, Tuple\n\ndef process_data(data: Dict[str, str]) -> Optional[str]:\n    \"\"\"Process data with type hints.\"\"\"\n    if not data:\n        return None\n    return data.get('key')\n```\n\n### Documentation\n- All public functions/methods must have docstrings\n- Use Google-style docstring format\n- Include parameter descriptions, return values, and exceptions\n- Add inline comments for complex logic\n\n## Project-Specific Patterns\n\n### Excel Processing (Line2Card.py)\n- Use `openpyxl` for Excel file operations\n- Column indices start at 1 (not 0)\n- Handle missing data with `or \"\"` fallbacks\n- Use `get_column_letter()` for column references\n- Adjust row heights for image insertion\n\n### Image Processing\n- Use `PIL` (Pillow) for image creation\n- Handle font fallbacks gracefully\n- Convert pixel dimensions to Excel points (1px ≈ 0.75pt)\n- Save images to memory buffers for Excel insertion\n\n### API Integration (DeepSeek)\n- Store API keys securely (not hardcoded)\n- Use environment variables for sensitive data\n- Handle API errors with appropriate retry logic\n- Validate responses before processing\n\n## File Structure\n```\nproject/\n├── AGENTS.md              # This file\n├── Line2Card.py          # Main business card generator\n├── deepseekeytest.py     # API integration test\n├── input.xlsx           # Input data file\n├── output.xlsx          # Output file (generated)\n└── *.rtf/.docx          # Documentation files\n```\n\n## Common Tasks\n\n### Adding New Features\n1. Check existing patterns in `Line2Card.py`\n2. Follow import and function structure\n3. Add comprehensive error handling\n4. Test with sample data\n5. Update documentation if needed\n\n### Modifying Excel Processing\n1. Verify column indices match input file structure\n2. Handle empty/missing values gracefully\n3. Maintain backward compatibility\n4. Test with both existing and new data formats\n\n### Testing Changes\n1. Run the script with sample input\n2. Verify output file is created correctly\n3. Check for any console errors\n4. Validate image quality and placement\n\n## Security Notes\n- Never commit API keys or sensitive data\n- Use environment variables for credentials\n- Validate all user inputs\n- Handle file paths securely\n- Use context managers for file operations\n\n## Performance Considerations\n- Process large Excel files in chunks if needed\n- Cache font loading for multiple images\n- Use memory-efficient image processing\n- Clean up temporary resources\n\n## Troubleshooting\n\n### Common Issues\n1. **Missing fonts**: Check font paths and fallbacks\n2. **Excel file errors**: Verify file format and permissions\n3. **Image insertion issues**: Check row heights and column widths\n4. **API errors**: Verify network connectivity and API keys\n\n### Debugging\n```python\n# Add debug prints for complex operations\nprint(f\"Processing row {row}: {data}\")\n\n# Use logging for production code\nimport logging\nlogging.basicConfig(level=logging.DEBUG)\n```\n\n## Best Practices\n1. Write modular, reusable functions\n2. Keep functions focused on single responsibilities\n3. Use descriptive variable and function names\n4. Add error handling for all external operations\n5. Document complex algorithms and business logic\n6. Test edge cases and error conditions\n7. Follow PEP 8 style guidelines\n\n## Notes for Agents\n- This is a Windows-based Python project\n- Files use Windows-style paths (backslashes)\n- Font paths are Windows-specific by default\n- Adjust paths for cross-platform compatibility if needed\n- Always test changes before considering work complete"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · deepseek-chat · 9.4s)

Created AGENTS.md with comprehensive guidelines for agentic coding agents. The file includes:

1. **Build/lint/test commands** - Installation, running scripts, and code quality checks
2. **Code style guidelines** - Imports, formatting, naming conventions, error handling, type hints
3. **Project-specific patterns** - Excel processing, image creation, API integration
4. **Common tasks and troubleshooting** - Adding features, modifying Excel processing, debugging
5. **Security and performance considerations**

The guidelines are tailored to this Python codebase's specific needs, focusing on the business card generator and API test scripts.

---

