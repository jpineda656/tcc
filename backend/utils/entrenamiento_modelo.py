# backend/utils/entrenamiento_modelo.py
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from app.db.coneccion import SessionLocal
from datetime import datetime
from app.models.meta_entrenamiento_model import MetadatosEntrenamiento
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training.log"),  # Guardar logs en archivo
        logging.StreamHandler()               # Mostrar logs en consola
    ]
)


logger = logging.getLogger(__name__)

# ------------------ FUNCIONES DE PREPARACIÓN DE DATOS ------------------

def load_dataset(dataset_dir: str):
    """
    Carga los datos del dataset estructurado en formato NumPy.
    Retorna los datos y etiquetas como arrays NumPy.
    """
    X = []  # Datos (secuencias)
    y = []  # Etiquetas (palabras)

    logger.info(f"Cargando dataset desde {dataset_dir}")
    label_map = {}  # Mapear palabras a índices

    for idx, word_dir in enumerate(os.listdir(dataset_dir)):
        word_path = os.path.join(dataset_dir, word_dir)
        if os.path.isdir(word_path):
            label_map[word_dir] = idx
            for file_name in os.listdir(word_path):
                if file_name.endswith(".npy"):
                    file_path = os.path.join(word_path, file_name)
                    try:
                        sequence = np.load(file_path)
                        X.append(sequence)
                        y.append(idx)
                    except Exception as e:
                        logger.error(f"Error al cargar archivo {file_path}: {e}")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    logger.info(f"Dataset cargado correctamente: {len(X)} secuencias, {len(label_map)} clases.")
    return X, y, label_map

def split_dataset(X, y, test_size=0.2, validation_size=0.1):
    """
    Divide el dataset en conjuntos de entrenamiento, validación y prueba.
    """
    logger.info("Dividiendo el dataset en entrenamiento, validación y prueba.")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=test_size + validation_size, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=test_size / (test_size + validation_size), random_state=42)
    logger.info(f"Conjuntos generados: {len(X_train)} entrenamiento, {len(X_val)} validación, {len(X_test)} prueba.")
    return X_train, X_val, X_test, y_train, y_val, y_test

# ------------------ FUNCIONES DE DEFINICIÓN Y ENTRENAMIENTO DEL MODELO ------------------

def create_lstm_model(input_shape, n_classes):
    """
    Crea un modelo LSTM para la clasificación de gestos.
    """
    model = tf.keras.Sequential([
        layers.Input(shape=input_shape),
        layers.LSTM(64, return_sequences=True),
        layers.LSTM(64),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(n_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    logger.info("Modelo LSTM creado y compilado.")
    return model

def train_model(model, X_train, y_train, X_val, y_val, batch_size=32, epochs=50, model_dir="models"):
    """
    Entrena el modelo LSTM y guarda el modelo entrenado.
    """
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        logger.info(f"Directorio para guardar modelos creado: {model_dir}")

    model_path = os.path.join(model_dir, "gesture_model.h5")

    logger.info("Iniciando entrenamiento del modelo.")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        batch_size=batch_size,
        epochs=epochs,
        callbacks=[
            tf.keras.callbacks.ModelCheckpoint(model_path, save_best_only=True, monitor='val_accuracy', mode='max'),
            tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)
        ]
    )
    logger.info(f"Entrenamiento completado. Modelo guardado en {model_path}.")
    return history, model_path

# ------------------ ENTRENAMIENTO COMPLETO ------------------

def train_gesture_recognition_model(meta_entrenamiento_id:int, dataset_dir="dataset", model_dir="models", 
                                    test_size=0.2, validation_size=0.1, 
                                    batch_size=32, epochs=50):
    """
    Proceso completo de entrenamiento del modelo: carga, división, entrenamiento.
    """
    db = SessionLocal()
    try:
        X, y, label_map = load_dataset(dataset_dir)
        X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y, test_size, validation_size)

        input_shape = X_train.shape[1:]  # (n_frames, n_points * 3)
        n_classes = len(label_map)
        model = create_lstm_model(input_shape, n_classes)

        history, model_path = train_model(model, X_train, y_train, X_val, y_val, batch_size, epochs)

        test_loss, test_accuracy = model.evaluate(X_test, y_test)
        logger.info(f"Evaluación en conjunto de prueba: pérdida = {test_loss:.4f}, precisión = {test_accuracy:.4f}")


        meta = db.query(MetadatosEntrenamiento).filter_by(id=meta_entrenamiento_id).first()
        if meta:
            meta.status = "completed"
            meta.finished_at = datetime.utcnow()
            # Registrar métricas si gustas
            meta.accuracy = f"{test_accuracy:.2f}"
            meta.loss = f"{test_loss:.2f}"
            db.commit()
            
        return {
            "message": "Entrenamiento completado exitosamente.",
            "model_path": model_path,
            "test_accuracy": test_accuracy,
            "label_map": label_map
        }
            
    except Exception as e:
        logger.error(f"Error en el entrenamiento del modelo: {e}")
        meta = db.query(MetadatosEntrenamiento).filter_by(id=meta_entrenamiento_id).first()
        if meta:
            meta.status = "failed"
            db.commit() 
        raise
    finally:
        db.close()
