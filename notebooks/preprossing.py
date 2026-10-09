# %%
import pandas as pd
import numpy as np
from sklearn.preprocessing  import LabelEncoder 
from imblearn.over_sampling import SMOTE


# %%
##load dataset 
df=pd.read_csv("dataset.csv")
print(df.head(5))

# %%
#drop unwanted row
df = df.drop(['UDI', 'Product ID'], axis=1)

#encode the type values
le_type=LabelEncoder()
df["Type"]=le_type.fit_transform(df["Type"])






# %%
# class imbalnce 
# Since failures are only 3.4%, model may always predict 0.


X = df.drop(['Target', 'Failure Type'], axis=1)
y = df['Target']

sm = SMOTE(random_state=42)
X_resampled, y_resampled = sm.fit_resample(X, y)



# %%
#features and target
X = df.drop(['Target', 'Failure Type'], axis=1)
y = df['Target']
# ----------------------

# %%
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    stratify=y,  # VERY IMPORTANT for imbalance
    random_state=42
)

# %%
from sklearn.ensemble import RandomForestClassifier

binary_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight={0:1, 1:5},
    random_state=42,
    n_jobs=-1
)

binary_model.fit(X_train, y_train)

# %%
# Get probabilities instead of direct class prediction
y_prob = binary_model.predict_proba(X_test)[:, 1]

# Change threshold (try 0.35 first)
y_pred_custom = (y_prob > 0.35).astype(int)

# %%
from sklearn.metrics import classification_report, confusion_matrix,accuracy_score

y_pred = binary_model.predict(X_test)
print(accuracy_score(y_test,y_pred_custom))
print(confusion_matrix(y_test, y_pred_custom))
print(classification_report(y_test, y_pred_custom))

# %%
for t in [0.5, 0.4, 0.35, 0.3, 0.25]:
    y_pred_custom = (y_prob > t).astype(int)
    print("Threshold:", t)
    print(classification_report(y_test, y_pred_custom))
# ---------------------------------------------
# %%
# if failure 
df_failures = df[df['Target'] == 1].copy()
print(df_failures['Failure Type'].value_counts())


# %%
df_failures = df_failures[df_failures['Failure Type'] != 'No Failure']
print(df_failures['Failure Type'].value_counts())


# %%
df_failures = df_failures.drop(['Target'], axis=1)
print(df_failures.head(5))

# %%
le_failure = LabelEncoder()
df_failures['Failure Type'] = le_failure.fit_transform(df_failures['Failure Type'])
# -------------------------------
# %%
X2 = df_failures.drop(['Failure Type'], axis=1)
y2 = df_failures['Failure Type']

# %%
X2_train, X2_test, y2_train, y2_test = train_test_split(
    X2, y2,
    test_size=0.2,
    stratify=y2,
    random_state=42
)

# %%
failure_type_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

failure_type_model.fit(X2_train, y2_train)

# %%
y2_pred = failure_type_model.predict(X2_test)

print(accuracy_score(y2_test,y2_pred))
print(confusion_matrix(y2_test, y2_pred))
print(classification_report(y2_test, y2_pred))

# %%
def predict_machine_status(input_data):
    prob = binary_model.predict_proba(input_data)[:,1]
    
    if prob > 0.35:  # your optimized threshold
        failure_type = failure_type_model.predict(input_data)
        return "Failure", le_failure.inverse_transform(failure_type)
    else:
        return "No Failure", None

# %%
import joblib
joblib.dump(binary_model, "binary_failure_model.pkl")
joblib.dump(failure_type_model, "failure_type_model.pkl")

# %%
joblib.dump(le_failure, "failure_type_encoder.pkl")
joblib.dump(le_type, "type_encoder.pkl")

# %%
BEST_THRESHOLD = 0.35
joblib.dump(BEST_THRESHOLD, "best_threshold.pkl")

# %%
print(df[['Air temperature [K]',
          'Process temperature [K]',
          'Rotational speed [rpm]',
          'Torque [Nm]',
          'Tool wear [min]']].max())


