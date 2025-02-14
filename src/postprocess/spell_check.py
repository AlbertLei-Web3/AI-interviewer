from spellchecker import SpellChecker as PySpellChecker
import asyncio

class SpellChecker:
    def __init__(self, timeout=0.5):
        """
        初始化拼写检查器
        Args:
            timeout (float): 检查超时时间，默认0.5秒
        """
        self.timeout = timeout
        self.spell = PySpellChecker()
    
    async def check(self, text: str, timeout: float = 0.5) -> str:
        """
        异步执行拼写检查
        timeout: 超时时间（秒）
        """
        try:
            return await asyncio.wait_for(
                self._check(text),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("拼写检查超时，跳过")
            return text
    
    async def _check(self, text: str) -> str:
        words = text.split()
        corrected_words = []
        
        for word in words:
            if not self.spell.known([word]):
                correction = self.spell.correction(word)
                corrected_words.append(correction if correction else word)
            else:
                corrected_words.append(word)
        
        return " ".join(corrected_words) 