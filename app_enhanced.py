# app_enhanced.py
"""
ULTIMATE MOSFET SIMULATION PLATFORM
Complete enhanced version with all modules integrated
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# =============================================================================
# MATERIAL DATABASE MODULE
# =============================================================================

MATERIAL_PROPERTIES = {
    "Silicon (Si)": {
        "type": "Semiconductor",
        "bandgap_value": 1.12,
        "bandgap_explanation": "▶ Moderate bandgap allows good balance between conductivity and breakdown voltage.",
        "electron_mobility_value": 1400,
        "electron_mobility_explanation": "▶ Determines how fast electrons move under electric field.",
        "thermal_conductivity_value": 150,
        "thermal_conductivity_explanation": "▶ Critical for power dissipation.",
        "breakdown_field_value": 0.3,
        "breakdown_field_explanation": "▶ Maximum electric field before avalanche breakdown.",
        "dielectric_constant": 11.7,
        "saturation_velocity": 1e7,
        "applications": "Low-frequency power devices, CMOS digital circuits"
    },
    
    "Gallium Nitride (GaN)": {
        "type": "Wide Bandgap Semiconductor",
        "bandgap_value": 3.4,
        "bandgap_explanation": "▶ Large bandgap enables high-temperature operation and radiation hardness.",
        "electron_mobility_value": 2000,
        "electron_mobility_explanation": "▶ High mobility combined with high breakdown enables excellent high-frequency performance.",
        "thermal_conductivity_value": 130,
        "thermal_conductivity_explanation": "▶ Good but not excellent thermal conductivity.",
        "breakdown_field_value": 3.3,
        "breakdown_field_explanation": "▶ 10x higher than Si! Enables much thinner drift regions.",
        "dielectric_constant": 9.0,
        "saturation_velocity": 2.5e7,
        "applications": "RF power amplifiers, fast switching converters, 5G infrastructure"
    },
    
    "Silicon Carbide (SiC)": {
        "type": "Wide Bandgap Semiconductor",
        "bandgap_value": 3.26,
        "bandgap_explanation": "▶ Wide bandgap enables high-temperature operation up to 600°C.",
        "electron_mobility_value": 950,
        "electron_mobility_explanation": "▶ Moderate mobility but excellent due to high breakdown field.",
        "thermal_conductivity_value": 490,
        "thermal_conductivity_explanation": "▶ Excellent! 3x better than Si. Enables very high power density.",
        "breakdown_field_value": 2.8,
        "breakdown_field_explanation": "▶ Very high breakdown enables compact high-voltage devices.",
        "dielectric_constant": 9.7,
        "saturation_velocity": 2.0e7,
        "applications": "High-voltage power devices, electric vehicle drivetrains, industrial motor drives"
    }
}

OXIDE_PROPERTIES = {
    "SiO₂": {
        "dielectric_constant": 3.9,
        "breakdown_field": 10,
        "explanation": "▶ Traditional gate oxide with excellent interface quality with Si.",
        "bandgap": 9.0,
        "thickness_range": "1-100 nm"
    },
    "HfO₂": {
        "dielectric_constant": 25,
        "breakdown_field": 5,
        "explanation": "▶ High-κ dielectric allows thicker physical layers with same capacitance.",
        "bandgap": 5.8,
        "thickness_range": "1-10 nm"
    },
    "Al₂O₃": {
        "dielectric_constant": 9.0,
        "breakdown_field": 8,
        "explanation": "▶ Good thermal stability, medium κ value.",
        "bandgap": 8.7,
        "thickness_range": "5-50 nm"
    }
}

# =============================================================================
# PHYSICS ENGINE MODULE
# =============================================================================

class MOSFETPhysics:
    def __init__(self):
        self.explanations = {}
        self.epsilon_0 = 8.854e-12
        self.q = 1.6e-19
        
    def calculate_drain_current(self, V_gs, V_ds, material, geometry):
        """
        Calculate drain current in linear and saturation regions
        """
        # Extract numerical values from material dictionary
        mu_n = material.get('electron_mobility_value', 1400)  # cm²/V·s
        C_ox = geometry.get('C_ox', 3.45e-3)  # F/m²
        W = geometry.get('width', 10e-6)  # m
        L = geometry.get('length', 1e-6)   # m
        V_th = geometry.get('V_th', 0.7)   # V
        
        # Convert mobility to m²/V·s for SI units
        mu_n_si = mu_n * 1e-4  # Convert cm²/V·s to m²/V·s
        
        # Calculate saturation voltage
        V_ds_sat = max(V_gs - V_th, 0)  # Ensure non-negative
        
        if V_gs <= V_th:
            # Cut-off region
            I_d = 0
            region = "Cut-off"
            explanation = """
            **Region: Cut-off**
            - **Condition:** V_gs ≤ V_th
            - **Channel:** No inversion layer formed
            - **Current:** Essentially zero (only leakage)
            - **Why?** Gate voltage insufficient to attract carriers
            """
            
        elif V_ds < V_ds_sat:
            # Linear region
            I_d = mu_n_si * C_ox * (W/L) * ((V_gs - V_th) * V_ds - 0.5 * V_ds**2)
            region = "Linear"
            explanation = f"""
            **Region: Linear (Triode)**
            - **Condition:** V_ds < V_ds_sat = {V_ds_sat:.2f}V
            - **Channel:** Fully formed from source to drain
            - **Behavior:** Acts like voltage-controlled resistor
            - **Current:** Increases with V_ds
            - **Why linear?** Uniform channel along entire length
            """
            
        else:
            # Saturation region
            I_d = 0.5 * mu_n_si * C_ox * (W/L) * (V_gs - V_th)**2
            region = "Saturation"
            explanation = f"""
            **Region: Saturation**
            - **Condition:** V_ds ≥ V_ds_sat = {V_ds_sat:.2f}V
            - **Pinch-off:** Channel pinches off near drain
            - **Behavior:** Constant current source
            - **Current:** Independent of V_ds (ideal case)
            - **Why saturate?** Carrier velocity saturation limits current
            """
        
        self.explanations['current_calculation'] = explanation
        self.explanations['operating_region'] = region
        
        return I_d, region

# =============================================================================
# ADVANCED PHYSICS MODULE
# =============================================================================

class AdvancedMOSFETPhysics:
    def __init__(self):
        self.epsilon_0 = 8.854e-12
        self.q = 1.6e-19
        self.k = 1.38e-23
        
    def calculate_with_short_channel_effects(self, V_gs, V_ds, material, geometry, temperature=300):
        """
        Advanced model including short-channel effects
        """
        # Extract parameters
        L = geometry['length']
        W = geometry['width']
        t_ox = geometry.get('oxide_thickness', 2e-9)
        V_th0 = geometry.get('V_th', 0.7)
        
        # Temperature effects
        T = temperature + 273.15  # Convert to Kelvin
        mu_n = self._temperature_dependent_mobility(material, T)
        V_th = self._temperature_dependent_vth(V_th0, T)
        
        # Short-channel effects
        V_th_sc = self._dibl_effect(V_th, V_ds, L)
        lambda_clm = self._channel_length_modulation(L, V_ds)
        
        # Oxide capacitance
        C_ox = material.get('dielectric_constant', 3.9) * self.epsilon_0 / t_ox
        
        # Basic current calculation (simplified)
        if V_gs <= V_th_sc:
            I_d = 0
            region = "Cut-off"
        else:
            V_gt = V_gs - V_th_sc
            V_ds_sat = V_gt
            
            if V_ds < V_ds_sat:
                # Linear region
                I_d = mu_n * C_ox * (W/L) * ((V_gs - V_th_sc) * V_ds - 0.5 * V_ds**2)
                region = "Linear"
            else:
                # Saturation region with CLM
                I_d_sat = 0.5 * mu_n * C_ox * (W/L) * (V_gs - V_th_sc)**2
                I_d = I_d_sat * (1 + lambda_clm * (V_ds - V_ds_sat))
                region = "Saturation"
        
        return I_d, region, {
            'effective_vth': V_th_sc,
            'dibl_effect': V_th_sc - V_th0,
            'velocity_saturation_factor': 0.8  # Simplified
        }
    
    def _temperature_dependent_mobility(self, material, T):
        """Temperature-dependent mobility model"""
        mu_300 = material['electron_mobility_value']
        return mu_300 * (300 / T)**2.0
    
    def _temperature_dependent_vth(self, V_th0, T):
        """Temperature-dependent threshold voltage"""
        return V_th0 - 0.002 * (T - 300)
    
    def _dibl_effect(self, V_th, V_ds, L):
        """Drain-Induced Barrier Lowering"""
        eta = 0.1 / (L * 1e6)
        return V_th - eta * V_ds
    
    def _channel_length_modulation(self, L, V_ds):
        """Channel Length Modulation parameter"""
        return 0.1 / (L * 1e6)
    
    def calculate_quantum_effects(self, material, t_ox, E_field):
        """
        Quantum mechanical effects in ultra-thin oxides
        """
        return {
            'tunneling_probability': 1e-6 if t_ox < 3e-9 else 1e-9,
            'quantum_capacitance': material.get('dielectric_constant', 3.9) * self.epsilon_0 / (t_ox + 0.3e-9)
        }

# =============================================================================
# MOSFET BUILDER MODULE
# =============================================================================

class MOSFETBuilder:
    def __init__(self):
        self.layers = []
        self.layer_properties = {}
        
    def add_layer(self, layer_type, material, thickness, properties=None):
        """Add a layer to the MOSFET structure"""
        layer = {
            'type': layer_type,
            'material': material,
            'thickness': thickness,
            'properties': properties or {}
        }
        self.layers.append(layer)
        
        explanation = self._generate_layer_explanation(layer)
        self.layer_properties[layer_type] = explanation
        
    def _generate_layer_explanation(self, layer):
        """Generate explanation for each layer"""
        explanations = {
            'gate_metal': f"""
            **Gate Metal Layer ({layer['material']}):**
            - **Function:** Provides electrical contact to gate electrode
            - **Work Function:** Determines threshold voltage
            - **Thickness {layer['thickness']}nm:** Affects series resistance
            """,
            
            'gate_oxide': f"""
            **Gate Oxide Layer ({layer['material']}):**
            - **Function:** Insulates gate from channel, forms capacitor
            - **Dielectric Constant:** {self._get_oxide_property(layer['material'], 'dielectric_constant')}
            - **Thickness {layer['thickness']}nm:** Thinner = higher capacitance
            """,
            
            'channel': f"""
            **Channel Layer ({layer['material']}):**
            - **Function:** Forms conduction path between source and drain
            - **Bandgap:** {self._get_material_property(layer['material'], 'bandgap_value')} eV
            - **Electron Mobility:** {self._get_material_property(layer['material'], 'electron_mobility_value')} cm²/V·s
            """,
            
            'source_drain': f"""
            **Source/Drain Regions ({layer['material']}):**
            - **Function:** Provide carrier injection/extraction
            - **Doping:** {layer['properties'].get('doping', 'N/A')}
            """,
            
            'substrate': f"""
            **Substrate Layer ({layer['material']}):**
            - **Function:** Mechanical support and thermal management
            - **Thermal Conductivity:** {self._get_material_property(layer['material'], 'thermal_conductivity_value')} W/m·K
            """
        }
        
        return explanations.get(layer['type'], "Layer explanation not available.")
    
    def _get_material_property(self, material, property_name):
        if material in MATERIAL_PROPERTIES:
            return MATERIAL_PROPERTIES[material].get(property_name, 'N/A')
        return 'N/A'
    
    def _get_oxide_property(self, oxide, property_name):
        if oxide in OXIDE_PROPERTIES:
            return OXIDE_PROPERTIES[oxide].get(property_name, 'N/A')
        return 'N/A'
    
    def calculate_overall_performance(self):
        """Calculate overall device performance"""
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

# =============================================================================
# APPLICATION SIMULATOR MODULE
# =============================================================================

class ApplicationSimulator:
    def __init__(self):
        self.applications = self._load_applications()
    
    def _load_applications(self):
        return {
            "Buck Converter": {
                "type": "Power Electronics",
                "description": "DC-DC step-down converter",
                "parameters": {"V_in": 12, "V_out": 3.3, "f_sw": 100000},
                "performance_metrics": ["efficiency", "power_loss", "temperature_rise"],
                "explanation": """
                **Buck Converter Application:**
                - **Purpose:** Steps down DC voltage efficiently
                - **MOSFET Role:** Switching element
                - **Key Requirements:** Fast switching, low R_ds(on)
                """
            },
            "RF Power Amplifier": {
                "type": "RF Applications", 
                "description": "Amplifies RF signals for transmission",
                "parameters": {"freq": 2.4e9, "P_out": 10, "gain": 20},
                "performance_metrics": ["efficiency", "linearity", "bandwidth"],
                "explanation": """
                **RF Power Amplifier Application:**
                - **Purpose:** Amplifies high-frequency signals
                - **MOSFET Role:** Active amplifying device
                - **Key Requirements:** High f_T, good linearity
                """
            },
            "CMOS Inverter": {
                "type": "Digital Circuits",
                "description": "Basic digital logic gate",
                "parameters": {"V_dd": 3.3, "load_capacitance": 1e-12},
                "performance_metrics": ["propagation_delay", "power_consumption"],
                "explanation": """
                **CMOS Inverter Application:**
                - **Purpose:** Fundamental building block of digital systems
                - **MOSFET Role:** Switching element
                - **Key Requirements:** Symmetric switching, low leakage
                """
            }
        }
    
    def simulate_application(self, mosfet_params, application_name):
        """Simulate MOSFET performance in specific application"""
        app = self.applications[application_name]
        material = mosfet_params['channel_material']
        
        results = {
            'efficiency': self._calculate_efficiency(material, app['type']),
            'power_loss': self._calculate_power_loss(material),
            'switching_speed': self._calculate_switching_speed(material),
            'thermal_rise': self._calculate_thermal_rise(material),
        }
        
        analysis = self._generate_analysis(material, app, results)
        return results, analysis
    
    def _calculate_efficiency(self, material, app_type):
        efficiencies = {
            'Silicon (Si)': {'Power Electronics': 85, 'RF Applications': 40, 'Digital Circuits': 95},
            'Gallium Nitride (GaN)': {'Power Electronics': 95, 'RF Applications': 60, 'Digital Circuits': 92},
            'Silicon Carbide (SiC)': {'Power Electronics': 92, 'RF Applications': 45, 'Digital Circuits': 90}
        }
        return efficiencies.get(material, {}).get(app_type, 80)
    
    def _calculate_power_loss(self, material):
        losses = {'Silicon (Si)': 2.0, 'Gallium Nitride (GaN)': 0.5, 'Silicon Carbide (SiC)': 1.0}
        return losses.get(material, 1.5)
    
    def _calculate_switching_speed(self, material):
        speeds = {'Silicon (Si)': 1e6, 'Gallium Nitride (GaN)': 5e6, 'Silicon Carbide (SiC)': 2e6}
        return speeds.get(material, 1e6)
    
    def _calculate_thermal_rise(self, material):
        rises = {'Silicon (Si)': 25, 'Gallium Nitride (GaN)': 15, 'Silicon Carbide (SiC)': 10}
        return rises.get(material, 20)
    
    def _generate_analysis(self, material, application, results):
        return f"""
        **{application['description']} - Performance Analysis:**
        
        **Material: {material}**
        - **Efficiency:** {results['efficiency']}% 
        - **Power Loss:** {results['power_loss']}W 
        - **Switching Speed:** {results['switching_speed']/1e6:.1f} MHz 
        - **Temperature Rise:** {results['thermal_rise']}°C 
        """

# =============================================================================
# ADVANCED APPLICATIONS MODULE
# =============================================================================

class AdvancedApplicationSimulator:
    def __init__(self):
        self.applications = self._load_advanced_applications()
    
    def _load_advanced_applications(self):
        return {
            "Electric Vehicle Motor Drive": {
                "type": "High-Power Automotive",
                "description": "3-phase inverter for EV traction motor",
                "parameters": {"V_bus": 400, "P_out": 150000, "f_sw": 20000},
                "circuit": "3-phase inverter with 6 MOSFETs",
                "key_metrics": ["efficiency", "power_density", "thermal_performance", "reliability"],
                "challenges": ["High current handling", "Thermal management", "EMI suppression"]
            },
            "5G Base Station PA": {
                "type": "RF Communications", 
                "description": "Power amplifier for 5G millimeter-wave",
                "parameters": {"freq": 28e9, "P_out": 10, "bandwidth": 100e6},
                "circuit": "Class-AB power amplifier",
                "key_metrics": ["PAE", "linearity", "thermal_stability", "ACLR"],
                "challenges": ["High frequency operation", "Linear efficiency", "Heat dissipation"]
            },
            "Server CPU Power Delivery": {
                "type": "High-Frequency Power Conversion",
                "description": "Multi-phase buck converter for CPU VRM",
                "parameters": {"V_in": 12, "V_out": 1.2, "I_max": 100, "f_sw": 500000},
                "circuit": "Multi-phase interleaved buck converter",
                "key_metrics": ["transient_response", "efficiency", "power_density", "cost"],
                "challenges": ["Fast transient response", "High current density", "Thermal management"]
            },
            "Solar Microinverter": {
                "type": "Renewable Energy",
                "description": "Grid-tied inverter for solar panels",
                "parameters": {"V_dc": 40, "V_ac": 230, "P_max": 300, "f_sw": 50000},
                "circuit": "H-bridge inverter with MPPT",
                "key_metrics": ["efficiency", "reliability", "cost", "power_quality"],
                "challenges": ["High efficiency requirements", "Grid compliance", "Long lifetime"]
            }
        }
    
    def simulate_advanced_application(self, mosfet_params, application_name, operating_conditions):
        """Advanced application simulation"""
        app = self.applications[application_name]
        material = mosfet_params['channel_material']
        
        if application_name == "Electric Vehicle Motor Drive":
            return self._simulate_ev_drive(material, operating_conditions)
        elif application_name == "5G Base Station PA":
            return self._simulate_5g_pa(material, operating_conditions)
        elif application_name == "Server CPU Power Delivery":
            return self._simulate_cpu_vrm(material, operating_conditions)
        elif application_name == "Solar Microinverter":
            return self._simulate_solar_inverter(material, operating_conditions)
        else:
            return self._simulate_general_application(material, operating_conditions)
    
    def _simulate_ev_drive(self, material, conditions):
        base_efficiency = {
            'Silicon (Si)': 96, 'Gallium Nitride (GaN)': 98.5, 'Silicon Carbide (SiC)': 97.5
        }
        
        return {
            'efficiency': base_efficiency.get(material, 95),
            'power_loss_reduction': 60 if material == 'Gallium Nitride (GaN)' else 40 if material == 'Silicon Carbide (SiC)' else 0,
            'system_weight': 85 if material == 'Gallium Nitride (GaN)' else 90 if material == 'Silicon Carbide (SiC)' else 100,
            'cooling_requirements': 'Forced air' if material == 'Gallium Nitride (GaN)' else 'Natural convection' if material == 'Silicon Carbide (SiC)' else 'Liquid cooling',
            'cost_analysis': 'Medium' if material == 'Gallium Nitride (GaN)' else 'Medium-High' if material == 'Silicon Carbide (SiC)' else 'Low',
            'key_advantage': 'Highest efficiency, smallest size' if material == 'Gallium Nitride (GaN)' else 'Best thermal performance' if material == 'Silicon Carbide (SiC)' else 'Cost-effective'
        }
    
    def _simulate_5g_pa(self, material, conditions):
        pae = {
            'Silicon (Si)': 35, 'Gallium Nitride (GaN)': 45, 'Silicon Carbide (SiC)': 38
        }
        
        return {
            'power_added_efficiency': pae.get(material, 30),
            'output_power': 10,
            'linearity': 'Excellent' if material == 'Gallium Nitride (GaN)' else 'Very Good' if material == 'Silicon Carbide (SiC)' else 'Good',
            'thermal_stability': 'Very Good' if material == 'Gallium Nitride (GaN)' else 'Excellent' if material == 'Silicon Carbide (SiC)' else 'Good',
            'key_advantage': 'Highest frequency capability' if material == 'Gallium Nitride (GaN)' else 'Good thermal handling' if material == 'Silicon Carbide (SiC)' else 'Cost-effective'
        }
    
    def _simulate_cpu_vrm(self, material, conditions):
        efficiency = {
            'Silicon (Si)': 88, 'Gallium Nitride (GaN)': 94, 'Silicon Carbide (SiC)': 91
        }
        
        return {
            'efficiency': efficiency.get(material, 85),
            'transient_response': 'Excellent' if material == 'Gallium Nitride (GaN)' else 'Very Good' if material == 'Silicon Carbide (SiC)' else 'Good',
            'power_density': 150 if material == 'Gallium Nitride (GaN)' else 120 if material == 'Silicon Carbide (SiC)' else 100,
            'cost_analysis': 'Medium' if material == 'Gallium Nitride (GaN)' else 'Medium-High' if material == 'Silicon Carbide (SiC)' else 'Low',
            'key_advantage': 'Fastest switching' if material == 'Gallium Nitride (GaN)' else 'Robust thermal performance' if material == 'Silicon Carbide (SiC)' else 'Cost-effective'
        }
    
    def _simulate_solar_inverter(self, material, conditions):
        efficiency = {
            'Silicon (Si)': 95, 'Gallium Nitride (GaN)': 97.5, 'Silicon Carbide (SiC)': 96.5
        }
        
        return {
            'efficiency': efficiency.get(material, 94),
            'reliability': 'Very Good' if material == 'Gallium Nitride (GaN)' else 'Excellent' if material == 'Silicon Carbide (SiC)' else 'Good',
            'lifetime': '20+ years' if material == 'Gallium Nitride (GaN)' else '25+ years' if material == 'Silicon Carbide (SiC)' else '15+ years',
            'cost_analysis': 'Medium' if material == 'Gallium Nitride (GaN)' else 'Medium-High' if material == 'Silicon Carbide (SiC)' else 'Low',
            'key_advantage': 'Highest efficiency' if material == 'Gallium Nitride (GaN)' else 'Longest lifetime' if material == 'Silicon Carbide (SiC)' else 'Proven reliability'
        }
    
    def _simulate_general_application(self, material, conditions):
        return {
            'efficiency': 90,
            'performance': 'Standard',
            'cost_analysis': 'Medium',
            'key_advantage': 'Balanced performance'
        }

# =============================================================================
# VISUALIZATION ENGINE MODULE
# =============================================================================

class VisualizationEngine:
    def __init__(self):
        self.colors = {
            'Si': '#1f77b4',
            'GaN': '#ff7f0e', 
            'SiC': '#2ca02c'
        }
    
    def create_iv_characteristics(self, materials_data, geometry):
        """Create I-V characteristics for multiple materials"""
        physics = MOSFETPhysics()
        
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
                properties['bandgap_value'] / 3.5,
                properties['electron_mobility_value'] / 2000,
                properties['thermal_conductivity_value'] / 500, 
                properties['breakdown_field_value'] / 3.5,
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
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

# =============================================================================
# 3D VISUALIZATION MODULE
# =============================================================================

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
            
            fig.add_trace(go.Mesh3d(
                x=[0, 1, 1, 0],
                y=[y_position, y_position, y_position + layer['thickness']/100, y_position + layer['thickness']/100],
                z=[0, 0, 1, 1],
                i=[0, 0, 0, 1],
                j=[1, 2, 3, 2],
                k=[2, 3, 1, 3],
                color=color,
                opacity=0.8,
                name=f"{layer['type']}: {layer['material']}"
            ))
            
            y_position += layer['thickness']/100
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Width',
                yaxis_title='Thickness',
                zaxis_title='Length'
            ),
            title="3D MOSFET Structure",
            width=800,
            height=500
        )
        
        return fig
    
    def create_electric_field_visualization(self, V_gs, V_ds, geometry):
        """Visualize electric field distribution"""
        x = np.linspace(0, geometry.get('length', 1e-6)*1e6, 20)
        y = np.linspace(0, geometry.get('width', 1e-6)*1e6, 20)
        
        X, Y = np.meshgrid(x, y)
        
        if V_gs > 0.7:
            E_max = V_gs / (geometry.get('oxide_thickness', 2e-9) * 1e9)
            Z = E_max * (1 - X/np.max(X)) * np.exp(-Y/np.max(Y))
        else:
            Z = np.zeros_like(X)
        
        fig = go.Figure(data=[
            go.Heatmap(
                x=x, y=y, z=Z,
                colorscale='Viridis'
            )
        ])
        
        fig.update_layout(
            title="Electric Field Distribution in Channel",
            xaxis_title='Channel Length (μm)',
            yaxis_title='Channel Width (μm)'
        )
        
        return fig

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    st.set_page_config(
        page_title="Ultimate MOSFET Simulator",
        layout="wide",
        page_icon="🎓"
    )
    
    st.title("🚀 Ultimate MOSFET Simulation Platform")
    st.markdown("**University of Hyderabad - BTech Project**")
    
    # Initialize session states
    if 'mosfet_builder' not in st.session_state:
        st.session_state.mosfet_builder = MOSFETBuilder()
    if 'advanced_physics' not in st.session_state:
        st.session_state.advanced_physics = AdvancedMOSFETPhysics()
    
    # Navigation
    pages = ["🏠 Home", "🔧 Basic Simulator", "⚡ Advanced Physics", "🏗️ Custom Builder", 
             "📊 Applications", "🎯 Advanced Apps", "📚 Education", "🔬 Research Tools"]
    
    page = st.sidebar.selectbox("Navigate to:", pages)
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "🔧 Basic Simulator":
        show_simulator()
    elif page == "⚡ Advanced Physics":
        show_advanced_physics()
    elif page == "🏗️ Custom Builder":
        show_custom_builder()
    elif page == "📊 Applications":
        show_applications()
    elif page == "🎯 Advanced Apps":
        show_advanced_applications()
    elif page == "📚 Education":
        show_education()
    elif page == "🔬 Research Tools":
        show_research_tools()

def show_home_page():
    st.header("🚀 Welcome to the Ultimate MOSFET Simulator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Complete MOSFET Analysis Platform
        
        **Advanced Features:**
        - ✅ **Real-time I-V Characteristic Simulation**
        - ✅ **Material Property Comparisons** (Si, GaN, SiC)
        - ✅ **Custom Layer-by-Layer MOSFET Design**
        - ✅ **Advanced Physics Models** with short-channel effects
        - ✅ **Application-Level Performance Testing**
        - ✅ **3D Visualization** of MOSFET structures
        - ✅ **Educational Explanations** & Cross-Question Prep
        - ✅ **Research Tools** for parameter analysis
        
        **Get Started:**
        1. **Basic Simulator**: Quick simulations with predefined materials
        2. **Advanced Physics**: Detailed models with quantum effects
        3. **Custom Builder**: Design your own MOSFET from scratch  
        4. **Applications**: Test MOSFETs in real-world circuits
        5. **Education**: Deep dive into semiconductor physics
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x200/4B7BF5/FFFFFF?text=MOSFET+Simulator", 
                caption="Advanced MOSFET Simulation")
        
        st.markdown("""
        ### 📈 Platform Capabilities
        - **3** Semiconductor Materials
        - **5** Layer Types  
        - **7** Application Types
        - **Advanced** Physics Models
        - **3D** Visualization
        - **Real-time** Calculations
        """)

def show_simulator():
    st.header("🔧 Basic MOSFET Simulator")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        material_choice = st.selectbox(
            "Channel Material:",
            list(MATERIAL_PROPERTIES.keys()),
            key="basic_material"
        )
        
        V_gs = st.slider("Gate Voltage V_gs (V)", 0.0, 10.0, 3.0, 0.1, key="basic_vgs")
        V_ds = st.slider("Drain Voltage V_ds (V)", 0.0, 20.0, 5.0, 0.5, key="basic_vds")
        
        gate_length = st.slider("Gate Length (μm)", 0.1, 10.0, 1.0, 0.1, key="basic_length")
        gate_width = st.slider("Gate Width (μm)", 1.0, 100.0, 10.0, 1.0, key="basic_width")
        
        compare_materials = st.checkbox("Compare Multiple Materials", key="basic_compare")
        if compare_materials:
            selected_materials = st.multiselect(
                "Select materials to compare:",
                list(MATERIAL_PROPERTIES.keys()),
                default=["Silicon (Si)", "Gallium Nitride (GaN)"],
                key="basic_materials_select"
            )
    
    with col2:
        material = MATERIAL_PROPERTIES[material_choice]
        
        st.subheader(f"Material: {material_choice}")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Bandgap", f"{material['bandgap_value']} eV")
            st.metric("Electron Mobility", f"{material['electron_mobility_value']} cm²/V·s")
        
        with col_b:
            st.metric("Thermal Conductivity", f"{material['thermal_conductivity_value']} W/m·K")
            st.metric("Breakdown Field", f"{material['breakdown_field_value']} MV/cm")
        
        physics = MOSFETPhysics()
        geometry = {
            'length': gate_length * 1e-6,
            'width': gate_width * 1e-6,
            'C_ox': 3.45e-3,
            'V_th': 0.7
        }
        
        try:
            I_d, region = physics.calculate_drain_current(V_gs, V_ds, material, geometry)
            
            st.subheader("Simulation Results")
            col_x, col_y = st.columns(2)
            
            with col_x:
                st.metric("Drain Current", f"{I_d*1000:.2f} mA")
                st.metric("Operating Region", region)
                
            with col_y:
                st.metric("Power", f"{I_d * V_ds:.3f} W")
                st.metric("Current Density", f"{(I_d*1000)/(gate_width):.2f} mA/mm")
            
            with st.expander("📚 Physics Explanation", expanded=True):
                for key, explanation in physics.explanations.items():
                    st.markdown(explanation)
                        
        except Exception as e:
            st.error(f"Calculation error: {e}")
        
        if compare_materials and len(selected_materials) > 1:
            st.subheader("Material Comparison")
            
            visualizer = VisualizationEngine()
            materials_data = {name: MATERIAL_PROPERTIES[name] for name in selected_materials}
            fig_iv = visualizer.create_iv_characteristics(materials_data, geometry)
            st.plotly_chart(fig_iv, use_container_width=True)
            
            fig_radar = visualizer.create_material_radar_chart(materials_data)
            st.plotly_chart(fig_radar, use_container_width=True)

def show_advanced_physics():
    st.header("⚡ Advanced MOSFET Physics")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        material_choice = st.selectbox(
            "Channel Material:",
            list(MATERIAL_PROPERTIES.keys()),
            key="adv_physics_material"
        )
        
        V_gs = st.slider("Gate Voltage V_gs (V)", 0.0, 5.0, 1.5, 0.1, key="adv_vgs")
        V_ds = st.slider("Drain Voltage V_ds (V)", 0.0, 10.0, 2.0, 0.1, key="adv_vds")
        
        gate_length = st.slider("Gate Length (nm)", 10, 1000, 100, 10, key="adv_length")
        oxide_thickness = st.slider("Oxide Thickness (nm)", 0.5, 10.0, 2.0, 0.1, key="adv_oxide")
        temperature = st.slider("Temperature (°C)", -55, 200, 25, 5, key="adv_temp")
    
    with col2:
        material = MATERIAL_PROPERTIES[material_choice]
        physics = st.session_state.advanced_physics
        
        geometry = {
            'length': gate_length * 1e-9,
            'width': 1e-6,
            'oxide_thickness': oxide_thickness * 1e-9,
            'V_th': 0.7
        }
        
        try:
            I_d, region, effects = physics.calculate_with_short_channel_effects(
                V_gs, V_ds, material, geometry, temperature
            )
            
            st.subheader("Advanced Simulation Results")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Drain Current", f"{I_d*1e6:.2f} μA")
                st.metric("Operating Region", region)
                
            with col_b:
                st.metric("Effective V_th", f"{effects['effective_vth']:.3f} V")
                st.metric("DIBL Effect", f"{effects['dibl_effect']*1000:.1f} mV")
                
            with col_c:
                st.metric("Temperature", f"{temperature}°C")
                st.metric("Gate Length", f"{gate_length} nm")
            
            quantum_effects = physics.calculate_quantum_effects(
                material, geometry['oxide_thickness'], V_gs/geometry['oxide_thickness']
            )
            
            with st.expander("🔬 Quantum Mechanical Effects", expanded=True):
                st.metric("Tunneling Probability", f"{quantum_effects['tunneling_probability']:.2e}")
                st.metric("Quantum Capacitance", f"{quantum_effects['quantum_capacitance']:.2e} F/m²")
                st.info("Quantum effects become significant for oxide thickness < 3nm")
            
            visualizer_3d = ThreeDVisualization()
            fig_field = visualizer_3d.create_electric_field_visualization(V_gs, V_ds, geometry)
            st.plotly_chart(fig_field, use_container_width=True)
            
        except Exception as e:
            st.error(f"Advanced calculation error: {e}")

def show_custom_builder():
    st.header("🏗️ Custom MOSFET Builder")
    
    builder = st.session_state.mosfet_builder
    
    tab1, tab2, tab3 = st.tabs(["Layer Builder", "Cross Section", "Performance"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add New Layer")
            
            layer_type = st.selectbox(
                "Layer Type:",
                ["gate_metal", "gate_oxide", "channel", "source_drain", "substrate"],
                key="layer_type_select"
            )
            
            if layer_type == "gate_metal":
                materials = ["Aluminum", "Copper", "Tungsten", "Polysilicon"]
            elif layer_type == "gate_oxide":
                materials = list(OXIDE_PROPERTIES.keys())
            elif layer_type == "channel":
                materials = list(MATERIAL_PROPERTIES.keys())
            elif layer_type == "source_drain":
                materials = ["Silicon (Si)", "Gallium Nitride (GaN)", "Silicon Carbide (SiC)"]
            else:
                materials = ["Silicon", "Sapphire", "Silicon Carbide", "GaN"]
            
            material = st.selectbox("Material:", materials, key="material_select")
            thickness = st.slider("Thickness (nm)", 1, 500, 100, 10, key="thickness_slider")
            
            properties = {}
            if layer_type in ["channel", "source_drain"]:
                doping_type = st.selectbox("Doping Type:", ["N-type", "P-type"], key="doping_type")
                doping_level = st.select_slider(
                    "Doping Concentration (cm⁻³)",
                    options=[1e14, 1e15, 1e16, 1e17, 1e18, 1e19],
                    value=1e17,
                    format_func=lambda x: f"{x:.0e}",
                    key="doping_level"
                )
                properties = {"doping_type": doping_type, "doping_level": doping_level}
            
            if st.button("➕ Add Layer", key="add_layer_btn"):
                builder.add_layer(layer_type, material, thickness, properties)
                st.success(f"✅ Added {material} {layer_type} layer!")
                st.rerun()
        
        with col2:
            st.subheader("Current Layer Stack")
            
            if builder.layers:
                st.info(f"📊 Total Layers: {len(builder.layers)}")
                
                for i, layer in enumerate(reversed(builder.layers)):
                    with st.expander(f"🏗️ Layer {len(builder.layers)-i}: {layer['type'].replace('_', ' ').title()}", 
                                   expanded=i==0):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**Material:** {layer['material']}")
                            st.write(f"**Thickness:** {layer['thickness']} nm")
                            if layer['properties']:
                                st.write(f"**Properties:** {layer['properties']}")
                        with col_b:
                            if st.button("🗑️ Remove", key=f"remove_{i}"):
                                builder.layers.pop(len(builder.layers)-1-i)
                                st.success("Layer removed!")
                                st.rerun()
                        
                        st.markdown(builder.layer_properties[layer['type']])
            else:
                st.info("🚀 No layers added yet. Start building your MOSFET!")
                
            if builder.layers and st.button("🗑️ Clear All Layers", type="secondary"):
                builder.layers.clear()
                builder.layer_properties.clear()
                st.success("All layers cleared!")
                st.rerun()
    
    with tab2:
        st.subheader("MOSFET Cross-Section Visualization")
        
        if builder.layers:
            svg = builder.get_cross_section_svg()
            st.components.v1.html(svg, height=400)
            
            st.subheader("3D Visualization")
            visualizer_3d = ThreeDVisualization()
            fig_3d = visualizer_3d.create_3d_mosfet(builder.layers)
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("⚠️ Add layers to see visualizations")
    
    with tab3:
        st.subheader("Device Performance Analysis")
        
        if builder.layers:
            performance, explanation = builder.calculate_overall_performance()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Threshold Voltage", f"{performance['estimated_vth']} V")
                st.metric("Max Current Density", f"{performance['max_current_density']} mA/mm")
                
            with col2:
                st.metric("Breakdown Voltage", f"{performance['breakdown_voltage']} V")
                st.metric("Switching Speed", f"{performance['switching_speed']/1e6:.0f} MHz")
                
            with col3:
                channel_layer = next((layer for layer in builder.layers if layer['type'] == 'channel'), None)
                if channel_layer:
                    material_name = channel_layer['material']
                    if material_name in MATERIAL_PROPERTIES:
                        material_data = MATERIAL_PROPERTIES[material_name]
                        st.metric("Channel Mobility", f"{material_data['electron_mobility_value']} cm²/V·s")
                        st.metric("Bandgap", f"{material_data['bandgap_value']} eV")
            
            with st.expander("🔍 Detailed Performance Analysis", expanded=True):
                st.markdown(explanation)
        else:
            st.info("🏗️ Build your MOSFET to see performance estimates")

def show_applications():
    st.header("📊 Basic Applications")
    
    app_simulator = ApplicationSimulator()
    visualizer = VisualizationEngine()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        application = st.selectbox(
            "Select Application:",
            list(app_simulator.applications.keys()),
            key="basic_app"
        )
        
        materials_to_compare = st.multiselect(
            "Materials to Compare:",
            list(MATERIAL_PROPERTIES.keys()),
            default=["Silicon (Si)", "Gallium Nitride (GaN)"],
            key="basic_app_materials"
        )
        
        if st.button("🚀 Run Simulation", key="basic_app_btn"):
            st.session_state.app_results = []
            for material in materials_to_compare:
                mosfet_params = {'channel_material': material}
                results, analysis = app_simulator.simulate_application(mosfet_params, application)
                st.session_state.app_results.append({
                    'material': material,
                    'results': results,
                    'analysis': analysis
                })
    
    with col2:
        app_info = app_simulator.applications[application]
        st.subheader(f"Application: {application}")
        st.markdown(app_info['explanation'])
        
        if hasattr(st.session_state, 'app_results') and st.session_state.app_results:
            fig = visualizer.create_application_comparison(st.session_state.app_results)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed Analysis")
            for result in st.session_state.app_results:
                with st.expander(f"🔬 {result['material']} Analysis", expanded=False):
                    st.markdown(result['analysis'])
        else:
            st.info("Select materials and run simulation to see results")

def show_advanced_applications():
    st.header("🎯 Advanced Real-World Applications")
    
    app_simulator = AdvancedApplicationSimulator()
    visualizer = VisualizationEngine()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        application = st.selectbox(
            "Select Advanced Application:",
            list(app_simulator.applications.keys()),
            key="advanced_app"
        )
        
        if application in app_simulator.applications:
            app_info = app_simulator.applications[application]
            st.subheader("Application Details")
            st.write(f"**Type:** {app_info['type']}")
            st.write(f"**Circuit:** {app_info['circuit']}")
            st.write(f"**Key Challenges:** {', '.join(app_info['challenges'])}")
        
        materials_to_compare = st.multiselect(
            "Compare Materials:",
            list(MATERIAL_PROPERTIES.keys()),
            default=["Silicon (Si)", "Gallium Nitride (GaN)", "Silicon Carbide (SiC)"],
            key="advanced_materials"
        )
        
        if st.button("🚀 Run Advanced Simulation", key="advanced_sim_btn"):
            st.session_state.advanced_app_results = []
            for material in materials_to_compare:
                try:
                    mosfet_params = {
                        'channel_material': material,
                        'geometry': {'length': 0.1e-6, 'width': 1e-6}
                    }
                    results = app_simulator.simulate_advanced_application(
                        mosfet_params, application, {}
                    )
                    st.session_state.advanced_app_results.append({
                        'material': material,
                        'results': results
                    })
                except Exception as e:
                    st.error(f"Error simulating {material}: {e}")
    
    with col2:
        if application in app_simulator.applications:
            app_info = app_simulator.applications[application]
            st.subheader(f"Advanced Application: {application}")
            st.markdown(app_info['description'])
        else:
            st.error("Selected application not found.")
            return
        
        if hasattr(st.session_state, 'advanced_app_results') and st.session_state.advanced_app_results:
            for result in st.session_state.advanced_app_results:
                with st.expander(f"📊 {result['material']} - Complete Analysis", expanded=True):
                    res = result['results']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'efficiency' in res:
                            st.metric("Efficiency", f"{res['efficiency']}%")
                        if 'power_added_efficiency' in res:
                            st.metric("Power Added Efficiency", f"{res['power_added_efficiency']}%")
                        if 'power_loss_reduction' in res:
                            st.metric("Power Loss Reduction", f"{res['power_loss_reduction']}%")
                            
                    with col2:
                        if 'system_weight' in res:
                            st.metric("System Weight", f"{res['system_weight']}%")
                        if 'cooling_requirements' in res:
                            st.metric("Cooling", res['cooling_requirements'])
                        if 'cost_analysis' in res:
                            st.metric("Cost", res['cost_analysis'])
                    
                    if 'key_advantage' in res:
                        st.info(f"**Key Advantage:** {res['key_advantage']}")
                    
                    st.markdown("### Application-Specific Insights")
                    if application == "Electric Vehicle Motor Drive":
                        efficiency_gain = res.get('efficiency', 0) - 95
                        if efficiency_gain > 0:
                            st.success(f"✅ {efficiency_gain}% efficiency gain → ~{efficiency_gain*2}km extra range")
                    
                    elif application == "5G Base Station PA":
                        st.success(f"✅ Higher efficiency → Reduced operating costs")
                        st.success(f"✅ Better thermal performance → Improved reliability")
        
        else:
            st.info("Select materials and run simulation to see advanced application analysis")

def show_education():
    st.header("📚 Educational Resources")
    
    tab1, tab2, tab3 = st.tabs(["MOSFET Fundamentals", "Material Science", "Viva Prep"])
    
    with tab1:
        st.subheader("MOSFET Operating Principles")
        st.markdown("""
        ### 🎯 How MOSFETs Work
        
        **Basic Operation:**
        1. **Gate Control**: Gate voltage creates electric field
        2. **Channel Formation**: Inversion layer forms when V_gs > V_th
        3. **Current Flow**: Electrons flow from source to drain
        4. **Pinch-off**: Channel pinches off in saturation region
        
        **Key Equations:**
        - **Linear Region**: I_d = μₙCₒₓ(W/L)[(V_gs - V_th)V_ds - ½V_ds²]
        - **Saturation Region**: I_d = ½μₙCₒₓ(W/L)(V_gs - V_th)²
        
        **Cross-Question Ready:**
        - What determines threshold voltage? → Work function, oxide charge, doping
        - Why does current saturate? → Channel pinch-off and velocity saturation
        - How does temperature affect operation? → Mobility decreases
        """)
    
    with tab2:
        st.subheader("Semiconductor Material Science")
        
        comparison_data = []
        for material, props in MATERIAL_PROPERTIES.items():
            comparison_data.append({
                'Material': material,
                'Bandgap (eV)': props['bandgap_value'],
                'Mobility (cm²/V·s)': props['electron_mobility_value'],
                'Thermal Cond. (W/m·K)': props['thermal_conductivity_value'],
                'Breakdown Field (MV/cm)': props['breakdown_field_value']
            })
        
        st.table(comparison_data)
        
        st.markdown("""
        **Material Selection Guidelines:**
        - **Silicon**: Cost-effective, mature technology
        - **GaN**: High frequency, fast switching
        - **SiC**: High temperature, high voltage
        
        **Key Trade-offs:**
        - Higher bandgap → Better temperature stability
        - Higher mobility → Faster switching
        - Better thermal conductivity → Higher power density
        """)
    
    with tab3:
        st.subheader("Viva Voce Preparation")
        st.markdown("""
        ### 🎓 Expected Questions & Answers
        
        **Basic Questions:**
        1. **What is the difference between enhancement and depletion mode?**
           - Enhancement: Normally OFF, needs positive V_gs
           - Depletion: Normally ON, needs negative V_gs to turn OFF
        
        2. **Why is gate oxide thickness important?**
           - Thinner oxide = higher capacitance = better control but more leakage
        
        **Intermediate Questions:**
        1. **Explain electron mobility significance**
           - Higher mobility = faster carrier transport = better high-frequency performance
        
        2. **Why wide bandgap for power devices?**
           - Higher breakdown voltage, better temperature stability
        
        **Advanced Questions:**
        1. **Compare GaN vs SiC for specific applications**
           - GaN: Better for high-frequency RF
           - SiC: Better for high-temperature power
        
        **Project Questions:**
        1. **Why this simulation approach?**
           - Educational focus with real-time feedback
           - Comprehensive material comparisons
           - Practical application testing
        """)

def show_research_tools():
    st.header("🔬 Research & Analysis Tools")
    
    tab1, tab2, tab3 = st.tabs(["Parameter Sweep", "Sensitivity Analysis", "Technology Comparison"])
    
    with tab1:
        st.subheader("Parameter Sweep Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sweep_parameter = st.selectbox(
                "Parameter to Sweep:",
                ["Gate Length", "Oxide Thickness", "Temperature", "Doping Concentration"]
            )
            
            material_research = st.selectbox(
                "Material:",
                list(MATERIAL_PROPERTIES.keys()),
                key="research_material"
            )
        
        with col2:
            st.subheader("Sweep Results")
            st.info("Parameter sweep analysis shows how device performance varies with different parameters")
            
            # Create sample sweep visualization
            x = np.linspace(10, 1000, 50)
            y1 = 1000 / np.sqrt(x)
            y2 = 0.1 * np.sqrt(x)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y1, name="Performance", line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=x, y=y2, name="Power", line=dict(color='red')))
            
            fig.update_layout(
                title="Parameter Sweep Analysis",
                xaxis_title="Gate Length (nm)",
                yaxis_title="Normalized Metric"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Sensitivity Analysis")
        st.markdown("""
        **Analyze how sensitive device performance is to various parameters:**
        
        - **Most sensitive**: Gate oxide thickness, channel length
        - **Moderately sensitive**: Doping concentration, temperature
        - **Less sensitive**: Channel width (for large devices)
        
        **Key Insights:**
        - Nanoscale devices are extremely sensitive to dimensional variations
        - Temperature stability varies significantly between materials
        - Process control becomes critical at advanced nodes
        """)
    
    with tab3:
        st.subheader("Technology Roadmap Comparison")
        
        tech_nodes = ["180nm", "90nm", "45nm", "28nm", "16nm", "7nm", "5nm", "3nm"]
        selected_nodes = st.multiselect("Select Technology Nodes:", tech_nodes, default=["90nm", "28nm", "7nm"])
        
        st.markdown("""
        **Evolution of Key Parameters:**
        
        | Node | Gate Length | Oxide Thickness | V_dd | Performance | Power |
        |------|-------------|-----------------|------|-------------|-------|
        | 180nm | 180nm | 4nm | 1.8V | 1x | 1x |
        | 90nm | 90nm | 2nm | 1.2V | 3x | 0.5x |
        | 28nm | 28nm | 1.2nm | 1.0V | 8x | 0.3x |
        | 7nm | 7nm | 0.7nm | 0.8V | 20x | 0.2x |
        
        **Beyond Silicon**: GaN and SiC enable performance beyond traditional scaling
        """)

if __name__ == "__main__":
    main()