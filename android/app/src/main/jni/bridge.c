// ─────────────────────────────────────────
// BlinkUI Android Bridge
// Connects C runtime to Android Views
// via JNI (Java Native Interface)
// ─────────────────────────────────────────

#include <jni.h>
#include <string.h>
#include <stdlib.h>
#include <android/log.h>

#define LOG_TAG "BlinkUI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// ─────────────────────────────────────────
// JNI function naming convention:
// Java_<package>_<class>_<method>
// ─────────────────────────────────────────

// Called when BlinkUI starts up
JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeInit(
    JNIEnv* env,
    jobject thiz
) {
    LOGI("BlinkUI C runtime initializing...");
    // TODO: call bk_runtime_init() from blinkui.c
    return (*env)->NewStringUTF(env, "BlinkUI runtime initialized");
}

// Called with the component tree JSON from Python
JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeRender(
    JNIEnv*  env,
    jobject  thiz,
    jstring  tree_json
) {
    const char* json = (*env)->GetStringUTFChars(env, tree_json, 0);
    LOGI("Rendering tree: %.100s...", json);

    // TODO: parse JSON, build BKNode tree, run reconciler
    // For now log that we received the tree

    (*env)->ReleaseStringUTFChars(env, tree_json, json);
}

// Called when user taps a view
JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeFireEvent(
    JNIEnv* env,
    jobject thiz,
    jint    node_id,
    jint    event_type,
    jfloat  x,
    jfloat  y
) {
    LOGI("Event fired: node=%d type=%d x=%.1f y=%.1f",
         node_id, event_type, x, y);

    // TODO: call bk_events_fire() from events.c
}

// Called every frame for animations
JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTick(
    JNIEnv* env,
    jobject thiz,
    jlong   delta_ms
) {
    // TODO: call bk_anim_tick() from animation.c
}

// Returns current runtime version
JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetVersion(
    JNIEnv* env,
    jobject thiz
) {
    return (*env)->NewStringUTF(env, "0.1.0");
}