# Project-Inverter-with-CCS-C2000

## Overview
This project is an inverter control system designed for the Texas Instruments TMS320F28335 DSP microcontroller, developed using Code Composer Studio (CCS).

## Hardware Platform
- **Microcontroller**: TMS320F28335 (C2000 DSP)
- **Development Environment**: Code Composer Studio (CCS)

## Project Structure

```
.
├── src/           # Source code files (.c)
├── include/       # Header files (.h)
├── lib/           # Libraries and dependencies
├── doc/           # Documentation
├── config/        # Configuration files (linker scripts, etc.)
└── README.md      # This file
```

### Directory Details

- **src/**: Contains all C source code files including main application, peripheral drivers, control algorithms, and ISRs.
- **include/**: Contains header files with function declarations, macros, type definitions, and register definitions.
- **lib/**: Contains TI DSP libraries, IQmath libraries, and other third-party dependencies.
- **doc/**: Project documentation including design specs, schematics, and user manuals.
- **config/**: Configuration files such as linker command files (.cmd) and memory configurations.

## Getting Started

### Prerequisites
- Code Composer Studio (CCS) v10.0 or higher
- TMS320F28335 controlCARD or custom hardware
- C2000Ware SDK (optional, for additional libraries and examples)

### Building the Project
1. Open Code Composer Studio
2. Import this project into CCS workspace
3. Configure the build settings for F28335 target
4. Build the project (Project → Build All)
5. Load and run on the target hardware

## Development

This project is structured to facilitate development of inverter control algorithms for the F28335 DSP platform.

## License

[Add license information here]

## Contributors

[Add contributor information here]