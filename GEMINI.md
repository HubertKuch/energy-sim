# Solar Project: Advanced Simulation Engine

This project is a high-fidelity solar energy simulation engine that combines a Go-based API gateway with a Python-based physics solver using the `pvlib` library.

## Architecture
- **Gateway (Go)**:
    - `main.go`: Entry point and dependency wiring.
    - `internal/simulation/`: Core business logic, HTTP handlers, and gRPC client orchestration.
- **Solver (Python)**:
    - `engine.py`: High-level entry point (gRPC and Domain).
    - `domain/`: Core physical entities (`SolarPanel`, `SolarBattery`, `SolarSystem`, etc.).
    - `parsers/`: Specialized translators for Protobuf, Weather, and Location data.
- **Protocol**: gRPC with Protobuf for efficient cross-language communication.

## Core Capabilities
- **SolarArray Modeling**: Supports 2D layouts (horizontal strings and vertical modules in series).
- **Physical Parameters**: Factors in Location (GPS), Surface Tilt, Azimuth, and Temperature coefficients.
- **BESS (Battery Energy Storage System)**: Simulates self-consumption, battery logic (charge/discharge limits, efficiency), and grid interactions.
- **Load Profile support**: Simulates real-world consumption patterns to calculate net grid impact.

## Development Workflows
- **Justfile**: Use `just test` for unit tests and `just integration-test` for full system verification.
- **Modularity**: Adheres to SOLID and KISS principles with clear separation between protocol, business logic, and physics.

## Roadmap (Next Steps)
1. **Economic Analysis Layer**: Implement Net Metering, ROI calculations, and LCOE (Levelized Cost of Energy).
2. **Multi-Orientation Support**: Allow systems with multiple arrays (e.g., East-West splits) connected to a single inverter.
3. **Real Weather Integration**: Replace procedural weather generation with TMY (Typical Meteorological Year) data or live API forecasts.
4. **Component Library**: Persistence layer for real-world panel and inverter specifications.
5. **Shading & Loss Models**: Account for environmental shading and wiring losses.
