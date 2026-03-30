package com.blinkui;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.LinearLayout;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import org.json.JSONObject;

public class BlinkUIActivity extends Activity {

    private static final String TAG      = "BlinkUI";
    private static final int    FRAME_MS = 16;

    private BlinkUIBridge    bridge;
    private ComponentFactory factory;
    private LinearLayout     rootView;
    private Handler          handler;

    // Python module running on device
    private PyObject pyModule;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        bridge  = BlinkUIBridge.getInstance();
        factory = new ComponentFactory(this);
        handler = new Handler(Looper.getMainLooper());

        rootView = new LinearLayout(this);
        rootView.setOrientation(LinearLayout.VERTICAL);
        setContentView(rootView);

        bridge.nativeInit();
        bridge.nativeSetActivity(this);

        // ── Start Python ──
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
        pyModule = py.getModule("main_screen");
        Log.i(TAG, "Python started — main_screen loaded");

        startAnimationLoop();

        // ── Render initial tree from Python ──
        String initialTree = pyModule.callAttr("get_initial_tree").toString();
        renderTree(initialTree);
    }

    /**
     * Called by C runtime (and directly) to update UI.
     * Always runs on UI thread.
     */
    public void renderTree(String treeJson) {
        handler.post(() -> {
            try {
                JSONObject tree = new JSONObject(treeJson);
                View       view = factory.buildView(tree, 1);
                rootView.removeAllViews();
                rootView.addView(view);
            } catch (Exception e) {
                Log.e(TAG, "Render error: " + e.getMessage());
            }
        });
    }

    /**
     * Called by ComponentFactory when a button is tapped.
     * Passes event to Python → gets new tree → re-renders.
     */
    public void handleEvent(int nodeId, int eventType) {
        // run off UI thread so Python can do heavy work
        new Thread(() -> {
            try {
                String newTree = pyModule
                    .callAttr("on_event", nodeId, eventType)
                    .toString();
                renderTree(newTree);
            } catch (Exception e) {
                Log.e(TAG, "Python event error: " + e.getMessage());
            }
        }).start();
    }

    private void startAnimationLoop() {
        handler.post(new Runnable() {
            long lastTime = System.currentTimeMillis();
            @Override
            public void run() {
                long now = System.currentTimeMillis();
                bridge.nativeTick(now - lastTime);
                lastTime = now;
                handler.postDelayed(this, FRAME_MS);
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}
