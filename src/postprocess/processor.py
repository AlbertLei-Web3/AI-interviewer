import asyncio
import time  # 添加用于性能监控
from .spell_check import SpellChecker
from .grammar_check import GrammarChecker
from .semantic_check import SemanticChecker
from .industry_terms import IndustryTermChecker

class TextProcessor:
    def __init__(self, industry="web3"):
        self.spell_checker = SpellChecker()
        self.grammar_checker = GrammarChecker()
        self.semantic_checker = SemanticChecker()
        self.industry_checker = IndustryTermChecker(industry)
        self.total_timeout = 2.9  # 总超时时间
        
        # [性能监控] 添加性能统计变量
        self.performance_stats = {
            "拼写检查": [],
            "术语检查": [],
            "语法检查": [],
            "语义分析": [],
            "总处理时间": []
        }
    
    async def process(self, text: str) -> str:
        """
        分组处理文本，保持必要的依赖顺序
        """
        if text is None or text == "":
            return text
        
        # [性能监控] 记录总处理开始时间
        total_start_time = time.time()
        processed_text = text
        start_time = asyncio.get_event_loop().time()
        
        try:
            # [性能监控] 记录总处理时间 - 移到 try 块的开始
            self.performance_stats["总处理时间"].append(0.0)  # 初始化，确保键存在
            current_index = len(self.performance_stats["总处理时间"]) - 1
            
            # [性能监控] 第一组开始时间
            group1_start = time.time()
            
            # 第一组：并行执行基础文本修正（拼写检查和行业术语）
            basic_tasks = [
                asyncio.create_task(self.spell_checker.check(text), name="拼写检查"),
                asyncio.create_task(self.industry_checker.check(text), name="术语检查")
            ]
            
            done, pending = await asyncio.wait(
                basic_tasks,
                timeout=1.0,  # 为基础处理分配1秒
                return_when=asyncio.ALL_COMPLETED
            )
            
            # [性能监控] 记录第一组完成时间
            group1_time = time.time() - group1_start
            print(f"第一组处理耗时: {group1_time:.3f}秒")
            
            # 合并基础处理结果
            spell_result = None
            term_result = None
            
            for task in done:
                try:
                    result = await task
                    task_name = task.get_name()
                    # [性能监控] 记录各任务耗时
                    task_time = time.time() - group1_start
                    self.performance_stats[task_name].append(task_time)
                    print(f"{task_name}耗时: {task_time:.3f}秒")
                    
                    if task_name == "拼写检查":
                        spell_result = result
                    elif task_name == "术语检查":
                        term_result = result
                except Exception as e:
                    print(f"{task.get_name()}出错: {str(e)}")

            # 智能合并拼写和术语检查结果
            if spell_result and term_result:
                words = spell_result.split()
                term_words = term_result.split()
                for i, word in enumerate(words):
                    # 如果是行业术语，使用术语检查的结果
                    if i < len(term_words) and term_words[i].lower() in self.industry_checker.terms:
                        words[i] = term_words[i]
                processed_text = " ".join(words)
            elif spell_result:
                processed_text = spell_result
            elif term_result:
                processed_text = term_result

            # 检查剩余时间
            remaining_time = self.total_timeout - (asyncio.get_event_loop().time() - start_time)
            if remaining_time <= 0:
                print("时间已到，跳过后续处理")
                return processed_text

            # [性能监控] 第二组开始时间
            group2_start = time.time()
            
            # 第二组：语法检查
            try:
                processed_text = await asyncio.wait_for(
                    self.grammar_checker.check(processed_text),
                    timeout=min(1.0, remaining_time)
                )
                # [性能监控] 记录语法检查耗时
                grammar_time = time.time() - group2_start
                self.performance_stats["语法检查"].append(grammar_time)
                print(f"语法检查耗时: {grammar_time:.3f}秒")
            except asyncio.TimeoutError:
                print("语法检查超时")
                return processed_text

            # 再次检查剩余时间
            remaining_time = self.total_timeout - (asyncio.get_event_loop().time() - start_time)
            if remaining_time <= 0:
                print("时间已到，跳过语义分析")
                return processed_text

            # [性能监控] 第三组开始时间
            group3_start = time.time()
            
            # 第三组：语义分析（基于所有前面的处理结果）
            try:
                processed_text = await asyncio.wait_for(
                    self.semantic_checker.check(processed_text),
                    timeout=remaining_time
                )
                # [性能监控] 记录语义分析耗时
                semantic_time = time.time() - group3_start
                self.performance_stats["语义分析"].append(semantic_time)
                print(f"语义分析耗时: {semantic_time:.3f}秒")
            except asyncio.TimeoutError:
                print("语义分析超时")
            
            # [性能监控]更新总处理时间
            total_time = time.time() - total_start_time
            self.performance_stats["总处理时间"][current_index] = total_time
            print(f"总处理耗时: {total_time:.3f}秒")
            
            return processed_text

        except Exception as e:
            print(f"后处理出错: {str(e)}")
            # 确保即使出错也记录处理时间
            total_time = time.time() - total_start_time
            if len(self.performance_stats["总处理时间"]) > 0:
                self.performance_stats["总处理时间"][-1] = total_time
            else:
                self.performance_stats["总处理时间"].append(total_time)
            return processed_text
            
    # [性能监控] 添加性能统计方法
    def get_performance_stats(self):
        """获取性能统计信息"""
        stats = {}
        for name, times in self.performance_stats.items():
            if times:
                avg_time = sum(times) / len(times)
                stats[name] = {
                    "平均耗时": avg_time,  # 保持数值类型
                    "最短耗时": min(times),
                    "最长耗时": max(times),
                    "处理次数": len(times),
                    "总耗时": sum(times)
                }
        return stats

    # 添加一个打印性能统计的方法
    def print_performance_stats(self):
        """打印性能统计信息"""
        stats = self.get_performance_stats()
        print("\n=== 性能统计 ===")
        for name, metrics in stats.items():
            print(f"\n{name}:")
            for metric, value in metrics.items():
                # 格式化输出时再转换为字符串
                if metric in ["平均耗时", "最短耗时", "最长耗时", "总耗时"]:
                    print(f"  {metric}: {value:.3f}秒")
                else:
                    print(f"  {metric}: {value}") 