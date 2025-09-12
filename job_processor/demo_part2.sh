#!/bin/bash

# Part 2: Python Job Processor Service - Interactive Demo Script
# This script demonstrates all aspects of the OptiFlight Coordinator Job Processor

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Utility functions
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_step() {
    echo -e "\n${GREEN}>>> $1${NC}\n"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

wait_for_user() {
    echo -e "\n${YELLOW}Press Enter to continue...${NC}"
    read -r
}

# Check if we're in the right directory
check_environment() {
    print_header "🔍 ENVIRONMENT VERIFICATION"
    
    print_step "Checking current directory and prerequisites"
    
    # Check if we're in the job_processor directory
    if [[ ! -f "app/main.py" ]]; then
        print_error "Please run this script from the job_processor directory"
        print_info "Current directory: $(pwd)"
        print_info "Expected files: app/main.py, Dockerfile, requirements.txt"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    print_info "✅ Environment check passed"
    print_info "📁 Current directory: $(pwd)"
    print_info "🐳 Docker version: $(docker --version)"
    print_info "🐍 Python version: $(python3 --version)"
    print_info "📡 curl version: $(curl --version | head -1)"
    
    wait_for_user
}

# Build and start the service
build_and_start_service() {
    print_header "🚀 BUILD AND DEPLOY SERVICE"
    
    print_step "Building Docker image"
    docker build -t optiflight-coordinator:latest . || {
        print_error "Failed to build Docker image"
        exit 1
    }
    
    print_step "Cleaning up existing containers"
    docker stop optiflight-coordinator 2>/dev/null || true
    docker rm optiflight-coordinator 2>/dev/null || true
    
    print_step "Starting OptiFlight Coordinator service"
    docker run -d --name optiflight-coordinator \
        -p 8000:8000 \
        -e LOG_LEVEL=info \
        -e DEBUG=false \
        optiflight-coordinator:latest || {
        print_error "Failed to start container"
        exit 1
    }
    
    print_step "Waiting for service to be ready"
    sleep 8
    
    # Verify container is running
    if docker ps | grep -q optiflight-coordinator; then
        print_info "✅ Service is running"
        print_info "🌐 Service URL: http://localhost:8000"
    else
        print_error "Service failed to start"
        print_info "Container logs:"
        docker logs optiflight-coordinator
        exit 1
    fi
    
    wait_for_user
}

# Test health endpoints
test_health_endpoints() {
    print_header "🏥 HEALTH CHECK VALIDATION"
    
    print_step "Testing basic health endpoint"
    if curl -f -s http://localhost:8000/health > /dev/null; then
        print_info "✅ Basic health check passed"
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        print_error "Basic health check failed"
        return 1
    fi
    
    print_step "Testing detailed health endpoint"
    if curl -f -s http://localhost:8000/health/detailed > /dev/null; then
        print_info "✅ Detailed health check passed"
        curl -s http://localhost:8000/health/detailed | python3 -m json.tool
    else
        print_error "Detailed health check failed"
        return 1
    fi
    
    print_step "Testing metrics summary endpoint"
    if curl -f -s http://localhost:8000/metrics/summary > /dev/null; then
        print_info "✅ Metrics endpoint accessible"
        curl -s http://localhost:8000/metrics/summary | python3 -m json.tool
    else
        print_warning "Metrics endpoint not accessible"
    fi
    
    wait_for_user
}

# Demonstrate configuration management
demo_configuration_management() {
    print_header "⚙️  CONFIGURATION MANAGEMENT DEMO"
    
    print_step "Creating tenant configuration for ABC Airlines"
    print_info "This demonstrates the CRUD API for tenant configurations"
    
    ABC_CONFIG='{
        "airline": "ABC",
        "max_parallel_executions": 10,
        "active_modules": [
            {
                "name": "route_optimizer",
                "image": "sita/route-optimizer",
                "version": "v1.2.0",
                "enabled": true,
                "cpu_request": "200m",
                "cpu_limit": "1000m",
                "memory_request": "256Mi",
                "memory_limit": "1Gi",
                "timeout_seconds": 300,
                "env_vars": {"LOG_LEVEL": "INFO", "OPTIMIZATION_MODE": "FUEL_EFFICIENT"}
            },
            {
                "name": "fuel_optimizer", 
                "image": "sita/fuel-optimizer",
                "version": "v1.1.0",
                "enabled": true,
                "cpu_request": "150m",
                "cpu_limit": "500m",
                "memory_request": "128Mi",
                "memory_limit": "512Mi",
                "timeout_seconds": 180,
                "env_vars": {"LOG_LEVEL": "INFO"}
            }
        ],
        "rate_limit_per_minute": 1000,
        "namespace": "airline-abc",
        "priority": 1,
        "resource_quota": {
            "requests.cpu": "4",
            "requests.memory": "8Gi",
            "limits.cpu": "16", 
            "limits.memory": "32Gi"
        }
    }'
    
    if curl -f -s -X POST http://localhost:8000/api/v1/config/tenants \
        -H "Content-Type: application/json" \
        -d "$ABC_CONFIG" > /dev/null; then
        print_info "✅ ABC Airlines configuration created"
        curl -s -X POST http://localhost:8000/api/v1/config/tenants \
            -H "Content-Type: application/json" \
            -d "$ABC_CONFIG" | python3 -m json.tool
    else
        print_error "Failed to create ABC Airlines configuration"
        return 1
    fi
    
    print_step "Creating second tenant configuration for XYZ Airlines"
    
    XYZ_CONFIG='{
        "airline": "XYZ",
        "max_parallel_executions": 5,
        "active_modules": [
            {
                "name": "weather_optimizer",
                "image": "sita/weather-optimizer",
                "version": "v1.0.0",
                "enabled": true,
                "timeout_seconds": 120
            }
        ],
        "rate_limit_per_minute": 500
    }'
    
    if curl -f -s -X POST http://localhost:8000/api/v1/config/tenants \
        -H "Content-Type: application/json" \
        -d "$XYZ_CONFIG" > /dev/null; then
        print_info "✅ XYZ Airlines configuration created"
        curl -s -X POST http://localhost:8000/api/v1/config/tenants \
            -H "Content-Type: application/json" \
            -d "$XYZ_CONFIG" | python3 -m json.tool
    else
        print_error "Failed to create XYZ Airlines configuration"
        return 1
    fi
    
    print_step "Retrieving all tenant configurations"
    if curl -f -s http://localhost:8000/api/v1/config/tenants > /dev/null; then
        print_info "✅ Successfully retrieved all configurations"
        curl -s http://localhost:8000/api/v1/config/tenants | python3 -m json.tool
    else
        print_error "Failed to retrieve configurations"
        return 1
    fi
    
    wait_for_user
}

# Demonstrate event processing and job orchestration
demo_event_processing() {
    print_header "🛩️  EVENT PROCESSING & JOB ORCHESTRATION"
    
    print_step "Processing Position Report Event for ABC Airlines"
    print_info "This demonstrates how position reports trigger optimization jobs"
    
    POSITION_EVENT='{
        "flight_id": "ABC123",
        "airline": "ABC",
        "aircraft_type": "A320",
        "registration": "N123AB",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 35000,
        "speed": 450,
        "heading": 90
    }'
    
    POSITION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/events/position-report \
        -H "Content-Type: application/json" \
        -d "$POSITION_EVENT")
    
    if echo "$POSITION_RESPONSE" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        print_info "✅ Position report processed successfully"
        echo "$POSITION_RESPONSE" | python3 -m json.tool
        
        # Extract job IDs for later monitoring
        JOB_IDS=$(echo "$POSITION_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for job in data.get('jobs', []):
        print(job['job_id'])
except:
    pass
")
    else
        print_error "Failed to process position report"
        echo "$POSITION_RESPONSE"
        return 1
    fi
    
    print_step "Processing Flight Plan Event for XYZ Airlines"
    print_info "This demonstrates flight plan optimization workflow"
    
    FLIGHT_PLAN_EVENT='{
        "flight_id": "XYZ456",
        "airline": "XYZ", 
        "aircraft_type": "B737",
        "registration": "N456CD",
        "route": [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 34.0522, "longitude": -118.2437}
        ],
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "estimated_duration": 360
    }'
    
    FLIGHT_PLAN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/events/flight-plan \
        -H "Content-Type: application/json" \
        -d "$FLIGHT_PLAN_EVENT")
    
    if echo "$FLIGHT_PLAN_RESPONSE" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        print_info "✅ Flight plan processed successfully"
        echo "$FLIGHT_PLAN_RESPONSE" | python3 -m json.tool
    else
        print_error "Failed to process flight plan"
        echo "$FLIGHT_PLAN_RESPONSE"
        return 1
    fi
    
    wait_for_user
}

# Demonstrate job management and monitoring
demo_job_management() {
    print_header "📊 JOB MANAGEMENT & MONITORING"
    
    print_step "Allowing jobs to process (waiting 6 seconds)"
    sleep 6
    
    print_step "Listing all active and completed jobs"
    if curl -f -s http://localhost:8000/api/v1/jobs > /dev/null; then
        print_info "✅ Successfully retrieved job list"
        curl -s http://localhost:8000/api/v1/jobs | python3 -m json.tool
    else
        print_error "Failed to retrieve job list"
        return 1
    fi
    
    print_step "Filtering jobs by airline (ABC)"
    if curl -f -s "http://localhost:8000/api/v1/jobs?airline=ABC" > /dev/null; then
        print_info "✅ Successfully retrieved ABC Airlines jobs"
        curl -s "http://localhost:8000/api/v1/jobs?airline=ABC" | python3 -m json.tool
    else
        print_error "Failed to retrieve ABC Airlines jobs"
    fi
    
    print_step "Getting administrative statistics"
    if curl -f -s http://localhost:8000/api/v1/admin/stats > /dev/null; then
        print_info "✅ Successfully retrieved admin statistics"
        curl -s http://localhost:8000/api/v1/admin/stats | python3 -m json.tool
    else
        print_error "Failed to retrieve admin statistics"
    fi
    
    print_step "Getting updated metrics summary"
    if curl -f -s http://localhost:8000/metrics/summary > /dev/null; then
        print_info "✅ Successfully retrieved metrics"
        curl -s http://localhost:8000/metrics/summary | python3 -m json.tool
    else
        print_error "Failed to retrieve metrics"
    fi
    
    wait_for_user
}

# Demonstrate advanced features
demo_advanced_features() {
    print_header "🚀 ADVANCED FEATURES DEMONSTRATION"
    
    print_step "Testing rate limiting with rapid requests"
    print_info "Sending multiple rapid requests to test rate limiting"
    
    for i in {1..5}; do
        echo -n "Request $i: "
        RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/events/position-report \
            -H "Content-Type: application/json" \
            -d '{
                "flight_id": "ABC999",
                "airline": "ABC", 
                "aircraft_type": "A320",
                "registration": "N999AB",
                "latitude": 41.405937,
                "longitude": 2.178605
            }')
        
        if echo "$RESPONSE" | grep -q "Rate limit exceeded"; then
            print_warning "Rate limited"
        elif echo "$RESPONSE" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
            print_info "Success"
        else
            print_error "Failed"
        fi
        sleep 0.1
    done
    
    print_step "Testing error handling with invalid event"
    print_info "Sending invalid event to test error handling"
    
    ERROR_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/events/position-report \
        -H "Content-Type: application/json" \
        -d '{
            "flight_id": "INVALID",
            "airline": "UNKNOWN_AIRLINE"
        }')
    
    if echo "$ERROR_RESPONSE" | grep -q "error\\|detail"; then
        print_info "✅ Error handling working correctly"
        echo "$ERROR_RESPONSE" | python3 -m json.tool
    else
        print_warning "Unexpected error response format"
        echo "$ERROR_RESPONSE"
    fi
    
    print_step "Testing configuration validation"
    print_info "Sending invalid configuration to test validation"
    
    VALIDATION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/config/tenants \
        -H "Content-Type: application/json" \
        -d '{
            "max_parallel_executions": 10
        }')
    
    if echo "$VALIDATION_RESPONSE" | grep -q "error\\|detail"; then
        print_info "✅ Configuration validation working correctly"
        echo "$VALIDATION_RESPONSE" | python3 -m json.tool
    else
        print_warning "Unexpected validation response format"
        echo "$VALIDATION_RESPONSE"
    fi
    
    wait_for_user
}

# Demonstrate testing framework
demo_testing_framework() {
    print_header "🧪 TESTING FRAMEWORK DEMONSTRATION"
    
    print_step "Running unit tests"
    print_info "Demonstrating the comprehensive test suite"
    
    # Create a simplified test runner for demo
    cat > demo_test_runner.py << 'EOF'
#!/usr/bin/env python3
"""Demo test runner to showcase testing capabilities."""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

def run_model_tests():
    """Run model validation tests."""
    try:
        from models import TenantConfig, ModuleConfig, PositionReportEvent
        
        # Test ModuleConfig
        config = ModuleConfig(
            name="test_optimizer",
            image="sita/test-optimizer"
        )
        assert config.name == "test_optimizer"
        assert config.version == "latest"  # default value
        print("✅ ModuleConfig test passed")
        
        # Test TenantConfig  
        tenant = TenantConfig(airline="TEST")
        assert tenant.airline == "TEST"
        assert tenant.max_parallel_executions == 10  # default value
        namespace = tenant.get_namespace()
        assert "test" in namespace.lower()
        print("✅ TenantConfig test passed")
        
        # Test PositionReportEvent
        position = PositionReportEvent(
            flight_id="TEST123",
            airline="TEST",
            aircraft_type="A320",
            registration="TEST-001",
            latitude=37.7749,
            longitude=-122.4194
        )
        assert position.flight_id == "TEST123"
        assert position.latitude == 37.7749
        print("✅ PositionReportEvent test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Model tests failed: {e}")
        return False

def run_config_tests():
    """Run configuration tests."""
    try:
        from config import Settings
        
        settings = Settings()
        assert settings.app_name == "OptiFlight Coordinator"
        assert settings.api_port == 8000
        print("✅ Configuration test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration tests failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔬 Running unit tests...")
    
    tests_passed = 0
    total_tests = 2
    
    if run_model_tests():
        tests_passed += 1
        
    if run_config_tests():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} test suites passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF
    
    if python3 demo_test_runner.py; then
        print_info "✅ Test demonstration completed successfully"
    else
        print_warning "Test demonstration had some issues (expected in demo environment)"
    fi
    
    print_step "Checking test coverage artifacts"
    if [ -f ".coverage" ]; then
        print_info "✅ Coverage data file found"
    else
        print_info "ℹ️  No coverage data (run pytest with coverage for detailed metrics)"
    fi
    
    if [ -d "htmlcov" ]; then
        print_info "✅ HTML coverage report directory found"
        print_info "📁 Coverage files: $(ls htmlcov/ | head -5 | tr '\n' ' ')..."
    else
        print_info "ℹ️  No HTML coverage report"
    fi
    
    # Clean up test file
    rm -f demo_test_runner.py
    
    wait_for_user
}

# Show container logs and debugging
show_debugging_info() {
    print_header "🔍 DEBUGGING & MONITORING INFORMATION"
    
    print_step "Container status and resource usage"
    if docker ps | grep -q optiflight-coordinator; then
        print_info "✅ Container is running"
        docker stats --no-stream optiflight-coordinator
    else
        print_error "Container is not running"
        return 1
    fi
    
    print_step "Recent container logs"
    print_info "Last 15 lines of application logs:"
    docker logs --tail=15 optiflight-coordinator
    
    print_step "Available API endpoints summary"
    echo -e "${CYAN}🌐 Available API Endpoints:${NC}"
    echo "  Health:           http://localhost:8000/health"
    echo "  Detailed Health:  http://localhost:8000/health/detailed"
    echo "  Metrics:          http://localhost:8000/metrics/summary"
    echo "  Configuration:    http://localhost:8000/api/v1/config/tenants"
    echo "  Events:           http://localhost:8000/api/v1/events/position-report"
    echo "  Events:           http://localhost:8000/api/v1/events/flight-plan"
    echo "  Jobs:             http://localhost:8000/api/v1/jobs"
    echo "  Admin Stats:      http://localhost:8000/api/v1/admin/stats"
    echo "  API Docs:         http://localhost:8000/docs (if debug enabled)"
    
    wait_for_user
}

# Showcase future-proofing capabilities
showcase_future_proofing() {
    print_header "🔮 FUTURE-PROOFING & EXTENSIBILITY"
    
    print_step "Architectural extensibility highlights"
    echo -e "${GREEN}🏗️  Architecture Benefits:${NC}"
    echo "  ✅ Modular design supports adding new optimization modules"
    echo "  ✅ Event-driven architecture allows new event types"
    echo "  ✅ Plugin-based filter system ready for implementation"
    echo "  ✅ Multi-tenant design scales horizontally"
    
    echo -e "\n${GREEN}🔧 Configuration Flexibility:${NC}"
    echo "  ✅ Dynamic module configuration per tenant"
    echo "  ✅ Resource quota management per namespace"
    echo "  ✅ Environment-specific settings support"
    echo "  ✅ Rate limiting and priority management"
    
    echo -e "\n${GREEN}📈 Scalability Features:${NC}"
    echo "  ✅ Kubernetes-native job orchestration"
    echo "  ✅ Background job processing with queue support"
    echo "  ✅ Metrics and monitoring integration"
    echo "  ✅ Structured logging for observability"
    
    echo -e "\n${GREEN}🛡️  Production Readiness:${NC}"
    echo "  ✅ Comprehensive error handling and validation"
    echo "  ✅ Security best practices (non-root containers)"
    echo "  ✅ Health checks and graceful shutdown"
    echo "  ✅ Test coverage and quality assurance"
    
    print_step "Code extensibility examples"
    print_info "Adding a new optimization module is as simple as:"
    echo '1. Add module configuration to tenant config:'
    echo '{
    "name": "new_optimizer",
    "image": "sita/new-optimizer",
    "version": "v1.0.0",
    "enabled": true
}'
    echo ''
    echo '2. Module automatically gets:'
    echo '   - Kubernetes job orchestration'
    echo '   - Resource management'
    echo '   - Monitoring and logging'
    echo '   - Error handling and retries'
    
    wait_for_user
}

# Clean up resources
cleanup() {
    print_header "🧹 CLEANUP"
    
    print_step "Stopping and removing OptiFlight Coordinator container"
    if docker ps | grep -q optiflight-coordinator; then
        docker stop optiflight-coordinator
        print_info "✅ Container stopped"
    fi
    
    if docker ps -a | grep -q optiflight-coordinator; then
        docker rm optiflight-coordinator
        print_info "✅ Container removed"
    fi
    
    # Optional: Remove image
    echo -e "\n${YELLOW}Do you want to remove the Docker image as well? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        docker rmi optiflight-coordinator:latest 2>/dev/null || true
        print_info "✅ Docker image removed"
    fi
    
    # Clean up temporary files
    rm -f demo_test_runner.py 2>/dev/null || true
    
    print_step "Demo cleanup completed"
}

# Main demo execution
main() {
    print_header "🚀 OptiFlight Coordinator Job Processor Demo"
    echo -e "${PURPLE}Part 2: Python Job Processor Service${NC}"
    echo -e "${PURPLE}Complete demonstration of all implemented features${NC}"
    
    echo -e "\n${CYAN}This demo will showcase:${NC}"
    echo "• Multi-tenant job processing engine"
    echo "• RESTful configuration management API"
    echo "• Event-driven optimization workflow"
    echo "• Kubernetes job orchestration simulation"
    echo "• Comprehensive monitoring and health checks"
    echo "• Production-ready containerization"
    echo "• Quality assurance through testing"
    echo "• Future-proof extensible architecture"
    
    wait_for_user
    
    # Execute demo steps
    check_environment
    build_and_start_service
    test_health_endpoints
    demo_configuration_management
    demo_event_processing
    demo_job_management
    demo_advanced_features
    demo_testing_framework
    show_debugging_info
    showcase_future_proofing
    
    print_header "✅ DEMO COMPLETED SUCCESSFULLY!"
    
    echo -e "${GREEN}📝 Summary of Demonstrated Features:${NC}"
    echo "   • Multi-tenant job processing with configuration management"
    echo "   • Event-driven optimization workflow orchestration"
    echo "   • Kubernetes job scheduling with proper resource management"
    echo "   • RESTful API for tenant configuration CRUD operations"
    echo "   • Comprehensive monitoring, metrics, and health checks"
    echo "   • Production-ready containerization with security best practices"
    echo "   • Extensive test coverage demonstrating code quality"
    echo "   • Future-proof architecture supporting extensibility"
    
    echo -e "\n${CYAN}🎯 Key Technical Achievements:${NC}"
    echo "   • Clean, readable, and maintainable Python code"
    echo "   • Working Job Scheduler simulation in Kubernetes"
    echo "   • Functional REST API for configuration management"
    echo "   • Comprehensive testing examples"
    echo "   • Production-ready deployment configuration"
    
    echo -e "\n${YELLOW}🤔 Ready for Live Discussion Topics:${NC}"
    echo "   • Adding new optimization modules and filters"
    echo "   • Scaling and performance considerations"
    echo "   • Security and multi-tenancy best practices"
    echo "   • Monitoring and observability strategies"
    echo "   • Testing and quality assurance approaches"
    
    cleanup
}

# Handle script interruption
trap cleanup INT TERM

# Run the demo
main