#!/usr/bin/env python3
"""
Deployment script for Helios Dynamics ERP system
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def run_command(command, description, show_output=False):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if show_output and result.stdout:
            print(f"Output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        if show_output and e.stdout:
            print(f"Stdout: {e.stdout}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        "python": "python --version",
        "docker": "docker --version",
        "docker-compose": "docker-compose --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        if not run_command(command, f"Checking {tool}"):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        return False
    
    print("✅ All requirements satisfied")
    return True

def check_docker_status():
    """Check detailed Docker status"""
    print("🐳 Checking Docker container status...")
    
    # Check running containers
    containers = run_command("docker ps", "Listing running containers", show_output=True)
    
    # Check container logs
    print("\n📋 Checking container logs...")
    
    # Get container names/IDs
    container_list = run_command("docker ps --format '{{.Names}}'", "Getting container names")
    
    if container_list:
        for container in container_list.strip().split('\n'):
            if container.strip():
                print(f"\n🔍 Logs for {container}:")
                logs = run_command(f"docker logs --tail=10 {container}", f"Getting logs for {container}", show_output=True)
    
    # Check if ports are in use
    print("\n🔌 Checking port usage...")
    ports_8000 = run_command("lsof -i :8000", "Checking port 8000", show_output=True)
    ports_8501 = run_command("lsof -i :8501", "Checking port 8501", show_output=True)

def install_requirements():
    """Install Python requirements with fallback options"""
    print("📦 Installing Python requirements...")
    
    # Try minimal requirements first
    if os.path.exists("requirements-minimal.txt"):
        print("📦 Installing minimal requirements first...")
        if run_command("pip install -r requirements-minimal.txt", "Installing minimal requirements"):
            print("✅ Minimal requirements installed successfully")
        
    # Try to install streamlit separately with specific options
    print("📦 Attempting to install Streamlit...")
    
    # Option 1: Try installing streamlit with no binary for pyarrow
    if run_command("pip install --no-binary=pyarrow streamlit==1.28.1", "Installing Streamlit (option 1)"):
        print("✅ Streamlit installed successfully")
        return True
    
    # Option 2: Try installing streamlit without pyarrow
    print("⚠️ Pyarrow installation failed, trying streamlit without pyarrow...")
    if run_command("pip install streamlit==1.28.1 --no-deps", "Installing Streamlit without dependencies"):
        # Install streamlit dependencies manually (excluding pyarrow)
        streamlit_deps = [
            "altair>=4.0.0",
            "blinker>=1.0.0",
            "cachetools>=4.0",
            "click>=7.0",
            "importlib-metadata>=1.4",
            "numpy",
            "packaging>=14.1",
            "pandas>=1.3.0",
            "pillow>=7.1.0",
            "protobuf>=3.20.2,<5",
            "rich>=10.14.0",
            "tenacity>=8.1.0",
            "toml",
            "typing-extensions>=4.3.0",
            "tzlocal>=1.1",
            "validators>=0.2",
            "gitpython!=3.1.19",
            "pydeck>=0.8.0b4",
            "tornado>=6.0.3",
            "watchdog"
        ]
        
        for dep in streamlit_deps:
            run_command(f"pip install {dep}", f"Installing {dep}")
        
        return True
    
    # Option 3: Skip streamlit for now
    print("⚠️ Streamlit installation failed. Continuing without frontend...")
    return False

def setup_database():
    """Initialize the database"""
    print("🗄️ Setting up database...")
    
    # Create databases directory
    os.makedirs("databases", exist_ok=True)
    
    # Run database initialization
    return run_command("python backend/test_system.py", "Database initialization")

def build_containers():
    """Build Docker containers"""
    print("🐳 Building Docker containers...")
    return run_command("docker-compose build", "Building containers")

def start_services():
    """Start all services"""
    print("🚀 Starting services...")
    return run_command("docker-compose up -d", "Starting services")

def check_health():
    """Check if services are healthy with detailed diagnostics"""
    print("🏥 Checking service health...")
    
    # Wait for services to start
    print("⏳ Waiting 15 seconds for services to start...")
    time.sleep(15)
    
    # First check if containers are running
    print("🔍 Checking container status...")
    containers = run_command("docker-compose ps", "Checking container status", show_output=True)
    
    # Check if API port is accessible
    print("🌐 Testing API connectivity...")
    
    # Try multiple health check attempts
    for attempt in range(3):
        print(f"🔄 Health check attempt {attempt + 1}/3...")
        
        # Check if port 8000 is responding
        api_response = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/", "Testing API root endpoint")
        
        if api_response and "200" in api_response:
            print("✅ API root endpoint responding")
            
            # Try health endpoint
            health_response = run_command("curl -s http://localhost:8000/health", "Testing health endpoint", show_output=True)
            
            if health_response:
                print("✅ API is healthy")
                print("✅ Frontend should be available at: http://localhost:8501")
                print("✅ API docs available at: http://localhost:8000/docs")
                return True
        
        if attempt < 2:  # Don't wait after last attempt
            print("⏳ Waiting 10 seconds before retry...")
            time.sleep(10)
    
    print("❌ Health check failed after 3 attempts")
    return False

def show_logs():
    """Show service logs with more detail"""
    print("📋 Detailed service logs:")
    
    # Show logs for all services
    services = ["api", "frontend"]
    
    for service in services:
        print(f"\n🔍 Logs for {service}:")
        logs = run_command(f"docker-compose logs --tail=20 {service}", f"Getting {service} logs", show_output=True)
    
    # Show general docker-compose logs
    print(f"\n🔍 General docker-compose logs:")
    general_logs = run_command("docker-compose logs --tail=30", "Getting general logs", show_output=True)

def diagnose_failure():
    """Comprehensive failure diagnosis"""
    print("\n🔍 DIAGNOSING DEPLOYMENT FAILURE")
    print("=" * 40)
    
    # 1. Check Docker status
    check_docker_status()
    
    # 2. Check docker-compose status  
    print("\n📊 Docker Compose Status:")
    run_command("docker-compose ps", "Docker compose status", show_output=True)
    
    # 3. Check if docker-compose.yml exists
    if os.path.exists("docker-compose.yml"):
        print("✅ docker-compose.yml exists")
    else:
        print("❌ docker-compose.yml missing!")
        return
    
    # 4. Check if Dockerfile exists
    if os.path.exists("Dockerfile"):
        print("✅ Dockerfile exists")
    else:
        print("❌ Dockerfile missing!")
    
    # 5. Test local connectivity
    print("\n🌐 Testing local connectivity:")
    run_command("curl -v http://localhost:8000", "Testing localhost:8000", show_output=True)
    
    # 6. Show detailed logs
    show_logs()
    
    # 7. Suggest solutions
    print("\n💡 SUGGESTED SOLUTIONS:")
    print("1. Try: docker-compose down && docker-compose up -d")
    print("2. Check if ports 8000/8501 are already in use")
    print("3. Try local development mode instead: python deploy.py -> option 3")
    print("4. Check Docker Desktop is running")
    print("5. Try: docker system prune (to clean up)")

def start_local_mode():
    """Start services in local mode without Docker"""
    print("🚀 Starting local mode...")
    
    # Install requirements first
    streamlit_available = install_requirements()
    
    # Test the system first
    print("🧪 Testing system...")
    if not run_command("python backend/test_system.py", "System test"):
        print("❌ System test failed")
        return False
    
    print("\n🎉 System test passed!")
    
    if streamlit_available:
        print("\n📊 Choose how to start:")
        print("1. Start API server only")
        print("2. Start frontend only") 
        print("3. Start both (API + Frontend)")
        print("4. Run demo mode")
        
        choice = input("\nEnter choice (1-4): ").strip()
    else:
        print("\n📊 Streamlit not available. Choose:")
        print("1. Start API server only")
        print("2. Run demo mode")
        print("3. Try installing Streamlit with conda")
        
        choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("🌐 Starting API server...")
        print("API will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop")
        subprocess.run([sys.executable, "backend/api.py"])
    
    elif choice == "2" and streamlit_available:
        print("🎨 Starting frontend...")
        print("Frontend will be available at: http://localhost:8501")
        print("Press Ctrl+C to stop")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
    
    elif choice == "3" and streamlit_available:
        print("🌐 Starting API server in background...")
        api_process = subprocess.Popen([sys.executable, "backend/api.py"])
        
        # Wait a bit for API to start
        time.sleep(3)
        
        print("🎨 Starting frontend...")
        print("Frontend available at: http://localhost:8501")
        print("API available at: http://localhost:8000")
        print("Press Ctrl+C to stop both services")
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            api_process.terminate()
            print("✅ Services stopped")
    
    elif choice == "2" or choice == "4":
        print("🎮 Starting demo mode...")
        subprocess.run([sys.executable, "backend/run_demo.py"])
    
    elif choice == "3" and not streamlit_available:
        print("🐍 Trying to install Streamlit with conda...")
        print("Run: conda install -c conda-forge streamlit")
        print("Then try running the deploy script again.")
    
    else:
        print("❌ Invalid choice")

def start_simple_mode():
    """Start in simple test mode"""
    print("🏠 Starting simple test mode...")
    
    print("\n📋 Available options:")
    print("1. Test the system")
    print("2. Run sales agent demo") 
    print("3. Test database connection")
    print("4. Install minimal requirements")
    print("5. Try alternative Streamlit installation")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("🧪 Testing system...")
        subprocess.run([sys.executable, "backend/test_system.py"])
    
    elif choice == "2":
        print("🛍️ Running sales agent demo...")
        subprocess.run([sys.executable, "backend/agents/sales_agent_simple.py"])
    
    elif choice == "3":
        print("🗄️ Testing database...")
        subprocess.run([sys.executable, "-c", "import sys; sys.path.append('backend'); from db import get_db; print('✅ Database connection successful')"])
    
    elif choice == "4":
        run_command("pip install -r requirements-minimal.txt", "Installing minimal requirements")
    
    elif choice == "5":
        print("🔧 Alternative Streamlit installation methods:")
        print("1. conda install -c conda-forge streamlit")
        print("2. pip install streamlit --no-cache-dir")
        print("3. Use Docker deployment instead")
    
    else:
        print("❌ Invalid choice")

def main():
    """Main deployment function"""
    print("🏢 Helios Dynamics ERP Deployment")
    print("=" * 50)
    
    # Ask for deployment mode
    print("\nChoose deployment mode:")
    print("1. Docker deployment (recommended - avoids build issues)")
    print("2. Local development mode (may have dependency issues)")
    print("3. Simple test mode (minimal setup, API only)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Docker deployment
        if not check_requirements():
            sys.exit(1)
        
        setup_database()
        
        if build_containers() and start_services():
            if check_health():
                print("\n🎉 Deployment successful!")
                print("\n📊 Access points:")
                print("   Frontend: http://localhost:8501")
                print("   API: http://localhost:8000")
                print("   API Docs: http://localhost:8000/docs")
                print("\n🔧 Management commands:")
                print("   Stop: docker-compose down")
                print("   Logs: docker-compose logs -f")
                print("   Restart: docker-compose restart")
            else:
                print("\n💥 DEPLOYMENT FAILED!")
                diagnose_failure()
                sys.exit(1)
        else:
            print("❌ Container build/start failed")
            diagnose_failure()
            sys.exit(1)
    
    elif choice == "2":
        # Local development mode
        start_local_mode()
    
    elif choice == "3":
        # Simple test mode
        start_simple_mode()
    
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()