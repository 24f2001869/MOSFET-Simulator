# modules/mosfet_builder.py
"""
CUSTOM LAYER-BY-LAYER MOSFET BUILDER
"""

class MOSFETBuilder:
    def __init__(self):
        self.layers = []
        self.layer_properties = {}
        
    def add_layer(self, layer_type, material, thickness, properties=None):
        """Add a layer to the MOSFET structure"""
        layer = {
            'type': layer_type,
            'material': material,
            'thickness': thickness,  # in nm
            'properties': properties or {}
        }
        self.layers.append(layer)
        
        # Generate explanation for this layer
        explanation = self._generate_layer_explanation(layer)
        self.layer_properties[layer_type] = explanation
        
    def _generate_layer_explanation(self, layer):
        """Generate cross-question ready explanation for each layer"""
        explanations = {
            'gate_metal': f"""
            **Gate Metal Layer ({layer['material']}):**
            - **Function:** Provides electrical contact to gate electrode
            - **Work Function:** Determines threshold voltage
            - **Thickness {layer['thickness']}nm:** Affects series resistance
            - **Why {layer['material']}?** {self._get_metal_explanation(layer['material'])}
            """,
            
            'gate_oxide': f"""
            **Gate Oxide Layer ({layer['material']}):**
            - **Function:** Insulates gate from channel, forms capacitor
            - **Dielectric Constant:** {self._get_oxide_property(layer['material'], 'dielectric_constant')}
            - **Thickness {layer['thickness']}nm:** Thinner = higher capacitance
            - **Why {layer['material']}?** {self._get_oxide_explanation(layer['material'])}
            """,
            
            'channel': f"""
            **Channel Layer ({layer['material']}):**
            - **Function:** Forms conduction path between source and drain
            - **Bandgap:** {self._get_material_property(layer['material'], 'bandgap_value')} eV
            - **Electron Mobility:** {self._get_material_property(layer['material'], 'electron_mobility_value')} cm²/V·s
            - **Why {layer['material']}?** {self._get_channel_explanation(layer['material'])}
            """,
            
            'source_drain': f"""
            **Source/Drain Regions ({layer['material']}):**
            - **Function:** Provide carrier injection/extraction
            - **Doping:** {layer['properties'].get('doping', 'N/A')}
            - **Why heavy doping?** Reduces parasitic resistance
            """,
            
            'substrate': f"""
            **Substrate Layer ({layer['material']}):**
            - **Function:** Mechanical support and thermal management
            - **Thermal Conductivity:** {self._get_material_property(layer['material'], 'thermal_conductivity_value')} W/m·K
            - **Why {layer['material']}?** {self._get_substrate_explanation(layer['material'])}
            """
        }
        
        return explanations.get(layer['type'], "Layer explanation not available.")
    
    def _get_metal_explanation(self, metal):
        explanations = {
            'Aluminum': "Low resistance, easy to process",
            'Copper': "Lower resistivity than Al",
            'Tungsten': "High temperature stability",
            'Polysilicon': "Traditional gate material"
        }
        return explanations.get(metal, "Standard gate electrode material")
    
    def _get_oxide_explanation(self, oxide):
        explanations = {
            'SiO₂': "Excellent interface with Si, high breakdown field",
            'HfO₂': "High-κ dielectric reduces gate leakage",
            'Al₂O₃': "Good thermal stability"
        }
        return explanations.get(oxide, "Gate insulation material")
    
    def _get_channel_explanation(self, material):
        explanations = {
            'Silicon (Si)': "Mature technology, good mobility, cost-effective",
            'Gallium Nitride (GaN)': "High electron mobility, wide bandgap",
            'Silicon Carbide (SiC)': "Excellent thermal conductivity",
            'Gallium Arsenide (GaAs)': "Very high electron mobility"
        }
        return explanations.get(material, "Channel material")
    
    def _get_substrate_explanation(self, material):
        explanations = {
            'Silicon': "Low cost, excellent crystal quality",
            'Sapphire': "Good insulator for RF applications",
            'Silicon Carbide': "Excellent thermal conductor",
            'GaN': "Native substrate, best performance"
        }
        return explanations.get(material, "Mechanical support")
    
    def _get_material_property(self, material, property_name):
        # Import here to avoid circular imports
        from .material_database import MATERIAL_PROPERTIES
        if material in MATERIAL_PROPERTIES:
            return MATERIAL_PROPERTIES[material].get(property_name, 'N/A')
        return 'N/A'
    
    def _get_oxide_property(self, oxide, property_name):
        from .material_database import OXIDE_PROPERTIES
        if oxide in OXIDE_PROPERTIES:
            return OXIDE_PROPERTIES[oxide].get(property_name, 'N/A')
        return 'N/A'
    
    def calculate_overall_performance(self):
        """Calculate overall device performance from layer stack"""
        # Simplified performance estimation
        if not self.layers:
            return {}, "No layers defined"
            
        performance = {
            'estimated_vth': 0.7,
            'max_current_density': 100,
            'breakdown_voltage': 50,
            'switching_speed': 1e9,
        }
        
        explanation = """
        **Overall Device Performance Analysis:**
        
        **Key Factors:**
        - **Threshold Voltage:** Affected by gate material and oxide
        - **Current Density:** Limited by channel mobility  
        - **Breakdown Voltage:** Determined by channel material
        - **Switching Speed:** Related to carrier mobility
        
        **Design Trade-offs:**
        - Thinner oxide = better control but higher leakage
        - Higher mobility = faster switching
        - Wide bandgap = better temperature stability
        """
        
        return performance, explanation
    
    def get_cross_section_svg(self):
        """Generate SVG representation"""
        if not self.layers:
            return "<svg width='400' height='200'><text x='200' y='100'>No layers defined</text></svg>"
            
        svg_template = """
        <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect x="50" y="50" width="300" height="200" fill="lightgray" stroke="black"/>
            {layers}
            <text x="200" y="280" text-anchor="middle" font-size="12">MOSFET Cross-Section</text>
        </svg>
        """
        
        layers_svg = ""
        y_position = 50
        layer_height = 200 / len(self.layers)
        
        colors = {
            'gate_metal': '#FFD700',
            'gate_oxide': '#87CEEB',
            'channel': '#98FB98',
            'source_drain': '#FFB6C1',
            'substrate': '#D2B48C'
        }
        
        for layer in self.layers:
            color = colors.get(layer['type'], '#CCCCCC')
            layers_svg += f'<rect x="50" y="{y_position}" width="300" height="{layer_height}" fill="{color}" stroke="black"/>'
            layers_svg += f'<text x="60" y="{y_position + 15}" font-size="10">{layer["type"]}</text>'
            layers_svg += f'<text x="60" y="{y_position + 30}" font-size="10">{layer["material"]}</text>'
            y_position += layer_height
            
        return svg_template.format(layers=layers_svg)