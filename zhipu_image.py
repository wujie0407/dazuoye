"""
智谱 AI 图像生成服务
CogView-4 API 集成
"""

import requests
import time
import base64
from typing import Dict, Any, Optional


class ZhipuImageGenerator:
    """智谱 AI 图像生成器"""
    
    BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
    
    def __init__(self, api_key: str):
        """
        初始化
        
        Args:
            api_key: 智谱 API Key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_kite_prompt(self, design_data: Dict[str, Any]) -> str:
        """
        根据风筝设计数据生成 AI 绘图提示词
        
        Args:
            design_data: 设计数据（包含材料选择）
            
        Returns:
            AI 绘图提示词
        """
        materials = design_data.get('materials', {})
        
        # 提取材料
        frame_materials = materials.get('骨架材料', [])
        surface_materials = materials.get('风筝面料', [])
        string_materials = materials.get('绳索材料', [])
        
        # 材料到视觉描述的映射
        material_descriptions = {
            # 骨架材料
            '竹子': '竹制骨架，自然的竹节纹理',
            '铝合金': '银色金属骨架，现代工业感',
            '碳纤维': '黑色碳纤维骨架，科技感十足',
            
            # 风筝面料
            '丝绸': '丝绸材质，柔软光滑，带有自然光泽',
            '尼龙': '尼龙布料，色彩鲜艳，现代感',
            'Mylar膜': '镭射膜材质，反光效果，未来科技感',
            
            # 绳索材料
            '麻绳': '天然麻绳，粗糙质感',
            '钢索': '金属钢索，坚固有力',
            '凯夫拉': '黑色凯夫拉纤维，高科技材质'
        }
        
        # 构建提示词
        prompt_parts = []
        
        # 基础描述
        prompt_parts.append("一只精美的中国传统风筝")
        
        # 添加骨架描述
        if frame_materials:
            frame_desc = ', '.join([material_descriptions.get(m, m) for m in frame_materials])
            prompt_parts.append(f"骨架使用{frame_desc}")
        
        # 添加面料描述
        if surface_materials:
            surface_desc = ', '.join([material_descriptions.get(m, m) for m in surface_materials])
            prompt_parts.append(f"面料是{surface_desc}")
        
        # 添加绳索描述
        if string_materials:
            string_desc = ', '.join([material_descriptions.get(m, m) for m in string_materials])
            prompt_parts.append(f"使用{string_desc}作为牵引线")
        
        # 风格和场景
        prompt_parts.append("在蓝天白云下飞翔")
        prompt_parts.append("阳光明媚，微风轻拂")
        prompt_parts.append("高质量，细节丰富，专业摄影")
        prompt_parts.append("4K分辨率，超清晰")
        
        # 组合提示词
        prompt = "，".join(prompt_parts) + "。"
        
        return prompt
    
    def generate_image(
        self, 
        prompt: str, 
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Optional[Dict[str, Any]]:
        """
        生成图像
        
        Args:
            prompt: 提示词
            size: 图像尺寸 (1024x1024, 768x1344, 1344x768, 1024x1792, 1792x1024)
            quality: 质量 (standard, hd)
            
        Returns:
            生成结果 {'url': '...', 'task_id': '...'}
        """
        url = f"{self.BASE_URL}/images/generations"
        
        payload = {
            "model": "cogview-4-20250304",  # 最新模型
            "prompt": prompt,
            "size": size,
            "quality": quality
        }
        
        print(f"[智谱AI] 开始生成图像...")
        print(f"[智谱AI] 提示词: {prompt}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            
            print(f"[智谱AI] 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 提取图像 URL
                if 'data' in data and len(data['data']) > 0:
                    image_data = data['data'][0]
                    image_url = image_data.get('url')
                    
                    if image_url:
                        print(f"[智谱AI] ✅ 生成成功！")
                        return {
                            'url': image_url,
                            'task_id': data.get('id'),
                            'prompt': prompt,
                            'created_at': data.get('created')
                        }
                
                print(f"[智谱AI] ⚠️ 响应格式异常: {data}")
                return None
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', error_msg)
                except:
                    pass
                
                print(f"[智谱AI] ❌ 生成失败 ({response.status_code}): {error_msg}")
                return None
                
        except requests.Timeout:
            print(f"[智谱AI] ❌ 请求超时")
            return None
        except Exception as e:
            print(f"[智谱AI] ❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
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
        # 生成提示词
        prompt = self.generate_kite_prompt(design_data)
        
        # 生成图像
        return self.generate_image(prompt, size=size)


# 测试函数
def test_generator():
    """测试智谱 AI 图像生成"""
    api_key = "b91a0c07fd0640f488491d6bd0fa4e7f.z5j8U7iiyrWkO5sc"
    
    generator = ZhipuImageGenerator(api_key)
    
    # 测试设计数据
    test_design = {
        'materials': {
            '骨架材料': ['竹子'],
            '风筝面料': ['丝绸'],
            '绳索材料': ['麻绳']
        }
    }
    
    # 生成图像
    result = generator.generate_kite_image(test_design)
    
    if result:
        print("\n✅ 测试成功！")
        print(f"图像URL: {result['url']}")
    else:
        print("\n❌ 测试失败")


if __name__ == "__main__":
    test_generator()