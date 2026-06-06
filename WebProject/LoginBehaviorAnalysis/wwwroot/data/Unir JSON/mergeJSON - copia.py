import json
import pandas as pd # Aunque no lo usamos para el archivo final, es útil para análisis previos.
import numpy as np # Para futuras operaciones si decides usarlas.

# --- 1. Carga de los dos conjuntos de datos ---
human_data = []
bot_data = []

print("Cargando mouse_data_Hum_Train.json...")
try:
    with open('mouse_data_Hum_Train.json', 'r') as f:
        human_data = json.load(f)
    print("mouse_data_Hum_Train.json cargado con éxito.")
except FileNotFoundError:
    print("Error: mouse_data_Hum_Train.json no encontrado. Asegúrate de que el archivo esté subido a tu entorno de Colab.")
    exit()

print("Cargando mouse_data_Bot_Train.json...")
try:
    with open('mouse_data_Bot_Train.json', 'r') as f:
        bot_data = json.load(f)
    print("mouse_data_Bot_Train.json cargado con éxito.")
except FileNotFoundError:
    print("Error: mouse_data_Bot_Train.json no encontrado. Asegúrate de que el archivo esté subido a tu entorno de Colab.")
    exit()

# --- 2. Asignar etiquetas y combinar los datos ---
# Etiqueta = 1 para humanos
for session in human_data:
    session['Label'] = 1 # 1 para humano

# Etiqueta = 0 para bots
for session in bot_data:
    session['Label'] = 0 # 0 para bot

# Combinar ambos datasets en una sola lista de diccionarios
combined_data = human_data + bot_data

print(f"\nTotal de sesiones cargadas: {len(combined_data)}")
print(f"Sesiones de humanos (Label=1): {len(human_data)}")
print(f"Sesiones de bots (Label=0): {len(bot_data)}")

# --- 3. Guardar el archivo combinado ---
output_filename = 'combined_mouse_data_labeled.json'
try:
    with open(output_filename, 'w') as f:
        json.dump(combined_data, f, indent=4) # indent=4 para que sea legible
    print(f"\n¡Archivo '{output_filename}' creado con éxito!")
    print(f"Puedes descargarlo desde el panel de archivos de Google Colab (icono de carpeta a la izquierda).")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")

# --- 4. Verificación rápida (opcional, para confirmar las etiquetas) ---
print("\n--- Verificación rápida del archivo combinado ---")
# Contar la distribución de las etiquetas en el archivo combinado
temp_labels = [session['Label'] for session in combined_data]
label_counts = pd.Series(temp_labels).value_counts()
print("Distribución de etiquetas en el archivo combinado:")
print(f"Humanos (Label=1): {label_counts.get(1, 0)} sesiones")
print(f"Bots (Label=0): {label_counts.get(0, 0)} sesiones")

# Ejemplo del primer elemento para verificar la estructura
if combined_data:
    print("\nEjemplo de la primera sesión combinada (verificar la etiqueta 'Label'):")
    print(json.dumps(combined_data[0], indent=4))
else:
    print("\nEl archivo combinado está vacío.")
