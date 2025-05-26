# download_esd_images.py
"""Download and save ESD circuit images for the application"""

import os
import requests
import base64
from pathlib import Path

# Create directories
STATIC_DIR = Path("app/static/images/esd_circuits")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Define image sources - all will be created locally due to download restrictions
IMAGE_SOURCES = {}  # Empty since we'll create all images locally

# Additional placeholder images for specific circuits
PLACEHOLDER_CIRCUITS = {
    "esd_protection_overview": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">ESD Protection Overview</text>
  
  <!-- I/O Pad -->
  <rect x="30" y="120" width="60" height="60" fill="#ffcc99" stroke="black" stroke-width="2"/>
  <text x="60" y="155" text-anchor="middle" font-family="Arial" font-size="12">I/O Pad</text>
  
  <!-- Protection Diodes -->
  <polygon points="120,110 120,130 140,120" fill="black"/>
  <line x1="140" y1="120" x2="140" y2="80" stroke="black" stroke-width="2"/>
  <text x="150" y="85" font-family="Arial" font-size="10">to VDD</text>
  
  <polygon points="140,170 120,160 120,180" fill="black"/>
  <line x1="140" y1="170" x2="140" y2="210" stroke="black" stroke-width="2"/>
  <text x="150" y="205" font-family="Arial" font-size="10">to VSS</text>
  
  <!-- Signal path -->
  <line x1="90" y1="150" x2="250" y2="150" stroke="black" stroke-width="2"/>
  <text x="170" y="145" text-anchor="middle" font-family="Arial" font-size="10">To Core</text>
  
  <!-- Core Circuit -->
  <rect x="250" y="120" width="80" height="60" fill="#ccccff" stroke="black" stroke-width="2"/>
  <text x="290" y="155" text-anchor="middle" font-family="Arial" font-size="12">Core Circuit</text>
  
  <!-- Power Rails -->
  <line x1="20" y1="80" x2="350" y2="80" stroke="red" stroke-width="3"/>
  <text x="360" y="85" font-family="Arial" font-size="12" fill="red">VDD</text>
  
  <line x1="20" y1="210" x2="350" y2="210" stroke="blue" stroke-width="3"/>
  <text x="360" y="215" font-family="Arial" font-size="12" fill="blue">VSS</text>
  
  <!-- ESD Event -->
  <path d="M 60 100 L 50 90 L 70 90 L 60 80" stroke="orange" stroke-width="3" fill="none"/>
  <text x="75" y="95" font-family="Arial" font-size="10" fill="orange">ESD</text>
</svg>''',
        "filename": "esd_protection_overview.svg",
        "description": "Basic ESD protection circuit overview"
    },
    
    "ggnmos_clamp": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Grounded-Gate NMOS (ggNMOS) Clamp</text>
  
  <!-- NMOS Symbol -->
  <rect x="170" y="100" width="60" height="80" fill="none" stroke="black" stroke-width="2"/>
  <line x1="150" y1="140" x2="170" y2="140" stroke="black" stroke-width="2"/>
  <line x1="230" y1="140" x2="250" y2="140" stroke="black" stroke-width="2"/>
  <line x1="200" y1="100" x2="200" y2="80" stroke="black" stroke-width="2"/>
  <line x1="200" y1="180" x2="200" y2="200" stroke="black" stroke-width="2"/>
  
  <!-- Gate connection to ground -->
  <line x1="150" y1="140" x2="150" y2="200" stroke="black" stroke-width="2"/>
  <text x="145" y="165" text-anchor="end" font-family="Arial" font-size="10">Gate</text>
  
  <!-- Drain/Source labels -->
  <text x="200" y="75" text-anchor="middle" font-family="Arial" font-size="10">Drain</text>
  <text x="200" y="215" text-anchor="middle" font-family="Arial" font-size="10">Source</text>
  
  <!-- Parasitic BJT -->
  <circle cx="280" cy="140" r="30" fill="none" stroke="red" stroke-width="1" stroke-dasharray="3,3"/>
  <text x="280" y="185" text-anchor="middle" font-family="Arial" font-size="10" fill="red">Parasitic</text>
  <text x="280" y="195" text-anchor="middle" font-family="Arial" font-size="10" fill="red">NPN</text>
  
  <!-- Power Rails -->
  <line x1="50" y1="80" x2="350" y2="80" stroke="red" stroke-width="3"/>
  <text x="360" y="85" font-family="Arial" font-size="12" fill="red">I/O</text>
  
  <line x1="50" y1="200" x2="350" y2="200" stroke="blue" stroke-width="3"/>
  <text x="360" y="205" font-family="Arial" font-size="12" fill="blue">VSS</text>
  
  <!-- Annotations -->
  <text x="200" y="250" text-anchor="middle" font-family="Arial" font-size="11">Triggers at ~6-8V via snapback</text>
  <text x="200" y="265" text-anchor="middle" font-family="Arial" font-size="11">Low holding voltage ~1-2V</text>
</svg>''',
        "filename": "ggnmos_clamp.svg",
        "description": "Grounded-gate NMOS ESD clamp structure"
    },
    
    "diode_protection": {
        "svg_content": '''<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="250" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">ESD Diode Protection</text>
  
  <!-- I/O Pad -->
  <rect x="50" y="100" width="60" height="40" fill="#ffcc99" stroke="black" stroke-width="2"/>
  <text x="80" y="125" text-anchor="middle" font-family="Arial" font-size="12">I/O</text>
  
  <!-- Upper Diode to VDD -->
  <polygon points="150,80 150,100 170,90" fill="black"/>
  <line x1="110" y1="120" x2="150" y2="120" stroke="black" stroke-width="2"/>
  <line x1="150" y1="120" x2="150" y2="90" stroke="black" stroke-width="2"/>
  <line x1="170" y1="90" x2="170" y2="60" stroke="black" stroke-width="2"/>
  
  <!-- Lower Diode to VSS -->
  <polygon points="170,140 150,130 150,150" fill="black"/>
  <line x1="150" y1="120" x2="150" y2="140" stroke="black" stroke-width="2"/>
  <line x1="170" y1="140" x2="170" y2="180" stroke="black" stroke-width="2"/>
  
  <!-- To Core -->
  <line x1="150" y1="120" x2="250" y2="120" stroke="black" stroke-width="2"/>
  <rect x="250" y="100" width="80" height="40" fill="#ccccff" stroke="black" stroke-width="2"/>
  <text x="290" y="125" text-anchor="middle" font-family="Arial" font-size="12">Core</text>
  
  <!-- Power Rails -->
  <line x1="30" y1="60" x2="350" y2="60" stroke="red" stroke-width="3"/>
  <text x="360" y="65" font-family="Arial" font-size="12" fill="red">VDD</text>
  
  <line x1="30" y1="180" x2="350" y2="180" stroke="blue" stroke-width="3"/>
  <text x="360" y="185" font-family="Arial" font-size="12" fill="blue">VSS</text>
  
  <!-- Current paths -->
  <path d="M 80 105 L 80 90 L 165 90" stroke="green" stroke-width="2" fill="none" marker-end="url(#arrowgreen)"/>
  <text x="120" y="85" font-family="Arial" font-size="10" fill="green">+ESD</text>
  
  <path d="M 80 135 L 80 150 L 165 150" stroke="purple" stroke-width="2" fill="none" marker-end="url(#arrowpurple)"/>
  <text x="120" y="165" font-family="Arial" font-size="10" fill="purple">-ESD</text>
  
  <!-- Arrows -->
  <defs>
    <marker id="arrowgreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="green"/>
    </marker>
    <marker id="arrowpurple" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="purple"/>
    </marker>
  </defs>
</svg>''',
        "filename": "diode_protection.svg",
        "description": "ESD diode protection scheme"
    },
    
    "ic_layout_example": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">IC Layout - Spacing Rules</text>
  
  <!-- N-well -->
  <rect x="50" y="60" width="150" height="100" fill="#e6f2ff" stroke="blue" stroke-width="2"/>
  <text x="125" y="55" text-anchor="middle" font-family="Arial" font-size="12" fill="blue">N-well</text>
  
  <!-- P-well -->
  <rect x="220" y="60" width="150" height="100" fill="#ffe6e6" stroke="red" stroke-width="2"/>
  <text x="295" y="55" text-anchor="middle" font-family="Arial" font-size="12" fill="red">P-well</text>
  
  <!-- Well taps -->
  <rect x="70" y="100" width="20" height="20" fill="blue" stroke="black"/>
  <text x="80" y="95" text-anchor="middle" font-family="Arial" font-size="10">N+</text>
  
  <rect x="160" y="100" width="20" height="20" fill="blue" stroke="black"/>
  <text x="170" y="95" text-anchor="middle" font-family="Arial" font-size="10">N+</text>
  
  <rect x="240" y="100" width="20" height="20" fill="red" stroke="black"/>
  <text x="250" y="95" text-anchor="middle" font-family="Arial" font-size="10">P+</text>
  
  <rect x="330" y="100" width="20" height="20" fill="red" stroke="black"/>
  <text x="340" y="95" text-anchor="middle" font-family="Arial" font-size="10">P+</text>
  
  <!-- Spacing annotations -->
  <line x1="90" y1="110" x2="160" y2="110" stroke="green" stroke-width="1"/>
  <line x1="90" y1="105" x2="90" y2="115" stroke="green" stroke-width="1"/>
  <line x1="160" y1="105" x2="160" y2="115" stroke="green" stroke-width="1"/>
  <text x="125" y="130" text-anchor="middle" font-family="Arial" font-size="10" fill="green">Max 20μm</text>
  
  <line x1="200" y1="110" x2="220" y2="110" stroke="orange" stroke-width="1"/>
  <line x1="200" y1="105" x2="200" y2="115" stroke="orange" stroke-width="1"/>
  <line x1="220" y1="105" x2="220" y2="115" stroke="orange" stroke-width="1"/>
  <text x="210" y="130" text-anchor="middle" font-family="Arial" font-size="10" fill="orange">Min 15μm</text>
  
  <!-- Guard ring -->
  <rect x="40" y="50" width="170" height="120" fill="none" stroke="green" stroke-width="4" stroke-dasharray="5,5"/>
  <text x="45" y="45" font-family="Arial" font-size="10" fill="green">Guard Ring</text>
  
  <!-- Annotations -->
  <text x="200" y="200" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold">Critical Spacing Rules:</text>
  <text x="200" y="220" text-anchor="middle" font-family="Arial" font-size="11">• Well tap spacing: 20μm max</text>
  <text x="200" y="235" text-anchor="middle" font-family="Arial" font-size="11">• Well-to-well spacing: 15μm min</text>
  <text x="200" y="250" text-anchor="middle" font-family="Arial" font-size="11">• Guard ring width: 2μm min</text>
</svg>''',
        "filename": "ic_layout_example.svg",
        "description": "IC layout showing spacing rules"
    },
    
    "guard_ring_layout": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Guard Ring Layout Structure</text>
  
  <!-- Outer P+ Guard Ring -->
  <rect x="50" y="60" width="300" height="180" fill="none" stroke="red" stroke-width="8"/>
  <text x="45" y="55" text-anchor="end" font-family="Arial" font-size="12" fill="red">P+ Guard Ring (to VSS)</text>
  
  <!-- Inner N+ Guard Ring -->
  <rect x="80" y="90" width="240" height="120" fill="none" stroke="blue" stroke-width="8"/>
  <text x="85" y="85" font-family="Arial" font-size="12" fill="blue">N+ Guard Ring (to VDD)</text>
  
  <!-- Circuit Block -->
  <rect x="120" y="120" width="160" height="60" fill="#e6e6e6" stroke="black" stroke-width="2"/>
  <text x="200" y="155" text-anchor="middle" font-family="Arial" font-size="14">Protected Circuit</text>
  
  <!-- Contacts on guard rings -->
  <!-- P+ contacts -->
  <circle cx="60" cy="70" r="3" fill="black"/>
  <circle cx="80" cy="70" r="3" fill="black"/>
  <circle cx="100" cy="70" r="3" fill="black"/>
  <circle cx="120" cy="70" r="3" fill="black"/>
  <circle cx="140" cy="70" r="3" fill="black"/>
  
  <!-- N+ contacts -->
  <circle cx="90" cy="100" r="3" fill="black"/>
  <circle cx="110" cy="100" r="3" fill="black"/>
  <circle cx="130" cy="100" r="3" fill="black"/>
  <circle cx="150" cy="100" r="3" fill="black"/>
  
  <!-- Dimension arrows -->
  <line x1="58" y1="250" x2="82" y2="250" stroke="black" stroke-width="1" marker-start="url(#arrowstart)" marker-end="url(#arrowend)"/>
  <text x="70" y="265" text-anchor="middle" font-family="Arial" font-size="10">2μm min</text>
  
  <!-- Cross-section indicator -->
  <line x1="200" y1="60" x2="200" y2="240" stroke="green" stroke-width="2" stroke-dasharray="10,5"/>
  <text x="205" y="150" font-family="Arial" font-size="10" fill="green">A-A'</text>
  
  <!-- Legend -->
  <text x="50" y="280" font-family="Arial" font-size="11" font-weight="bold">Key Benefits:</text>
  <text x="50" y="295" font-family="Arial" font-size="10">• Collects minority carriers • Prevents latchup triggering</text>
  
  <!-- Arrow markers -->
  <defs>
    <marker id="arrowstart" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto">
      <path d="M9,0 L9,6 L0,3 z" fill="black"/>
    </marker>
    <marker id="arrowend" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="black"/>
    </marker>
  </defs>
</svg>''',
        "filename": "guard_ring_layout.svg",
        "description": "Guard ring layout structure"
    },
    
    "esd_warning_symbol": {
        "svg_content": '''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#f8f9fa"/>
  
  <!-- Warning Triangle -->
  <polygon points="100,30 170,150 30,150" fill="#ffcc00" stroke="black" stroke-width="3"/>
  
  <!-- Hand symbol -->
  <g transform="translate(100,90)">
    <!-- Palm -->
    <ellipse cx="0" cy="0" rx="25" ry="30" fill="black"/>
    <!-- Fingers -->
    <rect x="-5" y="-30" width="8" height="20" fill="black"/>
    <rect x="5" y="-32" width="8" height="22" fill="black"/>
    <rect x="-15" y="-28" width="8" height="18" fill="black"/>
    <!-- Thumb -->
    <ellipse cx="-20" cy="-5" rx="8" ry="12" fill="black" transform="rotate(-30 -20 -5)"/>
  </g>
  
  <!-- Lightning bolt through hand -->
  <path d="M 85 70 L 95 90 L 85 90 L 95 110 L 105 90 L 95 90 L 105 70" fill="yellow" stroke="black" stroke-width="2"/>
  
  <!-- Text -->
  <text x="100" y="180" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">ESD SENSITIVE</text>
</svg>''',
        "filename": "esd_warning_symbol.svg",
        "description": "ESD warning symbol"
    },
    "rc_trigger_clamp": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">RC-Triggered Power Clamp</text>
  
  <!-- RC Network -->
  <rect x="50" y="60" width="40" height="20" fill="none" stroke="black" stroke-width="2"/>
  <text x="70" y="75" text-anchor="middle" font-family="Arial" font-size="12">R</text>
  
  <rect x="50" y="100" width="40" height="40" fill="none" stroke="black" stroke-width="2"/>
  <line x1="50" y1="120" x2="90" y2="120" stroke="black" stroke-width="2"/>
  <text x="70" y="125" text-anchor="middle" font-family="Arial" font-size="12">C</text>
  
  <!-- Trigger -->
  <line x1="90" y1="70" x2="120" y2="70" stroke="black" stroke-width="2"/>
  <line x1="90" y1="120" x2="120" y2="120" stroke="black" stroke-width="2"/>
  <line x1="120" y1="70" x2="120" y2="120" stroke="black" stroke-width="2"/>
  
  <!-- Inverter Chain -->
  <polygon points="130,85 130,105 150,95" fill="none" stroke="black" stroke-width="2"/>
  <circle cx="155" cy="95" r="5" fill="none" stroke="black" stroke-width="2"/>
  <polygon points="170,85 170,105 190,95" fill="none" stroke="black" stroke-width="2"/>
  
  <!-- Big NMOS -->
  <rect x="220" y="80" width="60" height="60" fill="none" stroke="black" stroke-width="2"/>
  <line x1="190" y1="95" x2="220" y2="95" stroke="black" stroke-width="2"/>
  <text x="250" y="115" text-anchor="middle" font-family="Arial" font-size="12">Big NMOS</text>
  
  <!-- Power Rails -->
  <line x1="30" y1="50" x2="350" y2="50" stroke="red" stroke-width="3"/>
  <text x="360" y="55" font-family="Arial" font-size="12" fill="red">VDD</text>
  
  <line x1="30" y1="160" x2="350" y2="160" stroke="blue" stroke-width="3"/>
  <text x="360" y="165" font-family="Arial" font-size="12" fill="blue">VSS</text>
  
  <!-- Connections -->
  <line x1="70" y1="60" x2="70" y2="50" stroke="red" stroke-width="2"/>
  <line x1="70" y1="140" x2="70" y2="160" stroke="blue" stroke-width="2"/>
  <line x1="250" y1="80" x2="250" y2="50" stroke="red" stroke-width="2"/>
  <line x1="250" y1="140" x2="250" y2="160" stroke="blue" stroke-width="2"/>
</svg>''',
        "filename": "rc_trigger_clamp.svg",
        "description": "RC-triggered ESD power clamp circuit"
    },
    
    "cross_domain_protection": {
        "svg_content": '''<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="250" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Cross-Domain ESD Protection</text>
  
  <!-- Domain 1 -->
  <rect x="20" y="50" width="150" height="150" fill="none" stroke="green" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="95" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="green">Domain 1</text>
  <line x1="30" y1="85" x2="160" y2="85" stroke="red" stroke-width="2"/>
  <text x="35" y="82" font-family="Arial" font-size="12" fill="red">VDD1</text>
  <line x1="30" y1="180" x2="160" y2="180" stroke="blue" stroke-width="2"/>
  <text x="35" y="177" font-family="Arial" font-size="12" fill="blue">VSS1</text>
  
  <!-- Domain 2 -->
  <rect x="230" y="50" width="150" height="150" fill="none" stroke="purple" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="305" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="purple">Domain 2</text>
  <line x1="240" y1="85" x2="370" y2="85" stroke="red" stroke-width="2"/>
  <text x="345" y="82" font-family="Arial" font-size="12" fill="red">VDD2</text>
  <line x1="240" y1="180" x2="370" y2="180" stroke="blue" stroke-width="2"/>
  <text x="345" y="177" font-family="Arial" font-size="12" fill="blue">VSS2</text>
  
  <!-- Signal Line -->
  <line x1="100" y1="130" x2="300" y2="130" stroke="black" stroke-width="2"/>
  <text x="200" y="125" text-anchor="middle" font-family="Arial" font-size="12">Signal</text>
  
  <!-- Back-to-back Diodes -->
  <polygon points="180,120 180,140 190,130" fill="black"/>
  <line x1="190" y1="130" x2="190" y2="85" stroke="black" stroke-width="1"/>
  <polygon points="210,140 210,120 220,130" fill="black"/>
  <line x1="210" y1="130" x2="210" y2="85" stroke="black" stroke-width="1"/>
  
  <polygon points="180,130 190,120 190,140" fill="black"/>
  <line x1="180" y1="130" x2="180" y2="180" stroke="black" stroke-width="1"/>
  <polygon points="220,130 210,120 210,140" fill="black"/>
  <line x1="220" y1="130" x2="220" y2="180" stroke="black" stroke-width="1"/>
  
  <!-- Resistor -->
  <rect x="195" y="125" width="10" height="10" fill="none" stroke="black" stroke-width="1"/>
  <text x="200" y="150" text-anchor="middle" font-family="Arial" font-size="10">100Ω</text>
</svg>''',
        "filename": "cross_domain_protection.svg",
        "description": "Cross-domain ESD protection with back-to-back diodes"
    },
    
    "latchup_structure": {
        "svg_content": '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Latchup Structure & Guard Ring</text>
  
  <!-- P-substrate -->
  <rect x="50" y="200" width="300" height="80" fill="#ffcccc" stroke="black"/>
  <text x="200" y="250" text-anchor="middle" font-family="Arial" font-size="14">P-substrate</text>
  
  <!-- N-well -->
  <rect x="100" y="120" width="200" height="80" fill="#ccccff" stroke="black"/>
  <text x="200" y="165" text-anchor="middle" font-family="Arial" font-size="14">N-well</text>
  
  <!-- PMOS -->
  <rect x="120" y="100" width="60" height="20" fill="#ff9999" stroke="black"/>
  <text x="150" y="95" text-anchor="middle" font-family="Arial" font-size="12">PMOS</text>
  
  <!-- NMOS -->
  <rect x="220" y="180" width="60" height="20" fill="#9999ff" stroke="black"/>
  <text x="250" y="175" text-anchor="middle" font-family="Arial" font-size="12">NMOS</text>
  
  <!-- Guard Rings -->
  <rect x="80" y="110" width="240" height="100" fill="none" stroke="green" stroke-width="4"/>
  <text x="75" y="105" text-anchor="end" font-family="Arial" font-size="12" fill="green">N+ Guard Ring</text>
  
  <rect x="60" y="90" width="280" height="140" fill="none" stroke="blue" stroke-width="4"/>
  <text x="55" y="85" text-anchor="end" font-family="Arial" font-size="12" fill="blue">P+ Guard Ring</text>
  
  <!-- Parasitic BJTs -->
  <path d="M 150 120 L 150 140 L 180 140 L 180 160" stroke="red" stroke-width="2" fill="none" marker-end="url(#arrowred)"/>
  <text x="165" y="135" font-family="Arial" font-size="10" fill="red">PNP</text>
  
  <path d="M 250 180 L 250 160 L 220 160 L 220 140" stroke="orange" stroke-width="2" fill="none" marker-end="url(#arroworange)"/>
  <text x="235" y="155" font-family="Arial" font-size="10" fill="orange">NPN</text>
  
  <!-- Well Taps -->
  <circle cx="90" cy="160" r="5" fill="black"/>
  <text x="85" y="155" text-anchor="end" font-family="Arial" font-size="10">P+ tap</text>
  
  <circle cx="310" cy="160" r="5" fill="black"/>
  <text x="315" y="155" text-anchor="start" font-family="Arial" font-size="10">N+ tap</text>
  
  <!-- Arrows -->
  <defs>
    <marker id="arrowred" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="red"/>
    </marker>
    <marker id="arroworange" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="orange"/>
    </marker>
  </defs>
</svg>''',
        "filename": "latchup_structure.svg",
        "description": "Latchup parasitic structure with guard rings"
    },
    
    "cdm_protection": {
        "svg_content": '''<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="250" fill="#f8f9fa"/>
  <text x="200" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">CDM Protection - Corner Stitching</text>
  
  <!-- Metal Bus -->
  <rect x="50" y="60" width="200" height="30" fill="#cccccc" stroke="black" stroke-width="2"/>
  <text x="150" y="80" text-anchor="middle" font-family="Arial" font-size="14">VDD Bus</text>
  
  <rect x="250" y="60" width="30" height="130" fill="#cccccc" stroke="black" stroke-width="2"/>
  
  <!-- Corner without stitching (BAD) -->
  <circle cx="250" cy="90" r="30" fill="none" stroke="red" stroke-width="3" stroke-dasharray="5,5"/>
  <text x="290" y="95" font-family="Arial" font-size="12" fill="red">No Stitching</text>
  <text x="290" y="110" font-family="Arial" font-size="10" fill="red">(CDM Risk)</text>
  
  <!-- Improved corner with stitching -->
  <rect x="50" y="160" width="200" height="30" fill="#999999" stroke="black" stroke-width="2"/>
  <text x="150" y="180" text-anchor="middle" font-family="Arial" font-size="14">VSS Bus</text>
  
  <rect x="250" y="160" width="30" height="30" fill="#999999" stroke="black" stroke-width="2"/>
  <rect x="220" y="190" width="60" height="30" fill="#999999" stroke="black" stroke-width="2"/>
  
  <!-- Vias at corner -->
  <circle cx="255" cy="185" r="2" fill="black"/>
  <circle cx="265" cy="185" r="2" fill="black"/>
  <circle cx="275" cy="185" r="2" fill="black"/>
  <circle cx="255" cy="195" r="2" fill="black"/>
  <circle cx="265" cy="195" r="2" fill="black"/>
  <circle cx="275" cy="195" r="2" fill="black"/>
  
  <circle cx="250" cy="190" r="30" fill="none" stroke="green" stroke-width="3" stroke-dasharray="5,5"/>
  <text x="290" y="195" font-family="Arial" font-size="12" fill="green">With Stitching</text>
  <text x="290" y="210" font-family="Arial" font-size="10" fill="green">(CDM Safe)</text>
  
  <!-- Current flow arrows -->
  <path d="M 100 75 L 200 75" stroke="blue" stroke-width="3" marker-end="url(#arrowblue)"/>
  <text x="150" y="55" text-anchor="middle" font-family="Arial" font-size="10" fill="blue">CDM Current</text>
  
  <defs>
    <marker id="arrowblue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="blue"/>
    </marker>
  </defs>
</svg>''',
        "filename": "cdm_corner_stitching.svg",
        "description": "CDM protection using corner stitching"
    }
}

def download_image(url, filepath):
    """Download image from URL and save to file"""
    try:
        # Add headers to avoid 403 errors from Wikipedia
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {filepath.name}")
            return True
        else:
            print(f"✗ Failed to download {url}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def save_svg(content, filepath):
    """Save SVG content to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created: {filepath.name}")
        return True
    except Exception as e:
        print(f"✗ Error saving {filepath.name}: {e}")
        return False

def main():
    """Create all ESD circuit images"""
    print("Creating ESD circuit images...\n")
    
    success_count = 0
    total_count = len(PLACEHOLDER_CIRCUITS)
    
    # Create all circuit diagrams as SVGs
    print("Creating custom circuit diagrams:")
    for key, info in PLACEHOLDER_CIRCUITS.items():
        filepath = STATIC_DIR / info['filename']
        if save_svg(info['svg_content'], filepath):
            success_count += 1
    
    print(f"\n✅ Successfully downloaded/created {success_count}/{total_count} images")
    print(f"📁 Images saved to: {STATIC_DIR}")
    
    # Create an index HTML file to preview all images
    index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>ESD Circuit Images</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .image-card { border: 1px solid #ddd; padding: 10px; text-align: center; }
        .image-card img { max-width: 100%; height: 200px; object-fit: contain; }
        .image-card h3 { margin: 10px 0 5px 0; font-size: 14px; }
        .image-card p { margin: 0; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <h1>ESD Circuit Images Gallery</h1>
    <div class="gallery">
'''
    
    # Use only placeholder circuits since we're creating all images locally
    for key, info in PLACEHOLDER_CIRCUITS.items():
        index_html += f'''
        <div class="image-card">
            <img src="{info['filename']}" alt="{info['description']}">
            <h3>{key}</h3>
            <p>{info['description']}</p>
        </div>
'''
    
    index_html += '''
    </div>
</body>
</html>'''
    
    with open(STATIC_DIR / "index.html", 'w') as f:
        f.write(index_html)
    
    print(f"\n📄 Preview gallery created: {STATIC_DIR}/index.html")

if __name__ == "__main__":
    main()
