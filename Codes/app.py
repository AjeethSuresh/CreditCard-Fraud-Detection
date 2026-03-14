import streamlit as st
import numpy as np
import pandas as pd
import pickle
import base64

# Configure the Streamlit page for a better initial look
st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import base64

# Configure the Streamlit page for a better initial look
st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS from separate file
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {e}")

load_css("style.css")

# Application Header Content
st.markdown("""
<div style='text-align: center; padding: 40px 0; animation: fadeInDown 1s ease;'>
    <h1 style='font-size: 4rem; margin-bottom: 0;'>🛡️ FraudShield <span style='font-weight: 300;'>AI</span></h1>
    <p style='font-size: 1.3rem; color: #94a3b8; max-width: 600px; margin: 15px auto; letter-spacing: 2px; font-weight: 600;'>
        CREDIT CARD FRAUD DETECTION
    </p>
</div>
""", unsafe_allow_html=True)

# Load the trained model AFTER the header styling
model_path = 'fraud_model.pkl'
try:
    model = pickle.load(open(model_path, 'rb'))
except FileNotFoundError:
    st.error(f"Model file '{model_path}' not found. Please train the model first.")
    st.stop()

# Core Prediction Function
def predict_fraud(amount, time_val, transaction_type, location_risk):
    # Instead of forcing the probability with the Location_Risk dropdown, 
    # we simulate the PCA values based on suspicious patterns:
    # High amounts (e.g. > $1000) and odd hours (between midnight and 5 AM) increase risk.
    
    is_suspicious = False
    base_risk = 0.0
    
    # Large unusual amounts
    if amount > 2500:
        base_risk -= 3.0
    elif amount > 1000:
        base_risk -= 1.5
        
    # Late night transactions
    if time_val < 5.0 or time_val > 23.0:
        base_risk -= 2.0
        is_suspicious = True
        
    # Combine with location risk as a modifier, not an absolute
    risk_modifier = {"Low": 0.0, "Medium": -1.0, "High": -2.0}
    loc_modifier = risk_modifier.get(location_risk, 0.0)
    
    # Transaction type modifier (Online might be slightly riskier for large amounts)
    tx_type_mapped = 1 if transaction_type == "Online" else 0
    if tx_type_mapped == 1 and is_suspicious:
        base_risk -= 1.0
        
    final_pca_val = base_risk + loc_modifier
    
    # Feature Vector for model (trained on: Time, Amount, V14, V17, V12)
    # The more negative V14, V17, V12 are, the higher the fraud probability
    input_data = np.array([[time_val, amount, final_pca_val, final_pca_val + 1, final_pca_val]])
    
    prediction = model.predict(input_data)[0]
    
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(input_data)[0][1] * 100
    else:
        prob = 100.0 if prediction == 1 else 0.0
        
    return prediction, prob

def render_risk_gauge(prob):
    # Determine the color and text based on probability
    if prob <= 30:
        color = "#10b981" # Emerald Green
        status = "Low Risk"
        icon = "🛡️"
    elif prob <= 70:
        color = "#f59e0b" # Amber
        status = "Medium Risk"
        icon = "⚠️"
    else:
        color = "#ef4444" # Red
        status = "Critical Risk"
        icon = "🚨"

    # HTML structure for the result card
    st.markdown(f"""
        <div class="result-card" style="border-top: 5px solid {color}; box-shadow: 0 10px 30px {color}22;">
            <div class="result-icon">{icon}</div>
            <h3 style="margin-top: 0; color: #f8fafc; font-size: 2rem;">{status}</h3>
            <div style="color: #94a3b8; font-size: 1.2rem; margin-top: 10px;">
                Detected anomalous signature probability: <strong style="color: {color}; font-size: 1.5rem;">{prob:.1f}%</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    progress_val = min(max(prob / 100.0, 0.0), 1.0)
    st.progress(progress_val)

tab1, tab2 = st.tabs(["🎯 Live Analysis", "📁 Batch Intelligence"])

with tab1:
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("Transaction Details")
        st.write("Enter the transaction information to check for potential fraud.")
        
        amt_col1, amt_col2 = st.columns([1, 3])
        with amt_col1:
            currency = st.selectbox("Currency", ["₹ INR", "$ USD", "€ EUR", "£ GBP"])
        with amt_col2:
            # Using value as a string in text_input to avoid number buttons entirely
            amount_str = st.text_input("Transaction Amount", value="150.00")
            try:
                amount = float(amount_str)
            except:
                amount = 0.0
                st.error("Please enter a valid amount")
            
        st.write("Time of Transaction")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            h = st.selectbox("Hour", options=[str(i).zfill(2) for i in range(1, 13)], index=1) # Default 02
        with t_col2:
            m = st.selectbox("Minute", options=[str(i).zfill(2) for i in range(0, 60, 5)], index=0)
        with t_col3:
            p = st.selectbox("AM/PM", options=["AM", "PM"], index=1) # Default PM
            
        # Convert to 24-hour decimal for the model
        hour_24 = int(h)
        if p == "PM" and hour_24 < 12: hour_24 += 12
        if p == "AM" and hour_24 == 12: hour_24 = 0
        time_val = hour_24 + (int(m) / 60.0)
        
        sel_col1, sel_col2 = st.columns(2)
        with sel_col1:
            transaction_type = st.selectbox("Transaction Source", ["Online", "POS"], help="Was this online or at a physical Point of Sale?")
        with sel_col2:
            location_risk = st.selectbox("Location Security", ["Low", "Medium", "High"], help="How secure is the location/IP of the transaction?")

        st.markdown("<br>", unsafe_allow_html=True)
        predict_button = st.button("Check For Fraud", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("Analysis Results")
        if predict_button:
            with st.spinner('Analyzing transaction patterns...'):
                prediction, prob = predict_fraud(amount, time_val, transaction_type, location_risk)
                render_risk_gauge(prob)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 40px 20px; color: #64748b;">
                    <br>
                    <div style="font-size: 4rem; margin-bottom: 20px; opacity: 0.5;">🛡️</div>
                    <h3 style="color: #cbd5e1; margin-top: 10px;">Ready to Check</h3>
                    <p style="margin-top: 10px;">Enter the transaction details on the left and click 'Check For Fraud' to see the results.</p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.subheader("Batch Fraud Check")
    st.write("Upload a CSV file containing multiple transactions to check them all at once.")
    
    uploaded_file = st.file_uploader("", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.markdown("<h4 style='color: #cbd5e1; margin-top: 20px;'>Uploaded Data Preview</h4>", unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
            
            required_cols = ['Amount', 'Time', 'Transaction_Type', 'Location_Risk']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"⚠️ Incorrect format. The CSV must contain these exact columns: {', '.join(missing_cols)}")
            else:
                if st.button("Start Batch Check"):
                    with st.status("Analyzing Transactions...", expanded=True) as status:
                        st.write("Checking entries...")
                        results = []
                        for index, row in df.iterrows():
                            pred, prob = predict_fraud(row['Amount'], row['Time'], row['Transaction_Type'], row['Location_Risk'])
                            
                            risk_level = "Low Risk"
                            if prob > 70:
                                risk_level = "Critical Risk"
                            elif prob > 30:
                                risk_level = "Medium Risk"
                                
                            results.append({
                                "Amount (₹)": row['Amount'],
                                "Sequence": row['Time'],
                                "Source": row['Transaction_Type'],
                                "Location": row['Location_Risk'],
                                "Fraud Prob %": f"{prob:.1f}%",
                                "Risk Status": risk_level
                            })
                        
                        results_df = pd.DataFrame(results)
                        status.update(label="Check Complete!", state="complete", expanded=False)
                        
                        # Style formatting using pandas Styler
                        def color_risk(val):
                            color = '#10b981' # Green
                            if val == 'Critical Risk': color = '#ef4444' # Red
                            elif val == 'Medium Risk': color = '#f59e0b' # Yellow
                            return f'color: {color}; font-weight: 800; background: rgba(0,0,0,0.3); border-radius: 4px; padding: 2px 8px;'
                        
                        st.markdown("<h4 style='color: #cbd5e1; margin-top: 20px;'>Batch Results</h4>", unsafe_allow_html=True)
                        st.dataframe(results_df.style.map(color_risk, subset=['Risk Status']), use_container_width=True)
                        
                        st.download_button(
                            label="📥 Download Results CSV",
                            data=results_df.to_csv(index=False).encode('utf-8'),
                            file_name='fraud_batch_results.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

