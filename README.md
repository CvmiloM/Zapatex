🥾 Zapatex - Sistema de Venta con Flask

Este proyecto es una app web básica hecha con Python + Flask, que simula una venta entre casa matriz y sucursales. Incluye cálculo de precios en dólares y un frontend estilizado con Tailwind CSS.

⚙️ Requisitos Previos

- Python 3.x
- Git (opcional, pero útil)
- Editor como VSCode

📦 Instalación del Entorno

1. Clona este repositorio (si no lo tienes aún)

git clone https://github.com/tu-usuario/zapatex.git
cd zapatex

2. Crea el entorno virtual

python -m venv venv

3. Activa el entorno virtual

- En PowerShell (Windows):
.
env\Scripts\Activate.ps1

- En CMD (Windows):
venv\Scripts ctivate.bat

- En Linux/macOS:
source venv/bin/activate

📥 Instalación de dependencias

pip install -r requirements.txt

Si requirements.txt no existe o está vacío, puedes instalar manualmente:

pip install flask requests

🚀 Ejecutar la Aplicación

Opción 1: Forma simple (recomendada)

python app.py

Asegúrate de que app.py tenga este bloque al final:

if __name__ == "__main__":
    app.run(debug=True)

Opción 2: Usando FLASK_ENV (requiere que el comando flask funcione en tu terminal)

$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run

🖥️ Ver la app

Una vez corriendo, abre tu navegador en:

http://127.0.0.1:5000

🧾 Notas

- El frontend usa Tailwind CSS vía CDN, no necesita instalación.
- static/js/script.js contiene la lógica de interacción.
- Los datos de sucursales están simulados como diccionarios Python.
