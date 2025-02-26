import datetime
import json
import os
import time
from typing import Dict, List

class PerformanceMonitor:
    _instance = None  # 单例模式
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.performance_log = []
            self.session_start_time = datetime.datetime.now()
            self.initialized = True
    
    def start_tracking(self) -> float:
        """开始追踪性能"""
        return time.time()
    
    def record_performance(self, start_time: float, operation: str, metadata: Dict = None):
        """记录性能数据"""
        end_time = time.time()
        duration = end_time - start_time
        
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operation': operation,
            'duration': duration
        }
        
        if metadata:
            log_entry.update(metadata)
            
        self.performance_log.append(log_entry)
        
        # 每10条记录自动保存
        if len(self.performance_log) >= 10:
            self.save_logs()
    
    def save_logs(self):
        """保存性能日志"""
        try:
            if not self.performance_log:
                return
                
            log_dir = os.path.join("logs", "performance")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(
                log_dir, 
                f"performance_log_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_log, f, indent=2)
            
            self.performance_log = []
            print(f"\n性能日志已保存到: {log_file}")
        except Exception as e:
            print(f"\n保存性能日志失败: {str(e)}") 