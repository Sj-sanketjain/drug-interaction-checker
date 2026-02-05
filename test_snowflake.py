from config.settings import settings

print("Testing Snowflake Configuration:")
print(f"Account: {settings.snowflake_account}")
print(f"User: {settings.snowflake_user}")
print(f"Database: {settings.snowflake_database}")
print(f"Schema: {settings.snowflake_schema}")

# Try connection
from database.connection import db_manager

if db_manager.connect():
    print("✅ Snowflake connection successful!")
else:
    print("❌ Snowflake connection failed!")

# test_ml_model.py
# from services.ml_risk_predictor import risk_predictor

# # Check if model is loaded
# if risk_predictor.model is not None:
#     print("✅ ML Model is LOADED")
#     print(f"   Model version: {risk_predictor.model_version}")
    
#     # Test prediction
#     test_data = {
#         'num_drugs': 3,
#         'num_contraindicated': 0,
#         'num_serious': 1,
#         'num_significant': 1,
#         'num_minor': 0,
#         'patient_age': 65,
#         'is_geriatric': True,
#         'has_renal_impairment': False,
#         'has_hepatic_impairment': False,
#         'num_chronic_conditions': 2,
#         'polypharmacy': False,
#         'num_allergies': 0
#     }
    
#     result = risk_predictor.predict_risk(test_data)
#     print(f"   Test prediction: {result.risk_score:.1f}/100 ({result.risk_category})")
# else:
#     print("❌ ML Model NOT loaded - using rule-based fallback")