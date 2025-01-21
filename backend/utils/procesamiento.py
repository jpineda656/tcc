import os
import json
import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

# ------------------ FUNCIONES DE NORMALIZACIÓN ------------------

def fill_missing_landmarks(frame: Dict) -> Dict:
    """
    Rellena puntos de referencia faltantes con valores predeterminados (0, 0, 0).
    """
    expected_points = {
        "pose": 33,
        "leftHand": 21,
        "rightHand": 21,
        "face": 468
    }

    def fill_landmarks(points, expected_count):
        if not points:
            logger.warning(f"Puntos faltantes detectados, rellenando con {expected_count} puntos.")
            return [{"x": 0, "y": 0, "z": 0} for _ in range(expected_count)]
        elif len(points) < expected_count:
            missing = expected_count - len(points)
            logger.warning(f"Puntos incompletos detectados, rellenando con {missing} puntos.")
            return points + [{"x": 0, "y": 0, "z": 0} for _ in range(missing)]
        return points

    filled_frame = {
        "pose": fill_landmarks(frame.get("pose", []), expected_points["pose"]),
        "leftHand": fill_landmarks(frame.get("leftHand", []), expected_points["leftHand"]),
        "rightHand": fill_landmarks(frame.get("rightHand", []), expected_points["rightHand"]),
        "face": fill_landmarks(frame.get("face", []), expected_points["face"]),
    }
    logger.debug(f"Frame completado: {filled_frame}")
    return filled_frame

def normalize_landmarks(frame: Dict) -> Dict:
    """
    Normaliza los puntos de referencia de un frame.
    """
    pose = frame.get("pose", [])
    if not pose or len(pose) < 12:
        logger.warning("No se encontraron suficientes puntos para normalizar. Frame no procesado.")
        return frame

    left_shoulder = np.array([pose[11]["x"], pose[11]["y"], pose[11]["z"]])
    right_shoulder = np.array([pose[12]["x"], pose[12]["y"], pose[12]["z"]])
    center = (left_shoulder + right_shoulder) / 2
    ref_distance = np.linalg.norm(left_shoulder - right_shoulder)

    if ref_distance == 0:
        logger.warning("La distancia de referencia entre hombros es cero. Ajustando a 1.")
        ref_distance = 1

    def normalize_points(points):
        return [
            {
                "x": (p["x"] - center[0]) / ref_distance,
                "y": (p["y"] - center[1]) / ref_distance,
                "z": (p["z"] - center[2]) / ref_distance,
            }
            for p in points
        ]

    normalized_frame = {
        "pose": normalize_points(frame.get("pose", [])),
        "leftHand": normalize_points(frame.get("leftHand", [])),
        "rightHand": normalize_points(frame.get("rightHand", [])),
        "face": normalize_points(frame.get("face", [])),
    }
    logger.debug(f"Frame normalizado: {normalized_frame}")
    return normalized_frame

def pad_or_trim_sequence(sequence: List[Dict], target_length: int = 30) -> List[Dict]:
    """
    Ajusta una secuencia a una longitud fija.
    """
    if len(sequence) > target_length:
        logger.info(f"Secuencia recortada de {len(sequence)} a {target_length} frames.")
        return sequence[:target_length]
    elif len(sequence) < target_length:
        last_frame = sequence[-1]
        logger.info(f"Secuencia rellenada de {len(sequence)} a {target_length} frames.")
        while len(sequence) < target_length:
            sequence.append(last_frame)
    return sequence

def preprocess_sequence(sequence: List[Dict], target_length: int = 30) -> List[Dict]:
    """
    Procesa una secuencia completa: normaliza, rellena y ajusta frames.
    """
    logger.info(f"Iniciando preprocesamiento de secuencia con {len(sequence)} frames.")
    processed_frames = [fill_missing_landmarks(frame) for frame in sequence]
    processed_frames = [normalize_landmarks(frame) for frame in processed_frames]
    final_sequence = pad_or_trim_sequence(processed_frames, target_length)
    logger.info("Preprocesamiento de secuencia completado.")
    return final_sequence

# ------------------ FUNCIONES DE ALMACENAMIENTO ------------------

def save_sequence_as_numpy(sequence: List[Dict], word: str, dataset_dir: str = "dataset") -> str:
    """
    Guarda una secuencia normalizada en formato NumPy (.npy), organizada por palabra.
    """
    try:
        word_dir = os.path.join(dataset_dir, word)
        os.makedirs(word_dir, exist_ok=True)

        seq_id = len(os.listdir(word_dir)) + 1
        file_name = f"seq_{seq_id:03d}.npy"
        file_path = os.path.join(word_dir, file_name)

        np_sequence = []
        for frame in sequence:
            frame_data = []
            for group in ["pose", "leftHand", "rightHand", "face"]:
                points = frame[group]
                for point in points:
                    frame_data.extend([point["x"], point["y"], point["z"]])
            np_sequence.append(frame_data)

        np_sequence = np.array(np_sequence, dtype=np.float32)
        np.save(file_path, np_sequence)
        
        logger.info(f"Secuencia guardada en {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error al guardar secuencia como NumPy: {e}")
        raise

def store_sequence(sequence: List[Dict], word: str, dataset_dir: str = "dataset"):
    """
    Guarda una secuencia en formato NumPy.
    """
    try:
        numpy_path = save_sequence_as_numpy(sequence, word, dataset_dir)
        logger.info(f"Secuencia guardada en formato:\n NumPy: {numpy_path}")
    except Exception as e:
        logger.error(f"Error en el almacenamiento estructurado: {e}")
        raise

# ------------------ PROCESAMIENTO COMPLETO ------------------

def preprocess_all_files(input_dir: str, output_dir: str, dataset_dir: str = "dataset"):
    """
    Preprocesa todos los archivos JSON en un directorio y los guarda en formato estructurado.
    """
    logger.info(f"Iniciando preprocesamiento en el directorio: {input_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Directorio de salida creado: {output_dir}")

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                with open(input_path, "r") as infile:
                    data = json.load(infile)

                if "framesData" in data and "label" in data:
                    label = data["label"]
                    frames_data = data["framesData"]

                    processed_sequence = preprocess_sequence(frames_data)
                    with open(output_path, "w") as outfile:
                        json.dump({"framesData": processed_sequence, "label": label}, outfile, indent=4)
                    store_sequence(processed_sequence, label, dataset_dir)
                    logger.info(f"Archivo procesado y almacenado: {filename}")
                else:
                    logger.error(f"Estructura no válida en el archivo: {filename}")
            except Exception as e:
                logger.exception(f"Error procesando el archivo {filename}: {e}")
