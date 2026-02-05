"""
Drug Interaction & Allergy Checker - Streamlit Frontend
WITH ALLERGY CHECKING ENABLED
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Drug Interaction Checker",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #667eea;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .severity-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
    }
    .contraindicated {
        background-color: #DC2626;
        color: white;
    }
    .serious {
        background-color: #EA580C;
        color: white;
    }
    .significant {
        background-color: #F59E0B;
        color: white;
    }
    .minor {
        background-color: #FCD34D;
        color: #333;
    }
    .risk-high {
        background-color: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-moderate {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-low {
        background-color: #D1FAE5;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .escalation-banner {
        background-color: #FEE2E2;
        border: 2px solid #DC2626;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        font-weight: bold;
    }
    .urgent-banner {
        background-color: #FEF3C7;
        border: 2px solid #F59E0B;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        font-weight: bold;
    }
    .allergy-severe {
        background-color: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .allergy-moderate {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .allergy-mild {
        background-color: #FEF9C3;
        border-left: 4px solid #EAB308;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_drugs' not in st.session_state:
    st.session_state.selected_drugs = []
if 'results' not in st.session_state:
    st.session_state.results = None
if 'all_drugs' not in st.session_state:
    st.session_state.all_drugs = []
if 'all_patients' not in st.session_state:
    st.session_state.all_patients = []
if 'enable_external_check' not in st.session_state:
    st.session_state.enable_external_check = True
if 'enable_smart_filtering' not in st.session_state:
    st.session_state.enable_smart_filtering = True
if 'enable_allergy_check' not in st.session_state:
    st.session_state.enable_allergy_check = False
if 'selected_patient_id' not in st.session_state:
    st.session_state.selected_patient_id = None


@st.cache_data
def fetch_all_drugs() -> List[Dict]:
    """Fetch all drugs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/drugs", params={"limit": 100})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch drugs: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []


@st.cache_data
def fetch_all_patients() -> List[Dict]:
    """Fetch all patients from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/patients", params={"limit": 100})
        if response.status_code == 200:
            return response.json()
        else:
            # If endpoint doesn't exist, return empty
            return []
    except Exception as e:
        return []


def check_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def check_interactions(
    drug_ids: List[str], 
    include_llm: bool = True,
    include_external_check: bool = True,
    apply_smart_filtering: bool = True,
    check_allergies: bool = False,
    patient_id: str = None
) -> Dict:
    """Check drug interactions with all features"""
    try:
        payload = {
            "drug_ids": drug_ids,
            "patient_id": patient_id,
            "check_allergies": check_allergies,
            "include_llm_analysis": include_llm,
            "include_external_check": include_external_check,
            "apply_smart_filtering": apply_smart_filtering
        }
        
        response = requests.post(
            f"{API_BASE_URL}/check-interactions",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error checking interactions: {e}")
        return None


def get_severity_badge(severity: str) -> str:
    """Get HTML badge for severity level"""
    severity_classes = {
        "CONTRAINDICATED": "contraindicated",
        "SERIOUS": "serious",
        "SIGNIFICANT": "significant",
        "MINOR": "minor",
        "SEVERE": "contraindicated",
        "MODERATE": "serious",
        "MILD": "significant"
    }
    css_class = severity_classes.get(severity, "minor")
    return f'<span class="severity-badge {css_class}">{severity}</span>'


def display_interaction(interaction: Dict):
    """Display a single interaction"""
    severity = interaction.get('severity_level', 'UNKNOWN')
    drug_a = interaction.get('drug_a', {}).get('drug_name', 'Unknown')
    drug_b = interaction.get('drug_b', {}).get('drug_name', 'Unknown')
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{drug_a} + {drug_b}**")
        
        with col2:
            st.markdown(get_severity_badge(severity), unsafe_allow_html=True)
        
        st.markdown(f"**Description:** {interaction.get('description', 'N/A')}")
        
        if interaction.get('clinical_effects'):
            st.markdown(f"**Clinical Effects:** {interaction['clinical_effects']}")
        
        # Show source if from external database
        source = interaction.get('source')
        if source and source not in ['', 'LOCAL']:
            confidence = interaction.get('confidence', 0)
            st.markdown(f"🔍 **Verified by:** {source} (Confidence: {confidence:.0%})")
        
        if interaction.get('management_recommendations'):
            with st.expander("💡 Management Recommendations"):
                st.info(interaction['management_recommendations'])
        
        st.divider()


# def display_allergy_alert(alert: Dict):
#     """Display allergy alert"""
#     severity = alert.get('severity', 'UNKNOWN').upper()
    
#     # Determine CSS class and icon
#     if severity == 'SEVERE':
#         css_class = "allergy-severe"
#         icon = "🚨"
#     elif severity == 'MODERATE':
#         css_class = "allergy-moderate"
#         icon = "⚠️"
#     else:
#         css_class = "allergy-mild"
#         icon = "ℹ️"
    
#     st.markdown(f"""
#     <div class="{css_class}">
#         <h4>{icon} ALLERGY ALERT: {alert['allergen_name']}</h4>
#         <p><strong>Matched Drug:</strong> {alert['matched_drug_name']}</p>
#         <p><strong>Severity:</strong> {severity}</p>
#         <p><strong>Reaction:</strong> {alert.get('reaction_description', 'N/A')}</p>
#     </div>
#     """, unsafe_allow_html=True)

def display_allergy_alert(alert):
    # Convert Pydantic to dict if needed
    if hasattr(alert, 'dict'):  # Pydantic v1
        alert = alert.dict()
    elif hasattr(alert, 'model_dump'):  # Pydantic v2
        alert = alert.model_dump()
    
    st.warning("🔔 **Allergy Alert**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Allergen:** {alert.get('allergen_name', 'Unknown')}")
        st.write(f"**Severity:** {alert.get('severity', 'Unknown')}")
        st.write(f"**Recommendation:** {alert.get('recommendation', 'Consult physician')}")
    
    with col2:
        st.write(f"**Matched Drug:** {alert.get('matched_drug_name', 'Unknown')}")
    
    st.info(alert.get('reaction_description', ''))


def display_escalation_banner(results: Dict):
    """Display escalation warning banner if needed"""
    if results.get('requires_escalation'):
        urgency = results.get('escalation_urgency', 'URGENT')
        
        if urgency == 'IMMEDIATE':
            st.markdown("""
            <div class="escalation-banner">
                🚨 <strong>IMMEDIATE ACTION REQUIRED</strong><br>
                Contraindicated drug interaction detected. Immediate clinical pharmacist consultation required.
            </div>
            """, unsafe_allow_html=True)
        elif urgency == 'URGENT':
            st.markdown("""
            <div class="urgent-banner">
                ⚠️ <strong>URGENT: Clinical Review Needed</strong><br>
                Multiple serious interactions detected. Clinical review recommended within 24 hours.
            </div>
            """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">💊 Drug Interaction & Allergy Checker</div>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Clinical Decision Support System**")
    
    # Check API health
    if not check_health():
        st.error("⚠️ Cannot connect to API. Please ensure the backend is running on http://localhost:8000")
        st.info("Run: `python -m app.main_enhanced` in your project directory")
        st.stop()
    else:
        st.success("✅ Connected to API")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        include_llm = st.checkbox(
            "Include AI Analysis",
            value=True,
            help="Use AI for clinical analysis (may take 3-5 seconds)"
        )
        
        st.divider()
        
        st.header("🚀 Advanced Features")
        
        enable_external_check = st.checkbox(
            "Check External Databases",
            value=st.session_state.enable_external_check,
            help="Verify interactions with RxNorm and FDA databases (adds 2-3 seconds)"
        )
        st.session_state.enable_external_check = enable_external_check
        
        enable_smart_filtering = st.checkbox(
            "Smart Alert Filtering",
            value=st.session_state.enable_smart_filtering,
            help="Filter low-priority alerts to reduce alert fatigue"
        )
        st.session_state.enable_smart_filtering = enable_smart_filtering
        
        # NEW: Allergy checking toggle
        enable_allergy_check = st.checkbox(
            "Check Patient Allergies",
            value=st.session_state.enable_allergy_check,
            help="Check if selected drugs match known patient allergies"
        )
        st.session_state.enable_allergy_check = enable_allergy_check
        
        if enable_smart_filtering:
            st.caption("✅ Shows all critical/serious alerts")
            st.caption("✅ Filters minor interactions")
        
        if enable_external_check:
            st.caption("🔍 Checks: RxNorm + FDA")
            st.caption("⚡ Results cached for 24h")
        
        if enable_allergy_check:
            st.caption("🔍 Checks: Patient allergy records")
            st.caption("⚠️ Requires patient selection")
        
        st.divider()
        
        st.header("📖 About")
        st.markdown("""
        This tool checks for:
        - Drug-drug interactions
        - Patient allergies
        - Severity classification
        - AI-powered analysis
        - Clinical recommendations
        
        **Features:**
        - 🎯 Smart alert filtering
        - 🔍 External database verification
        - 🚨 Automatic escalation
        - ⚠️ Allergy checking
        """)
        
        st.divider()
        
        st.header("🔗 Quick Links")
        st.markdown("[API Documentation](http://localhost:8000/docs)")
        st.markdown("[Health Check](http://localhost:8000/health)")
    
    # Main content
    st.header("1️⃣ Select Patient (Optional)")
    
    # Patient selection (only if allergy checking enabled)
    if enable_allergy_check:
        # Try to fetch patients
        if not st.session_state.all_patients:
            with st.spinner("Loading patients..."):
                st.session_state.all_patients = fetch_all_patients()
        
        if st.session_state.all_patients:
            patient_options = {
                f"{p['patient_id']} - {p.get('first_name', '')} {p.get('last_name', '')} (Age: {p.get('age', 'N/A')})": p['patient_id']
                for p in st.session_state.all_patients
            }
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_patient = st.selectbox(
                    "Select a patient:",
                    options=["-- No patient selected --"] + list(patient_options.keys()),
                    key="patient_selector"
                )
            
            if selected_patient != "-- No patient selected --":
                st.session_state.selected_patient_id = patient_options[selected_patient]
                st.info(f"✅ Selected: {selected_patient}")
            else:
                st.session_state.selected_patient_id = None
                st.warning("⚠️ Please select a patient to check allergies")
        else:
            # Fallback: manual patient ID entry
            st.session_state.selected_patient_id = st.text_input(
                "Enter Patient ID:",
                value="",
                placeholder="e.g., PAT_001",
                help="Enter patient ID to check allergies"
            )
            if st.session_state.selected_patient_id:
                st.info(f"✅ Using Patient ID: {st.session_state.selected_patient_id}")
    else:
        st.info("💡 Enable 'Check Patient Allergies' in settings to select a patient")
    
    st.divider()
    
    st.header("2️⃣ Select Medications")
    
    # Fetch drugs
    if not st.session_state.all_drugs:
        with st.spinner("Loading drugs..."):
            st.session_state.all_drugs = fetch_all_drugs()
    
    if not st.session_state.all_drugs:
        st.error("Failed to load drugs. Please check API connection.")
        st.stop()
    
    # Create drug selection interface
    drug_options = {
        f"{drug['drug_name']} ({drug['generic_name']})": drug['drug_id']
        for drug in st.session_state.all_drugs
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_drug = st.selectbox(
            "Add a drug:",
            options=["-- Select a drug --"] + list(drug_options.keys()),
            key="drug_selector"
        )
    
    with col2:
        if st.button("➕ Add Drug", use_container_width=True):
            if selected_drug != "-- Select a drug --":
                drug_id = drug_options[selected_drug]
                if drug_id not in st.session_state.selected_drugs:
                    st.session_state.selected_drugs.append(drug_id)
                    st.rerun()
                else:
                    st.warning("Drug already added!")
    
    # Display selected drugs
    if st.session_state.selected_drugs:
        st.subheader("Selected Medications:")
        
        cols = st.columns(4)
        for idx, drug_id in enumerate(st.session_state.selected_drugs):
            drug_info = next((d for d in st.session_state.all_drugs if d['drug_id'] == drug_id), None)
            if drug_info:
                with cols[idx % 4]:
                    st.info(f"💊 {drug_info['drug_name']}")
                    if st.button("❌", key=f"remove_{drug_id}"):
                        st.session_state.selected_drugs.remove(drug_id)
                        st.rerun()
        
        st.divider()
        
        # Check interactions button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Check Interactions", type="primary", use_container_width=True):
                if len(st.session_state.selected_drugs) < 2:
                    st.warning("Please select at least 2 drugs to check interactions")
                elif enable_allergy_check and not st.session_state.selected_patient_id:
                    st.warning("Please select a patient to check allergies")
                else:
                    with st.spinner("Analyzing drug interactions... This may take a few seconds."):
                        results = check_interactions(
                            st.session_state.selected_drugs,
                            include_llm,
                            st.session_state.enable_external_check,
                            st.session_state.enable_smart_filtering,
                            enable_allergy_check,
                            st.session_state.selected_patient_id
                        )
                        if results:
                            st.session_state.results = results
                            st.rerun()
    else:
        st.info("👆 Select at least 2 drugs to check for interactions")
    
    # Display results
    if st.session_state.results:
        st.divider()
        st.header("3️⃣ Analysis Results")
        
        results = st.session_state.results
        
        # Display escalation banner at the top if needed
        display_escalation_banner(results)
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Drugs Checked",
                len(results.get('drugs_checked', []))
            )
        
        with col2:
            st.metric(
                "Interactions Found",
                len(results.get('interactions_found', []))
            )
        
        with col3:
            st.metric(
                "Allergy Alerts",
                len(results.get('allergy_alerts', []))
            )
        
        with col4:
            severity_summary = results.get('severity_summary', {})
            critical_count = severity_summary.get('CONTRAINDICATED', 0)
            if critical_count > 0:
                st.metric("⚠️ Critical", critical_count)
            else:
                st.metric("✅ Status", "Safe")
        
        # External database verification status
        if results.get('external_sources_checked', 0) > 0:
            st.success(
                f"✅ Verified against {results['external_sources_checked']} external database source(s) (RxNorm + FDA)"
            )
        
        # Allergy Alerts Section (NEW!)
        if results.get('allergy_alerts'):
            st.divider()
            st.subheader("🚨 Allergy Alerts")
            
            allergy_count = len(results['allergy_alerts'])
            st.error(f"Found {allergy_count} allergy alert(s) for this patient!")
            
            for alert in results['allergy_alerts']:
                display_allergy_alert(alert)
            
            st.divider()
        
        # Severity breakdown
        st.subheader("📊 Severity Breakdown")
        severity_summary = results.get('severity_summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            count = severity_summary.get('CONTRAINDICATED', 0)
            st.markdown(f"**Contraindicated:** {count}")
            if count > 0:
                st.error("⛔ Never use together")
        
        with col2:
            count = severity_summary.get('SERIOUS', 0)
            st.markdown(f"**Serious:** {count}")
            if count > 0:
                st.warning("⚠️ Requires monitoring")
        
        with col3:
            count = severity_summary.get('SIGNIFICANT', 0)
            st.markdown(f"**Significant:** {count}")
            if count > 0:
                st.info("ℹ️ Monitor patient")
        
        with col4:
            count = severity_summary.get('MINOR', 0)
            st.markdown(f"**Minor:** {count}")
            if count > 0:
                st.success("✅ Low risk")
        
        st.divider()
        
        # Smart Alert Filtering Info
        if results.get('smart_alert_info'):
            st.subheader("🎯 Smart Alert Filtering")
            
            alert_info = results['smart_alert_info']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Interactions",
                    alert_info['total_interactions']
                )
            
            with col2:
                st.metric(
                    "Alerts Shown",
                    alert_info['alerts_shown'],
                    delta=None
                )
            
            with col3:
                filtered_count = alert_info['alerts_filtered']
                st.metric(
                    "Alerts Filtered",
                    filtered_count,
                    delta=f"-{filtered_count} alerts" if filtered_count > 0 else None,
                    delta_color="normal"
                )
            
            if alert_info.get('filtering_reason'):
                st.info(f"ℹ️ {alert_info['filtering_reason']}")
            
            if alert_info['total_interactions'] > alert_info['alerts_shown']:
                st.caption(
                    "💡 Lower-priority interactions were filtered to reduce alert fatigue. "
                    "All critical and serious interactions are always shown."
                )
            
            st.divider()
        
        # ML Risk Assessment
        if results.get('ml_risk_score'):
            st.subheader("🤖 ML Risk Assessment")
            
            risk_score = results.get('ml_risk_score', 0)
            risk_category = results.get('ml_risk_category', 'unknown')
            
            if risk_score >= 75:
                risk_class = "risk-high"
                icon = "🔴"
            elif risk_score >= 50:
                risk_class = "risk-high"
                icon = "🟠"
            elif risk_score >= 25:
                risk_class = "risk-moderate"
                icon = "🟡"
            else:
                risk_class = "risk-low"
                icon = "🟢"
            
            st.markdown(f"""
            <div class="{risk_class}">
                <h4>{icon} Risk Level: {risk_category.upper()}</h4>
                <p><strong>Risk Score:</strong> {risk_score:.1f}/100</p>
            </div>
            """, unsafe_allow_html=True)
            
            if results.get('ml_contributing_factors'):
                with st.expander("📋 Contributing Factors"):
                    for factor in results['ml_contributing_factors']:
                        st.markdown(f"- {factor}")
            
            st.divider()
        
        # Interactions
        if results.get('interactions_found'):
            st.subheader("⚠️ Drug Interactions Detected")
            
            # Group interactions by severity for better display
            interactions_by_severity = {
                'CONTRAINDICATED': [],
                'SERIOUS': [],
                'SIGNIFICANT': [],
                'MINOR': []
            }
            
            for interaction in results['interactions_found']:
                severity = interaction.get('severity_level', 'MINOR')
                interactions_by_severity[severity].append(interaction)
            
            # Display by severity (most severe first)
            for severity in ['CONTRAINDICATED', 'SERIOUS', 'SIGNIFICANT', 'MINOR']:
                interactions = interactions_by_severity[severity]
                if interactions:
                    st.markdown(f"**{severity} ({len(interactions)})**")
                    for interaction in interactions:
                        display_interaction(interaction)
        else:
            st.success("✅ No significant interactions found between selected medications")
        
        # AI Analysis
        if results.get('llm_analysis'):
            st.divider()
            st.subheader("🤖 AI Clinical Analysis")
            
            with st.container():
                st.info(results['llm_analysis'])
        
        # Recommendations
        if results.get('recommendations'):
            st.divider()
            st.subheader("💡 Clinical Recommendations")
            
            for idx, rec in enumerate(results['recommendations'], 1):
                st.markdown(f"{idx}. {rec}")
        
        # Additional info section
        st.divider()
        
        # Show technical details in expander
        with st.expander("🔧 Technical Details"):
            st.json({
                "check_id": results.get('check_id'),
                "checked_at": results.get('checked_at'),
                "patient_id": results.get('patient_id') if enable_allergy_check else None,
                "allergy_check_enabled": enable_allergy_check,
                "smart_filtering_enabled": st.session_state.enable_smart_filtering,
                "external_check_enabled": st.session_state.enable_external_check,
                "external_sources": results.get('external_sources_checked', 0),
                "requires_escalation": results.get('requires_escalation', False),
                "escalation_urgency": results.get('escalation_urgency'),
            })
        
        # Clear results button
        st.divider()
        if st.button("🔄 Start New Analysis", use_container_width=True):
            st.session_state.results = None
            st.session_state.selected_drugs = []
            st.session_state.selected_patient_id = None
            st.rerun()


if __name__ == "__main__":
    main()