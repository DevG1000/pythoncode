import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from PIL import Image, ImageDraw, ImageFont
import io
import os
import sys
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache

# 字体缓存
_FONT_CACHE = {}

@lru_cache(maxsize=3)
def _find_font_file() -> Optional[str]:
    """
    查找可用的中文字体文件（缓存结果）
    返回: 字体文件路径或None
    """
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',          # 微软雅黑 (Windows)
        '/System/Library/Fonts/PingFang.ttc', # 苹方 (macOS)
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf' # Linux
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None

def _get_cached_font(size: int) -> ImageFont.FreeTypeFont:
    """
    获取缓存字体
    参数: size - 字体大小
    返回: PIL字体对象
    """
    if size not in _FONT_CACHE:
        font_file = _find_font_file()
        if font_file:
            _FONT_CACHE[size] = ImageFont.truetype(font_file, size)
        else:
            _FONT_CACHE[size] = ImageFont.load_default()
    
    return _FONT_CACHE[size]

@dataclass
class ExcelProcessingConfig:
    """Excel处理配置类 - 遵循ISP原则"""
    input_file: str
    output_file: Optional[str] = None
    sheet_name: Optional[str] = None
    name_col: int = 4
    title_col: int = 5
    company_col: int = 3
    phone_col: int = 6
    email_col: int = 8
    address_col: int = 9
    image_col: int = 10
    chunk_size: int = 50
    show_progress: bool = True
    
    def validate(self):
        """验证配置参数"""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"输入文件不存在: {self.input_file}")
        
        # 验证列号在合理范围内
        columns = [self.name_col, self.title_col, self.company_col, 
                  self.phone_col, self.email_col, self.address_col, self.image_col]
        for col in columns:
            if col < 1 or col > 16384:  # Excel最大列数
                raise ValueError(f"列号必须在1-16384之间: {col}")
        
        if self.chunk_size < 1:
            raise ValueError(f"分块大小必须大于0: {self.chunk_size}")

@dataclass
class BusinessCardData:
    """名片数据类"""
    name: str
    title: str = ""
    company: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""

def create_business_card(data: Dict[str, str], width: int = 400, height: int = 250) -> Image.Image:
    """
    根据人员信息生成名片图像（优化版）
    
    参数:
        data: 包含 name, title, company, phone, email, address 的字典
        width, height: 图像尺寸（像素）
    
    返回:
        PIL图像对象
    """
    # 创建白色背景图像
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # 绘制边框
    draw.rectangle([(0, 0), (width-1, height-1)], outline='black', width=2)

    # 使用缓存字体（避免重复加载）
    font_large = _get_cached_font(24)
    font_medium = _get_cached_font(16)
    font_small = _get_cached_font(12)

    # 绘制文本
    y = 20
    
    # 使用局部变量减少字典访问
    name = data.get('name', '')
    title = data.get('title', '')
    company = data.get('company', '')
    phone = data.get('phone', '')
    email = data.get('email', '')
    address = data.get('address', '')
    
    draw.text((20, y), name, fill='black', font=font_large)
    y += 30
    draw.text((20, y), title, fill='gray', font=font_medium)
    y += 25
    draw.text((20, y), company, fill='black', font=font_medium)
    y += 30
    draw.text((20, y), f"电话: {phone}", fill='black', font=font_small)
    y += 20
    draw.text((20, y), f"邮箱: {email}", fill='black', font=font_small)
    y += 20
    if address:
        draw.text((20, y), f"地址: {address}", fill='black', font=font_small)

    return img

def add_business_cards_to_excel(config: ExcelProcessingConfig) -> str:
    """
    读取Excel，为每行生成名片并插入到指定列（优化版）- 遵循ISP原则
    
    参数:
        config: Excel处理配置
    
    返回:
        输出文件路径
    """
    # 验证配置
    config.validate()
    
    start_time = time.time()
    
    # 加载工作簿
    wb = openpyxl.load_workbook(config.input_file)
    sheet = wb[config.sheet_name] if config.sheet_name else wb.active
    
    # 计算处理范围
    start_row = 2
    max_row = sheet.max_row
    total_rows = max_row - start_row + 1
    
    if config.show_progress:
        print(f"开始处理Excel文件: {config.input_file}")
        print(f"总行数: {total_rows}")
        print(f"分块大小: {config.chunk_size}")
    
    processed = 0
    errors = 0
    
    # 分块处理优化内存使用
    for chunk_start in range(start_row, max_row + 1, config.chunk_size):
        chunk_end = min(chunk_start + config.chunk_size - 1, max_row)
        
        for row in range(chunk_start, chunk_end + 1):
            try:
                # 读取人员信息
                name = sheet.cell(row=row, column=config.name_col).value
                if not name:   # 姓名空则跳过该行
                    continue
                
                title = sheet.cell(row=row, column=config.title_col).value or ""
                company = sheet.cell(row=row, column=config.company_col).value or ""
                phone = sheet.cell(row=row, column=config.phone_col).value or ""
                email = sheet.cell(row=row, column=config.email_col).value or ""
                address = sheet.cell(row=row, column=config.address_col).value if config.address_col else ""
                
                data = {
                    'name': name,
                    'title': title,
                    'company': company,
                    'phone': phone,
                    'email': email,
                    'address': address
                }
                
                # 生成名片图像
                pil_img = create_business_card(data)
                
                # 将图像保存到内存字节流，使用with语句确保资源释放
                with io.BytesIO() as img_bytes:
                    pil_img.save(img_bytes, format='PNG', optimize=True)  # 优化PNG压缩
                    img_bytes.seek(0)
                    
                    # 创建openpyxl图像对象
                    xl_img = XLImage(img_bytes)
                    
                    # 插入到目标单元格
                    cell = f"{get_column_letter(config.image_col)}{row}"
                    sheet.add_image(xl_img, cell)
                    
                    # 调整行高以适应图像高度
                    img_height_pt = pil_img.height * 0.75
                    current_height = sheet.row_dimensions[row].height
                    if current_height is None or current_height < img_height_pt:
                        sheet.row_dimensions[row].height = img_height_pt
                
                processed += 1
                
                # 显示进度
                if config.show_progress and processed % 10 == 0:
                    progress = processed / total_rows * 100
                    print(f"进度: {processed}/{total_rows} ({progress:.1f}%)")
                    
            except Exception as e:
                errors += 1
                if config.show_progress:
                    print(f"第{row}行处理失败: {e}")
                continue
        
        # 每处理完一个块，可以强制垃圾回收（可选）
        if config.chunk_size >= 100:
            import gc
            gc.collect()
    
    # 保存文件
    output_file = config.output_file or config.input_file
    
    wb.save(output_file)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    if config.show_progress:
        print(f"\n处理完成!")
        print(f"成功处理: {processed} 行")
        print(f"失败: {errors} 行")
        print(f"总耗时: {elapsed:.2f} 秒")
        print(f"平均每行: {elapsed/processed*1000:.1f} 毫秒" if processed > 0 else "无成功处理的行")
        print(f"输出文件: {output_file}")
    
    return output_file

def add_business_cards_to_excel_legacy(input_file: str, output_file: Optional[str] = None, 
                                sheet_name: Optional[str] = None,
                                name_col: int = 4, title_col: int = 5, company_col: int = 3,
                                phone_col: int = 6, email_col: int = 8, address_col: int = 9,
                                image_col: int = 10, chunk_size: int = 50,
                                show_progress: bool = True) -> str:
    """
    向后兼容的旧版本函数 - 使用配置类包装新函数
    
    参数:
        input_file: 输入Excel文件路径
        output_file: 输出文件路径（默认覆盖输入文件）
        sheet_name: 工作表名称（默认活动工作表）
        name_col, title_col, etc.: 数据列号（从1开始）
        image_col: 图像插入列号
        chunk_size: 分块处理大小（优化内存使用）
        show_progress: 是否显示进度
    
    返回:
        输出文件路径
    """
    config = ExcelProcessingConfig(
        input_file=input_file,
        output_file=output_file,
        sheet_name=sheet_name,
        name_col=name_col,
        title_col=title_col,
        company_col=company_col,
        phone_col=phone_col,
        email_col=email_col,
        address_col=address_col,
        image_col=image_col,
        chunk_size=chunk_size,
        show_progress=show_progress
    )
    
    return add_business_cards_to_excel(config)

def benchmark_performance():
    """性能基准测试"""
    print("=" * 60)
    print("Line2Card 性能基准测试")
    print("=" * 60)
    
    test_data = {
        'name': '测试用户',
        'title': '测试职位',
        'company': '测试公司',
        'phone': '1234567890',
        'email': 'test@example.com',
        'address': '测试地址'
    }
    
    # 测试单张名片生成
    print("\n1. 测试单张名片生成性能:")
    start = time.time()
    for i in range(100):
        img = create_business_card(test_data)
    end = time.time()
    print(f"   生成100张名片耗时: {end - start:.3f}秒")
    print(f"   平均每张: {(end - start) * 10:.1f}毫秒")
    
    # 测试字体缓存效果
    print("\n2. 测试字体缓存效果:")
    start = time.time()
    for i in range(100):
        _get_cached_font(24)
        _get_cached_font(16)
        _get_cached_font(12)
    end = time.time()
    print(f"   100次字体获取耗时: {end - start:.3f}秒")
    
    # 内存使用测试
    print("\n3. 内存使用分析:")
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024
    
    images = []
    for i in range(50):
        images.append(create_business_card(test_data))
    
    mem_after = process.memory_info().rss / 1024 / 1024
    print(f"   生成50张图像内存增加: {mem_after - mem_before:.1f}MB")
    print(f"   平均每张图像内存: {(mem_after - mem_before) * 1024 / 50:.0f}KB")
    
    # 清理
    del images
    import gc
    gc.collect()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成名片并插入Excel')
    parser.add_argument('--input', default=r'D:\pythoncode\input.xlsx', help='输入Excel文件路径')
    parser.add_argument('--output', help='输出Excel文件路径（默认覆盖输入文件）')
    parser.add_argument('--sheet', help='工作表名称')
    parser.add_argument('--benchmark', action='store_true', help='运行性能基准测试')
    parser.add_argument('--chunk-size', type=int, default=50, help='分块处理大小')
    parser.add_argument('--no-progress', action='store_true', help='不显示进度')
    
    args = parser.parse_args()
    
    if args.benchmark:
        benchmark_performance()
    else:
        add_business_cards_to_excel(
            input_file=args.input,
            output_file=args.output,
            sheet_name=args.sheet,
            chunk_size=args.chunk_size,
            show_progress=not args.no_progress
        )

if __name__ == "__main__":
    main()
