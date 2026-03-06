import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuración de la ruta principal
@app.route('/')
def home():
    try:
        # Flask buscará automáticamente index.html dentro de la carpeta 'templates'
        return render_template('index.html')
    except Exception as e:
        return f"Error: No se encuentra el archivo index.html dentro de la carpeta templates. Detalle: {str(e)}", 404

# Ruta para recibir las API Keys del administrador
@app.route('/guardar-config', methods=['POST'])
def guardar_config():
    data = request.json
    api_key = data.get('api_key')
    ip_mikrotik = data.get('ip_mikrotik')
    
    # Aquí es donde el sistema usará database.py para guardar los datos
    # Por ahora, confirmamos que los datos llegaron correctamente
    if api_key and ip_mikrotik:
        return jsonify({"status": "success", "message": "Configuración guardada correctamente"}), 200
    else:
        return jsonify({"status": "error", "message": "Faltan datos obligatorios"}), 400

if __name__ == '__main__':
    # Usamos el puerto 5000 para que coincida con lo que configuraste en Railway Networking
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
