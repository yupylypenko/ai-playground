#!/usr/bin/env python3
"""
Generate online PlantUML renderer URLs
"""
import urllib.parse
import re

def extract_diagrams():
    """Extract PlantUML code blocks from DIAGRAMS.md"""
    with open('docs/DIAGRAMS.md', 'r') as f:
        content = f.read()
    
    # Find all PlantUML code blocks
    pattern = r'```plantuml\n(.*?)```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    
    return diagrams

def encode_for_url(diagram_code):
    """Encode PlantUML code for URL"""
    # PlantUML online server uses a special encoding
    compressed = diagram_code.encode('utf-8')
    # Base64 encode
    import base64
    encoded = base64.b64encode(compressed).decode('utf-8')
    return encoded

def generate_url(diagram_code):
    """Generate online PlantUML URL"""
    encoded = encode_for_url(diagram_code)
    url = f"http://www.plantuml.com/plantuml/png/{encoded}"
    return url

if __name__ == '__main__':
    diagrams = extract_diagrams()
    
    diagram_names = [
        'System Architecture',
        'Class Diagram',
        'Data Flow Sequence',
        'Component Interaction',
        'Deployment',
        'Mission State Flow'
    ]
    
    print("# Online Diagram URLs\n")
    print("You can view these diagrams online by clicking the links below:\n")
    
    for i, (diagram_code, name) in enumerate(zip(diagrams, diagram_names)):
        url = generate_url(diagram_code)
        print(f"### {name}")
        print(f"[View {name} Online]({url})\n")
        print("Or open in browser:")
        print(f"{url}\n")

