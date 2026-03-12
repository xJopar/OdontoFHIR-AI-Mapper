# **OdontoFHIR AI Mapper**

Este es un **prototipo de traducción asistida por IA** creado con la idea de agilizar la conversión de sistemas que **no utilizan FHIR** a documentos que puedan ser interpretados por un **servidor FHIR**.

La IA interpreta y convierte:

- fichas odontológicas de pacientes
- registros de alergias
- consultas clínicas

al estándar internacional **HL7 FHIR**, basado en los perfiles de **OdontoFHIR**, de forma rápida y sencilla.

Leer más sobre **OdontoFHIR** en: https://odontofhirparaguay.netlify.app/

# Estado del proyecto

Este proyecto es **un prototipo experimental**, para expandir el trabajo realizado con animos de explorar el uso de IA en la generación automática de recursos **HL7 FHIR** en el dominio odontológico.

https://sedici.unlp.edu.ar/handle/10915/191219

# Tecnologías utilizadas

### Backend

- Python
- FastAPI

### Frontend

- React
- Vite

### IA

- OpenAI API con el modelo **gpt-5-nano**

### Formato de datos Hl7 FHIR

- JSON FHIR

# Uso del sistema

## Configuración mínima

### `.env` para el backend

Declarar la API key de OpenAI:

```
OPENAI_API_KEY=tu_api_key
```


### `.env` para el frontend

Declarar la URL donde corre el backend:

```
VITE_API_URL=http://127.0.0.1:8000
```


# Ejecutar el sistema

### 1. Iniciar backend

```
uvicorn main:app--reload
```

---

### 2. Iniciar frontend

```
npm run dev
```