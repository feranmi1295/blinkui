package com.blinkui;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.LinearLayout;
import org.json.JSONObject;

public class BlinkUIActivity extends Activity {

    private static final String TAG      = "BlinkUI";
    private static final int    FRAME_MS = 16;

    private BlinkUIBridge    bridge;
    private ComponentFactory factory;
    private LinearLayout     rootView;
    private Handler          handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        bridge  = BlinkUIBridge.getInstance();
        factory = new ComponentFactory(this);
        handler = new Handler(Looper.getMainLooper());

        rootView = new LinearLayout(this);
        rootView.setOrientation(LinearLayout.VERTICAL);
        rootView.setBackgroundColor(android.graphics.Color.parseColor("#0F0F0F"));
        setContentView(rootView);

        // dark status bar
        getWindow().setStatusBarColor(android.graphics.Color.parseColor("#0F0F0F"));
        getWindow().getDecorView().setSystemUiVisibility(0);

        // init C runtime — initializes all transpiled screens
        String result = bridge.nativeInit();
        bridge.nativeSetActivity(this);
        Log.i(TAG, result);

        startAnimationLoop();

        // get initial tree from transpiled HomeScreen
        String initialTree = bridge.nativeGetInitialTree();
        renderTree(initialTree);
    }

    // Called by C runtime via bk_request_render()
    public void renderTree(String treeJson) {
        handler.post(() -> {
            try {
                JSONObject tree = new JSONObject(treeJson);
                View       view = factory.buildView(tree, 1);
                rootView.removeAllViews();
                rootView.addView(view);
                Log.i(TAG, "Tree rendered");
            } catch (Exception e) {
                Log.e(TAG, "Render error: " + e.getMessage());
            }
        });
    }

    // Called by ComponentFactory when button tapped
    public void handleEvent(int nodeId, int eventType) {
        new Thread(() ->
            bridge.nativeFireEvent(nodeId, eventType, 0f, 0f)
        ).start();
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
