import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("\n=== 所有音频设备 ===")
    for i in range(p.get_device_count()):
        try:
            device_info = p.get_device_info_by_index(i)
            print(f"\n设备 {i}: {device_info['name']}")
            print(f"   输入通道数: {device_info['maxInputChannels']}")
            print(f"   输出通道数: {device_info['maxOutputChannels']}")
            print(f"   默认采样率: {device_info['defaultSampleRate']}")
            print(f"   设备索引: {device_info['index']}")
            print(f"   默认输入: {device_info.get('defaultLowInputLatency', 'N/A')}")
            print(f"   默认输出: {device_info.get('defaultLowOutputLatency', 'N/A')}")
            print("---")
        except Exception as e:
            print(f"设备 {i} 信息获取失败: {str(e)}")
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()