#!/usr/bin/env python3
"""
Script to compare currently installed packages with requirements.txt
"""
import subprocess
import json

def get_installed_packages():
    """Get dictionary of installed packages and their versions"""
    result = subprocess.run(['pip', 'list', '--format=json'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error getting installed packages")
        return {}
    
    packages = json.loads(result.stdout)
    installed = {}
    for pkg in packages:
        installed[pkg['name'].lower()] = pkg['version']
    return installed

def parse_requirements_file(filename='requirements.txt'):
    """Parse requirements.txt and return dictionary of packages and version specs"""
    requirements = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse package name and version spec
                if '>=' in line:
                    name, ver_spec = line.split('>=')
                    requirements[name.strip().lower()] = ('>=', ver_spec.strip())
                elif '==' in line:
                    name, ver_spec = line.split('==')
                    requirements[name.strip().lower()] = ('==', ver_spec.strip())
                elif '>' in line:
                    name, ver_spec = line.split('>')
                    requirements[name.strip().lower()] = ('>', ver_spec.strip())
                elif '<' in line:
                    name, ver_spec = line.split('<')
                    requirements[name.strip().lower()] = ('<', ver_spec.strip())
                else:
                    # No version specified
                    requirements[line.strip().lower()] = (None, None)
    except FileNotFoundError:
        print(f"❌ {filename} not found")
        return {}
    
    return requirements

def check_version_compatibility(installed_ver, operator, required_ver):
    """Check if installed version meets requirement"""
    if operator is None:
        return True
    
    # Simple version comparison without packaging module
    def parse_version(v):
        return tuple(map(int, v.split('.')))
    
    try:
        installed = parse_version(installed_ver)
        required = parse_version(required_ver)
        
        if operator == '>=':
            return installed >= required
        elif operator == '==':
            return installed == required
        elif operator == '>':
            return installed > required
        elif operator == '<':
            return installed < required
    except:
        # If version parsing fails, do string comparison
        if operator == '==':
            return installed_ver == required_ver
        # For other operators, assume compatible if parsing fails
        return True
    
    return False

def main():
    print("📦 Package Comparison Tool")
    print("=" * 60)
    
    # Get installed packages
    installed = get_installed_packages()
    print(f"\n✓ Found {len(installed)} installed packages")
    
    # Parse requirements.txt
    requirements = parse_requirements_file()
    print(f"✓ Found {len(requirements)} packages in requirements.txt")
    
    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    
    # Check required packages
    print("\n🔍 REQUIRED PACKAGES STATUS:")
    print("-" * 40)
    missing = []
    version_mismatch = []
    satisfied = []
    
    for pkg, (op, req_ver) in requirements.items():
        if pkg not in installed:
            missing.append(pkg)
            print(f"❌ {pkg}: NOT INSTALLED (required: {op}{req_ver if req_ver else 'any'})")
        else:
            if op and req_ver:
                if check_version_compatibility(installed[pkg], op, req_ver):
                    satisfied.append(pkg)
                    print(f"✅ {pkg}: {installed[pkg]} (required: {op}{req_ver})")
                else:
                    version_mismatch.append(pkg)
                    print(f"⚠️  {pkg}: {installed[pkg]} (required: {op}{req_ver}) - VERSION MISMATCH")
            else:
                satisfied.append(pkg)
                print(f"✅ {pkg}: {installed[pkg]} (required: any version)")
    
    # Find extra packages
    print("\n📦 EXTRA INSTALLED PACKAGES (not in requirements.txt):")
    print("-" * 40)
    required_names = set(requirements.keys())
    extra_packages = []
    
    for pkg, ver in installed.items():
        if pkg not in required_names:
            extra_packages.append(pkg)
            print(f"📌 {pkg}: {ver}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Satisfied requirements: {len(satisfied)}")
    print(f"❌ Missing packages: {len(missing)}")
    print(f"⚠️  Version mismatches: {len(version_mismatch)}")
    print(f"📦 Extra packages: {len(extra_packages)}")
    
    # Recommendations
    if missing or version_mismatch:
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        if missing:
            print(f"• Install missing packages: pip install {' '.join(missing)}")
        if version_mismatch:
            print("• Fix version mismatches: pip install -r requirements.txt --upgrade")
        print("• Or simply run: pip install -r requirements.txt")
    else:
        print("\n✅ All requirements are satisfied!")
    
    # Generate pip freeze comparison
    print("\n📄 GENERATING DETAILED COMPARISON FILE...")
    with open('package_comparison.txt', 'w') as f:
        f.write("PACKAGE COMPARISON REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("CURRENTLY INSTALLED (pip freeze format):\n")
        f.write("-" * 40 + "\n")
        result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
        f.write(result.stdout)
        
        f.write("\n\nREQUIREMENTS.TXT CONTENTS:\n")
        f.write("-" * 40 + "\n")
        with open('requirements.txt', 'r') as req:
            f.write(req.read())
        
        f.write("\n\nDETAILED ANALYSIS:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Missing packages: {', '.join(missing) if missing else 'None'}\n")
        f.write(f"Version mismatches: {', '.join(version_mismatch) if version_mismatch else 'None'}\n")
        f.write(f"Extra packages: {', '.join(extra_packages[:10])}{'...' if len(extra_packages) > 10 else ''}\n")
    
    print("✓ Detailed comparison saved to: package_comparison.txt")

if __name__ == "__main__":
    main()