#!/usr/bin/env python3
"""
Regenerate online URLs for all diagrams
"""
import re
import base64

def read_diagrams():
    with open('docs/DIAGRAMS.md', 'r') as f:
        return f.read()

def generate_url(diagram_code):
    """Generate PlantUML URL"""
    encoded = base64.b64encode(diagram_code.encode('utf-8')).decode('utf-8')
    return f"http://www.plantuml.com/plantuml/png/{encoded}"

def main():
    content = read_diagrams()
    
    # Find all PlantUML code blocks
    pattern = r'```plantuml\n(.*?)\n```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    
    diagram_names = [
        'System Architecture',
        'Class Diagram', 
        'Data Flow Sequence',
        'Component Interaction',
        'Deployment',
        'Mission State Flow'
    ]
    
    print("Updated URLs for ARCHITECTURE.md:\n")
    
    for i, (diagram_code, name) in enumerate(zip(diagrams, diagram_names)):
        url = generate_url(diagram_code)
        print(f"- **[{name}]({url})**")

if __name__ == '__main__':
    main()

