#!/usr/bin/env python3
"""
TORQ APK Builder Script
Automated script to build Android APK
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description=""):
    """Run shell command with error handling"""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check pip
    if not run_command("pip --version", "Checking pip"):
        return False
    
    # Check if buildozer is installed
    try:
        import buildozer
        print("✅ Buildozer is installed")
    except ImportError:
        print("⚠️ Buildozer not found, will install...")
        if not run_command("pip install buildozer cython", "Installing buildozer"):
            return False
    
    return True

def setup_environment():
    """Setup build environment"""
    print("\n🛠️ Setting up build environment...")
    
    # Install mobile requirements
    if os.path.exists("requirements_mobile.txt"):
        if not run_command("pip install -r requirements_mobile.txt", "Installing mobile dependencies"):
            return False
    
    # Initialize buildozer if needed
    if not os.path.exists("buildozer.spec"):
        print("⚠️ buildozer.spec not found, initializing...")
        if not run_command("buildozer init", "Initializing buildozer"):
            return False
    
    return True

def build_apk(build_type="debug"):
    """Build the APK"""
    print(f"\n🏗️ Building {build_type} APK...")
    
    # Clean previous builds
    run_command("buildozer android clean", "Cleaning previous builds")
    
    # Build APK
    cmd = f"buildozer android {build_type}"
    if not run_command(cmd, f"Building {build_type} APK"):
        return False
    
    # Check if APK was created
    bin_dir = "bin"
    if os.path.exists(bin_dir):
        apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
        if apk_files:
            print(f"\n🎉 APK built successfully!")
            for apk in apk_files:
                apk_path = os.path.join(bin_dir, apk)
                size_mb = os.path.getsize(apk_path) / (1024 * 1024)
                print(f"📱 {apk} ({size_mb:.1f} MB)")
            return True
    
    print("❌ APK file not found in bin/ directory")
    return False

def install_apk():
    """Install APK on connected Android device"""
    print("\n📱 Installing APK on device...")
    
    # Check if adb is available
    if not run_command("adb version", "Checking ADB"):
        print("⚠️ ADB not found. Please install Android SDK or connect device manually.")
        return False
    
    # Check connected devices
    if not run_command("adb devices", "Checking connected devices"):
        return False
    
    # Find APK file
    bin_dir = "bin"
    if os.path.exists(bin_dir):
        apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
        if apk_files:
            apk_path = os.path.join(bin_dir, apk_files[0])
            return run_command(f"adb install -r {apk_path}", "Installing APK")
    
    print("❌ No APK file found to install")
    return False

def main():
    """Main build process"""
    print("🤖 TORQ Android APK Builder")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install required tools.")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        sys.exit(1)
    
    # Get build type from user
    build_type = input("\nBuild type (debug/release) [debug]: ").strip().lower()
    if build_type not in ["debug", "release"]:
        build_type = "debug"
    
    # Build APK
    if not build_apk(build_type):
        print("\n❌ APK build failed.")
        sys.exit(1)
    
    # Ask if user wants to install
    install_choice = input("\nInstall APK on connected device? (y/n) [n]: ").strip().lower()
    if install_choice == 'y':
        install_apk()
    
    print("\n🎉 Build process completed!")
    print("\nNext steps:")
    print("1. Find your APK in the 'bin/' directory")
    print("2. Transfer to Android device and install")
    print("3. Enable 'Install from Unknown Sources' if needed")
    print("4. Launch TORQ from app drawer")

if __name__ == "__main__":
    main()