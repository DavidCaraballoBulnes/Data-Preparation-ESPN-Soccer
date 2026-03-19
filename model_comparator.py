import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score
)
import warnings

def setup_warnings():
    # Ignorar advertencias para mantener la salida de consola limpia
    warnings.filterwarnings('ignore')

def create_output_directory(folder_name):
    # Crear el directorio para guardar los graficos si no existe
    os.makedirs(folder_name, exist_ok=True)

def load_data(file_path):
    # Cargar el conjunto de datos y seleccionar unicamente las columnas relevantes
    df = pd.read_csv(file_path)
    columns_to_keep = [
        "games", "time", "goals", "xG", "assists", "xA", "shots",
        "key_passes", "yellow_cards", "red_cards", "position",
        "npg", "npxG", "xGChain", "xGBuildup", "tackles"
    ]
    return df[columns_to_keep]

def prepare_features_and_labels(df):
    # Extraer la primera palabra de la columna de posicion
    df["position"] = [str(x).split()[0] for x in df["position"]]

    # Separar las caracteristicas de la variable objetivo
    X = df.drop("position", axis=1)
    y_raw = df["position"]

    # Codificar la variable objetivo
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)
    class_names = label_encoder.classes_
    
    print(f"Clases codificadas: { {name: i for i, name in enumerate(class_names)} }")

    return X, y_encoded

def prepare_and_scale_data(X, y):
    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Escalar los datos
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled

def get_models():
    # Definir y retornar el diccionario de modelos a comparar
    return {
        'KNN': KNeighborsClassifier(n_neighbors=5),
        'SVM': SVC(kernel="rbf", probability=True),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    }

def calculate_metrics(models, X_train, y_train, X_test, y_test):
    # Entrenar cada modelo y calcular sus metricas de rendimiento
    results = {}
    for name, model in models.items():
        # Entrenar el modelo
        model.fit(X_train, y_train)
        
        # Realizar predicciones
        predictions = model.predict(X_test)
        
        # Guardar metricas
        results[name] = [
            accuracy_score(y_test, predictions),
            precision_score(y_test, predictions, average='macro'),
            recall_score(y_test, predictions, average='macro'),
            f1_score(y_test, predictions, average='macro'),
            precision_score(y_test, predictions, average='weighted'),
            recall_score(y_test, predictions, average='weighted'),
            f1_score(y_test, predictions, average='weighted')
        ]
    return results

def plot_model_comparison(results, output_folder, file_name, subtitle=""):
    # Generar, guardar y mostrar el grafico de barras comparativo
    print(f"\nGenerando y guardando grafico comparativo en '{output_folder}/{file_name}'...")
    
    metrics_names = [
        "Accuracy", "Precision Macro", "Recall Macro", "F1 Macro", 
        "Precision Weighted", "Recall Weighted", "F1 Weighted"
    ]
    
    # Crear DataFrame transpuesto para facilitar el graficado
    df_metrics = pd.DataFrame(results, index=metrics_names).transpose()

    metrics = df_metrics.columns
    model_names = df_metrics.index

    x = np.arange(len(metrics))
    width = 0.12

    fig, ax = plt.subplots(figsize=(14, 7))
    displacements = np.linspace(-width * 2.5, width * 2.5, len(model_names))

    # Paleta de colores para diferenciar los modelos
    colors = ['blue', 'orange', 'green', 'red', 'purple']

    for i, model in enumerate(model_names):
        values = df_metrics.loc[model].values
        ax.bar(x + displacements[i], values, width, label=model, color=colors[i], edgecolor='white')

    # Configuracion visual del grafico
    ax.set_ylabel('Puntuacion', fontsize=12, fontweight='bold')
    
    title = 'Comparacion de Modelos por Metrica de Evaluacion'
    if subtitle:
        title += f' {subtitle}'
        
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.1)

    # Leyenda fuera del grafico
    ax.legend(title='Modelos', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=11, title_fontsize=12)

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Guardar y mostrar
    output_path = os.path.join(output_folder, file_name)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # 1. Configuracion inicial
    setup_warnings()
    file_path = "data_output/Estadisticas_Jugadores.csv"
    graphics_folder = "model_info"
    create_output_directory(graphics_folder)

    # 2. Carga y preprocesamiento
    df_raw = load_data(file_path)
    X, y = prepare_features_and_labels(df_raw)
    
    # 3. Preparacion de datos (division y escalado)
    X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled = prepare_and_scale_data(X, y)

    # 4. Obtener modelos
    models = get_models()

    # 5. Calcular metricas para datos sin escalar y escalados
    print("\nCalculando metricas para datos originales...")
    results_raw = calculate_metrics(models, X_train, y_train, X_test, y_test)
    
    print("Calculando metricas para datos escalados...")
    results_scaled = calculate_metrics(models, X_train_scaled, y_train, X_test_scaled, y_test)

    # 6. Generar graficos
    plot_model_comparison(
        results=results_raw, 
        output_folder=graphics_folder, 
        file_name="comparacion_modelos_original.png"
    )
    
    plot_model_comparison(
        results=results_scaled, 
        output_folder=graphics_folder, 
        file_name="comparacion_modelos_escalado.png", 
        subtitle="(con datos escalados)"
    )