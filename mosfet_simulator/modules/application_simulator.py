# modules/application_simulator.py
"""
APPLICATION SIMULATOR - Test MOSFETs in real circuits
"""

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
                - **MOSFET Role:** Switching element - turns ON/OFF to control output
                - **Key Requirements:** Fast switching, low R_ds(on), good thermal performance
                """
            },
            "RF Power Amplifier": {
                "type": "RF Applications", 
                "description": "Amplifies RF signals for transmission",
                "parameters": {"freq": 2.4e9, "P_out": 10, "gain": 20},
                "performance_metrics": ["efficiency", "linearity", "bandwidth"],
                "explanation": """
                **RF Power Amplifier Application:**
                - **Purpose:** Amplifies high-frequency signals for communication
                - **MOSFET Role:** Active amplifying device
                - **Key Requirements:** High f_T, good linearity, thermal stability
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
                - **MOSFET Role:** Switching element (both NMOS and PMOS)
                - **Key Requirements:** Symmetric switching, low leakage
                """
            }
        }
    
    def simulate_application(self, mosfet_params, application_name):
        """Simulate MOSFET performance in specific application"""
        app = self.applications[application_name]
        material = mosfet_params['channel_material']
        
        # Calculate application-specific performance
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
        
        **Why {material} performs this way:**
        {self._get_material_analysis(material, application['type'])}
        """
    
    def _get_material_analysis(self, material, app_type):
        analyses = {
            'Silicon (Si)': {
                'Power Electronics': "Good balance of cost and performance, but limited by switching losses",
                'RF Applications': "Limited by lower electron mobility and frequency response",
                'Digital Circuits': "Excellent for digital applications due to mature CMOS technology"
            },
            'Gallium Nitride (GaN)': {
                'Power Electronics': "Excellent for high-frequency switching due to high electron mobility",
                'RF Applications': "Superior for RF due to high electron velocity", 
                'Digital Circuits': "Less common for digital but offers speed advantages"
            },
            'Silicon Carbide (SiC)': {
                'Power Electronics': "Best for high-temperature and high-voltage applications",
                'RF Applications': "Good for high-power RF but limited by lower mobility",
                'Digital Circuits': "Not typically used for digital circuits"
            }
        }
        return analyses.get(material, {}).get(app_type, "Standard performance")