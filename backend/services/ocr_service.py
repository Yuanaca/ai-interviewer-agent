"""
OCR 服务 - 基于 EasyOCR 的图片文字识别
支持中英文混合识别，首次运行会自动下载模型
"""
import io
import os
from typing import Optional
from PIL import Image

# 延迟加载，避免启动时拖慢
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # GPU=False 用 CPU，避免 CUDA 依赖问题
        _reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # type: ignore
    return _reader


def image_to_text(image_bytes: bytes) -> str:
    """
    从图片字节流中提取文字
    支持 JPG/PNG/BMP/WEBP 等常见格式
    """
    # 打开图片
    img = Image.open(io.BytesIO(image_bytes))

    # 转 RGB（处理 RGBA/灰度等）
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    # 保存为临时文件（EasyOCR 需要文件路径或 numpy array）
    import numpy as np
    img_array = np.array(img)

    reader = _get_reader()
    results = reader.readtext(img_array)  # type: ignore

    # 按垂直位置排序，合并为段落
    if not results:
        return ""

    # 按 y 坐标分组（同一行），再按 x 排序
    line_threshold = 15  # 同一行的最大 y 偏差
    lines = []
    for (bbox, text, confidence) in results:
        if not text.strip():
            continue
        y_center = (bbox[0][1] + bbox[2][1]) / 2
        lines.append((y_center, bbox[0][0], text))

    if not lines:
        return ""

    # 按 y 排序
    lines.sort(key=lambda x: x[0])

    # 分组为行
    grouped = []
    current_line = [lines[0]]
    for item in lines[1:]:
        if abs(item[0] - current_line[-1][0]) < line_threshold:
            current_line.append(item)
        else:
            current_line.sort(key=lambda x: x[1])  # 按 x 排序
            grouped.append(current_line)
            current_line = [item]
    current_line.sort(key=lambda x: x[1])
    grouped.append(current_line)

    # 合并为文本
    text_lines = []
    for line in grouped:
        line_text = ' '.join(t[2] for t in line)
        text_lines.append(line_text)

    return '\n'.join(text_lines)


def is_image_file(filename: str) -> bool:
    """判断文件是否为图片"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif')
