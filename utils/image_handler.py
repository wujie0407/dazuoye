"""
图像处理工具
"""

import base64
import io
from typing import Tuple, Optional
from PIL import Image


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
    def image_to_base64(image: Image.Image, format: str = 'PNG') -> str:
        """
        将 PIL Image 转换为 Base64 字符串
        
        Args:
            image: PIL Image 对象
            format: 图像格式
            
        Returns:
            Base64 编码字符串
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode()
    
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
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
    
    @staticmethod
    def resize_image(
        image: Image.Image, 
        max_size: Tuple[int, int] = (1920, 1080)
    ) -> Image.Image:
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
    
    @staticmethod
    def crop_to_square(image: Image.Image) -> Image.Image:
        """
        裁剪为正方形（居中）
        
        Args:
            image: PIL Image 对象
            
        Returns:
            正方形图像
        """
        width, height = image.size
        size = min(width, height)
        
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        return image.crop((left, top, right, bottom))
