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

/**
 * Translates BlinkUI component JSON into real Android Views.
 *
 * This is the heart of the Android bridge.
 * Every component type maps to a native Android View.
 */
public class ComponentFactory {

    private final Context context;
    private final BlinkUIBridge bridge;

    public ComponentFactory(Context context) {
        this.context = context;
        this.bridge  = BlinkUIBridge.getInstance();
    }

    /**
     * Build a View from a component JSON node.
     * Called recursively for nested components.
     */
    public View buildView(JSONObject node, int nodeId) {
        try {
            String type = node.getString("type");

            switch (type) {
                case "VStack":     return buildVStack(node, nodeId);
                case "HStack":     return buildHStack(node, nodeId);
                case "Text":
                case "Heading":
                case "Label":      return buildText(node, nodeId);
                case "Button":     return buildButton(node, nodeId);
                case "ScrollView": return buildScrollView(node, nodeId);
                case "Card":       return buildCard(node, nodeId);
                default:
                    // unknown component — render as empty view
                    return new View(context);
            }
        } catch (Exception e) {
            return new View(context);
        }
    }

    // ── VStack → vertical LinearLayout ──
    private View buildVStack(JSONObject node, int nodeId) throws Exception {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.VERTICAL);

        applyLayout(layout, node);
        applyBackground(layout, node);
        buildChildren(layout, node, nodeId);

        return layout;
    }

    // ── HStack → horizontal LinearLayout ──
    private View buildHStack(JSONObject node, int nodeId) throws Exception {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.HORIZONTAL);

        applyLayout(layout, node);
        applyBackground(layout, node);
        buildChildren(layout, node, nodeId);

        return layout;
    }

    // ── Text/Heading/Label → TextView ──
    private View buildText(JSONObject node, int nodeId) throws Exception {
        TextView tv = new TextView(context);

        String content = node.optString("content", "");
        tv.setText(content);

        // font size
        int fontSize = node.optInt("font_size", 16);
        tv.setTextSize(fontSize);

        // bold
        if (node.optBoolean("bold", false)) {
            tv.setTypeface(null, Typeface.BOLD);
        }

        // color
        String color = node.optString("color", "#1C1C1E");
        if (!color.isEmpty()) {
            tv.setTextColor(parseColor(color));
        }

        applyLayout(tv, node);
        return tv;
    }

    // ── Button → Button ──
    private View buildButton(JSONObject node, final int nodeId) throws Exception {
        Button btn = new Button(context);

        String label = node.optString("label", "");
        btn.setText(label);

        // background color with corner radius
        String bgColor = node.optString("background", "#007AFF");
        int radius     = node.optInt("corner_radius", 12);
        setRoundedBackground(btn, bgColor, radius);

        // text color
        String textColor = node.optString("color", "#FFFFFF");
        btn.setTextColor(parseColor(textColor));

        // fire tap event through C runtime when tapped
        btn.setOnClickListener(v -> {
            bridge.nativeFireEvent(
                nodeId,
                BlinkUIBridge.EVENT_TAP,
                0f, 0f
            );
        });

        applyLayout(btn, node);
        return btn;
    }

    // ── ScrollView ──
    private View buildScrollView(JSONObject node, int nodeId) throws Exception {
        ScrollView sv = new ScrollView(context);
        applyLayout(sv, node);
        buildChildren(sv, node, nodeId);
        return sv;
    }

    // ── Card → elevated LinearLayout ──
    private View buildCard(JSONObject node, int nodeId) throws Exception {
        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);

        // white background with corner radius
        setRoundedBackground(card, "#FFFFFF", 12);

        // elevation for shadow
        card.setElevation(8f);

        applyLayout(card, node);
        buildChildren(card, node, nodeId);

        return card;
    }

    // ── Helpers ──

    private void buildChildren(
        ViewGroup parent,
        JSONObject node,
        int parentId
    ) throws Exception {
        JSONArray children = node.optJSONArray("children");
        if (children == null) return;

        for (int i = 0; i < children.length(); i++) {
            JSONObject child     = children.getJSONObject(i);
            int        childId   = parentId * 100 + i;
            View       childView = buildView(child, childId);
            parent.addView(childView);
        }
    }

    private void applyLayout(View view, JSONObject node) throws Exception {
        int width  = node.optInt("width",  -1);   // -1 = match_parent
        int height = node.optInt("height", -2);   // -2 = wrap_content

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            width  == -1 ? ViewGroup.LayoutParams.MATCH_PARENT : dpToPx(width),
            height == -2 ? ViewGroup.LayoutParams.WRAP_CONTENT : dpToPx(height)
        );

        // padding
        JSONArray padding = node.optJSONArray("padding");
        if (padding != null && padding.length() == 4) {
            view.setPadding(
                dpToPx(padding.getInt(3)),  // left
                dpToPx(padding.getInt(0)),  // top
                dpToPx(padding.getInt(1)),  // right
                dpToPx(padding.getInt(2))   // bottom
            );
        }

        // margin
        JSONArray margin = node.optJSONArray("margin");
        if (margin != null && margin.length() == 4) {
            params.setMargins(
                dpToPx(margin.getInt(3)),
                dpToPx(margin.getInt(0)),
                dpToPx(margin.getInt(1)),
                dpToPx(margin.getInt(2))
            );
        }

        // opacity
        float opacity = (float) node.optDouble("opacity", 1.0);
        view.setAlpha(opacity);

        // visibility
        boolean visible = node.optBoolean("visible", true);
        view.setVisibility(visible ? View.VISIBLE : View.GONE);

        view.setLayoutParams(params);
    }

    private void applyBackground(View view, JSONObject node) throws Exception {
        String bg = node.optString("background", null);
        if (bg != null && !bg.isEmpty() && !bg.equals("null")) {
            int radius = node.optInt("corner_radius", 0);
            setRoundedBackground(view, bg, radius);
        }
    }

    private void setRoundedBackground(View view, String color, int radiusDp) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(parseColor(color));
        drawable.setCornerRadius(dpToPx(radiusDp));
        view.setBackground(drawable);
    }

    private int parseColor(String color) {
        try {
            return Color.parseColor(color);
        } catch (Exception e) {
            return Color.BLACK;
        }
    }

    private int dpToPx(int dp) {
        float density = context.getResources().getDisplayMetrics().density;
        return Math.round(dp * density);
    }
}