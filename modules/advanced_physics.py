# modules/advanced_physics.py
"""
ADVANCED MOSFET PHYSICS MODELS
Adding quantum effects, short-channel effects, and temperature dependencies
"""

import numpy as np

class AdvancedMOSFETPhysics:
    def __init__(self):
        self.epsilon_0 = 8.854e-12
        self.q = 1.6e-19
        self.k = 1.38e-23
        
    def calculate_with_short_channel_effects(self, V_gs, V_ds, material, geometry, temperature=300):
        """
        Advanced model including:
        - Velocity saturation
        - Channel length modulation
        - Drain-induced barrier lowering (DIBL)
        - Temperature effects
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
        
        # Velocity saturation
        v_sat = material.get('saturation_velocity', 1e7) * 1e-2  # cm/s to m/s
        E_c = v_sat / mu_n  # Critical field
        
        # Current calculation with advanced effects
        if V_gs <= V_th_sc:
            I_d = 0
            region = "Cut-off"
        else:
            V_gt = V_gs - V_th_sc
            V_ds_sat = V_gt / (1 + (V_gt / (E_c * L)))
            
            if V_ds < V_ds_sat:
                # Linear region with velocity saturation
                I_d = (mu_n * C_ox * W / L) * (
                    V_gt * V_ds - 0.5 * V_ds**2
                ) / (1 + (V_ds / (E_c * L)))
                region = "Linear"
            else:
                # Saturation region with CLM
                I_d_sat = 0.5 * mu_n * C_ox * W / L * V_gt**2 / (1 + (V_gt / (E_c * L)))
                I_d = I_d_sat * (1 + lambda_clm * (V_ds - V_ds_sat))
                region = "Saturation"
        
        return I_d, region, {
            'effective_vth': V_th_sc,
            'dibl_effect': V_th_sc - V_th0,
            'velocity_saturation_factor': V_ds_sat / (V_gs - V_th_sc) if V_gs > V_th_sc else 0
        }
    
    def _temperature_dependent_mobility(self, material, T):
        """Temperature-dependent mobility model"""
        mu_300 = material['electron_mobility_value']
        # Simple power law model
        return mu_300 * (300 / T)**2.0
    
    def _temperature_dependent_vth(self, V_th0, T):
        """Temperature-dependent threshold voltage"""
        # V_th decreases with temperature
        return V_th0 - 0.002 * (T - 300)  # -2mV/°C typical
    
    def _dibl_effect(self, V_th, V_ds, L):
        """Drain-Induced Barrier Lowering"""
        # DIBL parameter (typical values)
        eta = 0.1 / (L * 1e6)  # Stronger for shorter channels
        return V_th - eta * V_ds
    
    def _channel_length_modulation(self, L, V_ds):
        """Channel Length Modulation parameter"""
        # Lambda inversely proportional to channel length
        return 0.1 / (L * 1e6)  # Typical value
    
    def calculate_quantum_effects(self, material, t_ox, E_field):
        """
        Quantum mechanical effects in ultra-thin oxides
        """
        # Simplified quantum tunneling model
        m_eff = 0.5 * 9.11e-31  # Effective electron mass
        phi_b = 3.1  # Barrier height in eV
        
        # Transmission probability (WKB approximation)
        if E_field > 0:
            k = np.sqrt(2 * m_eff * phi_b * self.q) / (1.054e-34)
            T_qm = np.exp(-2 * k * t_ox)
        else:
            T_qm = 0
            
        return {
            'tunneling_probability': T_qm,
            'quantum_capacitance': material.get('dielectric_constant', 3.9) * self.epsilon_0 / (t_ox + 0.3e-9)
        }