"""
JSONBin 云存储服务
负责与 JSONBin API 的所有交互
"""

import requests
from typing import Dict, Optional, Any, List
from datetime import datetime
import logging

from config import get_config

logger = logging.getLogger(__name__)


class JSONBinService:
    """JSONBin API 服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 JSONBin 服务
        
        Args:
            api_key: JSONBin API Key，为空则使用配置文件中的值
        """
        cfg = get_config()
        self.api_key = (api_key or cfg.api.JSONBIN_API_KEY).strip()
        self.base_url = cfg.api.JSONBIN_BASE_URL
        
        self.headers = {
            "Content-Type": "application/json",
            "X-Master-Key": self.api_key
        }
        
        # 创建 session（禁用系统代理）
        self._session = requests.Session()
        self._session.trust_env = False
        self._session.proxies = {}
    
    def _clean_bin_id(self, bin_id: str) -> str:
        """清理 Bin ID"""
        return bin_id.strip()
    
    def create_bin(
        self, 
        data: Dict[str, Any], 
        bin_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新的 Bin
        
        Args:
            data: 要存储的数据
            bin_name: Bin 名称
            
        Returns:
            创建结果
            
        Raises:
            ValueError: 数据格式错误
            ConnectionError: 网络请求失败
        """
        url = f"{self.base_url}/b"
        
        if not isinstance(data, dict):
            raise ValueError(f"数据必须是字典格式，当前类型: {type(data)}")
        
        headers = self.headers.copy()
        headers["X-Bin-Name"] = bin_name or f"kite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.debug(f"创建 Bin: {url}")
        
        try:
            response = self._session.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_msg = self._extract_error(response)
                raise ConnectionError(f"创建失败 ({response.status_code}): {error_msg}")
                
        except requests.RequestException as e:
            logger.error(f"创建 Bin 失败: {e}")
            raise ConnectionError(f"网络请求失败: {e}")
    
    def read_bin(self, bin_id: str) -> Dict[str, Any]:
        """
        读取 Bin 数据
        
        Args:
            bin_id: Bin ID
            
        Returns:
            Bin 中的数据
            
        Raises:
            ConnectionError: 读取失败
        """
        clean_id = self._clean_bin_id(bin_id)
        url = f"{self.base_url}/b/{clean_id}/latest"
        
        logger.debug(f"读取 Bin: {url}")
        
        try:
            response = self._session.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = self._extract_error(response)
                raise ConnectionError(f"读取失败 ({response.status_code}): {error_msg}")
                
        except requests.RequestException as e:
            logger.error(f"读取 Bin 失败: {e}")
            raise ConnectionError(f"网络请求失败: {e}")
    
    def update_bin(self, bin_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新 Bin 数据
        
        Args:
            bin_id: Bin ID
            data: 新数据
            
        Returns:
            更新结果
            
        Raises:
            ValueError: 数据格式错误
            ConnectionError: 更新失败
        """
        if not isinstance(data, dict):
            raise ValueError(f"数据必须是字典格式，当前类型: {type(data)}")
        
        clean_id = self._clean_bin_id(bin_id)
        url = f"{self.base_url}/b/{clean_id}"
        
        logger.debug(f"更新 Bin: {url}")
        
        try:
            response = self._session.put(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = self._extract_error(response)
                raise ConnectionError(f"更新失败 ({response.status_code}): {error_msg}")
                
        except requests.RequestException as e:
            logger.error(f"更新 Bin 失败: {e}")
            raise ConnectionError(f"网络请求失败: {e}")
    
    def delete_bin(self, bin_id: str) -> bool:
        """
        删除 Bin
        
        Args:
            bin_id: Bin ID
            
        Returns:
            是否删除成功
        """
        clean_id = self._clean_bin_id(bin_id)
        url = f"{self.base_url}/b/{clean_id}"
        
        logger.debug(f"删除 Bin: {url}")
        
        try:
            response = self._session.delete(url, headers=self.headers, timeout=30)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"删除 Bin 失败: {e}")
            return False
    
    def _extract_error(self, response: requests.Response) -> str:
        """从响应中提取错误信息"""
        try:
            error_json = response.json()
            return error_json.get('message', response.text)
        except:
            return response.text
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证 API Key 格式"""
        if not api_key:
            return False
        return len(api_key.strip()) >= 20


class DesignRepository:
    """设计数据仓库 - 封装设计数据的CRUD操作"""
    
    def __init__(self, jsonbin_service: Optional[JSONBinService] = None):
        self.jsonbin = jsonbin_service or JSONBinService()
        self._bin_id: Optional[str] = None
    
    @property
    def bin_id(self) -> Optional[str]:
        """获取当前 Bin ID"""
        if self._bin_id:
            return self._bin_id
        
        cfg = get_config()
        
        # 尝试从文件读取
        for filename in [cfg.system.BIN_ID_FILE, 'latest_bin.txt']:
            try:
                with open(filename, 'r') as f:
                    bin_id = f.read().strip()
                    if bin_id:
                        self._bin_id = bin_id
                        return self._bin_id
            except FileNotFoundError:
                continue
        
        return None
    
    @bin_id.setter
    def bin_id(self, value: str):
        """设置并保存 Bin ID"""
        self._bin_id = value
        cfg = get_config()
        
        try:
            with open(cfg.system.BIN_ID_FILE, 'w') as f:
                f.write(value)
        except Exception as e:
            logger.warning(f"保存 Bin ID 失败: {e}")
    
    def get_all_designs(self) -> List[Dict[str, Any]]:
        """获取所有设计"""
        if not self.bin_id:
            return []
        
        try:
            response = self.jsonbin.read_bin(self.bin_id)
            data = response.get('record', response)
            return data.get('designs', [])
        except Exception as e:
            logger.error(f"获取设计失败: {e}")
            return []
    
    def add_design(self, design: Dict[str, Any]) -> bool:
        """添加新设计"""
        try:
            existing = self.get_all_designs()
            existing.append(design)
            
            complete_data = {
                'designs': existing,
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'total_designs': len(existing),
                    'version': '2.0'
                }
            }
            
            if self.bin_id:
                self.jsonbin.update_bin(self.bin_id, complete_data)
            else:
                result = self.jsonbin.create_bin(complete_data, "kite_designs")
                self.bin_id = result['metadata']['id']
            
            return True
            
        except Exception as e:
            logger.error(f"添加设计失败: {e}")
            return False
    
    def clear_bin_id(self):
        """清除 Bin ID"""
        self._bin_id = None
        cfg = get_config()
        
        import os
        for filename in [cfg.system.BIN_ID_FILE, 'latest_bin.txt']:
            try:
                os.remove(filename)
            except:
                pass
