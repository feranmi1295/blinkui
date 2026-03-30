package com.blinkui;

public class BlinkUIBridge {

    static {
        System.loadLibrary("blinkui_bridge");
    }

    public native String nativeInit();
    public native void   nativeRender(String treeJson);
    public native void   nativeFireEvent(int nodeId, int eventType, float x, float y);
    public native void   nativeTick(long deltaMs);
    public native String nativeGetVersion();
    public native String nativeGetInitialTree();
    public native void   nativeSetActivity(Object activity);

    private static BlinkUIBridge instance;
    public static BlinkUIBridge getInstance() {
        if (instance == null) instance = new BlinkUIBridge();
        return instance;
    }

    public static final int EVENT_TAP        = 0;
    public static final int EVENT_LONG_PRESS = 1;
}
