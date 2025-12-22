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
        self.api_key = api_key.strip()  # 自动清理空格
        self.headers = {
            "Content-Type": "application/json",
            "X-Master-Key": self.api_key
        }
    
    @staticmethod
    def _clean_bin_id(bin_id: str) -> str:
        """
        清理 Bin ID（去除空格和特殊字符）
        
        Args:
            bin_id: 原始 Bin ID
            
        Returns:
            清理后的 Bin ID
        """
        return bin_id.strip()
    
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
        
        # 验证数据是字典
        if not isinstance(data, dict):
            raise Exception(f"数据必须是字典格式，当前类型: {type(data)}")
        
        # 尝试序列化验证
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
        print(f"[DEBUG] Headers: {headers}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"[DEBUG] 响应状态: {response.status_code}")
        
        if response.status_code in [200, 201]:  # 接受 200 或 201
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
        # 清理 Bin ID
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/bins/{clean_bin_id}"
        
        print(f"[DEBUG] 原始 Bin ID: '{bin_id}'")
        print(f"[DEBUG] 清理后 Bin ID: '{clean_bin_id}'")
        print(f"[DEBUG] 更新 URL: {url}")
        
        # 验证数据是字典
        if not isinstance(data, dict):
            raise Exception(f"数据必须是字典格式，当前类型: {type(data)}")
        
        # 尝试序列化验证
        try:
            import json as json_lib
            json_lib.dumps(data)
        except TypeError as e:
            raise Exception(f"数据包含不可序列化的对象: {str(e)}")
        
        response = requests.put(url, json=data, headers=self.headers)
        
        print(f"[DEBUG] 响应状态: {response.status_code}")
        print(f"[DEBUG] 响应内容: {response.text[:200]}")
        
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
        """
        读取 Bin 数据
        
        Args:
            bin_id: Bin ID
            
        Returns:
            Bin 数据
            
        Raises:
            Exception: 读取失败时抛出异常
        """
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/bins/{clean_bin_id}/latest"
        
        print(f"[DEBUG] 读取 URL: {url}")
        
        response = requests.get(url, headers=self.headers)
        
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
        """
        删除 Bin
        
        Args:
            bin_id: Bin ID
            
        Returns:
            是否删除成功
        """
        clean_bin_id = self._clean_bin_id(bin_id)
        url = f"{self.BASE_URL}/bins/{clean_bin_id}"
        
        print(f"[DEBUG] 删除 URL: {url}")
        
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 200
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        验证 API Key 格式是否有效（简单验证）
        
        Args:
            api_key: 要验证的 API Key
            
        Returns:
            是否有效
        """
        if not api_key:
            return False
        
        # 清理空格
        api_key = api_key.strip()
        
        # JSONBin API Key 通常是 32 位字符串
        if len(api_key) < 20:
            return False
        
        # 只验证格式，实际有效性在上传时验证
        return True