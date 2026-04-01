#!/usr/bin/env python3
"""
Production Deployment Script for PythonCode Project
Deploys the application to production environment with all necessary checks
"""

import os
import sys
import subprocess
import shutil
import time
from datetime import datetime
import json
import argparse

class ProductionDeployment:
    """Production deployment manager"""
    
    def __init__(self, environment="production"):
        """
        Initialize deployment manager
        
        Args:
            environment: Deployment environment (production, staging, development)
        """
        self.environment = environment
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.deployment_log = []
        self.start_time = datetime.now()
        
        # Environment-specific configurations
        self.configs = {
            "production": {
                "config_file": "config/config.production.yaml",
                "docker_compose": "docker-compose.production.yml",
                "deploy_dir": "/opt/pythoncode",
                "backup_dir": "/opt/pythoncode_backups",
                "service_name": "pythoncode",
                "port": 5000
            },
            "staging": {
                "config_file": "config/config.staging.yaml",
                "docker_compose": "docker-compose.staging.yml",
                "deploy_dir": "/opt/pythoncode_staging",
                "backup_dir": "/opt/pythoncode_staging_backups",
                "service_name": "pythoncode_staging",
                "port": 5001
            },
            "development": {
                "config_file": "config/config.yaml",
                "docker_compose": "docker-compose.yml",
                "deploy_dir": "/opt/pythoncode_dev",
                "backup_dir": "/opt/pythoncode_dev_backups",
                "service_name": "pythoncode_dev",
                "port": 5002
            }
        }
        
        self.env_config = self.configs.get(environment, self.configs["production"])
        
    def log(self, message, level="INFO"):
        """Log deployment message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
        
        # Also write to deployment log file
        with open("deployment.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def run_command(self, command, description=None, check=True):
        """Run a shell command"""
        if description:
            self.log(f"Running: {description}")
        
        self.log(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            if result.stderr:
                self.log(f"Stderr: {result.stderr.strip()}", level="WARNING")
                
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", level="ERROR")
            return False, e.stdout, e.stderr
        except Exception as e:
            self.log(f"Error running command: {e}", level="ERROR")
            return False, "", str(e)
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        self.log("Checking deployment prerequisites...")
        
        checks = []
        
        # Check Python version
        success, output, _ = self.run_command("python --version", "Checking Python version", check=False)
        if success and "Python 3" in output:
            checks.append(("Python 3.x", "✓"))
        else:
            checks.append(("Python 3.x", "✗"))
        
        # Check Docker
        success, output, _ = self.run_command("docker --version", "Checking Docker", check=False)
        if success and "Docker version" in output:
            checks.append(("Docker", "✓"))
        else:
            checks.append(("Docker", "✗"))
        
        # Check Docker Compose
        success, output, _ = self.run_command("docker-compose --version", "Checking Docker Compose", check=False)
        if success and "docker-compose version" in output:
            checks.append(("Docker Compose", "✓"))
        else:
            checks.append(("Docker Compose", "✗"))
        
        # Check Git
        success, output, _ = self.run_command("git --version", "Checking Git", check=False)
        if success and "git version" in output:
            checks.append(("Git", "✓"))
        else:
            checks.append(("Git", "✗"))
        
        # Display check results
        self.log("\nPrerequisite Check Results:")
        for check, status in checks:
            self.log(f"  {check}: {status}")
        
        # Return True if all checks passed
        return all(status == "✓" for _, status in checks)
    
    def run_tests(self):
        """Run tests before deployment"""
        self.log("Running tests before deployment...")
        
        test_commands = [
            ("python -m pytest tests/ -v", "Running unit tests"),
            ("python scripts/run_quality_checks.py", "Running quality checks"),
            ("python check_design_principles.py", "Checking design principles")
        ]
        
        all_passed = True
        
        for command, description in test_commands:
            self.log(f"\n{description}...")
            success, output, error = self.run_command(command, check=False)
            
            if success:
                self.log(f"{description} passed", level="SUCCESS")
            else:
                self.log(f"{description} failed", level="ERROR")
                if error:
                    self.log(f"Error: {error}", level="ERROR")
                all_passed = False
        
        return all_passed
    
    def create_backup(self):
        """Create backup of current deployment"""
        self.log("Creating backup of current deployment...")
        
        backup_dir = self.env_config["backup_dir"]
        deploy_dir = self.env_config["deploy_dir"]
        
        # Create backup directory if it doesn't exist
        self.run_command(f"mkdir -p {backup_dir}", "Creating backup directory")
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        if os.path.exists(deploy_dir):
            self.log(f"Backing up {deploy_dir} to {backup_path}")
            success, _, _ = self.run_command(
                f"cp -r {deploy_dir} {backup_path}",
                "Copying deployment directory"
            )
            
            if success:
                self.log(f"Backup created: {backup_path}", level="SUCCESS")
                return backup_path
            else:
                self.log("Backup failed", level="ERROR")
                return None
        else:
            self.log(f"Deployment directory {deploy_dir} does not exist, skipping backup")
            return None
    
    def build_docker_images(self):
        """Build Docker images"""
        self.log("Building Docker images...")
        
        docker_compose_file = self.env_config["docker_compose"]
        
        if os.path.exists(docker_compose_file):
            success, output, error = self.run_command(
                f"docker-compose -f {docker_compose_file} build",
                "Building Docker images"
            )
            
            if success:
                self.log("Docker images built successfully", level="SUCCESS")
                return True
            else:
                self.log("Docker build failed", level="ERROR")
                return False
        else:
            self.log(f"Docker compose file {docker_compose_file} not found", level="WARNING")
            
            # Try default docker-compose.yml
            if os.path.exists("docker-compose.yml"):
                success, output, error = self.run_command(
                    "docker-compose build",
                    "Building Docker images with default compose file"
                )
                return success
            else:
                self.log("No docker-compose file found", level="ERROR")
                return False
    
    def deploy_application(self):
        """Deploy the application"""
        self.log(f"Deploying application to {self.environment}...")
        
        deploy_dir = self.env_config["deploy_dir"]
        
        # Create deployment directory
        self.run_command(f"mkdir -p {deploy_dir}", "Creating deployment directory")
        
        # Copy project files
        self.log(f"Copying project files to {deploy_dir}")
        
        # List of files and directories to copy
        items_to_copy = [
            "api/",
            "command_system/",
            "card_generator/",
            "config/",
            "scripts/",
            "tests/",
            "utils/",
            "requirements.txt",
            "pyproject.toml",
            "README.md",
            "CHANGELOG.md",
            "docker-compose.yml",
            "Dockerfile",
            ".dockerignore"
        ]
        
        # Copy each item
        for item in items_to_copy:
            source = os.path.join(self.project_root, item)
            if os.path.exists(source):
                dest = os.path.join(deploy_dir, item)
                
                if os.path.isdir(source):
                    # Copy directory
                    self.run_command(
                        f"cp -r {source} {dest}",
                        f"Copying directory: {item}"
                    )
                else:
                    # Copy file
                    self.run_command(
                        f"cp {source} {dest}",
                        f"Copying file: {item}"
                    )
            else:
                self.log(f"Source not found: {item}", level="WARNING")
        
        # Set environment-specific config
        config_file = self.env_config["config_file"]
        if os.path.exists(config_file):
            dest_config = os.path.join(deploy_dir, "config/config.yaml")
            self.run_command(
                f"cp {config_file} {dest_config}",
                f"Setting {self.environment} configuration"
            )
        
        self.log(f"Application deployed to {deploy_dir}", level="SUCCESS")
        return True
    
    def start_services(self):
        """Start application services"""
        self.log("Starting application services...")
        
        deploy_dir = self.env_config["deploy_dir"]
        docker_compose_file = self.env_config["docker_compose"]
        
        # Change to deployment directory
        original_dir = os.getcwd()
        os.chdir(deploy_dir)
        
        try:
            # Start services with Docker Compose
            if os.path.exists(docker_compose_file):
                success, output, error = self.run_command(
                    f"docker-compose -f {docker_compose_file} up -d",
                    "Starting services with Docker Compose"
                )
            elif os.path.exists("docker-compose.yml"):
                success, output, error = self.run_command(
                    "docker-compose up -d",
                    "Starting services with default Docker Compose"
                )
            else:
                self.log("No docker-compose file found, starting manually", level="WARNING")
                
                # Try to start API service directly
                success, output, error = self.run_command(
                    "cd api && python app.py &",
                    "Starting API service manually",
                    check=False
                )
            
            if success:
                self.log("Services started successfully", level="SUCCESS")
                
                # Wait for services to be ready
                self.log("Waiting for services to be ready...")
                time.sleep(10)
                
                # Check service health
                port = self.env_config["port"]
                success, output, error = self.run_command(
                    f"curl -f http://localhost:{port}/health",
                    "Checking service health",
                    check=False
                )
                
                if success:
                    self.log("Service health check passed", level="SUCCESS")
                else:
                    self.log("Service health check failed", level="WARNING")
                
                return True
            else:
                self.log("Failed to start services", level="ERROR")
                return False
                
        finally:
            # Return to original directory
            os.chdir(original_dir)
    
    def run_post_deployment_checks(self):
        """Run post-deployment checks"""
        self.log("Running post-deployment checks...")
        
        port = self.env_config["port"]
        checks = []
        
        # Check if service is responding
        success, output, error = self.run_command(
            f"curl -s http://localhost:{port}/health",
            "Checking service health endpoint",
            check=False
        )
        
        if success and "healthy" in output.lower():
            checks.append(("Service Health", "✓"))
        else:
            checks.append(("Service Health", "✗"))
        
        # Check Docker containers
        success, output, error = self.run_command(
            "docker ps --filter 'name=pythoncode' --format 'table {{.Names}}\t{{.Status}}'",
            "Checking Docker containers",
            check=False
        )
        
        if success and "pythoncode" in output:
            checks.append(("Docker Containers", "✓"))
        else:
            checks.append(("Docker Containers", "✗"))
        
        # Display check results
        self.log("\nPost-Deployment Check Results:")
        for check, status in checks:
            self.log(f"  {check}: {status}")
        
        return all(status == "✓" for _, status in checks)
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        self.log("Generating deployment report...")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "environment": self.environment,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "log_entries": self.deployment_log,
            "summary": {
                "prerequisites_passed": self.prerequisites_passed,
                "tests_passed": self.tests_passed,
                "backup_created": self.backup_created is not None,
                "deployment_successful": self.deployment_successful,
                "services_started": self.services_started,
                "post_deployment_checks_passed": self.post_deployment_checks_passed
            }
        }
        
        # Save report to file
        report_file = f"deployment_report_{self.environment}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Deployment report saved to {report_file}", level="SUCCESS")
        return report_file
    
    def deploy(self):
        """Execute full deployment pipeline"""
        self.log(f"Starting {self.environment.upper()} deployment")
        self.log("="*60)
        
        try:
            # Step 1: Check prerequisites
            self.prerequisites_passed = self.check_prerequisites()
            if not self.prerequisites_passed:
                self.log("Prerequisite checks failed. Aborting deployment.", level="ERROR")
                return False
            
            # Step 2: Run tests
            self.tests_passed = self.run_tests()
            if not self.tests_passed:
                self.log("Tests failed. Aborting deployment.", level="ERROR")
                return False
            
            # Step 3: Create backup
            self.backup_created = self.create_backup()
            
            # Step 4: Build Docker images
            if not self.build_docker_images():
                self.log("Docker build failed. Aborting deployment.", level="ERROR")
                return False
            
            # Step 5: Deploy application
            self.deployment_successful = self.deploy_application()
            if not self.deployment_successful:
                self.log("Deployment failed. Aborting.", level="ERROR")
                return False
            
            # Step 6: Start services
            self.services_started = self.start_services()
            if not self.services_started:
                self.log("Failed to start services.", level="ERROR")
                return False
            
            # Step 7: Run post-deployment checks
            self.post_deployment_checks_passed = self.run_post_deployment_checks()
            
            # Step 8: Generate report
            report_file = self.generate_deployment_report()
            
            # Final summary
            self.log("\n" + "="*60)
            self.log(f"{self.environment.upper()} DEPLOYMENT COMPLETE")
            self.log("="*60)
            
            if all([
                self.prerequisites_passed,
                self.tests_passed,
                self.deployment_successful,
                self.services_started
            ]):
                self.log("Deployment successful! ✅", level="SUCCESS")
                self.log(f"Report: {report_file}")
                return True
            else:
                self.log("Deployment completed with issues ⚠️", level="WARNING")
                self.log(f"Report: {report_file}")
                return False
                
        except Exception as e:
            self.log(f"Deployment failed with error: {e}", level="ERROR")
            import traceback
            self.log(traceback.format_exc(), level="ERROR")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='PythonCode Production Deployment Script')
    parser.add_argument('--environment', '-e', default='production',
                       choices=['production', 'staging', 'development'],
                       help='Deployment environment (default: production)')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip tests before deployment')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip backup creation')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run - show what would be done without actually deploying')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print(f"Would deploy to: {args.environment}")
        print("Steps that would be executed:")
        print("  1. Check prerequisites")
        print("  2. Run tests" + (" (skipped)" if args.skip_tests else ""))
        print("  3. Create backup" + (" (skipped)" if args.skip_backup else ""))
        print("  4. Build Docker images")
        print("  5. Deploy application")
        print("  6. Start services")
        print("  7. Run post-deployment checks")
        print("  8. Generate report")
        return
    
    # Create deployment instance
    deployment = ProductionDeployment(environment=args.environment)
    
    # Override methods if skipping
    if args.skip_tests:
        deployment.run_tests = lambda: True
        deployment.tests_passed = True
    
    if args.skip_backup:
        deployment.create_backup = lambda: None
        deployment.backup_created = None
    
    # Execute deployment
    success = deployment.deploy()
    
    if success:
        print(f"\n{args.environment.upper()} deployment completed successfully!")
        sys.exit(0)
    else:
        print(f"\n{args.environment.upper()} deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()