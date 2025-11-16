# modules/physics_engine.py
"""
ADVANCED MOSFET PHYSICS ENGINE WITH CROSS-QUESTION EXPLANATIONS
"""

import numpy as np

class MOSFETPhysics:
    def __init__(self):
        self.explanations = {}
        
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
    
    def calculate_breakdown_voltage(self, material, thickness):
        """
        Calculate breakdown voltage based on material properties
        """
        E_br = material.get('breakdown_field_value', 0.3) * 1e6  # Convert to V/cm
        V_br = E_br * thickness * 1e-4  # Simple approximation
        
        explanation = f"""
        **Breakdown Voltage Analysis:**
        - **Material Breakdown Field:** {material.get('breakdown_field_value', 0.3)} MV/cm
        - **Calculated V_br:** {V_br:.1f} V
        
        **Physics Behind Breakdown:**
        1. High electric field accelerates carriers
        2. Carriers gain energy to create electron-hole pairs (impact ionization)
        3. Avalanche multiplication leads to uncontrolled current
        4. **Wide bandgap advantage:** Requires more energy for ionization
        """
        
        self.explanations['breakdown'] = explanation
        return V_br
    
    def get_material_comparison(self, materials):
        """
        Compare multiple materials for educational purposes
        """
        comparison = "## Material Properties Comparison\n\n"
        comparison += "| Property | " + " | ".join(materials.keys()) + " |\n"
        comparison += "|----------|" + "|".join(["----------"] * len(materials)) + "|\n"
        
        properties = ['bandgap_value', 'electron_mobility_value', 'thermal_conductivity_value', 'breakdown_field_value']
        prop_names = ['Bandgap (eV)', 'Mobility (cm²/V·s)', 'Thermal Cond. (W/m·K)', 'Breakdown Field (MV/cm)']
        
        for prop, name in zip(properties, prop_names):
            row = f"| {name} |"
            for material in materials.values():
                row += f" {material.get(prop, 'N/A')} |"
            comparison += row + "\n"
        
        return comparison