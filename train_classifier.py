import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Step 1: Load Dataset
df = pd.read_csv("exercise_data.csv")

# Step 2: Features & Labels
X = df[["elbow_angle", "knee_angle", "shoulder_angle"]]
y = df["label"]

# Step 3: Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate
y_pred = model.predict(X_test)
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))
print(f"✅ Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# Step 6: Save model
joblib.dump(model, "exercise_classifier.pkl")
print("\n💾 Model saved as: exercise_classifier.pkl")
