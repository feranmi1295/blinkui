package com.blinkui;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.Socket;

/**
 * BlinkUI Hot Reload Client
 * Connects to laptop hot reload server over WiFi
 * Receives screen updates and applies them instantly
 */
public class HotReloadClient {

    private static final String TAG  = "BlinkUI-HotReload";
    private static final int    PORT = 8974;

    private final BlinkUIActivity activity;
    private final Handler         handler;
    private       Thread          thread;
    private       boolean         running = false;
    private       String          serverIp;

    public HotReloadClient(BlinkUIActivity activity) {
        this.activity = activity;
        this.handler  = new Handler(Looper.getMainLooper());
    }

    public void connect(String serverIp) {
        this.serverIp = serverIp;
        this.running  = true;

        thread = new Thread(() -> {
            while (running) {
                try {
                    Log.i(TAG, "Connecting to " + serverIp + ":" + PORT);
                    Socket socket = new Socket(serverIp, PORT);
                    Log.i(TAG, "Connected to hot reload server");

                    BufferedReader reader = new BufferedReader(
                        new InputStreamReader(socket.getInputStream())
                    );

                    String line;
                    while ((line = reader.readLine()) != null && running) {
                        processMessage(line);
                    }

                    socket.close();
                    Log.i(TAG, "Disconnected from hot reload server");

                } catch (Exception e) {
                    Log.w(TAG, "Connection failed: " + e.getMessage());
                    // retry after 2 seconds
                    try { Thread.sleep(2000); } catch (InterruptedException ie) { break; }
                }
            }
        });
        thread.setDaemon(true);
        thread.start();
    }

    private void processMessage(String message) {
        try {
            JSONObject payload = new JSONObject(message);
            String type = payload.getString("type");

            if (type.equals("screen_update")) {
                String     screenName = payload.getString("screen");
                JSONObject tree       = payload.getJSONObject("tree");

                Log.i(TAG, "Hot reload: " + screenName);

                handler.post(() -> {
                    try {
                        activity.renderTree(tree.toString());
                        Log.i(TAG, "Applied hot reload for " + screenName);
                    } catch (Exception e) {
                        Log.e(TAG, "Apply error: " + e.getMessage());
                    }
                });
            }

        } catch (Exception e) {
            Log.e(TAG, "Message parse error: " + e.getMessage());
        }
    }

    public void disconnect() {
        running = false;
        if (thread != null) thread.interrupt();
    }
}
