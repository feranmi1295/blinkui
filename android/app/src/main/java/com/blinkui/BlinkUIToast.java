package com.blinkui;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.view.animation.DecelerateInterpolator;

/**
 * BlinkUI Toast
 * Animated dark toast with electric green accent
 * Types: success, error, info, warning
 */
public class BlinkUIToast {

    public static final String SUCCESS = "success";
    public static final String ERROR   = "error";
    public static final String INFO    = "info";
    public static final String WARNING = "warning";

    private static View     currentToast = null;
    private static Handler  handler      = new Handler(Looper.getMainLooper());
    private static Runnable dismissRunnable;

    public static void show(Context context, ViewGroup rootView,
                            String message, String type, int durationMs) {
        handler.post(() -> {
            // remove existing toast
            if (currentToast != null) {
                rootView.removeView(currentToast);
                if (dismissRunnable != null) handler.removeCallbacks(dismissRunnable);
            }

            // build toast view
            LinearLayout toast = buildToast(context, message, type);

            FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            );
            lp.gravity      = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
            lp.bottomMargin = dpToPx(context, 80);
            lp.leftMargin   = dpToPx(context, 16);
            lp.rightMargin  = dpToPx(context, 16);
            toast.setLayoutParams(lp);

            rootView.addView(toast);
            currentToast = toast;

            // animate in — slide up from bottom
            toast.setTranslationY(dpToPx(context, 100));
            toast.setAlpha(0f);

            AnimatorSet animIn = new AnimatorSet();
            animIn.playTogether(
                ObjectAnimator.ofFloat(toast, "translationY",
                    dpToPx(context, 100), 0f),
                ObjectAnimator.ofFloat(toast, "alpha", 0f, 1f)
            );
            animIn.setDuration(250);
            animIn.setInterpolator(new DecelerateInterpolator(2f));
            animIn.start();

            // auto dismiss
            dismissRunnable = () -> dismiss(rootView, toast);
            handler.postDelayed(dismissRunnable, durationMs);
        });
    }

    private static void dismiss(ViewGroup rootView, View toast) {
        AnimatorSet animOut = new AnimatorSet();
        animOut.playTogether(
            ObjectAnimator.ofFloat(toast, "translationY", 0f,
                dpToPx(toast.getContext(), 60)),
            ObjectAnimator.ofFloat(toast, "alpha", 1f, 0f)
        );
        animOut.setDuration(200);
        animOut.addListener(new android.animation.AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(android.animation.Animator animation) {
                rootView.removeView(toast);
                if (currentToast == toast) currentToast = null;
            }
        });
        animOut.start();
    }

    private static LinearLayout buildToast(Context ctx,
                                            String message, String type) {
        LinearLayout layout = new LinearLayout(ctx);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        layout.setGravity(Gravity.CENTER_VERTICAL);
        layout.setPadding(dpToPx(ctx, 16), dpToPx(ctx, 14),
                          dpToPx(ctx, 16), dpToPx(ctx, 14));

        // background
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(ctx, 12));
        bg.setStroke(dpToPx(ctx, 1), accentColor(type));
        layout.setBackground(bg);
        layout.setElevation(dpToPx(ctx, 8));

        // accent dot
        View dot = new View(ctx);
        dot.setBackgroundColor(accentColor(type));
        GradientDrawable dotBg = new GradientDrawable();
        dotBg.setColor(accentColor(type));
        dotBg.setCornerRadius(dpToPx(ctx, 4));
        dot.setBackground(dotBg);
        LinearLayout.LayoutParams dotLp = new LinearLayout.LayoutParams(
            dpToPx(ctx, 8), dpToPx(ctx, 8)
        );
        dotLp.rightMargin = dpToPx(ctx, 12);
        dotLp.gravity     = Gravity.CENTER_VERTICAL;
        dot.setLayoutParams(dotLp);
        layout.addView(dot);

        // message
        TextView tv = new TextView(ctx);
        tv.setText(message);
        tv.setTextColor(Color.parseColor("#FFFFFF"));
        tv.setTextSize(14);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        layout.addView(tv);

        return layout;
    }

    private static int accentColor(String type) {
        switch (type) {
            case SUCCESS: return Color.parseColor("#00FF88");
            case ERROR:   return Color.parseColor("#FF3B30");
            case WARNING: return Color.parseColor("#FF9500");
            case INFO:    return Color.parseColor("#0A84FF");
            default:      return Color.parseColor("#00FF88");
        }
    }

    private static int dpToPx(Context ctx, int dp) {
        return Math.round(dp * ctx.getResources().getDisplayMetrics().density);
    }
}
