import pytest
from src.config.config_manager import ConfigManager
import os

def test_config_singleton():
    """测试配置管理器单例模式"""
    config1 = ConfigManager()
    config2 = ConfigManager()
    assert config1 is config2

def test_config_values():
    """测试配置值获取和更新"""
    config = ConfigManager()
    
    # 1. 获取初始值
    initial_value = config.get('processing.total_timeout')
    assert isinstance(initial_value, (int, float)), "超时值应该是数字"
    
    # 2. 测试更新值
    new_value = 3.5
    config.set('processing.total_timeout', new_value)
    assert config.get('processing.total_timeout') == new_value
    
    # 3. 恢复原值
    config.set('processing.total_timeout', initial_value)

def test_config_update():
    """测试配置更新"""
    config = ConfigManager()
    config.set('processing.total_timeout', 3.0)
    assert config.get('processing.total_timeout') == 3.0 

def test_env_var_processing():
    """测试环境变量处理"""
    os.environ['TEST_KEY'] = 'test_value'
    config = ConfigManager()
    
    # 测试基本环境变量
    assert config.get('api.openai_api_key') == os.getenv('OPENAI_API_KEY')
    
    # 测试带默认值的环境变量
    assert config.get('audio.chunk_size') == '4096'  # 默认值

def test_config_default_values():
    """测试默认配置值"""
    config = ConfigManager()
    
    # 测试必须存在的配置项
    assert config.get('processing.timeouts.spell_check') == 5
    assert config.get('processing.timeouts.grammar_check') == 5
    assert config.get('industry') == 'web3'
    
    # 测试带默认值的环境变量配置
    assert config.get('audio.chunk_size') in ['4096', 4096]  # 可能是字符串或整数
    assert config.get('audio.channels') in ['1', 1]

def test_config_override():
    """测试配置覆盖机制"""
    config = ConfigManager()
    
    # 1. 保存原始值
    original_timeout = config.get('processing.total_timeout')
    
    try:
        # 2. 测试配置更新
        test_value = 5.0
        config.set('processing.total_timeout', test_value)
        assert config.get('processing.total_timeout') == test_value
        
        # 3. 测试嵌套配置更新
        config.set('processing.timeouts.spell_check', 10)
        assert config.get('processing.timeouts.spell_check') == 10
        
    finally:
        # 4. 恢复原始值
        config.set('processing.total_timeout', original_timeout) 