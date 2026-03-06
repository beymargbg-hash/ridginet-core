import sqlite3
from flask import Flask, request, jsonify
import routeros_api

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS LOCAL ---
def init_db():
    conn = sqlite3.connect('elohim_system.db')
    cursor = conn.cursor()
    # Tabla de abonados: vincula MikroTik con la App
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abonados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            dni TEXT UNIQUE,
            ip_mikrotik TEXT,
            perfil_mikrotik TEXT,
            estado TEXT DEFAULT 'Activo',
            ultimo_pago TEXT,
            metodo_pago TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- CONEXIÓN DINÁMICA AL MIKROTIK ---
def get_mt_connection(host, user, password):
    try:
        connection = routeros_api.RouterOsApiPool(host, username=user, password=password, plaintext_login=True)
        return connection.get_api()
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# --- LÓGICA DE SINCRONIZACIÓN (BARRIDO INICIAL) ---
@app.route('/api/sincronizar', methods=['POST'])
def sincronizar_wisp():
    data = request.json
    api = get_mt_connection(data['host'], data['user'], data['pass'])
    
    if not api:
        return jsonify({"error": "No se pudo conectar al MikroTik"}), 400

    # 1. Intentar leer de Secrets (PPPoE)
    clientes_encontrados = []
    try:
        secrets = api.get_resource('/ppp/secret').get()
        for s in secrets:
            clientes_encontrados.append({
                "nombre": s.get('comment', s['name']),
                "user_mt": s['name'],
                "tipo": "PPPoE"
            })
    except: pass

    # 2. Intentar leer de Simple Queues (IP Fija)
    try:
        queues = api.get_resource('/queue/simple').get()
        for q in queues:
            clientes_encontrados.append({
                "nombre": q.get('comment', q['name']),
                "ip": q['target'],
                "tipo": "Queue"
            })
    except: pass

    # GUARDAR EN DB LOCAL (Si no existen)
    conn = sqlite3.connect('elohim_system.db')
    cursor = conn.cursor()
    for c in clientes_encontrados:
        cursor.execute('INSERT OR IGNORE INTO abonados (nombre, ip_mikrotik) VALUES (?, ?)', 
                       (c['nombre'], c.get('ip') or c.get('user_mt')))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "Sincronización completada", "total": len(clientes_encontrados)})

# --- LÓGICA DE LOGIN PARA CLIENTES (DNI) ---
@app.route('/api/login_cliente', methods=['POST'])
def login_cliente():
    data = request.json # Recibe DNI del HTML
    dni = data.get('dni')
    
    conn = sqlite3.connect('elohim_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM abonados WHERE dni = ?', (dni,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "user": {"nombre": user[1], "estado": user[5]}})
    else:
        return jsonify({"status": "error", "message": "DNI no registrado"}), 404

# --- COMANDOS DE CORTE Y RECONEXIÓN ---
@app.route('/api/control', methods=['POST'])
def control_servicio():
    data = request.json # accion: 'corte' o 'reconectar'
    # Aquí se ejecuta el comando específico según el método detectado
    # Ejemplo para Address List (Corte por Firewall)
    # api.get_resource('/ip/firewall/address-list').add(list="MOROSOS", address=data['ip'])
    return jsonify({"status": f"Acción {data['accion']} enviada al router"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
