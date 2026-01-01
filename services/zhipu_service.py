"""
智谱 AI 图像生成服务
CogView-4 API 集成
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger(__name__)


class ZhipuImageService:
    """智谱 AI 图像生成服务"""
    
    # 备选模型列表（按优先级排序）
    FALLBACK_MODELS = [
        "cogView-4-250304",
        "cogview-4-250304", 
        "cogview-3-plus",
        "cogview-3",
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            api_key: 智谱 API Key，为空则使用配置文件中的值
        """
        cfg = get_config()
        self.api_key = api_key or cfg.api.ZHIPU_API_KEY
        self.base_url = cfg.api.ZHIPU_BASE_URL
        self.default_model = cfg.api.ZHIPU_MODEL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self._session = requests.Session()
        self._session.trust_env = False
    
    def generate_prompt(self, design_data: Dict[str, Any]) -> str:
        """
        根据设计数据生成 AI 绘图提示词
        
        Args:
            design_data: 设计数据（包含材料选择）
            
        Returns:
            AI 绘图提示词
        """
        cfg = get_config()
        materials = design_data.get('materials', {})
        descriptions = cfg.materials.MATERIAL_DESCRIPTIONS
        
        prompt_parts = ["一只精美的中国传统风筝"]
        
        # 骨架材料
        frame_materials = materials.get('骨架材料', [])
        if frame_materials:
            desc = ', '.join([descriptions.get(m, m) for m in frame_materials])
            prompt_parts.append(f"骨架使用{desc}")
        
        # 面料材料
        surface_materials = materials.get('风筝面料', [])
        if surface_materials:
            desc = ', '.join([descriptions.get(m, m) for m in surface_materials])
            prompt_parts.append(f"面料是{desc}")
        
        # 绳索材料
        string_materials = materials.get('绳索材料', [])
        if string_materials:
            desc = ', '.join([descriptions.get(m, m) for m in string_materials])
            prompt_parts.append(f"使用{desc}作为牵引线")
        
        # 场景描述
        prompt_parts.extend([
            "在蓝天白云下飞翔",
            "阳光明媚，微风轻拂",
            "高质量，细节丰富，专业摄影",
            "4K分辨率，超清晰"
        ])
        
        return "，".join(prompt_parts) + "。"
    
    def _try_generate(
        self,
        model: str,
        prompt: str,
        size: str = "1024x1024"
    ) -> Optional[Dict[str, Any]]:
        """尝试使用指定模型生成图像"""
        url = f"{self.base_url}/images/generations"
        
        payload = {
            "model": model,
            "prompt": prompt,
        }
        
        # CogView-3 系列支持 size 参数
        if "cogview-3" in model.lower():
            payload["size"] = size
        
        logger.debug(f"尝试模型: {model}")
        
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    image_url = data['data'][0].get('url')
                    
                    if image_url:
                        logger.info(f"使用 {model} 生成成功")
                        return {
                            'url': image_url,
                            'task_id': data.get('id'),
                            'model': model,
                            'prompt': prompt,
                            'created_at': data.get('created')
                        }
            
            logger.warning(f"{model} 生成失败: {response.status_code}")
            return None
            
        except requests.Timeout:
            logger.warning(f"{model} 请求超时")
            return None
        except Exception as e:
            logger.error(f"{model} 错误: {e}")
            return None
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024"
    ) -> Optional[Dict[str, Any]]:
        """
        生成图像（自动尝试多个模型）
        
        Args:
            prompt: 提示词
            size: 图像尺寸
            
        Returns:
            生成结果或 None
        """
        logger.info(f"开始生成图像: {prompt[:50]}...")
        
        # 优先使用默认模型
        models_to_try = [self.default_model] + [
            m for m in self.FALLBACK_MODELS if m != self.default_model
        ]
        
        for model in models_to_try:
            result = self._try_generate(model, prompt, size)
            if result:
                return result
            time.sleep(0.5)
        
        logger.error("所有模型均失败")
        return None
    
    def generate_kite_image(
        self,
        design_data: Dict[str, Any],
        size: str = "1024x1024"
    ) -> Optional[Dict[str, Any]]:
        """
        根据风筝设计生成图像
        
        Args:
            design_data: 设计数据
            size: 图像尺寸
            
        Returns:
            生成结果
        """
        prompt = self.generate_prompt(design_data)
        return self.generate_image(prompt, size=size)
    
    def test_connection(self) -> Dict[str, Any]:
        """测试 API 连接"""
        test_prompt = "一只可爱的小猫咪"
        
        for model in self.FALLBACK_MODELS:
            result = self._try_generate(model, test_prompt)
            if result:
                return {
                    'success': True,
                    'working_model': model,
                    'message': f'API 连接正常，可用模型: {model}'
                }
        
        return {
            'success': False,
            'working_model': None,
            'message': '所有模型均不可用'
        }
