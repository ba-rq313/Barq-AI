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
import requests

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
    .mode-images { background-color: #fff8e1; color: #f57c00; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. إدارة الذاكرة وحالات التنقل واللغات والإحصائيات
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

# عدادات الإحصائيات الحية للوحة التحكم
if "stats_images_analyzed" not in st.session_state:
    st.session_state.stats_images_analyzed = 0
if "stats_audio_processed" not in st.session_state:
    st.session_state.stats_audio_processed = 0
if "stats_images_generated" not in st.session_state:
    st.session_state.stats_images_generated = 0

# دالة Callback آمنة للتحكم في المدخلات وتجنب الأخطاء البرمجية للـ State
def handle_submit_callback():
    st.session_state["submitted_content"] = st.session_state.text_input_box
    st.session_state.text_input_box = ""

# ========================================================
# المرحلة الأولى: واجهة اختيار اللغة
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
# جلب المفاتيح بأمان من إعدادات Streamlit Secrets لضمان عملها فوراً
    API_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY", "")
    HF_TOKEN = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else os.environ.get("HF_TOKEN", "")
    client_general = Groq(api_key=API_KEY)
    client_games = Groq(api_key=API_KEY)
    client_code = Groq(api_key=API_KEY)

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

    # دالة توليد الصور المحدثة والمستقرة جداً
    def generate_image(prompt):
        if not HF_TOKEN:
            st.error("❌ عذراً! ميزة إنشاء الصور تتطلب مفتاح `HF_TOKEN` في Streamlit Secrets للعمل.")
            return None
        
        API_URL = "https://api-inference.huggingface.co/models/SG161222/Realistic_Vision_V4.0_noVAE"
        headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}"}
        payload = {
            "inputs": prompt, 
            "parameters": {
                "negative_prompt": "ugly, blurry, low quality, distorted, bad anatomy, deformed, watermark", 
                "num_inference_steps": 30
            }
        }

        try:
            with st.spinner("🔄 جاري إطلاق قدرات 'برق' لإنشاء صورة جبارة ودقيقة التفاصيل..."):
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 503:
                    st.warning("⏳ السيرفر يقوم بتحميل الموديل حالياً، انتظر ثوانٍ معدودة ثم أعد الضغط على إرسال.")
                    return None
                    
                if response.status_code == 200:
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    return image
                else:
                    st.error(f"❌ خطأ من السيرفر (كود {response.status_code}): يرجى إعادة المحاولة أو التحقق من الـ Token.")
                    return None
        except Exception as e:
            st.error(f"❌ حدث خطأ غير متوقع أثناء إنشاء الصورة: {str(e)}")
            return None

    # --- القائمة الجانبية (Sidebar) مع لوحة التحكم الإحصائية تفاعلياً ---
    with st.sidebar:
        st.header("📊 لوحة التحكم والإحصائيات الحية")
        
        total_msg = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric(label="💬 عدد رسائل المستخدم المرسلة", value=total_msg)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric(label="📸 صور محللة", value=st.session_state.stats_images_analyzed)
        with col_s2:
            st.metric(label="🎙️ صوتيات", value=st.session_state.stats_audio_processed)
        with col_s3:
            st.metric(label="✨ صور مولدة", value=st.session_state.stats_images_generated)
            
        st.markdown("🌐 **حالة السيرفر:** `متصل ومستقر 🟢` ")
        st.markdown(f"🎯 **النمط الحالي:** `{st.session_state.ai_mode.upper()}`")
        
        st.divider()
        st.header("📢 دعم التطبيق والإعلانات")
        st.link_button(
            label="اضغط هنا لمشاهدة الإعلانات ودعمنا لأننا نوفر كل شيء بالمجان",
            url="https://t.me/your_sponsor_channel"
        )
        st.divider()
        
        st.header("🎯 الأوضاع المتاحة")
        mode_option = st.radio(
            "اختر وضع الذكاء الاصطناعي الحالي:",
            options=["general", "games", "code", "images"],
            format_func=lambda x: {
                "general": "📚 معلومات عامة وإجابات شاملة",
                "games": "🎮 خبير الألعاب والتطبيقات",
                "code": "💻 خبير الأكواد والسكربتات",
                "images": "✨ خبير إنشاء الصور الاحترافية"
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
            st.session_state.stats_images_analyzed = 0
            st.session_state.stats_audio_processed = 0
            st.session_state.stats_images_generated = 0
            st.rerun()

    # الواجهة البرمجية لبرق الرئيسية
    mode_titles = {
        "general": "📚 برق الذكي - مساعدك الذكي للمعلومات العامة",
        "games": "🎮 برق الذكي - خبير الألعاب والتطبيقات المحترف",
        "code": "💻 برق الذكي - خبير البرمجة والمطور الفائق",
        "images": "✨ برق الذكي - خبير إنشاء الصور الاحترافية والجبارة"
    }
    mode_class = f"mode-{st.session_state.ai_mode}"
    st.markdown(f"<h1 class='mode-badge {mode_class}'>{mode_titles[st.session_state.ai_mode]}</h1>", unsafe_allow_html=True)
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
    
    tab_titles = ["📝 النص والرسائل"]
    if st.session_state.ai_mode != "images":
        tab_titles.extend(["📸 رفع الصور", "🎙️ تسجيل المايكروفون", "📹 لقطة الكاميرا"])
    
    media_tabs = st.tabs(tab_titles)

    image_file = None
    audio_recorded_bytes = None
    camera_photo = None

    with media_tabs[0]:
        st.text_area("اكتب رسالتك النصية هنا:", placeholder="اكتب شتريد او ولي من يمي...", height=100, key="text_input_box")

    if st.session_state.ai_mode != "images":
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
            
            # 1. تنفيذ إنشاء الصور
            if st.session_state.ai_mode == "images" and text_input_extracted:
                prompt_ar = text_input_extracted
                
                user_msg = {"role": "user", "content": f"🎨 أريدك أن تنشئ صورة جبارة ودقيقة التفاصيل بناءً على هذا الوصف:\n**{prompt_ar}**", "media": []}
                st.session_state.messages.append(user_msg)
                
                try:
                    selected_client = client_general
                    completion = selected_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Translate the user's prompt to English precisely for image generation. Do not explain, just give the translation. Concentrate on hyper-realistic and extreme details."}, {"role": "user", "content": prompt_ar}]
                    )
                    prompt_en = completion.choices[0].message.content
                except Exception as e:
                    prompt_en = prompt_ar
                
                generated_image = generate_image(prompt_en)
                
                if generated_image:
                    ai_reply = "✅ **تم إنشاء الصورة الجبارة بنجاح!** لقد ركزت على أدق التفاصيل لتنافس الشركات العالمية."
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply, "media": [{"type": "image", "data": generated_image}]})
                    st.session_state.stats_images_generated += 1
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ عذراً! حدث خطأ أثناء إنشاء الصورة. يرجى مراجعة صلاحيات مفتاح الـ TOKEN أو المحاولة لاحقاً."})
                
                st.session_state["submitted_content"] = ""
                st.rerun()

            # 2. تنفيذ الأوضاع الأخرى
            else:
                user_content = text_input_extracted if text_input_extracted else "تحليل المعطيات والوسائط المرفقة"
                message_obj = {"role": "user", "content": user_content, "media": []}
                
                if image_file and use_vision:
                    message_obj["media"].append({"type": "image", "data": Image.open(image_file)})
                    st.session_state.stats_images_analyzed += 1
                if camera_photo and use_vision:
                    message_obj["media"].append({"type": "image", "data": Image.open(camera_photo)})
                    st.session_state.stats_images_analyzed += 1
                if audio_recorded_bytes and use_audio:
                    message_obj["media"].append({"type": "audio", "data": audio_recorded_bytes})
                    st.session_state.stats_audio_processed += 1
                    
                st.session_state.messages.append(message_obj)
                
                p_clean = user_content.lower()
                res = ""
                
                if user_content in ANTI_INSULT:
                    res = ANTI_INSULT[user_content]
                elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
                    for keyword, response in CREATOR_QUESTIONS.items():
                        if keyword in p_clean:
                            res = response
                            break
                            
                else:
                    try:
                        selected_client = {"general": client_general, "games": client_games, "code": client_code}[st.session_state.ai_mode]
                        sys_prompt = SYSTEM_PROMPTS[st.session_state.ai_mode]
                        
                        if message_obj["media"]:
                            sys_prompt += "\nساعد أيضاً في تحليل الصور والمرفقات الأخرى إن وجد في سياق المحادثة."

                        completion = selected_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_content}]
                        )
                        res = completion.choices[0].message.content
                    except Exception as e:
                        res = f"❌ خطأ في الاتصال بسيرفر برق الرئيسي: {str(e)}"
                
                st.session_state.messages.append({"role": "assistant", "content": res})
                st.session_state["submitted_content"] = ""
                st.rerun()
