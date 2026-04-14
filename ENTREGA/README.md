# Mi Tienda — Guía de Sass y Node.js

## 📦 Estructura del proyecto

```
mi_tienda_final/
├── app.py
├── tienda_db.py
├── tienda.sqlite3
├── package.json          ← Administrador de paquetes (Node.js)
│
├── scss/                 ← Código fuente de estilos (Sass)
│   ├── main.scss         ← Punto de entrada principal
│   ├── abstracts/
│   │   ├── _variables.scss   ← Colores, fuentes, espaciados
│   │   └── _mixins.scss      ← Funciones reutilizables
│   ├── layout/
│   │   ├── _base.scss        ← Reset y body
│   │   ├── _header.scss      ← Topbar y navegación
│   │   └── _container.scss   ← Grid y contenedor
│   ├── components/
│   │   ├── _card.scss        ← Tarjetas de producto
│   │   └── _buttons.scss     ← Botones y controles
│   └── pages/
│       ├── _login.scss       ← Página de login
│       └── _admin.scss       ← Panel de administración
│
├── static/
│   ├── styles.css        ← CSS compilado (NO editar directamente)
│   ├── normalize.css
│   └── img/
│
└── templates/
```

---

## 🚀 Instalación

### 1. Instalar Node.js
Descárgalo desde: https://nodejs.org (versión LTS recomendada)

### 2. Instalar dependencias del proyecto
Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
npm install
```

Esto descarga **Sass** automáticamente usando el `package.json`.

---

## ⚙️ Comandos disponibles

| Comando | Descripción |
|---|---|
| `npm run sass:build` | Compila Sass → CSS (versión comprimida para producción) |
| `npm run sass:watch` | Compila automáticamente al guardar cambios (desarrollo) |
| `npm run sass:dev`   | Compila con source maps para depurar en el navegador |

### Flujo de trabajo recomendado

1. Abre **dos terminales**:
   - Terminal 1: `npm run sass:watch` (deja corriendo)
   - Terminal 2: `python app.py` (servidor Flask)
2. Edita los archivos `.scss` en la carpeta `scss/`
3. Sass recompilará `static/styles.css` automáticamente

---

## ✏️ ¿Dónde editar los estilos?

| ¿Qué quieres cambiar? | Archivo a editar |
|---|---|
| Colores, fuentes, tamaños | `scss/abstracts/_variables.scss` |
| Topbar / header | `scss/layout/_header.scss` |
| Tarjetas de producto | `scss/components/_card.scss` |
| Botones | `scss/components/_buttons.scss` |
| Página de login | `scss/pages/_login.scss` |
| Panel de admin | `scss/pages/_admin.scss` |

> ⚠️ **No edites `static/styles.css` directamente** — Sass lo sobreescribirá cada vez que compiles.

---

## 🎨 Variables principales

```scss
// En scss/abstracts/_variables.scss

$bg-color:   #f5efe6;   // Fondo crema
$card-bg:    #e8ded1;   // Beige de tarjetas
$text-dark:  #2d5a56;   // Verde pino (color principal)
$text-muted: #8a7e72;   // Gris café para descripciones
```

Para cambiar la paleta de colores de toda la tienda, solo modifica estos valores.
