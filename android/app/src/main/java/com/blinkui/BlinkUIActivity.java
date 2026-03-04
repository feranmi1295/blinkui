package com.blinkui;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.LinearLayout;

import org.json.JSONObject;

/**
 * The main Android Activity for BlinkUI apps.
 * Initializes the C runtime, starts Python,
 * and renders the component tree.
 */
public class BlinkUIActivity extends Activity {

    private static final String TAG       = "BlinkUI";
    private static final int    FRAME_MS  = 16; // 60fps

    private BlinkUIBridge    bridge;
    private ComponentFactory factory;
    private LinearLayout     rootView;
    private Handler          handler;
    private String           currentTree;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // ── init bridge ──
        bridge  = BlinkUIBridge.getInstance();
        factory = new ComponentFactory(this);
        handler = new Handler(Looper.getMainLooper());

        // ── create root view ──
        rootView = new LinearLayout(this);
        rootView.setOrientation(LinearLayout.VERTICAL);
        setContentView(rootView);

        // ── init C runtime ──
        String result = bridge.nativeInit();
        Log.i(TAG, result);

        // ── start animation loop ──
        startAnimationLoop();

        // ── render initial screen ──
        // In production this comes from Python via bk_py_call
        // For now render a test tree
        renderTestScreen();
    }

    /**
     * Called when Python produces a new component tree.
     * Runs on UI thread so Android views can be created.
     */
    public void renderTree(String treeJson) {
        handler.post(() -> {
            try {
                currentTree = treeJson;
                bridge.nativeRender(treeJson);

                JSONObject tree = new JSONObject(treeJson);
                View       view = factory.buildView(tree, 1);

                rootView.removeAllViews();
                rootView.addView(view);

                Log.i(TAG, "Tree rendered successfully");
            } catch (Exception e) {
                Log.e(TAG, "Render error: " + e.getMessage());
            }
        });
    }

    /** 60fps animation loop */
    private void startAnimationLoop() {
        handler.post(new Runnable() {
            long lastTime = System.currentTimeMillis();

            @Override
            public void run() {
                long now     = System.currentTimeMillis();
                long delta   = now - lastTime;
                lastTime     = now;

                bridge.nativeTick(delta);
                handler.postDelayed(this, FRAME_MS);
            }
        });
    }

    /** Test render — replace with Python output in production */
    private void renderTestScreen() {
        String testTree = "{"
            + "\"type\":\"VStack\","
            + "\"padding\":[24,24,24,24],"
            + "\"spacing\":16,"
            + "\"background\":\"#F2F2F7\","
            + "\"corner_radius\":0,"
            + "\"opacity\":1.0,"
            + "\"visible\":true,"
            + "\"margin\":[0,0,0,0],"
            + "\"children\":["
            + "  {\"type\":\"Heading\","
            + "   \"content\":\"Hello from BlinkUI\","
            + "   \"font_size\":28,\"bold\":true,"
            + "   \"color\":\"#1C1C1E\","
            + "   \"padding\":[0,0,0,0],"
            + "   \"margin\":[0,0,0,0],"
            + "   \"opacity\":1.0,\"visible\":true,"
            + "   \"children\":[]},"
            + "  {\"type\":\"Text\","
            + "   \"content\":\"Built with Python and C\","
            + "   \"font_size\":16,"
            + "   \"color\":\"#8E8E93\","
            + "   \"padding\":[0,0,0,0],"
            + "   \"margin\":[0,0,0,0],"
            + "   \"opacity\":1.0,\"visible\":true,"
            + "   \"children\":[]},"
            + "  {\"type\":\"Button\","
            + "   \"label\":\"Get Started\","
            + "   \"background\":\"#007AFF\","
            + "   \"color\":\"#FFFFFF\","
            + "   \"corner_radius\":12,"
            + "   \"font_size\":16,"
            + "   \"bold\":true,"
            + "   \"padding\":[14,20,14,20],"
            + "   \"margin\":[0,0,0,0],"
            + "   \"opacity\":1.0,\"visible\":true,"
            + "   \"children\":[]}"
            + "]}";

        renderTree(testTree);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}