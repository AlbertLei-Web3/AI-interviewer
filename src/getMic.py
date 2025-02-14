import pyaudio
import wave
import time
import keyboard
import threading
import os

def get_mic(device_index=None):
    """
    获取麦克风设备
    
    Args:
        device_index: 可选的设备索引，如果不指定则使用默认设备
    
    Returns:
        pyaudio.PyAudio: 音频设备对象
        int: 设备索引
    """
    p = pyaudio.PyAudio()
    
    if device_index is None:
        # 使用默认输入设备
        device_index = p.get_default_input_device_info()['index']
    
    device_info = p.get_device_info_by_index(device_index)
    if device_info['maxInputChannels'] == 0:
        raise ValueError(f"设备 {device_index} 不支持录音")
    
    return p, device_index

def list_audio_devices():
    """列出所有音频设备"""
    p = pyaudio.PyAudio()
    
    # 获取设备数量
    device_count = p.get_device_count()
    print(f"\n找到 {device_count} 个音频设备:")
    
    # 遍历并打印每个设备的信息
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        print(f"\n设备 {i}:")
        print(f"  名称: {device_info['name']}")
        print(f"  最大输入通道: {device_info['maxInputChannels']}")
        print(f"  最大输出通道: {device_info['maxOutputChannels']}")
        print(f"  默认采样率: {device_info['defaultSampleRate']}")
        
        # 如果是输入设备，标记为可用于录音
        if device_info['maxInputChannels'] > 0:
            print("  ✓ 可用于录音")
    
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()