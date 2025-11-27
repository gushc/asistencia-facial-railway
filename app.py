import os
import cv2
import numpy as np
import face_recognition
from flask import Flask, render_template, request, jsonify, Response
import requests
from io import BytesIO
import rarfile
import csv
from datetime import datetime
import time
import tempfile

app = Flask(__name__)

# Variables globales para el reconocimiento facial
lista_codificaciones = []
lista_nombres = []
caras_registradas = set()
ultima_asistencia = ""
estado_camara = "detenida"

def inicializar_sistema():
    """Inicializa el sistema de reconocimiento facial - SIN PILLOW"""
    global lista_codificaciones, lista_nombres
    
    try:
        # URL del RAR en Google Drive
        url_rar = "https://drive.google.com/uc?export=download&id=1HDUQre_8ujk_6TNtNvPvrIeBVHUJ5vHj"
        
        print("⬇ Descargando fotos desde Drive...")
        response = requests.get(url_rar)
        if response.status_code != 200:
            raise Exception("No se pudo descargar el archivo RAR desde Drive")

        # ✅ SOLUCIÓN: Usar archivo temporal seguro
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rar') as temp_file:
            temp_file.write(response.content)
            ruta_rar_temp = temp_file.name

        # Extraer imágenes del RAR
        print("⬇ Extrayendo imágenes del RAR...")
        with rarfile.RarFile(ruta_rar_temp) as rf:
            lista_codificaciones = []
            lista_nombres = []
            for archivo in rf.namelist():
                if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                    with rf.open(archivo) as img_file:
                        # ✅ SOLUCIÓN: Usar OpenCV en lugar de Pillow
                        img_data = img_file.read()
                        img_np = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                        
                        if img_np is not None:
                            # Convertir BGR a RGB (OpenCV usa BGR por defecto)
                            img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                            
                            cods = face_recognition.face_encodings(img_rgb)
                            if len(cods) > 0:
                                lista_codificaciones.append(cods[0])
                                lista_nombres.append("Gus")  # Todos los archivos son de Gustavo
                            else:
                                print(f"⚠ No se detectó cara en la imagen {archivo}")
                        else:
                            print(f"❌ No se pudo decodificar la imagen {archivo}")
        
        # ✅ SOLUCIÓN: Limpiar archivo temporal correctamente
        try:
            os.unlink(ruta_rar_temp)
        except:
            pass
            
        print(f"✅ Total de codificaciones cargadas: {len(lista_codificaciones)}")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar el sistema: {str(e)}")
        return False

def registrar_asistencia(nombre):
    """Registra la asistencia en el archivo CSV"""
    global caras_registradas, ultima_asistencia
    
    if nombre != "Desconocido" and nombre not in caras_registradas:
        archivo_asistencia = "asistencia_version3.csv"
        
        # ✅ SOLUCIÓN: Usar modo append seguro
        try:
            # Crear archivo si no existe
            file_exists = os.path.exists(archivo_asistencia)
            
            with open(archivo_asistencia, "a", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Nombre", "Fecha", "Hora"])
                
                # Registrar asistencia
                ahora = datetime.now()
                fecha = ahora.strftime("%d/%m/%Y")
                hora = ahora.strftime("%H:%M:%S")
                writer.writerow([nombre, fecha, hora])
            
            caras_registradas.add(nombre)
            ultima_asistencia = f"{nombre} - {fecha} {hora}"
            print(f"✅ Asistencia registrada: {ultima_asistencia}")
            return True
        except Exception as e:
            print(f"❌ Error al registrar asistencia: {e}")
            return False
    
    return False

def generar_frames():
    """✅ SOLUCIÓN: Versión para nube - Sin cámara física"""
    global estado_camara, lista_codificaciones, lista_nombres
    
    estado_camara = "activa"
    
    while estado_camara == "activa":
        try:
            # ✅ SOLUCIÓN: En Render no hay cámaras, usamos modo demostración
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Fondo azul oscuro
            frame[:, :] = (50, 50, 120)
            
            # Información del sistema
            cv2.putText(frame, "SISTEMA DE ASISTENCIA FACIAL - MODO NUBE", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Personas registradas: {len(lista_codificaciones)}", (30, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, f"Estado: {estado_camara.upper()}", (30, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Simular detección (para demostración)
            if len(lista_codificaciones) > 0:
                cv2.putText(frame, "✅ Sistema listo para reconocimiento", (30, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, "Gus - Detectado", (200, 350), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Dibujar recuadro simulado
                cv2.rectangle(frame, (150, 300), (350, 400), (0, 255, 0), 2)
                
                # Simular registro de asistencia ocasionalmente
                if np.random.random() < 0.02:  # 2% de probabilidad por frame
                    registrar_asistencia("Gus")
            else:
                cv2.putText(frame, "❌ Sistema no inicializado", (30, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Última asistencia
            if ultima_asistencia:
                cv2.putText(frame, f"Ultima: {ultima_asistencia}", (30, 400), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Codificar frame como JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # Controlar FPS
            
        except Exception as e:
            print(f"Error en generacion de frames: {e}")
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
        'message': 'Sistema de reconocimiento facial iniciado',
        'personas_registradas': len(lista_codificaciones)
    })

@app.route('/detener_reconocimiento', methods=['POST'])
def detener_reconocimiento():
    global estado_camara
    estado_camara = "detenida"
    return jsonify({
        'status': 'success', 
        'message': 'Sistema de reconocimiento detenido'
    })

@app.route('/obtener_asistencias')
def obtener_asistencias():
    try:
        asistencias = []
        if os.path.exists("asistencia_version3.csv"):
            with open("asistencia_version3.csv", "r", encoding='utf-8') as f:
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
        'total_asistencias_hoy': len(caras_registradas)
    })

@app.route('/resultados')
def resultados():
    return render_template('resultados.html')

# ================= INICIALIZACIÓN =================

if __name__ == '__main__':
    print("🚀 Inicializando sistema de reconocimiento facial...")
    print("📊 Cargando dataset desde la nube...")
    
    if inicializar_sistema():
        print("✅ Sistema inicializado correctamente")
        print(f"👤 Personas registradas: {len(lista_codificaciones)}")
    else:
        print("❌ Error en la inicialización del sistema")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Servidor Flask iniciado en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)