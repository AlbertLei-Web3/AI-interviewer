import asyncio
import language_tool_python
from functools import lru_cache

class GrammarChecker:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式，确保只初始化一次"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, timeout=1.0):
        """初始化语法检查器"""
        if not self._initialized:
            self.timeout = timeout
            try:
                # 使用 2.7.1 版本的初始化方式
                self.tool = language_tool_python.LanguageTool('en-US', remote_server='https://languagetool.org/api/')
                print("语法检查器初始化成功（本地模式）")
                self._initialized = True
                # 初始化缓存
                self._check_cache = {}
                self.max_cache_size = 500
            except Exception as e:
                print(f"语法检查器初始化失败: {str(e)}")
                self.tool = None
    
    @lru_cache(maxsize=1000)
    async def _check_cached(self, text: str) -> str:
        """缓存检查结果"""
        if not self.tool:
            return text
        try:
            matches = self.tool.check(text)
            return self.tool.correct(text)
        except Exception as e:
            print(f"语法检查处理出错: {str(e)}")
            return text
    
    async def check(self, text: str, timeout: float = 1.0) -> str:
        """
        异步执行语法检查
        timeout: 超时时间（秒）
        """
        try:
            return await asyncio.wait_for(
                self._check_cached(text),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("语法检查超时，跳过")
            return text
        except Exception as e:
            print(f"语法检查出错: {str(e)}")
            return text 