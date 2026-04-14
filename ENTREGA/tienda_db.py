# tienda_db.py
import os
import sqlite3
from sqlite3 import Error


class BaseDatosTienda:
    def __init__(self, ruta="./", bd="tienda.sqlite3"):
        self.bd_path = os.path.join(ruta, bd)
        self.con = None
        self.cursor = None
        self.conectar()
        self.crear_tablas()

    def conectar(self):
        try:
            self.con = sqlite3.connect(self.bd_path, check_same_thread=False)
            self.con.row_factory = sqlite3.Row
            self.cursor = self.con.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            self.con.commit()
        except Error as e:
            print(f"[DB] Error al conectar: {e}")

    def cerrar(self):
        try:
            if self.con:
                self.con.close()
        except Error as e:
            print(f"[DB] Error al cerrar: {e}")

    def crear_tablas(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio REAL NOT NULL CHECK(precio >= 0),
                    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                    imagen_url TEXT
                );
            """)
            # Agrega la columna si la tabla ya existía sin ella
            try:
                self.cursor.execute("ALTER TABLE productos ADD COLUMN imagen_url TEXT;")
                self.con.commit()
            except Exception:
                pass  # La columna ya existe, no hay problema

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_nombre TEXT NOT NULL,
                    cliente_email TEXT,
                    total REAL NOT NULL CHECK(total >= 0),
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    direccion TEXT,
                    ciudad TEXT,
                    telefono TEXT,
                    creado_en TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedido_items(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                    precio_unit REAL NOT NULL CHECK(precio_unit >= 0),
                    FOREIGN KEY(pedido_id) REFERENCES pedidos(id)
                        ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY(producto_id) REFERENCES productos(id)
                        ON DELETE RESTRICT ON UPDATE CASCADE
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS avisos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    activo INTEGER NOT NULL DEFAULT 1,
                    creado_en TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS gastos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concepto TEXT NOT NULL,
                    monto REAL NOT NULL CHECK(monto >= 0),
                    fecha TEXT NOT NULL DEFAULT (date('now'))
                );
            """)

            # Migración: agregar columnas de entrega si ya existía la tabla sin ellas
            for col in [
                "ALTER TABLE pedidos ADD COLUMN direccion TEXT;",
                "ALTER TABLE pedidos ADD COLUMN ciudad TEXT;",
                "ALTER TABLE pedidos ADD COLUMN telefono TEXT;"
            ]:
                try:
                    self.cursor.execute(col)
                    self.con.commit()
                except Exception:
                    pass

            # Migración: agregar columna 'estado' si ya existía la tabla sin ella
            try:
                self.cursor.execute("ALTER TABLE pedidos ADD COLUMN estado TEXT NOT NULL DEFAULT 'pendiente';")
                self.con.commit()
            except Exception:
                pass  # La columna ya existe

            self.con.commit()
        except Error as e:
            print(f"[DB] Error creando tablas: {e}")

    # --------- Productos (CRUD) ----------
    def crear_producto(self, nombre, descripcion, precio, stock, imagen_url=None):
        try:
            self.cursor.execute("""
                INSERT INTO productos(nombre, descripcion, precio, stock, imagen_url)
                VALUES(?,?,?,?,?);
            """, (nombre.strip(), descripcion, float(precio), int(stock), imagen_url))
            self.con.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"[DB] No se pudo crear producto: {e}")
            return None

# --------- Usuarios (ESTO ES LO QUE FALTA) ----------
    def verificar_usuario(self, usuario, password):
        """Verifica credenciales y retorna el usuario si existe."""
        try:
            # Buscamos en la tabla 'usuarios'
            self.cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?;", (usuario, password))
            return self.cursor.fetchone()
        except Error as e:
            print(f"[DB] Error verificando usuario: {e}")
            return None
        
    def listar_productos(self):
        try:
            self.cursor.execute("SELECT * FROM productos ORDER BY id DESC;")
            return self.cursor.fetchall()
        except Error as e:
            print(f"[DB] Error listando productos: {e}")
            return []

    def obtener_producto(self, producto_id):
        try:
            self.cursor.execute("SELECT * FROM productos WHERE id=?;", (producto_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"[DB] Error obteniendo producto: {e}")
            return None

    def actualizar_stock(self, producto_id, nuevo_stock):
        try:
            self.cursor.execute(
                "UPDATE productos SET stock=? WHERE id=?;",
                (int(nuevo_stock), producto_id)
            )
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error actualizando stock: {e}")
            return False

    # --------- Pedidos ----------
    def crear_pedido(self, cliente_nombre, cliente_email, items, **kwargs):
        """
        items: lista de dicts: [{"producto_id":1, "cantidad":2}, ...]
        - Calcula total
        - Valida stock
        - Descuenta stock
        - Inserta pedido + items en transacción
        """
        try:
            self.cursor.execute("BEGIN;")

            total = 0.0
            lineas = []

            for it in items:
                pid = int(it["producto_id"])
                qty = int(it["cantidad"])

                self.cursor.execute("SELECT id, precio, stock FROM productos WHERE id=?;", (pid,))
                p = self.cursor.fetchone()
                if not p:
                    raise ValueError(f"Producto {pid} no existe")
                if p["stock"] < qty:
                    raise ValueError(f"Stock insuficiente para producto {pid}")

                precio_unit = float(p["precio"])
                total += precio_unit * qty
                lineas.append((pid, qty, precio_unit))

            self.cursor.execute("""
                INSERT INTO pedidos(cliente_nombre, cliente_email, total, direccion, ciudad, telefono)
                VALUES(?,?,?,?,?,?);
            """, (cliente_nombre.strip(), cliente_email, total,
                    kwargs.get('direccion'), kwargs.get('ciudad'), kwargs.get('telefono')))
            pedido_id = self.cursor.lastrowid

            for (pid, qty, precio_unit) in lineas:
                self.cursor.execute("""
                    INSERT INTO pedido_items(pedido_id, producto_id, cantidad, precio_unit)
                    VALUES(?,?,?,?);
                """, (pedido_id, pid, qty, precio_unit))

                # descontar stock
                self.cursor.execute("""
                    UPDATE productos SET stock = stock - ?
                    WHERE id=?;
                """, (qty, pid))

            self.con.commit()
            return pedido_id

        except Exception as e:
            self.con.rollback()
            print(f"[DB] Error creando pedido: {e}")
            return None

    def eliminar_producto(self, producto_id):
        try:
            self.cursor.execute("DELETE FROM productos WHERE id=?;", (producto_id,))
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error eliminando producto: {e}")
            return False

    def actualizar_producto(self, producto_id, nombre, descripcion, precio, stock, imagen_url=None):
        try:
            if imagen_url:
                self.cursor.execute(
                    "UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=?, imagen_url=? WHERE id=?;",
                    (nombre.strip(), descripcion, float(precio), int(stock), imagen_url, producto_id)
                )
            else:
                self.cursor.execute(
                    "UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=? WHERE id=?;",
                    (nombre.strip(), descripcion, float(precio), int(stock), producto_id)
                )
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error actualizando producto: {e}")
            return False

    # --------- Avisos ----------
    def crear_aviso(self, titulo, mensaje):
        try:
            self.cursor.execute(
                "INSERT INTO avisos(titulo, mensaje) VALUES(?,?);",
                (titulo.strip(), mensaje.strip())
            )
            self.con.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"[DB] Error creando aviso: {e}")
            return None

    def listar_avisos(self, solo_activos=False):
        try:
            if solo_activos:
                self.cursor.execute("SELECT * FROM avisos WHERE activo=1 ORDER BY creado_en DESC;")
            else:
                self.cursor.execute("SELECT * FROM avisos ORDER BY creado_en DESC;")
            return self.cursor.fetchall()
        except Error as e:
            print(f"[DB] Error listando avisos: {e}")
            return []

    def eliminar_aviso(self, aviso_id):
        try:
            self.cursor.execute("DELETE FROM avisos WHERE id=?;", (aviso_id,))
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error eliminando aviso: {e}")
            return False

    # --------- Pedidos (admin) ----------
    def listar_pedidos(self):
        try:
            self.cursor.execute("""
                SELECT p.id, p.cliente_nombre, p.cliente_email, p.total,
                       p.creado_en, p.estado,
                       GROUP_CONCAT(pr.nombre || ' x' || pi.cantidad, ', ') AS productos
                FROM pedidos p
                LEFT JOIN pedido_items pi ON pi.pedido_id = p.id
                LEFT JOIN productos pr ON pr.id = pi.producto_id
                GROUP BY p.id
                ORDER BY p.creado_en DESC;
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"[DB] Error listando pedidos: {e}")
            return []

    def actualizar_estado_pedido(self, pedido_id, estado):
        estados_validos = ("pendiente", "procesando", "enviado", "entregado", "cancelado")
        if estado not in estados_validos:
            return False
        try:
            self.cursor.execute("UPDATE pedidos SET estado=? WHERE id=?;", (estado, pedido_id))
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error actualizando estado de pedido: {e}")
            return False

    def reporte_ventas_diarias(self, fecha=None):
        """Retorna pedidos y totales del día indicado (hoy por defecto)."""
        try:
            if not fecha:
                from datetime import date
                fecha = date.today().isoformat()
            self.cursor.execute("""
                SELECT p.id, p.cliente_nombre, p.cliente_email, p.total,
                       p.creado_en, p.estado,
                       GROUP_CONCAT(pr.nombre || ' x' || pi.cantidad, ', ') AS productos
                FROM pedidos p
                LEFT JOIN pedido_items pi ON pi.pedido_id = p.id
                LEFT JOIN productos pr ON pr.id = pi.producto_id
                WHERE DATE(p.creado_en) = ?
                GROUP BY p.id
                ORDER BY p.creado_en;
            """, (fecha,))
            pedidos = self.cursor.fetchall()
            self.cursor.execute(
                "SELECT COALESCE(SUM(total),0) as gran_total, COUNT(*) as num_pedidos FROM pedidos WHERE DATE(creado_en)=?;",
                (fecha,)
            )
            resumen = self.cursor.fetchone()
            return {"fecha": fecha, "pedidos": pedidos, "resumen": resumen}
        except Error as e:
            print(f"[DB] Error en reporte diario: {e}")
            return {"fecha": fecha, "pedidos": [], "resumen": None}

    # --------- Usuarios (registro) ----------
    def registrar_usuario(self, usuario, password):
        try:
            self.cursor.execute(
                "INSERT INTO usuarios(usuario, password, rol) VALUES(?,?,'cliente');",
                (usuario.strip(), password)
            )
            self.con.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"[DB] Error registrando usuario: {e}")
            return None

    # --------- Gastos ----------
    def crear_gasto(self, concepto, monto, fecha=None):
        try:
            if fecha:
                self.cursor.execute(
                    "INSERT INTO gastos(concepto, monto, fecha) VALUES(?,?,?);",
                    (concepto.strip(), float(monto), fecha)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO gastos(concepto, monto) VALUES(?,?);",
                    (concepto.strip(), float(monto))
                )
            self.con.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"[DB] Error creando gasto: {e}")
            return None

    def listar_gastos(self, fecha=None):
        try:
            if fecha:
                self.cursor.execute(
                    "SELECT * FROM gastos WHERE fecha=? ORDER BY id DESC;", (fecha,)
                )
            else:
                self.cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC, id DESC;")
            return self.cursor.fetchall()
        except Error as e:
            print(f"[DB] Error listando gastos: {e}")
            return []

    def eliminar_gasto(self, gasto_id):
        try:
            self.cursor.execute("DELETE FROM gastos WHERE id=?;", (gasto_id,))
            self.con.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"[DB] Error eliminando gasto: {e}")
            return False

    def semilla_productos(self):
        """Crea tablas de usuarios, admin por defecto y productos iniciales."""
        try:
            # Crear tabla de usuarios si no existe
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'cliente'
                );
            """)
            self.con.commit()

            # Crear admin por defecto si no hay usuarios
            self.cursor.execute("SELECT COUNT(*) as c FROM usuarios;")
            if self.cursor.fetchone()["c"] == 0:
                self.cursor.execute(
                    "INSERT INTO usuarios(usuario, password, rol) VALUES('admin','admin123','admin');"
                )
                self.con.commit()
                print("[DB] Administrador por defecto creado (admin / admin123)")

            # Insertar productos iniciales si la tabla está vacía
            self.cursor.execute("SELECT COUNT(*) as c FROM productos;")
            if self.cursor.fetchone()["c"] == 0:
                productos = [
                    (
                        "Peluche Haru Urara",
                        "Peluche de Haru Uruara, la hija de todo fan de umamusume",
                        350.00, 10,
                        "/static/img/haru.jpg"
                    ),
                    (
                        "Figura de T.M Opera O",
                        "Figura de T.M Opera O",
                        850.00, 5,
                        "/static/img/opera.png"
                    ),
                    (
                        "Figura de Sakura Bakushin O",
                        "Figura de Sakura Bakushin O",
                        900.00, 5,
                        "/static/img/sakura.jpg"
                    ),
                ]
                for nombre, desc, precio, stock, img in productos:
                    self.cursor.execute(
                        "INSERT INTO productos(nombre, descripcion, precio, stock, imagen_url) VALUES(?,?,?,?,?);",
                        (nombre, desc, precio, stock, img)
                    )
                self.con.commit()
                print("[DB] Productos iniciales creados.")

        except Error as e:
            print(f"[DB] Error en semilla inicial: {e}")