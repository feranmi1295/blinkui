cmake_minimum_required(VERSION 3.22)
project(blinkui_bridge)

set(RUNTIME_DIR /home/abiodunidris/Desktop/BlinkUI/blinkui/runtime)

add_library(
    blinkui_bridge
    SHARED
    bridge.c
    ${RUNTIME_DIR}/core/blinkui.c
    ${RUNTIME_DIR}/core/reconciler.c
    ${RUNTIME_DIR}/core/events.c
    ${RUNTIME_DIR}/animation/animation.c
)

target_include_directories(blinkui_bridge PRIVATE
    ${RUNTIME_DIR}/core
    ${RUNTIME_DIR}/animation
)

target_compile_definitions(blinkui_bridge PRIVATE
    ANDROID
    NO_PYTHON
)

target_link_libraries(blinkui_bridge
    android
    log
    m
)
