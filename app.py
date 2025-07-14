import streamlit as st
import requests
import urllib.parse

API_URL = "http://localhost:8080/api/products"
BASE_URL = "http://localhost:8080"

# --- Configuración de la página y Estilos CSS ---
st.set_page_config(layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

/* Oculta el encabezado por defecto de Streamlit */
.stApp > header {
    display: none;
}

/* Oculta la barra de menú con las opciones "About", "Settings", etc. */
.css-h5rpfg {
    display: none;
}

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #f5f7fa;
    color: #222222;
}

.header {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 25px 0 15px 0;
    border-bottom: 2px solid #ddd;
}
.header img {
    height: 60px;
    border-radius: 12px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.header h1 {
    font-weight: 900;
    font-size: 3.5rem;
    background: linear-gradient(90deg, #27ae60, #2ecc71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: 2px;
}
.header h1 {
    font-weight: 900;
    font-size: 3.5rem;
    color: #27ae60;
    text-shadow: 2px 2px 8px rgba(39, 174, 96, 0.7);
    margin: 0;
}

/* Tarjeta producto */
.product-container {
    background: white;
    border-radius: 18px;
    box-shadow: 0 8px 18px rgba(0,0,0,0.1);
    padding: 22px 20px;
    margin-bottom: 30px;
    transition: transform 0.2s ease-in-out;
    box-sizing: border-box;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.product-container:hover {
    transform: translateY(-6px);
    box-shadow: 0 14px 28px rgba(0,0,0,0.15);
}

.product-image img {
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    width: 100%;
    height: 180px;
    object-fit: contain;
    margin-bottom: 15px;
}

.product-details h2 {
    color: #34495e;
    font-weight: 700;
    margin-bottom: 8px;
    font-size: 1.3rem;
}

.price {
    font-size: 1.3rem;
    font-weight: 700;
    color: #27ae60;
    margin-top: 4px;
    margin-bottom: 8px;
}

.kg-info {
    font-size: 1.1rem;
    font-weight: 600;
    color: #555555;
    margin-bottom: 10px;
}

.description {
    font-size: 1.05rem;
    color: #555;
    line-height: 1.5;
    margin-bottom: 18px;
    white-space: pre-wrap;
    flex-grow: 1;
}

.whatsapp-btn {
    display: inline-block;
    background-color: #25d366;
    color: white !important;
    font-weight: 700;
    padding: 12px 26px;
    border-radius: 50px;
    text-decoration: none;
    box-shadow: 0 7px 16px rgba(37,211,102,0.45);
    transition: background-color 0.3s ease;
    font-size: 1.1rem;
    text-align: center;
}
.whatsapp-btn:hover {
    background-color: #1ebe5b;
    box-shadow: 0 10px 20px rgba(30,180,70,0.7);
}

footer {
    text-align: center;
    color: #999999;
    font-size: 0.9rem;
    padding: 20px 0 10px 0;
    margin-top: 40px;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# Header con logo y título
st.markdown("""
<div class="header">
    <h1>Tienda Takana</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar con filtros
st.sidebar.header("Filtros de búsqueda")

# Obtener productos de la API
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    productos = response.json()
except Exception as e:
    st.error(f"Error al obtener productos: {e}")
    productos = []

# Obtener lista única de categorías
categorias = sorted({cat for p in productos for cat in p.get("categories", [])})

# Filtros de categoría y nombre
categoria_seleccionada = st.sidebar.selectbox("Selecciona categoría", options=["Todas"] + categorias)
nombre_buscar = st.sidebar.text_input("Buscar por nombre")

# Obtener precios para filtro
precios = [p.get("price", 0) for p in productos if p.get("price") is not None]

if precios:
    precio_min = min(precios)
    precio_max = max(precios)
    if precio_min == precio_max:
        precio_max = precio_min + 1.0
else:
    precio_min, precio_max = 0, 1000

rango_precio = st.sidebar.slider(
    "Rango de precio",
    float(precio_min),
    float(precio_max),
    (float(precio_min), float(precio_max))
)

# Función para filtrar productos
def filtrar_productos(productos, categoria, nombre, precio_min, precio_max):
    filtrados = []
    nombre = nombre.lower().strip()
    for p in productos:
        if categoria != "Todas" and categoria not in p.get("categories", []):
            continue
        if nombre and nombre not in p.get("name", "").lower():
            continue
        precio = p.get("price")
        if precio is None or precio < precio_min or precio > precio_max:
            continue
        filtrados.append(p)
    return filtrados

productos_filtrados = filtrar_productos(productos, categoria_seleccionada, nombre_buscar, rango_precio[0], rango_precio[1])

# Mostrar productos filtrados en tarjetas con 3 columnas por fila
if productos_filtrados:
    num_cols = 3  # columnas por fila
    for i in range(0, len(productos_filtrados), num_cols):
        cols = st.columns(num_cols)
        for j, producto in enumerate(productos_filtrados[i:i+num_cols]):
            if not producto.get("name") or producto.get("price") is None:
                continue

            image_url = producto.get("imageUrl")
            full_image_url = BASE_URL + image_url if image_url else None

            with cols[j]:
                nombre = producto.get("name", "")
                descripcion = producto.get("description", "Sin descripción disponible.")
                categorias = ", ".join(producto.get("categories", []))
                precio = producto.get("price", "N/A")

                mensaje = (
                    f"Hola, me interesa el producto:\n"
                    f"Nombre: {nombre}\n"
                    f"Descripción: {descripcion}\n"
                    f"Categoría(s): {categorias}\n"
                    f"Precio: ${precio}"
                )
                wa_link = "https://wa.me/2615586001?text=" + urllib.parse.quote(mensaje)

                st.markdown(f'''
                <div class="product-container">
                    <div class="product-image">
                        {f'<img src="{full_image_url}" alt="{nombre}">' if full_image_url else 'Imagen no disponible'}
                    </div>
                    <div class="product-details">
                        <h2>{nombre}</h2>
                        <div class="price">Precio: ${precio}</div>
                        {f'<div class="kg-info">Precio por kilo: ${producto["pricePerKilo"]}</div>' if producto.get("pricePerKilo") else ''}
                        <div class="description">{descripcion}</div>
                        <a href="{wa_link}" class="whatsapp-btn" target="_blank" rel="noopener noreferrer">Pedir por WhatsApp</a>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

else:
    st.info("No hay productos que coincidan con los filtros.")

# Footer
st.markdown("""
<footer>
    &copy; 2025 TiendaInventario - Contacto: +54 261 5586001
</footer>
""", unsafe_allow_html=True)
