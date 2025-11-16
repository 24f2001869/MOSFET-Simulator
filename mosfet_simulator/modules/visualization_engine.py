# modules/visualization_engine.py
"""
VISUALIZATION ENGINE - Advanced plots and charts
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

class VisualizationEngine:
    def __init__(self):
        self.colors = {
            'Si': '#1f77b4',
            'GaN': '#ff7f0e', 
            'SiC': '#2ca02c'
        }
    
    def create_iv_characteristics(self, materials_data, geometry):
        """Create I-V characteristics for multiple materials"""
        physics = __import__('modules.physics_engine', fromlist=['MOSFETPhysics']).MOSFETPhysics()
        
        V_ds_range = np.linspace(0, 10, 50)
        V_gs_values = [2, 3, 4, 5]
        
        fig = go.Figure()
        
        for material_name, material_data in materials_data.items():
            for V_gs in V_gs_values:
                I_d_values = []
                for V_ds in V_ds_range:
                    try:
                        I_d, _ = physics.calculate_drain_current(V_gs, V_ds, material_data, geometry)
                        I_d_values.append(I_d * 1000)  # mA
                    except:
                        I_d_values.append(0)
                
                fig.add_trace(go.Scatter(
                    x=V_ds_range, 
                    y=I_d_values,
                    name=f"{material_name} V_gs={V_gs}V",
                    line=dict(dash='dash' if V_gs == 5 else 'solid')
                ))
        
        fig.update_layout(
            title="I-V Characteristics Comparison",
            xaxis_title="Drain-Source Voltage V_ds (V)",
            yaxis_title="Drain Current I_d (mA)",
            hovermode="x unified"
        )
        return fig
    
    def create_material_radar_chart(self, materials_data):
        """Create radar chart comparing material properties"""
        categories = ['Bandgap', 'Mobility', 'Thermal Conductivity', 'Breakdown Field']
        
        fig = go.Figure()
        
        for material_name, properties in materials_data.items():
            values = [
                properties['bandgap_value'] / 3.5,  # Normalized
                properties['electron_mobility_value'] / 2000,
                properties['thermal_conductivity_value'] / 500, 
                properties['breakdown_field_value'] / 3.5,
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the polygon
                theta=categories + [categories[0]],
                fill='toself',
                name=material_name
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Material Properties Comparison"
        )
        return fig
    
    def create_application_comparison(self, comparison_data):
        """Create bar chart comparing materials in applications"""
        materials = [data['material'] for data in comparison_data]
        efficiencies = [data['results']['efficiency'] for data in comparison_data]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=materials, 
            y=efficiencies,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        ))
        
        fig.update_layout(
            title="Efficiency Comparison in Application",
            xaxis_title="Material",
            yaxis_title="Efficiency (%)"
        )
        return fig