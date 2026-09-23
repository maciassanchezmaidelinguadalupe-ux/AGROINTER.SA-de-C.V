import os
import sqlite3
import io
from datetime import datetime
from flask import (Flask, render_template_string, request,
                    redirect, url_for, session, flash, jsonify, send_file)

# Importaciones para generación de PDF con ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

app = Flask(__name__)
app.secret_key = 'agrointer_secret_key_2026'

# BASE DE DATOS E INICIALIZACION
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agrointer_calidad.db')

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# LISTAS INICIALES
LISTAS_INICIALES = {
    'proveedores': [
        "ACEITES, GRASAS Y DERIVADOS, S.A DE C.V.", "AGRICULTORES UNIDOS DE EMANCIPACION",
        "AGROINDUSTRIAS DE BUENAVENTURA", "AGROINTER", "AGROPECUARIA DE GRANOS E INSUMOS",
        "AGROPECUARIA EL DUQUE", "AGROPECUARIA EL OBRAJE", "AGROPECUARIA LA CAPILLA DEL NORESTE",
        "AGROPECUARIA VILLA DE GUADALUPE", "AGROPECUARIA VIÑEDOS SALVADOR", "AGYDSA",
        "ANGELICA MACIAS", "BARTLETT", "BODEGA AGS", "BUENAVENTURA", "CARGILL DE MEXICO",
        "COFCO AGRI MEXICO", "COMERCIALIZADORA AL GRANO", "DISTRIBUIDORA PREMIO",
        "EDITH MIRELLA RAMIREZ", "EDITH MIRELLA RMZ MORA", "EDUARDO PEREZ", "EFREN HDZ VAZQUEZ",
        "EFREN HERNANDEZ", "ELPIDIO", "GARCIA MARTINEZ", "ESTABLO LA FORTUNA",
        "FAB. DE JABON LA CORONA", "FIBRAS Y SEMILLAS DE CHIHUAHUA", "FORRAJERA SAN RAFAEL",
        "FORRAJES LOS CHAPETEADOS", "FORRAJES BAGO", "FORRAJES CAMPOS", "FORRAJES CHAPETEADOS",
        "FORRAJES GUTIERREZ", "FRACCION DE LA TRINIDAD", "GRANEROS SAN JUAN",
        "GRANOS Y SERVICIOS INTEGRALES", "GUADALUPE HERRERA ESPARZA", "HORACIO LUQUE",
        "INDUSTRIAL DE OLEAGINOSAS", "ISRAEL PEREZ GUTIERREZ", "JESUS VALDIVIA", "JESUS VARELA",
        "JUAN CARLOS RODRIGUEZ", "JUAN JOSE DE LEON GALAVIZ", "JULIO CESAR PADILLA",
        "JUMANDI GROUP", "LECHERA Y FORRAJES SAN JOSE", "LUIS LOERA", "MANUEL GUTIERREZ",
        "MAQUILADORA DE OLEAGINOSAS", "MARTIN CASTELLANOS", "MATANUZKA", "MERCADERES AGROPECUARIOS",
        "MERCATAM", "MIELES Y DERIVADOS NACIONALES", "MIGUEL CARDENAS", "MIGUEL VAZQUEZ",
        "NICOLAS VALDIVIA", "NUTRILAG, S.A. de C.V.", "PELSA AGROPECUARIA", "PRIMOS AND COUSINS",
        "PROAN", "PROCESADORA DE ALIMENTOS PARA GANADO", "PROCESADORA DE ALIMENTOS PARA GANADO SA DE CV",
        "PRODUCCION LECHERA LA MERCED", "PRODUCTOS AGRICOLAS MATANUZKA", "PROMOTORA DE LA GANADERIA SUSTENTABLE",
        "PRONAIN", "RANCHO ALVAREZ JIMENEZ", "ROBERTO RAFAEL REYNOSO MANCILLA", "ROSALBA PADILLA GALLO",
        "SCOULAR", "SCOULER DE MEXICO", "SERVIGRANOS PAJI", "UNIDAD DE PRODUCCION RURAL SANTA TERESA",
        "VGC GRANOS", "VITERRA MEXICO SA DE CV", "YUME"
    ],
    'choferes': [
        "Antonio Esparza", "Benjamin Marquez", "Carlos Alberto Lozano Lozano", "Daniel Candela",
        "Derian Avila", "Diego Lona", "Erik Castañeda", "Fabian Macias", "Fernando Hernandez Orozco",
        "Gerardo de Luna", "Guadalupe Jimenez", "Ignacio Olvera Rodriguez", "Isaac Lara",
        "Israel Perez", "Jesus Olvera", "Jesus Ornelas", "Jorge Ortiz", "Jose Diego de la Cruz",
        "Juan Antonio Alcala", "Juan Jose Romo de Anda", "Juan Manuel Gaytan Ramos", "Leobardo Martinez",
        "Leonel Juarez", "Luis Alberto Perez", "Luis Antonio Alcala", "Luis Fernando Orozco",
        "Mario Gallegos", "Martin Luevano Robles", "Miguel Angel Flores", "Misael Gutierrez",
        "Nicanor Vazquez", "Orlando Lozano", "Pepe Gomez", "Ponciano Vargas Hermosillo",
        "Rafael Orozco", "Ramses Navarro", "Roberto Esparza", "Rolando Perez", "Saul Gonzalez",
        "Silvino Martinez"
    ],
    'placas': [
        "05-AB-3V", "07-BD-7V", "07-BG-8B", "08-AH-5J", "12-BD-7W", "16-AD-2U", "17-AG-9P", "23-BD-9U",
        "238-EN-5", "24-BD-9U", "27-BD-5X", "31-AK-7G", "36-BD-4V", "38-AE-6F", "41-BJ-2X", "51-BL-8W",
        "52-BL-8W", "53-BL-8W", "54-AM-7R", "55-AM-7R", "58-AB-8H", "59-AB-8H", "59-AZ-7A", "61-BN-4G",
        "66-AK-1Y", "67-AF-1K", "680-ET-4", "75-BN-7F", "76-BN-7F", "77-BN-7F", "79-AZ-8A", "80-AZ-3B",
        "82-BN-4G", "91-AU-4Y", "92-AP-7F", "99-AK-7T", "HX-1365A", "HZ-32-53A", "JC-18-35B", "JK-81-28-A"
    ],
    'tipos_vehiculo': [
        "Plataforma", "Tolva Freightliner M2", "Tolva KW T370", "Tolva KW T480", "Torton",
        "Torton KW", "Torton Piso Vivo Freightliner M2", "Torton Piso Vivo KW T370", "Trailer",
        "Trailer Cascadia Freightliner", "Trailer Columbia Freightliner", "Trailer Full Cascadia Fr.",
        "Trailer KW", "Trailer KW T660", "Trailer KW T680", "Trailer Prostar International"
    ],
    'inspectores': [
        "DIANA GARCIA", "CARMEN RODRIGUEZ", "MAIDELIN MACIAS", "FLOR ESCOBEDO"
    ]
}

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recepciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE NOT NULL,
        fecha_hora TEXT NOT NULL,
        proveedor TEXT NOT NULL,
        chofer TEXT NOT NULL,
        placas TEXT NOT NULL,
        tipo_vehiculo TEXT NOT NULL,
        peso_bruto REAL,
        tara REAL,
        peso_neto REAL,
        peso_especifico REAL,
        humedad REAL,
        impurezas REAL,
        grano_quebrado REAL,
        danio_hongos REAL,
        danio_insectos REAL,
        danio_calor REAL,
        danio_podrido REAL,
        danio_otros REAL,
        danio_total REAL,
        materia_extrana REAL,
        color TEXT,
        olor TEXT,
        infestacion TEXT,
        equipo_bph TEXT DEFAULT 'BPH-001',
        equipo_hm TEXT DEFAULT 'HM-001',
        dictamen TEXT NOT NULL,
        fuera_especificacion TEXT,
        inspector TEXT NOT NULL,
        observaciones TEXT,
        confirmado INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opciones_listas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        valor TEXT NOT NULL,
        UNIQUE (categoria, valor)
    )
    """)
    for cat, lista in LISTAS_INICIALES.items():
        for val in lista:
            cursor.execute("INSERT OR IGNORE INTO opciones_listas (categoria, valor) VALUES (?,?)", (cat, val))
    conn.commit()
    conn.close()

init_db()

# --- PLANTILLA HTML (SIN AUTOLLENADO DE IA) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agrointer - Control de Calidad</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
:root {
  --verde-fuerte: #1b4332;
  --verde-medio: #2d6a4f;
  --verde-claro: #52b788;
  --verde-bajo: #d8f3dc;
  --verde-acento: #74c69d;
  --blanco: #ffffff;
  --gris-fondo: #f8f9fa;
}
body {
  background-color: var(--gris-fondo);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}
.navbar-custom {
  background: linear-gradient(135deg, var(--verde-fuerte) 0%, var(--verde-medio) 100%);
  padding: 15px 30px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.brand-title {
  color: var(--blanco);
  font-weight: 700;
  font-size: 1.4rem;
  letter-spacing: 0.5px;
}
.brand-subtitle {
  color: var(--verde-bajo);
  font-size: 0.85rem;
  display: block;
}
.logo-header {
  max-height: 55px;
  background-color: var(--blanco);
  padding: 4px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.card-custom {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  background: var(--blanco);
  margin-bottom: 25px;
}
.card-header-custom {
  background-color: var(--verde-medio);
  color: var(--blanco);
  border-radius: 12px 12px 0 0 !important;
  padding: 12px 20px;
  font-weight: 600;
}
.btn-agro {
  background-color: var(--verde-medio);
  color: var(--blanco);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.btn-agro:hover {
  background-color: var(--verde-fuerte);
  color: var(--blanco);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.btn-agro-light {
  background-color: var(--verde-bajo);
  color: var(--verde-fuerte);
  border: 1px solid var(--verde-claro);
  font-weight: 600;
}
.btn-agro-light:hover {
  background-color: var(--verde-claro);
  color: var(--blanco);
}
.metric-card {
  background: linear-gradient(135deg, var(--verde-bajo) 0%, #ffffff 100%);
  border-left: 5px solid var(--verde-medio);
  padding: 20px;
  border-radius: 8px;
}
.metric-val {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--verde-fuerte);
}
.status-badge-accepted {
  background-color: #d4edda;
  color: #155724;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
}
.status-badge-rejected {
  background-color: #f8d7da;
  color: #721c24;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
}
.login-box {
  max-width: 420px;
  margin: 80px auto;
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-top: 6px solid var(--verde-fuerte);
}
</style>
</head>
<body>
{% if not session.get('logged_in') %}
<div class="container">
  <div class="login-box text-center">
    <img src="{{ url_for('static', filename='logo.png') }}" alt="Agrointer Logo" style="max-width: 180px;" class="mb-3" onerror="this.src='https://via.placeholder.com/180x60?text=AGROINTER'">
    <h4 class="fw-bold mb-1" style="color: var(--verde-fuerte);">Control de Calidad</h4>
    <p class="text-muted small mb-4">Agroingredientes Internacionales S.A. de C.V.</p>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="alert alert-danger py-2 mb-3" role="alert">
          {{ messages[0] }}
        </div>
      {% endif %}
    {% endwith %}
    <form method="POST" action="{{ url_for('login') }}">
      <div class="mb-3 text-start">
        <label class="form-label font-weight-bold">Contraseña de Acceso:</label>
        <div class="input-group">
          <span class="input-group-text"><i class="fas fa-lock"></i></span>
          <input type="password" name="password" class="form-control" placeholder="Ingrese clave..." required>
        </div>
      </div>
      <button type="submit" class="btn btn-agro w-100 mt-2">
        <i class="fas fa-sign-in-alt me-2"></i>Ingresar al Sistema
      </button>
    </form>
  </div>
</div>
{% else %}
<nav class="navbar navbar-custom sticky-top">
  <div class="container-fluid">
    <div>
      <span class="brand-title"><i class="fas fa-seedling me-2"></i>AGROINTER</span>
      <span class="brand-subtitle">Módulo de Control de Calidad y Muestreo de Granos</span>
    </div>
    <div class="d-flex align-items-center gap-3">
      <a href="{{ url_for('logout') }}" class="btn btn-sm btn-outline-light me-2"><i class="fas fa-power-off me-1"></i>Salir</a>
      <img src="{{ url_for('static', filename='logo.png') }}" alt="Agrointer Logo" class="logo-header" onerror="this.src='https://via.placeholder.com/150x50?text=AGROINTER'">
    </div>
  </div>
</nav>

<div class="container-fluid py-4 px-4">
  <div class="row mb-4">
    <div class="col-12 d-flex gap-2">
      <a href="#dashboard" class="btn btn-agro-light"><i class="fas fa-chart-line me-2"></i>Dashboard</a>
      <a href="#nuevo" class="btn btn-agro"><i class="fas fa-plus-circle me-2"></i>Nueva Recepción</a>
      <a href="#historial" class="btn btn-agro-light"><i class="fas fa-history me-2"></i>Historial de Cargas</a>
    </div>
  </div>

  <div id="dashboard" class="row mb-4">
    <div class="col-12 mb-2">
      <h5 class="fw-bold" style="color: var(--verde-fuerte);"><i class="fas fa-tachometer-alt me-2"></i>Resumen Operativo de Calidad</h5>
    </div>
    <div class="col-md-3">
      <div class="card-custom metric-card">
        <small class="text-muted fw-bold">CARGAS TOTALES</small>
        <div class="metric-val">{{ total_cargas }}</div>
        <small class="text-success"><i class="fas fa-truck"></i> Registradas en sistema</small>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card-custom metric-card" style="border-left-color: #28a745;">
        <small class="text-muted fw-bold">ACEPTADAS</small>
        <div class="metric-val text-success">{{ aceptadas }}</div>
        <small class="text-muted">Cumplen especificación</small>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card-custom metric-card" style="border-left-color: #dc3545;">
        <small class="text-muted fw-bold">RECHAZADAS</small>
        <div class="metric-val text-danger">{{ rechazadas }}</div>
        <small class="text-danger"><i class="fas fa-exclamation-triangle"></i> Fuera de norma</small>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card-custom metric-card">
        <small class="text-muted fw-bold">HUMEDAD PROMEDIO</small>
        <div class="metric-val">{{ humedad_prom }}%</div>
        <small class="text-muted">Norma NMX-FF-034: ≤14.0%</small>
      </div>
    </div>
  </div>

  <div id="nuevo" class="card card-custom">
    <div class="card-header card-header-custom d-flex justify-content-between align-items-center">
      <span><i class="fas fa-vial me-2"></i>Captura de Análisis de Calidad y Muestreo de Maíz</span>
      <span class="badge bg-light text-dark">Folio Automático</span>
    </div>
    <div class="card-body">
      <form action="{{ url_for('guardar_analisis') }}" method="POST" id="form-analisis">
        <div class="row g-3 mb-4">
          <div class="col-12"><h6 class="fw-bold border-bottom pb-2" style="color: var(--verde-fuerte);">1. Información de Vehículo y Recepción</h6></div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Proveedor</label>
            <div class="input-group">
              <input list="dl_proveedores" id="input_proveedor" name="proveedor" class="form-control" placeholder="Escriba para buscar..." required>
              <datalist id="dl_proveedores">
                {% for item in listas.proveedores %}
                <option value="{{ item }}">
                {% endfor %}
              </datalist>
              <button type="button" class="btn btn-outline-secondary" title="Agregar nuevo" onclick="agregarOpcion('proveedores', 'input_proveedor')"><i class="fas fa-plus text-success"></i></button>
              <button type="button" class="btn btn-outline-secondary" title="Eliminar seleccionado" onclick="eliminarOpcion('proveedores', 'input_proveedor')"><i class="fas fa-trash text-danger"></i></button>
            </div>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Chofer</label>
            <div class="input-group">
              <input list="dl_choferes" id="input_chofer" name="chofer" class="form-control" placeholder="Escriba para buscar..." required>
              <datalist id="dl_choferes">
                {% for item in listas.choferes %}
                <option value="{{ item }}">
                {% endfor %}
              </datalist>
              <button type="button" class="btn btn-outline-secondary" title="Agregar nuevo" onclick="agregarOpcion('choferes', 'input_chofer')"><i class="fas fa-plus text-success"></i></button>
              <button type="button" class="btn btn-outline-secondary" title="Eliminar seleccionado" onclick="eliminarOpcion('choferes', 'input_chofer')"><i class="fas fa-trash text-danger"></i></button>
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-bold">Placas</label>
            <div class="input-group">
              <input list="dl_placas" id="input_placas" name="placas" class="form-control" placeholder="Buscar..." required>
              <datalist id="dl_placas">
                {% for item in listas.placas %}
                <option value="{{ item }}">
                {% endfor %}
              </datalist>
              <button type="button" class="btn btn-outline-secondary" title="Agregar" onclick="agregarOpcion('placas', 'input_placas')"><i class="fas fa-plus text-success"></i></button>
              <button type="button" class="btn btn-outline-secondary" title="Eliminar" onclick="eliminarOpcion('placas', 'input_placas')"><i class="fas fa-trash text-danger"></i></button>
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-bold">Tipo Vehículo</label>
            <div class="input-group">
              <input list="dl_tipos_vehiculo" id="input_tipo_vehiculo" name="tipo_vehiculo" class="form-control" placeholder="Buscar..." required>
              <datalist id="dl_tipos_vehiculo">
                {% for item in listas.tipos_vehiculo %}
                <option value="{{ item }}">
                {% endfor %}
              </datalist>
              <button type="button" class="btn btn-outline-secondary" title="Agregar" onclick="agregarOpcion('tipos_vehiculo', 'input_tipo_vehiculo')"><i class="fas fa-plus text-success"></i></button>
              <button type="button" class="btn btn-outline-secondary" title="Eliminar" onclick="eliminarOpcion('tipos_vehiculo', 'input_tipo_vehiculo')"><i class="fas fa-trash text-danger"></i></button>
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-bold">Peso Neto (Kg)</label>
            <input type="number" step="0.01" id="input_peso_neto" name="peso_neto" class="form-control" placeholder="18600">
          </div>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-12"><h6 class="fw-bold border-bottom pb-2" style="color: var(--verde-fuerte);">2. Parámetros Métricos (NMX-FF-034/NMX-FF-119)</h6></div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Peso Específico (g/l)</label>
            <div class="input-group">
              <input type="number" step="0.1" id="input_peso_especifico" name="peso_especifico" class="form-control" placeholder="72.4">
              <span class="input-group-text">g/l</span>
            </div>
            <span class="form-text extra-small">Muestreo Agrointer: gramos por litro</span>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Humedad (%)</label>
            <div class="input-group">
              <input type="number" step="0.1" id="input_humedad" name="humedad" class="form-control" placeholder="13.8">
              <span class="input-group-text">%</span>
            </div>
            <span class="form-text extra-small">Límite norma: ≤ 14.0%</span>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Impurezas (%)</label>
            <div class="input-group">
              <input type="number" step="0.1" id="input_impurezas" name="impurezas" class="form-control" placeholder="1.7">
              <span class="input-group-text">%</span>
            </div>
            <span class="form-text extra-small">Límite: ≤ 15.0%</span>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Grano Quebrado (%)</label>
            <div class="input-group">
              <input type="number" step="0.1" id="input_grano_quebrado" name="grano_quebrado" class="form-control" placeholder="3.4">
              <span class="input-group-text">%</span>
            </div>
          </div>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-12"><h6 class="fw-bold border-bottom pb-2" style="color: var(--verde-fuerte);">3. Categorización de Grano Dañado (%)</h6></div>
          <div class="col-md-2">
            <label class="form-label small">Hongos (%)</label>
            <input type="number" step="0.01" id="input_danio_hongos" name="danio_hongos" class="form-control" value="0">
          </div>
          <div class="col-md-2">
            <label class="form-label small">Insectos (%)</label>
            <input type="number" step="0.01" id="input_danio_insectos" name="danio_insectos" class="form-control" value="0">
          </div>
          <div class="col-md-2">
            <label class="form-label small">Calor (%)</label>
            <input type="number" step="0.01" id="input_danio_calor" name="danio_calor" class="form-control" value="0">
          </div>
          <div class="col-md-2">
            <label class="form-label small">Podrido (%)</label>
            <input type="number" step="0.01" id="input_danio_podrido" name="danio_podrido" class="form-control" value="0">
          </div>
          <div class="col-md-2">
            <label class="form-label small">Otros Daños (%)</label>
            <input type="number" step="0.01" id="input_danio_otros" name="danio_otros" class="form-control" value="0">
          </div>
          <div class="col-md-2">
            <label class="form-label small">Materia Extraña (%)</label>
            <input type="number" step="0.01" id="input_materia_extrana" name="materia_extrana" class="form-control" value="0">
          </div>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-12"><h6 class="fw-bold border-bottom pb-2" style="color: var(--verde-fuerte);">4. Análisis Organoléptico y Datos Operativos</h6></div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Color</label>
            <select id="input_color" name="color" class="form-select">
              <option>Característico (Amarillo/Blanco)</option>
              <option>Ligeramente decolorado</option>
              <option>Fuera de color</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Olor</label>
            <select id="input_olor" name="olor" class="form-select">
              <option>Normal / Característico</option>
              <option>Humedad / Moho</option>
              <option>Fermentado / Comercial</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Infestación</label>
            <select id="input_infestacion" name="infestacion" class="form-select">
              <option value="No">No (Libre de plaga)</option>
              <option value="Si">Sí (Insecto vivo)</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold">Inspector / Operador</label>
            <div class="input-group">
              <input list="dl_inspectores" id="input_inspector" name="inspector" class="form-control" placeholder="Buscar..." required>
              <datalist id="dl_inspectores">
                {% for item in listas.inspectores %}
                <option value="{{ item }}">
                {% endfor %}
              </datalist>
              <button type="button" class="btn btn-outline-secondary" title="Agregar" onclick="agregarOpcion('inspectores', 'input_inspector')"><i class="fas fa-plus text-success"></i></button>
              <button type="button" class="btn btn-outline-secondary" title="Eliminar" onclick="eliminarOpcion('inspectores', 'input_inspector')"><i class="fas fa-trash text-danger"></i></button>
            </div>
          </div>
          <div class="col-12">
            <label class="form-label small fw-bold">Observaciones del Análisis</label>
            <textarea id="input_observaciones" name="observaciones" class="form-control" rows="2" placeholder="Comentarios adicionales sobre el muestreo..."></textarea>
          </div>
        </div>

        <div class="d-flex justify-content-end align-items-center gap-3">
          <div class="input-group" style="max-width: 320px;">
            <input type="text" id="buscar_ticket_input" class="form-control" placeholder="Buscar ticket (folio)...">
            <button type="button" class="btn btn-warning fw-bold text-dark" onclick="buscarTicket()"><i class="fas fa-search me-1"></i> Buscar</button>
          </div>
          <button type="submit" class="btn btn-agro btn-lg px-5">
            <i class="fas fa-check-circle me-2"></i> Guardar análisis
          </button>
        </div>
      </form>
    </div>
  </div>

  <div id="historial" class="card card-custom">
    <form id="form-eliminar-seleccionados" action="{{ url_for('eliminar_seleccionados') }}" method="POST">
      <div class="card-header card-header-custom d-flex justify-content-between align-items-center">
        <span><i class="fas fa-list-alt me-2"></i>Historial de Recepciones y Control de Auditoría</span>
        <button type="submit" id="btn-eliminar-masivo" class="btn btn-danger btn-sm text-white fw-bold" disabled onclick="return confirmarEliminacion();">
          <i class="fas fa-trash-alt me-1"></i> Eliminar Seleccionados (<span id="contador-seleccionados">0</span>)
        </button>
      </div>
      <div class="card-body table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th style="width: 40px;" class="text-center">
                <input type="checkbox" id="select-all" class="form-check-input" onchange="toggleSelectAll(this)">
              </th>
              <th>Folio Único</th>
              <th>Fecha/Hora</th>
              <th>Proveedor</th>
              <th>Humedad</th>
              <th>P. Específico</th>
              <th>Impurezas</th>
              <th>Grano Dañado</th>
              <th>Dictamen</th>
              <th>Acciones / PDF</th>
            </tr>
          </thead>
          <tbody>
            {% for r in recepciones %}
            <tr>
              <td class="text-center">
                <input type="checkbox" name="folios_seleccionados" value="{{ r.folio }}" class="form-check-input row-checkbox" onchange="actualizarBotonEliminar()">
              </td>
              <td class="fw-bold text-danger">{{ r.folio }}</td>
              <td><small>{{ r.fecha_hora }}</small></td>
              <td>{{ r.proveedor }}</td>
              <td>{{ (r.humedad ~ '%') if r.humedad is not none else 'Pendiente' }}</td>
              <td>{{ r.peso_especifico }} g/l</td>
              <td>{{ (r.impurezas ~ '%') if r.impurezas is not none else 'Pendiente' }}</td>
              <td>{{ (r.danio_total ~ '%') if r.danio_total is not none else 'Pendiente' }}</td>
              <td>
                {% if r.dictamen == 'PENDIENTE' %}
                  <span class="badge bg-warning text-dark">PENDIENTE</span>
                {% elif r.dictamen == 'ACEPTADO' %}
                  <span class="status-badge-accepted"><i class="fas fa-check me-1"></i>ACEPTADO</span>
                {% else %}
                  <span class="status-badge-rejected" title="{{ r.fuera_especificacion }}"><i class="fas fa-times me-1"></i>RECHAZADO</span>
                {% endif %}
              </td>
              <td>
                <a href="{{ url_for('descargar_pdf', folio=r.folio) }}" class="btn btn-sm btn-agro-light">
                  <i class="fas fa-file-pdf text-danger me-1"></i> Reporte PDF
                </a>
              </td>
            </tr>
            {% else %}
            <tr>
              <td colspan="10" class="text-center text-muted py-4">No hay muestras registradas aún. Registre una arriba.</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </form>
  </div>
</div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleSelectAll(source) {
  const checkboxes = document.querySelectorAll('.row-checkbox');
  checkboxes.forEach(cb => cb.checked = source.checked);
  actualizarBotonEliminar();
}

function actualizarBotonEliminar() {
  const checkboxes = document.querySelectorAll('.row-checkbox:checked');
  const cantidad = checkboxes.length;
  const btn = document.getElementById('btn-eliminar-masivo');
  const contador = document.getElementById('contador-seleccionados');
  if (contador) contador.textContent = cantidad;
  if (btn) btn.disabled = (cantidad === 0);
  
  const selectAll = document.getElementById('select-all');
  const totalCheckboxes = document.querySelectorAll('.row-checkbox');
  if (selectAll && totalCheckboxes.length > 0) {
    selectAll.checked = (checkboxes.length === totalCheckboxes.length);
  }
}

function confirmarEliminacion() {
  const cantidad = document.querySelectorAll('.row-checkbox:checked').length;
  return confirm(`¿Está seguro de que desea eliminar permanentemente ${cantidad} registro(s) seleccionado(s)?`);
}

function agregarOpcion(categoria, inputId) {
  const val = document.getElementById(inputId).value.trim();
  if (!val) { alert("Ingrese un valor para agregar."); return; }
  fetch('/agregar_opcion', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({categoria: categoria, valor: val})
  }).then(res => res.json()).then(data => {
    if (data.status === 'ok') {
      alert("Opción agregada exitosamente.");
      location.reload();
    } else {
      alert(data.message || "Error al agregar.");
    }
  });
}

function eliminarOpcion(categoria, inputId) {
  const val = document.getElementById(inputId).value.trim();
  if (!val) { alert("Seleccione o escriba el valor exacto a eliminar."); return; }
  if (confirm(`¿Desea eliminar '${val}' de la lista?`)) {
    fetch('/eliminar_opcion', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({categoria: categoria, valor: val})
    }).then(res => res.json()).then(data => {
      if (data.status === 'ok') {
        alert("Opción eliminada.");
        location.reload();
      } else {
        alert(data.message || "Error al eliminar.");
      }
    });
  }
}

function buscarTicket() {
  const folio = document.getElementById('buscar_ticket_input').value.trim();
  if (!folio) { alert("Ingrese un número de ticket o folio."); return; }
  fetch(`/buscar_ticket?folio=${encodeURIComponent(folio)}`)
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        const r = data.registro;
        document.getElementById('input_proveedor').value = r.proveedor || "";
        document.getElementById('input_chofer').value = r.chofer || "";
        document.getElementById('input_placas').value = r.placas || "";
        document.getElementById('input_tipo_vehiculo').value = r.tipo_vehiculo || "";
        document.getElementById('input_peso_neto').value = r.peso_neto || "";
        document.getElementById('input_peso_especifico').value = r.peso_especifico || "";
        document.getElementById('input_humedad').value = r.humedad || "";
        document.getElementById('input_impurezas').value = r.impurezas || "";
        document.getElementById('input_grano_quebrado').value = r.grano_quebrado || "";
        document.getElementById('input_danio_hongos').value = r.danio_hongos || 0;
        document.getElementById('input_danio_insectos').value = r.danio_insectos || 0;
        document.getElementById('input_danio_calor').value = r.danio_calor || 0;
        document.getElementById('input_danio_podrido').value = r.danio_podrido || 0;
        document.getElementById('input_danio_otros').value = r.danio_otros || 0;
        document.getElementById('input_materia_extrana').value = r.materia_extrana || 0;
        document.getElementById('input_inspector').value = r.inspector || "";
        document.getElementById('input_observaciones').value = r.observaciones || "";
        alert(`Registro ${r.folio} encontrado y cargado en el formulario.`);
      } else {
        alert(data.message);
      }
    });
}
</script>
</body>
</html>
"""

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template_string(HTML_TEMPLATE)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recepciones ORDER BY id DESC")
    recepciones = cursor.fetchall()
    
    listas = {}
    for cat in ['proveedores', 'choferes', 'placas', 'tipos_vehiculo', 'inspectores']:
        cursor.execute("SELECT valor FROM opciones_listas WHERE categoria = ? ORDER BY valor ASC", (cat,))
        listas[cat] = [row['valor'] for row in cursor.fetchall()]
        
    total_cargas = len(recepciones)
    aceptadas = sum(1 for r in recepciones if r['dictamen'] == 'ACEPTADO')
    rechazadas = sum(1 for r in recepciones if r['dictamen'] == 'RECHAZADO')
    humedades = [r['humedad'] for r in recepciones if r['humedad'] is not None]
    humedad_prom = round(sum(humedades) / len(humedades), 1) if humedades else 0.0
    conn.close()
    
    return render_template_string(
        HTML_TEMPLATE,
        recepciones=recepciones,
        total_cargas=total_cargas,
        aceptadas=aceptadas,
        rechazadas=rechazadas,
        humedad_prom=humedad_prom,
        listas=listas
    )

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('password') == 'agrointer123':
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        flash('Contraseña de acceso incorrecta. Intente nuevamente.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/agregar_opcion', methods=['POST'])
def agregar_opcion():
    data = request.json
    categoria = data.get('categoria')
    valor = data.get('valor')
    if categoria and valor:
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO opciones_listas (categoria, valor) VALUES (?, ?)", (categoria, valor))
            conn.commit()
            conn.close()
            return jsonify({'status': 'ok'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Ese elemento ya existe en la lista.'})
    return jsonify({'status': 'error', 'message': 'Datos inválidos.'})

@app.route('/eliminar_opcion', methods=['POST'])
def eliminar_opcion():
    data = request.json
    categoria = data.get('categoria')
    valor = data.get('valor')
    if categoria and valor:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM opciones_listas WHERE categoria = ? AND valor = ?", (categoria, valor))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'message': 'Datos inválidos.'})

@app.route('/buscar_ticket', methods=['GET'])
def buscar_ticket():
    folio = request.args.get('folio', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recepciones WHERE folio LIKE ?", (f"%{folio}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'status': 'ok', 'registro': dict(row)})
    return jsonify({'status': 'error', 'message': 'No se encontró ningún ticket con ese folio.'})

@app.route('/guardar_analisis', methods=['POST'])
def guardar_analisis():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recepciones")
    count = cursor.fetchone()[0] + 1
    folio = f"CAL-2026-{count:06d}"
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    humedad = float(request.form.get('humedad', 0))
    peso_especifico = float(request.form.get('peso_especifico', 0))
    impurezas = float(request.form.get('impurezas', 0))
    grano_quebrado = float(request.form.get('grano_quebrado', 0))
    danio_hongos = float(request.form.get('danio_hongos', 0))
    danio_insectos = float(request.form.get('danio_insectos', 0))
    danio_calor = float(request.form.get('danio_calor', 0))
    danio_podrido = float(request.form.get('danio_podrido', 0))
    danio_otros = float(request.form.get('danio_otros', 0))
    danio_total = round(danio_hongos + danio_insectos + danio_calor + danio_podrido + danio_otros, 2)
    infestacion = request.form.get('infestacion')
    
    dictamen = "ACEPTADO"
    razones_rechazo = []
    
    if humedad > 14.0:
        dictamen = "RECHAZADO"
        razones_rechazo.append(f"Humedad ({humedad}%) excede el estándar de 14.0%")
    if peso_especifico < 71.0:
        dictamen = "RECHAZADO"
        razones_rechazo.append(f"Peso específico ({peso_especifico} g/l) por debajo de 71.0 g/l")
    if impurezas > 15.0:
        dictamen = "RECHAZADO"
        razones_rechazo.append(f"Impurezas ({impurezas}%) exceden el 15.0%")
    if infestacion == "Si":
        dictamen = "RECHAZADO"
        razones_rechazo.append("Presencia de plagas vivas detectada")
        
    fuera_especificacion = ", ".join(razones_rechazo) if razones_rechazo else "Dentro de norma"
    
    cursor.execute("""
    INSERT INTO recepciones (
        folio, fecha_hora, proveedor, chofer, placas, tipo_vehiculo, peso_neto,
        peso_especifico, humedad, impurezas, grano_quebrado, danio_hongos,
        danio_insectos, danio_calor, danio_podrido, danio_otros, danio_total,
        materia_extrana, color, olor, infestacion, dictamen, fuera_especificacion,
        inspector, observaciones, confirmado
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        folio, fecha_hora, request.form.get('proveedor'), request.form.get('chofer'),
        request.form.get('placas'), request.form.get('tipo_vehiculo'), request.form.get('peso_neto'),
        peso_especifico, humedad, impurezas, grano_quebrado, danio_hongos,
        danio_insectos, danio_calor, danio_podrido, danio_otros, danio_total,
        request.form.get('materia_extrana', 0), request.form.get('color'), request.form.get('olor'),
        infestacion, dictamen, fuera_especificacion, request.form.get('inspector'),
        request.form.get('observaciones')
    ))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/eliminar_seleccionados', methods=['POST'])
def eliminar_seleccionados():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    folios = request.form.getlist('folios_seleccionados')
    if folios:
        conn = get_db()
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM recepciones WHERE folio = ?", [(f,) for f in folios])
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/descargar_pdf/<folio>')
def descargar_pdf(folio):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recepciones WHERE folio = ?", (folio,))
    r = cursor.fetchone()
    conn.close()
    
    if not r:
        flash("Folio no encontrado.")
        return redirect(url_for('index'))
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1b4332'),
        alignment=1,
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2d6a4f'),
        spaceBefore=10,
        spaceAfter=5
    )
    normal_style = styles['Normal']
    elements = []
    
    elements.append(Paragraph("AGROINGREDIENTES INTERNACIONALES S.A. DE C.V.", title_style))
    elements.append(Paragraph(f"<b>REPORTE DE CONTROL DE CALIDAD Y MUESTREO</b><br/><b>Folio:</b> {r['folio']}", ParagraphStyle('Center', alignment=1, fontSize=11, spaceAfter=15)))
    elements.append(Paragraph("1. DATOS GENERALES Y VEHÍCULO", subtitle_style))
    
    data_gen = [
        [Paragraph("<b>Fecha y Hora:</b>", normal_style), Paragraph(str(r['fecha_hora']), normal_style),
         Paragraph("<b>Proveedor:</b>", normal_style), Paragraph(str(r['proveedor']), normal_style)],
        [Paragraph("<b>Chofer:</b>", normal_style), Paragraph(str(r['chofer']), normal_style), 
         Paragraph("<b>Placas:</b>", normal_style), Paragraph(str(r['placas']), normal_style)],
        [Paragraph("<b>Tipo Vehículo:</b>", normal_style), Paragraph(str(r['tipo_vehiculo']), normal_style),
         Paragraph("<b>Peso Neto:</b>", normal_style), Paragraph(f"{r['peso_neto'] or 0} Kg", normal_style)]
    ]
    t_gen = Table(data_gen, colWidths=[110, 160, 110, 160])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d8f3dc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_gen)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("2. PARÁMETROS DE CALIDAD (NMX-FF-034)", subtitle_style))
    data_cal = [
        ["Parámetro", "Resultado", "Espec. Norma", "Estado"],
        ["Humedad", f"{r['humedad']}%", "≤ 14.0%", "PENDIENTE" if r['dictamen'] == 'PENDIENTE' or r['humedad'] is None else ("RECHAZADO" if r['humedad'] > 14.0 else "ACEPTADO")],
        ["Peso Específico", f"{r['peso_especifico']} g/l", "≥ 71.0 g/l", "PENDIENTE" if r['dictamen'] == 'PENDIENTE' or r['peso_especifico'] is None else ("RECHAZADO" if r['peso_especifico'] < 71.0 else "ACEPTADO")],
        ["Impurezas", f"{r['impurezas']}%", "≤ 15.0%", "PENDIENTE" if r['dictamen'] == 'PENDIENTE' or r['impurezas'] is None else ("RECHAZADO" if r['impurezas'] > 15.0 else "ACEPTADO")],
        ["Grano Quebrado", f"{r['grano_quebrado']}%", "≤ 5.0%", "PENDIENTE" if r['dictamen'] == 'PENDIENTE' else "ACEPTADO"],
        ["Grano Dañado Total", f"{r['danio_total']}%", "≤ 5.0%", "PENDIENTE" if r['dictamen'] == 'PENDIENTE' else "ACEPTADO"],
    ]
    t_cal = Table(data_cal, colWidths=[150, 130, 130, 130])
    t_cal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d6a4f')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_cal)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("3. DICTAMEN FINAL", subtitle_style))
    color_dictamen = colors.HexColor('#155724') if r['dictamen'] == 'ACEPTADO' else colors.HexColor('#721c24')
    bg_dictamen = colors.HexColor('#d4edda') if r['dictamen'] == 'ACEPTADO' else colors.HexColor('#f8d7da')
    
    data_dict = [
        [Paragraph(f"<b>DICTAMEN FINAL:</b> <font color='{color_dictamen.hexval()}'>{r['dictamen']}</font>", ParagraphStyle('Dict', fontSize=12)),
         Paragraph(f"<b>Inspector:</b> {r['inspector']}", normal_style)],
        [Paragraph(f"<b>Observaciones / Fuera de Norma:</b> {r['fuera_especificacion'] or 'Ninguna'}", normal_style), ""]
    ]
    t_dict = Table(data_dict, colWidths=[350, 190])
    t_dict.setStyle(TableStyle([
        ('SPAN', (0,1), (1,1)),
        ('BACKGROUND', (0,0), (-1,-1), bg_dictamen),
        ('GRID', (0,0), (-1,-1), 0.5, color_dictamen),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_dict)
    
    doc.build(elements)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Reporte_{r['folio']}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)