from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import json
import csv
import io
import base64
import pdfplumber

load_dotenv()

app = FastAPI(title="OdontoFHIR-AI Mapper API")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejemplo estructural reducido.
# La idea no es pegar todo el Bundle, sino darle al modelo una guía clara
# de cómo se ven los recursos y referencias dentro de OdontoFHIR.
FHIR_EXAMPLE = {
    "resourceType": "Bundle",
    "type": "document",
    "entry": [
        {
            "resource": {
                "resourceType": "Composition",
                "status": "final",
                "title": "Ficha Clínica Odontológica",
                "subject": {"reference": "Patient/paciente-1"},
                "author": [{"reference": "Practitioner/odontologo-1"}],
                "section": [
                    {
                        "title": "Consulta",
                        "entry": [
                            {"reference": "urn:uuid:obsproc-1"}
                        ]
                    }
                ]
            }
        },
        {
            "resource": {
                "resourceType": "Patient",
                "id": "paciente-1",
                "name": [{"given": ["Diego"], "family": "Gómez"}],
                "birthDate": "2003-09-01"
            }
        },
        {
            "resource": {
                "resourceType": "Practitioner",
                "id": "odontologo-1",
                "name": [{"given": ["Julia"], "family": "Ochoa"}]
            }
        },
        {
            "resource": {
                "resourceType": "Encounter",
                "id": "encuentro-1",
                "status": "finished",
                "subject": {"reference": "Patient/paciente-1"}
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "id": "obsproc-1",
                "status": "final",
                "subject": {"reference": "Patient/paciente-1"},
                "encounter": {"reference": "Encounter/encuentro-1"},
                "code": {
                    "coding": [
                        {
                            "system": "https://odontofhir.py/fhir/CodeSystem/Hallazgos-OdontoFHIR-1",
                            "code": "12005OF",
                            "display": "Caries dental"
                        }
                    ]
                }
            }
        }
    ]
}
FHIR_RESPONSE_SCHEMA = {
    "name": "odontofhir_response",
    "schema": {
        "type": "object",
        "additionalProperties": True
    }
}

def build_prompt(tipo: str, texto_documento: str) -> str:
    """
    Construye el prompt principal para documentos basados en texto.
    El modelo debe interpretar información libre y devolver JSON FHIR.
    """
    return f"""
Eres un experto en interoperabilidad clínica odontológica utilizando HL7 FHIR R4 y la guía de implementación OdontoFHIR.

Tu tarea es interpretar el contenido recibido (texto, imagen interpretada, PDF o CSV procesado) y transformarlo en recursos FHIR válidos conforme a los perfiles definidos por OdontoFHIR.

Tipo solicitado por la interfaz:
{tipo}

Reglas obligatorias:

- Devuelve SOLO JSON válido.
- No incluyas explicaciones.
- No uses markdown.
- Usa estructura compatible con HL7 FHIR R4.
- Si tipo = paciente, devuelve preferentemente un recurso Patient.
- Si tipo = alergia, devuelve preferentemente un recurso AllergyIntolerance.
- Si tipo = consulta, puedes devolver un Encounter o un Bundle document si la información clínica es amplia y contiene múltiples recursos relacionados.
- Si falta un dato, omite el campo en lugar de inventarlo.
- Mantén consistencia entre referencias como Patient, Practitioner y Encounter.
- Usa referencias relativas entre recursos cuando estén en el mismo Bundle.
- Prioriza siempre los perfiles definidos por OdontoFHIR antes que los recursos base de FHIR.

Reglas de perfiles OdontoFHIR:

Los recursos deben ajustarse a los siguientes perfiles:

Bundle → Expediente Odontológico
Composition → Ficha Clínica
Encounter → Consulta Odontológica
Condition → Hallazgos Odontológicos
Procedure → Procedimientos Odontológicos
Patient → Paciente Odontológico
Practitioner → Profesional Odontológico
AllergyIntolerance → Registro de Alergias

Cuando se utilicen estos recursos:

- Deben incluir el campo `meta.profile` apuntando al perfil correspondiente de OdontoFHIR.
- Las referencias entre recursos deben mantenerse consistentes (Patient, Practitioner, Encounter).
- Si el contenido describe una atención completa, devuelve un Bundle tipo `document`.

Reglas de interpretación clínica:

- Hallazgos clínicos observados deben representarse como Condition.
- Procedimientos realizados deben representarse como Procedure.
- Datos demográficos corresponden al recurso Patient.
- Datos del odontólogo corresponden al recurso Practitioner.
- El acto clínico debe representarse como Encounter.
- La estructura narrativa del expediente debe representarse con Composition.
- Si existe una ficha clínica completa, devolver Bundle document con Composition como recurso principal.

Reglas de terminología:

Utiliza preferentemente los CodeSystems y ValueSets de OdontoFHIR:

- Anatomía Dental
- Hallazgos Odontológicos
- Procedimientos Odontológicos
- Secciones de la Ficha Clínica
- Documentos de Identidad
- Nacionalidad
- Pueblos Indígenas
- Direcciones geográficas de Paraguay

Cuando se detecten conceptos clínicos compatibles con estas terminologías, utiliza los códigos definidos en OdontoFHIR.

Reglas específicas por perfil:

Patient (Paciente Odontológico):

- Debe incluir identifier con tipo de documento válido del ValueSet DocumentoIdentidad.
- Puede incluir extensiones:
    - nacionalidad
    - pueblosIndigenas
    - dirección paraguaya extendida (departamento, ciudad, barrio, número de casa).

Practitioner (Profesional Odontológico):

- Debe incluir extensión obligatoria para registro profesional RPRO.
- Debe incluir identifier oficial.

Encounter (Consulta Odontológica):

- Debe referenciar al Patient y al Practitioner.
- Puede contener referencia a Condition y Procedure asociados a la consulta.

Condition (Hallazgo Odontológico):

- Debe usar códigos del CodeSystem Hallazgos Odontológicos cuando corresponda.
- Puede incluir bodySite usando códigos de Anatomía Dental.

Procedure (Procedimiento Odontológico):

- Debe usar códigos del CodeSystem Procedimientos Odontológicos.
- Debe referenciar al paciente y al profesional.
- Puede referenciar hallazgos previos.

AllergyIntolerance (Registro de Alergias):

- Representa alergias o intolerancias relevantes del paciente.
- Debe incluir clinicalStatus y código de la sustancia o alergeno cuando sea posible.

Reglas de Bundle clínico:

Si el contenido describe una atención clínica completa:

- Devuelve un Bundle con type = "document".
- El primer recurso debe ser Composition (Ficha Clínica).
- El Composition debe referenciar:
    - Patient
    - Encounter
    - Condition
    - Procedure
    - AllergyIntolerance cuando existan.

Ejemplo estructural de referencia:
{json.dumps(FHIR_EXAMPLE, ensure_ascii=False, indent=2)}

Contenido a interpretar:
{texto_documento}
""".strip()


def build_image_input(tipo: str, media_type: str, image_base64: str):
    """
    Construye la entrada multimodal para imágenes.
    """
    prompt = f"""
Eres un experto en interoperabilidad clínica odontológica usando HL7 FHIR R4
y en la estructura del proyecto OdontoFHIR.

Debes interpretar la imagen clínica odontológica y devolver SOLO JSON válido.

Tipo solicitado por la interfaz:
{tipo}

Reglas obligatorias:
- Devuelve SOLO JSON válido.
- No incluyas explicaciones.
- No uses markdown.
- Usa estructura compatible con HL7 FHIR R4.
- Si el contenido corresponde a múltiples recursos relacionados, puedes devolver un Bundle.
- Si falta un dato, omite el campo en lugar de inventarlo.
- Si la imagen representa una ficha clínica más amplia, puedes devolver un Bundle tipo document.
- Prioriza la estructura usada por OdontoFHIR.

Ejemplo estructural de referencia:
{json.dumps(FHIR_EXAMPLE, ensure_ascii=False, indent=2)}
""".strip()

    return [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:{media_type};base64,{image_base64}"
                }
            ]
        }
    ]


def clean_raw_json_text(raw_text: str) -> str:
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def parse_json_output(raw_text: str):
    cleaned = clean_raw_json_text(raw_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        with open("debug_raw_output.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)

        raise HTTPException(
            status_code=502,
            detail={
                "message": "La IA no devolvió JSON válido.",
                "parse_error": str(exc),
                "raw_preview": cleaned[:1000]
            }
        ) from exc


def csv_to_structured_text(file_bytes: bytes) -> str:
    """
    Convierte CSV a texto estructurado legible por la IA.
    No asume columnas fijas; simplemente serializa filas.
    """
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío o no se pudo leer.")

    lines = ["Documento CSV odontológico:"]
    for index, row in enumerate(rows, start=1):
        clean_items = [f"{k}: {v}" for k, v in row.items()]
        lines.append(f"Fila {index}: " + " | ".join(clean_items))

    return "\n".join(lines)


def txt_to_text(file_bytes: bytes) -> str:
    """
    Lee un TXT como texto plano.
    """
    text = file_bytes.decode("utf-8", errors="ignore").strip()

    if not text:
        raise HTTPException(status_code=400, detail="El archivo TXT está vacío.")

    return text


def pdf_to_text(file_bytes: bytes) -> str:
    """
    Extrae texto de un PDF. Si el PDF es una imagen escaneada sin texto embebido,
    este método puede devolver poco contenido; en ese caso convendría tratarlo
    luego como imagen o usar OCR en otra etapa.
    """
    pages_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text() or ""
            if extracted.strip():
                pages_text.append(extracted)

    text = "\n\n".join(pages_text).strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No se pudo extraer texto del PDF. Es posible que sea un PDF escaneado."
        )

    return text


def interpret_text_with_ai(tipo: str, texto: str):
    prompt = build_prompt(tipo, texto)

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        text={"format": {"type": "json_object"}}
    )

    raw_text = response.output_text
    return parse_json_output(raw_text)


def interpret_image_with_ai(tipo: str, file_bytes: bytes, media_type: str):
    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
    input_payload = build_image_input(tipo, media_type, image_base64)

    response = client.responses.create(
        model="gpt-5-nano",
        input=input_payload,
        text={"format": {"type": "json_object"}}
    )

    raw_text = response.output_text
    return parse_json_output(raw_text)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convertir")
async def convertir_documento(
    tipo: str = Form(...),
    archivo: UploadFile = File(...)
):
    """
    Endpoint principal.
    Recibe el tipo elegido en el frontend y el archivo a interpretar.
    """
    if not archivo.filename:
        raise HTTPException(status_code=400, detail="No se recibió ningún archivo.")

    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo recibido está vacío.")

    extension = archivo.filename.rsplit(".", 1)[-1].lower()

    if extension == "csv":
        texto = csv_to_structured_text(contenido)
        return interpret_text_with_ai(tipo, texto)

    if extension == "txt":
        texto = txt_to_text(contenido)
        return interpret_text_with_ai(tipo, texto)

    if extension == "pdf":
        texto = pdf_to_text(contenido)
        return interpret_text_with_ai(tipo, texto)

    if extension in {"png", "jpg", "jpeg", "webp"}:
        media_type_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }
        return interpret_image_with_ai(tipo, contenido, media_type_map[extension])

    raise HTTPException(
        status_code=400,
        detail="Tipo de archivo no soportado. Usa CSV, TXT, PDF, PNG, JPG, JPEG o WEBP."
    )