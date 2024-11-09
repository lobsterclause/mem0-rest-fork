# Graph Memory Testing Environment

This directory contains a complete test environment for verifying mem0's graph memory functionality. The test setup exactly replicates the example from the official documentation.

## Quick Start

1. Copy and configure environment:
   ```bash
   cd sw/mem0-rest-fork
   cp sample.test.env test.env
   # Edit test.env with your OpenAI API key and other settings
   ```

2. Run tests:
   ```bash
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

3. Check results in test_output/ directory

## Components

### Core Files
- `test_graph_memory.py` - Test script that replicates the example
- `test_requirements.txt` - Python dependencies with exact versions
- `test.Dockerfile` - Container setup with visualization support
- `test-docker-compose.yml` - Service orchestration
- `sample.test.env` - Environment variable template
- `run_tests.sh` - Test execution script

### Documentation
- `TEST_README.md` (this file) - Main documentation
- `test_output/README.md` - Visualization guide

### Output
- `test_output/` - Directory for graph visualizations
  - Numbered PNG files showing graph evolution
  - See test_output/README.md for details

## Prerequisites

1. Docker and Docker Compose installed
2. At least 4GB of available memory
3. OpenAI API key

## Configuration

### Environment Setup
1. Copy the sample environment file:
   ```bash
   cp sample.test.env test.env
   ```

2. Edit test.env and set:
   - OPENAI_API_KEY (required)
   - Other optional settings as needed

### Environment Variables
All configuration options in test.env:
- OpenAI settings (API key, model)
- Neo4j connection details
- Test parameters
- Visualization settings
- Optional TEST_RUN_ID for unique test runs

### Neo4j Setup
- Version: 5.15.0
- APOC plugins enabled
- Memory settings optimized
- Persistent storage configured
- Custom ports to avoid conflicts:
  - HTTP: 7475 (instead of 7474)
  - Bolt: 7688 (instead of 7687)

## Running the Tests

1. Quick Start:
   ```bash
   cd sw/mem0-rest-fork
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

2. With Custom Run ID:
   ```bash
   TEST_RUN_ID=custom_run_1 ./run_tests.sh
   ```

3. Manual Steps:
   ```bash
   # Build and start containers
   docker-compose -f test-docker-compose.yml --env-file test.env up --build

   # View logs
   docker-compose -f test-docker-compose.yml logs -f

   # Clean up
   docker-compose -f test-docker-compose.yml down -v
   ```

## Test Sequence

1. Environment Setup:
   - Neo4j database starts
   - APOC plugins load
   - Python environment prepares

2. Memory Operations:
   - Clear existing memories
   - Add test memories one by one
   - Generate visualizations
   - Test search functionality

3. Output Generation:
   - Graph visualizations saved with timestamps
   - Operation results logged
   - Search results displayed

## Visualization Guide

See test_output/README.md for:
- File naming convention
- Graph element descriptions
- Expected progression
- Interpretation guide
- Troubleshooting tips

## Troubleshooting

1. Container Issues:
   ```bash
   # Check container status
   docker-compose -f test-docker-compose.yml ps

   # View detailed logs
   docker-compose -f test-docker-compose.yml logs -f
   ```

2. Neo4j Issues:
   - Check Neo4j logs for APOC plugin status
   - Verify memory settings
   - Check connection details in test.env
   - Verify ports 7475 and 7688 are available

3. Python Issues:
   - Verify dependencies in test_requirements.txt
   - Check matplotlib system dependencies
   - Review Python environment in Dockerfile

4. Visualization Issues:
   - Check test_output directory permissions
   - Verify matplotlib backend setting
   - Review container logs for errors

## Cleaning Up

```bash
# Remove containers and volumes
docker-compose -f test-docker-compose.yml down -v

# Clean test output
rm -rf test_output/*.png
```

## Next Steps

After successful testing:
1. Review graph visualizations in test_output/
2. Verify memory operations worked as expected
3. Check search functionality results
4. Plan REST API integration based on findings

## References

- [Mem0 Documentation](https://docs.mem0.ai/open-source/graph-memory)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Original Example](https://colab.research.google.com/drive/1PfIGVHnliIlG2v8cx0g45TF0US-jRPZ1)
