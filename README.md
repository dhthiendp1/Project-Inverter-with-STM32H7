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

#### Summarry Commit

- **feat**  	Tính năng mới: Thêm một chức năng mới.
- **fix**	    Sửa lỗi: Sửa một lỗi đang tồn tại.
- **refactor**	Tái cấu trúc: Dọn dẹp, tối ưu cấu trúc code mà không thay đổi hành vi.	Đổi tên biến, tách hàm lớn thành hàm nhỏ.
- **docs**	    Tài liệu: Thêm/sửa đổi file tài liệu (README.md, User Manual).
- **style**	    Định dạng code: Sửa lỗi định dạng (dấu cách, dấu chấm phẩy, xuống dòng).
- **test**	    Thêm/sửa code test
- **chore**	    Tác vụ khác: Cập nhật công cụ, cấu hình Git, không liên quan đến code chức năng. Cập nhật file .gitignore, sửa file dự án CCS.