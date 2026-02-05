"""
Train the ML Risk Prediction Model

This script:
1. Loads training data from training_data.json
2. Trains a Random Forest classifier
3. Evaluates performance on test set
4. Saves the trained model
5. Shows feature importance
"""
import asyncio
import json
import numpy as np
import os
from services.ml_risk_predictor import risk_predictor
from loguru import logger

async def train_model():
    """Train the ML risk prediction model"""
    
    print("=" * 60)
    print("ML RISK PREDICTOR - MODEL TRAINING")
    print("=" * 60)
    
    # Load training data
    print("\n1️⃣  Loading training data...")
    try:
        with open('training_data.json', 'r') as f:
            training_data = json.load(f)
        print(f"   ✅ Loaded {len(training_data)} training examples")
    except FileNotFoundError:
        print("   ❌ ERROR: training_data.json not found")
        print("\n   Run this first:")
        print("   python generate_training_data.py")
        return
    except json.JSONDecodeError as e:
        print(f"   ❌ ERROR: Invalid JSON in training_data.json")
        print(f"   {e}")
        return
    
    # Validate data quality
    print(f"\n2️⃣  Validating data quality...")
    
    # Check for required fields
    required_fields = [
        'drugs_checked', 'severity_summary', 'allergy_alerts',
        'patient_age', 'has_renal_impairment', 'has_hepatic_impairment',
        'num_chronic_conditions', 'adverse_event_occurred'
    ]
    
    for idx, example in enumerate(training_data[:5]):  # Check first 5 examples
        for field in required_fields:
            if field not in example:
                print(f"   ❌ ERROR: Missing field '{field}' in example {idx}")
                return
    
    print(f"   ✅ Data structure is valid")
    
    # Check class balance
    adverse_events = sum(ex['adverse_event_occurred'] for ex in training_data)
    no_events = len(training_data) - adverse_events
    adverse_rate = adverse_events / len(training_data) * 100
    
    print(f"\n3️⃣  Data Summary:")
    print(f"   Total examples: {len(training_data):,}")
    print(f"   Adverse events: {adverse_events:,} ({adverse_rate:.1f}%)")
    print(f"   No adverse events: {no_events:,} ({(100-adverse_rate):.1f}%)")
    
    if adverse_rate < 10 or adverse_rate > 90:
        print(f"\n   ⚠️  WARNING: Class imbalance detected!")
        print(f"   Adverse event rate is {adverse_rate:.1f}%")
        print(f"   This may affect model performance")
    else:
        print(f"   ✅ Class balance is reasonable")
    
    # Train model
    print(f"\n4️⃣  Training Random Forest model...")
    print(f"   This may take 30-60 seconds...")
    
    try:
        metrics = await risk_predictor.train_model(training_data)
        
        print(f"\n5️⃣  ✅ TRAINING COMPLETE!")
        print(f"   " + "=" * 56)
        
        print(f"\n   📊 Model Performance Metrics:")
        print(f"   ┌{'─' * 54}┐")
        print(f"   │ {'Metric':<20} {'Score':<15} {'Interpretation':<16} │")
        print(f"   ├{'─' * 54}┤")
        print(f"   │ {'Accuracy':<20} {metrics['accuracy']*100:>6.2f}% {_interpret_accuracy(metrics['accuracy']):<20} │")
        print(f"   │ {'Precision':<20} {metrics['precision']*100:>6.2f}% {_interpret_precision(metrics['precision']):<20} │")
        print(f"   │ {'Recall':<20} {metrics['recall']*100:>6.2f}% {_interpret_recall(metrics['recall']):<20} │")
        print(f"   │ {'ROC-AUC':<20} {metrics['roc_auc']:>6.3f}  {_interpret_roc_auc(metrics['roc_auc']):<20} │")
        print(f"   └{'─' * 54}┘")
        
        print(f"\n   📈 Dataset Split:")
        print(f"   Training examples: {metrics['training_samples']:,}")
        print(f"   Test examples: {metrics['test_samples']:,}")
        print(f"   Test set ratio: {metrics['test_samples']/(metrics['training_samples']+metrics['test_samples'])*100:.1f}%")
        
        # Feature importance
        if risk_predictor.feature_importance:
            print(f"\n   🎯 Top 5 Most Important Features:")
            sorted_features = sorted(
                risk_predictor.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for i, (feature, importance) in enumerate(sorted_features[:5], 1):
                bar_length = int(importance * 30)
                bar = '█' * bar_length
                print(f"   {i}. {feature:<25} {bar} {importance:.3f}")
        
        print(f"\n   💾 Model saved to: models/risk_prediction_model.pkl")
        
        # Test the model with a sample prediction
        print(f"\n6️⃣  Testing prediction...")
        test_data = training_data[0]
        result = await risk_predictor.predict_risk(test_data)
        
        print(f"   ✅ Prediction successful!")
        print(f"   Sample prediction:")
        print(f"   ├─ Risk Score: {result.risk_score:.1f}/100")
        print(f"   ├─ Risk Category: {result.risk_category.upper()}")
        print(f"   ├─ Adverse Event Probability: {result.probability_adverse_event:.1%}")
        print(f"   └─ Confidence: {result.confidence:.1%}")
        
        print(f"\n" + "=" * 60)
        print(f"✅ MODEL TRAINING SUCCESSFUL!")
        print(f"=" * 60)
        
        print(f"\n📝 Next steps:")
        print(f"   1. Restart your application")
        print(f"   2. The ML predictor will now use the trained model")
        print(f"   3. Check /check-interactions endpoint for ML predictions")
        print(f"   4. Monitor prediction quality over time")
        
        print(f"\n💡 Tips:")
        print(f"   - Model improves with more training data")
        print(f"   - Retrain periodically with real clinical outcomes")
        print(f"   - Compare ML predictions with rule-based system")
        
        print(f"\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR during training: {type(e).__name__}")
        print(f"   {str(e)}")
        print(f"\n🔍 Troubleshooting:")
        print(f"   1. Check training_data.json is valid")
        print(f"   2. Ensure required Python packages installed:")
        print(f"      pip install scikit-learn numpy")
        print(f"   3. Check logs for detailed error")
        
        print(f"\n📋 Full error details:")
        import traceback
        traceback.print_exc()


def _interpret_accuracy(score):
    """Interpret accuracy score"""
    if score >= 0.90:
        return "Excellent"
    elif score >= 0.80:
        return "Good"
    elif score >= 0.70:
        return "Fair"
    else:
        return "Needs improvement"


def _interpret_precision(score):
    """Interpret precision score"""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.65:
        return "Fair"
    else:
        return "Low"


def _interpret_recall(score):
    """Interpret recall score"""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.65:
        return "Fair"
    else:
        return "Low - may miss events"


def _interpret_roc_auc(score):
    """Interpret ROC-AUC score"""
    if score >= 0.90:
        return "Excellent"
    elif score >= 0.80:
        return "Good"
    elif score >= 0.70:
        return "Fair"
    else:
        return "Poor"


async def retrain_model():
    """Retrain with additional data (future use)"""
    print("\n🔄 Model retraining not yet implemented")
    print("   This would load existing model and training data,")
    print("   add new examples, and retrain")


if __name__ == "__main__":
    try:
        asyncio.run(train_model())
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
