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
                case "SmartList":     return buildSmartList(node, id);
                case "AICard":        return buildAICard(node, id);
                case "SmartForm":     return buildSmartForm(node, id);
                case "AutoStyle":     return buildAutoStyle(node, id);
                case "SmartText":     return buildSmartText(node, id);
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
                    // check if child has explicit width
                    int childW = child.optInt("width", -99);
                    if (childW != -99 && childW > 0) {
                        // fixed width child (avatar, icon etc)
                        params = new LinearLayout.LayoutParams(dpToPx(childW), ViewGroup.LayoutParams.WRAP_CONTENT);
                    } else if (child.optString("type","").equals("Spacer")) {
                        // spacer takes remaining space
                        params = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f);
                    } else if (i == 0) {
                        // first child — wrap content
                        params = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                    } else {
                        // other children share remaining space
                        params = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f);
                    }
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

        // background means it acts as a badge/avatar — fixed size, centered
        String bg = node.optString("background", "");
        if (!bg.isEmpty()) {
            int size = dpToPx(node.optInt("font_size", defaultSize) * 2 + 8);
            GradientDrawable bgDrawable = new GradientDrawable();
            bgDrawable.setColor(parseColor(bg));
            int radius = node.optInt("corner_radius", size / 2);
            bgDrawable.setCornerRadius(dpToPx(radius > 0 ? radius : size / 2));
            tv.setBackground(bgDrawable);
            tv.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(size, size);
            tv.setLayoutParams(lp);
            return tv;
        }

        applyPadding(tv, node);
        tv.setLayoutParams(new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
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

    // ── AI-Native Components ──

    private View buildSmartList(JSONObject node, int nodeId) throws Exception {
        // SmartList — auto-renders list data with detected template
        LinearLayout container = new LinearLayout(context);
        container.setOrientation(LinearLayout.VERTICAL);
        container.setBackgroundColor(parseColor("#0F0F0F"));

        String template = node.optString("template", "row_text");
        org.json.JSONArray items = node.optJSONArray("items");

        if (items == null || items.length() == 0) {
            // empty state
            TextView empty = new TextView(context);
            empty.setText("No items yet");
            empty.setTextColor(parseColor("#555555"));
            empty.setTextSize(14);
            empty.setGravity(Gravity.CENTER);
            empty.setPadding(0, dpToPx(32), 0, dpToPx(32));
            container.addView(empty);
            return container;
        }

        for (int i = 0; i < items.length(); i++) {
            View item = buildSmartListItem(items.get(i), template, nodeId * 100 + i);
            container.addView(item);
        }

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        container.setLayoutParams(lp);
        return container;
    }

    private View buildSmartListItem(Object data, String template, int nodeId) {
        LinearLayout item = new LinearLayout(context);
        item.setOrientation(LinearLayout.HORIZONTAL);
        item.setGravity(Gravity.CENTER_VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(10));
        item.setBackground(bg);
        item.setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14));

        // accent bar
        View accent = new View(context);
        GradientDrawable accentBg = new GradientDrawable();
        accentBg.setColor(parseColor("#00FF88"));
        accentBg.setCornerRadius(dpToPx(2));
        accent.setBackground(accentBg);
        LinearLayout.LayoutParams accentLp = new LinearLayout.LayoutParams(dpToPx(3), dpToPx(40));
        accentLp.rightMargin = dpToPx(12);
        accent.setLayoutParams(accentLp);
        item.addView(accent);

        // content
        LinearLayout content = new LinearLayout(context);
        content.setOrientation(LinearLayout.VERTICAL);

        TextView title = new TextView(context);
        String titleText = "";
        if (data instanceof String) {
            titleText = (String) data;
        } else if (data instanceof org.json.JSONObject) {
            try {
                org.json.JSONObject obj = (org.json.JSONObject) data;
                titleText = obj.optString("title", obj.optString("name",
                            obj.optString("label", obj.toString())));
            } catch (Exception e) { titleText = data.toString(); }
        } else {
            titleText = data.toString();
        }

        title.setText(titleText);
        title.setTextColor(parseColor("#FFFFFF"));
        title.setTextSize(15);
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        content.addView(title);

        item.addView(content);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dpToPx(8);
        item.setLayoutParams(lp);

        int nid = nodeId;
        item.setOnClickListener(v -> {
            BlinkUIActivity.animateButtonPress(v);
            v.postDelayed(() -> activity.handleEvent(nid, BlinkUIBridge.EVENT_TAP), 80);
        });

        return item;
    }

    private View buildAICard(JSONObject node, int nodeId) throws Exception {
        // AICard — generates card UI from prompt
        String prompt = node.optString("prompt", "");
        String type   = detectCardType(prompt);

        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(parseColor("#1A1A1A"));
        bg.setCornerRadius(dpToPx(16));
        bg.setStroke(dpToPx(1), parseColor("#2A2A2A"));
        card.setBackground(bg);
        card.setElevation(dpToPx(4));
        card.setPadding(dpToPx(20), dpToPx(20), dpToPx(20), dpToPx(20));

        // AI-generated header
        View accentLine = new View(context);
        GradientDrawable accentBg = new GradientDrawable();
        accentBg.setColor(parseColor("#00FF88"));
        accentBg.setCornerRadius(dpToPx(2));
        accentLine.setBackground(accentBg);
        LinearLayout.LayoutParams alp = new LinearLayout.LayoutParams(dpToPx(32), dpToPx(3));
        alp.bottomMargin = dpToPx(16);
        accentLine.setLayoutParams(alp);
        card.addView(accentLine);

        // prompt as subtitle
        TextView promptLabel = new TextView(context);
        promptLabel.setText("✦ " + prompt);
        promptLabel.setTextColor(parseColor("#00FF88"));
        promptLabel.setTextSize(11);
        LinearLayout.LayoutParams plp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        plp.bottomMargin = dpToPx(8);
        promptLabel.setLayoutParams(plp);
        card.addView(promptLabel);

        // render children if present
        org.json.JSONArray children = node.optJSONArray("children");
        if (children != null) {
            for (int i = 0; i < children.length(); i++) {
                org.json.JSONObject child = children.getJSONObject(i);
                card.addView(buildView(child, nodeId * 100 + i));
            }
        } else {
            // placeholder content
            TextView placeholder = new TextView(context);
            placeholder.setText("AI-generated: " + type);
            placeholder.setTextColor(parseColor("#555555"));
            placeholder.setTextSize(13);
            card.addView(placeholder);
        }

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dpToPx(12);
        card.setLayoutParams(lp);
        return card;
    }

    private String detectCardType(String prompt) {
        String p = prompt.toLowerCase();
        if (p.contains("profile") || p.contains("user")) return "profile";
        if (p.contains("product") || p.contains("price")) return "product";
        if (p.contains("stat") || p.contains("metric")) return "stats";
        if (p.contains("weather")) return "weather";
        return "info";
    }

    private View buildSmartForm(JSONObject node, int nodeId) throws Exception {
        LinearLayout form = new LinearLayout(context);
        form.setOrientation(LinearLayout.VERTICAL);
        form.setBackgroundColor(parseColor("#0F0F0F"));

        org.json.JSONArray fields = node.optJSONArray("fields");
        if (fields != null) {
            for (int i = 0; i < fields.length(); i++) {
                String fieldName = fields.getString(i);
                View field = buildSmartField(fieldName, nodeId * 100 + i);
                form.addView(field);
            }
        }

        // submit button
        Button submit = new Button(context);
        submit.setText(node.optString("submit_label", "Submit"));
        submit.setAllCaps(false);
        submit.setTextSize(16);
        submit.setTypeface(null, android.graphics.Typeface.BOLD);
        submit.setTextColor(parseColor("#0F0F0F"));
        GradientDrawable submitBg = new GradientDrawable();
        submitBg.setColor(parseColor("#00FF88"));
        submitBg.setCornerRadius(dpToPx(10));
        submit.setBackground(submitBg);
        submit.setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14));
        LinearLayout.LayoutParams slp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        slp.topMargin = dpToPx(16);
        submit.setLayoutParams(slp);
        int nid = nodeId;
        submit.setOnClickListener(v -> {
            BlinkUIActivity.animateButtonPress(v);
            v.postDelayed(() -> activity.handleEvent(nid, BlinkUIBridge.EVENT_TAP), 80);
        });
        form.addView(submit);

        return form;
    }

    private View buildSmartField(String fieldName, int nodeId) {
        LinearLayout wrapper = new LinearLayout(context);
        wrapper.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams wlp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        wlp.bottomMargin = dpToPx(12);
        wrapper.setLayoutParams(wlp);

        // label
        TextView label = new TextView(context);
        String labelText = fieldName.substring(0, 1).toUpperCase() +
                          fieldName.substring(1).replace("_", " ");
        label.setText(labelText);
        label.setTextColor(parseColor("#999999"));
        label.setTextSize(12);
        LinearLayout.LayoutParams llp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        llp.bottomMargin = dpToPx(4);
        label.setLayoutParams(llp);
        wrapper.addView(label);

        // input
        android.widget.EditText input = new android.widget.EditText(context);
        String f = fieldName.toLowerCase();
        if (f.contains("password") || f.contains("pass")) {
            input.setInputType(android.text.InputType.TYPE_CLASS_TEXT |
                               android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
        } else if (f.contains("email")) {
            input.setInputType(android.text.InputType.TYPE_CLASS_TEXT |
                               android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        } else if (f.contains("phone") || f.contains("mobile")) {
            input.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        } else if (f.contains("age") || f.contains("count") || f.contains("amount")) {
            input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        }

        input.setHint("Enter " + labelText.toLowerCase());
        input.setHintTextColor(parseColor("#444444"));
        input.setTextColor(parseColor("#FFFFFF"));
        input.setTextSize(15);
        GradientDrawable inputBg = new GradientDrawable();
        inputBg.setColor(parseColor("#1A1A1A"));
        inputBg.setCornerRadius(dpToPx(8));
        inputBg.setStroke(dpToPx(1), parseColor("#2A2A2A"));
        input.setBackground(inputBg);
        input.setPadding(dpToPx(14), dpToPx(12), dpToPx(14), dpToPx(12));
        wrapper.addView(input);

        return wrapper;
    }

    private View buildAutoStyle(JSONObject node, int nodeId) throws Exception {
        // render child with auto-detected styling
        org.json.JSONArray children = node.optJSONArray("children");
        if (children != null && children.length() > 0) {
            return buildView(children.getJSONObject(0), nodeId);
        }
        return buildText(node, nodeId, 16, false);
    }

    private View buildSmartText(JSONObject node, int nodeId) throws Exception {
        String value  = node.optString("content", "");
        String format = node.optString("format", detectFormat(value));

        TextView tv = new TextView(context);
        tv.setTextSize(node.optInt("font_size", 16));
        tv.setLayoutParams(new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        switch (format) {
            case "currency":
                tv.setText(value);
                tv.setTextColor(parseColor("#00FF88"));
                tv.setTypeface(null, android.graphics.Typeface.BOLD);
                break;
            case "error":
                tv.setText("⚠ " + value);
                tv.setTextColor(parseColor("#FF3B30"));
                break;
            case "success":
                tv.setText("✓ " + value);
                tv.setTextColor(parseColor("#00FF88"));
                break;
            case "percentage":
                tv.setText(value);
                tv.setTextColor(parseColor("#0A84FF"));
                tv.setTypeface(null, android.graphics.Typeface.BOLD);
                break;
            default:
                tv.setText(value);
                tv.setTextColor(parseColor("#FFFFFF"));
        }
        return tv;
    }

    private String detectFormat(String value) {
        if (value.startsWith("$") || value.startsWith("₦")) return "currency";
        if (value.toLowerCase().contains("error")) return "error";
        if (value.toLowerCase().contains("success")) return "success";
        try {
            double d = Double.parseDouble(value.replace("%",""));
            if (value.endsWith("%")) return "percentage";
        } catch (Exception ignored) {}
        return "text";
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
