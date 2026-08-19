from pathlib import Path
from faster_whisper import WhisperModel

ARCHIVO_AUDIO = Path("AIAgentsFundamentals3.mp3")
ARCHIVO_SALIDA = Path("AIAgentsFundamentals_transcripcion2.txt")

if not ARCHIVO_AUDIO.exists():
    raise FileNotFoundError(f"No se encontró el archivo: {ARCHIVO_AUDIO.resolve()}")

# Para una GPU NVIDIA de 8 GB:
# - medium suele ofrecer buen equilibrio entre calidad y consumo.
# - float16 aprovecha la GPU.
model = WhisperModel(
    "medium",
    device="cuda",
    compute_type="float16"
)

segments, info = model.transcribe(
    str(ARCHIVO_AUDIO),
    language="en",       # El título sugiere que el audio está en inglés
    beam_size=5,
    vad_filter=True      # Reduce el procesamiento de silencios
)

print(f"Idioma detectado: {info.language}")
print(f"Probabilidad: {info.language_probability:.2%}")

with ARCHIVO_SALIDA.open("w", encoding="utf-8") as archivo:
    for segment in segments:
        texto = segment.text.strip()
        archivo.write(texto + "\n")
        print(f"[{segment.start:.2f}s → {segment.end:.2f}s] {texto}")

print(f"\nTranscripción guardada en: {ARCHIVO_SALIDA.resolve()}")