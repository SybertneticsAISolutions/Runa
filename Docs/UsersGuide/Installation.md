# Runa Installation Guide

This guide walks you through the process of installing Runa on various platforms.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+ (or equivalent Linux distribution)
- **Python**: Python 3.8 or newer
- **Disk Space**: 250MB for a basic installation
- **Memory**: 512MB RAM (2GB recommended for development)

### Recommended for AI Features
- **Python**: Python 3.9+
- **Memory**: 8GB+ RAM
- **GPU**: NVIDIA GPU with CUDA support (for accelerated AI operations)
- **Disk Space**: 2GB+ (including AI model storage)

## Installation Methods

### Method 1: Using pip (Recommended)

The simplest way to install Runa is via pip, Python's package manager:

```bash
pip install runa-lang
```

For a specific version:

```bash
pip install runa-lang==1.0.0
```

To install with all optional dependencies (including AI features):

```bash
pip install runa-lang[all]
```

### Method 2: Using the Official Installer

1. Download the appropriate installer for your platform from the [Runa downloads page](https://runa-lang.org/downloads).
2. Run the installer and follow the on-screen instructions.
3. Choose between standard installation or customize components.
4. The installer will set up necessary environment variables automatically.

### Method 3: From Source

For the latest development version or to contribute to Runa:

```bash
# Clone the repository
git clone https://github.com/SybertneticsAISolutions/Runa.git

# Navigate to the directory
cd Runa

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Docker Installation

To use Runa in a containerized environment:

```bash
# Pull the official Docker image
docker pull runaproject/runa:latest

# Run a Runa container
docker run -it runaproject/runa:latest
```

## Platform-Specific Instructions

### Windows

1. Ensure Python 3.8+ is installed and added to PATH.
2. Open Command Prompt or PowerShell as administrator.
3. Run `pip install runa-lang`
4. Add Runa to your PATH environment variable if not done automatically:
   ```
   setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Programs\Runa"
   ```

### macOS

1. Ensure Python 3.8+ is installed (via Homebrew, official installer, or similar).
2. Open Terminal and run:
   ```bash
   pip3 install runa-lang
   ```
3. For the full experience, install recommended tools:
   ```bash
   brew install graphviz  # For knowledge graph visualization
   ```

### Linux (Ubuntu/Debian)

1. Ensure prerequisites are installed:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
2. Install Runa:
   ```bash
   pip3 install runa-lang
   ```
3. For optional dependencies:
   ```bash
   sudo apt install graphviz  # For knowledge graph visualization
   ```

## Verifying Installation

To verify that Runa is installed correctly:

```bash
runa --version
```

You should see output showing the installed version of Runa.

To test with a simple program:

1. Create a file named `hello.runa` with the following content:
   ```
   Let message be "Hello, Runa!"
   Print(message)
   ```

2. Run the program:
   ```bash
   runa run hello.runa
   ```

3. You should see the output: `Hello, Runa!`

## IDE Extensions & Tools

For an enhanced development experience, install these tools:

- **VS Code Extension**: Install the Runa extension from the marketplace or:
  ```bash
  code --install-extension runa-lang.runa-vscode
  ```

- **JetBrains IDEs** (IntelliJ IDEA, PyCharm): Install the "Runa Language Support" plugin from the marketplace.

## Troubleshooting

### Common Installation Issues

#### "Command not found" after installation

Ensure the installation path is in your system's PATH variable. You can add it manually:

- **Windows**: Add to PATH environment variable
- **macOS/Linux**: Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.)
  ```bash
  export PATH="$PATH:$HOME/.local/bin"
  ```

#### Permission denied errors

Use `sudo` (Linux/macOS) or run as administrator (Windows) if you're installing system-wide.

#### Dependency conflicts

Create a virtual environment for a clean installation:

```bash
python -m venv runa-env
source runa-env/bin/activate  # On Windows: runa-env\Scripts\activate
pip install runa-lang
```

#### LLVM/JIT compilation issues

Install LLVM development packages:
- **Ubuntu/Debian**: `sudo apt install llvm-dev`
- **macOS**: `brew install llvm`
- **Windows**: Download from the [LLVM releases page](https://releases.llvm.org/download.html)

### Getting Help

If you encounter issues not covered here:

1. Check the [FAQ](./FAQ.md) for common questions
2. Visit the [Community Forum](https://community.runa-lang.org)
3. Open an issue on the [GitHub issue tracker](https://github.com/SybertneticsAISolutions/Runa/issues)
4. Join the [Discord community](https://discord.gg/runa-lang) for real-time help

## Upgrading Runa

To upgrade to the latest version:

```bash
pip install --upgrade runa-lang
```

To upgrade to a specific version:

```bash
pip install --upgrade runa-lang==1.0.0
```

## Uninstallation

To remove Runa from your system:

```bash
pip uninstall runa-lang
```

For a complete removal, also delete:
- Configuration files: `~/.runa` (Linux/macOS) or `%USERPROFILE%\.runa` (Windows)
- Cached files: `~/.cache/runa` (Linux/macOS) or `%LOCALAPPDATA%\runa` (Windows)

## Next Steps

Now that you've installed Runa, proceed to the [Getting Started](./GettingStarted.md) guide to learn the basics of programming with Runa. 