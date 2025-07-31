import streamlit as st
import pandas as pd
import random
import pandas as pd
import plotly.express as px
import streamlit as st


# Page configuration
st.set_page_config(
    page_title="⚡ Battery Cell Management System",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    .temp-normal {
        color: #28a745;
        font-weight: bold;
    }
    
    .temp-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .temp-danger {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ Battery Cell Management System</h1>
    <p>Monitor and manage up to 8 battery cells with real-time calculations and visualizations</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Sidebar for cell configuration
st.sidebar.header("🔧 Cell Configuration")
st.sidebar.markdown("Configure your battery cells below:")

# Number of cells selector
num_cells = st.sidebar.slider("Number of Cells", min_value=1, max_value=8, value=4)

# Cell configuration
cell_configs = []
for i in range(1, num_cells + 1):
    with st.sidebar.expander(f"🔋 Cell {i} Configuration", expanded=False):
        cell_type = st.selectbox(
            f"Cell {i} Type",
            ["", "lfp", "mnc", "other"],
            key=f"cell_type_{i}",
            format_func=lambda x: {
                "": "Select type...",
                "lfp": "LFP (Lithium Iron Phosphate)",
                "mnc": "MNC (Manganese Nickel Cobalt)",
                "other": "Other"
            }.get(x, x)
        )
        
        current = st.number_input(
            f"Cell {i} Current (A)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key=f"current_{i}"
        )
        
        if cell_type and current > 0:
            voltage = 3.2 if cell_type == "lfp" else 3.6
            capacity = round(voltage * current, 2)
            st.info(f"💡 Voltage: {voltage}V | Capacity: {capacity}Wh")
        
        if cell_type and current > 0:
            cell_configs.append({
                'cell_num': i,
                'cell_type': cell_type,
                'current': current
            })

# Generate button
if st.sidebar.button("🚀 Generate Results", type="primary"):
    if cell_configs:
        st.session_state.cells_data = {}
        
        for config in cell_configs:
            cell_type = config['cell_type']
            current = config['current']
            cell_num = config['cell_num']
            
            voltage = 3.2 if cell_type == "lfp" else 3.6
            max_vol = 3.4 if cell_type == "mnc" else 4.0
            min_vol = 2.8 if cell_type == "lfp" else 3.2
            temp = round(random.uniform(25, 40), 1)
            capacity = round(voltage * current, 2)
            
            cell_key = f"cell_{cell_num}_{cell_type}"
            
            st.session_state.cells_data[cell_key] = {
                "Cell ID": cell_key,
                "Type": cell_type.upper(),
                "Voltage (V)": voltage,
                "Current (A)": current,
                "Temperature (°C)": temp,
                "Capacity (Wh)": capacity,
                "Max Voltage (V)": max_vol,
                "Min Voltage (V)": min_vol
            }
        
        st.session_state.generated = True
        st.sidebar.success(f"✅ Generated data for {len(cell_configs)} cells!")
    else:
        st.sidebar.error("❌ Please configure at least one cell!")

# Reset button
if st.sidebar.button("🗑️ Reset All"):
    st.session_state.cells_data = {}
    st.session_state.generated = False
    st.sidebar.success("🔄 All data cleared!")

# Main content area
if st.session_state.generated and st.session_state.cells_data:
    # Convert to DataFrame for better display
    df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
    
    # Overview metrics
    st.header("📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔋 Total Cells",
            value=len(df),
            delta=f"{len(df)}/8 configured"
        )
    
    with col2:
        total_capacity = df['Capacity (Wh)'].sum()
        st.metric(
            label="⚡ Total Capacity",
            value=f"{total_capacity:.1f} Wh",
            delta=f"Avg: {total_capacity/len(df):.1f} Wh"
        )
    
    with col3:
        avg_temp = df['Temperature (°C)'].mean()
        temp_delta = "Normal" if avg_temp < 35 else "Warning" if avg_temp < 38 else "Critical"
        st.metric(
            label="🌡️ Avg Temperature",
            value=f"{avg_temp:.1f}°C",
            delta=temp_delta
        )
    
    with col4:
        total_current = df['Current (A)'].sum()
        st.metric(
            label="🔄 Total Current",
            value=f"{total_current:.1f} A",
            delta=f"Avg: {total_current/len(df):.1f} A"
        )
    
    st.divider()
    
    # Data table with enhanced formatting
    st.header("📈 Detailed Cell Data")
    
    # Format the dataframe for better display
    display_df = df.copy()
    
    # Add temperature status
    def get_temp_status(temp):
        if temp < 35:
            return "🟢 Normal"
        elif temp <= 38:
            return "🟡 Warning"
        else:
            return "🔴 Critical"
    
    display_df['Temp Status'] = display_df['Temperature (°C)'].apply(get_temp_status)
    
    # Reorder columns
    column_order = ['Cell ID', 'Type', 'Voltage (V)', 'Current (A)', 
                   'Temperature (°C)', 'Temp Status', 'Capacity (Wh)', 
                   'Max Voltage (V)', 'Min Voltage (V)']
    display_df = display_df[column_order]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Temperature (°C)": st.column_config.NumberColumn(
                "Temperature (°C)",
                format="%.1f°C"
            ),
            "Voltage (V)": st.column_config.NumberColumn(
                "Voltage (V)",
                format="%.1fV"
            ),
            "Current (A)": st.column_config.NumberColumn(
                "Current (A)",
                format="%.1fA"
            ),
            "Capacity (Wh)": st.column_config.NumberColumn(
                "Capacity (Wh)",
                format="%.2f Wh"
            )
        }
    )
    
    st.divider()
    
    # Visualizations
    st.header("📊 Data Visualizations")
    
    # Create tabs for different charts
    tab1, tab2, tab3, tab4 = st.tabs(["🔋 Capacity Analysis", "🌡️ Temperature Monitor", "⚡ Voltage Overview", "📈 Performance Summary"])
    
    with tab1:
        # Capacity bar chart
        fig_capacity = px.bar(
            df, 
            x='Cell ID', 
            y='Capacity (Wh)',
            color='Type',
            title="Battery Cell Capacity Analysis",
            text='Capacity (Wh)'
        )
        fig_capacity.update_traces(texttemplate='%{text:.1f}Wh', textposition='outside')
        fig_capacity.update_layout(height=500, showlegend=True)
        st.plotly_chart(fig_capacity, use_container_width=True)
    
    with tab2:
        # Temperature gauge chart
        fig_temp = go.Figure()
        
        for idx, row in df.iterrows():
            color = 'green' if row['Temperature (°C)'] < 35 else 'orange' if row['Temperature (°C)'] <= 38 else 'red'
            fig_temp.add_trace(go.Scatter(
                x=[row['Cell ID']], 
                y=[row['Temperature (°C)']],
                mode='markers+text',
                marker=dict(size=20, color=color),
                text=f"{row['Temperature (°C)']}°C",
                textposition="top center",
                name=row['Cell ID']
            ))
        
        fig_temp.add_hline(y=35, line_dash="dash", line_color="orange", 
                          annotation_text="Warning Threshold (35°C)")
        fig_temp.add_hline(y=38, line_dash="dash", line_color="red", 
                          annotation_text="Critical Threshold (38°C)")
        
        fig_temp.update_layout(
            title="Temperature Monitoring Dashboard",
            xaxis_title="Cell ID",
            yaxis_title="Temperature (°C)",
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with tab3:
        # Voltage comparison
        fig_voltage = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Current vs Max/Min Voltage", "Voltage Distribution by Type")
        )
        
        # Voltage range chart
        fig_voltage.add_trace(
            go.Scatter(x=df['Cell ID'], y=df['Voltage (V)'], 
                      mode='markers', name='Current Voltage',
                      marker=dict(size=12, color='blue')),
            row=1, col=1
        )
        fig_voltage.add_trace(
            go.Scatter(x=df['Cell ID'], y=df['Max Voltage (V)'], 
                      mode='markers', name='Max Voltage',
                      marker=dict(size=8, color='red')),
            row=1, col=1
        )
        fig_voltage.add_trace(
            go.Scatter(x=df['Cell ID'], y=df['Min Voltage (V)'], 
                      mode='markers', name='Min Voltage',
                      marker=dict(size=8, color='green')),
            row=1, col=1
        )
        
        # Voltage by type
        voltage_by_type = df.groupby('Type')['Voltage (V)'].mean()
        fig_voltage.add_trace(
            go.Bar(x=voltage_by_type.index, y=voltage_by_type.values,
                   name='Avg Voltage by Type', marker_color='purple'),
            row=1, col=2
        )
        
        fig_voltage.update_layout(height=500, showlegend=True)
        st.plotly_chart(fig_voltage, use_container_width=True)
    
    with tab4:
        # Performance summary
        col1, col2 = st.columns(2)
        
        with col1:
            # Power calculation (V * A)
            df['Power (W)'] = df['Voltage (V)'] * df['Current (A)']
            fig_power = px.pie(
                df, 
                values='Power (W)', 
                names='Cell ID',
                title="Power Distribution Across Cells"
            )
            st.plotly_chart(fig_power, use_container_width=True)
        
        with col2:
            # Efficiency radar chart (normalized metrics)
            categories = ['Voltage', 'Current', 'Capacity', 'Temperature']
            
            # Normalize values for radar chart
            normalized_df = df[['Voltage (V)', 'Current (A)', 'Capacity (Wh)', 'Temperature (°C)']].copy()
            for col in normalized_df.columns:
                normalized_df[col] = (normalized_df[col] - normalized_df[col].min()) / (normalized_df[col].max() - normalized_df[col].min()) * 100
            
            fig_radar = go.Figure()
            
            for idx, row in df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=normalized_df.loc[idx].values,
                    theta=categories,
                    fill='toself',
                    name=row['Cell ID'],
                    opacity=0.7
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Cell Performance Comparison (Normalized)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Download functionality
    st.divider()
    st.header("💾 Export Data")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="battery_cells_data.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name="battery_cells_data.json",
            mime="application/json"
        )

else:
    # Welcome screen
    st.info("👋 Welcome! Configure your battery cells in the sidebar and click 'Generate Results' to start.")
    
    # Instructions
    with st.expander("📖 How to Use", expanded=True):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Configure Cells**: Use the sidebar to set up 1-8 battery cells
        2. **Select Cell Type**: Choose from LFP, MNC, or Other
        3. **Set Current**: Enter the current value for each cell
        4. **Generate Results**: Click the generate button to process data
        5. **Analyze**: View metrics, tables, and visualizations
        6. **Export**: Download your data as CSV or JSON
        
        ### Cell Type Specifications:
        - **LFP**: Voltage 3.2V, Min 2.8V, Max 4.0V
        - **MNC**: Voltage 3.6V, Min 3.2V, Max 3.4V  
        - **Other**: Voltage 3.6V, Min 3.2V, Max 4.0V
        
        ### Features:
        - 📊 Real-time calculations
        - 🌡️ Temperature monitoring with alerts
        - 📈 Interactive visualizations
        - 💾 Data export capabilities
        - 📱 Responsive design
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚡ Battery Cell Management System | Built with Streamlit 🚀</p>
</div>
""", unsafe_allow_html=True)
