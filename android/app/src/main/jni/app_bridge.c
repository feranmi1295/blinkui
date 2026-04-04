#include <jni.h>
#include <android/log.h>
#include <stdlib.h>
#include <string.h>

#define LOG_TAG "BlinkUI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// ── Forward declarations ──
typedef struct _ChatsScreen   ChatsScreen;
typedef struct _ChatScreen    ChatScreen;
typedef struct _StatusScreen  StatusScreen;
typedef struct _CallsScreen   CallsScreen;
typedef struct _ProfileScreen ProfileScreen;

ChatsScreen*   ChatsScreen_init(void);
char*          ChatsScreen_get_tree(ChatsScreen* self);
void           ChatsScreen_on_event(ChatsScreen* self, int node_id, int event_type);

ChatScreen*    ChatScreen_init(void);
char*          ChatScreen_get_tree(ChatScreen* self);
void           ChatScreen_on_event(ChatScreen* self, int node_id, int event_type);

StatusScreen*  StatusScreen_init(void);
char*          StatusScreen_get_tree(StatusScreen* self);
void           StatusScreen_on_event(StatusScreen* self, int node_id, int event_type);

CallsScreen*   CallsScreen_init(void);
char*          CallsScreen_get_tree(CallsScreen* self);
void           CallsScreen_on_event(CallsScreen* self, int node_id, int event_type);

ProfileScreen* ProfileScreen_init(void);
char*          ProfileScreen_get_tree(ProfileScreen* self);
void           ProfileScreen_on_event(ProfileScreen* self, int node_id, int event_type);

// ── Global state ──
static JavaVM*        g_jvm      = NULL;
static jobject        g_activity = NULL;
static ChatsScreen*   g_chats    = NULL;
static ChatScreen*    g_chat     = NULL;
static StatusScreen*  g_status   = NULL;
static CallsScreen*   g_calls    = NULL;
static ProfileScreen* g_profile  = NULL;
static int            g_screen   = 0;
// 0=chats 1=chat 2=status 3=calls 4=profile

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    g_jvm = vm;
    return JNI_VERSION_1_6;
}

static void call_render(const char* json) {
    if (!g_jvm || !g_activity) return;
    JNIEnv* env;
    int attached = 0;
    if ((*g_jvm)->GetEnv(g_jvm, (void**)&env, JNI_VERSION_1_6) == JNI_EDETACHED) {
        (*g_jvm)->AttachCurrentThread(g_jvm, &env, NULL);
        attached = 1;
    }
    jclass    cls = (*env)->GetObjectClass(env, g_activity);
    jmethodID m   = (*env)->GetMethodID(env, cls, "renderTree", "(Ljava/lang/String;)V");
    if (m) {
        jstring js = (*env)->NewStringUTF(env, json);
        (*env)->CallVoidMethod(env, g_activity, m, js);
        (*env)->DeleteLocalRef(env, js);
    }
    if (attached) (*g_jvm)->DetachCurrentThread(g_jvm);
}

void bk_request_render(void* screen) {
    char* tree = NULL;
    switch (g_screen) {
        case 0: if (g_chats)   tree = ChatsScreen_get_tree(g_chats);   break;
        case 1: if (g_chat)    tree = ChatScreen_get_tree(g_chat);     break;
        case 2: if (g_status)  tree = StatusScreen_get_tree(g_status); break;
        case 3: if (g_calls)   tree = CallsScreen_get_tree(g_calls);   break;
        case 4: if (g_profile) tree = ProfileScreen_get_tree(g_profile);break;
    }
    if (tree) call_render(tree);
}

void bk_navigate(int screen_index) {
    g_screen = screen_index;
    bk_request_render(NULL);
}

void bk_toast(const char* message, const char* type) {
    if (!g_jvm || !g_activity) return;
    JNIEnv* env;
    int attached = 0;
    if ((*g_jvm)->GetEnv(g_jvm, (void**)&env, JNI_VERSION_1_6) == JNI_EDETACHED) {
        (*g_jvm)->AttachCurrentThread(g_jvm, &env, NULL);
        attached = 1;
    }
    jstring jmsg  = (*env)->NewStringUTF(env, message);
    jstring jtype = (*env)->NewStringUTF(env, type);
    jclass    cls = (*env)->GetObjectClass(env, g_activity);
    jmethodID m   = (*env)->GetMethodID(env, cls,
        "showToast", "(Ljava/lang/String;Ljava/lang/String;I)V");
    if (m) (*env)->CallVoidMethod(env, g_activity, m, jmsg, jtype, (jint)2500);
    (*env)->DeleteLocalRef(env, jmsg);
    (*env)->DeleteLocalRef(env, jtype);
    if (attached) (*g_jvm)->DetachCurrentThread(g_jvm);
}

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
    g_chats   = ChatsScreen_init();
    g_chat    = ChatScreen_init();
    g_status  = StatusScreen_init();
    g_calls   = CallsScreen_init();
    g_profile = ProfileScreen_init();
    LOGI("WhatsApp clone screens initialized");
    return (*env)->NewStringUTF(env, "BlinkUI WhatsApp clone ready");
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetInitialTree(
    JNIEnv* env, jobject thiz
) {
    if (!g_chats) g_chats = ChatsScreen_init();
    return (*env)->NewStringUTF(env, ChatsScreen_get_tree(g_chats));
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeFireEvent(
    JNIEnv* env, jobject thiz,
    jint node_id, jint event_type, jfloat x, jfloat y
) {
    LOGI("Event: node=%d screen=%d", node_id, g_screen);
    switch (g_screen) {
        case 0: if (g_chats)   ChatsScreen_on_event(g_chats, node_id, event_type);   break;
        case 1: if (g_chat)    ChatScreen_on_event(g_chat, node_id, event_type);     break;
        case 2: if (g_status)  StatusScreen_on_event(g_status, node_id, event_type); break;
        case 3: if (g_calls)   CallsScreen_on_event(g_calls, node_id, event_type);   break;
        case 4: if (g_profile) ProfileScreen_on_event(g_profile, node_id, event_type);break;
    }
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetTabConfig(
    JNIEnv* env, jobject thiz
) {
    return (*env)->NewStringUTF(env,
        "{\"tabs\":["
        "{\"label\":\"Chats\", \"icon\":\"chat\"},"
        "{\"label\":\"Status\",\"icon\":\"star\"},"
        "{\"label\":\"Calls\", \"icon\":\"phone\"}"
        "]}"
    );
}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetTabTree(
    JNIEnv* env, jobject thiz, jint tab_index
) {
    char* tree = NULL;
    switch (tab_index) {
        case 0: g_screen = 0; tree = ChatsScreen_get_tree(g_chats);   break;
        case 1: g_screen = 2; tree = StatusScreen_get_tree(g_status); break;
        case 2: g_screen = 3; tree = CallsScreen_get_tree(g_calls);   break;
    }
    if (!tree) tree = "{}";
    return (*env)->NewStringUTF(env, tree);
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeRender(
    JNIEnv* env, jobject thiz, jstring tree_json) {}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTick(
    JNIEnv* env, jobject thiz, jlong delta_ms) {}

JNIEXPORT jstring JNICALL
Java_com_blinkui_BlinkUIBridge_nativeGetVersion(
    JNIEnv* env, jobject thiz
) {
    return (*env)->NewStringUTF(env, "0.4.0");
}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeHttpResponse(
    JNIEnv* env, jobject thiz,
    jint request_id, jint status, jstring body) {}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeHttpGet(
    JNIEnv* env, jobject thiz,
    jstring url, jint request_id) {}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeTextChange(
    JNIEnv* env, jobject thiz,
    jint node_id, jstring text) {}

JNIEXPORT void JNICALL
Java_com_blinkui_BlinkUIBridge_nativeShowToast(
    JNIEnv* env, jobject thiz,
    jstring message, jstring type, jint duration) {}
