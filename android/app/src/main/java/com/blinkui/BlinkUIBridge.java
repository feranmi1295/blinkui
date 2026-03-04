package com.blinkui;

/**
 * JNI bridge between Java/Android and the BlinkUI C runtime.
 * All communication between Python->C->Android goes through here.
 */
public class BlinkUIBridge {

    // Load the compiled C library
    static {
        System.loadLibrary("blinkui_bridge");
    }

    // ── Native methods — implemented in bridge.c ──

    /** Initialize the BlinkUI C runtime */
    public native String nativeInit();

    /** Render a component tree from JSON */
    public native void nativeRender(String treeJson);

    /** Fire an event from a native view */
    public native void nativeFireEvent(int nodeId, int eventType, float x, float y);

    /** Advance animations by delta milliseconds */
    public native void nativeTick(long deltaMs);

    /** Get C runtime version */
    public native String nativeGetVersion();

    // ── Singleton ──
    private static BlinkUIBridge instance;

    public static BlinkUIBridge getInstance() {
        if (instance == null) {
            instance = new BlinkUIBridge();
        }
        return instance;
    }

    // ── Event types matching events.h ──
    public static final int EVENT_TAP         = 0;
    public static final int EVENT_LONG_PRESS  = 1;
    public static final int EVENT_SWIPE_LEFT  = 2;
    public static final int EVENT_SWIPE_RIGHT = 3;
    public static final int EVENT_SCROLL      = 8;
}