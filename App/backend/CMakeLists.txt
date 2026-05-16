cmake_minimum_required(VERSION 3.15)
project(FOC_Backend_STM32 VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
add_definitions(-DWIN32_LEAN_AND_MEAN)

include_directories(include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/stlink/include/stlink)
include_directories(${CMAKE_SOURCE_DIR}/third_party/libusb/include/libusb-1.0)

find_package(cppzmq CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

file(GLOB_RECURSE SRC_FILES "src/*.cpp")
add_executable(${PROJECT_NAME} ${SRC_FILES})

target_link_libraries(${PROJECT_NAME} PRIVATE 
    cppzmq 
    nlohmann_json::nlohmann_json 
    ${CMAKE_SOURCE_DIR}/third_party/stlink/lib/libstlink.dll.a
    ${CMAKE_SOURCE_DIR}/third_party/libusb/lib/libusb-1.0.dll.a
)

add_compile_definitions(FRONTEND_JSON_PATH="${CMAKE_CURRENT_SOURCE_DIR}/../frontend/gui/block_mapping.json")