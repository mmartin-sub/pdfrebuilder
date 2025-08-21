#!/usr/bin/env python3
"""
Project Configuration Migration Script

This script provides comprehensive migration capabilities for Multi-Format Document Engine
projects, including configuration files, font setups, and workflow updates.

Usage:
    python migrate_project_configs.py <project_directory> [--target-version 1.0] [--backup]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pdfrebuilder.models.schema_migration import SchemaMigrationError, migrate_schema
from pdfrebuilder.models.schema_validator import validate_document


class ProjectMigrator:
    """Handles migration of entire project configurations"""

    def __init__(self, project_dir: Path, target_version: str = "1.0", create_backup: bool = True):
        self.project_dir = project_dir
        self.target_version = target_version
        self.create_backup = create_backup
        self.backup_dir: Path | None = None
        self.migration_log: list[str] = []

    def migrate_project(self) -> bool:
        """
        Migrate entire project to target version

        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            self.log("Starting project migration...")
            self.log(f"Project directory: {self.project_dir}")
            self.log(f"Target version: {self.target_version}")

            # Create backup if requested
            if self.create_backup:
                self._create_project_backup()

            # Find and migrate configuration files
            config_files = self._find_configuration_files()
            self.log(f"Found {len(config_files)} configuration files")

            success_count = 0
            for config_file in config_files:
                if self._migrate_configuration_file(config_file):
                    success_count += 1

            # Migrate font configurations
            self._migrate_font_configurations()

            # Update workflow files
            self._update_workflow_files()

            # Generate migration report
            self._generate_migration_report()

            self.log(f"Migration completed: {success_count}/{len(config_files)} files migrated successfully")
            return success_count == len(config_files)

        except Exception as e:
            self.log(f"Migration failed with error: {e}")
            return False

    def _create_project_backup(self) -> None:
        """Create comprehensive project backup"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_dir / f"migration_backup_{timestamp}"
        self.backup_dir.mkdir(exist_ok=True)

        self.log(f"Creating backup in: {self.backup_dir}")

        # Backup configuration files
        config_files = self._find_configuration_files()
        for config_file in config_files:
            backup_path = self.backup_dir / config_file.relative_to(self.project_dir)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config_file, backup_path)

        # Backup override files
        override_files = list(self.project_dir.glob("**/manual_overrides.json5"))
        for override_file in override_files:
            backup_path = self.backup_dir / override_file.relative_to(self.project_dir)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(override_file, backup_path)

        # Backup custom scripts
        scripts_dir = self.project_dir / "scripts"
        if scripts_dir.exists():
            shutil.copytree(scripts_dir, self.backup_dir / "scripts")

        # Create backup manifest
        manifest_file = self.backup_dir / "backup_manifest.txt"
        with open(manifest_file, "w") as f:
            for item in self.backup_dir.rglob("*"):
                if item.is_file() and item != manifest_file:
                    f.write(f"{item.relative_to(self.backup_dir)}\n")

        self.log("Backup created successfully")

    def _find_configuration_files(self) -> list[Path]:
        """Find all configuration files that need migration"""
        config_patterns = [
            "**/layout_config.json",
            "**/config.json",
            "**/document_config.json",
            "**/*_config.json",
        ]

        config_files = []
        for pattern in config_patterns:
            config_files.extend(self.project_dir.glob(pattern))

        # Remove duplicates and sort
        config_files = sorted(set(config_files))

        # Filter out backup files and test files
        filtered_files = []
        for config_file in config_files:
            if not any(part in config_file.parts for part in ["backup", "test", "temp", ".git", "__pycache__"]):
                filtered_files.append(config_file)

        return filtered_files

    def _migrate_configuration_file(self, config_file: Path) -> bool:
        """
        Migrate a single configuration file

        Args:
            config_file: Path to configuration file

        Returns:
            bool: True if migration successful
        """
        try:
            self.log(f"Migrating: {config_file}")

            # Load current configuration
            with open(config_file, encoding="utf-8") as f:
                current_config = json.load(f)

            # Check if migration is needed
            current_version = current_config.get("version", "unknown")
            if current_version == self.target_version:
                self.log(f"  Already at target version {self.target_version}")
                return True

            # Perform migration
            migrated_config = migrate_schema(current_config, self.target_version)

            # Validate migrated configuration
            validation_result = validate_document(migrated_config)
            if not validation_result.is_valid:
                self.log(f"  Validation failed: {validation_result.errors}")
                return False

            # Save migrated configuration
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(migrated_config, f, indent=2)

            self.log(f"  ✓ Migrated from {current_version} to {self.target_version}")
            return True

        except SchemaMigrationError as e:
            self.log(f"  ✗ Migration failed: {e}")
            return False
        except Exception as e:
            self.log(f"  ✗ Unexpected error: {e}")
            return False

    def _migrate_font_configurations(self) -> None:
        """Migrate font configurations to new format"""
        self.log("Migrating font configurations...")

        # Look for font configuration files
        font_config_files = list(self.project_dir.glob("**/font_config.json"))

        for font_config_file in font_config_files:
            try:
                with open(font_config_file, encoding="utf-8") as f:
                    font_config = json.load(f)

                # Convert old format to new format
                if "font_paths" in font_config:
                    new_config = {
                        "font_manager": {
                            "cache_directory": "./fonts/cache/",
                            "download_directory": "./fonts/downloaded/",
                            "system_fonts": True,
                            "google_fonts": {"enabled": True, "api_key": None},
                        },
                        "font_mappings": {},
                    }

                    # Convert font mappings
                    if "font_mappings" in font_config:
                        for font_name, font_path in font_config["font_mappings"].items():
                            new_config["font_mappings"][font_name] = {
                                "family": font_name,
                                "variants": ["regular"],
                                "source": "local",
                                "path": font_path,
                            }

                    # Save updated configuration
                    with open(font_config_file, "w", encoding="utf-8") as f:
                        json.dump(new_config, f, indent=2)

                    self.log(f"  ✓ Migrated font configuration: {font_config_file}")

            except Exception as e:
                self.log(f"  ✗ Failed to migrate font configuration {font_config_file}: {e}")

    def _update_workflow_files(self) -> None:
        """Update workflow files for new version"""
        self.log("Updating workflow files...")

        # Update Makefile if present
        makefile = self.project_dir / "Makefile"
        if makefile.exists():
            self._update_makefile(makefile)

        # Update GitHub Actions workflows
        workflows_dir = self.project_dir / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                self._update_github_workflow(workflow_file)

        # Update Docker files
        dockerfile = self.project_dir / "Dockerfile"
        if dockerfile.exists():
            self._update_dockerfile(dockerfile)

    def _update_makefile(self, makefile: Path) -> None:
        """Update Makefile for new version"""
        try:
            with open(makefile) as f:
                content = f.read()

            # Replace old commands with new ones
            replacements = {
                "pip install -r requirements.txt": "hatch env create",
                "python -m pytest": "hatch run test",
                "black .": "hatch run style",
                "pip freeze": "hatch env show",
            }

            updated_content = content
            for old_cmd, new_cmd in replacements.items():
                updated_content = updated_content.replace(old_cmd, new_cmd)

            if updated_content != content:
                with open(makefile, "w") as f:
                    f.write(updated_content)
                self.log("  ✓ Updated Makefile")

        except Exception as e:
            self.log(f"  ✗ Failed to update Makefile: {e}")

    def _update_github_workflow(self, workflow_file: Path) -> None:
        """Update GitHub Actions workflow file"""
        try:
            with open(workflow_file) as f:
                content = f.read()

            # Update Python setup and commands
            replacements = {
                "pip install -r requirements.txt": "pip install hatch uv",
                "python -m pytest": "hatch run test",
                "actions/setup-python@v4": "actions/setup-python@v5",
            }

            updated_content = content
            for old_text, new_text in replacements.items():
                updated_content = updated_content.replace(old_text, new_text)

            if updated_content != content:
                with open(workflow_file, "w") as f:
                    f.write(updated_content)
                self.log(f"  ✓ Updated workflow: {workflow_file.name}")

        except Exception as e:
            self.log(f"  ✗ Failed to update workflow {workflow_file.name}: {e}")

    def _update_dockerfile(self, dockerfile: Path) -> None:
        """Update Dockerfile for new version"""
        try:
            with open(dockerfile) as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                # Update Python version and package management
                if "COPY requirements.txt" in line:
                    updated_lines.append("COPY pyproject.toml .\n")
                elif "pip install -r requirements.txt" in line:
                    updated_lines.append("RUN pip install hatch uv && hatch env create\n")
                elif 'CMD ["python"' in line:
                    updated_lines.append('CMD ["hatch", "run", "python", "main.py"]\n')
                else:
                    updated_lines.append(line)

            with open(dockerfile, "w") as f:
                f.writelines(updated_lines)

            self.log("  ✓ Updated Dockerfile")

        except Exception as e:
            self.log(f"  ✗ Failed to update Dockerfile: {e}")

    def _generate_migration_report(self) -> None:
        """Generate comprehensive migration report"""
        report_file = self.project_dir / "migration_report.txt"

        with open(report_file, "w") as f:
            f.write("Multi-Format Document Engine Migration Report\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Project Directory: {self.project_dir}\n")
            f.write(f"Target Version: {self.target_version}\n")
            f.write(f"Backup Directory: {self.backup_dir}\n\n")

            f.write("Migration Log:\n")
            f.write("-" * 20 + "\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")

            f.write("\nNext Steps:\n")
            f.write("-" * 20 + "\n")
            f.write("1. Test migrated configurations with your workflows\n")
            f.write("2. Update any custom scripts to use new import paths\n")
            f.write("3. Run comprehensive tests: hatch run test\n")
            f.write("4. Validate documentation: python scripts/validate_docs.py --all\n")
            f.write("5. Remove backup directory after confirming migration success\n")

        self.log(f"Migration report saved to: {report_file}")

    def log(self, message: str) -> None:
        """Add message to migration log"""
        self.migration_log.append(message)
        print(message)


def main():
    """Main migration script entry point"""
    parser = argparse.ArgumentParser(description="Migrate Multi-Format Document Engine project configurations")
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("--target-version", default="1.0", help="Target schema version (default: 1.0)")
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before migration",
    )
    parser.add_argument("--no-backup", action="store_false", dest="backup", help="Skip backup creation")

    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    if not project_dir.exists():
        print(f"Error: Project directory does not exist: {project_dir}")
        sys.exit(1)

    if not project_dir.is_dir():
        print(f"Error: Path is not a directory: {project_dir}")
        sys.exit(1)

    # Perform migration
    migrator = ProjectMigrator(project_dir, args.target_version, args.backup)
    success = migrator.migrate_project()

    if success:
        print("\n✓ Migration completed successfully!")
        print("Please review the migration report and test your configurations.")
        sys.exit(0)
    else:
        print("\n✗ Migration completed with errors.")
        print("Please review the migration report and address any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
