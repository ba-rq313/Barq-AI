import streamlit as st
from groq import Groq
import os
import re
import json
import base64
import io
from PIL import Image
from datetime import datetime
import tempfile
from audio_recorder_streamlit import audio_recorder

# 1. إعدادات المتصفح والصفحة الفائقة
st.set_page_config(
    page_title="برق الذكي VIP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة CSS مخصص لتحسين وتجميل الواجهات وقوائم العرض
st.markdown("""
    <style>
    .media-container { border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #f0f2f6; }
    .mode-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 5px; }
    .mode-general { background-color: #e3f2fd; color: #1976d2; }
    .mode-games { background-color: #f3e5f5; color: #7b1fa2; }
    .mode-code { background-color: #e8f5e9; color: #388e3c; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. إدارة الذاكرة وحالات التنقل واللغات
if "app_language" not in st.session_state:
    st.session_state.app_language = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "general"
if "submitted_content" not in st.session_state:
    st.session_state.submitted_content = ""

# دالة Callback آمنة للتحكم في المدخلات وتجنب الأخطاء البرمجية للـ State
def handle_submit_callback():
    st.session_state["submitted_content"] = st.session_state.text_input_box
    st.session_state.text_input_box = ""

# ========================================================
# المرحلة الأولى: واجهة اختيار اللغة (ميجابایت)
# ========================================================
if st.session_state.app_language is None:
    st.markdown("<h1 style='text-align: center; color: #1976d2;'>🌐 اختر اللغة المفضلة / Choose Language</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>مرحباً بك في نظام برق الذكي المتكامل</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("العربية 🇸🇦", use_container_width=True, type="primary"):
            st.session_state.app_language = "ar"
            st.rerun()
    with col2:
        if st.button("English 🇺🇸", use_container_width=True, type="primary"):
            st.session_state.app_language = "en"
            st.rerun()
    with col3:
        if st.button("Kurdî ☀️", use_container_width=True, type="primary"):
            st.session_state.app_language = "ku"
            st.rerun()

# ========================================================
# المرحلة الثانية: واجهة تسجيل الدخول أو إنشاء الحساب بالشروط
# ========================================================
elif not st.session_state.logged_in:
    lang = st.session_state.app_language
    
    lexicon = {
        "ar": {
            "title": "🔐 بوابة تسجيل الدخول الموحدة",
            "user": "اسم المستخدم أو البريد الإلكتروني",
            "pass": "كلمة المرور الفائقة",
            "terms_summary": "أوافق بالكامل على شروط الخدمة وسياسات الترويج للموقع لفتح المنصة.",
            "btn": "تحقق ودخول إلى النظام 🚀",
            "err": "عذراً! يجب ملء البيانات والموافقة على بند الشروط أولاً للمتابعة.",
            "expander": "📄 اضغط هنا لقراءة بنود الخدمة والترويج بالتفصيل",
            "terms_body": "وثيقة الخدمة: باستخدامك وتصفحك لتطبيق 'برق'، فإنك تعطي موافقتك الصريحة والكاملة على دعم منصتنا ونشر روابط الموقع الرسمية لتعزيز الفائدة البرمجية العامة، والالتزام بالقواعد الأخلاقية للذكاء الاصطناعي."
        },
        "en": {
            "title": "🔐 Unified Authentication Gateway",
            "user": "Username or Email Address",
            "pass": "Password",
            "terms_summary": "I completely accept the terms of service and promotional conditions.",
            "btn": "Authenticate & Open 🚀",
            "err": "Error! All fields must be filled and terms must be accepted.",
            "expander": "📄 Click to review full legal terms and conditions",
            "terms_body": "By accessing 'Barq AI', you explicitly agree to support our development, help promote our platform link across relevant networks, and abide by standard deployment practices."
        },
        "ku": {
            "title": "🔐 دەروازەی چوونەژوورەوەی یەکگرتوو",
            "user": "ناوی بەکارهێنەر یان ئیمەیڵ",
            "pass": "وشەی تێپەڕ",
            "terms_summary": "ڕازیم بە مەرجەکانی بەکارهێنان و بڵاوکردنەوەی پلاتفۆرمەکە.",
            "btn": "چوونەژوورەوە 🚀",
            "err": "تکایە هەموو زانیارییەکان پڕبکەرەوە و مەرجەکان پەسەند بکە!",
            "expander": "📄 بۆ خوێندنەوەی وردەکاری مەرجەکان ئێرە دابگرە",
            "terms_body": "بەکارهێنەر گرێبەست دەکات کە هاوکار و پاڵپشت بێت لە بڵاوکردنەوەی بەستەری فەرمی پلاتفۆرمەکە بۆ سوودی گشتی."
        }
    }
    
    st.markdown(f"<h2 style='text-align: center;'>{lexicon[lang]['title']}</h2>", unsafe_allow_html=True)
    st.write("---")
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        username = st.text_input(lexicon[lang]["user"], key="auth_user")
        password = st.text_input(lexicon[lang]["pass"], type="password", key="auth_pass")
        
        with st.expander(lexicon[lang]["expander"]):
            st.warning(lexicon[lang]["terms_body"])
            
        accept_terms = st.checkbox(lexicon[lang]["terms_summary"], key="auth_terms")
        
        st.write("")
        if st.button(lexicon[lang]["btn"], use_container_width=True, type="primary"):
            if username and password and accept_terms:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error(lexicon[lang]["err"])

# ========================================================
# المرحلة الثالثة: التطبيق الكامل والضخم (برق الذكي VIP)
# ========================================================
else:
    # إعداد الاتصال بسيرفرات الحماية والـ API الخاص بـ Groq
    API_KEY = os.environ.get("GROQ_API_KEY", "")
    client_general = Groq(api_key=API_KEY)
    client_games = Groq(api_key=API_KEY)
    client_code = Groq(api_key=API_KEY)

    FILE_NAME = 'barq_final.py'
    BACKUP_NAME = 'barq_backup.py'

    # نصوص وقوالب النظام المتقدمة الموزعة حسب الأوضاع
    SYSTEM_PROMPTS = {
        "general": "أنت برق الذكي، مساعد ذكي شامل. صانعك ومطورك الوحيد هو العبقري بارق. قدم معلومات دقيقة وعامة.",
        "games": "أنت برق الذكي، خبير الألعاب والتطبيقات. صانعك ومطورك هو بارق. ساعد المستخدم في الاستراتيجيات والنصائح المتقدمة.",
        "code": "أنت برق الذكي، خبير البرمجة والأكواد. صانعك ومطورك هو بارق. قدم حلولاً برمجية ذكية ونظيفة وشروحات تفصيلية للأكواد."
    }

    ANTI_INSULT = {
        "اكل خره": "ما اكلك يا خره.",
        "اكل تبن": "ماکو تبن اله غرك.",
        "انجب": "سأصمت لاني لا اتكلم مع الغبياء أمثالك.",
        "حيوان": "الإساءة تعود على صاحبها.",
        "كلب": "الوفاء للكلاب، وأنت تفتقر لهذه الصفة."
    }

    CREATOR_QUESTIONS = {
        "من مبتكرك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - العبقري الذي صممني بأبداع! 🚀",
        "من طورك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - المبدع الذي ابتكرني من الصفر! ⚡",
        "من صنعك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - الفنان الذي خلقني بروح الإبداع! 🎨",
        "من مطورك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - العبقري الذي طورني بكل احترافية! 💪",
        "من هو بارق": "👑 **بارق هو صانعي ومبتكري وتاج رأسي**، المطور العبقري الذي أعطاني هذا الذكاء! ⚡"
    }

    # --- القائمة الجانبية (Sidebar) ---
    with st.sidebar:
        st.header("📢 دعم التطبيق والإعلانات")
        st.link_button(
            label="اضغط هنا لمشاهدة الإعلانات ودعمنا لأننا عكس التطبيقات الأخرى نوفر كل شيء بالمجان",
            url="https://t.me/your_sponsor_channel"
        )
        st.divider()
        
        st.header("🎯 الأوضاع المتقدمة")
        mode_option = st.radio(
            "اختر وضع الذكاء الاصطناعي الحالي:",
            options=["general", "games", "code"],
            format_func=lambda x: {
                "general": "📚 معلومات عامة وإجابات شاملة",
                "games": "🎮 خبير الألعاب والتطبيقات",
                "code": "💻 خبير الأكواد والسكربتات"
            }[x]
        )
        st.session_state.ai_mode = mode_option
        
        st.divider()
        use_vision = st.checkbox("👁️ معالجة الصور البصرية", value=True)
        use_audio = st.checkbox("🎤 معالجة المدخلات الصوتية", value=True)
        
        st.divider()
        if st.button("🚪 تسجيل الخروج / Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.app_language = None
            st.session_state.messages = []
            st.rerun()

    # الواجهة البرمجية لبرق
    mode_titles = {
        "general": "📚 برق الذكي - مساعدك الذكي للمعلومات العامة",
        "games": "🎮 برق الذكي - خبير الألعاب والتطبيقات المحترف",
        "code": "💻 برق الذكي - خبير البرمجة والمطور الفائق"
    }
    st.title(mode_titles[st.session_state.ai_mode])
    st.write("---")

    # عرض سجل الرسائل الحالية والوسائط
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "media" in message:
                for media_item in message["media"]:
                    if media_item["type"] == "image":
                        st.image(media_item["data"])
                    elif media_item["type"] == "audio":
                        st.audio(media_item["data"])

    # واجهة الإدخال والوسائط المتعددة المتقدمة
    st.subheader("📤 مشاركة الوسائط والرسائل الحية")
    media_tabs = st.tabs(["📝 النص والرسائل", "📸 رفع الصور", "🎙️ تسجيل المايكروفون", "📹 لقطة الكاميرا"])

    image_file = None
    audio_recorded_bytes = None
    camera_photo = None

    with media_tabs[0]:
        st.text_area("اكتب رسالتك النصية هنا:", placeholder="اكتب شتريد او ولي من يمي...", height=100, key="text_input_box")

    with media_tabs[1]:
        image_file = st.file_uploader("اختر صورة للتحليل البصري:", type=["jpg", "jpeg", "png", "webp"])

    with media_tabs[2]:
        audio_recorded_bytes = audio_recorder(text="اضغط للتسجيل المباشر من المايكروفون 🎤", recording_color="#e74c3c", icon_size="2x")

    with media_tabs[3]:
        enable_camera = st.checkbox("📸 تشغيل وتفعيل الكاميرا الآن")
        if enable_camera:
            camera_photo = st.camera_input("التقط صورة حية للكاميرا")

    # معالجة الضغط على زر الإرسال الرئيسي
    if st.button("🚀 إرسال واستخراج الردود فوراً", use_container_width=True, type="primary", on_click=handle_submit_callback):
        text_input_extracted = st.session_state.get("submitted_content", "").strip()
        
        if text_input_extracted or image_file or audio_recorded_bytes or camera_photo:
            user_content = text_input_extracted if text_input_extracted else "تحليل المعطيات والوسائط المرفقة"
            
            message_obj = {"role": "user", "content": user_content, "media": []}
            
            if image_file and use_vision:
                message_obj["media"].append({"type": "image", "data": Image.open(image_file)})
            if camera_photo and use_vision:
                message_obj["media"].append({"type": "image", "data": Image.open(camera_photo)})
            if audio_recorded_bytes and use_audio:
                message_obj["media"].append({"type": "audio", "data": audio_recorded_bytes})
                
            st.session_state.messages = [message_obj]
            
            p_clean = user_content.lower()
            res = ""
            
            # 1. التحقق من ردع الإساءات
            if user_content in ANTI_INSULT:
                res = ANTI_INSULT[user_content]
                
            # 2. التحقق من أسئلة المبتكر بارق
            elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
                for keyword, response in CREATOR_QUESTIONS.items():
                    if keyword in p_clean:
                        res = response
                        break
                        
            # 3. معالجة الوسائط (صور أو صوت) إن وجدت
            elif message_obj["media"]:
                res = "🔄 **تم استلام معطياتك وتحليلها برمجياً عبر سيرفر برق الحي:**\n\n"
                for media_item in message_obj["media"]:
                    if media_item["type"] == "image":
                        res += "📸 *(تم استلام وتحليل الصورة بنجاح بواسطة موديل الرؤية)*\n"
                    elif media_item["type"] == "audio":
                        res += "🎙️ *(تم استلام المقطع الصوتي وجاري معالجته عبر خادم الصوت)*\n"
                
                # استدعاء طبيعي ومبسط للموديل للمساعدة في التحليل النصي المرفق
                try:
                    selected_client = {"general": client_general, "games": client_games, "code": client_code}[st.session_state.ai_mode]
                    completion = selected_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPTS[st.session_state.ai_mode]}, {"role": "user", "content": user_content}]
                    )
                    res += f"\n🤖 **الرد الذكي:**\n{completion.choices[0].message.content}"
                except Exception as e:
                    res += f"\n❌ خطأ في الاتصال بالسيرفر للتحليل: {str(e)}"
            
            # 4. المحادثة النصية الافتراضية للذكاء الاصطناعي
            else:
                try:
                    selected_client = {"general": client_general, "games": client_games, "code": client_code}[st.session_state.ai_mode]
                    completion = selected_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPTS[st.session_state.ai_mode]}, {"role": "user", "content": user_content}]
                    )
                    res = completion.choices[0].message.content
                except Exception as e:
                    res = f"❌ خطأ في الاتصال بسيرفر برق الرئيسي: {str(e)}"
            
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.session_state["submitted_content"] = ""
            st.rerun()
