Proyecto CMR - Gestión de Ventas

Descripción del Proyecto

Este sistema de gestión de ventas (CMR) fue desarrollado como parte del examen parcial de Administración de Bases de Datos. La aplicación permite a los usuarios:

Visualizar un catálogo de productos (mínimo 10 artículos con descripción, imagen, precio y stock).

Crear un perfil de usuario y gestionar un carrito de compras.

Realizar pedidos, verificar datos de compra y descontar stock automáticamente.

Guardar pedidos en la base de datos con un ID único.

Acceder a un modo administrador para gestionar productos, pedidos y reportes.

Tecnologías Utilizadas

Backend: Python con Flask

Frontend: HTML, SCSS

Gestión de dependencias: Node.js y Gulp

Base de datos: SQLite (tienda.sqlite3)

Control de versiones: Git y GitHub

Organización de Carpetas

ENTREGA/ → Carpeta principal del proyecto

static/ → Archivos estáticos (imágenes, estilos SCSS/CSS)

templates/ → Vistas HTML

app.py → Aplicación Flask

package.json y package-lock.json → Dependencias Node.js y Gulp

.gitignore → Configuración de exclusiones

Funcionalidades Principales

Usuario

Visualizar catálogo de productos.

Crear perfil y acceder con usuario/contraseña.

Agregar productos al carrito.

Realizar pedidos y verificar datos.

Stock actualizado automáticamente.

Administrador

Login único con perfil y contraseña.

Agregar, eliminar y editar productos.

Actualizar stock.

Agregar avisos al cliente.

Ver y editar pedidos mediante check box.

Generar reporte de ventas diarias.

Roles del Equipo

Ana Camacho (@anneg)

Integración de ramas y resolución de conflictos en Git

Configuración de .gitignore y organización de carpetas

Documentación y soporte técnico

Pruebas y validación final

Jaqueline Pérez (@linnjackie)

Implementación de base de datos tienda.sqlite3

Inserción de productos iniciales (12 artículos en total)

Funciones de carrito y pedidos

Brisa Martínez [Líder de equipo] (@Bri21M)

Desarrollo de vistas en Flask (templates/)

Catálogo de productos y login de usuarios

Estilos SCSS y organización en static/

Módulo administrador (CRUD de productos, avisos, reportes)

Generación de reporte de ventas diarias

Todos los integrantes participaron en commits y revisiones de código para asegurar calidad y cumplimiento de la rúbrica.