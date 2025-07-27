# This script can be run to interactively setup the DB contianer through the terminal
import subprocess
import os
import sys
from pathlib import Path
from simple_chalk import green, red, magenta, blue




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

  # Setup chalk standardards
  success=green.bold
  fail=red.bold
  info=blue.bold
  default=magenta.bold

  print(info("""Welcome to the Postgres DB interactive setup.
          Based on the inputs provided, this will create a .env file for your DB instance, start the Docker container, and display the running containers for reference.
          Please note you will need Python, Docker, and Docker Compose installed before running this file.
          For each input the default will be listed in parenthases, hitting enter without providing an input will use those inputs.
          """))

  venv_name = input(f"Please enter existing venv you would like to use or if none exists the name you wish to give it {default("venv")}: ").strip() or "venv"

  # Setup virtual environment
  successful, venv_path = setup_venv(venv_name)

  if not successful:
      print("❌ Failed to setup virtual environment, please try running again or manually create.")
      sys.exit(1)

  # Install dependencies
  if not install_dependencies(venv_path):
      print("❌ Failed to install dependencies")
      return

  print("✅ Python environment setup complete!")

  # Continue with your PostgreSQL setup...
  # create_env_file()
  # setup_docker()

if __name__ == "__main__":
    main()
