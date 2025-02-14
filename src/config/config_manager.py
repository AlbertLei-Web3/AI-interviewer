import os
from typing import Dict, Any
from dotenv import load_dotenv
import json

class ConfigManager:
    _instance = None  # 存储单例实例

    def __new__(cls):
        """单例模式：确保只有一个ConfigManager实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # 创建新实例
        return cls._instance

    def __init__(self):
        """初始化配置管理器"""
        if not hasattr(self, 'initialized'):  # 确保初始化只执行一次
            # 加载.env文件中的环境变量配置
            load_dotenv()

            # 配置字典，保存项目的基础设置和环境变量
            self.config = {
                # API设置（OpenAI API 密钥）
                "openai_api_key": os.getenv('OPENAI_API_KEY'),
                
                # Whisper设置（音频转文字模型路径和模型类型）
                "whisper_model_path": os.getenv('WHISPER_MODEL_PATH'),
                "whisper_model_type": os.getenv('WHISPER_MODEL_TYPE', 'medium'),  # 默认'medium'类型
                
                # 音频设置（音频分片大小、音频通道数、采样率）
                "audio_chunk_size": int(os.getenv('AUDIO_CHUNK_SIZE', 4096)),
                "audio_channels": int(os.getenv('AUDIO_CHANNELS', 1)),
                "audio_rate": int(os.getenv('AUDIO_RATE', 48000)),
                
                # 后处理设置（包括超时、缓存大小、批次大小、各个步骤的超时）
                "processing": {
                    "total_timeout": 2.9,  # 总处理超时，单位秒
                    "cache_size": 1000,    # 缓存大小
                    "batch_size": 5,       # 批处理大小
                    "timeouts": {
                        "spell_check": 5,   # 拼写检查超时
                        "grammar_check": 5, # 语法检查超时
                        "semantic_check": 5,# 语义检查超时
                        "industry_check": 5 # 行业术语检查超时
                    }
                },

                # 面试设置（面试上下文和行业类型）
                "interview_context": os.getenv('INTERVIEW_CONTEXT'),
                "industry": "web3"  # 默认行业设置为'web3'
            }

            # 尝试加载本地的配置文件（例如config.json）
            self._load_local_config()

            # 设置初始化标志，防止重复初始化
            self.initialized = True

    def _load_local_config(self):
        """加载本地配置文件（config.json）并合并到当前配置"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                local_config = json.load(f)
                # 处理环境变量替换
                self._process_env_vars(local_config)
                self._update_dict(self.config, local_config)
        except FileNotFoundError:
            pass  # 如果没有找到文件，则忽略

    def _update_dict(self, d1: Dict, d2: Dict):
        """递归地将d2的内容更新到d1字典中"""
        for k, v in d2.items():
            if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                # 如果d1中的值是字典且d2中的值也是字典，递归合并
                self._update_dict(d1[k], v)
            else:
                d1[k] = v  # 否则直接更新

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，通过'点'分隔的键来访问嵌套字典中的值"""
        keys = key.split('.')  # 将key分割为列表
        value = self.config  # 从配置字典开始查找
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)  # 逐级查找
            else:
                return default  # 如果找不到，返回默认值
        return value if value is not None else default  # 返回查找到的值，若没有则返回默认值

    def set(self, key: str, value: Any):
        """设置配置值，通过'点'分隔的键来更新嵌套字典中的值"""
        keys = key.split('.')  # 将key分割为列表
        config = self.config  # 从配置字典开始
        for k in keys[:-1]:  # 遍历key，直到倒数第二个
            if k not in config:
                config[k] = {}  # 如果没有这个键，则创建一个字典
            config = config[k]  # 进入下一级字典
        config[keys[-1]] = value  # 更新最后一级键的值

    def _process_env_vars(self, config: Dict):
        """处理配置中的环境变量引用"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._process_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_key = value[2:-1]
                default = None
                if ":" in env_key:
                    env_key, default = env_key.split(":", 1)
                config[key] = os.getenv(env_key, default)
