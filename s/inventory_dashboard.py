import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from ultralytics import YOLO
import random
import os

# Initialize session state
if 'video_feed' not in st.session_state:
    st.session_state.video_feed = None
if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False

# Load mock data
def load_mock_data():
    current_time = datetime.now()
    
    # Mock inventory data
    products = [
        {'sku': 'A123', 'name': 'Product A', 'threshold': 10},
        {'sku': 'B456', 'name': 'Product B', 'threshold': 5},
        {'sku': 'C789', 'name': 'Product C', 'threshold': 8}
    ]
    
    # Generate mock sales data
    dates = pd.date_range(end=current_time, periods=90, freq='D')
    sales_data = []
    for sku in ['A123', 'B456', 'C789']:
        sales = np.random.poisson(5, len(dates))
        sales_data.extend([{'date': d, 'sku': sku, 'sales': s} for d, s in zip(dates, sales)])
    
    return products, pd.DataFrame(sales_data)

# Initialize YOLO model
def init_yolo():
    return YOLO('yolov8n.pt')

# Process video frame
def process_frame(frame, model):
    results = model(frame)
    return results[0].plot()

# Dashboard layout
st.set_page_config(page_title="Inventory Monitoring Dashboard", layout="wide")

# Sidebar - Admin Tools
st.sidebar.header("Admin Tools")
with st.sidebar:
    st.subheader("Upload Data")
    uploaded_sales = st.file_uploader("Upload Sales Data (CSV)", type="csv")
    uploaded_images = st.file_uploader("Upload Product Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    st.subheader("Settings")
    threshold = st.slider("Low Stock Threshold", 0, 50, 10)
    mode = st.selectbox("Operation Mode", ["Live", "Simulation"])

# Main content
st.title("Real-time Inventory Monitoring Dashboard")

# Tab layout
tabs = st.tabs(["Live Monitoring", "Inventory Summary", "Sales Forecast", "Alerts", "Product Insights"])

# Tab 1: Live Monitoring
with tabs[0]:
    st.header("Live Shelf Monitoring")
    
    # Video feed controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera Feed"):
            st.session_state.video_feed = cv2.VideoCapture(0)
        if st.button("Stop Camera Feed"):
            if st.session_state.video_feed:
                st.session_state.video_feed.release()
                st.session_state.video_feed = None
    with col2:
        st.checkbox("Pause Feed", value=False, key="is_paused")
    
    # Video feed display
    if st.session_state.video_feed:
        frame_placeholder = st.empty()
        while not st.session_state.is_paused:
            ret, frame = st.session_state.video_feed.read()
            if not ret:
                break
            processed_frame = process_frame(frame, init_yolo())
            frame_placeholder.image(processed_frame, channels="BGR")

# Tab 2: Inventory Summary
with tabs[1]:
    st.header("Inventory Summary")
    
    # Load mock data
    products, _ = load_mock_data()
    
    # Create summary table
    inventory_data = []
    for product in products:
        detected = random.randint(0, 20)
        pos = random.randint(0, 20)
        status = "Good" if detected >= product['threshold'] else "Low" if detected > 0 else "Out-of-stock"
        inventory_data.append({
            'SKU': product['sku'],
            'Product Name': product['name'],
            'Shelf Count': detected,
            'POS Count': pos,
            'Status': status
        })
    
    df = pd.DataFrame(inventory_data)
    
    # Color-coded status
    status_colors = {
        'Good': 'background-color: #d4edda',
        'Low': 'background-color: #fff3cd',
        'Out-of-stock': 'background-color: #f8d7da'
    }
    
    st.dataframe(
        df.style.applymap(lambda x: status_colors.get(x, ''), subset=['Status'])
    )

# Tab 3: Sales Forecast
# Tab 3: Sales Forecast
with tabs[2]:
    st.header("Sales Forecast")
    
    # Load mock sales data
    _, sales_data = load_mock_data()
    
    # Filter by SKU
    sku = st.selectbox("Select SKU", sales_data['sku'].unique())
    filtered_data = sales_data[sales_data['sku'] == sku]
    
    # Create forecast
    forecast = filtered_data.copy()
    future_dates = pd.date_range(
        start=filtered_data['date'].max(),
        periods=30,
        freq='D'
    )
    forecast_values = np.random.normal(
        filtered_data['sales'].mean(),
        filtered_data['sales'].std(),
        len(future_dates)
    )

    # ✅ Correct way to extend the DataFrame
    future_df = pd.DataFrame([
        {'date': d, 'sku': sku, 'sales': s} 
        for d, s in zip(future_dates, forecast_values)
    ])
    forecast = pd.concat([forecast, future_df], ignore_index=True)
    
    # Plot
    fig = px.line(
        forecast,
        x='date',
        y='sales',
        title=f"Sales Forecast for SKU {sku}",
        labels={'date': 'Date', 'sales': 'Sales'}
    )
    fig.add_vline(x=filtered_data['date'].max(), line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)


# Tab 4: Alerts
with tabs[3]:
    st.header("Alerts")
    
    # Generate mock alerts
    alerts = [
        {'timestamp': datetime.now(), 'type': 'Low Stock', 'sku': 'A123', 'severity': 'High'},
        {'timestamp': datetime.now() - timedelta(hours=1), 'type': 'Mismatch', 'sku': 'B456', 'severity': 'Medium'},
        {'timestamp': datetime.now() - timedelta(hours=2), 'type': 'Out of Stock', 'sku': 'C789', 'severity': 'Critical'}
    ]
    
    df_alerts = pd.DataFrame(alerts)
    st.dataframe(df_alerts)
    
    if st.button("Download Alerts as CSV"):
        df_alerts.to_csv("alerts.csv", index=False)
        st.success("Alerts downloaded successfully!")

# Tab 5: Product Insights
with tabs[4]:
    st.header("Product Insights")
    
    # Product selector
    selected_sku = st.selectbox("Select Product", ['A123', 'B456', 'C789'])
    
    # Product details
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Product Details")
        st.image("https://via.placeholder.com/200", caption=f"SKU {selected_sku}")
        st.metric("Shelf Count", value=random.randint(0, 20))
        st.metric("POS Count", value=random.randint(0, 20))
        st.metric("Reorder Suggestion", value="Yes" if random.random() > 0.5 else "No")
    
    with col2:
        st.subheader("Sales Trend")
        # Generate mock sales trend
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        sales = np.random.poisson(5, len(dates))
        
        fig = px.line(
            x=dates,
            y=sales,
            title="7-day Sales Trend",
            labels={'x': 'Date', 'y': 'Sales'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Downloadable Reports
st.sidebar.header("Download Reports")
if st.sidebar.button("Download Daily Report"):
    st.sidebar.success("Daily report downloaded successfully!")
if st.sidebar.button("Download Forecast Report"):
    st.sidebar.success("Forecast report downloaded successfully!")
