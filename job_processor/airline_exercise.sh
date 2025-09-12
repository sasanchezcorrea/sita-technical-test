#!/bin/bash

# Multi-Tenant Airline Exercise - 10 Airlines Demo
# This script demonstrates the multi-tenant capabilities of the OptiFlight Job Processor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}Multi-Tenant Airline Exercise - 10 Airlines Demo${NC}"
echo "============================================================"

BASE_URL="http://localhost:8000"

# Function to print colored output
print_step() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_info() {
    echo -e "${CYAN}[INFO] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if service is running
check_service() {
    print_info "Checking if OptiFlight Job Processor is running..."
    
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        print_step "Service is running at $BASE_URL"
    else
        print_error "Service is not running. Please start it first:"
        echo "  Docker: docker run -d -p 8000:8000 optiflight-coordinator:latest"
        echo "  Local:  ./run_job_processor.sh start"
        exit 1
    fi
}

# Create airline configuration
create_airline_config() {
    local airline="$1"
    local config="$2"
    
    print_info "Creating configuration for $airline..."
    
    response=$(curl -s -X POST "$BASE_URL/api/v1/config/tenants" \
        -H "Content-Type: application/json" \
        -d "$config")
    
    if echo "$response" | grep -q "created/updated successfully"; then
        print_step "$airline configuration created"
    else
        print_error "Failed to create $airline configuration"
        echo "$response"
    fi
}

# Create all airline configurations
create_airline_configs() {
    print_step "Creating configurations for 10 airlines..."
    
    # Lufthansa - Premium European carrier
    create_airline_config "LUFTHANSA" '{
        "airline":"LUFTHANSA",
        "max_parallel_executions":15,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240}
        ],
        "rate_limit_per_minute":1500,
        "priority":1
    }'
    
    # Emirates - Premium long-haul carrier
    create_airline_config "EMIRATES" '{
        "airline":"EMIRATES",
        "max_parallel_executions":20,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"weather_optimizer","image":"sita/weather-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":180}
        ],
        "rate_limit_per_minute":2000,
        "priority":1
    }'
    
    # American Airlines - Large US domestic
    create_airline_config "AMERICAN" '{
        "airline":"AMERICAN",
        "max_parallel_executions":12,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"cost_optimizer","image":"sita/cost-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":200}
        ],
        "rate_limit_per_minute":1200,
        "priority":2
    }'
    
    # British Airways - Global network
    create_airline_config "BRITISH" '{
        "airline":"BRITISH",
        "max_parallel_executions":18,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"slot_optimizer","image":"sita/slot-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":150}
        ],
        "rate_limit_per_minute":1800,
        "priority":1
    }'
    
    # Qantas - Long-haul specialist
    create_airline_config "QANTAS" '{
        "airline":"QANTAS",
        "max_parallel_executions":10,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"long_haul_optimizer","image":"sita/long-haul-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":400}
        ],
        "rate_limit_per_minute":800,
        "priority":2
    }'
    
    # Air France - Hub operations
    create_airline_config "AIR_FRANCE" '{
        "airline":"AIR_FRANCE",
        "max_parallel_executions":14,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"hub_optimizer","image":"sita/hub-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":180}
        ],
        "rate_limit_per_minute":1400,
        "priority":1
    }'
    
    # Singapore Airlines - Premium service
    create_airline_config "SINGAPORE" '{
        "airline":"SINGAPORE",
        "max_parallel_executions":16,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"premium_optimizer","image":"sita/premium-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":220}
        ],
        "rate_limit_per_minute":1600,
        "priority":1
    }'
    
    # Delta - US domestic focus
    create_airline_config "DELTA" '{
        "airline":"DELTA",
        "max_parallel_executions":13,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"domestic_optimizer","image":"sita/domestic-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":180}
        ],
        "rate_limit_per_minute":1300,
        "priority":2
    }'
    
    # Cathay Pacific - Cargo specialist
    create_airline_config "CATHAY" '{
        "airline":"CATHAY",
        "max_parallel_executions":11,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"cargo_optimizer","image":"sita/cargo-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":160}
        ],
        "rate_limit_per_minute":1100,
        "priority":2
    }'
    
    # United - Network carrier
    create_airline_config "UNITED" '{
        "airline":"UNITED",
        "max_parallel_executions":17,
        "active_modules":[
            {"name":"route_optimizer","image":"sita/route-optimizer","version":"v1.2.0","enabled":true,"timeout_seconds":300},
            {"name":"fuel_optimizer","image":"sita/fuel-optimizer","version":"v1.1.0","enabled":true,"timeout_seconds":240},
            {"name":"network_optimizer","image":"sita/network-optimizer","version":"v1.0.0","enabled":true,"timeout_seconds":250}
        ],
        "rate_limit_per_minute":1700,
        "priority":1
    }'
}

# Send position report for airline
send_position_report() {
    local airline="$1"
    local flight_id="$2"
    local aircraft_type="$3"
    local registration="$4"
    local latitude="$5"
    local longitude="$6"
    
    local json_data=$(cat <<EOF
{
    "airline": "$airline",
    "flight_id": "$flight_id",
    "aircraft_type": "$aircraft_type",
    "registration": "$registration",
    "latitude": $latitude,
    "longitude": $longitude
}
EOF
)
    
    response=$(curl -s -X POST "$BASE_URL/api/v1/events/position-report" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    if echo "$response" | grep -q "processed successfully"; then
        jobs_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('jobs', [])))" 2>/dev/null || echo "0")
        print_step "  $flight_id: $jobs_count jobs submitted"
        return 0
    else
        print_error "  Failed to process $flight_id"
        return 1
    fi
}

# Generate realistic flight events
generate_flight_events() {
    print_step "Generating flight events for all airlines..."
    
    total_events=0
    
    # Lufthansa flights
    print_info "Generating events for LUFTHANSA..."
    send_position_report "LUFTHANSA" "LH401" "A350" "D-AIXA" 52.5200 13.4050 && ((total_events++))
    send_position_report "LUFTHANSA" "LH440" "A380" "D-AIMB" 53.6333 9.9833 && ((total_events++))
    send_position_report "LUFTHANSA" "LH500" "B747" "D-ABYA" 50.1109 8.6821 && ((total_events++))
    
    # Emirates flights
    print_info "Generating events for EMIRATES..."
    send_position_report "EMIRATES" "EK202" "A380" "A6-EUA" 25.2532 55.3657 && ((total_events++))
    send_position_report "EMIRATES" "EK215" "B777" "A6-EBX" 25.2048 55.2708 && ((total_events++))
    send_position_report "EMIRATES" "EK225" "A350" "A6-EXA" 24.4539 54.3773 && ((total_events++))
    
    # American flights
    print_info "Generating events for AMERICAN..."
    send_position_report "AMERICAN" "AA100" "B737" "N123AA" 32.8998 -97.0403 && ((total_events++))
    send_position_report "AMERICAN" "AA150" "A321" "N456AA" 33.9425 -118.4081 && ((total_events++))
    send_position_report "AMERICAN" "AA200" "B787" "N789AA" 40.6892 -74.1745 && ((total_events++))
    
    # British Airways flights
    print_info "Generating events for BRITISH..."
    send_position_report "BRITISH" "BA100" "A350" "G-XWBA" 51.4700 -0.4543 && ((total_events++))
    send_position_report "BRITISH" "BA150" "B787" "G-ZBKA" 51.1481 -0.1903 && ((total_events++))
    send_position_report "BRITISH" "BA200" "A380" "G-XLEA" 53.3537 -2.2750 && ((total_events++))
    
    # Qantas flights
    print_info "Generating events for QANTAS..."
    send_position_report "QANTAS" "QF1" "A380" "VH-OQA" -33.9399 151.1753 && ((total_events++))
    send_position_report "QANTAS" "QF7" "B787" "VH-ZNA" -37.6690 144.8410 && ((total_events++))
    send_position_report "QANTAS" "QF25" "A330" "VH-QPD" -31.9403 115.9669 && ((total_events++))
    
    # Air France flights
    print_info "Generating events for AIR_FRANCE..."
    send_position_report "AIR_FRANCE" "AF447" "A350" "F-HTYA" 49.0097 2.5479 && ((total_events++))
    send_position_report "AIR_FRANCE" "AF83" "B777" "F-GSQA" 45.7256 5.0811 && ((total_events++))
    send_position_report "AIR_FRANCE" "AF1180" "A320" "F-HEPD" 43.6426 1.3678 && ((total_events++))
    
    # Singapore Airlines flights
    print_info "Generating events for SINGAPORE..."
    send_position_report "SINGAPORE" "SQ231" "A380" "9V-SKA" 1.3644 103.9915 && ((total_events++))
    send_position_report "SINGAPORE" "SQ317" "B787" "9V-OFA" 1.3521 103.8198 && ((total_events++))
    send_position_report "SINGAPORE" "SQ25" "A350" "9V-SMA" 22.3193 114.1694 && ((total_events++))
    
    # Delta flights
    print_info "Generating events for DELTA..."
    send_position_report "DELTA" "DL67" "A350" "N502DN" 33.6407 -84.4277 && ((total_events++))
    send_position_report "DELTA" "DL159" "B737" "N3739P" 40.7769 -73.8740 && ((total_events++))
    send_position_report "DELTA" "DL201" "A321" "N301DN" 42.2140 -83.3534 && ((total_events++))
    
    # Cathay Pacific flights
    print_info "Generating events for CATHAY..."
    send_position_report "CATHAY" "CX888" "A350" "B-LRA" 22.3080 113.9185 && ((total_events++))
    send_position_report "CATHAY" "CX251" "B777" "B-KQA" 22.5431 113.9914 && ((total_events++))
    send_position_report "CATHAY" "CX100" "A330" "B-LAD" 23.3924 113.2988 && ((total_events++))
    
    # United flights
    print_info "Generating events for UNITED..."
    send_position_report "UNITED" "UA1" "B787" "N26966" 41.9742 -87.9073 && ((total_events++))
    send_position_report "UNITED" "UA15" "A350" "N35953" 37.6213 -122.3790 && ((total_events++))
    send_position_report "UNITED" "UA857" "B737" "N37409" 39.8561 -104.6737 && ((total_events++))
    
    print_step "Generated $total_events flight events across all airlines"
}

# Send flight plan
send_flight_plan() {
    local json_data="$1"
    local flight_id="$2"
    
    response=$(curl -s -X POST "$BASE_URL/api/v1/events/flight-plan" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    if echo "$response" | grep -q "processed successfully"; then
        jobs_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('jobs', [])))" 2>/dev/null || echo "0")
        print_step "  $flight_id: $jobs_count jobs submitted"
    else
        print_error "  Failed to process flight plan for $flight_id"
    fi
}

# Generate flight plan events
generate_flight_plans() {
    print_step "Generating flight plan events..."
    
    # Lufthansa flight plan
    print_info "Creating flight plan for LUFTHANSA..."
    send_flight_plan '{
        "flight_id":"LH2054",
        "airline":"LUFTHANSA",
        "aircraft_type":"A350",
        "registration":"D-AIXB",
        "route":[
            {"latitude":52.5200,"longitude":13.4050},
            {"latitude":40.7128,"longitude":-74.0060}
        ],
        "departure_airport":"FRA",
        "arrival_airport":"JFK",
        "estimated_duration":480
    }' "LH2054"
    
    # Emirates flight plan
    print_info "Creating flight plan for EMIRATES..."
    send_flight_plan '{
        "flight_id":"EK205",
        "airline":"EMIRATES",
        "aircraft_type":"A380",
        "registration":"A6-EUB",
        "route":[
            {"latitude":25.2532,"longitude":55.3657},
            {"latitude":51.4700,"longitude":-0.4543}
        ],
        "departure_airport":"DXB",
        "arrival_airport":"LHR",
        "estimated_duration":420
    }' "EK205"
    
    # American flight plan
    print_info "Creating flight plan for AMERICAN..."
    send_flight_plan '{
        "flight_id":"AA50",
        "airline":"AMERICAN",
        "aircraft_type":"B787",
        "registration":"N801AA",
        "route":[
            {"latitude":40.6892,"longitude":-74.1745},
            {"latitude":34.0522,"longitude":-118.2437}
        ],
        "departure_airport":"JFK",
        "arrival_airport":"LAX",
        "estimated_duration":360
    }' "AA50"
    
    # British Airways flight plan
    print_info "Creating flight plan for BRITISH..."
    send_flight_plan '{
        "flight_id":"BA1",
        "airline":"BRITISH",
        "aircraft_type":"A350",
        "registration":"G-XWBB",
        "route":[
            {"latitude":51.4700,"longitude":-0.4543},
            {"latitude":40.6892,"longitude":-74.1745}
        ],
        "departure_airport":"LHR",
        "arrival_airport":"JFK",
        "estimated_duration":480
    }' "BA1"
    
    # Qantas flight plan
    print_info "Creating flight plan for QANTAS..."
    send_flight_plan '{
        "flight_id":"QF12",
        "airline":"QANTAS",
        "aircraft_type":"A380",
        "registration":"VH-OQB",
        "route":[
            {"latitude":-33.9399,"longitude":151.1753},
            {"latitude":34.0522,"longitude":-118.2437}
        ],
        "departure_airport":"SYD",
        "arrival_airport":"LAX",
        "estimated_duration":840
    }' "QF12"
}

# Monitor job execution
monitor_jobs() {
    print_step "Monitoring job execution..."
    
    print_info "Waiting for jobs to complete..."
    sleep 8
    
    echo ""
    print_step "Job Status Summary:"
    echo ""
    
    # Get overall job statistics
    response=$(curl -s "$BASE_URL/api/v1/jobs")
    
    total_jobs=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
    print_info "Total jobs processed: $total_jobs"
    
    # Show jobs by status
    for status in "running" "completed" "failed"; do
        status_response=$(curl -s "$BASE_URL/api/v1/jobs?status_filter=$status")
        count=$(echo "$status_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
        
        case $status in
            "running") echo -e "  ${YELLOW}Running: $count${NC}" ;;
            "completed") echo -e "  ${GREEN}Completed: $count${NC}" ;;
            "failed") echo -e "  ${RED}Failed: $count${NC}" ;;
        esac
    done
    
    echo ""
    
    # Show jobs by airline
    print_step "Jobs by Airline:"
    echo ""
    
    airlines=("LUFTHANSA" "EMIRATES" "AMERICAN" "BRITISH" "QANTAS" "AIR_FRANCE" "SINGAPORE" "DELTA" "CATHAY" "UNITED")
    
    for airline in "${airlines[@]}"; do
        airline_response=$(curl -s "$BASE_URL/api/v1/jobs?airline=$airline")
        count=$(echo "$airline_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
        
        if [ "$count" -gt 0 ]; then
            # Count completed jobs
            completed=$(echo "$airline_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
completed = sum(1 for job in data['jobs'] if job.get('status') == 'completed')
print(completed)
" 2>/dev/null || echo "0")
            
            echo -e "  ${CYAN}$airline: $count jobs ($completed completed)${NC}"
        fi
    done
}

# Show system metrics
show_metrics() {
    print_step "System Metrics:"
    echo ""
    
    metrics=$(curl -s "$BASE_URL/metrics/summary")
    
    echo "$metrics" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  Active Jobs: {data.get('active_jobs', 0)}\")
print(f\"  Completed (24h): {data.get('completed_jobs_24h', 0)}\")
print(f\"  Failed (24h): {data.get('failed_jobs_24h', 0)}\")
print(f\"  Average Duration: {data.get('average_job_duration', 0):.1f}s\")
print(f\"  Tenants: {data.get('tenants_count', 0)}\")
print(f\"  Memory Usage: {data.get('memory_usage_percent', 0):.1f}%\")
print(f\"  CPU Usage: {data.get('cpu_usage_percent', 0):.1f}%\")
" 2>/dev/null
}

# List all tenant configurations
show_configurations() {
    print_step "Tenant Configurations:"
    echo ""
    
    configs=$(curl -s "$BASE_URL/api/v1/config/tenants")
    
    echo "$configs" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for airline, config in data.get('configurations', {}).items():
    modules = config.get('active_modules', [])
    rate_limit = config.get('rate_limit_per_minute', 0)
    max_parallel = config.get('max_parallel_executions', 0)
    print(f\"  {airline}: {len(modules)} modules, {max_parallel} max parallel, {rate_limit}/min rate limit\")
" 2>/dev/null
}

# Cleanup function
cleanup() {
    print_warning "Cleaning up demo data..."
    
    airlines=("LUFTHANSA" "EMIRATES" "AMERICAN" "BRITISH" "QANTAS" "AIR_FRANCE" "SINGAPORE" "DELTA" "CATHAY" "UNITED")
    
    for airline in "${airlines[@]}"; do
        curl -s -X DELETE "$BASE_URL/api/v1/config/tenants/$airline" > /dev/null
        print_info "Removed $airline configuration"
    done
    
    print_step "Demo cleanup completed"
}

# Main execution
main() {
    case "${1:-demo}" in
        "demo"|"")
            check_service
            create_airline_configs
            echo ""
            generate_flight_events
            echo ""
            generate_flight_plans
            echo ""
            monitor_jobs
            echo ""
            show_metrics
            echo ""
            show_configurations
            ;;
        "cleanup")
            cleanup
            ;;
        "monitor")
            check_service
            monitor_jobs
            show_metrics
            ;;
        "configs")
            check_service
            show_configurations
            ;;
        *)
            echo "Usage: $0 [demo|cleanup|monitor|configs]"
            echo ""
            echo "Commands:"
            echo "  demo     - Run complete 10-airline demo (default)"
            echo "  cleanup  - Remove all demo airline configurations"
            echo "  monitor  - Show current job status and metrics"
            echo "  configs  - Show current tenant configurations"
            ;;
    esac
}

main "$@"