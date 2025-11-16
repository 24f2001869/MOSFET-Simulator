# modules/3d_visualization.py
"""
3D VISUALIZATION ENGINE
Interactive 3D MOSFET structure visualization
"""

import plotly.graph_objects as go
import numpy as np

class ThreeDVisualization:
    def __init__(self):
        self.colors = {
            'gate_metal': '#FFD700',
            'gate_oxide': '#87CEEB', 
            'channel': '#98FB98',
            'source_drain': '#FFB6C1',
            'substrate': '#D2B48C'
        }
    
    def create_3d_mosfet(self, layers):
        """Create interactive 3D MOSFET visualization"""
        fig = go.Figure()
        
        y_position = 0
        for layer in layers:
            color = self.colors.get(layer['type'], '#CCCCCC')
            
            # Create simple 3D representation
            fig.add_trace(go.Scatter3d(
                x=[0, 1, 1, 0, 0],
                y=[y_position, y_position, y_position + layer['thickness']/100, 
                   y_position + layer['thickness']/100, y_position],
                z=[0, 0, 0, 0, 0],
                mode='lines',
                line=dict(color=color, width=5),
                name=f"{layer['type']}: {layer['material']}"
            ))
            
            # Add fill
            fig.add_trace(go.Mesh3d(
                x=[0, 1, 1, 0],
                y=[y_position, y_position, y_position + layer['thickness']/100, y_position + layer['thickness']/100],
                z=[0, 0, 0, 0],
                color=color,
                opacity=0.6,
                name=f"{layer['type']} Fill"
            ))
            
            y_position += layer['thickness']/100
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Width',
                yaxis_title='Thickness',
                zaxis_title='Length',
                aspectmode='data'
            ),
            title="3D MOSFET Structure",
            width=800,
            height=500
        )
        
        return fig
    
    def create_electric_field_visualization(self, V_gs, V_ds, geometry):
        """Visualize electric field distribution"""
        # Create a simple 2D heatmap for electric field
        x = np.linspace(0, geometry.get('length', 1e-6)*1e6, 20)  # μm
        y = np.linspace(0, geometry.get('width', 1e-6)*1e6, 20)   # μm
        
        X, Y = np.meshgrid(x, y)
        
        # Simplified electric field calculation
        if V_gs > 0.7:  # Above threshold
            E_max = V_gs / (geometry.get('oxide_thickness', 2e-9) * 1e9)  # V/μm
            # Create gradient from source to drain
            Z = E_max * (1 - X/np.max(X)) * np.exp(-Y/np.max(Y))
        else:
            Z = np.zeros_like(X)
        
        fig = go.Figure(data=[
            go.Heatmap(
                x=x, y=y, z=Z,
                colorscale='Viridis',
                hoverongaps=False
            )
        ])
        
        fig.update_layout(
            title="Electric Field Distribution in Channel",
            xaxis_title='Channel Length (μm)',
            yaxis_title='Channel Width (μm)'
        )
        
        return fig
    
    def create_simple_3d_structure(self):
        """Create a simple 3D MOSFET structure for demonstration"""
        fig = go.Figure()
        
        # Create a simple cube representation
        fig.add_trace(go.Mesh3d(
            x=[0, 1, 1, 0, 0, 1, 1, 0],
            y=[0, 0, 1, 1, 0, 0, 1, 1],
            z=[0, 0, 0, 0, 1, 1, 1, 1],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color='lightblue',
            opacity=0.6
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y', 
                zaxis_title='Z'
            ),
            title="Simple 3D MOSFET Structure"
        )
        
        return fig