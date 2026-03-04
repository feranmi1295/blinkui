cmake_minimum_required(VERSION 3.22)
project(blinkui_bridge)

# ── include BlinkUI C runtime sources ──
set(RUNTIME_DIR ${CMAKE_SOURCE_DIR}/../../../../runtime)

set(BLINKUI_SOURCES
    ${RUNTIME_DIR}/core/blinkui.c
    ${RUNTIME_DIR}/core/reconciler.c
    ${RUNTIME_DIR}/core/events.c
    ${RUNTIME_DIR}/animation/animation.c
    bridge.c
)

# ── build shared library (.so) ──
# Android loads .so files at runtime
add_library(
    blinkui_bridge
    SHARED
    ${BLINKUI_SOURCES}
)

# ── include directories ──
target_include_directories(blinkui_bridge PRIVATE
    ${RUNTIME_DIR}/core
    ${RUNTIME_DIR}/animation
)

# ── link Android system libraries ──
target_link_libraries(blinkui_bridge
    android     # Android NDK
    log         # __android_log_print
    m           # math
)