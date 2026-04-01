#!/usr/bin/env python3
"""
One-click Deployment Script for PythonCode Project
Simplified deployment for all environments
"""

import os
import sys
import argparse

def deploy_development():
    """Deploy to development environment"""
    print("Deploying to development environment...")
    os.system("python scripts/deploy_development.py")
    return True

def deploy_staging():
    """Deploy to staging environment"""
    print("Deploying to staging environment...")
    os.system("python scripts/deploy_production.py --environment staging")
    return True

def deploy_production():
    """Deploy to production environment"""
    print("Deploying to production environment...")
    
    # Confirm production deployment
    print("\n" + "="*60)
    print("PRODUCTION DEPLOYMENT CONFIRMATION")
    print("="*60)
    print("\nWARNING: You are about to deploy to PRODUCTION.")
    print("This will affect live users and data.")
    print("\nPlease confirm:")
    print("  1. All tests have passed")
    print("  2. Code review is complete")
    print("  3. Backup of current deployment exists")
    print("  4. You have notified the team")
    
    confirmation = input("\nType 'DEPLOY' to confirm: ")
    
    if confirmation != "DEPLOY":
        print("Deployment cancelled")
        return False
    
    os.system("python scripts/deploy_production.py --environment production")
    return True

def deploy_all():
    """Deploy to all environments (dev -> staging -> prod)"""
    print("Deploying to all environments...")
    
    print("\n1. Development deployment:")
    if not deploy_development():
        print("Development deployment failed")
        return False
    
    print("\n2. Staging deployment:")
    if not deploy_staging():
        print("Staging deployment failed")
        return False
    
    print("\n3. Production deployment:")
    if not deploy_production():
        print("Production deployment failed")
        return False
    
    return True

def show_status():
    """Show deployment status"""
    print("Deployment Status")
    print("="*60)
    
    # Check if services are running
    print("\nChecking services...")
    
    services = [
        ("API Service", "http://localhost:5000/health"),
        ("Command System", "command_system/ directory"),
        ("Card Generator", "card_generator/ directory"),
        ("Monitoring", "monitoring_dashboard.py")
    ]
    
    for service, check in services:
        if "http" in check:
            # Check HTTP service
            import urllib.request
            try:
                response = urllib.request.urlopen(check, timeout=2)
                if response.getcode() == 200:
                    print(f"  ✓ {service}: Running")
                else:
                    print(f"  ✗ {service}: Not responding")
            except:
                print(f"  ✗ {service}: Not running")
        else:
            # Check directory or file
            if os.path.exists(check):
                print(f"  ✓ {service}: Available")
            else:
                print(f"  ✗ {service}: Not found")
    
    # Show deployment info
    print("\nDeployment scripts available:")
    print("  • python deploy.py --dev      - Deploy to development")
    print("  • python deploy.py --staging  - Deploy to staging")
    print("  • python deploy.py --prod     - Deploy to production")
    print("  • python deploy.py --all      - Deploy to all environments")
    print("  • python deploy.py --status   - Show current status")
    
    print("\nQuick commands:")
    print("  • Start API: cd api && python app.py")
    print("  • Run tests: python -m pytest tests/")
    print("  • Monitor: python monitoring_dashboard.py")
    print("  • Web Dashboard: python web_dashboard.py")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='PythonCode One-Click Deployment')
    parser.add_argument('--dev', action='store_true', help='Deploy to development')
    parser.add_argument('--staging', action='store_true', help='Deploy to staging')
    parser.add_argument('--prod', action='store_true', help='Deploy to production')
    parser.add_argument('--all', action='store_true', help='Deploy to all environments')
    parser.add_argument('--status', action='store_true', help='Show deployment status')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("PythonCode Deployment System")
    print("="*60)
    
    try:
        if args.dev:
            deploy_development()
        elif args.staging:
            deploy_staging()
        elif args.prod:
            deploy_production()
        elif args.all:
            deploy_all()
        elif args.status:
            show_status()
            
    except KeyboardInterrupt:
        print("\nDeployment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()