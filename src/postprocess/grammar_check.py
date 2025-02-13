import asyncio
import language_tool_python

class GrammarChecker:
    def __init__(self):
        # 使用本地服务器
        try:
            self.tool = language_tool_python.LanguageTool('en-US', remote_server=None)
            print("语法检查器初始化成功（本地模式）")
        except Exception as e:
            print(f"语法检查器初始化失败: {str(e)}")
            self.tool = None
    
    async def check(self, text: str, timeout: float = 1.0) -> str:
        """
        异步执行语法检查
        timeout: 超时时间（秒）
        """
        if not self.tool:
            return text
            
        try:
            return await asyncio.wait_for(
                self._check(text),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("语法检查超时，跳过")
            return text
        except Exception as e:
            print(f"语法检查出错: {str(e)}")
            return text
    
    async def _check(self, text: str) -> str:
        try:
            matches = self.tool.check(text)
            return self.tool.correct(text)
        except Exception as e:
            print(f"语法检查处理出错: {str(e)}")
            return text 