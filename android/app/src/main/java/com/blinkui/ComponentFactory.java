package com.blinkui;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;

public class ComponentFactory {

    private final Context          context;
    private final BlinkUIBridge    bridge;
    private final BlinkUIActivity  activity;

    public ComponentFactory(Context context) {
        this.context  = context;
        this.bridge   = BlinkUIBridge.getInstance();
        this.activity = (BlinkUIActivity) context;
    }

    public View buildView(JSONObject node, int nodeId) {
        try {
            // use node_id from JSON if present
            int id = node.optInt("node_id", nodeId);

            switch (node.getString("type")) {
                case "VStack":     return buildVStack(node, id);
                case "HStack":     return buildHStack(node, id);
                case "Heading":
                case "Label":
                case "Text":       return buildText(node, id);
                case "Button":     return buildButton(node, id);
                case "ScrollView": return buildScrollView(node, id);
                case "Card":       return buildCard(node, id);
                default:           return new View(context);
            }
        } catch (Exception e) {
            return new View(context);
        }
    }

    private View buildVStack(JSONObject node, int nodeId) throws Exception {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.VERTICAL);
        applyLayout(layout, node);
        applyBackground(layout, node);
        buildChildren(layout, node, nodeId);
        return layout;
    }

    private View buildHStack(JSONObject node, int nodeId) throws Exception {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        applyLayout(layout, node);
        applyBackground(layout, node);
        buildChildren(layout, node, nodeId);
        return layout;
    }

    private View buildText(JSONObject node, int nodeId) throws Exception {
        TextView tv = new TextView(context);
        tv.setText(node.optString("content", ""));
        tv.setTextSize(node.optInt("font_size", 16));
        if (node.optBoolean("bold", false))
            tv.setTypeface(null, Typeface.BOLD);
        String color = node.optString("color", "#1C1C1E");
        if (!color.isEmpty()) tv.setTextColor(parseColor(color));
        applyLayout(tv, node);
        return tv;
    }

    private View buildButton(JSONObject node, final int nodeId) throws Exception {
        Button btn = new Button(context);
        btn.setText(node.optString("label", ""));
        btn.setAllCaps(false);
        btn.setTextSize(node.optInt("font_size", 16));
        if (node.optBoolean("bold", false))
            btn.setTypeface(null, Typeface.BOLD);

        String bgColor = node.optString("background", "#007AFF");
        int    radius  = node.optInt("corner_radius", 12);
        setRoundedBackground(btn, bgColor, radius);
        btn.setTextColor(parseColor(node.optString("color", "#FFFFFF")));

        // route tap through Python via Activity
        btn.setOnClickListener(v ->
            activity.handleEvent(nodeId, BlinkUIBridge.EVENT_TAP)
        );

        applyLayout(btn, node);
        return btn;
    }

    private View buildScrollView(JSONObject node, int nodeId) throws Exception {
        ScrollView sv = new ScrollView(context);
        applyLayout(sv, node);
        buildChildren(sv, node, nodeId);
        return sv;
    }

    private View buildCard(JSONObject node, int nodeId) throws Exception {
        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        setRoundedBackground(card, "#FFFFFF", 12);
        card.setElevation(8f);
        applyLayout(card, node);
        buildChildren(card, node, nodeId);
        return card;
    }

    private void buildChildren(ViewGroup parent, JSONObject node, int parentId) throws Exception {
        JSONArray children = node.optJSONArray("children");
        if (children == null) return;
        for (int i = 0; i < children.length(); i++) {
            JSONObject child = children.getJSONObject(i);
            int childId = child.optInt("node_id", parentId * 100 + i);
            parent.addView(buildView(child, childId));
        }
    }

    private void applyLayout(View view, JSONObject node) throws Exception {
        int width  = node.optInt("width",  -1);
        int height = node.optInt("height", -2);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            width  == -1 ? ViewGroup.LayoutParams.MATCH_PARENT : dpToPx(width),
            height == -2 ? ViewGroup.LayoutParams.WRAP_CONTENT : dpToPx(height)
        );

        JSONArray padding = node.optJSONArray("padding");
        if (padding != null && padding.length() == 4) {
            view.setPadding(
                dpToPx(padding.getInt(3)),
                dpToPx(padding.getInt(0)),
                dpToPx(padding.getInt(1)),
                dpToPx(padding.getInt(2))
            );
        }

        JSONArray margin = node.optJSONArray("margin");
        if (margin != null && margin.length() == 4) {
            params.setMargins(
                dpToPx(margin.getInt(3)),
                dpToPx(margin.getInt(0)),
                dpToPx(margin.getInt(1)),
                dpToPx(margin.getInt(2))
            );
        }

        view.setAlpha((float) node.optDouble("opacity", 1.0));
        view.setVisibility(node.optBoolean("visible", true) ? View.VISIBLE : View.GONE);
        view.setLayoutParams(params);
    }

    private void applyBackground(View view, JSONObject node) throws Exception {
        String bg = node.optString("background", null);
        if (bg != null && !bg.isEmpty() && !bg.equals("null")) {
            setRoundedBackground(view, bg, node.optInt("corner_radius", 0));
        }
    }

    private void setRoundedBackground(View view, String color, int radiusDp) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(parseColor(color));
        d.setCornerRadius(dpToPx(radiusDp));
        view.setBackground(d);
    }

    private int parseColor(String color) {
        try { return Color.parseColor(color); }
        catch (Exception e) { return Color.BLACK; }
    }

    private int dpToPx(int dp) {
        return Math.round(dp * context.getResources().getDisplayMetrics().density);
    }
}
