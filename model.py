import numpy as np
import matplotlib.pyplot as plt
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.optimizers import Adam
from itertools import combinations
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_text
import shap

# Beispiel-Daten
input_data = list(combinations(range(14), 7))


def read_num_sols_per_puzzle(filename=None):
    """Liest die Textdatei mit den Lösungen pro Puzzle aus"""
    if filename is None:
        filename = "3432.txt"
    sols_pp = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    for line in lines:
        sols_pp.append(int(line))
    return tuple(sols_pp)


# Eingabedaten in binäre Vektoren umwandeln
def to_binary_vector(indices, length=14):
    vector = [0] * length
    for index in indices:
        vector[index] = 1
    return vector


output_data = read_num_sols_per_puzzle()

X = np.array([to_binary_vector(tup) for tup in input_data])
y = np.array(output_data)

# Normiere die Eingabedaten
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Aufteilen in Trainings- und Testdaten
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Definiere das Modell
# model = Sequential()
# model.add(Dense(64, input_dim=X.shape[1], activation='relu'))
# model.add(Dense(32, activation='relu'))
# model.add(Dense(1, activation='linear'))
#
# # Kompiliere das Modell
# model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
#
# # Trainiere das Modell
# model.fit(X_train, y_train, epochs=100, batch_size=1, verbose=1)
#
# # Vorhersagen machen
# train_predictions = model.predict(X_train)
# test_predictions = model.predict(X_test)
# print("Train Predictions:", train_predictions)
# print("Test Predictions:", test_predictions)
#
# # Gewichtungen des Netzes analysieren
# for layer in model.layers:
#     weights = layer.get_weights()
#     print(weights)
#
# # MSE berechnen
# train_mse = mean_squared_error(y_train, train_predictions)
# test_mse = mean_squared_error(y_test, test_predictions)
# print(f"Train MSE: {train_mse}")
# print(f"Test MSE: {test_mse}")

# Definiere den Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Trainiere das Modell
rf_model.fit(X_train, y_train)

# Vorhersagen machen
train_predictions_rf = rf_model.predict(X_train)
test_predictions_rf = rf_model.predict(X_test)

# MSE berechnen
train_mse_rf = mean_squared_error(y_train, train_predictions_rf)
test_mse_rf = mean_squared_error(y_test, test_predictions_rf)
print(f"Random Forest Train MSE: {train_mse_rf}")
print(f"Random Forest Test MSE: {test_mse_rf}")

# Plot: Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Test)
# plt.figure(figsize=(10, 6))
# plt.plot(y_test, label='Tatsächliche Ausgabedaten (Test)', marker='o')
# plt.plot(test_predictions_rf, label='Vorhersagen des Modells (Test)', marker='x')
# plt.xlabel('Datenpunkt')
# plt.ylabel('Wert')
# plt.title('Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Test) RF')
# plt.legend()
# plt.show()
#
# # Plot: Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Train)
# plt.figure(figsize=(10, 6))
# plt.plot(y_train, label='Tatsächliche Ausgabedaten (Train)', marker='o')
# plt.plot(train_predictions_rf, label='Vorhersagen des Modells (Train)', marker='x')
# plt.xlabel('Datenpunkt')
# plt.ylabel('Wert')
# plt.title('Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Train) RF')
# plt.legend()
# plt.show()

# Plot: Tatsächliche Ausgabedaten vs. Vorhersagen des Modells
# plt.figure(figsize=(10, 6))
# plt.plot(y_test, label='Tatsächliche Ausgabedaten (Test)', marker='o')
# plt.plot(test_predictions, label='Vorhersagen des Modells (Test)', marker='x')
# plt.xlabel('Datenpunkt')
# plt.ylabel('Wert')
# plt.title('Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Test) NN')
# plt.legend()
# plt.show()
#
# # Plot: Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Train)
# plt.figure(figsize=(10, 6))
# plt.plot(y_train, label='Tatsächliche Ausgabedaten (Train)', marker='o')
# plt.plot(train_predictions, label='Vorhersagen des Modells (Train)', marker='x')
# plt.xlabel('Datenpunkt')
# plt.ylabel('Wert')
# plt.title('Tatsächliche Ausgabedaten vs. Vorhersagen des Modells (Train) NN')
# plt.legend()
# plt.show()

# Feature-Wichtigkeit extrahieren
feature_importances = rf_model.feature_importances_

# Visualisieren
plt.figure(figsize=(12, 8))
plt.bar(range(X.shape[1]), feature_importances, tick_label=[f'var_{i}' for i in range(X.shape[1])])
plt.xlabel('Feature')
plt.ylabel('Wichtigkeit')
plt.title('Feature-Wichtigkeit im Random Forest')
plt.show()


# Struktur eines Entscheidungsbaums drucken
# Wir nehmen den ersten Baum aus dem Wald (rf_model.estimators_[0])
tree = rf_model.estimators_[0]

# Exportiere die Struktur des Entscheidungsbaums als Text
tree_rules = export_text(tree, feature_names=[f'var_{i}' for i in range(X.shape[1])])

# Drucke die Struktur
# print(tree_rules)

# # SHAP-Werte berechnen und plotten (optional, wenn du die SHAP-Bibliothek installiert hast)
# background_sample = shap.sample(X_scaled, 100)
# explainer = shap.KernelExplainer(model.predict, background_sample)
# shap_values = explainer.shap_values(X_scaled)
# shap.summary_plot(shap_values, X_scaled, feature_names=[f'var_{i}' for i in range(X.shape[1])])

# SHAP-Werte berechnen
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_scaled)

# Zusammenfassung der SHAP-Werte plotten
shap.summary_plot(shap_values, X_scaled, feature_names=[f'var_{i}' for i in range(X.shape[1])])
