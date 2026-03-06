# src/agents/voice_agent.py
import io
from faster_whisper import WhisperModel

# Carrega o modelo UMA vez quando o arquivo é importado
# "small" = bom equilíbrio velocidade/precisão pra PT-BR
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

async def transcribe_voice(file_bytes: bytes) -> str:
    try:
        audio_buffer = io.BytesIO(file_bytes)
        segments, _ = whisper_model.transcribe(audio_buffer, language="pt")
        texto = " ".join(seg.text for seg in segments)
        print(f"[VOZ TRANSCRITA]: {texto}")
        return texto
    except Exception as e:
        print(f"Erro de transcrição: {e}")
        return None

