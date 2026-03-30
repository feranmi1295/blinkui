#include <jni.h>
#include <string.h>
#include <stdlib.h>
#include <android/log.h>

#define LOG_TAG "BlinkUI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

static JavaVM* g_jvm      = NULL;
static jobject g_activity = NULL;

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    g_jvm = vm;
    LOGI("BlinkUI JNI loaded");
    return JNI_VERSION_1_6;
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeSetActivity(
    JNIEnv* env, jobject thiz, jobject activity
) {
    if (g_activity) (*env)->DeleteGlobalRef(env, g_activity);
    g_activity = (*env)->NewGlobalRef(env, activity);
}

// Call Java renderTree() from C
void bk_call_render(const char* tree_json) {
    if (!g_jvm || !g_activity) return;
    JNIEnv* env;
    int attached = 0;
    if ((*g_jvm)->GetEnv(g_jvm, (void**)&env, JNI_VERSION_1_6) == JNI_EDETACHED) {
        (*g_jvm)->AttachCurrentThread(g_jvm, &env, NULL);
        attached = 1;
    }
    jclass    cls    = (*env)->GetObjectClass(env, g_activity);
    jmethodID method = (*env)->GetMethodID(env, cls, "renderTree", "(Ljava/lang/String;)V");
    if (method) {
        jstring json = (*env)->NewStringUTF(env, tree_json);
        (*env)->CallVoidMethod(env, g_activity, method, json);
        (*env)->DeleteLocalRef(env, json);
    }
    if (attached) (*g_jvm)->DetachCurrentThread(g_jvm);
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeInit(
    JNIEnv* env, jobject thiz
) {
    LOGI("BlinkUI C runtime initializing...");
    return (*env)->NewStringUTF(env, "BlinkUI runtime initialized");
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeRender(
    JNIEnv* env, jobject thiz, jstring tree_json
) {
    const char* json = (*env)->GetStringUTFChars(env, tree_json, 0);
    LOGI("Rendering: %.80s...", json);
    (*env)->ReleaseStringUTFChars(env, tree_json, json);
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeFireEvent(
    JNIEnv* env, jobject thiz,
    jint node_id, jint event_type, jfloat x, jfloat y
) {
    LOGI("Event: node=%d type=%d", node_id, event_type);
    // Event handling now done in Java → Python
    // This is called but Java intercepts first
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTick(
    JNIEnv* env, jobject thiz, jlong delta_ms
) {}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetVersion(
    JNIEnv* env, jobject thiz
) {
    return (*env)->NewStringUTF(env, "0.1.0");
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetInitialTree(
    JNIEnv* env, jobject thiz
) {
    // fallback tree if Python isn't ready yet
    return (*env)->NewStringUTF(env,
        "{\"type\":\"VStack\",\"padding\":[24,24,24,24],"
        "\"background\":\"#F2F2F7\",\"corner_radius\":0,"
        "\"opacity\":1.0,\"visible\":true,\"margin\":[0,0,0,0],"
        "\"children\":[{\"type\":\"Text\",\"content\":\"Loading Python...\","
        "\"font_size\":20,\"bold\":true,\"color\":\"#1C1C1E\","
        "\"padding\":[0,0,0,0],\"margin\":[0,0,0,0],"
        "\"opacity\":1.0,\"visible\":true,\"children\":[]}]}"
    );
}
