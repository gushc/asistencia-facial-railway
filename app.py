import os
import numpy as np
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
import time
import csv
import warnings
from PIL import Image, ImageDraw
import io

warnings.filterwarnings("ignore")

app = Flask(__name__)

# Variables globales simplificadas
lista_codificaciones = []
lista_nombres = []
caras_registradas = set()
ultima_asistencia = ""
estado_camara = "detenida"

def inicializar_sistema():
    """Inicializa el sistema SIN face-recognition"""
    global lista_codificaciones, lista_nombres
    
    try:
        print("Inicializando sistema de demostración...")
        
        # Crear datos de demostración SIN face-recognition
        print("Generando datos de demostración...")
        
        # Encoding dummy para mantener la estructura
        dummy_encoding = np.random.rand(128)
        lista_codificaciones.append(dummy_encoding)
        lista_nombres.append("Usuario Demo")
        
        print("✅ Sistema de demostración inicializado")
        return True
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False

def registrar_asistencia(nombre):
    """Registra la asistencia en CSV"""
    global caras_registradas, ultima_asistencia
    
    if nombre != "Desconocido" and nombre not in caras_registradas:
        archivo_asistencia = "asistencia_version3.csv"
        
        try:
            file_exists = os.path.exists(archivo_asistencia)
            
            with open(archivo_asistencia, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Nombre", "Fecha", "Hora"])
                
                ahora = datetime.now()
                fecha = ahora.strftime("%d/%m/%Y")
                hora = ahora.strftime("%H:%M:%S")
                writer.writerow([nombre, fecha, hora])
            
            caras_registradas.add(nombre)
            ultima_asistencia = f"{nombre} - {fecha} {hora}"
            print(f"✅ Asistencia registrada: {ultima_asistencia}")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando asistencia: {e}")
            return False
    
    return False

def generar_frames():
    """Genera frames simulados SIN OpenCV"""
    global estado_camara
    
    estado_camara = "activa"
    frame_count = 0
    
    while estado_camara == "activa":
        try:
            # Crear frame simulado
            width, height = 640, 480
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Fondo azul
            frame[:, :] = [50, 50, 120]
            
            # Crear imagen PIL
            pil_image = Image.fromarray(frame)
            draw = ImageDraw.Draw(pil_image)
            
            # Texto informativo
            textos = [
                "SISTEMA DE ASISTENCIA FACIAL - MODO DEMO",
                f"Personas registradas: {len(lista_codificaciones)}",
                f"Estado: {estado_camara.upper()}",
                "Render Free Tier - Versión Ligera",
                "✅ Sistema funcionando correctamente"
            ]
            
            # Simular detección periódica
            frame_count += 1
            if frame_count % 30 == 0 and len(lista_nombres) > 0:
                registrar_asistencia(lista_nombres[0])
            
            # Agregar texto al frame
            y_offset = 50
            for texto in textos:
                draw.text((30, y_offset), texto, fill=(255, 255, 255))
                y_offset += 40
            
            # Agregar contador
            draw.text((30, height - 50), f"Frame: {frame_count}", fill=(255, 255, 255))
            
            # Convertir a bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format="JPEG", quality=85)
            frame_bytes = img_byte_arr.getvalue()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.2)  # 5 FPS para reducir carga
            
        except Exception as e:
            print(f"❌ Error en generación de frames: {e}")
            break
    
    estado_camara = "detenida"

# ================= RUTAS FLASK =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/iniciar_reconocimiento', methods=['POST'])
def iniciar_reconocimiento():
    global estado_camara
    estado_camara = "activa"
    return jsonify({
        'status': 'success',
        'message': 'Sistema de demostración iniciado',
        'personas_registradas': len(lista_codificaciones)
    })

@app.route('/detener_reconocimiento', methods=['POST'])
def detener_reconocimiento():
    global estado_camara
    estado_camara = "detenida"
    return jsonify({
        'status': 'success', 
        'message': 'Sistema detenido'
    })

@app.route('/obtener_asistencias')
def obtener_asistencias():
    try:
        asistencias = []
        if os.path.exists("asistencia_version3.csv"):
            with open("asistencia_version3.csv", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                asistencias = list(reader)
        return jsonify({'asistencias': asistencias})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/estado_sistema')
def estado_sistema():
    return jsonify({
        'estado_camara': estado_camara,
        'personas_registradas': len(lista_codificaciones),
        'ultima_asistencia': ultima_asistencia,
        'total_asistencias': len(caras_registradas)
    })

@app.route('/resultados')
def resultados():
    return render_template('resultados.html')

# ================= INICIALIZACIÓN =================

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Asistencia - Versión Ligera")
    
    if inicializar_sistema():
        print("✅ Sistema de demostración listo")
    else:
        print("⚠️  Sistema en modo limitado")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
