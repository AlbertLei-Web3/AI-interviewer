import asyncio
import spacy

class SemanticChecker:
    def __init__(self, timeout=0.5):
        """
        初始化语义检查器
        Args:
            timeout (float): 检查超时时间，默认0.5秒
        """
        self.timeout = timeout
        # 加载英语语言模型
        self.nlp = spacy.load("en_core_web_sm")
    
    async def check(self, text: str, timeout: float = 0.5) -> str:
        """
        异步执行语义分析
        timeout: 超时时间（秒）
        """
        try:
            return await asyncio.wait_for(
                self._check(text),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("语义分析超时，跳过")
            return text
    
    async def _check(self, text: str) -> str:
        doc = self.nlp(text)
        
        # 提取主要实体和关键词
        entities = [ent.text for ent in doc.ents]
        
        # 如果找到实体，确保它们的大小写正确
        for entity in entities:
            if entity.lower() in text.lower():
                text = text.replace(entity.lower(), entity)
        
        return text 