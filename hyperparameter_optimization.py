import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import f1_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
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

def engineer_features(df):
    # Crear nuevas caracteristicas normalizadas por partido jugado
    df_engineered = df.copy()
    df_engineered['tackles_per_game'] = df_engineered['tackles'] / df_engineered['games']
    df_engineered['goals_per_game'] = df_engineered['goals'] / df_engineered['games']
    df_engineered['assists_per_game'] = df_engineered['assists'] / df_engineered['games']
    df_engineered['key_passes_per_game'] = df_engineered['key_passes'] / df_engineered['games']
    return df_engineered

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

    # Mapear las posiciones al espanol
    mapping = {
        "D": "Defensa",
        "GK": "Portero",
        "F": "Delantero",
        "M": "Centrocampista",
        "S": "Segundo delantero"
    }

    vectorized_mapping_function = np.vectorize(lambda x: mapping.get(x, x))
    mapped_class_names = vectorized_mapping_function(class_names)

    print("\nClases mapeadas:")
    print(mapped_class_names)

    return X, y_encoded, mapped_class_names

def perform_grid_search(X, y):
    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Definir el pipeline con PolynomialFeatures y RandomForest
    pipeline_poly = Pipeline([
        ('poly', PolynomialFeatures(include_bias=False)),
        ('model', RandomForestClassifier(class_weight="balanced", random_state=42))
    ])

    # Definir espacio de busqueda de hiperparametros
    param_grid = {
        'model__n_estimators': [200],
        'model__max_depth': [20],
        'model__min_samples_leaf': [2],
        'model__max_features': ['log2'],
        'poly__degree': [2]
    }

    print("\nEjecutando Grid Search... (puede tardar 1-2 minutos)")
    grid_search = GridSearchCV(
        pipeline_poly,
        param_grid,
        cv=5,
        scoring='accuracy',  # Metrica a optimizar
        n_jobs=-1,           # Ejecucion en paralelo
        verbose=1            # Mostrar progreso
    )

    # Entrenar modelo con Grid Search
    grid_search.fit(X_train, y_train)

    # Obtener el mejor modelo y realizar predicciones
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    return grid_search, X_test, y_test, y_pred

def print_evaluation_metrics(grid_search, y_test, y_pred, target_names):
    # Imprimir los mejores hiperparametros encontrados
    print("\n" + "="*60)
    print("MEJORES HIPERPARAMETROS ENCONTRADOS")
    print("="*60)
    for param, value in grid_search.best_params_.items():
        print(f"  {param:20s}: {value}")
    
    # Imprimir metricas de evaluacion
    print(f"\nMejor Accuracy (CV): {grid_search.best_score_:.4f}")
    print(f"F1-Score en Test: {f1_score(y_test, y_pred, average='weighted'):.4f}")
    print(f"Accuracy en Test: {accuracy_score(y_test, y_pred):.4f}")

    print("\nReporte de Clasificacion:")
    print(classification_report(y_test, y_pred, target_names=target_names))

def plot_confusion_matrix_chart(y_test, y_pred, class_names, output_folder):
    # Generar, guardar y mostrar la matriz de confusion
    print(f"\nGenerando y guardando Matriz de confusion en '{output_folder}'...")
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
    disp.plot(cmap='Blues')
    
    plt.title('Matriz de Confusion - Deteccion de posicion', fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Guardar la imagen en alta calidad antes de mostrarla
    output_path = os.path.join(output_folder, "matriz_confusion_gridsearch.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # 1. Configuracion inicial
    setup_warnings()
    file_path = "data_output/Estadisticas_Jugadores.csv"
    graphics_folder = "graphics"
    create_output_directory(graphics_folder)

    # 2. Carga y preprocesamiento de datos
    df_raw = load_data(file_path)
    df_engineered = engineer_features(df_raw)
    X, y, mapped_class_names = prepare_features_and_labels(df_engineered)

    # 3. Busqueda de hiperparametros (Grid Search)
    grid_search_results, X_test, y_test, y_pred = perform_grid_search(X, y)

    # 4. Evaluacion numerica
    print_evaluation_metrics(grid_search_results, y_test, y_pred, mapped_class_names)

    # 5. Visualizacion y guardado
    plot_confusion_matrix_chart(y_test, y_pred, mapped_class_names, graphics_folder)