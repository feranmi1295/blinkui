package com.blinkui;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;

/**
 * BlinkUI Network Layer
 * Handles HTTP requests from transpiled C screens
 * Callbacks route through JNI back to C handlers
 */
public class BlinkUINetwork {

    private static final String TAG = "BlinkUI-Network";

    private final ExecutorService executor = Executors.newFixedThreadPool(4);
    private final Handler         handler  = new Handler(Looper.getMainLooper());
    private final BlinkUIActivity activity;

    // pending request callbacks: request_id → screen pointer (as long)
    private final java.util.Map<Integer, Long> pendingRequests =
        new java.util.concurrent.ConcurrentHashMap<>();

    public BlinkUINetwork(BlinkUIActivity activity) {
        this.activity = activity;
    }

    // ── Called from C via JNI ──

    public void get(String url, int requestId) {
        Log.i(TAG, "GET " + url + " [id=" + requestId + "]");
        executor.execute(() -> {
            try {
                String response = httpGet(url);
                onResponse(requestId, 200, response);
            } catch (Exception e) {
                Log.e(TAG, "GET failed: " + e.getMessage());
                onResponse(requestId, 500, e.getMessage());
            }
        });
    }

    public void post(String url, String body, int requestId) {
        Log.i(TAG, "POST " + url + " [id=" + requestId + "]");
        executor.execute(() -> {
            try {
                String response = httpPost(url, body);
                onResponse(requestId, 200, response);
            } catch (Exception e) {
                Log.e(TAG, "POST failed: " + e.getMessage());
                onResponse(requestId, 500, e.getMessage());
            }
        });
    }

    private void onResponse(int requestId, int status, String body) {
        // deliver response back to C runtime on main thread
        handler.post(() ->
            activity.getBridge().nativeHttpResponse(requestId, status, body)
        );
    }

    // ── HTTP implementation ──

    private String httpGet(String urlStr) throws IOException {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");
        conn.setConnectTimeout(10000);
        conn.setReadTimeout(10000);

        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) sb.append(line);
        }
        return sb.toString();
    }

    private String httpPost(String urlStr, String body) throws IOException {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);
        conn.setConnectTimeout(10000);
        conn.setReadTimeout(10000);

        if (body != null) {
            try (OutputStream os = conn.getOutputStream()) {
                os.write(body.getBytes("UTF-8"));
            }
        }

        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) sb.append(line);
        }
        return sb.toString();
    }
}
