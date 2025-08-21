import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Use the standard library tomllib if available (Python 3.11+)
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        print(
            "Error: 'tomli' is required for this script on Python < 3.11. Please run 'pip install tomli'",
            file=sys.stderr,
        )
        sys.exit(1)

import requests
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

# --- Configuration ---
STUBS_DIR = Path("stubs")
PYPROJECT_PATH = Path("pyproject.toml")


def get_hatch_python_executable() -> str:
    """Gets the absolute path to the Python executable in the active Hatch environment."""
    print("--- Locating Hatch environment's Python executable ---")
    try:
        result = subprocess.run(
            ["hatch", "run", "which", "python"],
            capture_output=True,
            text=True,
            check=True,
        )
        executable_path = result.stdout.strip()
        print(f"  -> Found at: {executable_path}")
        return executable_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(
            f"Error: Could not find the Python executable in the Hatch environment. {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def get_project_name() -> str:
    """Dynamically reads the project name from pyproject.toml."""
    print(f"--- Reading project name from {PYPROJECT_PATH} ---")
    if not PYPROJECT_PATH.is_file():
        print(
            f"Error: {PYPROJECT_PATH} not found in the current directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
        project_name = data.get("project", {}).get("name")
    print(f"  -> Found project name: '{project_name}'")
    return project_name


def get_all_project_dependencies() -> list[str]:
    """Gets a complete list of all project dependencies from Hatch, including all optional groups."""
    print("--- Getting all project dependencies from Hatch ---")
    result = subprocess.run(
        ["hatch", "dep", "show", "requirements", "--all"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()


def get_installed_packages_info(hatch_python: str) -> dict:
    """
    Runs an inspector script inside the Hatch env to get a reliable map of installed packages.
    """
    print("--- Running inspector script inside Hatch environment to map packages ---")

    inspector_script = """
import json
from importlib import metadata
from packaging.utils import canonicalize_name

packages = {}
for dist in metadata.distributions():
    dist_name = dist.metadata["name"]
    normalized_dist_name = canonicalize_name(dist_name)

    import_names = []
    try:
        top_level = dist.read_text('top_level.txt')
        if top_level:
            import_names = list(filter(None, top_level.strip().splitlines()))
    except Exception:
        pass

    if not import_names:
        import_names = [dist_name.replace('-', '_')]

    packages[normalized_dist_name] = {
        "dist_name": dist_name,
        "version": dist.version,
        "import_names": import_names,
    }
print(json.dumps(packages, indent=2))
"""
    try:
        result = subprocess.run(
            [hatch_python, "-c", inspector_script],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print("Error: The package inspector script failed.", file=sys.stderr)
        print(f"Stderr: {e.stderr if hasattr(e, 'stderr') else str(e)}", file=sys.stderr)
        sys.exit(1)


def generate_stubs(dry_run: bool, only_packages: list[str] | None):
    if dry_run:
        print("\n*** Running in DRY-RUN mode. No files will be created or deleted. ***")

    hatch_python_executable = get_hatch_python_executable()
    project_name = get_project_name()
    all_deps = get_all_project_dependencies()
    installed_packages = get_installed_packages_info(hatch_python_executable)

    req_to_dist_map = {}
    for dist_name_key, info in installed_packages.items():
        dist_name = info["dist_name"]
        req_to_dist_map[canonicalize_name(dist_name)] = dist_name_key
        if dist_name.startswith("py"):
            potential_req_name = dist_name[2:]
            req_to_dist_map[canonicalize_name(potential_req_name)] = dist_name_key

    unique_deps = {canonicalize_name(Requirement(d).name): d for d in all_deps}.values()

    if only_packages:
        normalized_only_set = {canonicalize_name(p) for p in only_packages}
        print(f"\n--- Filtering to process ONLY: {', '.join(only_packages)} ---")
        filtered_deps = [dep for dep in unique_deps if canonicalize_name(Requirement(dep).name) in normalized_only_set]

        found_deps_names = {canonicalize_name(Requirement(dep).name) for dep in filtered_deps}
        not_found = normalized_only_set - found_deps_names
        if not_found:
            print(
                f"Error: The following packages specified with --only were not found in project dependencies: {', '.join(not_found)}",
                file=sys.stderr,
            )
            sys.exit(1)
        unique_deps = filtered_deps

    stubs_to_install = []
    packages_to_stub = {}

    print("\n--- Resolving and categorizing dependencies ---")
    for dep_string in unique_deps:
        req = Requirement(dep_string)
        pypi_name = req.name

        if pypi_name.startswith("types-"):
            print(f"  -> Skipping '{pypi_name}' (it is a stub package).")
            continue

        normalized_pypi_name = canonicalize_name(pypi_name)

        if normalized_pypi_name == canonicalize_name(project_name):
            print(f"  -> Skipping self-dependency: '{dep_string}'")
            continue

        print(f"Processing '{pypi_name}'...")
        stub_package_name = f"types-{pypi_name}"
        response = requests.get(f"https://pypi.org/pypi/{stub_package_name}/json")

        if response.status_code == 200:
            if canonicalize_name(stub_package_name) in installed_packages:
                print(f"  -> Found '{stub_package_name}', which is already installed.")
            else:
                print(f"  -> Found '{stub_package_name}'. Would recommend adding it as a dependency.")
                stubs_to_install.append(stub_package_name)
        else:
            dist_name_key = req_to_dist_map.get(normalized_pypi_name)
            if dist_name_key and dist_name_key in installed_packages:
                package_info = installed_packages[dist_name_key]
                pinned_spec = f"{package_info['dist_name']}=={package_info['version']}"
                import_names = package_info["import_names"]
                print(f"  -> Found installed as '{package_info['dist_name']}'. Queued for stub generation.")
                packages_to_stub[pypi_name] = (import_names, pinned_spec)
            else:
                print(
                    f"  -> WARNING: Could not resolve '{pypi_name}' to an installed package. Skipping.",
                    file=sys.stderr,
                )

    if stubs_to_install and not only_packages:
        print("\n--- Recommended Action ---")
        print("Add the following stub packages to your project's development dependencies:")
        print("-" * 30)
        for stub in sorted(stubs_to_install):
            print(f'  "{stub}",')
        print("-" * 30)

    failed_libs = []
    if packages_to_stub:
        prefix = "[Dry Run] " if dry_run else ""
        print(f"\n--- {prefix}Managing local stubs in ./{STUBS_DIR} ---")
        if not dry_run:
            STUBS_DIR.mkdir(exist_ok=True)

        print(f"\n--- {prefix}Cleaning up stubs for packages to be regenerated ---")
        for pypi_name, (import_names, _) in packages_to_stub.items():
            for import_name in import_names:
                stub_dir_to_remove = STUBS_DIR / import_name
                if stub_dir_to_remove.exists():
                    print(f"  -> {prefix}Would remove old stubs at '{stub_dir_to_remove}'")
                    if not dry_run:
                        shutil.rmtree(stub_dir_to_remove)

        print(f"\n--- {prefix}Generating new stubs from pinned versions ---")
        for pypi_name, (import_names, pinned_spec) in packages_to_stub.items():
            print(f"\nProcessing '{pypi_name}' ({pinned_spec})...")
            if dry_run:
                print(f"  -> {prefix}Would generate stubs for import name(s): {import_names}")
                continue

            with tempfile.TemporaryDirectory() as temp_dir_str:
                temp_dir = Path(temp_dir_str)
                try:
                    subprocess.run(
                        [
                            hatch_python_executable,
                            "-m",
                            "venv",
                            str(temp_dir / ".venv"),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    pip_executable = str(temp_dir / ".venv" / "bin" / "pip")
                    pyright_executable = str(temp_dir / ".venv" / "bin" / "pyright")

                    print(f"  -> Installing '{pinned_spec}' and 'pyright' into temporary environment...")
                    subprocess.run(
                        [pip_executable, "install", pinned_spec, "pyright"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )

                    for import_name in import_names:
                        print(f"  -> Generating stub for import '{import_name}'...")
                        subprocess.run(
                            [pyright_executable, "--createstub", import_name],
                            check=True,
                            capture_output=True,
                            text=True,
                            cwd=temp_dir,
                        )

                        source_stub_dir = temp_dir / "typings"

                        for stub_file in source_stub_dir.glob("**/*.pyi"):
                            relative_path = stub_file.relative_to(source_stub_dir)
                            destination_file = STUBS_DIR / relative_path
                            destination_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(stub_file), str(destination_file))

                        print(f"  -> Successfully generated stubs in '{STUBS_DIR}/'")

                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    error_message = e.stderr.strip() if hasattr(e, "stderr") and e.stderr else str(e)
                    print(
                        f"  -> ERROR: Failed to create stub for {pypi_name}. Reason: {error_message}",
                        file=sys.stderr,
                    )
                    failed_libs.append(f"{pypi_name}")

    # --- NEW: Conditional Cache Clearing ---
    if not only_packages:
        prefix = "[Dry Run] " if dry_run else ""
        print(f"\n--- {prefix}Clearing type checker caches ---")
        for cache_name in [".mypy_cache", ".pyright_cache"]:
            cache_path = Path.cwd() / cache_name
            if cache_path.is_dir():
                print(f"  -> {prefix}Would remove '{cache_name}'...")
                if not dry_run:
                    shutil.rmtree(cache_path)
            else:
                print(f"  -> Cache '{cache_name}' not found. Skipping.")
    else:
        print("\n--- Skipping cache clearing because --only is active. ---")
    # --- End Conditional Logic ---

    print("\n--- All tasks complete! ---")
    if failed_libs:
        print("\nCould not generate stubs for the following libraries:", file=sys.stderr)
        for lib in set(failed_libs):
            print(f"  - {lib}", file=sys.stderr)
        sys.exit(1)

    if packages_to_stub and not dry_run:
        print("\nSuccessfully generated/updated all necessary local stubs.")
        print(f"Review the changes in the '{STUBS_DIR}/' directory and commit them.")
    elif dry_run:
        print("\nDry run finished. No changes were made.")


def main():
    parser = argparse.ArgumentParser(
        description="A tool for managing Python type stubs for your project.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Check for community stubs and generate local ones if not found.",
    )
    generate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run, showing what would be done without changing any files.",
    )
    # --- NEW: Updated --only argument ---
    generate_parser.add_argument(
        "--only",
        dest="only_packages",
        nargs="+",  # Accept one or more arguments
        metavar="PACKAGE_NAME",
        help="Target only one or more specific packages (e.g., --only requests google-api-core).",
    )

    args = parser.parse_args()

    if not args.command:
        print("-------------------------------------------------")
        print("Welcome to the Stub Management Tool!")
        print("-------------------------------------------------")
        print("\nUsage:")
        print("  hatch run stubs generate [OPTIONS]")
        print("\nCommands:")
        print("  generate     Checks for and generates all necessary type stubs.")
        print("\nOptions:")
        print("  --dry-run    Show what would be done without making any changes.")
        print("  --only NAME [NAME ...]")
        print("               Target only specific packages. Disables cache clearing.")
        print("\n-------------------------------------------------")
        parser.print_help()
        sys.exit(0)

    if args.command == "generate":
        generate_stubs(dry_run=args.dry_run, only_packages=args.only_packages)


if __name__ == "__main__":
    main()
