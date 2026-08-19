from pathlib import Path
from faster_whisper import WhisperModel
import html
import json


AUDIO = Path("AIAgentsFundamentals3.mp3")
TRANSCRIPCION = Path("AIAgentsFundamentals_transcripcion3"
".txt")
SALIDA = Path("index.html")


def formatear_tiempo(segundos: float) -> str:
    segundos = int(segundos)
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    if horas:
        return f"{horas:02}:{minutos:02}:{segundos:02}"

    return f"{minutos:02}:{segundos:02}"


if not AUDIO.exists():
    raise FileNotFoundError(f"No se encontró {AUDIO}")

if not TRANSCRIPCION.exists():
    raise FileNotFoundError(f"No se encontró {TRANSCRIPCION}")


# El texto se conserva como referencia.
texto_original = TRANSCRIPCION.read_text(encoding="utf-8").strip()


# Para GPU NVIDIA.
model = WhisperModel(
    "medium",
    device="cuda",
    compute_type="float16"
)

segments, info = model.transcribe(
    str(AUDIO),
    language="en",
    beam_size=5,
    vad_filter=True,
    word_timestamps=True
)


segmentos = []

for numero, segmento in enumerate(segments, start=1):
    texto = segmento.text.strip()

    if not texto:
        continue

    segmentos.append(
        {
            "id": numero,
            "inicio": round(segmento.start, 2),
            "fin": round(segmento.end, 2),
            "marca": formatear_tiempo(segmento.start),
            "texto": texto
        }
    )


segmentos_json = json.dumps(
    segmentos,
    ensure_ascii=False
).replace("</", "<\\/")


pagina = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AI Agents Fundamentals</title>

    <style>
        :root {{
            --fondo: #f4f5f7;
            --tarjeta: #ffffff;
            --texto: #202124;
            --secundario: #667085;
            --principal: #405cf5;
            --principal-suave: #eef1ff;
            --borde: #e4e7ec;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: var(--fondo);
            color: var(--texto);
            font-family: Arial, Helvetica, sans-serif;
        }}

        .contenedor {{
            width: min(950px, calc(100% - 32px));
            margin: 0 auto;
            padding: 38px 0 80px;
        }}

        header {{
            margin-bottom: 24px;
        }}

        h1 {{
            margin: 0 0 10px;
            font-size: clamp(28px, 5vw, 42px);
        }}

        .descripcion {{
            margin: 0;
            color: var(--secundario);
            line-height: 1.5;
        }}

        .reproductor {{
            position: sticky;
            top: 10px;
            z-index: 20;
            padding: 18px;
            margin-bottom: 24px;
            border: 1px solid var(--borde);
            border-radius: 16px;
            background: var(--tarjeta);
            box-shadow: 0 8px 25px rgba(16, 24, 40, 0.1);
        }}

        audio {{
            width: 100%;
        }}

        .estado {{
            margin-top: 10px;
            color: var(--secundario);
            font-size: 14px;
        }}

        .transcripcion {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .segmento {{
            display: grid;
            grid-template-columns: 75px 1fr;
            gap: 16px;
            padding: 17px;
            border: 1px solid var(--borde);
            border-radius: 12px;
            background: var(--tarjeta);
            cursor: pointer;
            transition:
                border-color 0.2s,
                background-color 0.2s,
                transform 0.2s;
        }}

        .segmento:hover {{
            border-color: var(--principal);
            transform: translateY(-1px);
        }}

        .segmento.activo {{
            border-color: var(--principal);
            background: var(--principal-suave);
        }}

        .tiempo {{
            color: var(--principal);
            font-family: Consolas, monospace;
            font-weight: bold;
        }}

        .texto {{
            margin: 0;
            font-size: 17px;
            line-height: 1.65;
        }}

        @media (max-width: 600px) {{
            .contenedor {{
                width: min(100% - 20px, 950px);
                padding-top: 20px;
            }}

            .segmento {{
                grid-template-columns: 1fr;
                gap: 8px;
            }}

            .texto {{
                font-size: 16px;
            }}
        }}
    </style>
</head>

<body>
    <main class="contenedor">
        <header>
            <h1>AI Agents Fundamentals</h1>

            <p class="descripcion">
                Seleccioná cualquier fragmento para reproducir el audio
                desde ese punto.
            </p>
        </header>

        <section class="reproductor">
            <audio
                id="audio"
                src="{html.escape(AUDIO.name)}"
                controls
                preload="metadata"
            ></audio>

            <div class="estado" id="estado">
                {len(segmentos)} fragmentos · idioma detectado:
                {html.escape(info.language)}
            </div>
        </section>

        <section
            id="transcripcion"
            class="transcripcion"
        ></section>
    </main>

    <script>
        const segmentos = {segmentos_json};

        const audio = document.getElementById("audio");
        const contenedor = document.getElementById("transcripcion");

        let indiceActivo = -1;

        function escaparHtml(texto) {{
            const elemento = document.createElement("div");
            elemento.textContent = texto;
            return elemento.innerHTML;
        }}

        function mostrarTranscripcion() {{
            segmentos.forEach((segmento, indice) => {{
                const articulo = document.createElement("article");

                articulo.className = "segmento";
                articulo.dataset.indice = indice;

                articulo.innerHTML = `
                    <span class="tiempo">
                        ${{segmento.marca}}
                    </span>

                    <p class="texto">
                        ${{escaparHtml(segmento.texto)}}
                    </p>
                `;

                articulo.addEventListener("click", () => {{
                    audio.currentTime = segmento.inicio;
                    audio.play();
                }});

                contenedor.appendChild(articulo);
            }});
        }}

        function actualizarFragmento() {{
            const tiempo = audio.currentTime;

            const nuevoIndice = segmentos.findIndex((segmento) => {{
                return (
                    tiempo >= segmento.inicio &&
                    tiempo < segmento.fin
                );
            }});

            if (
                nuevoIndice === -1 ||
                nuevoIndice === indiceActivo
            ) {{
                return;
            }}

            const anterior = document.querySelector(
                ".segmento.activo"
            );

            if (anterior) {{
                anterior.classList.remove("activo");
            }}

            const actual = document.querySelector(
                `.segmento[data-indice="${{nuevoIndice}}"]`
            );

            if (actual) {{
                actual.classList.add("activo");

                actual.scrollIntoView({{
                    behavior: "smooth",
                    block: "center"
                }});
            }}

            indiceActivo = nuevoIndice;
        }}

        mostrarTranscripcion();

        audio.addEventListener(
            "timeupdate",
            actualizarFragmento
        );
    </script>
</body>
</html>
"""


SALIDA.write_text(pagina, encoding="utf-8")

print(f"Idioma detectado: {info.language}")
print(f"Fragmentos creados: {len(segmentos)}")
print(f"Web generada: {SALIDA.resolve()}")