# ESD and Latch-up Guidelines for {{ technology_name | upper }}

## 1. Introduction

These are the specific ESD and latch-up guidelines for the **{{ technology_name }}** process technology. This document provides comprehensive design rules and recommendations to ensure robust ESD protection and latch-up immunity.

**Document Version:** Generated (Auto-generated)  
**Technology Node:** {{ technology_name }}  
**Process Type:** {{ process_type | default("Standard CMOS") }}

## 2. General ESD Requirements

### 2.1 Target ESD Levels
- **Human Body Model (HBM):** {{ esd_levels.hbm }}
- **Charged Device Model (CDM):** {{ esd_levels.cdm }}
{% if esd_levels.mm is defined -%}
- **Machine Model (MM):** {{ esd_levels.mm }}
{% endif %}

### 2.2 ESD Protection Strategy
{% if advanced_protection_scheme %}
- **Protection Scheme:** Advanced multi-stage protection
- **Details:** {{ advanced_protection_scheme_details }}
{% else %}
- **Protection Scheme:** Standard single-stage protection
- **Implementation:** Basic clamp and guard ring approach
{% endif %}

### 2.3 Design Methodology
- All I/O pads must include primary ESD protection devices
- Core circuits require secondary protection for CDM compliance
- Power supply clamps are mandatory for robust ESD performance
- ESD current paths must be clearly defined and optimized

## 3. Latch-up Prevention Rules

### 3.1 General Latch-up Requirements
{{ latch_up_rules.rule1 }}

### 3.2 Spacing Requirements
- **Minimum NWELL to PSUB spacing near I/O:** {{ latch_up_rules.nwell_psub_spacing_io }}
- **Minimum guard ring width:** {{ latch_up_rules.guard_ring_width | default("2.0μm") }}
- **Substrate contact spacing:** {{ latch_up_rules.substrate_contact_spacing | default("10μm maximum") }}

### 3.3 Well and Substrate Contacts
- NWELL must have regular N+ contacts to VDD
- PSUB must have regular P+ contacts to VSS
- Contact resistance should be minimized
- Contacts must be placed strategically near switching circuits

### 3.4 Layout Guidelines
{% if latch_up_rules.layout_guidelines is defined %}
{% for guideline in latch_up_rules.layout_guidelines %}
- {{ guideline }}
{% endfor %}
{% else %}
- Keep PMOS and NMOS devices adequately separated
- Use guard rings around sensitive analog circuits
- Minimize parasitic thyristor structures
- Ensure adequate substrate and well biasing
{% endif %}

## 4. Approved ESD Protection Devices

### 4.1 Standard ESD Clamps

| Clamp Name | Type | ESD Rating | Application | Notes |
|------------|------|------------|-------------|-------|
{% for clamp in approved_clamps %}
| {{ clamp.name }} | {{ clamp.type }} | {{ clamp.rating }} | {{ clamp.application | default("General I/O") }} | {{ clamp.notes | default("Standard usage") }} |
{% endfor %}

### 4.2 Clamp Selection Guidelines
- **Primary Protection:** Use for direct I/O pad protection
- **Secondary Protection:** Use for internal circuit protection
- **Power Clamps:** Required between all power supply pairs
- **Special Purpose:** For specific applications (RF, analog, high-speed)

### 4.3 Implementation Requirements
{% if clamp_requirements is defined %}
{% for requirement in clamp_requirements %}
- {{ requirement }}
{% endfor %}
{% else %}
- All clamps must be characterized for the target technology
- Trigger voltages must be below oxide breakdown
- On-resistance must be sufficiently low for ESD current handling
- Parasitic capacitance must meet signal integrity requirements
{% endif %}

## 5. Design Rules and Constraints

### 5.1 Physical Design Rules
{% if design_rules is defined %}
{% for category, rules in design_rules.items() %}

#### {{ category | title }}
{% for rule in rules %}
- **{{ rule.name }}:** {{ rule.value }} ({{ rule.description | default("") }})
{% endfor %}
{% endfor %}
{% else %}
- **Minimum metal width for ESD paths:** 10μm
- **Maximum current density:** 1mA/μm for sustained operation
- **Via redundancy:** Minimum 2x for ESD current paths
- **Metal line spacing:** Follow standard DRC with 2x safety margin near ESD devices
{% endif %}

### 5.2 Electrical Constraints
- **Maximum allowable resistance:** {{ electrical_constraints.max_resistance | default("100Ω") }} for ESD current paths
- **Minimum trigger voltage:** {{ electrical_constraints.min_trigger_voltage | default("VDD + 0.3V") }}
- **Maximum clamping voltage:** {{ electrical_constraints.max_clamp_voltage | default("2 × VDD") }}
- **Leakage current limit:** {{ electrical_constraints.max_leakage | default("1μA @ operating temperature") }}

## 6. Verification and Testing

### 6.1 Design Verification Checklist
- [ ] All I/O pads have appropriate ESD protection
- [ ] Power supply clamps are present and correctly sized
- [ ] Guard rings are implemented where required
- [ ] ESD current paths are verified and optimized
- [ ] Latch-up spacing rules are met
- [ ] Parasitic thyristor structures are identified and mitigated

### 6.2 Required Simulations
{% if simulation_requirements is defined %}
{% for sim in simulation_requirements %}
- **{{ sim.type }}:** {{ sim.description }}
  - Tools: {{ sim.tools | join(", ") }}
  - Criteria: {{ sim.criteria }}
{% endfor %}
{% else %}
- **TLP (Transmission Line Pulse) Analysis:** Verify ESD device behavior
- **HBM/CDM Simulation:** Full-chip ESD simulation
- **Latch-up Simulation:** Verify thyristor trigger conditions
- **Parasitic Extraction:** Verify ESD current paths
{% endif %}

### 6.3 Test Requirements
- HBM testing per JEDEC JS-001 standard
- CDM testing per JEDEC JS-002 standard
- Latch-up testing per JEDEC JEP78 standard
- Device-level TLP characterization

## 7. Technology-Specific Considerations

### 7.1 Process Variations
{% if process_variations is defined %}
{% for variation in process_variations %}
- **{{ variation.parameter }}:** {{ variation.description }}
  - Impact: {{ variation.impact }}
  - Mitigation: {{ variation.mitigation }}
{% endfor %}
{% else %}
- Process corners affect ESD device performance
- Temperature variations impact trigger voltages
- Oxide thickness variations affect breakdown voltages
- Metal sheet resistance affects ESD current distribution
{% endif %}

### 7.2 Special Requirements
{% if special_requirements is defined %}
{% for req in special_requirements %}
- **{{ req.category }}:** {{ req.description }}
{% endfor %}
{% else %}
- High-voltage I/O requires enhanced protection schemes
- RF circuits need low-capacitance ESD devices
- Analog circuits require careful noise isolation
- High-speed interfaces need optimized parasitic control
{% endif %}

## 8. Documentation and Sign-off Requirements

### 8.1 Required Deliverables
- ESD protection implementation report
- Latch-up analysis and mitigation report
- Simulation results and verification summary
- Test plan and acceptance criteria
- Design review checklists and sign-offs

### 8.2 Review Process
1. **Initial Design Review:** Verify protection strategy
2. **Implementation Review:** Check layout and routing
3. **Verification Review:** Validate simulation results
4. **Final Sign-off:** Confirm all requirements are met

## 9. References and Standards

### 9.1 Industry Standards
- JEDEC JS-001: Human Body Model ESD Test
- JEDEC JS-002: Charged Device Model ESD Test
- JEDEC JEP78: IC Latch-up Test
- ESDA SP5.1: ESD Design Methodologies

### 9.2 Internal References
{% if internal_references is defined %}
{% for ref in internal_references %}
- {{ ref.title }}: {{ ref.description }}
{% endfor %}
{% else %}
- Technology Design Rule Manual
- ESD Device Characterization Report
- Latch-up Analysis Methodology
- Process Design Kit (PDK) Documentation
{% endif %}

---

**Document Control:**
- **Generated:** Auto-generated
- **Technology:** {{ technology_name }}
- **Revision:** Auto-generated from configuration
- **Status:** {{ document_status | default("Active") }}

*This document is automatically generated. For questions or updates, please modify the technology configuration and regenerate.*
