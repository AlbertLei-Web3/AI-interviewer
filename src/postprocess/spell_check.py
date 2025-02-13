from spellchecker import SpellChecker as PySpellChecker
import asyncio

class SpellChecker:
    def __init__(self):
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