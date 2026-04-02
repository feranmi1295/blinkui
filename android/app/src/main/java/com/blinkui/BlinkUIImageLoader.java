package com.blinkui;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.ImageView;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * BlinkUI Image Loader
 * Async image loading with memory cache
 */
public class BlinkUIImageLoader {

    private static final String TAG = "BlinkUI-Image";

    private static final java.util.Map<String, Bitmap> cache =
        new java.util.concurrent.ConcurrentHashMap<>();

    private static final ExecutorService executor =
        Executors.newFixedThreadPool(3);

    private static final Handler handler =
        new Handler(Looper.getMainLooper());

    public static void load(String url, ImageView imageView) {
        // check cache first
        if (cache.containsKey(url)) {
            imageView.setImageBitmap(cache.get(url));
            return;
        }

        // placeholder — dark grey
        imageView.setBackgroundColor(android.graphics.Color.parseColor("#1A1A1A"));

        executor.execute(() -> {
            try {
                Bitmap bitmap = downloadBitmap(url);
                if (bitmap != null) {
                    cache.put(url, bitmap);
                    handler.post(() -> {
                        imageView.setImageBitmap(bitmap);
                        imageView.setBackground(null);
                        // fade in
                        imageView.setAlpha(0f);
                        imageView.animate().alpha(1f).setDuration(200).start();
                    });
                }
            } catch (Exception e) {
                Log.e(TAG, "Load failed: " + url + " — " + e.getMessage());
            }
        });
    }

    private static Bitmap downloadBitmap(String urlStr) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(8000);
        conn.connect();

        try (InputStream is = conn.getInputStream()) {
            return BitmapFactory.decodeStream(is);
        }
    }

    public static void clearCache() {
        cache.clear();
    }
}
