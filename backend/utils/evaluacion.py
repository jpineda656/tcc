# import os
# import json
# import numpy as np
# import tensorflow as tf
# import logging
# from typing import Dict
# # Eliminamos configuración redundante de logging
# logger = logging.getLogger(__name__)

# # ------------------ CONSTANTES ------------------
# MODEL_PATH = "models/gesture_model.h5"
# LABEL_MAP_PATH = "models/label_map.json"

# # Variables globales para caché
# _model = None
# _label_map = None

# # ------------------ FUNCIÓN DE CARGA CON CACHÉ ------------------
# def load_model_cached():
#     global _model
#     if _model is None:
#         if not os.path.exists(MODEL_PATH):
#             logger.error(f"El modelo no se encontró en {MODEL_PATH}.")
#             raise FileNotFoundError(f"El modelo no se encontró en {MODEL_PATH}.")
#         logger.info("Cargando modelo.")
#         _model = tf.keras.models.load_model(MODEL_PATH)
#         logger.info("Modelo cargado correctamente.")
#     return _model

# def load_label_map_cached():
#     global _label_map
#     if _label_map is None:
#         if not os.path.exists(LABEL_MAP_PATH):
#             logger.error(f"El archivo de etiquetas no se encontró en {LABEL_MAP_PATH}.")
#             raise FileNotFoundError(f"El archivo de etiquetas no se encontró en {LABEL_MAP_PATH}.")
#         with open(LABEL_MAP_PATH, "r") as f:
#             _label_map = json.load(f)
#     return _label_map

# # ------------------ NORMALIZACIÓN Y PREPROCESAMIENTO ------------------
# def fill_missing_landmarks(frame: Dict) -> Dict:
#     expected_points = {
#         "pose": 33,
#         "leftHand": 21,
#         "rightHand": 21,
#         "face": 468
#     }

#     def fill_landmarks(points, expected_count):
#         if not points:
#             logger.warning(f"Puntos faltantes detectados, rellenando con {expected_count} puntos.")
#             return [{"x": 0, "y": 0, "z": 0} for _ in range(expected_count)]
#         elif len(points) < expected_count:
#             missing = expected_count - len(points)
#             logger.warning(f"Puntos incompletos detectados, rellenando con {missing} puntos.")
#             return points + [{"x": 0, "y": 0, "z": 0} for _ in range(missing)]
#         return points

#     return {
#         "pose": fill_landmarks(frame.get("pose", []), expected_points["pose"]),
#         "leftHand": fill_landmarks(frame.get("leftHand", []), expected_points["leftHand"]),
#         "rightHand": fill_landmarks(frame.get("rightHand", []), expected_points["rightHand"]),
#         "face": fill_landmarks(frame.get("face", []), expected_points["face"]),
#     }

# def normalize_landmarks(frame: Dict) -> Dict:
#     frame = fill_missing_landmarks(frame)

#     pose = frame.get("pose", [])
#     if not pose or len(pose) < 12:
#         logger.warning("No se encontraron suficientes puntos para normalizar. Frame no procesado.")
#         return frame

#     left_shoulder = np.array([pose[11]["x"], pose[11]["y"], pose[11]["z"]])
#     right_shoulder = np.array([pose[12]["x"], pose[12]["y"], pose[12]["z"]])
#     center = (left_shoulder + right_shoulder) / 2
#     ref_distance = np.linalg.norm(left_shoulder - right_shoulder)

#     if ref_distance == 0:
#         logger.warning("La distancia de referencia entre hombros es cero. Ajustando a 1.")
#         ref_distance = 1

#     def normalize_points(points):
#         return [
#             {
#                 "x": (p["x"] - center[0]) / ref_distance,
#                 "y": (p["y"] - center[1]) / ref_distance,
#                 "z": (p["z"] - center[2]) / ref_distance,
#             }
#             for p in points
#         ]

#     return {
#         "pose": normalize_points(frame.get("pose", [])),
#         "leftHand": normalize_points(frame.get("leftHand", [])),
#         "rightHand": normalize_points(frame.get("rightHand", [])),
#         "face": normalize_points(frame.get("face", [])),
#     }

# def pad_or_trim_sequence(sequence: list, target_length: int = 30) -> list:
#     if len(sequence) > target_length:
#         logger.info(f"Secuencia recortada de {len(sequence)} a {target_length} frames.")
#         return sequence[:target_length]
#     elif len(sequence) < target_length:
#         last_frame = sequence[-1]
#         logger.info(f"Secuencia rellenada de {len(sequence)} a {target_length} frames.")
#         while len(sequence) < target_length:
#             sequence.append(last_frame)
#     return sequence

# def preprocess_for_evaluation(data: Dict) -> np.ndarray:
#     frames = data.get("framesData", [])
#     if not frames:
#         raise ValueError("No se encontraron framesData en los datos recibidos.")

#     logger.info(f"Procesando {len(frames)} frames para evaluación.")
#     frames = pad_or_trim_sequence(frames, target_length=30)
#     normalized_frames = [normalize_landmarks(frame) for frame in frames]

#     input_sequence = []
#     for frame in normalized_frames:
#         frame_data = []
#         for group in ["pose", "leftHand", "rightHand", "face"]:
#             points = frame.get(group, [])
#             for point in points:
#                 frame_data.extend([point["x"], point["y"], point["z"]])
#         input_sequence.append(frame_data)

#     input_array = np.array(input_sequence, dtype=np.float32)
#     input_array = np.expand_dims(input_array, axis=0)  # Agregar dimensión batch
#     return input_array

# # ------------------ PREDICCIÓN ------------------
# def predict(data: Dict):
#     CONFIDENCE_THRESHOLD = 0.8

#     try:
#         model = load_model_cached()
#         label_map = load_label_map_cached()
#         input_array = preprocess_for_evaluation(data)

#         logger.info("Realizando predicción.")
#         predictions = model.predict(input_array)
#         predicted_class_idx = int(np.argmax(predictions))
#         confidence = float(predictions[0][predicted_class_idx])

#         if confidence < CONFIDENCE_THRESHOLD:
#             logger.warning(f"Confianza baja ({confidence:.2f}). Predicción no aceptada.")
#             return {
#                 "predicted_label": None,
#                 "confidence": confidence,
#                 "message": "Confianza insuficiente para una predicción confiable."
#             }

#         # Obtener la etiqueta predicha a partir del mapa de etiquetas
#         predicted_label = None
#         for label, idx in label_map.items():
#             if idx == predicted_class_idx:
#                 predicted_label = label
#                 break

#         logger.info(f"Predicción completada: {predicted_label} (Confianza: {confidence:.2f})")
#         return {
#             "predicted_label": predicted_label,
#             "confidence": confidence
#         }
#     except Exception as e:
#         logger.error(f"Error en la predicción: {e}")
#         raise e
# backend/utils/evaluacion.py
import os
import json
import numpy as np
import tensorflow as tf
import logging
from typing import Dict

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("prediction.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ------------------ CONSTANTES ------------------
MODEL_PATH = "models/gesture_model.h5"
LABEL_MAP_PATH = "models/label_map.json"
CONFIDENCE_THRESHOLD = 0.8

# Variables globales para caché
_model = None
_label_map = None
_inv_label_map = None  # <<-- Se añade para la versión invertida

# ------------------ FUNCIÓN DE CARGA CON CACHÉ ------------------
def load_model_cached():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"El modelo no se encontró en {MODEL_PATH}.")
            raise FileNotFoundError(f"El modelo no se encontró en {MODEL_PATH}.")
        logger.info("Cargando modelo.")
        _model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Modelo cargado correctamente.")
    return _model

def load_label_map_cached():
    """
    Carga el label_map original (clase -> índice) y crea un inv_label_map (índice -> clase),
    guardándolos en variables globales.
    """
    global _label_map, _inv_label_map
    if _label_map is None or _inv_label_map is None:
        if not os.path.exists(LABEL_MAP_PATH):
            logger.error(f"El archivo de etiquetas no se encontró en {LABEL_MAP_PATH}.")
            raise FileNotFoundError(f"El archivo de etiquetas no se encontró en {LABEL_MAP_PATH}.")
        with open(LABEL_MAP_PATH, "r") as f:
            _label_map = json.load(f)

        # Crear la versión invertida
        _inv_label_map = {v: k for k, v in _label_map.items()}

        logger.info(f"label_map cargado con {len(_label_map)} clases.")
    return _label_map, _inv_label_map

# ------------------ NORMALIZACIÓN Y PREPROCESAMIENTO ------------------
def fill_missing_landmarks(frame: Dict) -> Dict:
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

    return {
        "pose": fill_landmarks(frame.get("pose", []), expected_points["pose"]),
        "leftHand": fill_landmarks(frame.get("leftHand", []), expected_points["leftHand"]),
        "rightHand": fill_landmarks(frame.get("rightHand", []), expected_points["rightHand"]),
        "face": fill_landmarks(frame.get("face", []), expected_points["face"]),
    }

def normalize_landmarks(frame: Dict) -> Dict:
    frame = fill_missing_landmarks(frame)
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

    return {
        "pose": normalize_points(frame.get("pose", [])),
        "leftHand": normalize_points(frame.get("leftHand", [])),
        "rightHand": normalize_points(frame.get("rightHand", [])),
        "face": normalize_points(frame.get("face", [])),
    }

def pad_or_trim_sequence(sequence: list, target_length: int = 30) -> list:
    if len(sequence) > target_length:
        logger.info(f"Secuencia recortada de {len(sequence)} a {target_length} frames.")
        return sequence[:target_length]
    elif len(sequence) < target_length:
        last_frame = sequence[-1]
        logger.info(f"Secuencia rellenada de {len(sequence)} a {target_length} frames.")
        while len(sequence) < target_length:
            sequence.append(last_frame)
    return sequence

def preprocess_for_evaluation(data: Dict) -> np.ndarray:
    frames = data.get("framesData", [])
    if not frames:
        raise ValueError("No se encontraron framesData en los datos recibidos.")

    logger.info(f"Procesando {len(frames)} frames para evaluación.")

    frames = pad_or_trim_sequence(frames, target_length=30)
    normalized_frames = [normalize_landmarks(frame) for frame in frames]

    input_sequence = []
    for frame in normalized_frames:
        frame_data = []
        for group in ["pose", "leftHand", "rightHand", "face"]:
            points = frame[group]
            for point in points:
                frame_data.extend([point["x"], point["y"], point["z"]])
        input_sequence.append(frame_data)

    input_array = np.array(input_sequence, dtype=np.float32)
    input_array = np.expand_dims(input_array, axis=0)  # Agregar dimensión batch
    return input_array

# ------------------ FUNCIÓN DE PREDICCIÓN ------------------
def predict(data: Dict):
    try:
        # Cargar modelo y mapas en caché
        model = load_model_cached()
        label_map, inv_label_map = load_label_map_cached()

        # Preprocesar
        input_array = preprocess_for_evaluation(data)

        logger.info("Realizando predicción.")
        predictions = model.predict(input_array)

        predicted_class_idx = int(np.argmax(predictions))
        confidence = float(predictions[0][predicted_class_idx])

        if confidence < CONFIDENCE_THRESHOLD:
            logger.warning(f"Confianza baja ({confidence:.2f}). Predicción no aceptada.")
            return {
                "predicted_label": None,
                "confidence": confidence,
                "message": "Confianza insuficiente para una predicción confiable."
            }

        # Usamos inv_label_map para obtener la clase de forma directa
        predicted_label = inv_label_map.get(predicted_class_idx, None)

        logger.info(f"Predicción completada: {predicted_label} (Confianza: {confidence:.2f})")
        return {
            "predicted_label": predicted_label,
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"Error en la predicción: {e}")
        raise e
