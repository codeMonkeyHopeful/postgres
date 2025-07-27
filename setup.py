# Fixed version of your virtual environment functions

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


def get_venv_paths(venv_path):
    """Get OS-specific paths for the virtual environment"""
    venv_path = Path(venv_path)

    if os.name == 'nt':  # Windows
        python_exe = venv_path / 'Scripts' / 'python.exe'
        pip_exe = venv_path / 'Scripts' / 'pip.exe'
        scripts_dir = venv_path / 'Scripts'
    else:  # Unix/Linux/Mac
        python_exe = venv_path / 'bin' / 'python'
        pip_exe = venv_path / 'bin' / 'pip'
        scripts_dir = venv_path / 'bin'

    return python_exe, pip_exe, scripts_dir


def create_venv_env(venv_path):
    """Create environment dict for running commands in venv context"""
    venv_path = Path(venv_path)
    python_exe, pip_exe, scripts_dir = get_venv_paths(venv_path)

    # Create a copy of the current environment
    env = os.environ.copy()

    # Update environment for venv
    env['VIRTUAL_ENV'] = str(venv_path)
    env['PATH'] = str(scripts_dir) + os.pathsep + env.get('PATH', '')

    # Remove PYTHONHOME if it exists (can interfere with venv)
    env.pop('PYTHONHOME', None)

    return env, python_exe, pip_exe


def install_dependencies(venv_path):
    """Install required dependencies in the virtual environment"""
    env, python_exe, pip_exe = create_venv_env(venv_path)

    # Verify pip executable exists
    if not pip_exe.exists():
        print(f"❌ pip executable not found: {pip_exe}")
        return False

    # List of dependencies to install
    dependencies = ['simple_chalk', 'python-dotenv']

    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        result = subprocess.run([str(pip_exe), 'install', dep],
                               capture_output=True, text=True, env=env)

        if result.returncode == 0:
            print(f"✅ {dep} installed successfully!")
        else:
            print(f"❌ Failed to install {dep}: {result.stderr}")
            return False

    return True


def run_python_script(script_path, venv_path):
    """Run a Python script using the venv's Python"""
    env, python_exe, _ = create_venv_env(venv_path)

    if not python_exe.exists():
        print(f"❌ Python executable not found: {python_exe}")
        return False, "", "Python executable not found"

    # Run the script with the venv environment
    result = subprocess.run([str(python_exe), str(script_path)],
                           capture_output=True, text=True, env=env)

    return result.returncode == 0, result.stdout, result.stderr


def import_chalk_from_venv(venv_path):
    """Import simple_chalk by running it through the venv's Python"""
    env, python_exe, _ = create_venv_env(venv_path)

    # Test if simple_chalk is available in the venv
    test_import = """
try:
    from simple_chalk import chalk
    print("SUCCESS: simple_chalk imported")
except ImportError as e:
    print(f"ERROR: {e}")
    exit(1)
"""

    result = subprocess.run([str(python_exe), '-c', test_import],
                           capture_output=True, text=True, env=env)

    if result.returncode == 0:
        # If we can import it in the venv, we need to add the venv to sys.path
        # to import it in the current process
        venv_path = Path(venv_path)
        if os.name == 'nt':
            site_packages = venv_path / 'Lib' / 'site-packages'
        else:
            version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = venv_path / 'lib' / version / 'site-packages'

        if site_packages.exists() and str(site_packages) not in sys.path:
            sys.path.insert(0, str(site_packages))

        try:
            from simple_chalk import chalk
            return chalk
        except ImportError as e:
            print(f"❌ Failed to import simple_chalk: {e}")
            return None
    else:
        print(f"❌ simple_chalk not available in venv: {result.stdout}{result.stderr}")
        return None

def import_dotenv_from_venv(venv_path):
    """Import simple_chalk by running it through the venv's Python"""
    env, python_exe, _ = create_venv_env(venv_path)

    # Test if simple_chalk is available in the venv
    test_import = """
try:
    from dotenv import load_dotenv
    print("SUCCESS: load_dotenv imported")
except ImportError as e:
    print(f"ERROR: {e}")
    exit(1)
"""

    result = subprocess.run([str(python_exe), '-c', test_import],
                           capture_output=True, text=True, env=env)

    if result.returncode == 0:
        # If we can import it in the venv, we need to add the venv to sys.path
        # to import it in the current process
        venv_path = Path(venv_path)
        if os.name == 'nt':
            site_packages = venv_path / 'Lib' / 'site-packages'
        else:
            version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = venv_path / 'lib' / version / 'site-packages'

        if site_packages.exists() and str(site_packages) not in sys.path:
            sys.path.insert(0, str(site_packages))

        try:
            from dotenv import load_dotenv
            return load_dotenv
        except ImportError as e:
            print(f"❌ Failed to import load_dotenv: {e}")
            return None
    else:
        print(f"❌ load_dotenv not available in venv: {result.stdout}{result.stderr}")
        return None


def run_command_in_venv(command, venv_path):
    """Run any command in the virtual environment context"""
    env, python_exe, _ = create_venv_env(venv_path)

    # If command starts with 'python', replace with venv python
    if isinstance(command, list) and command[0] == 'python':
        command[0] = str(python_exe)
    elif isinstance(command, str) and command.startswith('python '):
        command = command.replace('python ', f'"{python_exe}" ', 1)

    result = subprocess.run(command, capture_output=True, text=True, env=env, shell=isinstance(command, str))
    return result


def prep_env_file_inputs(info, default):
    POSTGRES_USER=input(f"Please enter the username you would like to use when connecting to the DB {default("admin")} : ").strip() or "admin"
    POSTGRES_PASSWORD=input(f"Please enter the password for user {info(POSTGRES_USER)} when connecting to the DB {default("password123")} : ").strip() or "password123"
    POSTGRES_DB=input(f"What would you like to name your DB? {default("api_db")} : ").strip() or "api_db"
    POSTGRES_CONTAINER_NAME=input(f"What do you want to name your Docker container?  This will also be used in your DB. {default("postgres_container")} : ").strip() or "postgres_container"
    POSTGRES_PORT=input(f"What port would you like to use for your DB? {default("5432")} : ").strip() or "5432"
    PGADMIN_DEFAULT_EMAIL=input(f"What email would you like to use for pgAdmin? {default("example@email.com")} : ").strip() or "example@email.com"
    PGADMIN_DEFAULT_PASSWORD=input(f"What password would you like to use for pgAdmin? {default("admin123")} : ").strip() or "admin123"
    PGADMIN_PORT=input(f"What port would you like to use for pgAdmin? {default("8080")} : ").strip() or "8080"

    return f"""# PostgreSQL
POSTGRES_USER={POSTGRES_USER}
POSTGRES_PASSWORD={POSTGRES_PASSWORD}
POSTGRES_DB={POSTGRES_DB}
POSTGRES_CONTAINER_NAME={POSTGRES_CONTAINER_NAME}
POSTGRES_PORT={POSTGRES_PORT}

# pgAdmin
PGADMIN_DEFAULT_EMAIL={PGADMIN_DEFAULT_EMAIL}
PGADMIN_DEFAULT_PASSWORD={PGADMIN_DEFAULT_PASSWORD}
PGADMIN_PORT={PGADMIN_PORT}
"""



def create_env_file(env_content, success, alert, default, filename=".env", directory=None ):
    """Check if .env file exists in specified directory"""
    if directory is None:
        directory = Path.cwd()  # Current working directory
    else:
        directory = Path(directory)

    env_file = directory / filename
    if env_file.exists():
        print(alert(f"❗ .env file already exists at {env_file}, skipping creation."))

        overwrite = input(alert(f"Do you want to overwrite the existing .env file (y/n)? {default('n')}")).strip().lower() or 'n'

        if overwrite in ['y', 'yes', 'yeah', 'yep', 'true', '1']:
            print(alert("Will overwrite"))
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(success(f"✅ .env file created at {env_file}"))
            return True, env_file

        else:
            print(success("Will not overwrite, proceeding without creating .env file."))
            return False, env_file
    else:
        print(success(f"✅ .env file does not exist, creating at {env_file}"))
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(success(f"✅ .env file created at {env_file}"))
        return True, env_file


def load_env_vars(env_file='.env'):
    """Load environment variables from .env file"""
    try:
        load_dotenv = import_dotenv_from_venv('venv')

        if not Path(env_file).exists():
            print(f"❌ .env file not found: {env_file}")
            return None

        # Load the .env file
        load_dotenv(env_file)

        # Extract the variables we need
        env_vars = {
            'POSTGRES_USER': os.getenv('POSTGRES_USER', 'admin'),
            'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password123'),
            'POSTGRES_DB': os.getenv('POSTGRES_DB', 'api_db'),
            'POSTGRES_CONTAINER_NAME': os.getenv('POSTGRES_CONTAINER_NAME', 'postgres_container'),
            'POSTGRES_PORT': os.getenv('POSTGRES_PORT', '5432'),
            'PGADMIN_DEFAULT_EMAIL': os.getenv('PGADMIN_DEFAULT_EMAIL', 'admin@example.com'),
            'PGADMIN_DEFAULT_PASSWORD': os.getenv('PGADMIN_DEFAULT_PASSWORD', 'admin123'),
            'PGADMIN_PORT': os.getenv('PGADMIN_PORT', '8080'),
        }

        return env_vars

    except ImportError:
        print("❌ python-dotenv not installed. Installing...")
        # Use your existing venv installation function
        env, python_exe, pip_exe = create_venv_env('venv')
        result = subprocess.run([str(pip_exe), 'install', 'python-dotenv'],
                               capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print("✅ python-dotenv installed successfully!")
            # Try again
            return load_env_vars(env_file)
        else:
            print("❌ Failed to install python-dotenv, falling back to manual parsing")
            return load_env_manual(env_file)

def main():
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

    # Install dependencies
    if not install_dependencies(venv_path):
        print("❌ Failed to install dependencies")
        return

    print("✅ Python environment setup complete!")

    # Import chalk from the venv
    chalk = import_chalk_from_venv(venv_path)

    # Setup chalk standards
    if chalk:
        success = chalk.green.bold
        alert = chalk.red.bold
        info = chalk.blue.bold
        default = chalk.magenta.bold
        print(success("✅ Chalk imported successfully!"))
    else:
        print("❌ Could not import chalk, continuing without colored output...")
        # Fallback functions for when chalk is not available
        success = lambda x: f"✅ {x}"
        alert = lambda x: f"⚠️  {x}"
        info = lambda x: f"ℹ️  {x}"
        default = lambda x: f"({x})"

    # Prepare environment file inputs
    env_content = prep_env_file_inputs(info, default)


    print(info("Preparing .env file with the following inputs:"))
    print(env_content)

    try:
      # Create .env file
      status, env_file = create_env_file(env_content, success, alert, default)
    except Exception as e:
      print(alert(f"❌ Error creating .env file: {e}"))
      sys.exit(1)

    env_vars = load_env_vars(env_file)

    if env_vars is None:
        print(alert("❌ Failed to load environment variables from .env file."))
        sys.exit(1)

    print(success("✅ Environment variables loaded successfully!"))

    print(info("Environment variables:"))
    for key, value in env_vars.items():
        print(f"{key}: {value}")

    print(info("Starting Docker container..."))

    docker_command_up = [
        'docker', 'compose', 'up', '-d',
        '--build'
    ]
    status = run_command_in_venv(docker_command_up, venv_path)

    if status.returncode == 0:
        print(success("✅ Docker container started successfully!"))
    else:
        print(alert(f"❌ Failed to start Docker container: {status.stderr}"))
        sys.exit(1)


    docker_command_ps = [
        'docker', 'ps'
    ]

    print(info("Running Docker containers:"))
    status = run_command_in_venv(docker_command_ps, venv_path)

    print(success("Exiting setup script. You can now connect to your PostgreSQL database using the provided credentials."))


if __name__ == "__main__":
    main()
