package com.blinkui;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.DecelerateInterpolator;
import android.view.animation.OvershootInterpolator;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * BlinkUI Modal
 * Dark overlay with animated card popup
 */
public class BlinkUIModal {

    public interface ModalDismissListener {
        void onDismiss();
    }

    private final Context              context;
    private final ViewGroup            rootView;
    private       FrameLayout          overlay;
    private       ModalDismissListener dismissListener;

    public BlinkUIModal(Context context, ViewGroup rootView) {
        this.context  = context;
        this.rootView = rootView;
    }

    public void show(String title, String message,
                     String confirmLabel, String cancelLabel,
                     Runnable onConfirm, ModalDismissListener onDismiss) {

        this.dismissListener = onDismiss;

        // ── dim overlay ──
        overlay = new FrameLayout(context);
        overlay.setBackgroundColor(Color.argb(180, 0, 0, 0));
        overlay.setLayoutParams(new ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ));

        // dismiss on outside tap
        overlay.setOnClickListener(v -> dismiss());

        // ── modal card ──
        LinearLayout card = buildCard(
            title, message, confirmLabel, cancelLabel, onConfirm
        );

        FrameLayout.LayoutParams cardLp = new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        );
        cardLp.gravity      = Gravity.BOTTOM;
        cardLp.leftMargin   = dpToPx(16);
        cardLp.rightMargin  = dpToPx(16);
        cardLp.bottomMargin = dpToPx(32);
        card.setLayoutParams(cardLp);

        overlay.addView(card);
        rootView.addView(overlay);

        // ── animate in ──
        overlay.setAlpha(0f);
        card.setTranslationY(dpToPx(100));
        card.setAlpha(0f);

        ObjectAnimator overlayFade = ObjectAnimator.ofFloat(overlay, "alpha", 0f, 1f);
        overlayFade.setDuration(200);

        ObjectAnimator cardSlide = ObjectAnimator.ofFloat(card, "translationY",
            dpToPx(100), 0f);
        ObjectAnimator cardFade  = ObjectAnimator.ofFloat(card, "alpha", 0f, 1f);
        cardSlide.setDuration(300);
        cardFade.setDuration(300);
        cardSlide.setInterpolator(new OvershootInterpolator(2f));

        AnimatorSet set = new AnimatorSet();
        set.playTogether(overlayFade, cardSlide, cardFade);
        set.start();
    }

    private LinearLayout buildCard(String title, String message,
                                   String confirmLabel, String cancelLabel,
                                   Runnable onConfirm) {
        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dpToPx(24), dpToPx(24), dpToPx(24), dpToPx(24));

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(20));
        bg.setStroke(dpToPx(1), Color.parseColor("#2A2A2A"));
        card.setBackground(bg);

        // stop outside click from propagating
        card.setOnClickListener(v -> {});

        // ── accent line ──
        View accentLine = new View(context);
        accentLine.setBackgroundColor(Color.parseColor("#00FF88"));
        LinearLayout.LayoutParams accentLp = new LinearLayout.LayoutParams(
            dpToPx(40), dpToPx(3)
        );
        accentLp.gravity      = Gravity.CENTER_HORIZONTAL;
        accentLp.bottomMargin = dpToPx(20);
        accentLine.setLayoutParams(accentLp);
        card.addView(accentLine);

        // ── title ──
        TextView titleView = new TextView(context);
        titleView.setText(title);
        titleView.setTextColor(Color.parseColor("#FFFFFF"));
        titleView.setTextSize(20);
        titleView.setTypeface(null, android.graphics.Typeface.BOLD);
        titleView.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams titleLp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        );
        titleLp.bottomMargin = dpToPx(12);
        titleView.setLayoutParams(titleLp);
        card.addView(titleView);

        // ── message ──
        if (message != null && !message.isEmpty()) {
            TextView msgView = new TextView(context);
            msgView.setText(message);
            msgView.setTextColor(Color.parseColor("#999999"));
            msgView.setTextSize(15);
            msgView.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams msgLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            );
            msgLp.bottomMargin = dpToPx(24);
            msgView.setLayoutParams(msgLp);
            card.addView(msgView);
        }

        // ── buttons ──
        LinearLayout btnRow = new LinearLayout(context);
        btnRow.setOrientation(LinearLayout.HORIZONTAL);

        if (cancelLabel != null && !cancelLabel.isEmpty()) {
            android.widget.Button cancelBtn = buildModalButton(
                cancelLabel, "#242424", "#FFFFFF", false
            );
            cancelBtn.setOnClickListener(v -> dismiss());
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f
            );
            lp.rightMargin = dpToPx(8);
            cancelBtn.setLayoutParams(lp);
            btnRow.addView(cancelBtn);
        }

        android.widget.Button confirmBtn = buildModalButton(
            confirmLabel != null ? confirmLabel : "OK",
            "#00FF88", "#0F0F0F", true
        );
        confirmBtn.setOnClickListener(v -> {
            dismiss();
            if (onConfirm != null) onConfirm.run();
        });
        LinearLayout.LayoutParams confirmLp = new LinearLayout.LayoutParams(
            0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f
        );
        confirmBtn.setLayoutParams(confirmLp);
        btnRow.addView(confirmBtn);

        card.addView(btnRow);
        return card;
    }

    private android.widget.Button buildModalButton(
            String label, String bg, String textColor, boolean bold) {
        android.widget.Button btn = new android.widget.Button(context);
        btn.setText(label);
        btn.setAllCaps(false);
        btn.setTextSize(16);
        btn.setTypeface(null, bold ?
            android.graphics.Typeface.BOLD :
            android.graphics.Typeface.NORMAL
        );
        btn.setTextColor(Color.parseColor(textColor));

        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(Color.parseColor(bg));
        drawable.setCornerRadius(dpToPx(10));
        btn.setBackground(drawable);
        btn.setPadding(dpToPx(16), dpToPx(12), dpToPx(16), dpToPx(12));
        return btn;
    }

    public void dismiss() {
        if (overlay == null) return;

        ObjectAnimator fade = ObjectAnimator.ofFloat(overlay, "alpha", 1f, 0f);
        fade.setDuration(200);
        fade.setInterpolator(new DecelerateInterpolator());
        fade.addListener(new android.animation.AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(android.animation.Animator animation) {
                rootView.removeView(overlay);
                overlay = null;
                if (dismissListener != null) dismissListener.onDismiss();
            }
        });
        fade.start();
    }

    private int dpToPx(int dp) {
        return Math.round(dp * context.getResources().getDisplayMetrics().density);
    }
}
