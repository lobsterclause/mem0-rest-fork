#!/bin/bash

# Default values
DOCKER=false
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--docker)
            DOCKER=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to run tests locally
run_local_tests() {
    # Create and activate virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    pip install -r test_requirements.txt
    
    # Build test command
    TEST_CMD="pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=src --cov-report=xml --cov-report=html"
    fi
    
    if [ ! -z "$SPECIFIC_TEST" ]; then
        TEST_CMD="$TEST_CMD $SPECIFIC_TEST"
    fi
    
    # Run tests
    echo "Running tests..."
    $TEST_CMD
    
    # Deactivate virtual environment
    deactivate
}

# Function to run tests in Docker
run_docker_tests() {
    # Build test command
    TEST_CMD="pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=src --cov-report=xml --cov-report=html"
    fi
    
    if [ ! -z "$SPECIFIC_TEST" ]; then
        TEST_CMD="$TEST_CMD $SPECIFIC_TEST"
    fi
    
    # Build test image
    echo "Building test Docker image..."
    docker build -f test.Dockerfile -t mem0-rest-test .
    
    # Run tests in container
    echo "Running tests in Docker..."
    docker run --rm \
        -v "$(pwd)/test_output:/app/test_output" \
        -v "$(pwd)/htmlcov:/app/htmlcov" \
        -v "$(pwd)/coverage.xml:/app/coverage.xml" \
        mem0-rest-test $TEST_CMD
}

# Main execution
echo "Starting test execution..."

if [ "$DOCKER" = true ]; then
    run_docker_tests
else
    run_local_tests
fi

# Check test results
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "Tests completed successfully!"
else
    echo "Tests failed with exit code $EXIT_CODE"
fi

# Open coverage report if generated
if [ "$COVERAGE" = true ] && [ -f "htmlcov/index.html" ]; then
    echo "Opening coverage report..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open htmlcov/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open htmlcov/index.html
    elif [[ "$OSTYPE" == "msys" ]]; then
        start htmlcov/index.html
    fi
fi

exit $EXIT_CODE
