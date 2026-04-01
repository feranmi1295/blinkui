cmake_minimum_required(VERSION 3.22)
project(blinkui_bridge)

set(RUNTIME_DIR /home/abiodunidris/Desktop/BlinkUI/blinkui/runtime)
set(GENERATED_DIR /home/abiodunidris/Desktop/BlinkUI/blinkui/testapp/.blink/generated/c)

add_library(
    blinkui_bridge
    SHARED
    app_bridge.c
    ${GENERATED_DIR}/global_store.c
    ${GENERATED_DIR}/HomeScreen.c
    ${GENERATED_DIR}/DetailScreen.c
    ${RUNTIME_DIR}/core/components.c
    ${RUNTIME_DIR}/core/reconciler.c
    ${RUNTIME_DIR}/core/events.c
    ${RUNTIME_DIR}/animation/animation.c
)

target_include_directories(blinkui_bridge PRIVATE
    ${RUNTIME_DIR}/core
    ${RUNTIME_DIR}/animation
    ${GENERATED_DIR}
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
