# set shell 
set windows-shell := ["powershell.exe", "-c"]
set shell := ["bash", "-c"]

# --- Python Setup ---
python_version := "3.12"

python_dir := if os_family() == "windows" { ".\\.venv\\Scripts" } else { "./.venv/bin" }
python := python_dir + if os_family() == "windows" { "\\python.exe" } else { "/python" + python_version }
system_python := if os_family() == "windows" { "py.exe -" + python_version } else { "python" + python_version }

python_activate := "source " + python_dir + if os_family() == "windows" {"\\Activate.ps1" } else {"/activate" }
pip := python_dir+ if os_family() == "windows" {"\\pip.exe" } else {"/pip" }
pytest := python_dir+ if os_family() == "windows" {"\\pytest.exe" } else {"/pytest" }

# List recipes
@default:
    just --list --unsorted

# --- Python generate ---
# Print helper path to .venv
print_python_activate:
    echo {{ python_activate }}

# Generate python vnev 
generate_python_venv:
    {{ system_python }} -m venv .venv
    {{ python_activate }}
    {{ pip }} install -r requirements.txt

pip_install package:
    {{ pip }} install {{ package }}

pip_package_version package:
    {{ pip }} index versions {{ package }}

pip_freeze:
    pipreqs ./python --savepath ./requirements.txt --force

run:
    ./scripts/run.sh