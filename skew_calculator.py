import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, PowerTransformer
import warnings

def setup_warnings():
    # Ignorar advertencias para mantener la salida de consola limpia
    warnings.filterwarnings('ignore')

def load_data(file_path):
    # Cargar el conjunto de datos y seleccionar unicamente las columnas relevantes
    df = pd.read_csv(file_path)
    columns_to_keep = [
        "games", "time", "goals", "xG", "assists", "xA", "shots",
        "key_passes", "yellow_cards", "red_cards", "position",
        "npg", "npxG", "xGChain", "xGBuildup", "tackles"
    ]
    return df[columns_to_keep]

def process_target_variable(df):
    # Extraer la primera palabra de la columna de posicion
    df["position"] = [str(x).split()[0] for x in df["position"]]
    print("Informacion del DataFrame:")
    print(df.info())

    # Separar las caracteristicas de la variable objetivo
    X = df.drop("position", axis=1)
    y_raw = df["position"]

    # Codificar la variable objetivo
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)
    class_names = label_encoder.classes_
    
    print(f"\nClases codificadas: { {name: i for i, name in enumerate(class_names)} }")

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

    # Devolvemos solo X (caracteristicas numericas) para el analisis de sesgo
    return X

def engineer_features(X):
    # Crear nuevas caracteristicas normalizadas por partido jugado
    X_engineered = X.copy()
    X_engineered['tackles_per_game'] = X_engineered['tackles'] / X_engineered['games']
    X_engineered['goals_per_game'] = X_engineered['goals'] / X_engineered['games']
    X_engineered['assists_per_game'] = X_engineered['assists'] / X_engineered['games']
    X_engineered['key_passes_per_game'] = X_engineered['key_passes'] / X_engineered['games']
    return X_engineered

def evaluate_and_plot_transformations(df_features):
    # Iterar sobre cada columna numerica para aplicar transformaciones y graficar
    for column in df_features.columns:
        print(f"\n--- Analizando: {column} ---")
        
        print("1. Aplica transformacion logaritmica ('np.log1p')")
        log_transformation = np.log1p(df_features[column])

        print("2. Aplica transformacion Yeo-Johnson con 'PowerTransformer'")
        power_transformer = PowerTransformer(method='yeo-johnson', standardize=True)
        yeo_johnson_transformation = pd.DataFrame(
            power_transformer.fit_transform(df_features[[column]]), 
            columns=[column]
        )

        print("3. Generando graficos comparativos...")
        # Concatenamos reiniciando el indice para evitar problemas de alineacion con pandas
        transformations_df = pd.concat([
            df_features[column].reset_index(drop=True), 
            log_transformation.reset_index(drop=True), 
            yeo_johnson_transformation.reset_index(drop=True)
        ], axis=1)
        
        transformations_df.columns = ["Original", "Logaritmica", "Yeo-Johnson"]

        # Crear figura con 3 subgraficos
        fig, axes = plt.subplots(1, 3, figsize=(20, 7))
        axes = axes.flatten()

        # Grafico 1: Datos originales
        axes[0].hist(transformations_df['Original'], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[0].set_title("SIN ESCALAR", fontweight='bold', fontsize=12)
        axes[0].set_xlabel(column)
        axes[0].axvline(transformations_df['Original'].mean(), color='red', linestyle='--', alpha=0.7, label='Media')
        axes[0].legend(fontsize=8, loc='upper right') 

        # Grafico 2: Transformacion Logaritmica
        axes[1].hist(transformations_df['Logaritmica'], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[1].set_title("TRANSFORMACION LOGARITMICA", fontweight='bold', fontsize=12)
        axes[1].set_xlabel(column)
        axes[1].axvline(transformations_df['Logaritmica'].mean(), color='red', linestyle='--', alpha=0.7, label='Media')
        axes[1].legend(fontsize=8, loc='upper right')

        # Grafico 3: Transformacion Yeo-Johnson
        axes[2].hist(transformations_df['Yeo-Johnson'], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[2].set_title("TRANSFORMACION YEO-JOHNSON", fontweight='bold', fontsize=12)
        axes[2].set_xlabel(column)
        axes[2].axvline(transformations_df['Yeo-Johnson'].mean(), color='red', linestyle='--', alpha=0.7, label='Media')
        axes[2].legend(fontsize=8, loc='upper right')

        plt.suptitle(f'Analisis de Sesgo: {column}', fontsize=14, fontweight='bold', y=1)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # 1. Configuracion inicial
    setup_warnings()
    file_path = "data_output/Estadisticas_Jugadores.csv"

    # 2. Carga y preprocesamiento de datos
    df_raw = load_data(file_path)
    X_features = process_target_variable(df_raw)
    
    # 3. Ingenieria de caracteristicas
    X_engineered = engineer_features(X_features)

    # 4. Evaluacion de sesgo y visualizacion
    evaluate_and_plot_transformations(X_engineered)