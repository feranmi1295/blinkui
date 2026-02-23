cmake_minimum_required(VERSION 3.20)
project(blinkui_runtime C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

find_package(Python3 REQUIRED COMPONENTS Development.Embed)

set(SOURCES
    core/blinkui.c
    core/node.c
    core/reconciler.c
    core/events.c
    python/py_host.c
    animation/animation.c
)

add_library(blinkui_runtime STATIC ${SOURCES})

target_include_directories(blinkui_runtime PUBLIC
    ${Python3_INCLUDE_DIRS}
    core/
    python/
    animation/
)

target_link_libraries(blinkui_runtime PUBLIC
    ${Python3_LIBRARIES}
    m
)

add_executable(blinkui_test ${SOURCES})

target_include_directories(blinkui_test PUBLIC
    ${Python3_INCLUDE_DIRS}
    core/
    python/
    animation/
)

target_link_libraries(blinkui_test
    Python3::Python
    m
)