import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_curve, auc
from sklearn.tree import plot_tree
from sklearn.preprocessing import label_binarize
import warnings

def ignore_warnings():
    # Ignorar advertencias para mantener limpia la salida en la consola
    warnings.filterwarnings('ignore')

def create_output_directory(folder_name):
    # Crear el directorio para guardar los graficos si no existe
    os.makedirs(folder_name, exist_ok=True)

def load_data(file_path):
    # Cargar el conjunto de datos y seleccionar las columnas relevantes
    df = pd.read_csv(file_path)
    columns_to_keep = [
        "games", "time", "goals", "xG", "assists", "xA", "shots", 
        "key_passes", "yellow_cards", "red_cards", "position", 
        "npg", "npxG", "xGChain", "xGBuildup", "tackles"
    ]
    return df[columns_to_keep]

def engineer_features(df):
    # Crear nuevas caracteristicas basadas en promedios por partido
    df_engineered = df.copy()
    df_engineered['tackles_per_game'] = df_engineered['tackles'] / df_engineered['games']
    df_engineered['goals_per_game'] = df_engineered['goals'] / df_engineered['games']
    df_engineered['assists_per_game'] = df_engineered['assists'] / df_engineered['games']
    df_engineered['key_passes_per_game'] = df_engineered['key_passes'] / df_engineered['games']
    return df_engineered

def prepare_features_and_labels(df):
    # Limpiar la columna de posicion y separar caracteristicas de la etiqueta
    df["position"] = [x.split()[0] for x in df["position"]]
    
    X = df.drop("position", axis=1)
    y_raw = df["position"]

    # Codificar las etiquetas de texto a valores numericos
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    class_names = label_encoder.classes_

    # Mapear las siglas de las posiciones al espanol
    mapping = {
        "D": "Defensa",
        "GK": "Portero",
        "F": "Delantero",
        "M": "Centrocampista",
        "S": "Segundo delantero"
    }

    vectorized_mapping_function = np.vectorize(lambda x: mapping.get(x, x))
    mapped_class_names = vectorized_mapping_function(class_names)

    return X, y, mapped_class_names

def train_model(X, y):
    # Dividir los datos y entrenar el pipeline
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y
    )

    pipeline = Pipeline([
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('model', RandomForestClassifier(
            class_weight="balanced",
            n_estimators=200,
            max_depth=20,
            min_samples_leaf=2,
            max_features='log2'
        ))
    ])

    pipeline.fit(X_train, y_train)
    
    # Predecir en Train y en Test para poder evaluar el sobreajuste (overfitting)
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    return pipeline, X_train, X_test, y_train, y_test, y_pred_train, y_pred_test

def print_evaluation_metrics(y_train, y_pred_train, y_test, y_pred_test, target_names):
    # Calcular accuracies
    acc_train = accuracy_score(y_train, y_pred_train)
    acc_test = accuracy_score(y_test, y_pred_test)
    
    # Imprimir metricas de evaluacion para justificar que no hay sobreajuste
    print("--- EVALUACION DEL SOBREAJUSTE (OVERFITTING) ---")
    print(f"Accuracy en Train: {acc_train:.4f}")
    print(f"Accuracy en Test:  {acc_test:.4f}")
    print(f"Diferencia:        {abs(acc_train - acc_test):.4f}")
    
    # Imprimir las metricas generales en Test
    print("\n--- METRICAS GENERALES EN TEST ---")
    print(f"F1-Score ponderado: {f1_score(y_test, y_pred_test, average='weighted'):.4f}")
    print("\nReporte de Clasificacion:")
    print(classification_report(y_test, y_pred_test, target_names=target_names))

def plot_confusion_matrix_chart(y_test, y_pred, class_names, output_folder):
    # Generar, guardar y mostrar la matriz de confusion
    print(f"\nGenerando y guardando Matriz de confusion en '{output_folder}'...")
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
    disp.plot(cmap='Blues')
    plt.title('Matriz de Confusion - Deteccion de posicion', fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Guardar imagen antes de mostrarla
    plt.savefig(os.path.join(output_folder, "matriz_confusion.png"), dpi=300, bbox_inches='tight')
    plt.show()

def plot_roc_curve_chart(pipeline, X_test, y_test, class_names, output_folder):
    # Generar, guardar y mostrar la curva ROC Multiclase
    print(f"Generando y guardando Curva ROC en '{output_folder}'...")
    y_score = pipeline.predict_proba(X_test)
    classes_unique = np.arange(len(class_names))
    y_test_bin = label_binarize(y_test, classes=classes_unique)
    n_classes = y_test_bin.shape[1]

    plt.figure(figsize=(8, 6))
    for i in range(n_classes):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'ROC {class_names[i]} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], 'k--', label='Azar')
    plt.xlabel('Tasa de Falsos Positivos')
    plt.ylabel('Tasa de Verdaderos Positivos')
    plt.title('Curva ROC por Posicion')
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    
    plt.savefig(os.path.join(output_folder, "curva_roc.png"), dpi=300, bbox_inches='tight')
    plt.show()

def plot_feature_importance_chart(pipeline, original_columns, output_folder):
    # Visualizar y guardar las 15 caracteristicas mas influyentes
    print(f"Generando y guardando Importancia de Caracteristicas en '{output_folder}'...")
    poly_features = pipeline.named_steps['poly'].get_feature_names_out(original_columns)
    importances = pipeline.named_steps['model'].feature_importances_
    indices = np.argsort(importances)[-15:]

    plt.figure(figsize=(10, 6))
    plt.title("Top 15 Caracteristicas mas influyentes (con Polinomios)")
    plt.barh(range(len(indices)), importances[indices], color='forestgreen', align='center')
    plt.yticks(range(len(indices)), [poly_features[i] for i in indices])
    plt.xlabel('Importancia relativa')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_folder, "importancia_caracteristicas.png"), dpi=300, bbox_inches='tight')
    plt.show()

def plot_decision_tree_chart(pipeline, original_columns, class_names, output_folder):
    # Visualizar y guardar la estructura parcial del primer arbol de decision
    print(f"Generando y guardando Arbol de Decision en '{output_folder}'...")
    poly_features = pipeline.named_steps['poly'].get_feature_names_out(original_columns)
    
    plt.figure(figsize=(35, 12))
    plot_tree(pipeline.named_steps['model'].estimators_[0], 
              feature_names=poly_features, 
              class_names=class_names, 
              filled=True, 
              max_depth=3, 
              fontsize=7,  
              rounded=True, 
              precision=2)

    plt.title("Estructura de decision (Primer arbol del bosque - Vista parcial)", fontsize=16)
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_folder, "arbol_decision.png"), dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # 1. Configuracion inicial
    ignore_warnings()
    file_path = "data_output/Estadisticas_Jugadores.csv"
    graphics_folder = "model_info"
    
    # Crear carpeta para los graficos
    create_output_directory(graphics_folder)
    
    # 2. Carga y preprocesamiento
    df_raw = load_data(file_path)
    df_engineered = engineer_features(df_raw)
    X, y, mapped_class_names = prepare_features_and_labels(df_engineered)
    
    # 3. Entrenamiento del modelo evaluando train y test
    pipeline, X_train, X_test, y_train, y_test, y_pred_train, y_pred_test = train_model(X, y)
    
    # 4. Evaluacion numerica del sobreajuste y metricas generales
    print_evaluation_metrics(y_train, y_pred_train, y_test, y_pred_test, mapped_class_names)
    
    # 5. Visualizaciones y guardado usando los datos de prueba
    plot_confusion_matrix_chart(y_test, y_pred_test, mapped_class_names, graphics_folder)
    plot_roc_curve_chart(pipeline, X_test, y_test, mapped_class_names, graphics_folder)
    plot_feature_importance_chart(pipeline, X.columns, graphics_folder)
    plot_decision_tree_chart(pipeline, X.columns, mapped_class_names, graphics_folder)