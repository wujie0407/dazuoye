"""
图像处理工具模块
"""

import base64
import io
from PIL import Image
from typing import Tuple


class ImageHandler:
    """图像处理工具类"""
    
    @staticmethod
    def base64_to_image(base64_str: str) -> Image.Image:
        """
        将 Base64 字符串转换为 PIL Image
        
        Args:
            base64_str: Base64 编码的图像字符串
            
        Returns:
            PIL Image 对象
        """
        # 移除 data URL 前缀
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        image_bytes = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_bytes))
    
    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
        """
        将 PIL Image 转换为字节数据
        
        Args:
            image: PIL Image 对象
            format: 图像格式
            
        Returns:
            图像字节数据
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()
    
    @staticmethod
    def resize_image(image: Image.Image, max_size: Tuple[int, int] = (1920, 1080)) -> Image.Image:
        """
        调整图像大小（保持比例）
        
        Args:
            image: PIL Image 对象
            max_size: 最大尺寸 (width, height)
            
        Returns:
            调整后的图像
        """
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """
        获取图像信息
        
        Args:
            image: PIL Image 对象
            
        Returns:
            图像信息字典
        """
        return {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
            "width": image.width,
            "height": image.height
        }