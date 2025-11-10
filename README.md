# 🧠 Centro de Capacitación Ultra-Automatizado
### Backend de Automatización Inteligente (FastAPI + LangGraph + LangChain)

---

## 🌍 Contexto de la Idea

Este proyecto nace del caso **“Centro de Capacitación Ultra-Automatizado”**, una propuesta de ingeniería que busca demostrar cómo una empresa digital puede **automatizar todos los procesos de capacitación corporativa** utilizando inteligencia artificial.

El objetivo es construir un sistema que funcione casi como un **organismo digital vivo**:
- **El cerebro (IA + LLMs)** interpreta las necesidades del cliente expresadas en lenguaje natural.
- **La memoria (Base de Datos Vectorial)** recuerda y reutiliza contenidos previos.
- **El sistema nervioso (LangGraph)** coordina los pasos, controla los flujos y aprende de los resultados.
- **El esqueleto (LMS + Backend)** arma los cursos, los evalúa y los publica automáticamente.
- **El corazón (pasarela de pagos)** mantiene el ciclo financiero sin intervención humana.

En resumen: un cliente escribe “Necesito entrenar a mi equipo de ventas en empatía y manejo de CRM”,  
y la plataforma responde generando **una propuesta de curso completa, con precio, contenidos, videos, evaluaciones y certificación automática**… todo en cuestión de minutos.

---

## ⚙️ Descripción Técnica

El sistema está dividido en **4 Macroprocesos**, cada uno gestionado por un grafo independiente de LangGraph:

1. **M1 – Interacción y Definición:**  
   Captura el prompt del cliente, analiza el lenguaje natural, genera preguntas de clarificación y crea la propuesta del curso.

2. **M2 – Fabricación del Contenido:**  
   El motor de IA produce el contenido educativo (lecciones, videos, quizzes) y lo ensambla en el LMS.

3. **M3 – Entrega y Administración:**  
   Publica el curso, notifica al cliente, asigna alumnos y monitoriza su progreso.

4. **M4 – Evolución y Mantenimiento:**  
   Analiza métricas, feedback, pagos y mejoras, alimentando la memoria del sistema para hacerlo más inteligente.

---

## 🧠 Tecnologías principales

- **Python 3.10+**
- **FastAPI** – servidor principal (API REST)
- **LangGraph** – orquestación de flujos con IA
- **LangChain** – cadenas y herramientas cognitivas
- **FAISS / Chroma** – búsqueda semántica de contenidos
- **SQLite** – persistencia local de checkpoints
- **Uvicorn** – servidor ASGI para desarrollo

---

## 🚀 Instalación y Ejecución

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu_usuario/automa-backend.git
cd automa-backend/backend
```

### 2️⃣ Crear entorno virtual
**Windows CMD**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

> Si no tienes `requirements.txt`, puedes crear uno con:
> ```
> fastapi
> uvicorn
> langchain
> langchain-openai
> langgraph
> langchain-community
> faiss-cpu
> pydantic
> python-dotenv
> ```

---

### 4️⃣ Ejecutar el servidor FastAPI
Desde la carpeta `backend`:
```bash
uvicorn api.main:app --reload
```

---

### 5️⃣ Verificar que corre en localhost
Abre tu navegador en:

```
http://127.0.0.1:8000
```

Deberías ver algo como:
```json
{"status": "ok", "message": "AUTOMA backend corriendo correctamente"}
```

También puedes probar la documentación automática en:
```
http://127.0.0.1:8000/docs
```

Ahí podrás ejecutar directamente los endpoints de prueba como `/m1/prompt`, `/m1/answers`, `/m1/approval`, etc.

---

## 🧩 Estructura de Carpetas del Backend

```
backend/
├── api/
│   ├── main.py
│   ├── routes/
│   │   ├── m1_interaccion.py
│   │   ├── m2_fabricacion.py
│   │   ├── m3_entrega.py
│   │   ├── m4_evolucion.py
│   │   └── health.py
│   ├── schemas/
│   ├── deps.py
│   └── middleware.py
│
├── core/
│   ├── config.py
│   ├── logging.py
│   ├── metrics.py
│   ├── errors.py
│   └── utils.py
│
├── graphs/
│   ├── m1_interaccion/
│   │   ├── graph.py
│   │   ├── nodes/
│   │   │   ├── nlp.py
│   │   │   ├── clarify.py
│   │   │   ├── mapping.py
│   │   │   ├── syllabus.py
│   │   │   ├── pricing.py
│   │   │   └── proposal.py
│   │   └── prompts/
│   ├── m2_fabricacion/
│   │   └── graph.py
│   ├── m3_entrega/
│   │   └── graph.py
│   └── m4_evolucion/
│       └── graph.py
│
├── services/
│   ├── retriever/
│   │   ├── build_index.py
│   │   ├── loader.py
│   │   └── skills_data/
│   ├── lms_adapter.py
│   ├── mailer.py
│   ├── payment_adapter.py
│   └── qc_validator.py
│
├── data/
│   ├── checkpoints/
│   │   └── m1.sqlite
│   └── skills_index/
│       └── faiss_index.bin
│
├── tests/
│   └── test_nodes/
│
├── scripts/
│   ├── run_dev.sh
│   └── rebuild_index.py
│
├── requirements.txt
└── README.md
```

---

## 👨‍💻 Ejemplo de flujo básico

1. El cliente escribe en el frontend:  
   `"Necesito un curso para entrenar a mi equipo de ventas en empatía y manejo de CRM."`

2. El backend (M1) ejecuta:
   - Extracción de competencias.
   - Generación de preguntas de clarificación (si aplica).
   - Creación de sílabus + cotización dinámica.

3. El cliente aprueba → inicia M2:
   - Se genera el curso completo con lecciones, videos, quizzes.

4. El LMS publica automáticamente el curso (M3).

5. Los datos de uso alimentan M4 para mejorar los futuros cursos.

---

## 🧩 Créditos
**Centro de Capacitación Ultra-Automatizado**  
Proyecto académico – Ingeniería de Computación y Sistemas e Inteligencia Artificial   
**Semestre:** 2025-20  
**Universidad:** Universidad Privada Antenor Orrego – Trujillo, Perú
