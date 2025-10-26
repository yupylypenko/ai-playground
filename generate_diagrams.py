#!/usr/bin/env python3
"""
Generate PNG diagrams from PlantUML code in DIAGRAMS.md
"""
import re
import subprocess
import os

def extract_diagrams():
    """Extract PlantUML code blocks from DIAGRAMS.md"""
    with open('docs/DIAGRAMS.md', 'r') as f:
        content = f.read()
    
    # Find all PlantUML code blocks
    pattern = r'```plantuml\n(.*?)```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    
    print(f"Found {len(diagrams)} PlantUML diagrams")
    return diagrams

def generate_pngs(diagrams):
    """Generate PNG files from PlantUML code"""
    os.makedirs('docs/images', exist_ok=True)
    
    diagram_names = [
        'system-overview',
        'class-diagram',
        'data-flow-sequence',
        'component-interaction',
        'deployment',
        'mission-state'
    ]
    
    for i, diagram_code in enumerate(diagrams):
        name = diagram_names[i] if i < len(diagram_names) else f'diagram-{i}'
        
        # Write PlantUML code to temporary file
        temp_file = f'{name}.puml'
        with open(temp_file, 'w') as f:
            f.write(diagram_code)
        
        # Generate PNG
        print(f"Generating {name}.png...")
        result = subprocess.run(
            ['java', '-jar', 'plantuml.jar', '-tpng', temp_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Move PNG to docs/images
            subprocess.run(['mv', f'{name}.png', f'docs/images/{name}.png'])
            subprocess.run(['rm', temp_file])
            print(f"✓ Generated docs/images/{name}.png")
        else:
            print(f"✗ Error generating {name}.png")
            print(result.stderr)
    
    print(f"\n✓ Generated {len(diagrams)} PNG files in docs/images/")

if __name__ == '__main__':
    diagrams = extract_diagrams()
    if diagrams:
        generate_pngs(diagrams)
    else:
        print("No diagrams found in DIAGRAMS.md")
