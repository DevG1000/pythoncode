#!/usr/bin/env python3
"""
Development Deployment Script for PythonCode Project
Quick deployment for development environment
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def run_command(command, description=None):
    """Run a shell command"""
    if description:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {description}")
        print(f"  Command: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line:
                    print(f"  Output: {line}")

        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                if line:
                    print(f"  Error: {line}")

        return result.returncode == 0

    except Exception as e:
        print(f"  Error: {e}")
        return False


def check_dependencies():
    """Check and install dependencies"""
    print("\n" + "=" * 60)
    print("Checking and installing dependencies...")
    print("=" * 60)

    # Check Python
    if not run_command("python --version", "Checking Python"):
        print("ERROR: Python not found or not accessible")
        return False

    # Install/upgrade pip
    run_command("python -m pip install --upgrade pip", "Upgrading pip")

    # Install dependencies
    if os.path.exists("requirements.txt"):
        run_command("pip install -r requirements.txt", "Installing Python dependencies")
    else:
        print("WARNING: requirements.txt not found")

    return True


def setup_environment():
    """Setup development environment"""
    print("\n" + "=" * 60)
    print("Setting up development environment...")
    print("=" * 60)

    # Create necessary directories
    directories = ["logs", "data", "uploads", "backups"]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

    # Copy environment config if needed
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        import shutil

        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example")

    return True


def run_quick_tests():
    """Run quick tests"""
    print("\n" + "=" * 60)
    print("Running quick tests...")
    print("=" * 60)

    tests = [
        ("python -m pytest tests/ -xvs -k 'not slow'", "Running quick unit tests"),
        ("python scripts/run_quality_checks.py --quick", "Running quick quality checks"),
        ("python check_design_principles.py", "Checking design principles"),
    ]

    all_passed = True

    for command, description in tests:
        print(f"\n{description}:")
        success = run_command(command)

        if success:
            print(f"  [OK] {description} passed")
        else:
            print(f"  ✗ {description} failed")
            all_passed = False

    return all_passed


def start_services():
    """Start development services"""
    print("\n" + "=" * 60)
    print("Starting development services...")
    print("=" * 60)

    services = []

    # Check if Docker is available
    docker_available = run_command("docker --version", "Checking Docker", check=False)

    if docker_available and os.path.exists("docker-compose.yml"):
        # Start with Docker Compose
        print("Starting services with Docker Compose...")
        success = run_command("docker-compose up -d", "Starting Docker services")

        if success:
            services.append(("Docker Services", "[OK]"))

            # Wait for services to be ready
            import time

            print("Waiting for services to start...")
            time.sleep(5)

            # Check service health
            health_check = run_command("docker-compose ps", "Checking Docker services status", check=False)
        else:
            services.append(("Docker Services", "✗"))
    else:
        print("Docker not available or docker-compose.yml not found")
        services.append(("Docker Services", "✗ (skipped)"))

    # Start API service directly
    print("\nStarting API service...")
    api_success = run_command("cd api && python app.py &", "Starting API service", check=False)

    if api_success:
        services.append(("API Service", "[OK]"))

        # Wait for API to start
        import time

        time.sleep(3)

        # Check API health
        health_success = run_command("curl -s http://localhost:5000/health", "Checking API health", check=False)

        if health_success:
            services.append(("API Health", "[OK]"))
        else:
            services.append(("API Health", "✗"))
    else:
        services.append(("API Service", "✗"))

    # Display service status
    print("\nService Status:")
    for service, status in services:
        print(f"  {service}: {status}")

    return all(status == "[OK]" for service, status in services if "skipped" not in status)


def display_welcome():
    """Display welcome message and next steps"""
    print("\n" + "=" * 60)
    print("DEVELOPMENT DEPLOYMENT COMPLETE!")
    print("=" * 60)

    print("\nYour PythonCode development environment is ready!")

    print("\nServices available:")
    print("  • API Service: http://localhost:5000")
    print("  • API Documentation: http://localhost:5000/docs")
    print("  • Health Check: http://localhost:5000/health")

    print("\nUseful commands:")
    print("  • Run tests: python -m pytest tests/")
    print("  • Run quality checks: python scripts/run_quality_checks.py")
    print("  • Check design principles: python check_design_principles.py")
    print("  • Start monitoring: python monitoring_dashboard.py")
    print("  • Start web dashboard: python web_dashboard.py")

    print("\nProject structure:")
    print("  • api/ - API service (Flask)")
    print("  • command_system/ - Command execution system")
    print("  • card_generator/ - Business card generator")
    print("  • config/ - Configuration files")
    print("  • scripts/ - Utility scripts")
    print("  • tests/ - Test files")
    print("  • utils/ - Utility modules")

    print("\nNext steps:")
    print("  1. Visit http://localhost:5000 to verify API is running")
    print("  2. Run tests to ensure everything works: python -m pytest tests/")
    print("  3. Check the monitoring dashboard: python monitoring_dashboard.py")
    print("  4. Review the project documentation in README.md")

    print("\n" + "=" * 60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PythonCode Development Deployment")
    parser.add_argument("--skip-tests", action="store_true", help="Skip tests before deployment")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--quick", action="store_true", help="Quick deployment (skip tests and some checks)")

    args = parser.parse_args()

    if args.quick:
        args.skip_tests = True
        args.skip_deps = True

    print("PythonCode Development Deployment")
    print("=" * 60)

    try:
        # Step 1: Dependencies
        if not args.skip_deps:
            if not check_dependencies():
                print("ERROR: Dependency check/installation failed")
                sys.exit(1)
        else:
            print("\nSkipping dependency check/installation")

        # Step 2: Environment setup
        if not setup_environment():
            print("ERROR: Environment setup failed")
            sys.exit(1)

        # Step 3: Tests
        if not args.skip_tests:
            if not run_quick_tests():
                print("\nWARNING: Some tests failed")
                response = input("Continue with deployment? (y/n): ")
                if response.lower() != "y":
                    print("Deployment cancelled")
                    sys.exit(1)
        else:
            print("\nSkipping tests")

        # Step 4: Start services
        if not start_services():
            print("\nWARNING: Some services failed to start")

        # Step 5: Display welcome
        display_welcome()

        print("\nDevelopment deployment completed! [ROCKET]")

    except KeyboardInterrupt:
        print("\n\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Deployment failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
