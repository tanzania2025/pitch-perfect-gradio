#!/usr/bin/env python3
"""
Analyze codebase and update requirements.txt
"""
import ast
import os
import subprocess
import re

def find_imports(directory='.'):
    """Find all imports in Python files"""
    imports = set()
    
    for root, dirs, files in os.walk(directory):
        # Skip virtual environments and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
                except:
                    pass
    
    return imports

def get_stdlib_modules():
    """Get list of standard library modules"""
    import sys
    stdlib = set(sys.builtin_module_names)
    
    # Common stdlib modules not in builtin_module_names
    stdlib.update([
        'os', 'sys', 'json', 'time', 'datetime', 'random', 'math',
        'collections', 'itertools', 'functools', 'typing', 'pathlib',
        'subprocess', 'threading', 'multiprocessing', 'asyncio',
        're', 'string', 'textwrap', 'unicodedata', 'base64',
        'hashlib', 'hmac', 'secrets', 'uuid', 'io', 'pickle',
        'csv', 'configparser', 'logging', 'warnings', 'traceback',
        'unittest', 'doctest', 'pdb', 'profile', 'timeit',
        'urllib', 'http', 'email', 'mimetypes', 'socket',
        'ssl', 'select', 'struct', 'platform', 'locale',
        'gettext', 'tempfile', 'shutil', 'zipfile', 'tarfile',
        'sqlite3', 'xml', 'html', 'webbrowser', 'cgi',
        'ast', 'types', 'copy', 'pprint', 'enum', 'numbers',
        'statistics', 'decimal', 'fractions', 'queue', 'heapq',
        'bisect', 'array', 'weakref', 'dataclasses', 'contextvars'
    ])
    
    return stdlib

def map_import_to_package(imports):
    """Map imports to installable package names"""
    # Common import -> package name mappings
    package_map = {
        'cv2': 'opencv-python',
        'sklearn': 'scikit-learn',
        'PIL': 'Pillow',
        'Image': 'Pillow',
        'yaml': 'pyyaml',
        'dotenv': 'python-dotenv',
        'googleapiclient': 'google-api-python-client',
        'google': 'google-cloud-*',  # Needs specific packages
    }
    
    packages = set()
    stdlib = get_stdlib_modules()
    
    for imp in imports:
        if imp in stdlib:
            continue
        
        if imp in package_map:
            packages.add(package_map[imp])
        else:
            packages.add(imp)
    
    # Filter out local modules (assuming they start with lowercase and are short)
    packages = {p for p in packages if not (p.islower() and len(p) < 5 and '.' not in p)}
    
    return packages

def get_installed_version(package):
    """Get installed version of a package"""
    try:
        result = subprocess.run(['pip', 'show', package], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':')[1].strip()
    except:
        pass
    return None

def main():
    print("🔍 Analyzing Python codebase...")
    
    # Find all imports
    imports = find_imports()
    print(f"Found {len(imports)} unique imports")
    
    # Map to packages
    required_packages = map_import_to_package(imports)
    print(f"Identified {len(required_packages)} required packages")
    
    # Read existing requirements.txt
    existing_packages = set()
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg = re.split('[<>=!]', line)[0].strip()
                    existing_packages.add(pkg)
    
    # Find what's missing and what's extra
    missing = required_packages - existing_packages
    extra = existing_packages - required_packages
    
    print(f"\n📋 Analysis Results:")
    print(f"Missing packages: {missing}")
    print(f"Potentially unused: {extra}")
    
    # Create new requirements.txt
    print("\n📝 Creating new requirements.txt...")
    with open('requirements_new.txt', 'w') as f:
        f.write("# Auto-generated requirements.txt\n")
        f.write("# Review and adjust versions as needed\n\n")
        
        for pkg in sorted(required_packages):
            if pkg == 'google-cloud-*':
                f.write("# Add specific google-cloud packages as needed\n")
                continue
            
            version = get_installed_version(pkg)
            if version:
                f.write(f"{pkg}=={version}\n")
            else:
                f.write(f"{pkg}\n")
    
    print("✅ Created requirements_new.txt - review and rename to requirements.txt")
    
    # Save analysis report
    with open('requirements_analysis.txt', 'w') as f:
        f.write("REQUIREMENTS ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Imports found: {', '.join(sorted(imports))}\n\n")
        f.write(f"Required packages: {', '.join(sorted(required_packages))}\n\n")
        f.write(f"Missing from requirements.txt: {', '.join(sorted(missing))}\n\n")
        f.write(f"Potentially unused in requirements.txt: {', '.join(sorted(extra))}\n")
    
    print("📊 Detailed analysis saved to requirements_analysis.txt")

if __name__ == "__main__":
    main()