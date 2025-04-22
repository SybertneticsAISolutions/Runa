#!/usr/bin/env python3
"""
Runa Package Builder

This script builds distribution packages for Runa, including platform-specific installers
and distribution packages.

Usage:
    python package_builder.py [--platform all|windows|macos|linux] [--version X.Y.Z] [--output ./dist]
"""

import os
import sys
import shutil
import subprocess
import argparse
import json
import platform
import datetime
import hashlib
import tempfile
from pathlib import Path

# Constants for package building
PACKAGE_NAME = "runa"
DEFAULT_VERSION = "0.9.0"  # Will be replaced by actual version
CONFIG_FILE = "package_config.json"
README_FILE = "../README.md"
LICENSE_FILE = "../LICENSE"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build Runa distribution packages")
    parser.add_argument("--platform", choices=["all", "windows", "macos", "linux"], 
                        default="all", help="Target platform")
    parser.add_argument("--version", default=None, help="Package version (defaults to version in package_config.json)")
    parser.add_argument("--output", default="./dist", help="Output directory")
    parser.add_argument("--optimize", action="store_true", help="Apply aggressive optimizations")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests before packaging")
    return parser.parse_args()

def load_config():
    """Load configuration from package_config.json."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {CONFIG_FILE} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Configuration file {CONFIG_FILE} is not valid JSON.")
        sys.exit(1)

def get_version(args, config):
    """Determine package version."""
    if args.version:
        return args.version
    elif "version" in config:
        return config["version"]
    else:
        return DEFAULT_VERSION

def run_tests():
    """Run the test suite before packaging."""
    print("Running test suite...")
    try:
        result = subprocess.run(["python", "../tests/run_tests.py"], 
                              check=True, capture_output=True, text=True)
        print("Test suite passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Test suite failed!\n{e.stdout}\n{e.stderr}")
        return False

def create_build_directory(output_dir, version):
    """Create and prepare the build directory."""
    build_dir = os.path.join(output_dir, f"runa-{version}")
    
    # Create directory if it doesn't exist, otherwise clean it
    if os.path.exists(build_dir):
        print(f"Cleaning existing build directory: {build_dir}")
        shutil.rmtree(build_dir)
    
    print(f"Creating build directory: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)
    
    return build_dir

def copy_files(src_dir, build_dir, file_patterns):
    """Copy files matching patterns from source to build directory."""
    for pattern in file_patterns:
        for src_file in Path(src_dir).glob(pattern):
            # Get relative path to maintain directory structure
            rel_path = src_file.relative_to(src_dir)
            dest_file = Path(build_dir) / rel_path
            
            # Create parent directories if they don't exist
            os.makedirs(dest_file.parent, exist_ok=True)
            
            # Copy the file
            print(f"Copying {rel_path}")
            shutil.copy2(src_file, dest_file)

def build_windows_installer(build_dir, version, config):
    """Build Windows installer using NSIS."""
    print("Building Windows installer...")
    
    # Check if NSIS is installed
    nsis_path = shutil.which("makensis")
    if not nsis_path:
        print("Error: NSIS not found. Please install NSIS to build Windows installers.")
        return None
    
    # Create NSIS script
    nsis_script = os.path.join(tempfile.gettempdir(), "runa_installer.nsi")
    with open(nsis_script, "w") as f:
        f.write(f"""
!include "MUI2.nsh"

; General
Name "Runa Programming Language {version}"
OutFile "{build_dir}/../runa-{version}-setup.exe"
InstallDir "$PROGRAMFILES\\Runa"
InstallDirRegKey HKLM "Software\\Runa" "Install_Dir"

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "{build_dir}\\runa.ico"
!define MUI_UNICON "{build_dir}\\runa.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{build_dir}\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Runa Core Files" SecCore
  SetOutPath "$INSTDIR"
  
  ; Files to install
  File /r "{build_dir}\\*.*"
  
  ; Write the installation path into the registry
  WriteRegStr HKLM "SOFTWARE\\Runa" "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Runa" "DisplayName" "Runa Programming Language"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Runa" "UninstallString" '"$INSTDIR\\uninstall.exe"'
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Runa" "NoModify" 1
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Runa" "NoRepair" 1
  WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Add to PATH" SecAddPath
  EnVar::AddValue "PATH" "$INSTDIR\\bin"
SectionEnd

Section "Start Menu Shortcuts" SecShortcuts
  CreateDirectory "$SMPROGRAMS\\Runa"
  CreateShortcut "$SMPROGRAMS\\Runa\\Runa.lnk" "$INSTDIR\\bin\\runa.exe"
  CreateShortcut "$SMPROGRAMS\\Runa\\Documentation.lnk" "$INSTDIR\\docs\\index.html"
  CreateShortcut "$SMPROGRAMS\\Runa\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Runa"
  DeleteRegKey HKLM "SOFTWARE\\Runa"

  ; Remove from PATH
  EnVar::DeleteValue "PATH" "$INSTDIR\\bin"

  ; Remove Start Menu items
  Delete "$SMPROGRAMS\\Runa\\*.*"
  RMDir "$SMPROGRAMS\\Runa"

  ; Remove files and directories
  RMDir /r "$INSTDIR"
SectionEnd
        """)
    
    # Run NSIS
    subprocess.run([nsis_path, nsis_script], check=True)
    
    # Clean up
    os.unlink(nsis_script)
    
    installer_path = os.path.join(build_dir, "..", f"runa-{version}-setup.exe")
    if os.path.exists(installer_path):
        print(f"Windows installer created: {installer_path}")
        return installer_path
    else:
        print("Error: Windows installer creation failed.")
        return None

def build_macos_package(build_dir, version, config):
    """Build macOS package (.pkg)."""
    print("Building macOS package...")
    
    # Check if pkgbuild is available (macOS only)
    pkgbuild_path = shutil.which("pkgbuild")
    if not pkgbuild_path:
        print("Error: pkgbuild not found. This is only available on macOS.")
        return None
    
    # Create temporary directory for package structure
    pkg_root = os.path.join(tempfile.gettempdir(), "runa_pkg_root")
    if os.path.exists(pkg_root):
        shutil.rmtree(pkg_root)
    os.makedirs(os.path.join(pkg_root, "usr/local/runa"), exist_ok=True)
    
    # Copy files to package root
    shutil.copytree(build_dir, os.path.join(pkg_root, "usr/local/runa"), dirs_exist_ok=True)
    
    # Create scripts directory for pre/post-install scripts
    scripts_dir = os.path.join(tempfile.gettempdir(), "runa_pkg_scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Create postinstall script to add symlinks
    with open(os.path.join(scripts_dir, "postinstall"), "w") as f:
        f.write("""#!/bin/bash
mkdir -p /usr/local/bin
ln -sf /usr/local/runa/bin/runa /usr/local/bin/runa
ln -sf /usr/local/runa/bin/runapm /usr/local/bin/runapm
exit 0
""")
    
    # Make script executable
    os.chmod(os.path.join(scripts_dir, "postinstall"), 0o755)
    
    # Build package
    output_pkg = os.path.join(build_dir, "..", f"runa-{version}.pkg")
    subprocess.run([
        "pkgbuild",
        "--root", pkg_root,
        "--identifier", "org.runa-lang.pkg",
        "--version", version,
        "--scripts", scripts_dir,
        "--install-location", "/",
        output_pkg
    ], check=True)
    
    # Clean up
    shutil.rmtree(pkg_root)
    shutil.rmtree(scripts_dir)
    
    if os.path.exists(output_pkg):
        print(f"macOS package created: {output_pkg}")
        return output_pkg
    else:
        print("Error: macOS package creation failed.")
        return None

def build_linux_packages(build_dir, version, config):
    """Build Linux packages (deb, rpm, etc.)."""
    print("Building Linux packages...")
    packages = []
    
    # Check if we have the tools for .deb packaging
    dpkg_path = shutil.which("dpkg-deb")
    if dpkg_path:
        deb_package = build_deb_package(build_dir, version, config)
        if deb_package:
            packages.append(deb_package)
    else:
        print("Warning: dpkg-deb not found. Skipping .deb package creation.")
    
    # Check if we have the tools for .rpm packaging
    rpmbuild_path = shutil.which("rpmbuild")
    if rpmbuild_path:
        rpm_package = build_rpm_package(build_dir, version, config)
        if rpm_package:
            packages.append(rpm_package)
    else:
        print("Warning: rpmbuild not found. Skipping .rpm package creation.")
    
    # Create .tar.gz archive (works on any Linux system)
    tarball = build_tarball(build_dir, version)
    if tarball:
        packages.append(tarball)
    
    return packages

def build_deb_package(build_dir, version, config):
    """Build Debian package (.deb)."""
    print("Building Debian package...")
    
    # Create directory structure for .deb
    deb_root = os.path.join(tempfile.gettempdir(), "runa_deb_root")
    if os.path.exists(deb_root):
        shutil.rmtree(deb_root)
    
    # Create directories
    os.makedirs(os.path.join(deb_root, "usr/local/runa"), exist_ok=True)
    os.makedirs(os.path.join(deb_root, "usr/local/bin"), exist_ok=True)
    os.makedirs(os.path.join(deb_root, "DEBIAN"), exist_ok=True)
    
    # Copy files
    shutil.copytree(build_dir, os.path.join(deb_root, "usr/local/runa"), dirs_exist_ok=True)
    
    # Create symlinks
    os.symlink("/usr/local/runa/bin/runa", os.path.join(deb_root, "usr/local/bin/runa"))
    os.symlink("/usr/local/runa/bin/runapm", os.path.join(deb_root, "usr/local/bin/runapm"))
    
    # Create control file
    with open(os.path.join(deb_root, "DEBIAN/control"), "w") as f:
        f.write(f"""Package: runa
Version: {version}
Section: devel
Priority: optional
Architecture: {platform.machine()}
Depends: python3 (>= 3.8)
Maintainer: Runa Team <team@runa-lang.org>
Description: Runa Programming Language
 Runa is a modern programming language designed for AI systems integration.
""")
    
    # Build .deb package
    output_deb = os.path.join(build_dir, "..", f"runa_{version}_{platform.machine()}.deb")
    subprocess.run(["dpkg-deb", "--build", deb_root, output_deb], check=True)
    
    # Clean up
    shutil.rmtree(deb_root)
    
    if os.path.exists(output_deb):
        print(f"Debian package created: {output_deb}")
        return output_deb
    else:
        print("Error: Debian package creation failed.")
        return None

def build_rpm_package(build_dir, version, config):
    """Build RPM package (.rpm)."""
    print("Building RPM package...")
    
    # Create RPM build directories
    rpm_build_dir = os.path.join(tempfile.gettempdir(), "runa_rpm_build")
    for subdir in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        os.makedirs(os.path.join(rpm_build_dir, subdir), exist_ok=True)
    
    # Create tarball for source
    tarball_name = f"runa-{version}.tar.gz"
    tarball_path = os.path.join(rpm_build_dir, "SOURCES", tarball_name)
    
    # Create tarball
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_runa_dir = os.path.join(temp_dir, f"runa-{version}")
        shutil.copytree(build_dir, temp_runa_dir)
        
        # Create the tarball
        subprocess.run(["tar", "-czf", tarball_path, "-C", temp_dir, f"runa-{version}"], check=True)
    
    # Create spec file
    spec_path = os.path.join(rpm_build_dir, "SPECS", "runa.spec")
    with open(spec_path, "w") as f:
        f.write(f"""
%define name runa
%define version {version}
%define release 1

Name: %{{name}}
Version: %{{version}}
Release: %{{release}}
Summary: Runa Programming Language
License: MIT
URL: https://runa-lang.org
Source0: %{{name}}-%{{version}}.tar.gz
BuildArch: {platform.machine()}
Requires: python3 >= 3.8

%description
Runa is a modern programming language designed for AI systems integration.

%prep
%setup -q

%install
mkdir -p %{{buildroot}}/usr/local/runa
cp -r * %{{buildroot}}/usr/local/runa/
mkdir -p %{{buildroot}}/usr/local/bin
ln -sf /usr/local/runa/bin/runa %{{buildroot}}/usr/local/bin/runa
ln -sf /usr/local/runa/bin/runapm %{{buildroot}}/usr/local/bin/runapm

%files
/usr/local/runa
/usr/local/bin/runa
/usr/local/bin/runapm

%changelog
* {datetime.datetime.now().strftime('%a %b %d %Y')} Runa Team <team@runa-lang.org> - {version}-1
- Initial package release
""")
    
    # Build RPM
    subprocess.run([
        "rpmbuild", "-bb",
        "--define", f"_topdir {rpm_build_dir}",
        spec_path
    ], check=True)
    
    # Find the built RPM
    rpm_path = None
    for root, dirs, files in os.walk(os.path.join(rpm_build_dir, "RPMS")):
        for file in files:
            if file.startswith(f"runa-{version}") and file.endswith(".rpm"):
                rpm_path = os.path.join(root, file)
                break
    
    if rpm_path:
        output_rpm = os.path.join(build_dir, "..", os.path.basename(rpm_path))
        shutil.copy2(rpm_path, output_rpm)
        print(f"RPM package created: {output_rpm}")
        
        # Clean up
        shutil.rmtree(rpm_build_dir)
        
        return output_rpm
    else:
        print("Error: RPM package creation failed.")
        return None

def build_tarball(build_dir, version):
    """Build a .tar.gz archive."""
    print("Building tarball...")
    
    tarball_path = os.path.join(os.path.dirname(build_dir), f"runa-{version}.tar.gz")
    
    # Get directory name from build_dir
    build_dir_name = os.path.basename(build_dir)
    parent_dir = os.path.dirname(build_dir)
    
    # Create tarball
    subprocess.run(["tar", "-czf", tarball_path, "-C", parent_dir, build_dir_name], check=True)
    
    if os.path.exists(tarball_path):
        print(f"Tarball created: {tarball_path}")
        return tarball_path
    else:
        print("Error: Tarball creation failed.")
        return None

def generate_checksums(package_files):
    """Generate SHA-256 checksums for all package files."""
    if not package_files:
        return None
    
    checksum_file = os.path.join(os.path.dirname(package_files[0]), "SHA256SUMS")
    
    with open(checksum_file, "w") as f:
        for package_file in package_files:
            if os.path.exists(package_file):
                # Calculate SHA-256 hash
                with open(package_file, "rb") as pf:
                    file_hash = hashlib.sha256(pf.read()).hexdigest()
                
                # Write hash and filename to checksum file
                f.write(f"{file_hash}  {os.path.basename(package_file)}\n")
    
    print(f"Checksums written to: {checksum_file}")
    return checksum_file

def optimize_binaries(build_dir, config):
    """Apply optimization techniques to binaries."""
    print("Applying optimizations to binaries...")
    
    # Find all binary files
    binaries = []
    for root, dirs, files in os.walk(os.path.join(build_dir, "bin")):
        for file in files:
            if not file.endswith((".py", ".txt", ".md")):
                binaries.append(os.path.join(root, file))
    
    # Apply optimizations based on platform
    if platform.system() == "Linux":
        for binary in binaries:
            try:
                # Strip debug symbols
                subprocess.run(["strip", "-s", binary], check=True)
                print(f"Optimized: {os.path.basename(binary)}")
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to optimize {os.path.basename(binary)}")
    
    elif platform.system() == "Darwin":  # macOS
        for binary in binaries:
            try:
                # Strip debug symbols
                subprocess.run(["strip", binary], check=True)
                print(f"Optimized: {os.path.basename(binary)}")
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to optimize {os.path.basename(binary)}")
    
    elif platform.system() == "Windows":
        # Windows binaries optimization would go here
        # This often requires specific tools like UPX
        pass
    
    return True

def main():
    # Parse arguments
    args = parse_args()
    
    # Load configuration
    config = load_config()
    
    # Get version
    version = get_version(args, config)
    print(f"Building Runa version {version}")
    
    # Run tests if not skipped
    if not args.skip_tests:
        if not run_tests():
            if input("Tests failed. Continue with package building? (y/n): ").lower() != 'y':
                sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Create build directory
    build_dir = create_build_directory(args.output, version)
    
    # Copy source files to build directory
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    copy_files(src_dir, build_dir, config.get("files_to_include", ["**/*.py", "**/*.runa"]))
    
    # Copy documentation
    copy_files(src_dir, build_dir, config.get("docs_to_include", ["docs/**/*"]))
    
    # Copy license and readme
    shutil.copy2(os.path.join(src_dir, "LICENSE"), os.path.join(build_dir, "LICENSE"))
    shutil.copy2(os.path.join(src_dir, "README.md"), os.path.join(build_dir, "README.md"))
    
    # Create bin directory
    bin_dir = os.path.join(build_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    
    # Build the executables
    print("Building executables...")
    if not os.path.exists(os.path.join(src_dir, "build_bin.py")):
        print("Error: build_bin.py script not found. Cannot build executables.")
        sys.exit(1)
    
    subprocess.run([sys.executable, os.path.join(src_dir, "build_bin.py"), 
                  "--output", bin_dir, "--version", version], check=True)
    
    # Apply optimizations if requested
    if args.optimize:
        optimize_binaries(build_dir, config)
    
    # Build platform-specific packages
    packages = []
    
    if args.platform in ["all", "windows"] and platform.system() == "Windows":
        windows_package = build_windows_installer(build_dir, version, config)
        if windows_package:
            packages.append(windows_package)
    
    if args.platform in ["all", "macos"] and platform.system() == "Darwin":
        macos_package = build_macos_package(build_dir, version, config)
        if macos_package:
            packages.append(macos_package)
    
    if args.platform in ["all", "linux"] and platform.system() == "Linux":
        linux_packages = build_linux_packages(build_dir, version, config)
        if linux_packages:
            packages.extend(linux_packages)
    
    # Generate checksums for all packages
    if packages:
        checksum_file = generate_checksums(packages)
    
    print("\nPackage building completed!")
    print(f"Packages were saved to: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main() 