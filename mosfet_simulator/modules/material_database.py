# modules/material_database.py
"""
COMPREHENSIVE MATERIAL DATABASE WITH PHYSICS EXPLANATIONS
"""

MATERIAL_PROPERTIES = {
    "Silicon (Si)": {
        "type": "Semiconductor",
        "bandgap_value": 1.12,  # eV
        "bandgap_explanation": "▶ Moderate bandgap allows good balance between conductivity and breakdown voltage.",
        "electron_mobility_value": 1400,  # cm²/V·s
        "electron_mobility_explanation": "▶ Determines how fast electrons move under electric field.",
        "thermal_conductivity_value": 150,  # W/m·K
        "thermal_conductivity_explanation": "▶ Critical for power dissipation.",
        "breakdown_field_value": 0.3,  # MV/cm
        "breakdown_field_explanation": "▶ Maximum electric field before avalanche breakdown.",
        "dielectric_constant": 11.7,
        "saturation_velocity": 1e7,  # cm/s
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
        "breakdown_field_value": 3.3,  # MV/cm
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
        "breakdown_field": 10,  # MV/cm
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