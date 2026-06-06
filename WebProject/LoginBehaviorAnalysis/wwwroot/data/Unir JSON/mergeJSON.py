import json

def merge_json(file1, file2, output_file):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
    
    # Combinar los JSON (puedes ajustar según la estructura)
    if isinstance(data1, dict) and isinstance(data2, dict):
        merged_data = {**data1, **data2}  # Fusionar diccionarios
    elif isinstance(data1, list) and isinstance(data2, list):
        merged_data = data1 + data2  # Unir listas
    else:
        merged_data = [data1, data2]  # Envolver en una lista si son distintos tipos
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        json.dump(merged_data, f_out, ensure_ascii=False, indent=4)
    
    print(f"JSON fusionado guardado en {output_file}")

# Uso
test_file1 = '1.json'
test_file2 = '2.json'
output_file = 'merged.json'
merge_json(test_file1, test_file2, output_file)
