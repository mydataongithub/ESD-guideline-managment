import pandas as pd
import os

# Create sample data for ESD rules
esd_rules_data = {
    'Rule ID': ['ESD-001', 'ESD-002', 'ESD-003', 'LU-001', 'LU-002'],
    'Type': ['ESD', 'ESD', 'ESD', 'Latchup', 'Latchup'],
    'Title': [
        'Input Pin Protection',
        'Power Clamp Design',
        'Guard Ring Implementation',
        'Well Tap Spacing',
        'Substrate Contact Density'
    ],
    'Description': [
        'All input pins must have dual diode ESD protection connected to VDD and VSS rails',
        'Power clamps must be distributed across the chip with maximum 100um spacing',
        'Guard rings must surround all I/O pads with minimum 2um width',
        'N-well and P-well taps must be placed with maximum 25um spacing',
        'Substrate contacts must maintain minimum density of 1 contact per 100um²'
    ],
    'Severity': ['High', 'High', 'Medium', 'High', 'Medium'],
    'Category': ['IO', 'Power', 'IO', 'Layout', 'Layout']
}

# Create DataFrame
df = pd.DataFrame(esd_rules_data)

# Save to Excel
output_path = os.path.join('samples', 'sample_esd_rules.xlsx')
df.to_excel(output_path, index=False, sheet_name='ESD_Rules')

print(f"Created sample Excel file: {output_path}")

# Create a more complex Excel with multiple sheets
with pd.ExcelWriter(os.path.join('samples', 'complex_rules.xlsx')) as writer:
    # ESD Rules sheet
    df.to_excel(writer, sheet_name='ESD_Rules', index=False)
    
    # Technology info sheet
    tech_data = {
        'Technology': ['180nm CMOS', '65nm CMOS', '28nm CMOS'],
        'HBM Target': ['2kV', '1kV', '500V'],
        'CDM Target': ['500V', '250V', '125V']
    }
    pd.DataFrame(tech_data).to_excel(writer, sheet_name='Technology_Info', index=False)
    
    # Clamp specifications
    clamp_data = {
        'Clamp Name': ['GGNMOS_2x50', 'DIODE_STI', 'RC_CLAMP'],
        'Type': ['GGNMOS', 'Diode', 'RC-triggered'],
        'Trigger Voltage': ['6.5V', '0.7V', '5.5V'],
        'Holding Voltage': ['4.5V', '0.7V', '3.5V']
    }
    pd.DataFrame(clamp_data).to_excel(writer, sheet_name='Clamp_Specs', index=False)

print("Created complex Excel file with multiple sheets")
