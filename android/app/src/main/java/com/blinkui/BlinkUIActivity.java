package com.blinkui;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.ObjectAnimator;
import android.animation.AnimatorSet;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import android.view.animation.OvershootInterpolator;
import android.widget.LinearLayout;
import org.json.JSONObject;

public class BlinkUIActivity extends Activity {

    private static final String TAG      = "BlinkUI";
    private static final int    FRAME_MS = 16;

    private BlinkUIBridge    bridge;
    private ComponentFactory factory;
    private LinearLayout     rootView;
    private Handler          handler;

    // animation state
    private int  prevScreen   = -1;
    private boolean animating = false;

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

        bridge.nativeInit();
        bridge.nativeSetActivity(this);

        startAnimationLoop();

        // render initial screen with fade in
        String initialTree = bridge.nativeGetInitialTree();
        renderTreeAnimated(initialTree, "fade_in");
    }

    // ── Called by C runtime via bk_request_render ──
    public void renderTree(String treeJson) {
        renderTreeAnimated(treeJson, "fade");
    }

    // ── Called by C runtime via bk_navigate ──
    public void navigateTo(int screenIndex) {
        String tree = bridge.nativeGetInitialTree();
        String anim = screenIndex > 0 ? "slide_in" : "slide_back";
        renderTreeAnimated(tree, anim);
    }

    // ── Core render + animate ──
    private void renderTreeAnimated(String treeJson, String animType) {
        handler.post(() -> {
            try {
                JSONObject tree = new JSONObject(treeJson);
                View newView    = factory.buildView(tree, 1);

                switch (animType) {
                    case "fade_in":
                        fadeIn(newView);
                        break;
                    case "slide_in":
                        slideIn(newView, 1);
                        break;
                    case "slide_back":
                        slideIn(newView, -1);
                        break;
                    default:
                        crossFade(newView);
                        break;
                }

            } catch (Exception e) {
                Log.e(TAG, "Render error: " + e.getMessage());
            }
        });
    }

    // ── Animations ──

    private void fadeIn(View newView) {
        newView.setAlpha(0f);
        rootView.removeAllViews();
        rootView.addView(newView);

        ObjectAnimator fade = ObjectAnimator.ofFloat(newView, "alpha", 0f, 1f);
        fade.setDuration(300);
        fade.setInterpolator(new DecelerateInterpolator());
        fade.start();
    }

    private void crossFade(View newView) {
        if (rootView.getChildCount() == 0) {
            fadeIn(newView);
            return;
        }

        View oldView = rootView.getChildAt(0);

        // fade out old
        ObjectAnimator fadeOut = ObjectAnimator.ofFloat(oldView, "alpha", 1f, 0f);
        fadeOut.setDuration(120);

        // fade in new
        newView.setAlpha(0f);
        fadeOut.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                rootView.removeAllViews();
                rootView.addView(newView);
                ObjectAnimator fadeIn = ObjectAnimator.ofFloat(newView, "alpha", 0f, 1f);
                fadeIn.setDuration(150);
                fadeIn.setInterpolator(new DecelerateInterpolator());
                fadeIn.start();
            }
        });
        fadeOut.start();
    }

    private void slideIn(View newView, int direction) {
        // direction: 1 = slide from right, -1 = slide from left
        float screenWidth = getResources().getDisplayMetrics().widthPixels;

        newView.setAlpha(0f);
        newView.setTranslationX(direction * screenWidth * 0.3f);

        rootView.removeAllViews();
        rootView.addView(newView);

        AnimatorSet set = new AnimatorSet();

        ObjectAnimator slideX = ObjectAnimator.ofFloat(
            newView, "translationX",
            direction * screenWidth * 0.3f, 0f
        );
        ObjectAnimator fadeIn = ObjectAnimator.ofFloat(newView, "alpha", 0f, 1f);

        set.playTogether(slideX, fadeIn);
        set.setDuration(280);
        set.setInterpolator(new DecelerateInterpolator(2f));
        set.start();
    }

    // ── Button press animation ──
    public static void animateButtonPress(View btn) {
        AnimatorSet set = new AnimatorSet();

        ObjectAnimator scaleDownX = ObjectAnimator.ofFloat(btn, "scaleX", 1f, 0.95f);
        ObjectAnimator scaleDownY = ObjectAnimator.ofFloat(btn, "scaleY", 1f, 0.95f);
        scaleDownX.setDuration(80);
        scaleDownY.setDuration(80);

        ObjectAnimator scaleUpX = ObjectAnimator.ofFloat(btn, "scaleX", 0.95f, 1f);
        ObjectAnimator scaleUpY = ObjectAnimator.ofFloat(btn, "scaleY", 0.95f, 1f);
        scaleUpX.setDuration(200);
        scaleUpY.setDuration(200);
        scaleUpX.setInterpolator(new OvershootInterpolator(3f));
        scaleUpY.setInterpolator(new OvershootInterpolator(3f));

        AnimatorSet down = new AnimatorSet();
        down.playTogether(scaleDownX, scaleDownY);

        AnimatorSet up = new AnimatorSet();
        up.playTogether(scaleUpX, scaleUpY);

        set.playSequentially(down, up);
        set.start();
    }

    // ── State change pulse on text ──
    public static void animateStateChange(View view) {
        ObjectAnimator scaleX = ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.08f, 1f);
        ObjectAnimator scaleY = ObjectAnimator.ofFloat(view, "scaleY", 1f, 1.08f, 1f);
        scaleX.setDuration(250);
        scaleY.setDuration(250);
        scaleX.setInterpolator(new OvershootInterpolator(4f));
        scaleY.setInterpolator(new OvershootInterpolator(4f));

        AnimatorSet set = new AnimatorSet();
        set.playTogether(scaleX, scaleY);
        set.start();
    }

    // ── Called by ComponentFactory ──
    public void handleEvent(int nodeId, int eventType) {
        new Thread(() ->
            bridge.nativeFireEvent(nodeId, eventType, 0f, 0f)
        ).start();
    }

    public void handleTextChange(int nodeId, String text) {
        new Thread(() ->
            bridge.nativeTextChange(nodeId, text)
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
