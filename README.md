# SmartBakery · Sales Intelligence

Aplicación web en **Python + Streamlit + pandas** para explorar el histórico de
ventas de una panadería y obtener una interpretación del periodo con IA
generativa (Amazon Bedrock).

La aplicación calcula todas las cifras en local con pandas; el modelo de IA solo
interpreta esas métricas ya calculadas, nunca las recalcula.

## Funcionalidades

- **Acceso** con usuario y contraseña (local, de demostración).
- **Inicio**: saludo, fecha y portada animada.
- **Analítica**:
  - filtros por rango de fechas y por producto;
  - indicadores de ingresos y unidades con su variación contra el periodo
    anterior de la misma duración, producto más vendido y mejor día;
  - gráficas de ingresos por día, top 10 de productos (por ingresos o por
    unidades) y ventas por hora;
  - tabla de detalle con los registros filtrados;
  - panel **AI Business Analysis**, que envía las métricas agregadas a una API en
    AWS y muestra resumen, hallazgos y recomendaciones en forma de conversación.
- El resto de módulos del menú (Ventas, Productos, Inventario, Clientes,
  Pronósticos, Reportes y Configuración) muestran una pantalla de *Próximamente*.

## Requisitos

- **Python 3.11 o superior** (pandas 3 lo exige; probado con Python 3.14).
- Git.
- Una cuenta de Kaggle para descargar el dataset.
- Conexión a internet en el navegador para cargar la tipografía (Google Fonts) y
  los iconos de la portada (Font Awesome). Sin ella la aplicación funciona, con
  las fuentes del sistema y sin esos iconos.
- Opcional: un endpoint propio en AWS para el panel de IA (ver
  [Integración con IA](#integración-con-ia-opcional)).

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/SmartBakery.git
cd SmartBakery
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

Si PowerShell bloquea la activación, ejecuta una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Solo hay dos dependencias directas, con versión fijada: `streamlit==1.62.0` y
`pandas==3.0.5`.

### 4. Descargar el dataset

El dataset **no se incluye** en el repositorio. Descárgalo de Kaggle:
[French Bakery Daily Sales](https://www.kaggle.com/datasets/matthieugimbert/french-bakery-daily-sales).

Crea la carpeta `data/` en la raíz del proyecto y coloca el CSV con este nombre
exacto:

```text
data/Bakery sales.csv
```

Si usas la [CLI de Kaggle](https://github.com/Kaggle/kaggle-api), puedes hacerlo
en un solo paso:

```bash
kaggle datasets download -d matthieugimbert/french-bakery-daily-sales -p data --unzip
```

El CSV debe traer las columnas `date`, `time`, `ticket_number`, `article`,
`Quantity` y `unit_price` (la columna índice sin nombre se descarta). La
aplicación trabaja siempre con la copia local y nunca modifica el archivo.

### 5. Configurar las credenciales

Copia la plantilla de secretos:

```bash
# macOS / Linux / Git Bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Windows (PowerShell)
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Edita `.streamlit/secrets.toml` y define tu usuario y contraseña:

```toml
AWS_API_URL = ""

[auth]
username = "usuario"
password = "tu-clave"
```

Deja `AWS_API_URL` vacío si no tienes un endpoint de IA: el resto de la
aplicación funciona igual. `.streamlit/secrets.toml` está en `.gitignore` y
nunca debe subirse al repositorio.

### 6. Ejecutar

```bash
streamlit run app.py
```

La aplicación queda disponible en <http://localhost:8501>. Inicia sesión con las
credenciales del paso anterior.

## Estructura del proyecto

```text
SmartBakery/
├── app.py                      # Entrada: login, páginas y menú lateral
├── requirements.txt            # Dependencias con versión fijada
├── .streamlit/
│   ├── config.toml             # Tema: colores, tipografía y paleta de gráficas
│   └── secrets.toml.example    # Plantilla de credenciales y endpoint de IA
├── app_pages/
│   ├── home.py                 # Vista de Inicio
│   └── analytics.py            # Vista de Analítica
├── src/
│   ├── auth.py                 # Inicio de sesión local
│   ├── login_ui.py             # Estilos y animación de la pantalla de acceso
│   ├── home_ui.py              # Portada de Inicio
│   ├── sidebar.py              # Menú lateral
│   ├── ui.py                   # Tarjetas de indicadores, formatos y piezas comunes
│   ├── data_loader.py          # Lectura y limpieza del CSV (cacheada)
│   ├── analytics.py            # Métricas, agregaciones y payload para la IA
│   └── ai.py                   # Panel de IA y llamada a la API
├── assets/                     # Logo e ilustraciones SVG
└── data/                       # Dataset local (no se versiona)
```

Las páginas se registran con `st.navigation` y `st.Page`; el menú lateral se
dibuja a medida en `src/sidebar.py`.

## Cómo funciona

### Limpieza de datos

`src/data_loader.py` deja el dataset listo para analizar:

1. descarta las columnas índice tipo `Unnamed: 0`;
2. normaliza los encabezados a minúsculas (`Quantity` → `quantity`);
3. convierte `date` a fecha y extrae la hora del día de `time`;
4. convierte `quantity` y `ticket_number` a número;
5. limpia `unit_price` (símbolo `€`, espacios y coma decimal: `0,90 €` → `0.90`);
6. descarta los registros inválidos: fechas, horas o importes no convertibles y
   artículos vacíos o con el marcador `.`;
7. calcula `revenue = quantity * unit_price`.

Con el dataset original se descartan 5 de 234.005 filas. Las cantidades
negativas **se conservan**: son devoluciones, así que el ingreso mostrado es
neto.

### Rendimiento

Leer y limpiar el CSV es el único paso costoso, por eso `load_sales()` usa
`@st.cache_data` y solo se ejecuta una vez por proceso del servidor. Los filtros
y las agregaciones son operaciones vectorizadas de pandas que tardan decenas de
milisegundos, así que no se cachean.

### Apariencia

El tema (colores, radios, tipografía Space Grotesk y paleta de las gráficas) se
define en `.streamlit/config.toml`. Las piezas a medida (tarjetas de
indicadores, menú lateral, pantalla de acceso y portada) usan CSS y HTML
inyectados con `st.html` / `st.markdown`; la animación de partículas del acceso
corre en un `st.iframe`.

## Integración con IA (opcional)

El panel **AI Business Analysis** llama a una API HTTP:

```text
SmartBakery
     │  POST /sales/analyze (JSON)
     ▼
Amazon API Gateway → AWS Lambda → Amazon Bedrock (Amazon Nova Micro)
     │
     ▼
Resumen, hallazgos y recomendaciones
```

SmartBakery solo necesita la URL del endpoint en `AWS_API_URL`; **no guarda
ninguna credencial de AWS**. La autenticación entre Lambda y Bedrock se resuelve
con IAM del lado de AWS. El código de la Lambda no forma parte de este
repositorio: cualquier backend que respete el contrato de abajo funciona.

### Petición

`src/ai.py` envía con `urllib.request` un `POST` con
`Content-Type: application/json` y un timeout de 15 s. El cuerpo lo genera
`build_metrics_payload()` a partir de los datos filtrados (las listas están
recortadas en este ejemplo):

```json
{
  "currency": "EUR",
  "period": { "start": "2022-01-03", "end": "2022-01-09", "product_filter": "Todos" },
  "metrics": {
    "total_revenue": 3468.6,
    "total_units": 1826.0,
    "total_tickets": 789,
    "best_selling_product": "TRADITIONAL BAGUETTE",
    "highest_revenue_product": "TRADITIONAL BAGUETTE",
    "best_sales_day": "2022-01-09"
  },
  "top_products": [
    { "article": "TRADITIONAL BAGUETTE", "revenue": 688.8, "units": 574.0 }
  ],
  "daily_performance": [
    { "date": "2022-01-03", "revenue": 715.5, "units": 357.0 }
  ],
  "hourly_performance": [
    { "hour": 0, "revenue": 0.0 }
  ]
}
```

`top_products` trae hasta 10 productos, `daily_performance` un registro por día
con ventas y `hourly_performance` siempre las 24 horas. El payload exacto de la
selección actual se puede consultar en la propia aplicación, en
*Developer details*.

### Respuesta

La API debe responder `200` con este formato; si no, el panel muestra un error
de formato:

```json
{
  "analysis": {
    "summary": "...",
    "insights": ["...", "..."],
    "recommendations": ["...", "..."]
  }
}
```

Los errores HTTP se traducen a mensajes comprensibles, sin mostrar trazas ni la
URL del endpoint:

| Código | Mensaje en pantalla |
| --- | --- |
| 400 | Los datos enviados no son válidos para el análisis. |
| 401 / 403 | El servicio de análisis rechazó la solicitud. |
| 404 | No se encontró el servicio de análisis en la URL configurada. |
| 413 | Selecciona un periodo más corto para realizar el análisis con IA. |
| 429 | Se alcanzó temporalmente el límite de solicitudes. |
| Otros / timeout | El servicio no está disponible o no fue posible conectar. |

### Estados del panel

**Sin conectar** (falta `AWS_API_URL`), **Conectado**, **Analizando**,
**Analysis completed** y **Error**. Cada análisis se añade al hilo de la
conversación junto con los filtros que lo pidieron, así que se pueden comparar
varios seguidos. La conversación vive solo en `st.session_state`: no hay
persistencia.

## Limitaciones

- **El acceso es solo para uso local.** No hay hashing de contraseñas, sesiones
  firmadas ni control de intentos: las credenciales se comparan contra
  `secrets.toml` con `hmac.compare_digest`. No debe usarse como autenticación de
  producción.
- Solo están implementados los módulos **Inicio** y **Analítica**.
- No hay base de datos: la aplicación lee siempre el CSV local.
- La tabla de detalle muestra los primeros 100 registros filtrados e indica
  cuántos hay en total.
- Si la API responde `413`, hay que elegir un rango más corto: la aplicación no
  divide la petición automáticamente.

## Solución de problemas

| Síntoma | Causa y solución |
| --- | --- |
| `pip install` falla con `pandas==3.0.5` | Python anterior a 3.11. Crea el entorno con Python 3.11 o superior. |
| «No se encontró el dataset en …» | El CSV no está en `data/Bakery sales.csv` (revisa carpeta y nombre exacto). |
| «No hay credenciales configuradas» | Falta `.streamlit/secrets.toml` o su bloque `[auth]` (paso 5). |
| El panel de IA dice **Sin conectar** | `AWS_API_URL` está vacío, no empieza por `http(s)://` o quedó debajo de `[auth]`: en TOML las claves sueltas deben ir antes de cualquier sección. |
| Un cambio en `secrets.toml` no se aplica | Reinicia `streamlit run app.py`. |

## Créditos

- Dataset: *French Bakery Daily Sales*, publicado por Matthieu Gimbert en
  [Kaggle](https://www.kaggle.com/datasets/matthieugimbert/french-bakery-daily-sales).
- Ilustraciones de pan y croissant: [SVG Repo](https://www.svgrepo.com/).
- Tipografía [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk)
  (Google Fonts) e iconos de [Font Awesome](https://fontawesome.com/) y
  Material Symbols.
