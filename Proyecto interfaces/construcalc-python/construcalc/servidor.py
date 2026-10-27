
from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__, static_folder="css", static_url_path="/css")
app.secret_key = "construcalc"



@app.before_request
def revisar_sesion():
    libres = ["/", "/login", "/registro"]
    if request.path not in libres and not request.path.startswith("/css") and "usuario" not in session:
        return redirect("/login")


@app.route("/")
def inicio():
    return render_template("inicio.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("registro.html")
    f = request.form
    usuario = f["usuario"].strip().lower()
    if len(usuario) < 3 or len(f["clave"]) < 6 or f["clave"] != f["confirmar"]:
        return render_template("registro.html", error="Usuario mínimo 3 letras. Contraseña mínimo 6 y las dos iguales")
    with open("usuarios.json", encoding="utf-8") as archivo:
        lista = json.load(archivo)
    for u in lista:
        if u["usuario"] == usuario:
            return render_template("registro.html", error="Ese usuario ya existe")
    lista.append({"usuario": usuario, "nombre": usuario, "rol": f["rol"], "clave": f["clave"]})
    with open("usuarios.json", "w", encoding="utf-8") as archivo:
        json.dump(lista, archivo, indent=2, ensure_ascii=False)
    return render_template("login.html", mensaje="Cuenta creada. Ahora inicia sesión.")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    with open("usuarios.json", encoding="utf-8") as archivo:
        lista = json.load(archivo)
    for u in lista:
        if u["usuario"] == request.form["usuario"].strip().lower() and u["clave"] == request.form["clave"]:
            session["usuario"] = {"nombre": u["nombre"], "rol": u["rol"], "iniciales": u["nombre"][0].upper()}
            return redirect("/menu")
    return render_template("login.html", error="Usuario o contraseña incorrectos")


@app.route("/salir")
def salir():
    session.clear()
    return redirect("/login")


@app.route("/menu")
def menu():
    return render_template("menu.html", usuario=session["usuario"])



@app.route("/<pagina>", methods=["GET", "POST"])
def calcular(pagina):
    if pagina not in ["muro", "viga", "columna", "contrapiso-2", "losa", "piso", "pintura"]:
        return redirect("/menu")
    resultado = None
    if request.method == "POST":
        f = request.form
        if pagina == "muro":
            s = float(f["largo"]) * float(f["alto"])
            if f["espesor"] == "20":
                cemento, arena = 10.13, 0.077
            else:
                cemento, arena = 15.2, 0.115
            resultado = {"superficie": f"{s:.2f}", "cemento": f"{s * cemento:.2f}", "arena": f"{s * arena:.3f}", "ladrillos": round(s * 120)}
        elif pagina == "viga":
            L = float(f["largo"])
            resultado = {"cemento": f"{L * 9:.2f}", "arena": f"{L * 0.02:.3f}", "piedra": f"{L * 0.02:.3f}", "hierro8": f"{L * 4:.2f}", "hierro4": f"{L * 3:.2f}"}
        elif pagina == "columna":
            L = float(f["largo"])
            resultado = {"cemento": f"{L * 7.5:.2f}", "arena": f"{L * 0.016:.3f}", "piedra": f"{L * 0.016:.3f}", "hierro10": f"{L * 6:.2f}", "hierro4": f"{L * 3:.2f}"}
        elif pagina == "contrapiso-2":
            v = float(f["espesor"]) * float(f["ancho"]) * float(f["largo"])
            resultado = {"volumen": f"{v:.2f}", "cemento": f"{v * 105:.2f}", "arena": f"{v * 0.45:.3f}", "piedra": f"{v * 0.9:.3f}"}
        elif pagina == "losa":
            s = float(f["ancho"]) * float(f["largo"])
            resultado = {"superficie": f"{s:.2f}", "cemento": f"{s * 33:.2f}", "arena": f"{s * 0.072:.3f}", "piedra": f"{s * 0.072:.3f}", "hierro8": f"{s * 7:.2f}", "hierro6": f"{s * 4:.2f}"}
        elif pagina == "piso":
            s = float(f["ancho"]) * float(f["largo"])
            resultado = {"base": f"{s:.2f}", "recorte": f"{s * 0.10:.2f}", "total": f"{s * 1.10:.2f}"}
        elif pagina == "pintura":
            resultado = {"rendimiento": 6, "litros": f"{float(f['superficie']) / 6:.2f}"}
    return render_template(pagina + ".html", usuario=session["usuario"], resultado=resultado)


app.run(port=5000, debug=True)