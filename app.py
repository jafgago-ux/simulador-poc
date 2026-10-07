import subprocess
import tempfile
from pathlib import Path
from flask import Flask, request, render_template, send_file
from openpyxl import load_workbook

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simular", methods=["POST"])
def simular():
    try:
        a1 = int(request.form["a1"])
        a2 = int(request.form["a2"])
    except ValueError:
        return "Por favor, introduce números enteros válidos.", 400

    # Carpeta temporal que se borra sola al terminar
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        # 1. Abrir la plantilla Excel
        wb = load_workbook("plantilla.xlsx")

        # 2. Escribir los números en la hoja INPUTS
        ws_inputs = wb["INPUTS"]
        ws_inputs["A1"] = a1
        ws_inputs["A2"] = a2
	
	wb.active = wb["OUTPUTS"]

        # 3. Guardar el Excel modificado en la carpeta temporal
        excel_modificado = td_path / "modificado.xlsx"
        wb.save(excel_modificado)

        # 4. Ejecutar LibreOffice para recalcular y convertir a PDF
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf:calc_pdf_Export",
            "--outdir", str(td_path),
            str(excel_modificado)
        ], check=True, timeout=120)

        # 5. Enviar el PDF al navegador
        pdf_path = td_path / "modificado.pdf"
        return send_file(pdf_path, as_attachment=True, download_name="resultado.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)