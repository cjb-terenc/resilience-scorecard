import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Community Resilience Scorecard", layout="wide")

st.title("🏘️ Community Resilience Scorecard")
st.markdown("Welcome! This tool provides a baseline resilience snapshot for your community using publicly available data.")

# Scoring helper functions
def poverty_score(value):
    if value <= 5: return 5
    elif value <= 10: return 4
    elif value <= 15: return 3
    elif value <= 20: return 2
    else: return 1

def income_score(value):
    if value >= 75000: return 5
    elif value >= 60000: return 4
    elif value >= 45000: return 3
    elif value >= 30000: return 2
    else: return 1

def unemployment_score(value):
    if value <= 2: return 5
    elif value <= 4: return 4
    elif value <= 6: return 3
    elif value <= 8: return 2
    else: return 1

def education_score(value):  # % with BA+
    if value >= 40: return 5
    elif value >= 30: return 4
    elif value >= 20: return 3
    elif value >= 10: return 2
    else: return 1

    # Household & Infrastructure
def renter_score(value):
    if value <= 20: return 5
    elif value <= 30: return 4
    elif value <= 40: return 3
    elif value <= 50: return 2
    else: return 1

def old_housing_score(value):
    if value <= 20: return 5
    elif value <= 35: return 4
    elif value <= 50: return 3
    elif value <= 65: return 2
    else: return 1

def no_vehicle_score(value):
    if value <= 5: return 5
    elif value <= 10: return 4
    elif value <= 15: return 3
    elif value <= 20: return 2
    else: return 1

# Health & Medical
def uninsured_score(value):
    if value <= 5: return 5
    elif value <= 10: return 4
    elif value <= 15: return 3
    elif value <= 20: return 2
    else: return 1

def disability_score(value):
    if value <= 10: return 5
    elif value <= 15: return 4
    elif value <= 20: return 3
    elif value <= 25: return 2
    else: return 1

def trauma_distance_score(value):  # in miles
    if value <= 10: return 5
    elif value <= 20: return 4
    elif value <= 30: return 3
    elif value <= 40: return 2
    else: return 1

def hospital_beds_score(value):  # per 10k
    if value >= 40: return 5
    elif value >= 30: return 4
    elif value >= 20: return 3
    elif value >= 10: return 2
    else: return 1

# Community Capacity
def ltd_english_score(value):
    if value <= 1: return 5
    elif value <= 3: return 4
    elif value <= 5: return 3
    elif value <= 7: return 2
    else: return 1

def broadband_score(value):
    if value >= 90: return 5
    elif value >= 80: return 4
    elif value >= 70: return 3
    elif value >= 60: return 2
    else: return 1

def residential_stability_score(value):
    if value >= 90: return 5
    elif value >= 80: return 4
    elif value >= 70: return 3
    elif value >= 60: return 2
    else: return 1

# Environmental
def flood_risk_score(value):
    if value <= 2: return 5
    elif value <= 5: return 4
    elif value <= 10: return 3
    elif value <= 15: return 2
    else: return 1

def fema_risk_score(value):  # uses qualitative NRI category
    risk_map = {
        "Very Low": 5,
        "Low": 4,
        "Moderate": 3,
        "Relatively High": 2,
        "Very High": 1
    }
    return risk_map.get(str(value).strip(), 3)  # Default to 3 if unknown

# Load the sample data
@st.cache_data
def load_data():
    df = pd.read_csv('data/iowa_tracts_sample.csv')
    return df

data = load_data()

import requests

st.subheader("📍 Locate Your Community by Address")

# Structured address inputs
street = st.text_input("Street Address", "514 N Madison St")
city = st.text_input("City", "Bloomfield")
state = st.text_input("State (2-letter code)", "IA")
zipcode = st.text_input("ZIP Code", "52537")

def get_census_tract_from_components(street, city, state, zip):
    base_url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    params = {
        "street": street,
        "city": city,
        "state": state,
        "zip": zip,
        "benchmark": "Public_AR_Current",
        "vintage": "Census2020_Census2020",
        "format": "json"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            tract_info = data["result"]["addressMatches"][0]["geographies"]["Census Tracts"][0]
            return tract_info["GEOID"]  # 11-digit tract FIPS
        except (IndexError, KeyError):
            return None
    else:
        return None

# Only call geocoder if all fields are filled
selected_tract = None
if all([street, city, state, zipcode]):
    tract_fips = get_census_tract_from_components(street, city, state, zipcode)
    if tract_fips:
        st.success(f"Address is located in Census Tract: {tract_fips}")
        selected_tract = int(tract_fips[-6:])  # Extract tract code (last 6 digits)
    else:
        st.error("Unable to find census tract for this address.")

# User selects a census tract
tracts = data['Tract'].tolist()
if not selected_tract:
    selected_tract = st.selectbox("Or select a Census Tract manually:", data['Tract'].tolist())

# Display data for the selected tract
tract_data = data[data['Tract'] == selected_tract].squeeze()

# Apply scoring for all pillars
socio_score_values = {
    "Poverty Rate": poverty_score(tract_data['Poverty_Rate']),
    "Median Income": income_score(tract_data['Median_Household_Income']),
    "Unemployment": unemployment_score(tract_data['Unemployment_Rate']),
    "Education (BA+)": education_score(tract_data['Educational_Attainment_BAplus'])
}
socio_score = sum(socio_score_values.values()) / len(socio_score_values)

infra_score_values = {
    "Renter-Occupied": renter_score(tract_data['Renter_Occupied']),
    "Older Housing": old_housing_score(tract_data['Older_Housing']),
    "No Vehicle": no_vehicle_score(tract_data['No_Vehicle'])
}
infra_score = sum(infra_score_values.values()) / len(infra_score_values)

health_score_values = {
    "Uninsured": uninsured_score(tract_data['Uninsured']),
    "Disability": disability_score(tract_data['Disability']),
    "Trauma Center Distance": trauma_distance_score(tract_data['Trauma_Center_Distance_Miles']),
    "Hospital Beds per 10k": hospital_beds_score(tract_data['Hospital_Beds_per_10k'])
}
health_score = sum(health_score_values.values()) / len(health_score_values)

community_score_values = {
    "Limited English": ltd_english_score(tract_data['Ltd_English']),
    "Broadband Access": broadband_score(tract_data['Broadband_Access']),
    "Residential Stability": residential_stability_score(tract_data['Residential_Stability'])
}
community_score = sum(community_score_values.values()) / len(community_score_values)

environment_score_values = {
    "Flood Risk": flood_risk_score(tract_data['Flood_Risk_Percent']),
    "FEMA Risk": fema_risk_score(tract_data['FEMA_Risk_Score'])
}
environment_score = sum(environment_score_values.values()) / len(environment_score_values)

# Weighted overall score (scale to 100)
# Weighted contributions to 100-point scale
socio_points = (socio_score / 5) * 30
infra_points = (infra_score / 5) * 20
health_points = (health_score / 5) * 20
community_points = (community_score / 5) * 15
environment_points = (environment_score / 5) * 15

overall_score = socio_points + infra_points + health_points + community_points + environment_points

# Display scores
st.metric("🏛 Socioeconomic Vulnerability (Max 30)", f"{socio_points:.1f}")
st.metric("🏚 Infrastructure Vulnerability (Max 20)", f"{infra_points:.1f}")
st.metric("🩺 Health & Medical Vulnerability (Max 20)", f"{health_points:.1f}")
st.metric("🧭 Community Capacity (Max 15)", f"{community_points:.1f}")
st.metric("🌪 Environmental Risk (Max 15)", f"{environment_points:.1f}")
st.metric("💯 Total Resilience Score (0–100)", f"{overall_score:.1f}")

import matplotlib.pyplot as plt

# Improved bar chart
st.subheader("📊 Pillar Contributions to Resilience Score (0–100)")

pillars = ['Socioeconomic', 'Infrastructure', 'Health & Medical', 'Community', 'Environment']
scores = [socio_points, infra_points, health_points, community_points, environment_points]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(pillars, scores, color='steelblue')
ax.set_ylim(0, 30)
ax.set_ylabel('Points Contributed')
ax.set_title('Resilience Score Breakdown by Pillar')
ax.bar_label(bars, fmt='%.1f', padding=3)
plt.xticks(rotation=15)

st.pyplot(fig)

# Improved radar chart
st.subheader("🕸 Resilience Profile (1–5 scale)")

labels = ['Socioeconomic', 'Infrastructure', 'Health & Medical', 'Community Capacity', 'Environmental']
scores_1_to_5 = [socio_score, infra_score, health_score, community_score, environment_score]

# Repeat first value to close the loop
scores = scores_1_to_5 + scores_1_to_5[:1]
angles = np.linspace(0, 2 * np.pi, len(scores_1_to_5), endpoint=False).tolist()
angles += angles[:1]

fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Light grid
ax2.grid(color='gray', linestyle='dotted', linewidth=0.5)
ax2.spines['polar'].set_visible(False)

# Plot data
ax2.plot(angles, scores, color='darkorange', linewidth=2)
ax2.fill(angles, scores, color='orange', alpha=0.25)

# Ticks and labels
ax2.set_yticks([1, 2, 3, 4, 5])
ax2.set_yticklabels(['1', '2', '3', '4', '5'], color='gray')
ax2.set_ylim(0, 5)

ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(labels, color='black', fontsize=10)

ax2.set_title('Community Resilience Radar', y=1.1)

st.pyplot(fig2)

st.subheader(f"Resilience Indicators for Census Tract {selected_tract}")

# Display indicators grouped by pillar
st.markdown("### 1. Socioeconomic Vulnerability")
st.write(f"**Median Household Income:** ${tract_data['Median_Household_Income']:,.0f}")
st.write(f"**Poverty Rate:** {tract_data['Poverty_Rate']}%")
st.write(f"**Unemployment Rate:** {tract_data['Unemployment_Rate']}%")
st.write(f"**Educational Attainment (BA+):** {tract_data['Educational_Attainment_BAplus']}%")

st.markdown("### 2. Household & Infrastructure Vulnerability")
st.write(f"**% Renter-Occupied Housing:** {tract_data['Renter_Occupied']}%")
st.write(f"**% Older Housing Stock (Pre-1980):** {tract_data['Older_Housing']}%")
st.write(f"**% Households with No Vehicle:** {tract_data['No_Vehicle']}%")

st.markdown("### 3. Health Vulnerability")
st.write(f"**% Uninsured:** {tract_data['Uninsured']}%")
st.write(f"**% with Disabilities:** {tract_data['Disability']}%")
st.write(f"**Distance to Nearest Trauma Center:** {tract_data['Trauma_Center_Distance_Miles']} miles")
st.write(f"**Hospital Beds per 10,000 People:** {tract_data['Hospital_Beds_per_10k']}")

st.markdown("### 4. Community Capacity")
st.write(f"**% Limited English Speaking Households:** {tract_data['Ltd_English']}%")
st.write(f"**% with Broadband Access:** {tract_data['Broadband_Access']}%")
st.write(f"**% Residential Stability (≥1 year):** {tract_data['Residential_Stability']}%")

st.markdown("### 5. Environmental Risk")
st.write(f"**FEMA Overall Risk Score:** {tract_data['FEMA_Risk_Score']}")
st.write(f"**% of Tract in 100/500-Year Flood Zone:** {tract_data['Flood_Risk_Percent']}%")
