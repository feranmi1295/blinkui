package com.blinkui;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;

public class ComponentFactory {

    private final Context         context;
    private final BlinkUIBridge   bridge;
    private final BlinkUIActivity activity;

    public ComponentFactory(Context context) {
        this.context  = context;
        this.bridge   = BlinkUIBridge.getInstance();
        this.activity = (BlinkUIActivity) context;
    }

    public View buildView(JSONObject node, int nodeId) {
        try {
            int id = node.optInt("node_id", nodeId);
            switch (node.getString("type")) {
                case "VStack":        return buildStack(node, id, LinearLayout.VERTICAL, nodeId == 1 ? 0 : 1);
                case "HStack":        return buildStack(node, id, LinearLayout.HORIZONTAL, 1);
                case "ZStack":        return buildStack(node, id, LinearLayout.VERTICAL, 1);
                case "Card":          return buildCard(node, id);
                case "ScrollView":    return buildScrollView(node, id);
                case "Heading":       return buildText(node, id, 28, true);
                case "Label":         return buildText(node, id, 14, false);
                case "Text":          return buildText(node, id, 16, false);
                case "Button":        return buildButton(node, id);
                case "NavigationBar": return buildNavBar(node, id);
                case "TextField":     return buildTextField(node, id);
                case "Divider":       return buildDivider(node, id);
                case "Spacer":        return buildSpacer(node, id);
                case "List":
                case "ListView":      return buildScrollView(node, id);
                case "ListItem":      return buildListItem(node, id);
                case "Modal":         return buildModalTrigger(node, id);
                case "Image":
                case "Avatar":        return buildImage(node, id);
                case "Icon":          return buildIcon(node, id);
                default:              return new View(context);
            }
        } catch (Exception e) {
            return new View(context);
        }
    }

    private View buildStack(JSONObject node, int nodeId, int orientation, int depth) throws Exception {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(orientation);
        boolean isRoot = (orientation == LinearLayout.VERTICAL && depth == 0);
        applyBackground(layout, node);
        int spacing = dpToPx(node.optInt("spacing", 0));
        JSONArray children = node.optJSONArray("children");
        if (children != null) {
            for (int i = 0; i < children.length(); i++) {
                JSONObject child = children.getJSONObject(i);
                int childId = child.optInt("node_id", nodeId * 100 + i);
                View childView = buildView(child, childId);
                LinearLayout.LayoutParams params;
                if (orientation == LinearLayout.HORIZONTAL) {
                    params = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f);
                    if (i > 0) params.leftMargin = spacing;
                } else {
                    params = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                    if (i > 0) params.topMargin = spacing;
                }
                childView.setLayoutParams(params);
                layout.addView(childView);
            }
        }
        applyPadding(layout, node);
        if (isRoot || node.optBoolean("scrollable", false)) {
            layout.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
            ScrollView sv = new ScrollView(context);
            sv.setFillViewport(false);
            sv.setBackgroundColor(parseColor(node.optString("background", "#0F0F0F")));
            sv.addView(layout);
            sv.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            return sv;
        }
        layout.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return layout;
    }

    private View buildCard(JSONObject node, int nodeId) throws Exception {
        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        String bg = node.optString("background", "#1A1A1A");
        int radius = dpToPx(node.optInt("corner_radius", 12));
        setRoundedBackground(card, bg, radius);
        card.setElevation(dpToPx(4));
        int spacing = dpToPx(node.optInt("spacing", 0));
        JSONArray children = node.optJSONArray("children");
        if (children != null) {
            for (int i = 0; i < children.length(); i++) {
                JSONObject child = children.getJSONObject(i);
                int childId = child.optInt("node_id", nodeId * 100 + i);
                View childView = buildView(child, childId);
                LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                if (i > 0) p.topMargin = spacing;
                childView.setLayoutParams(p);
                card.addView(childView);
            }
        }
        applyPadding(card, node);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dpToPx(8);
        card.setLayoutParams(lp);
        return card;
    }

    private View buildScrollView(JSONObject node, int nodeId) throws Exception {
        ScrollView sv = new ScrollView(context);
        sv.setBackgroundColor(parseColor(node.optString("background", "#0F0F0F")));
        sv.setFillViewport(true);
        LinearLayout inner = new LinearLayout(context);
        inner.setOrientation(LinearLayout.VERTICAL);
        inner.setBackgroundColor(parseColor(node.optString("background", "#0F0F0F")));
        int spacing = dpToPx(node.optInt("spacing", 0));
        JSONArray children = node.optJSONArray("children");
        if (children != null) {
            for (int i = 0; i < children.length(); i++) {
                JSONObject child = children.getJSONObject(i);
                int childId = child.optInt("node_id", nodeId * 100 + i);
                View childView = buildView(child, childId);
                LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                if (i > 0) p.topMargin = spacing;
                childView.setLayoutParams(p);
                inner.addView(childView);
            }
        }
        applyPadding(inner, node);
        sv.addView(inner);
        sv.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        return sv;
    }

    private View buildText(JSONObject node, int nodeId, int defaultSize, boolean defaultBold) throws Exception {
        TextView tv = new TextView(context);
        tv.setText(node.optString("content", ""));
        tv.setTextSize(node.optInt("font_size", defaultSize));
        boolean bold = node.optBoolean("bold", defaultBold);
        tv.setTypeface(null, bold ? Typeface.BOLD : Typeface.NORMAL);
        String color = node.optString("color", "#FFFFFF");
        if (!color.isEmpty()) tv.setTextColor(parseColor(color));
        String align = node.optString("text_align", "left");
        if (align.equals("center")) tv.setGravity(Gravity.CENTER_HORIZONTAL);
        applyPadding(tv, node);
        tv.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return tv;
    }

    private View buildButton(JSONObject node, final int nodeId) throws Exception {
        Button btn = new Button(context);
        btn.setText(node.optString("label", ""));
        btn.setAllCaps(false);
        btn.setTextSize(node.optInt("font_size", 16));
        btn.setTypeface(null, Typeface.BOLD);
        String bg = node.optString("background", "#00FF88");
        int radius = dpToPx(node.optInt("corner_radius", 6));
        setRoundedBackground(btn, bg, radius);
        btn.setTextColor(parseColor(node.optString("color", "#0F0F0F")));
        btn.setOnClickListener(v -> {
            BlinkUIActivity.animateButtonPress(v);
            v.postDelayed(() -> activity.handleEvent(nodeId, BlinkUIBridge.EVENT_TAP), 80);
        });
        applyPadding(btn, node);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dpToPx(8);
        lp.bottomMargin = dpToPx(4);
        btn.setLayoutParams(lp);
        return btn;
    }

    private View buildNavBar(JSONObject node, int nodeId) throws Exception {
        TextView tv = new TextView(context);
        tv.setText(node.optString("content", node.optString("title", "Screen")));
        tv.setTextSize(20);
        tv.setTypeface(null, Typeface.BOLD);
        tv.setTextColor(parseColor("#FFFFFF"));
        tv.setGravity(Gravity.CENTER);
        tv.setBackgroundColor(parseColor("#0F0F0F"));
        tv.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));
        tv.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return tv;
    }

    private View buildTextField(JSONObject node, final int nodeId) throws Exception {
        android.widget.EditText et = new android.widget.EditText(context);
        et.setHint(node.optString("placeholder", ""));
        et.setHintTextColor(parseColor("#555555"));
        et.setTextColor(parseColor("#FFFFFF"));
        et.setTextSize(node.optInt("font_size", 16));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(node.optInt("corner_radius", 8)));
        bg.setStroke(dpToPx(1), parseColor("#2A2A2A"));
        et.setBackground(bg);
        et.setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14));
        et.addTextChangedListener(new android.text.TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                activity.handleTextChange(nodeId, s.toString());
            }
            public void afterTextChanged(android.text.Editable s) {}
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dpToPx(8);
        et.setLayoutParams(lp);
        return et;
    }

    private View buildDivider(JSONObject node, int nodeId) {
        View divider = new View(context);
        divider.setBackgroundColor(parseColor("#2A2A2A"));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(1));
        lp.topMargin = dpToPx(8);
        lp.bottomMargin = dpToPx(8);
        divider.setLayoutParams(lp);
        return divider;
    }

    private View buildSpacer(JSONObject node, int nodeId) {
        View spacer = new View(context);
        spacer.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(node.optInt("height", 16))));
        return spacer;
    }

    private View buildListItem(JSONObject node, int nodeId) throws Exception {
        LinearLayout item = new LinearLayout(context);
        item.setOrientation(LinearLayout.HORIZONTAL);
        item.setGravity(Gravity.CENTER_VERTICAL);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(8));
        item.setBackground(bg);
        item.setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14));
        View accent = new View(context);
        accent.setBackgroundColor(parseColor("#00FF88"));
        GradientDrawable accentBg = new GradientDrawable();
        accentBg.setColor(parseColor("#00FF88"));
        accentBg.setCornerRadius(dpToPx(4));
        accent.setBackground(accentBg);
        LinearLayout.LayoutParams accentLp = new LinearLayout.LayoutParams(dpToPx(3), ViewGroup.LayoutParams.MATCH_PARENT);
        accentLp.rightMargin = dpToPx(12);
        accent.setLayoutParams(accentLp);
        item.addView(accent);
        JSONArray children = node.optJSONArray("children");
        if (children != null) {
            for (int i = 0; i < children.length(); i++) {
                JSONObject child = children.getJSONObject(i);
                item.addView(buildView(child, child.optInt("node_id", nodeId * 100 + i)));
            }
        } else {
            String text = node.optString("content", "");
            if (!text.isEmpty()) {
                TextView tv = new TextView(context);
                tv.setText(text);
                tv.setTextColor(parseColor("#FFFFFF"));
                tv.setTextSize(16);
                item.addView(tv);
            }
        }
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dpToPx(8);
        item.setLayoutParams(lp);
        int nid = nodeId;
        item.setOnClickListener(v -> {
            BlinkUIActivity.animateButtonPress(v);
            v.postDelayed(() -> activity.handleEvent(nid, BlinkUIBridge.EVENT_TAP), 80);
        });
        return item;
    }

    private View buildModalTrigger(JSONObject node, final int nodeId) throws Exception {
        Button btn = new Button(context);
        btn.setText(node.optString("label", node.optString("title", "Open")));
        btn.setAllCaps(false);
        btn.setTextSize(16);
        btn.setTypeface(null, Typeface.BOLD);
        btn.setTextColor(parseColor("#0F0F0F"));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(parseColor("#00FF88"));
        bg.setCornerRadius(dpToPx(10));
        btn.setBackground(bg);
        String title   = node.optString("title", "Confirm");
        String message = node.optString("message", "");
        String confirm = node.optString("confirm", "Confirm");
        String cancel  = node.optString("cancel", "Cancel");
        btn.setOnClickListener(v -> {
            BlinkUIActivity.animateButtonPress(v);
            v.postDelayed(() -> activity.showModal(title, message, confirm, cancel,
                () -> activity.handleEvent(nodeId, BlinkUIBridge.EVENT_TAP)), 80);
        });
        applyPadding(btn, node);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dpToPx(8);
        btn.setLayoutParams(lp);
        return btn;
    }

    private View buildImage(JSONObject node, int nodeId) throws Exception {
        android.widget.ImageView iv = new android.widget.ImageView(context);
        iv.setScaleType(android.widget.ImageView.ScaleType.CENTER_CROP);
        int width  = node.optInt("width", -1);
        int height = node.optInt("height", 200);
        int radius = node.optInt("corner_radius", 0);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            width == -1 ? ViewGroup.LayoutParams.MATCH_PARENT : dpToPx(width), dpToPx(height));
        lp.topMargin = dpToPx(8);
        lp.bottomMargin = dpToPx(8);
        iv.setLayoutParams(lp);
        if (radius > 0) {
            iv.setClipToOutline(true);
            GradientDrawable bg = new GradientDrawable();
            bg.setCornerRadius(dpToPx(radius));
            bg.setColor(parseColor("#1A1A1A"));
            iv.setBackground(bg);
        } else {
            iv.setBackgroundColor(parseColor("#1A1A1A"));
        }
        String src = node.optString("src", node.optString("url", ""));
        if (!src.isEmpty()) BlinkUIImageLoader.load(src, iv);
        return iv;
    }

    private View buildIcon(JSONObject node, int nodeId) throws Exception {
        android.widget.ImageView iv = new android.widget.ImageView(context);
        String name  = node.optString("name", "add");
        int    size  = node.optInt("size", 24);
        String color = node.optString("color", "#00FF88");

        int resId = getIconResource(name);
        if (resId != 0) {
            iv.setImageResource(resId);
            // tint the icon with the requested color
            iv.setColorFilter(parseColor(color),
                android.graphics.PorterDuff.Mode.SRC_IN);
        }

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            dpToPx(size), dpToPx(size)
        );
        lp.gravity = Gravity.CENTER;
        iv.setLayoutParams(lp);
        iv.setScaleType(android.widget.ImageView.ScaleType.FIT_CENTER);
        return iv;
    }

    private int getIconResource(String name) {
        switch (name.toLowerCase()) {
            case "home":         return R.drawable.ic_home;
            case "search":       return R.drawable.ic_search;
            case "user":
            case "profile":
            case "person":       return R.drawable.ic_person;
            case "settings":     return R.drawable.ic_settings;
            case "add":
            case "plus":         return R.drawable.ic_add;
            case "close":
            case "x":            return R.drawable.ic_close;
            case "back":         return R.drawable.ic_back;
            case "heart":        return R.drawable.ic_heart;
            case "star":         return R.drawable.ic_star;
            case "chat":
            case "message":      return R.drawable.ic_chat;
            case "bell":
            case "notification": return R.drawable.ic_notification;
            case "ai":
            case "robot":        return R.drawable.ic_ai;
            default:             return R.drawable.ic_add;
        }
    }

    private String iconSymbol(String name) {
        switch (name.toLowerCase()) {
            case "home":       return "\u2302";
            case "back":       return "\u2190";
            case "forward":    return "\u2192";
            case "menu":       return "\u2630";
            case "close":      return "\u2715";
            case "search":     return "\u2315";
            case "settings":   return "\u2699";
            case "user":
            case "profile":    return "\u25c9";
            case "add":        return "+";
            case "edit":       return "\u270e";
            case "delete":     return "\ud83d\uddd1";
            case "check":
            case "success":    return "\u2713";
            case "error":      return "\u2715";
            case "warning":    return "\u26a0";
            case "info":       return "\u2139";
            case "heart":      return "\u2665";
            case "star":       return "\u2605";
            case "bell":       return "\ud83d\udd14";
            case "chat":       return "\u25ce";
            case "mail":       return "\u2709";
            case "send":       return "\u27a4";
            case "lightning":  return "\u26a1";
            case "ai":         return "\u2726";
            case "code":       return "</>";
            default:           return name;
        }
    }

    private void applyBackground(View view, JSONObject node) {
        String bg = node.optString("background", "");
        if (!bg.isEmpty()) {
            setRoundedBackground(view, bg, dpToPx(node.optInt("corner_radius", 0)));
        }
    }

    private void applyPadding(View view, JSONObject node) throws Exception {
        JSONArray p = node.optJSONArray("padding");
        if (p != null && p.length() == 4) {
            view.setPadding(dpToPx(p.getInt(3)), dpToPx(p.getInt(0)),
                            dpToPx(p.getInt(1)), dpToPx(p.getInt(2)));
        }
    }

    private void setRoundedBackground(View view, String color, int radiusPx) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(parseColor(color));
        d.setCornerRadius(radiusPx);
        view.setBackground(d);
    }

    private int parseColor(String color) {
        try { return Color.parseColor(color); }
        catch (Exception e) { return Color.TRANSPARENT; }
    }

    private int dpToPx(int dp) {
        return Math.round(dp * context.getResources().getDisplayMetrics().density);
    }
}
