"""
Edge TTS Service - 使用 Microsoft Edge TTS 生成自然语音
参考 ASR-LLM-TTS-master 项目实现
"""
import edge_tts
import asyncio
import os
import uuid
import tempfile
from typing import Optional
from app.core.logger import logger

# 语音配置 - 中文女声
DEFAULT_VOICE = "zh-CN-XiaoyiNeural"  # 小艺 - 年轻女声，适合面试官角色
ALTERNATIVE_VOICES = {
    "female_young": "zh-CN-XiaoyiNeural",
    "female_mature": "zh-CN-XiaoxiaoNeural",
    "male_young": "zh-CN-YunxiNeural",
    "male_mature": "zh-CN-YunjianNeural",
}

class EdgeTTSService:
    def __init__(self):
        self.output_dir = tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_audio_async(
        self, 
        text: str, 
        voice: str = DEFAULT_VOICE,
        rate: str = "+0%",  # 语速调整: +10%, -10% 等
        pitch: str = "+0Hz"  # 音调调整
    ) -> Optional[str]:
        """
        异步生成语音文件
        返回生成的音频文件路径
        """
        try:
            # 生成唯一文件名
            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            output_path = os.path.join(self.output_dir, filename)
            
            # 创建 Edge TTS 通信对象
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            
            logger.info(f"TTS audio generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Edge TTS error: {str(e)}")
            return None
    
    def generate_audio(
        self, 
        text: str, 
        voice: str = DEFAULT_VOICE,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Optional[str]:
        """
        同步生成语音文件（包装异步方法）
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.generate_audio_async(text, voice, rate, pitch)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Edge TTS sync error: {str(e)}")
            return None
    
    def cleanup_file(self, filepath: str):
        """清理临时音频文件"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.warning(f"Failed to cleanup TTS file: {str(e)}")

# 单例
edge_tts_service = EdgeTTSService()
