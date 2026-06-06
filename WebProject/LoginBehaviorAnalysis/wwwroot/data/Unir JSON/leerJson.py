#leer registros individuales del json
import json

def mostrar_datos_por_indice_y_label(json_file, indice, label):
    # Leer el archivo JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Filtrar los registros por el valor de Label
    registros_filtrados = [registro for registro in data if registro['Label'] == label]
    
    # Verificar si el índice solicitado está dentro del rango de registros filtrados
    if 0 <= indice < len(registros_filtrados):
        # Obtener el registro en el índice solicitado
        registro = registros_filtrados[indice]
        
        # Mostrar los datos del registro
        print(f"UserId: {registro['UserId']}")
        print(f"Etiqueta (Label): {registro['Label']}")
        print("Eventos:")
        
        for evento in registro['Events']:
            print(f"  Tipo: {evento['Type']}, Timestamp: {evento['Timestamp']}, X: {evento['X']}, Y: {evento['Y']}, Button: {evento['Button']}")
            print(f"  Element: {evento['Element']}, ScrollX: {evento['ScrollX']}, ScrollY: {evento['ScrollY']}, IdleTime: {evento['IdleTime']}")
        print("-" * 50)  # Separador entre registros
    else:
        print("Índice fuera de rango o no se encontraron registros con ese label.")

# Llamada a la función con el archivo JSON, índice y label deseado
mostrar_datos_por_indice_y_label('DataMouse.json', 0, 0)  # Cambia 'data.json' por tu archivo real
