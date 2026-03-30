import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from tienda_db import BaseDatosTienda

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = "cambia-esto-por-algo-seguro"

db = BaseDatosTienda(ruta="./", bd="tienda.sqlite3")
# IMPORTANTE: Usamos la nueva semilla para crear al admin y no productos basura
db.semilla_productos() 

def carrito_session():
    if "carrito" not in session:
        session["carrito"] = {}
    return session["carrito"]

# --- RUTAS DE AUTENTICACIÓN ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        
        user_data = db.verificar_usuario(usuario, password)
        
        if user_data:
            session["usuario_id"] = user_data["id"]
            session["usuario_nombre"] = user_data["usuario"]
            session["rol"] = user_data["rol"]
            flash(f"Bienvenido {user_data['usuario']}")
            
            if user_data["rol"] == "admin":
                return redirect(url_for("admin_panel"))
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos.")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.")
    return redirect(url_for("index"))

# --- RUTA DE ADMINISTRADOR (NUEVA) ---

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Protección de seguridad: si no es admin, mandarlo al login o error
    if session.get("rol") != "admin":
        flash("Acceso restringido solo para administradores.")
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio", type=float)
        stock = request.form.get("stock", type=int)
        imagen_url = None

        # Manejo de archivo de imagen subido
        archivo = request.files.get("imagen")
        if archivo and archivo.filename and allowed_file(archivo.filename):
            ext = archivo.filename.rsplit(".", 1)[1].lower()
            nombre_archivo = f"{uuid.uuid4().hex}.{ext}"
            carpeta = os.path.join(app.root_path, "static", "img")
            os.makedirs(carpeta, exist_ok=True)
            archivo.save(os.path.join(carpeta, nombre_archivo))
            imagen_url = f"/static/img/{nombre_archivo}"

        if nombre and precio is not None:
            db.crear_producto(nombre, descripcion, precio, stock, imagen_url)
            flash("Producto agregado correctamente.")
        else:
            flash("Error: El nombre y el precio son obligatorios.")
        
        return redirect(url_for("admin_panel"))

    productos = db.listar_productos()
    return render_template("admin.html", productos=productos)

# --- RUTAS DE LA TIENDA (TU CÓDIGO ORIGINAL) ---

@app.route("/")
def index():
    productos = db.listar_productos()
    return render_template("index.html", productos=productos, carrito=carrito_session())

@app.route("/producto/<int:producto_id>")
def producto(producto_id):
    p = db.obtener_producto(producto_id)
    if not p:
        return "Producto no encontrado", 404
    return render_template("producto.html", p=p, carrito=carrito_session())

@app.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    pid = request.form.get("producto_id", type=int)
    qty = request.form.get("cantidad", type=int, default=1)

    p = db.obtener_producto(pid)
    if not p:
        flash("Producto no existe.")
        return redirect(url_for("index"))

    cart = carrito_session()
    cart[str(pid)] = int(cart.get(str(pid), 0)) + max(qty, 1)
    session["carrito"] = cart
    flash("Agregado al carrito.")
    return redirect(request.referrer or url_for("index"))

@app.route("/carrito")
def carrito():
    cart = carrito_session()
    items = []
    total = 0.0

    for pid_str, qty in cart.items():
        p = db.obtener_producto(int(pid_str))
        if not p:
            continue
        subtotal = float(p["precio"]) * int(qty)
        total += subtotal
        items.append({"p": p, "qty": int(qty), "subtotal": subtotal})

    return render_template("carrito.html", items=items, total=total)

@app.route("/carrito/quitar", methods=["POST"])
def carrito_quitar():
    pid = request.form.get("producto_id", type=int)
    cart = carrito_session()
    cart.pop(str(pid), None)
    session["carrito"] = cart
    return redirect(url_for("carrito"))

@app.route("/checkout", methods=["POST"])
def checkout():
    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip() or None

    if not nombre:
        flash("Escribe tu nombre para continuar.")
        return redirect(url_for("carrito"))

    cart = carrito_session()
    if not cart:
        flash("Tu carrito está vacío.")
        return redirect(url_for("index"))

    items = [{"producto_id": int(pid), "cantidad": int(qty)} for pid, qty in cart.items()]

    pedido_id = db.crear_pedido(nombre, email, items)
    if not pedido_id:
        flash("No se pudo procesar el pedido (¿stock insuficiente?).")
        return redirect(url_for("carrito"))

    session["carrito"] = {}
    return render_template("checkout_ok.html", pedido_id=pedido_id)

# Corregido el error de dedo de tu código original: era __name__ y "__main__"
if __name__ == "__main__":
    app.run(debug=True)