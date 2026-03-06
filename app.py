import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Asegúrate de que index.html esté dentro de la carpeta 'templates'
    return render_template('index.html')

if __name__ == '__main__':
    # Railway asigna un puerto dinámico, esto lo captura correctamente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
