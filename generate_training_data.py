"""
Generate synthetic training data for ML risk predictor
This creates realistic training examples for the machine learning model
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random

def generate_synthetic_training_data(n_samples=2000):
    """
    Generate synthetic training data for adverse event prediction
    
    This creates realistic examples with correlations between:
    - Number of drugs and interaction risk
    - Patient age and adverse event risk
    - Severity of interactions and outcomes
    - Comorbidities and risk factors
    
    Args:
        n_samples: Number of training examples to generate
    
    Returns:
        List of training examples with features and outcomes
    """
    np.random.seed(42)
    random.seed(42)
    
    training_data = []
    
    # Drug names for realistic examples
    common_drugs = [
        "Warfarin", "Aspirin", "Metformin", "Lisinopril", "Amlodipine",
        "Atorvastatin", "Omeprazole", "Metoprolol", "Levothyroxine", "Losartan",
        "Gabapentin", "Hydrochlorothiazide", "Albuterol", "Sertraline", "Furosemide"
    ]
    
    print(f"🔬 Generating {n_samples} synthetic training examples...")
    print(f"   This simulates real-world drug interaction scenarios")
    
    for i in range(n_samples):
        if (i + 1) % 500 == 0:
            print(f"   Progress: {i + 1}/{n_samples} ({(i+1)/n_samples*100:.1f}%)")
        
        # Generate features with realistic correlations
        num_drugs = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                                     p=[0.05, 0.15, 0.20, 0.20, 0.15, 0.10, 0.07, 0.05, 0.02, 0.01])
        
        # Select random drugs
        selected_drugs = random.sample(common_drugs, min(num_drugs, len(common_drugs)))
        
        # More drugs = higher chance of interactions
        # Contraindicated interactions are rare but serious
        if num_drugs >= 5:
            num_contraindicated = np.random.choice([0, 1, 2], p=[0.80, 0.15, 0.05])
        elif num_drugs >= 3:
            num_contraindicated = np.random.choice([0, 1], p=[0.95, 0.05])
        else:
            num_contraindicated = 0
        
        # Serious interactions more common with polypharmacy
        if num_drugs >= 4:
            num_serious = np.random.choice([0, 1, 2, 3], p=[0.50, 0.30, 0.15, 0.05])
        elif num_drugs >= 2:
            num_serious = np.random.choice([0, 1, 2], p=[0.70, 0.25, 0.05])
        else:
            num_serious = 0
        
        # Significant interactions fairly common
        num_significant = 0
        if num_drugs >= 2:
            num_significant = np.random.poisson(num_drugs * 0.3)
            num_significant = min(num_significant, num_drugs)
        
        # Minor interactions very common
        num_minor = np.random.poisson(num_drugs * 0.4)
        num_minor = min(num_minor, num_drugs * 2)
        
        # Patient demographics
        # Age distribution: skewed toward elderly
        age_group = np.random.choice(['young', 'middle', 'elderly'], p=[0.15, 0.35, 0.50])
        if age_group == 'young':
            patient_age = int(np.random.uniform(18, 40))
        elif age_group == 'middle':
            patient_age = int(np.random.uniform(40, 65))
        else:
            patient_age = int(np.random.uniform(65, 95))
        
        is_geriatric = patient_age >= 65
        
        # Comorbidities more common in elderly
        if is_geriatric:
            has_renal_impairment = np.random.random() < 0.25
            has_hepatic_impairment = np.random.random() < 0.15
            num_chronic_conditions = np.random.choice([0, 1, 2, 3, 4, 5, 6], 
                                                       p=[0.05, 0.15, 0.25, 0.25, 0.15, 0.10, 0.05])
        else:
            has_renal_impairment = np.random.random() < 0.08
            has_hepatic_impairment = np.random.random() < 0.05
            num_chronic_conditions = np.random.choice([0, 1, 2, 3], 
                                                       p=[0.40, 0.35, 0.20, 0.05])
        
        polypharmacy = num_drugs >= 5
        
        # Allergies
        num_allergies = np.random.choice([0, 1, 2, 3], p=[0.70, 0.20, 0.08, 0.02])
        
        # Calculate risk score using rule-based approach
        risk_score = 0
        risk_score += num_contraindicated * 30
        risk_score += num_serious * 15
        risk_score += num_significant * 7
        risk_score += num_minor * 2
        
        # Age factor
        if patient_age >= 80:
            risk_score *= 1.4
        elif is_geriatric:
            risk_score *= 1.3
        
        # Organ impairment
        if has_renal_impairment:
            risk_score *= 1.25
        if has_hepatic_impairment:
            risk_score *= 1.25
        
        # Polypharmacy
        if polypharmacy:
            risk_score *= 1.2
        
        # Allergies and chronic conditions
        risk_score += num_allergies * 10
        risk_score += num_chronic_conditions * 3
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Determine if adverse event occurred
        # This is the target variable we're trying to predict
        
        # Base probability from risk score
        base_prob = risk_score / 100
        
        # Adjust probability based on specific risk factors
        if num_contraindicated > 0:
            base_prob = min(base_prob * 2.5, 0.95)  # Very high risk
        elif num_serious > 0:
            base_prob = min(base_prob * 1.8, 0.85)
        
        # Geriatric patients more vulnerable
        if is_geriatric:
            base_prob = min(base_prob * 1.3, 0.90)
        
        # Organ impairment increases risk
        if has_renal_impairment or has_hepatic_impairment:
            base_prob = min(base_prob * 1.2, 0.90)
        
        # Add some randomness (clinical variation)
        noise = np.random.normal(0, 0.1)
        final_prob = max(0.0, min(1.0, base_prob + noise))
        
        # Determine outcome
        adverse_event_occurred = 1 if np.random.random() < final_prob else 0
        
        # For very safe regimens, force no adverse event
        if num_contraindicated == 0 and num_serious == 0 and risk_score < 20:
            if np.random.random() < 0.92:  # 92% of safe regimens have no events
                adverse_event_occurred = 0
        
        # Create training example
        example = {
            # Input features
            'drugs_checked': [{"drug_id": f"DRUG_{j}", "drug_name": drug} 
                             for j, drug in enumerate(selected_drugs)],
            'severity_summary': {
                'CONTRAINDICATED': int(num_contraindicated),
                'SERIOUS': int(num_serious),
                'SIGNIFICANT': int(num_significant),
                'MINOR': int(num_minor)
            },
            'allergy_alerts': [f"ALLERGY_{j}" for j in range(num_allergies)],
            'patient_age': int(patient_age),
            'has_renal_impairment': bool(has_renal_impairment),
            'has_hepatic_impairment': bool(has_hepatic_impairment),
            'num_chronic_conditions': int(num_chronic_conditions),
            
            # Target (what we're trying to predict)
            'adverse_event_occurred': int(adverse_event_occurred),
            
            # Metadata (for analysis, not used in training)
            'risk_score': float(risk_score),
            'adverse_event_probability': float(final_prob),
            'age_group': age_group,
            'generated_at': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
        }
        
        training_data.append(example)
    
    print(f"   ✅ Generated {len(training_data)} examples")
    return training_data


def analyze_training_data(training_data):
    """Analyze and print statistics about the training data"""
    print(f"\n📊 TRAINING DATA STATISTICS")
    print(f"=" * 60)
    
    # Basic stats
    total = len(training_data)
    adverse_events = sum(ex['adverse_event_occurred'] for ex in training_data)
    no_events = total - adverse_events
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total examples: {total:,}")
    print(f"   Adverse events: {adverse_events:,} ({adverse_events/total*100:.1f}%)")
    print(f"   No adverse events: {no_events:,} ({no_events/total*100:.1f}%)")
    
    # Risk score stats
    risk_scores = [ex['risk_score'] for ex in training_data]
    print(f"\n⚠️  Risk Score Distribution:")
    print(f"   Mean: {np.mean(risk_scores):.1f}")
    print(f"   Median: {np.median(risk_scores):.1f}")
    print(f"   Min: {min(risk_scores):.1f}")
    print(f"   Max: {max(risk_scores):.1f}")
    print(f"   Std: {np.std(risk_scores):.1f}")
    
    # Severity distribution
    print(f"\n🔍 Interaction Severity:")
    contraindicated = sum(ex['severity_summary']['CONTRAINDICATED'] for ex in training_data)
    serious = sum(ex['severity_summary']['SERIOUS'] for ex in training_data)
    significant = sum(ex['severity_summary']['SIGNIFICANT'] for ex in training_data)
    minor = sum(ex['severity_summary']['MINOR'] for ex in training_data)
    
    print(f"   Contraindicated: {contraindicated}")
    print(f"   Serious: {serious}")
    print(f"   Significant: {significant}")
    print(f"   Minor: {minor}")
    
    # Patient demographics
    ages = [ex['patient_age'] for ex in training_data]
    geriatric = sum(1 for ex in training_data if ex['patient_age'] >= 65)
    renal = sum(1 for ex in training_data if ex['has_renal_impairment'])
    hepatic = sum(1 for ex in training_data if ex['has_hepatic_impairment'])
    
    print(f"\n👥 Patient Demographics:")
    print(f"   Average age: {np.mean(ages):.1f} years")
    print(f"   Geriatric (≥65): {geriatric} ({geriatric/total*100:.1f}%)")
    print(f"   Renal impairment: {renal} ({renal/total*100:.1f}%)")
    print(f"   Hepatic impairment: {hepatic} ({hepatic/total*100:.1f}%)")
    
    # Drug count distribution
    drug_counts = [len(ex['drugs_checked']) for ex in training_data]
    polypharmacy = sum(1 for count in drug_counts if count >= 5)
    
    print(f"\n💊 Medication Statistics:")
    print(f"   Average drugs per patient: {np.mean(drug_counts):.1f}")
    print(f"   Polypharmacy (≥5 drugs): {polypharmacy} ({polypharmacy/total*100:.1f}%)")
    
    print(f"\n" + "=" * 60)


def save_training_data(training_data, filename='training_data.json'):
    """Save training data to JSON and CSV files"""
    print(f"\n💾 Saving training data...")
    
    # Save JSON (full data)
    with open(filename, 'w') as f:
        json.dump(training_data, f, indent=2)
    print(f"   ✅ Saved to {filename}")
    
    # Create CSV for easy inspection
    df_data = []
    for example in training_data:
        row = {
            'num_drugs': len(example['drugs_checked']),
            'num_contraindicated': example['severity_summary']['CONTRAINDICATED'],
            'num_serious': example['severity_summary']['SERIOUS'],
            'num_significant': example['severity_summary']['SIGNIFICANT'],
            'num_minor': example['severity_summary']['MINOR'],
            'patient_age': example['patient_age'],
            'is_geriatric': int(example['patient_age'] >= 65),
            'has_renal_impairment': int(example['has_renal_impairment']),
            'has_hepatic_impairment': int(example['has_hepatic_impairment']),
            'num_chronic_conditions': example['num_chronic_conditions'],
            'num_allergies': len(example['allergy_alerts']),
            'polypharmacy': int(len(example['drugs_checked']) >= 5),
            'risk_score': round(example['risk_score'], 1),
            'adverse_event': example['adverse_event_occurred']
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    csv_filename = filename.replace('.json', '.csv')
    df.to_csv(csv_filename, index=False)
    print(f"   ✅ Saved to {csv_filename}")
    
    print(f"\n   📁 Files created:")
    print(f"   - {filename} (complete data for training)")
    print(f"   - {csv_filename} (preview/analysis)")


if __name__ == "__main__":
    print("=" * 60)
    print("SYNTHETIC TRAINING DATA GENERATOR")
    print("ML Risk Predictor Model")
    print("=" * 60)
    
    # Generate training data
    training_data = generate_synthetic_training_data(n_samples=2000)
    
    # Analyze the data
    analyze_training_data(training_data)
    
    # Save to files
    save_training_data(training_data)
    
    print(f"\n✅ TRAINING DATA GENERATION COMPLETE!")
    print(f"=" * 60)
    print(f"\n📝 Next steps:")
    print(f"   1. Review training_data.csv to inspect the data")
    print(f"   2. Run: python train_ml_model.py")
    print(f"   3. Model will be saved to: models/risk_prediction_model.pkl")
    print(f"=" * 60)
