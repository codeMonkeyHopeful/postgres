# This script can be run to interactively setup the DB contianer through the terminal
import subprocess
import os
import sys
from pathlib import Path





def setup_venv(venv_name="venv"):
    """Create virtual environment if it doesn't exist"""
    venv_path = Path(venv_name)

    if venv_path.exists() and (venv_path / 'pyvenv.cfg').exists():
        print(f"✅ Virtual environment '{venv_name}' already exists")
        return True, venv_path

    print(f"🔧 Creating virtual environment '{venv_name}'...")

    try:
        result = subprocess.run([sys.executable, '-m', 'venv', venv_name],
                               capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Virtual environment '{venv_name}' created successfully!")
            return True, venv_path
        else:
            print(f"❌ Failed to create venv: {result.stderr}")
            return False, None

    except Exception as e:
        print(f"❌ Error creating venv: {e}")
        return False, None


def activate_venv(venv_path):
    """Activate virtual environment by modifying Python environment for current OS"""
    venv_path = Path(venv_path)

    # Check if venv exists and is valid
    if not venv_path.exists() or not (venv_path / 'pyvenv.cfg').exists():
        print(f"❌ Virtual environment not found or invalid: {venv_path}")
        return False

    # Get OS-specific paths
    if os.name == 'nt':  # Windows
        python_exe = venv_path / 'Scripts' / 'python.exe'
        scripts_dir = venv_path / 'Scripts'
        site_packages = venv_path / 'Lib' / 'site-packages'
    else:  # Unix/Linux/Mac
        python_exe = venv_path / 'bin' / 'python'
        scripts_dir = venv_path / 'bin'
        # Get Python version for site-packages path
        version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = venv_path / 'lib' / version / 'site-packages'

    # Verify critical files exist
    if not python_exe.exists():
        print(f"❌ Python executable not found in venv: {python_exe}")
        return False

    if not site_packages.exists():
        print(f"❌ Site-packages directory not found: {site_packages}")
        return False

    # Modify Python path to prioritize venv packages
    site_packages_str = str(site_packages)
    if site_packages_str not in sys.path:
        sys.path.insert(0, site_packages_str)

    # Update environment variables
    os.environ['VIRTUAL_ENV'] = str(venv_path)

    # Update PATH to prioritize venv executables
    current_path = os.environ.get('PATH', '')
    scripts_dir_str = str(scripts_dir)
    if scripts_dir_str not in current_path:
        os.environ['PATH'] = f"{scripts_dir_str}{os.pathsep}{current_path}"

    # Update sys.executable to point to venv python
    sys.executable = str(python_exe)

    # Remove PYTHONHOME if set (can interfere with venv)
    if 'PYTHONHOME' in os.environ:
        del os.environ['PYTHONHOME']

    print(f"✅ Virtual environment activated: {venv_path}")
    return True



def install_dependencies(venv_path):
    """Install required dependencies in created venv"""
    if os.name == 'nt':  # Windows
        pip_exe = venv_path / 'Scripts' / 'pip.exe'
    else:  # Unix/Linux/Mac
        pip_exe = venv_path / 'bin' / 'pip'

    # List installs  we need here
    dependencies = ['simple_chalk']

    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        result = subprocess.run([str(pip_exe), 'install', dep],
                               capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {dep} installed successfully!")
        else:
            print(f"❌ Failed to install {dep}: {result.stderr}")
            return False

    return True

def import_chalk():
    try:
        from simple_chalk import chalk
        return chalk
    except ImportError as e:
        print(f"❌ Failed to import simple_chalk: {e}")
        print("💡 Make sure the virtual environment is activated and simple_chalk is installed")
        return None

def main():

    # Inputs needed
# # PostgreSQL
# POSTGRES_USER=
# POSTGRES_PASSWORD=
# POSTGRES_DB=
# POSTGRES_CONTAINER_NAME=
# POSTGRES_PORT=

# # pgAdmin
# PGADMIN_DEFAULT_EMAIL=
# PGADMIN_DEFAULT_PASSWORD=
# PGADMIN_PORT=



  print("""Welcome to the Postgres DB interactive setup.
          Based on the inputs provided, this will create a .env file for your DB instance, start the Docker container, and display the running containers for reference.
          Please note you will need Python, Docker, and Docker Compose installed before running this file.
          For each input the default will be listed in parenthases, hitting enter without providing an input will use those inputs.
          """)

  venv_name = input(f"Please enter existing venv you would like to use or if none exists the name you wish to give it (venv): ").strip() or "venv"

  # Setup virtual environment
  successful, venv_path = setup_venv(venv_name)

  if not successful:
      print("❌ Failed to setup virtual environment, please try running again or manually create.")
      sys.exit(1)

  activated = activate_venv(venv_path)

  if not activated:
      print("❌ Failed to activate virtual environment, please try running again or manually activate.")
      sys.exit(1)

  # Install dependencies
  if not install_dependencies(venv_path):
      print("❌ Failed to install dependencies")
      return

  print("✅ Python environment setup complete!")

  chalk=import_chalk()

    # Setup chalk standardards
  success=chalk.green.bold
  fail=chalk.red.bold
  info=chalk.blue.bold
  default=chalk.magenta.bold

  # Continue with your PostgreSQL setup...
  # create_env_file()
  # setup_docker()

if __name__ == "__main__":
    main()
