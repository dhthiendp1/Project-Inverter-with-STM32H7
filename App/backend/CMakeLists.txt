cmake_minimum_minimum_required(VERSION 3.15)
project(FOC_Backend_STM32 VERSION 1.0.0 LANGUAGES CXX)

# Sử dụng chuẩn C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Khai báo đường dẫn thư mục include
include_directories(include)

# Tìm các thư viện (Giả sử bạn cài qua vcpkg hoặc MSYS2)
find_package(cppzmq CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

# Lấy tất cả file nguồn
file(GLOB_RECURSE SRC_FILES "src/*.cpp")

# Tạo file thực thi
add_executable(${PROJECT_NAME} ${SRC_FILES})

# Link thư viện
target_link_libraries(${PROJECT_NAME} PRIVATE cppzmq nlohmann_json::nlohmann_json)