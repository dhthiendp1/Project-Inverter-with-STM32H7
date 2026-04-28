# Project-Inverter-with-STM32H7

## Overview
This project is an inverter control system designed for the Core STM32H732ZGT6.

## Hardware Platform
- **Microcontroller**: STM32H732ZGT6
-  **Developed**: CubeMX, CubeIDE, CubePrograming 

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

## Directory Details

```
.
- **src/**:     # Chứa file .c
- **include/**: # Chứa file .h tự định nghĩa.
- **lib/**:     # Thư viện bên thứ 3 (math.h, lib từ DSP).
- **doc/**:     # Tài liệu
- **config/**:  # Tệp .cmd hệ thống DSP
```
## Summarry Commit

```
.
- feat  	# Thêm một chức năng mới.
- fix       # Sửa lỗi Sửa một lỗi đang tồn tại.
- refactor	# Tái cấu trúc: Dọn dẹp, tối ưu cấu trúc code mà không thay đổi hành vi. Đổi tên biến, tách hàm lớn thành hàm nhỏ.
- docs      # Tài liệu: Thêm/sửa đổi file tài liệu (README.md, User Manual).
- style	    # Định dạng code: Sửa lỗi định dạng (dấu cách, dấu chấm phẩy, xuống dòng).
- test      # Thêm/sửa code khi test
- chore     # Tác vụ khác: Cập nhật công cụ, cấu hình Git, không liên quan đến code chức năng. Cập nhật file .gitignore, sửa file dự án CCS.
```
