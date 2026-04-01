// ─────────────────────────────────────────
// BlinkUI App Bridge
// Connects transpiled screen .so to Android
// ─────────────────────────────────────────

#include <jni.h>
#include <android/log.h>
#include <stdlib.h>
#include <string.h>

#define LOG_TAG "BlinkUI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// ── Forward declarations from generated C ──
// These are compiled into the same .so by CMake

typedef struct _HomeScreen HomeScreen;
HomeScreen* HomeScreen_init(void);
char*       HomeScreen_get_tree(HomeScreen* self);
void        HomeScreen_on_event(HomeScreen* self, int node_id, int event_type);

typedef struct _DetailScreen DetailScreen;
DetailScreen* DetailScreen_init(void);
char*         DetailScreen_get_tree(DetailScreen* self);
void          DetailScreen_on_event(DetailScreen* self, int node_id, int event_type);

// ── Global state ──
static JavaVM* g_jvm         = NULL;
static jobject g_activity     = NULL;
static HomeScreen*   g_home   = NULL;
static DetailScreen* g_detail = NULL;
static int g_current_screen   = 0; // 0=home, 1=detail

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    g_jvm = vm;
    LOGI("BlinkUI App Bridge loaded");
    return JNI_VERSION_1_6;
}

// Call Java renderTree() from C
static void call_render(const char* tree_json) {
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

// bk_request_render — called by generated handlers
void bk_request_render(void* screen) {
    char* tree = NULL;
    if (g_current_screen == 0 && g_home) {
        tree = HomeScreen_get_tree(g_home);
    } else if (g_current_screen == 1 && g_detail) {
        tree = DetailScreen_get_tree(g_detail);
    }
    if (tree) {
        LOGI("Re-rendering after state change");
        // call renderTree for crossfade animation
        call_render(tree);
    }
}

// bk_navigate — called by go_detail, go_back etc
void bk_navigate(int screen_index) {
    g_current_screen = screen_index;

    // get new tree
    char* tree = NULL;
    if (screen_index == 0 && g_home) {
        tree = HomeScreen_get_tree(g_home);
    } else if (screen_index == 1 && g_detail) {
        tree = DetailScreen_get_tree(g_detail);
    }
    if (!tree) return;

    // call navigateTo on activity for animated transition
    if (!g_jvm || !g_activity) return;
    JNIEnv* env;
    int attached = 0;
    if ((*g_jvm)->GetEnv(g_jvm, (void**)&env, JNI_VERSION_1_6) == JNI_EDETACHED) {
        (*g_jvm)->AttachCurrentThread(g_jvm, &env, NULL);
        attached = 1;
    }
    jclass    cls    = (*env)->GetObjectClass(env, g_activity);
    jmethodID method = (*env)->GetMethodID(env, cls, "navigateTo", "(I)V");
    if (method) {
        (*env)->CallVoidMethod(env, g_activity, method, (jint)screen_index);
    }
    // store tree for navigateTo to use
    call_render(tree);
    if (attached) (*g_jvm)->DetachCurrentThread(g_jvm);
}

// ── JNI methods ──

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeSetActivity(
    JNIEnv* env, jobject thiz, jobject activity
) {
    if (g_activity) (*env)->DeleteGlobalRef(env, g_activity);
    g_activity = (*env)->NewGlobalRef(env, activity);
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeInit(
    JNIEnv* env, jobject thiz
) {
    // init all screens
    g_home   = HomeScreen_init();
    g_detail = DetailScreen_init();
    LOGI("Screens initialized: home=%p detail=%p", g_home, g_detail);
    return (*env)->NewStringUTF(env, "BlinkUI screens initialized");
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetInitialTree(
    JNIEnv* env, jobject thiz
) {
    if (!g_home) g_home = HomeScreen_init();
    char* tree = HomeScreen_get_tree(g_home);
    LOGI("Initial tree: %.80s...", tree);
    return (*env)->NewStringUTF(env, tree);
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeFireEvent(
    JNIEnv* env, jobject thiz,
    jint node_id, jint event_type, jfloat x, jfloat y
) {
    LOGI("Event: node=%d type=%d screen=%d", node_id, event_type, g_current_screen);

    if (g_current_screen == 0 && g_home) {
        HomeScreen_on_event(g_home, node_id, event_type);
    } else if (g_current_screen == 1 && g_detail) {
        DetailScreen_on_event(g_detail, node_id, event_type);
    }
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeRender(
    JNIEnv* env, jobject thiz, jstring tree_json
) {}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTick(
    JNIEnv* env, jobject thiz, jlong delta_ms
) {}

// Text field change — store value in screen state
// For now just log it; full binding requires state name map
JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTextChange(
    JNIEnv* env, jobject thiz, jint node_id, jstring text
) {
    const char* str = (*env)->GetStringUTFChars(env, text, 0);
    LOGI("TextField node=%d value=%s", node_id, str);
    (*env)->ReleaseStringUTFChars(env, text, str);
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetVersion(
    JNIEnv* env, jobject thiz
) {
    return (*env)->NewStringUTF(env, "0.1.0");
}
