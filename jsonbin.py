"""
JSONBin 服务模块 - 支持代理
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
        self.api_key = api_key.strip()
        self.headers = {
            "Content-Type": "application/json",
            "X-Master-Key": self.api_key
        }
        
        # 创建 session（不使用代理）
        self._session = requests.Session()
        self._session.trust_env = False  # 忽略系统代理
        self._session.proxies = {}  # 清空代理设置
    
    @staticmethod
    def _clean_bin_id(bin_id: str) -> str:
        """清理 Bin ID"""
        return bin_id.strip()
    
    def create_bin(self, data: Dict[str, Any], bin_name: Optional[str] = None) -> Dict[str, Any]:
        """创建新的 Bin"""
        url = f"{self.BASE_URL}/b"
        
        if not isinstance(data, dict):
            raise Exception(f"数据必须是字典格式，当前类型: {type(data)}")
        
        try:
            import json as json_lib
            json_lib.dumps(data)
        except TypeError as e:
            raise Exception(f"数据包含不可序列化的对象: {str(e)}")
        
        headers = self.headers.copy()
        if bin_name:
            headers["X-Bin-Name"] = bin_name
        else:
            headers["X-Bin-Name"] = f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"[DEBUG] 创建 Bin - URL: {url}")
        
        response = self._session.post(url, json=data, headers=headers)
        
        print(f"[DEBUG] 响应状态: {response.status_code}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get('message', error_msg)
            except:
                pass
            raise Exception(f"创建失败 ({response.status_code}): {error_msg}")
    
    def update_bin(self, bin_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新已有的 Bin"""
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/b/{clean_bin_id}"
        
        print(f"[DEBUG] 更新 URL: {url}")
        
        if not isinstance(data, dict):
            raise Exception(f"数据必须是字典格式，当前类型: {type(data)}")
        
        try:
            import json as json_lib
            json_lib.dumps(data)
        except TypeError as e:
            raise Exception(f"数据包含不可序列化的对象: {str(e)}")
        
        response = self._session.put(url, json=data, headers=self.headers)
        
        print(f"[DEBUG] 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get('message', error_msg)
            except:
                pass
            raise Exception(f"更新失败 ({response.status_code}): {error_msg}")
    
    def read_bin(self, bin_id: str) -> Dict[str, Any]:
        """读取 Bin 数据"""
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/b/{clean_bin_id}/latest"
        
        print(f"[DEBUG] 读取 URL: {url}")
        
        response = self._session.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get('message', error_msg)
            except:
                pass
            raise Exception(f"读取失败 ({response.status_code}): {error_msg}")
    
    def delete_bin(self, bin_id: str) -> bool:
        """删除 Bin"""
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/b/{clean_bin_id}"
        
        print(f"[DEBUG] 删除 URL: {url}")
        
        response = self._session.delete(url, headers=self.headers)
        return response.status_code == 200
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证 API Key 格式"""
        if not api_key:
            return False
        
        api_key = api_key.strip()
        
        if len(api_key) < 20:
            return False
        
        return True