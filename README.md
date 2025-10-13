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