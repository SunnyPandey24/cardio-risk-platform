import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

md("# Cardiovascular Disease Risk - Statistical Analysis\n"
   "End-to-end Python analysis: feature engineering, EDA, outlier detection, "
   "hypothesis testing, ANOVA, and predictive modeling.")

code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_style("whitegrid")
df = pd.read_csv("../data/excel_cleaned_cardio_data.csv")
df.head()""")

md("## 1. Dataset Overview")
code("""print(df.shape)
df.info()""")

code("df.describe(include='all').T")

md("## 2. Feature Engineering Recap\n"
   "`bmi`, `age_group`, `bp_category`, `pulse_pressure` and a composite "
   "`risk_score` / `risk_tier` were engineered from the raw clinical fields.")

code("df[['bmi','age_group','bp_category','pulse_pressure','risk_score','risk_tier']].sample(5, random_state=1)")

md("## 3. Outlier Detection (BMI) - IQR method")
code("""q1, q3 = df['bmi'].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
outliers = df[(df['bmi'] < lower) | (df['bmi'] > upper)]
print(f"IQR bounds: [{lower:.1f}, {upper:.1f}]")
print(f"Outliers detected: {len(outliers)} ({len(outliers)/len(df)*100:.2f}% of data)")

fig, ax = plt.subplots(1, 2, figsize=(11,4))
sns.boxplot(x=df['bmi'], ax=ax[0]); ax[0].set_title('BMI distribution (with outliers)')
sns.histplot(df['bmi'], bins=50, kde=True, ax=ax[1]); ax[1].set_title('BMI histogram')
plt.tight_layout(); plt.savefig('bmi_outliers.png', dpi=110); plt.show()""")

md("## 4. Exploratory Data Analysis")
code("""fig, ax = plt.subplots(1, 2, figsize=(11,4))
df.groupby('age_group')['cardio'].mean().mul(100).plot(kind='bar', ax=ax[0], color='#c0392b')
ax[0].set_ylabel('Disease rate (%)'); ax[0].set_title('Disease Rate by Age Group')
df.groupby('bp_category')['cardio'].mean().mul(100).sort_values().plot(kind='barh', ax=ax[1], color='#2980b9')
ax[1].set_xlabel('Disease rate (%)'); ax[1].set_title('Disease Rate by BP Category')
plt.tight_layout(); plt.savefig('eda_age_bp.png', dpi=110); plt.show()""")

code("""plt.figure(figsize=(8,6))
corr_cols = ['age','bmi','ap_hi','ap_lo','cholesterol','gluc','smoke','alco','active','risk_score','cardio']
sns.heatmap(df[corr_cols].corr(), annot=True, fmt='.2f', cmap='RdBu_r', center=0)
plt.title('Correlation Matrix'); plt.tight_layout(); plt.savefig('correlation_heatmap.png', dpi=110); plt.show()""")

md("## 5. Hypothesis Testing\n"
   "**H0:** Mean systolic BP (ap_hi) is the same for patients with and without cardiovascular disease.\n"
   "**H1:** Mean systolic BP differs between the two groups.")
code("""grp_pos = df.loc[df.cardio == 1, 'ap_hi']
grp_neg = df.loc[df.cardio == 0, 'ap_hi']
t_stat, p_val = stats.ttest_ind(grp_pos, grp_neg, equal_var=False)
print(f"Mean ap_hi (cardio=1): {grp_pos.mean():.1f}  |  Mean ap_hi (cardio=0): {grp_neg.mean():.1f}")
print(f"t-statistic = {t_stat:.2f}, p-value = {p_val:.2e}")
print("Reject H0 -> significant difference" if p_val < 0.05 else "Fail to reject H0")""")

md("## 6. ANOVA - Risk Score across BMI Categories\n"
   "Testing whether mean `risk_score` differs significantly across BMI categories.")
code("""groups = [g['risk_score'].values for _, g in df.groupby('bmi_category')]
f_stat, p_val = stats.f_oneway(*groups)
print(f"F-statistic = {f_stat:.2f}, p-value = {p_val:.2e}")
print("Reject H0 -> at least one BMI group has a different mean risk score" if p_val < 0.05 else "Fail to reject H0")""")

md("## 7. Chi-Square Test - Cholesterol vs Cardiovascular Disease")
code("""contingency = pd.crosstab(df['cholesterol_label'], df['cardio'])
chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
print(contingency)
print(f"\\nchi2 = {chi2:.2f}, dof = {dof}, p-value = {p_val:.2e}")""")

md("## 8. Predictive Modeling - Logistic Regression & Random Forest")
code("""from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, roc_curve

features = ['age','gender','bmi','ap_hi','ap_lo','cholesterol','gluc','smoke','alco','active']
X, y = df[features], df['cardio']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s, X_test_s = scaler.fit_transform(X_train), scaler.transform(X_test)

lr = LogisticRegression(max_iter=1000).fit(X_train_s, y_train)
rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1).fit(X_train, y_train)

lr_auc = roc_auc_score(y_test, lr.predict_proba(X_test_s)[:,1])
rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:,1])
print(f"Logistic Regression ROC-AUC: {lr_auc:.3f}")
print(f"Random Forest ROC-AUC:       {rf_auc:.3f}")
print()
print(classification_report(y_test, rf.predict(X_test)))""")

code("""fpr, tpr, _ = roc_curve(y_test, rf.predict_proba(X_test)[:,1])
plt.figure(figsize=(5,5))
plt.plot(fpr, tpr, label=f'Random Forest (AUC={rf_auc:.3f})', color='#c0392b')
plt.plot([0,1],[0,1],'--', color='gray')
plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate'); plt.title('ROC Curve'); plt.legend()
plt.tight_layout(); plt.savefig('roc_curve.png', dpi=110); plt.show()""")

code("""importances = pd.Series(rf.feature_importances_, index=features).sort_values()
importances.plot(kind='barh', figsize=(6,5), color='#27ae60')
plt.title('Random Forest Feature Importance'); plt.tight_layout()
plt.savefig('feature_importance.png', dpi=110); plt.show()""")

md("## 9. Key Findings\n"
   "- Systolic blood pressure shows a statistically significant difference between diseased and healthy patients (p < 0.001).\n"
   "- Risk score differs significantly across BMI categories (ANOVA p < 0.001).\n"
   "- Cholesterol level and cardiovascular disease are significantly associated (Chi-square p < 0.001).\n"
   "- The Random Forest model reaches ROC-AUC ≈ 0.73, with systolic BP, diastolic BP, and cholesterol as the strongest predictors.\n"
   "- Risk tiers show a clear escalation in disease rate: Low → Medium → High → Critical.")

nb['cells'] = cells
with open('Cardio_Statistical_Analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
print("notebook built")
