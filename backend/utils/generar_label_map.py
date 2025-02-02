# backend/utils/generar_label_map.py
import os
import json

def create_label_map_from_folders(dataset_dir="dataset", output_path="models/label_map.json"):
    """
    Lee todas las subcarpetas en 'dataset_dir' y crea un label_map.json
    en la ruta 'output_path'.
    """
    if not os.path.exists(dataset_dir):
        print(f"Carpeta {dataset_dir} no existe.")
        return

    # Leer subcarpetas
    labels = sorted([
        d for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d))
    ])

    # Crear el mapeo label -> índice
    label_map = {}
    for idx, label in enumerate(labels):
        label_map[label] = idx

    # Guardar en JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    print(f"label_map.json generado en {output_path}")


if __name__ == "__main__":
    create_label_map_from_folders()
