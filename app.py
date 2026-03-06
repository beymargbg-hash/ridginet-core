import os
from flask import Flask, render_template

# Definimos la app
app = Flask(__name__)

@app.route('/')
def home():
    # Railway buscará index.html dentro de la carpeta 'templates'
    return render_template('index.html')

if __name__ == '__main__':
    # Captura el puerto que Railway asigna (usamos 5000 por defecto)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
