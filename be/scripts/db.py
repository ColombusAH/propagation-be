#!/usr/bin/env python
"""
Database migration utility script for Python Prisma.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent


def run_command(command, env=None):
    """Run a shell command and display output"""
    print(f"Running: {' '.join(command)}")
    
    if env is None:
        env = os.environ.copy()
    
    try:
        result = subprocess.run(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def setup_prisma_environment():
    """Set up the Prisma environment"""
    env = os.environ.copy()
    
    # Check if DATABASE_URL is set, if not, use default for local development
    if "DATABASE_URL" not in env:
        # Default for local development
        env["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/shifty"
        print(f"Using default DATABASE_URL: {env['DATABASE_URL']}")
    
    return env


def generate_client():
    """Generate Prisma client"""
    env = setup_prisma_environment()
    run_command(["python", "-m", "prisma", "generate"], env)
    print("Prisma client generated successfully!")


def create_migration(name):
    """Create a new migration"""
    env = setup_prisma_environment()
    migration_name = name or "schema-update"
    run_command(["python", "-m", "prisma", "migrate", "dev", "--name", migration_name], env)
    print(f"Migration '{migration_name}' created successfully!")


def deploy_migrations():
    """Deploy all pending migrations"""
    env = setup_prisma_environment()
    run_command(["python", "-m", "prisma", "migrate", "deploy"], env)
    print("Migrations deployed successfully!")


def reset_database():
    """Reset the database (WARNING: destroys all data)"""
    env = setup_prisma_environment()
    confirm = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Operation canceled.")
        return
    
    run_command(["python", "-m", "prisma", "migrate", "reset", "--force"], env)
    print("Database reset successfully!")


def status():
    """Show migration status"""
    env = setup_prisma_environment()
    run_command(["python", "-m", "prisma", "migrate", "status"], env)


def main():
    parser = argparse.ArgumentParser(description="Database migration utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate client
    subparsers.add_parser("generate", help="Generate Prisma client")
    
    # Create migration
    migrate_parser = subparsers.add_parser("migrate", help="Create a new migration")
    migrate_parser.add_argument("--name", help="Migration name")
    
    # Deploy migrations
    subparsers.add_parser("deploy", help="Deploy all pending migrations")
    
    # Reset database
    subparsers.add_parser("reset", help="Reset database (WARNING: destroys all data)")
    
    # Status
    subparsers.add_parser("status", help="Show migration status")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generate_client()
    elif args.command == "migrate":
        create_migration(args.name)
    elif args.command == "deploy":
        deploy_migrations()
    elif args.command == "reset":
        reset_database()
    elif args.command == "status":
        status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 