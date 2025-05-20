from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import time
from transbank.webpay.webpay_plus.transaction import Transaction

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Sucursal

app = Flask(__name__)
app.secret_key = "zapatex-secret"

# Credenciales Transbank
commerce_code = "597055555532"
api_key = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"

# Configuración SQLite
engine = create_engine("sqlite:///zapatex.db")
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Poblado inicial (solo si BD está vacía)
def poblar_bd():
    if db_session.query(Sucursal).count() == 0:
        datos = [
            Sucursal(nombre="Sucursal 1", cantidad=50, precio=333),
            Sucursal(nombre="Sucursal 2", cantidad=23, precio=222),
            Sucursal(nombre="Sucursal 3", cantidad=100, precio=1111)
        ]
        db_session.add_all(datos)
        db_session.commit()

poblar_bd()

@app.route("/")
def venta():
    mensaje = session.pop("mensaje", None)
    sucursales = db_session.query(Sucursal).all()

    # Depuración: imprimir en consola los valores que se enviarán
    for s in sucursales:
        print(f"DEBUG - {s.nombre} stock: {s.cantidad}")

    return render_template("venta.html", casa_matriz={"cantidad": 10, "precio": 999}, sucursales=sucursales, mensaje=mensaje)


@app.route("/calcular_usd", methods=["POST"])
def calcular_usd():
    data = request.get_json()
    total_clp = data["total_clp"]
    usd_api = requests.get("https://api.exchangerate-api.com/v4/latest/CLP").json()
    tasa = usd_api["rates"]["USD"]
    total_usd = round(total_clp * tasa, 2)
    return jsonify({"total_usd": total_usd})

@app.route("/realizar_venta", methods=["POST"])
def realizar_venta():
    data = request.get_json()
    nombre_sucursal = data["sucursal"]
    cantidad = int(data["cantidad"])

    if cantidad <= 0:
        return jsonify({"status": "error", "message": "La cantidad debe ser mayor a 0."}), 400

    suc = db_session.query(Sucursal).filter_by(nombre=nombre_sucursal).first()
    if not suc or suc.cantidad < cantidad:
        return jsonify({"status": "error", "message": f"Stock insuficiente en {nombre_sucursal}"}), 400

    suc.cantidad -= cantidad
    db_session.commit()

    if suc.cantidad == 0:
        print(f"Stock bajo en {nombre_sucursal} (simulado SSE)")

    return jsonify({"status": "ok", "message": "Venta realizada correctamente"})

@app.route("/iniciar_pago", methods=["POST"])
def iniciar_pago():
    data = request.get_json()
    amount = data.get("amount", 1000)
    session["ultima_sucursal"] = data.get("sucursal", "Sucursal 1")
    session["ultima_cantidad"] = data.get("cantidad", 1)

    buy_order = f"ORD-{int(time.time())}"
    session_id = f"SID-{int(time.time())}"
    return_url = "http://127.0.0.1:5000/retorno_pago"

    tx = Transaction.build_for_integration(commerce_code=commerce_code, api_key=api_key)

    try:
        response = tx.create(buy_order, session_id, amount, return_url)
        return jsonify({"url": response['url'], "token": response['token']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/retorno_pago", methods=["GET", "POST"])
def retorno_pago():
    token_ws = request.args.get("token_ws") if request.method == "GET" else request.form.get("token_ws")

    if not token_ws:
        return "Token no válido", 400

    tx = Transaction.build_for_integration(commerce_code=commerce_code, api_key=api_key)

    try:
        response = tx.commit(token_ws)

        if response["status"] == "AUTHORIZED":
            nombre_sucursal = session.get("ultima_sucursal", "Sucursal 1")
            cantidad = int(session.get("ultima_cantidad", 1))

            suc = db_session.query(Sucursal).filter_by(nombre=nombre_sucursal).first()
            if suc and suc.cantidad >= cantidad:
                suc.cantidad -= cantidad
                db_session.commit()
                if suc.cantidad == 0:
                    print(f"Stock bajo en {nombre_sucursal} (simulado SSE)")
                session["mensaje"] = f"✅ Compra exitosa en {nombre_sucursal} - {cantidad} unidades compradas"
            else:
                session["mensaje"] = f"⚠️ Pago exitoso, pero stock insuficiente para registrar venta"

            return redirect(url_for("venta"))
        else:
            return f"<h1 style='color:red;'>❌ Pago rechazado</h1><p>Status: {response['status']}</p>"
    except Exception as e:
        return f"<h1 style='color:red;'>❌ Error en commit()</h1><pre>{str(e)}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
