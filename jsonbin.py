"""
JSONBin 服务模块
负责所有与 JSONBin API 的交互
"""

import requests
from typing import Dict, Optional, Any
from datetime import datetime


class JSONBinService:
    """JSONBin API 服务类"""
    
    BASE_URL = "https://api.jsonbin.io/v3"
    
    def __init__(self, api_key: str):
        """
        初始化 JSONBin 服务
        
        Args:
            api_key: JSONBin API Key
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-Master-Key": api_key
        }
    
    def create_bin(self, data: Dict[str, Any], bin_name: Optional[str] = None) -> Dict[str, Any]:
        """
        创建新的 Bin
        
        Args:
            data: 要存储的数据
            bin_name: Bin 名称（可选）
            
        Returns:
            API 响应数据
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        url = f"{self.BASE_URL}/b"
        
        headers = self.headers.copy()
        if bin_name:
            headers["X-Bin-Name"] = bin_name
        else:
            headers["X-Bin-Name"] = f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 修改点：直接发送 data，不要包装
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"创建失败: {response.status_code} - {response.text}")
    
    def update_bin(self, bin_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新已有的 Bin
        
        Args:
            bin_id: Bin ID
            data: 要更新的数据
            
        Returns:
            API 响应数据
            
        Raises:
            Exception: 更新失败时抛出异常
        """
        url = f"{self.BASE_URL}/b/{bin_id}"
        
        # 修改点：直接发送 data，不要包装
        response = requests.put(url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"更新失败: {response.status_code} - {response.text}")
    
    def delete_bin(self, bin_id: str) -> bool:
        """
        删除 Bin
        
        Args:
            bin_id: Bin ID
            
        Returns:
            是否删除成功
        """
        url = f"{self.BASE_URL}/b/{bin_id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 200
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        验证 API Key 是否有效
        
        Args:
            api_key: 要验证的 API Key
            
        Returns:
            是否有效
        """
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return False
        
        try:
            headers = {"X-Master-Key": api_key}
            response = requests.get(f"{JSONBinService.BASE_URL}/b", headers=headers)
            return response.status_code in [200, 401]  # 401 说明 key 格式正确但可能无权限
        except:
            return False