package com.blinkui;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * BlinkUI Tab Bar
 * Dark themed, electric green active indicator
 */
public class TabBarManager {

    public interface TabSelectListener {
        void onTabSelected(int index);
    }

    private final Context           context;
    private final TabSelectListener listener;
    private int                     activeTab = 0;
    private LinearLayout            tabBar;
    private TextView[]              tabViews;

    // tab config
    private String[] labels;
    private String[] icons;

    public TabBarManager(Context context, TabSelectListener listener) {
        this.context  = context;
        this.listener = listener;
    }

    public View buildTabBar(String[] labels, String[] icons) {
        this.labels   = labels;
        this.icons    = icons;
        this.tabViews = new TextView[labels.length];

        // container
        tabBar = new LinearLayout(context);
        tabBar.setOrientation(LinearLayout.HORIZONTAL);
        tabBar.setBackgroundColor(Color.parseColor("#0F0F0F"));

        // top border line
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

    private TextView buildTab(String label, String icon, boolean active) {
        TextView tv = new TextView(context);
        tv.setText((icon.isEmpty() ? "" : icon + "\n") + label);
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

        // deactivate old
        tabViews[activeTab].setTextColor(Color.parseColor("#666666"));
        tabViews[activeTab].setTypeface(null, Typeface.NORMAL);

        // activate new
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
