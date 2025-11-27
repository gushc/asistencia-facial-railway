import os
import numpy as np
import face_recognition
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
import time
import csv
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

# Variables globales simplificadas
lista_codificaciones = []
lista_nombres = []
caras_registradas = set()
ultima_asistencia = ""
estado_camara = "detenida"

def inicializar_sistema():
    """Inicializa el sistema optimizado para Free Tier"""
    global lista_codificaciones, lista_nombres
    
    try:
        print("Inicializando sistema de reconocimiento facial...")
        
        # Crear datos de demostración SIN descargar archivos grandes
        print("Generando datos de demostración...")
        
        # Generar encoding de ejemplo para demostración
        try:
            # Crear una imagen sintética simple
            face_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            cods = face_recognition.face_encodings(face_image)
            
            if len(cods) > 0:
                lista_codificaciones.append(cods[0])
                lista_nombres.append("Usuario Demo")
                print("✅ Encoding de demostración creado")
            else:
                # Fallback: crear array dummy
                dummy_encoding = np.random.rand(128)
                lista_codificaciones.append(dummy_encoding)
                lista_nombres.append("Usuario Demo")
                print("✅ Encoding dummy creado (modo fallback)")
                
        except Exception as e:
            print(f"⚠️  Error creando encoding: {e}")
            # Último fallback
            lista_codificaciones.append(np.zeros(128))
            lista_nombres.append("Usuario Demo")
        
        print(f"✅ Sistema inicializado: {len(lista_codificaciones)} persona registrada")
        return True
        
    except Exception as e:
        print(f"❌ Error crítico en inicialización: {e}")
        return False

def registrar_asistencia(nombre):
    """Registra la asistencia en CSV"""
    global caras_registradas, ultima_asistencia
    
    if nombre != "Desconocido" and nombre not in caras_registradas:
        archivo_asistencia = "asistencia.csv"
        
        try:
            file_exists = os.path.exists(archivo_asistencia)
            
            with open(archivo_asistencia, "a", newline="", encoding='utf-8') as f:
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
    """Genera frames simulados para Free Tier"""
    global estado_camara
    
    estado_camara = "activa"
    frame_count = 0
    
    while estado_camara == "activa":
        try:
            # Crear frame simulado (sin OpenCV)
            height, width = 480, 640
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Fondo azul
            frame[:, :] = [50, 50, 120]
            
            # Texto informativo (simulado)
            textos = [
                "SISTEMA DE ASISTENCIA FACIAL - MODO DEMO",
                f"Personas registradas: {len(lista_codificaciones)}",
                f"Estado: {estado_camara.upper()}",
                "Sistema funcionando en Render Free Tier",
                "✅ Reconocimiento facial activo"
            ]
            
            # Simular detección periódica
            frame_count += 1
            if frame_count % 50 == 0 and len(lista_codificaciones) > 0:
                registrar_asistencia("Usuario Demo")
            
            # Codificar frame como JPEG (simplificado)
            from PIL import Image, ImageDraw, ImageFont
            pil_image = Image.fromarray(frame)
            draw = ImageDraw.Draw(pil_image)
            
            # Agregar texto
            y_offset = 50
            for texto in textos:
                draw.text((30, y_offset), texto, fill=(255, 255, 255))
                y_offset += 40
            
            # Convertir a bytes
            import io
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
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
        'message': 'Sistema de reconocimiento iniciado',
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
        if os.path.exists("asistencia.csv"):
            with open("asistencia.csv", "r", encoding='utf-8') as f:
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
    print("🚀 Iniciando Sistema de Asistencia Facial - Render Free Tier")
    
    if inicializar_sistema():
        print("✅ Sistema listo para usar")
    else:
        print("⚠️  Sistema en modo limitado")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)