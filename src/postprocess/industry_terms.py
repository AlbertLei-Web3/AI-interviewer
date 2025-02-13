from src.config.industry_terms import WEB3_TERMS
import asyncio
from difflib import get_close_matches

class IndustryTermChecker:
    def __init__(self, industry="web3"):
        self.terms = WEB3_TERMS if industry == "web3" else {}
    
    async def check(self, text: str, timeout: float = 0.5) -> str:
        """
        异步执行行业术语检查
        timeout: 超时时间（秒）
        """
        try:
            return await asyncio.wait_for(
                self._check(text),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("行业术语检查超时，跳过")
            return text
    
    async def _check(self, text: str) -> str:
        words = text.split()
        corrected_words = []
        
        for word in words:
            # 检查是否是行业术语的错误写法
            for correct_term, wrong_terms in self.terms.items():
                if word.lower() in wrong_terms:
                    word = correct_term
                    break
            corrected_words.append(word)
        
        return " ".join(corrected_words) 