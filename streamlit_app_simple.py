"""
Drug Interaction Checker - Streamlit Frontend (Simplified)
"""
import streamlit as st
import requests
import time

# Configuration
st.set_page_config(
    page_title="Drug Interaction Checker",
    page_icon="💊",
    layout="wide"
)

# Title
st.title("💊 Drug Interaction & Allergy Checker")
st.markdown("**AI-Powered Clinical Decision Support System**")

# Check API connection
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        st.success("✅ Connected to API")
        api_working = True
    else:
        st.error("❌ API returned error")
        api_working = False
except Exception as e:
    st.error(f"❌ Cannot connect to API: {e}")
    st.info("💡 Make sure backend is running: `python app/main_enhanced.py`")
    api_working = False
    st.stop()

# Fetch drugs
@st.cache_data
def get_drugs():
    try:
        response = requests.get("http://localhost:8000/api/v1/drugs?limit=100")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

st.header("Select Medications")

drugs = get_drugs()

if not drugs:
    st.error("Failed to load drugs from database")
    st.stop()

st.success(f"✅ Loaded {len(drugs)} drugs from database")

# Initialize session state
if 'selected_drugs' not in st.session_state:
    st.session_state.selected_drugs = []

# Drug selection
drug_dict = {f"{d['drug_name']} ({d['generic_name']})": d for d in drugs}
drug_names = list(drug_dict.keys())

selected_name = st.selectbox("Choose a drug:", ["-- Select --"] + drug_names)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("➕ Add Drug"):
        if selected_name != "-- Select --":
            drug_info = drug_dict[selected_name]
            if drug_info['drug_id'] not in [d['drug_id'] for d in st.session_state.selected_drugs]:
                st.session_state.selected_drugs.append(drug_info)
                st.rerun()
            else:
                st.warning("Already added!")

# Display selected drugs
if st.session_state.selected_drugs:
    st.subheader("Selected Drugs:")
    
    for drug in st.session_state.selected_drugs:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"💊 **{drug['drug_name']}** ({drug['generic_name']})")
        with col2:
            st.write(f"*{drug['drug_class']}*")
        with col3:
            if st.button("❌ Remove", key=drug['drug_id']):
                st.session_state.selected_drugs = [
                    d for d in st.session_state.selected_drugs 
                    if d['drug_id'] != drug['drug_id']
                ]
                st.rerun()
    
    st.divider()
    
    # Check interactions button
    if len(st.session_state.selected_drugs) >= 2:
        include_ai = st.checkbox("Include AI Analysis (takes 3-5 seconds)", value=True)
        
        if st.button("🔍 Check Interactions", type="primary"):
            with st.spinner("Analyzing..."):
                try:
                    drug_ids = [d['drug_id'] for d in st.session_state.selected_drugs]
                    
                    payload = {
                        "drug_ids": drug_ids,
                        "check_allergies": False,
                        "include_llm_analysis": include_ai
                    }
                    
                    response = requests.post(
                        "http://localhost:8000/api/v1/check-interactions",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        st.success("✅ Analysis Complete!")
                        
                        # Display results
                        st.header("Results")
                        
                        # Summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Interactions Found", len(results.get('interactions_found', [])))
                        with col2:
                            st.metric("Risk Score", f"{results.get('risk_score', 0):.1f}/100")
                        with col3:
                            contraindicated = results.get('severity_summary', {}).get('CONTRAINDICATED', 0)
                            if contraindicated > 0:
                                st.metric("⚠️ Critical", contraindicated)
                            else:
                                st.metric("Status", "✅ Safe")
                        
                        st.divider()
                        
                        # Severity breakdown
                        st.subheader("Severity Breakdown")
                        severity = results.get('severity_summary', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Contraindicated", severity.get('CONTRAINDICATED', 0))
                        with col2:
                            st.metric("Serious", severity.get('SERIOUS', 0))
                        with col3:
                            st.metric("Significant", severity.get('SIGNIFICANT', 0))
                        with col4:
                            st.metric("Minor", severity.get('MINOR', 0))
                        
                        st.divider()
                        
                        # Interactions
                        interactions = results.get('interactions_found', [])
                        if interactions:
                            st.subheader(f"⚠️ {len(interactions)} Drug Interaction(s) Detected")
                            
                            for idx, interaction in enumerate(interactions, 1):
                                severity_level = interaction.get('severity_level', 'UNKNOWN')
                                
                                # Color based on severity
                                if severity_level == 'CONTRAINDICATED':
                                    st.error(f"**{idx}. {interaction['drug_a']['drug_name']} + {interaction['drug_b']['drug_name']}** - 🔴 {severity_level}")
                                elif severity_level == 'SERIOUS':
                                    st.warning(f"**{idx}. {interaction['drug_a']['drug_name']} + {interaction['drug_b']['drug_name']}** - 🟠 {severity_level}")
                                elif severity_level == 'SIGNIFICANT':
                                    st.info(f"**{idx}. {interaction['drug_a']['drug_name']} + {interaction['drug_b']['drug_name']}** - 🟡 {severity_level}")
                                else:
                                    st.success(f"**{idx}. {interaction['drug_a']['drug_name']} + {interaction['drug_b']['drug_name']}** - 🟢 {severity_level}")
                                
                                st.write(f"**Description:** {interaction.get('description', 'N/A')}")
                                
                                if interaction.get('clinical_effects'):
                                    st.write(f"**Clinical Effects:** {interaction['clinical_effects']}")
                                
                                if interaction.get('management_recommendations'):
                                    with st.expander("💡 View Management Recommendations"):
                                        st.info(interaction['management_recommendations'])
                                
                                st.divider()
                        else:
                            st.success("✅ No significant interactions found!")
                        
                        # AI Analysis
                        if results.get('llm_analysis'):
                            st.subheader("🤖 AI Clinical Analysis")
                            st.info(results['llm_analysis'])
                        
                        # Recommendations
                        if results.get('recommendations'):
                            st.subheader("💡 Recommendations")
                            for rec in results['recommendations']:
                                st.write(f"• {rec}")
                        
                        # ML Risk
                        if results.get('ml_risk_score'):
                            st.divider()
                            st.subheader("🤖 ML Risk Assessment")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("ML Risk Score", f"{results['ml_risk_score']:.1f}/100")
                            with col2:
                                st.metric("Risk Category", results.get('ml_risk_category', 'unknown').upper())
                            
                            if results.get('ml_contributing_factors'):
                                with st.expander("View Contributing Factors"):
                                    for factor in results['ml_contributing_factors']:
                                        st.write(f"• {factor}")
                        
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("👆 Select at least 2 drugs to check interactions")
else:
    st.info("👆 Select drugs from the dropdown above")

# Sidebar
with st.sidebar:
    st.header("📖 About")
    st.write("""
    This tool checks for:
    - Drug-drug interactions
    - Severity classification
    - AI-powered analysis
    - Clinical recommendations
    """)
    
    st.divider()
    
    st.header("🔗 Links")
    st.markdown("[API Docs](http://localhost:8000/docs)")
    st.markdown("[Health Check](http://localhost:8000/health)")
    
    if st.button("🔄 Reset All"):
        st.session_state.selected_drugs = []
        st.rerun()
