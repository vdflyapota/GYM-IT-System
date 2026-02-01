# Load Testing Report

## Tool Used
- Custom Python load testing scripts

## Test Scenario
- Simulated up to 1,000 concurrent users accessing the API Gateway and all core microservices.
- Tested both read and write operations where applicable to mimic realistic usage patterns.

## Results
- The system remained stable under full load.
- No service crashes or errors were observed during testing.
- Average response time across services stayed well within acceptable limits (<2 seconds for key endpoints).
- CPU, memory, and database usage remained within safe operating thresholds.

## Conclusion
- The system demonstrates sufficient scalability and performance for expected production usage.
- The tests confirm that the Notification Service, Activity Dashboard, and all core services can handle peak load reliably.
