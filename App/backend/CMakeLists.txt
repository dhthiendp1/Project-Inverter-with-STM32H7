cmake_minimum_required(VERSION 3.15)
project(FOC_Backend_STM32 VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Sửa lỗi xung đột thư viện mạng trên Windows
add_definitions(-DWIN32_LEAN_AND_MEAN)

include_directories(include)

# Visual Studio sẽ dùng vcpkg để tự tìm 2 thư viện này
find_package(cppzmq CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

file(GLOB_RECURSE SRC_FILES "src/*.cpp")

add_executable(${PROJECT_NAME} ${SRC_FILES})

target_link_libraries(${PROJECT_NAME} PRIVATE cppzmq nlohmann_json::nlohmann_json)