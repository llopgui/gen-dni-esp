# Generador DNI (España) — aplicación de escritorio

Aplicación de **escritorio** en Python con interfaz **tkinter** para practicar el **algoritmo oficial** de la letra del DNI español: cálculo, validación y generación de identificadores **ficticios** con fines **didácticos**.

> **Propósito educativo.** Este repositorio es un **ejercicio de programación** y de interfaz de usuario. No sustituye documentación oficial, no verifica identidades reales y **no está pensado** para entornos de producción ni cumplimiento normativo.

---

## Tabla de contenidos

- [Aviso de uso responsable](#aviso-de-uso-responsable)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Recursos gráficos y ejecutable](#recursos-gráficos-y-ejecutable)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Notas técnicas](#notas-técnicas)
- [Licencia](#licencia)

---

## Aviso de uso responsable

Los números y combinaciones generados por esta herramienta son **aleatorios y ficticios** respecto a personas reales. Coincidencias casuales con datos reales son **posibles** y **no implican** que el software “obtenga” o “revelé” datos verdaderos.

**Queda prohibido** emplear este proyecto, o derivados del mismo, para:

- **Fraude**, estafa o suplantación de identidad  
- Eludir **controles de identidad**, verificación de clientes (KYC/AML) o sistemas de seguridad  
- **Acceso no autorizado** a sistemas, cuentas o servicios  
- Cualquier actividad que vulnere la **legislación aplicable** (incluida la protección de datos y la normativa penal)

El **autor y los colaboradores** no se hacen responsables del **uso indebido** del código. El uso del software es **exclusiva responsabilidad** de quien lo ejecuta o lo distribuye.

Si necesitas validar identidades o documentos en un contexto profesional, utiliza **procedimientos y herramientas homologadas** y asesoramiento legal adecuado.

---

## Características

| Área | Descripción |
|------|-------------|
| **Letra del DNI** | Cálculo de la letra de control a partir de ocho dígitos (tabla oficial). |
| **Validación** | Comprobación de un DNI completo (número + letra). |
| **Generación unitaria** | DNI aleatorio con entropía criptográfica (`secrets`). |
| **Lotes** | Hasta **10.000** DNIs únicos por lote, con exportación. |
| **Exportación** | Archivos **`.txt`** o **`.csv`** con separadores configurables (salto de línea, coma, punto y coma, tabulador). |
| **Interfaz** | Ventana única con diseño claro, aviso legal visible en la propia aplicación. |

---

## Requisitos

- **Python 3.10+** (recomendado usar la última versión estable que tengas instalada).  
- **tkinter** (incluido con la instalación estándar de Python en Windows en la mayoría de casos).  
- Dependencias **pip** solo para **desarrollo** y empaquetado: ver `requirements-dev.txt`.  
- En **tiempo de ejecución** la aplicación no exige paquetes pip adicionales (`requirements.txt` está vacío a propósito).

---

## Instalación

### Opción A: entorno con `uv` (recomendado si ya usas `uv`)

```bash
# Incluye pip en el venv (--seed). Sin él, algunos entornos uv quedan sin pip.
uv venv --seed
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt -r requirements-dev.txt
```

Si tu `.venv` se creó sin pip:

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
```

### Opción B: `venv` clásico

```bash
python -m venv .venv --upgrade-deps
```

**Windows:**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
```

---

## Uso

### Aplicación gráfica

Desde la **raíz del repositorio**:

```bash
python -m src.main
```

Equivalente directo a la GUI:

```bash
python -m src.dni_gui
```

### Registro (logging)

El módulo `src.dni` utiliza por defecto nivel **WARNING** (constante `_LOG_LEVEL_DEFAULT` en `src/dni.py`). No se emplea fichero `.env` ni variables de entorno para la configuración básica.

---

## Pruebas y calidad

```bash
pytest
```

Herramientas habituales del proyecto (definidas en `requirements-dev.txt`): **Black**, **Ruff**, **mypy**, **pytest-cov**, según tu flujo de trabajo.

---

## Recursos gráficos y ejecutable

En **`assets/`** se incluyen **`icon.png`** (origen) e **`icon.ico`** (Windows: ventana, barra de tareas y ejecutable empaquetado). La GUI resuelve rutas también bajo **PyInstaller** (`sys._MEIPASS`).

### Regenerar el icono `.ico`

Script mantenido en el repositorio (requiere **Pillow**, incluida en `requirements-dev.txt`):

```bash
python tools/generate_icons.py
```

Opciones avanzadas: `python tools/generate_icons.py --help`.

### Generar el `.exe` (Windows, PyInstaller)

Se usa el fichero **`GeneradorDNI.spec`** ( **`upx=False`**: comprimir el binario con UPX suele **estropear el icono** del ejecutable en Windows).

```bash
python tools/build_exe.py
```

Para limpiar la carpeta `build/` antes de compilar:

```bash
python tools/build_exe.py --clean
```

Salida esperada: **`dist/GeneradorDNI.exe`**. En el registro de PyInstaller debería aparecer la copia del icono al recurso del EXE.

**Nota:** Si `pyinstaller` instalado vía `uv` da problemas de *trampoline*, invoca siempre **`python -m PyInstaller`** (lo hace el script anterior). En caso extremo:

```powershell
.\.venv\Scripts\python.exe -m pip install --force-reinstall pyinstaller
```

---

## Estructura del proyecto

```text
gen-dni-esp/
├── assets/              # Iconos (PNG / ICO)
├── src/
│   ├── main.py          # Punto de entrada de la aplicación
│   ├── dni.py           # Lógica del DNI (cálculo, validación, lotes)
│   └── dni_gui.py       # Interfaz tkinter
├── tests/               # Pruebas automatizadas
├── tools/
│   ├── generate_icons.py   # Generación multi-resolución del .ico
│   └── build_exe.py        # Invocación reproducible de PyInstaller
├── GeneradorDNI.spec    # Especificación de empaquetado
├── requirements.txt
└── requirements-dev.txt
```

---

## Notas técnicas

- La generación aleatoria prioriza **`secrets`** del estándar library de Python.  
- Los DNIs de lote se generan como **únicos dentro del lote** (hasta el límite configurado en la UI).  
- El proyecto sirve para practicar **algoritmos**, **GUI**, **empaquetado** y **buenas prácticas** de documentación y licencias; no constituye asesoramiento legal ni de seguridad.

---

## Licencia

El texto de la licencia se encuentra en el fichero [`LICENSE`](LICENSE). Úsala y modifica el código de acuerdo con sus términos; la **responsabilidad** por el **uso** del software sigue siendo **tuya**, de acuerdo con el [aviso de uso responsable](#aviso-de-uso-responsable).

---

<p align="center">
  <sub>Proyecto de ejemplo / ejercicio · Python · tkinter · Sin garantías expresas o implícitas</sub>
</p>
