package com.blinkui;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

public class TabBarManager {

    public interface TabSelectListener {
        void onTabSelected(int index);
    }

    private final Context           context;
    private final TabSelectListener listener;
    private int                     activeTab = 0;
    private LinearLayout            tabBar;
    private TextView[]              tabViews;
    private String[]                labels;
    private String[]                icons;

    public TabBarManager(Context context, TabSelectListener listener) {
        this.context  = context;
        this.listener = listener;
    }

    public View buildTabBar(String[] labels, String[] icons) {
        this.labels   = labels;
        this.icons    = icons;
        this.tabViews = new TextView[labels.length];

        tabBar = new LinearLayout(context);
        tabBar.setOrientation(LinearLayout.HORIZONTAL);
        tabBar.setBackgroundColor(Color.parseColor("#0F0F0F"));

        View border = new View(context);
        border.setBackgroundColor(Color.parseColor("#2A2A2A"));

        LinearLayout wrapper = new LinearLayout(context);
        wrapper.setOrientation(LinearLayout.VERTICAL);
        wrapper.setBackgroundColor(Color.parseColor("#0F0F0F"));
        wrapper.addView(border, new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, dpToPx(1)
        ));
        wrapper.addView(tabBar);

        for (int i = 0; i < labels.length; i++) {
            final int index = i;
            TextView tab = buildTab(labels[i], icons != null ? icons[i] : "", i == 0);
            tab.setOnClickListener(v -> selectTab(index));
            tabViews[i] = tab;
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f
            );
            tabBar.addView(tab, lp);
        }

        return wrapper;
    }

    private String resolveIcon(String name) {
        if (name == null || name.isEmpty()) return "";
        switch (name.toLowerCase()) {
            case "home":     return "\u2302";
            case "search":   return "\u2315";
            case "profile":
            case "user":     return "\u25c9";
            case "settings": return "\u2699";
            case "chat":     return "\u25ce";
            case "heart":    return "\u2665";
            case "star":     return "\u2605";
            case "add":      return "+";
            case "menu":     return "\u2630";
            default:         return name;
        }
    }

    private int getIconRes(String name) {
        if (name == null || name.isEmpty()) return 0;
        switch (name.toLowerCase()) {
            case "home":     return R.drawable.ic_home;
            case "search":   return R.drawable.ic_search;
            case "profile":
            case "user":     return R.drawable.ic_person;
            case "settings": return R.drawable.ic_settings;
            case "chat":     return R.drawable.ic_chat;
            case "add":      return R.drawable.ic_add;
            case "heart":    return R.drawable.ic_heart;
            case "star":     return R.drawable.ic_star;
            case "bell":     return R.drawable.ic_notification;
            default:         return 0;
        }
    }

    private View buildTabItem(String label, String icon, boolean active) {
        LinearLayout tab = new LinearLayout(context);
        tab.setOrientation(LinearLayout.VERTICAL);
        tab.setGravity(Gravity.CENTER);
        tab.setPadding(dpToPx(8), dpToPx(8), dpToPx(8), dpToPx(8));

        int iconRes = getIconRes(icon);
        if (iconRes != 0) {
            android.widget.ImageView iv = new android.widget.ImageView(context);
            iv.setImageResource(iconRes);
            int iconColor = active ?
                Color.parseColor("#00FF88") : Color.parseColor("#555555");
            iv.setColorFilter(iconColor, android.graphics.PorterDuff.Mode.SRC_IN);
            LinearLayout.LayoutParams ilp = new LinearLayout.LayoutParams(dpToPx(22), dpToPx(22));
            ilp.gravity = Gravity.CENTER_HORIZONTAL;
            ilp.bottomMargin = dpToPx(3);
            iv.setLayoutParams(ilp);
            tab.addView(iv);
        }

        TextView tv = new TextView(context);
        tv.setText(label);
        tv.setTextSize(10);
        tv.setGravity(Gravity.CENTER);
        tv.setTextColor(active ?
            Color.parseColor("#00FF88") : Color.parseColor("#555555"));
        tv.setTypeface(null, active ? Typeface.BOLD : Typeface.NORMAL);
        tab.addView(tv);

        return tab;
    }

    private TextView buildTab(String label, String icon, boolean active) {
        TextView tv = new TextView(context);
        String sym = resolveIcon(icon);
        tv.setText((sym.isEmpty() ? "" : sym + "\n") + label);
        tv.setGravity(Gravity.CENTER);
        tv.setTextSize(11);
        tv.setPadding(dpToPx(8), dpToPx(10), dpToPx(8), dpToPx(10));
        tv.setTextColor(active ?
            Color.parseColor("#00FF88") :
            Color.parseColor("#666666")
        );
        tv.setTypeface(null, active ? Typeface.BOLD : Typeface.NORMAL);
        return tv;
    }

    public void selectTab(int index) {
        if (index == activeTab) return;
        tabViews[activeTab].setTextColor(Color.parseColor("#666666"));
        tabViews[activeTab].setTypeface(null, Typeface.NORMAL);
        activeTab = index;
        tabViews[activeTab].setTextColor(Color.parseColor("#00FF88"));
        tabViews[activeTab].setTypeface(null, Typeface.BOLD);
        listener.onTabSelected(index);
    }

    public int getActiveTab() { return activeTab; }

    private int dpToPx(int dp) {
        return Math.round(dp * context.getResources().getDisplayMetrics().density);
    }
}
