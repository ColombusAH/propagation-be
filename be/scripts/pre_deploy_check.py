#!/usr/bin/env python
"""
Pre-deployment check script to verify application configuration.
"""
import os
import sys
import subprocess
import importlib.util
import json
from pathlib import Path

def check_file_exists(file_path, required=True):
    """Check if a file exists and print status"""
    path = Path(file_path)
    exists = path.exists()
    
    if exists:
        print(f"✅ Found {file_path}")
    elif required:
        print(f"❌ Missing required file: {file_path}")
        return False
    else:
        print(f"⚠️ Optional file not found: {file_path}")
    
    return exists

def check_import(module_name):
    """Check if a Python module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ Module '{module_name}' is available")
        return True
    except ImportError as e:
        print(f"❌ Cannot import module '{module_name}': {e}")
        return False

def check_command(command):
    """Check if a command is available"""
    try:
        subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            shell=True
        )
        print(f"✅ Command '{command}' is available")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Command '{command}' failed")
        return False
    except FileNotFoundError:
        print(f"❌ Command '{command}' not found")
        return False

def check_environment_variables():
    """Check for critical environment variables"""
    critical_vars = ["DATABASE_URL", "SECRET_KEY"]
    optional_vars = ["PORT", "DEBUG", "API_V1_STR", "PROJECT_NAME"]
    
    all_present = True
    print("\n== Environment Variables ==")
    
    for var in critical_vars:
        if var in os.environ:
            # Mask the value if it might contain sensitive data
            if "URL" in var or "KEY" in var or "SECRET" in var or "PASSWORD" in var:
                print(f"✅ {var} is set [value masked]")
            else:
                print(f"✅ {var} is set to: {os.environ[var]}")
        else:
            print(f"❌ Critical variable {var} is not set")
            all_present = False
    
    for var in optional_vars:
        if var in os.environ:
            print(f"✅ Optional variable {var} is set")
        else:
            print(f"⚠️ Optional variable {var} is not set")
    
    return all_present

def check_prisma_schema():
    """Check the Prisma schema for potential issues"""
    schema_path = "prisma/schema.prisma"
    
    if not check_file_exists(schema_path):
        return False
    
    try:
        with open(schema_path, "r") as f:
            schema_content = f.read()
        
        # Check for proper client provider
        if "provider = \"prisma-client-py\"" in schema_content:
            print("✅ Prisma schema has correct Python client provider")
        else:
            print("❌ Prisma schema does not use prisma-client-py provider")
            return False
        
        # Check for database URL env var usage
        if "url      = env(\"DATABASE_URL\")" in schema_content:
            print("✅ Prisma schema uses DATABASE_URL from environment")
        else:
            print("❌ Prisma schema doesn't use DATABASE_URL from environment")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking Prisma schema: {e}")
        return False

def check_docker_files():
    """Check Dockerfile and docker-compose.yml"""
    docker_files = [
        ("Dockerfile", True),
        ("Dockerfile.dev", False),
        ("docker-compose.yml", True),
        ("docker-entrypoint.sh", True),
        ("scripts/railway-entrypoint.sh", True),
    ]
    
    all_required_exist = True
    print("\n== Docker Files ==")
    
    for file_path, required in docker_files:
        if not check_file_exists(file_path, required) and required:
            all_required_exist = False
    
    return all_required_exist

def main():
    """Run all checks"""
    print("=== Pre-Deployment Check ===\n")
    
    checks = [
        ("Critical Files", lambda: check_file_exists("app/main.py") and 
                                 check_file_exists("requirements.txt") and
                                 check_file_exists("prisma/schema.prisma")),
        ("Prisma Schema", check_prisma_schema),
        ("Docker Files", check_docker_files),
        ("Python Dependencies", lambda: check_import("prisma") and 
                                     check_import("fastapi") and
                                     check_import("uvicorn")),
        ("Node Dependencies", lambda: check_command("node --version") and 
                                   check_command("npx --version") and
                                   check_command("npx prisma --version")),
        ("Environment Variables", check_environment_variables),
    ]
    
    results = {}
    all_passed = True
    
    for name, check_func in checks:
        print(f"\n== {name} ==")
        passed = check_func()
        results[name] = passed
        if not passed and name != "Environment Variables":  # Environment vars might be set at deployment
            all_passed = False
    
    print("\n=== Summary ===")
    for name, passed in results.items():
        print(f"{name}: {'✅ Passed' if passed else '❌ Failed'}")
    
    if all_passed:
        print("\n✅ All checks passed! Ready for deployment.")
        return 0
    else:
        print("\n❌ Some checks failed. Review the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 