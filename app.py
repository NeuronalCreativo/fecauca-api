from flask import Flask, request, jsonify
import psycopg2
import google.generativeai as genai

app = Flask(__name__)

# Configura la API Key de Gemini AI
genai.configure(api_key='AIzaSyBO-KTGJqkYP2mn6PiR83goA2VNpzN1HQk')

# Conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        dbname="d2unpgeivgeb1f",
        user="u68u55gkus3ja5",
        password="p29ee0e0aa8361191a5e959813a56b5687c6e2028227980a45ca18fdc586d2bdd",
        host="c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    return conn

# Función para buscar productos en la base de datos
def buscar_productos(consulta):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE nombre ILIKE %s", (f'%{consulta}%',))
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos

# Endpoint para manejar solicitudes de AutoReply
@app.route('/autoreply', methods=['POST'])
def autoreply():
    # Obtener los datos del mensaje
    data = request.json
    sender_message = data.get('senderMessage')  # Mensaje enviado por el usuario
    sender_name = data.get('senderName')       # Nombre del remitente

    # Usar Gemini AI para procesar el mensaje
    respuesta_gemini = generar_respuesta_gemini(sender_message)

    # Si Gemini AI sugiere buscar en la base de datos, hazlo
    if "buscar" in respuesta_gemini.lower() or "producto" in respuesta_gemini.lower():
        productos = buscar_productos(sender_message)
        if productos:
            respuesta_gemini = "Aquí tienes los productos que encontré:\n"
            for producto in productos:
                respuesta_gemini += f"- {producto[1]} (Código: {producto[0]}, Precio: ${producto[3]:.2f})\n"
        else:
            respuesta_gemini = "No encontré productos que coincidan con tu búsqueda. ¿Necesitas ayuda con algo más?"

    # Devolver la respuesta en el formato que espera AutoReply
    return jsonify({
        "data": [
            {
                "message": respuesta_gemini
            }
        ]
    })

# Función para generar respuestas usando Gemini AI
def generar_respuesta_gemini(mensaje):
    model = genai.GenerativeModel('gemini-pro')  # Usa el modelo adecuado
    response = model.generate_content(mensaje)
    return response.text

if __name__ == '__main__':
    app.run(debug=True)