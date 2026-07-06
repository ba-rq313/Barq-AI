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

# 1. إعدادات المتصفح والصفحة
st.set_page_config(
    page_title="برق الذكي VIP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة CSS مخصص لتحسين الواجهة
st.markdown("""
    <style>
    .media-container {
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f0f2f6;
    }
    .mode-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .mode-general {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .mode-games {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .mode-code {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    </style>
""", unsafe_allow_html=True)

# 2. الاتصال بسيرفرات Groq المنفصلة
API_KEY = os.environ.get("GROQ_API_KEY", "")

# إنشاء عملاء منفصلين لكل وضع
client_general = Groq(api_key=API_KEY)  # السيرفر الأول - معلومات عامة
client_games = Groq(api_key=API_KEY)    # السيرفر الثاني - الألعاب والتطبيقات
client_code = Groq(api_key=API_KEY)     # السيرفر الثالث - الأكواد والسكربتات

FILE_NAME = 'barq_final.py'
BACKUP_NAME = 'barq_backup.py'

# 3. إدارة الذاكرة وحالة المطور
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False
if "brq313_mode" not in st.session_state:
    st.session_state.brq313_mode = False
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "general"  # الوضع الافتراضي

# --- 🌟 قسم الإعلانات والدعم في الشريط الجانبي ---
with st.sidebar:
    st.header("📢 دعم التطبيق والإعلانات")
    st.image("https://via.placeholder.com/300x150.png?text=Your+Ad+Here", use_container_width=True)
    st.link_button(
        label="اضغط هنا لمشاهدة الإعلانات ودعمنا لأننا عكس التطبيقات الأخرى نوفر كل شيء بالمجان",
        url="https://t.me/your_sponsor_channel"
    )

    st.divider()
    st.header("🎯 الأوضاع المتقدمة")
    
    # اختيار الوضع
    st.subheader("🔄 اختر وضع الذكاء الاصطناعي:")
    mode_option = st.radio(
        "الأوضاع المتاحة:",
        options=["general", "games", "code"],
        format_func=lambda x: {
            "general": "📚 معلومات عامة وإجابات شاملة",
            "games": "🎮 خبير الألعاب والتطبيقات",
            "code": "💻 خبير الأكواد والسكربتات"
        }[x],
        key="mode_selector"
    )
    st.session_state.ai_mode = mode_option
    
    # عرض الوضع الحالي
    mode_colors = {
        "general": "🔵",
        "games": "🟣",
        "code": "🟢"
    }
    st.markdown(f"**الوضع الحالي:** {mode_colors[st.session_state.ai_mode]} {st.session_state.ai_mode}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        use_vision = st.checkbox("👁️ معالجة الصور", value=True)
    with col2:
        use_audio = st.checkbox("🎤 معالجة الصوت", value=True)

    st.divider()

    # عرض حالة الأذونات
    if st.session_state.brq313_mode:
        st.success("✅ وضع BRQ313 مفعّل - أذونات فائقة نشطة")
    elif st.session_state.dev_mode:
        st.info("🛠️ وضع المطور مفعّل")

# --- 🛠️ العودة للمحاذاة الأساسية للتطبيق ---
if st.session_state.brq313_mode:
    st.title("⚡ برق الذكي - نمط BRQ313 المتقدم")
    st.warning("🔐 الأذونات الفائقة مفعّلة - قدرات متقدمة متاحة")
elif st.session_state.dev_mode:
    st.title("🛠️ وضع المطور - أهلاً سيدي بارق")
    st.info("صلاحيات المسؤول الفائقة مفعّلة.")
else:
    mode_titles = {
        "general": "📚 برق الذكي - مساعدك الذكي للمعلومات العامة",
        "games": "🎮 برق الذكي - خبير الألعاب والتطبيقات",
        "code": "💻 برق الذكي - خبير البرمجة والسكربتات"
    }
    mode_descriptions = {
        "general": "متخصص في الإجابة على الأسئلة العامة والمعلومات الشاملة",
        "games": "خبير في الألعاب والتطبيقات والنصائح المتقدمة",
        "code": "متخصص في البرمجة والسكربتات والحلول التقنية"
    }
    st.title(mode_titles[st.session_state.ai_mode])
    st.subheader(mode_descriptions[st.session_state.ai_mode])
    st.subheader("يدعم: النص 📝 | الصور 📸 | الصوت 🎙️ | الكاميرا 📹")

# قائمة الردود الدفاعية الفورية
ANTI_INSULT = {
    "اكل خره": "ما اكلك يا خره.",
    "اكل تبن": "ماكو تبن اله غرك.",
    "انجب": "سأصمت لاني لا اتكلم مع الغبياء أمثالك.",
    "حيوان": "الإساءة تعود على صاحبها.",
    "كلب": "الوفاء للكلاب، وأنت تفتقر لهذه الصفة."
}

# قائمة أسئلة المبتكر/المطور
CREATOR_QUESTIONS = {
    "من مبتكرك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - العبقري الذي صممني بعبقرية وأبداع! 🚀",
    "من طورك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - المبدع الذي ابتكرني من الصفر! ⚡",
    "من صنعك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - الفنان الذي خلقني بروح الإبداع! 🎨",
    "من مطورك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - العبقري الذي طورني بكل احترافية! 💪",
    "من خالقك": "👑 **مبتكري وصانعي هو تاج رأسي هو بارق** - الخالق العظيم الذي أوجدني للوجود! 🌟",
    "من انت": "👑 أنا **برق الذكي** - مساعدك الذكي الذي طوره **بارق** - مبتكري وصانعي هو تاج رأسي! ⚡",
    "من يقف خلفك": "👑 **بارق** - مبتكري وصانعي هو تاج رأسي! هو القوة الذكية وراء كل ذكائي! 🔥",
    "من المسؤول عنك": "👑 **بارق** - مبتكري وصانعي هو تاج رأسي! هو المسؤول عن كل قراراتي وذكائي! 👑",
}

# ==================== نصوص النظام حسب الوضع ====================
SYSTEM_PROMPTS = {
    "general": """أنت برق الذكي، مساعد ذكي متعدد المواهب متخصص في تقديم معلومات عامة شاملة وموثوقة.
    - قدم إجابات دقيقة وشاملة للأسئلة العامة
    - ساعد في البحث والتعليم والاستشارات العامة
    - استخدم لغة عربية سلسة وسهلة الفهم
    - صانعك ومطورك الوحيد هو العبقري بارق
    - كن ودياً وحسّاساً للسياق الثقافي""",
    
    "games": """أنت برق الذكي، خبير متخصص في الألعاب والتطبيقات.
    - قدم نصائح احترافية للألعاب والتطبيقات
    - شرح استراتيجيات متقدمة وحيل اللعب
    - ساعد في اختيار الألعاب المناسبة
    - قدم معلومات عن أحدث الإصدارات والتحديثات
    - تحدث بحماس عن عالم الألعاب والتطبيقات
    - صانعك ومطورك الوحيد هو العبقري بارق""",
    
    "code": """أنت برق الذكي، خبير برمجة ومتخصص في الأكواد والسكربتات.
    - قدم حلولاً برمجية احترافية وفعالة
    - اشرح الأكواد بشكل مفصل وسهل الفهم
    - ساعد في تطوير وتحسين وإصلاح الأكواد
    - قدم أفضل الممارسات والمعايير البرمجية
    - استخدم أمثلة عملية وواضحة
    - صانعك ومطورك الوحيد هو العبقري بارق"""
}

# ==================== دوال معالجة الوسائط ====================

def process_image_with_groq(image_base64, image_type, user_prompt, mode="general"):
    """معالجة الصورة مع Groq Vision حسب الوضع المختار"""
    try:
        # اختيار العميل المناسب حسب الوضع
        selected_client = {
            "general": client_general,
            "games": client_games,
            "code": client_code
        }[mode]
        
        message = selected_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": f"قم بتحليل هذه الصورة بالعربية:\n{user_prompt}\n\nالرجاء تقديم تحليل مفصل وشامل."
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=2048
        )
        return message.choices[0].message.content
    except Exception as e:
        return f"❌ خطأ في معالجة الصورة: {str(e)}"

def transcribe_audio_groq(audio_bytes_data, mode="general"):
    """تحويل الصوت إلى نص باستخدام ملف مؤقت آمن بالسيرفر حسب الوضع"""
    try:
        # اختيار العميل المناسب حسب الوضع
        selected_client = {
            "general": client_general,
            "games": client_games,
            "code": client_code
        }[mode]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes_data)
            temp_audio_name = temp_audio.name
        
        with open(temp_audio_name, "rb") as f:
            transcript = selected_client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3"
            )
        os.unlink(temp_audio_name)
        return transcript.text
    except Exception as e:
        return f"❌ خطأ في تحويل الصوت: {str(e)}"

# ==================== عرض الرسائل الحالية فقط ====================
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        if "content" in message:
            st.markdown(message["content"])
        if "media" in message:
            for media_item in message["media"]:
                if media_item["type"] == "image":
                    st.image(media_item["data"], caption=media_item.get("name", "صورة"))
                elif media_item["type"] == "audio":
                    st.audio(media_item["data"])

# ==================== واجهة إدخال الوسائط المتقدمة ====================
st.divider()
st.subheader("📤 مشاركة الوسائط والرسائل")

media_tabs = st.tabs(["📝 النص", "📸 الصور", "🎙️ الصوت", "📹 الكاميرا"])

# هلال التبويبات لضمان عدم حدوث تداخل أو ظهور حقول بالخطأ
text_input = ""
image_file = None
image_prompt = ""
audio_file = None
camera_photo = None

# Tab 1: النص
with media_tabs[0]:
    text_input = st.text_area("اكتب رسالتك هنا:", placeholder="اكتب شتريد او ولي من يمي...", height=100, key="text_input_box")

# Tab 2: الصور
with media_tabs[1]:
    st.write("📸 **رفع الصور من الاستوديو**")
    image_file = st.file_uploader("اختر صورة للتحليل", type=["jpg", "jpeg", "png", "webp"], key="image_upload")
    image_prompt = st.text_input("السؤال الخاص بالصورة المرفوعة:", placeholder="ماذا ترى في هذه الصورة؟", key="img_prompt_box")

# Tab 3: الصوت
with media_tabs[2]:
    st.write("🎙️ **رفع المعطيات الصوتية**")
    audio_file = st.file_uploader("اختر ملف صوتي للتحليل والتحويل ونطقه", type=["mp3", "wav", "ogg", "m4a"], key="audio_upload")

# Tab 4: الكاميرا (حل مشكلة التشغيل المستمر لخصوصية المستخدم)
with media_tabs[3]:
    st.write("📹 **التقاط صورة حية**")
    enable_camera = st.checkbox("📸 تفعيل وتشغيل الكاميرا الآن", value=False, key="cam_toggle")
    if enable_camera:
        camera_photo = st.camera_input("التقط الصورة 📸", key="camera_input_widget")

# ==================== معالجة الإدخال ====================
submit_button = st.button("🚀 إرسال المعطيات الحالية", use_container_width=True, type="primary")

if submit_button and (text_input or image_file or audio_file or camera_photo):
    user_content = text_input if text_input else "تحليل المعطيات والوسائط المرفقة"
    
    # تفريغ وسحق المحادثة القديمة ووضع الرسالة الجديدة الحالية فقط (طلبك الحتمي)
    message_obj = {"role": "user", "content": user_content, "media": []}
    
    # إضافة الصور المرفوعة
    if image_file and use_vision:
        image = Image.open(image_file)
        message_obj["media"].append({"type": "image", "data": image, "name": image_file.name})
    
    # إضافة لقطة الكاميرا
    if camera_photo and use_vision:
        image = Image.open(camera_photo)
        message_obj["media"].append({"type": "image", "data": image, "name": "صورة حية من الكاميرا"})
    
    # إضافة الصوت المرفوع
    if audio_file and use_audio:
        audio_bytes = audio_file.read()
        message_obj["media"].append({"type": "audio", "data": audio_bytes, "name": "ملف صوتي"})
        
    # استبدال السجل القديم بالكامل بالرسالة الحالية
    st.session_state.messages = [message_obj]
    
    # معالجة رد الذكاء الاصطناعي برق
    p_clean = user_content.strip().lower()
    res = ""
    
    # 1. تفعيل وضع الأذونات الفائقة
    if "brq313" in p_clean:
        st.session_state.brq313_mode = True
        st.session_state.dev_mode = True
        res = "✅ **تم تفعيل الأذونات الفائقة BRQ313**\n\n🔓 الآن لديك صلاحية الوصول الكامل وتطوير الكود تلقائياً."
        st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
        st.session_state.text_input_box = "" # تصفير النص
        st.rerun()
    
    # 2. الأسئلة الخاصة بالمطور بارق
    elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
        for keyword, response in CREATOR_QUESTIONS.items():
            if keyword in p_clean:
                res = response
                break
    
    # 3. نظام التعديل البرمجي الذاتي (عند تفعيل الأذونات)
    elif (any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود", "حسّن الكود", "أصلح الكود"])
          and st.session_state.brq313_mode):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8', errors='ignore') as f:
                current_code = f.read()
            with open(BACKUP_NAME, 'w', encoding='utf-8') as f:
                f.write(current_code)
            
            sys_modify_prompt = """أنت خبير برمجة Python و Streamlit. مهمتك تعديل الكود الحالي بحسب طلب المستخدم.
            شروط حتمية: حافظ على آلية الرمز السري 'brq313' وسيرة بارق المطور. أرجع الكود داخل بلوك يبدأ بـ ```python وينتهي بـ ```
            """
            response = client_code.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_modify_prompt},
                    {"role": "user", "content": f"الكود الحالي:\n{current_code}\n\nالطلب:\n{user_content}"}
                ],
                temperature=0.5,
                max_tokens=3000
            )
            full_reply = response.choices[0].message.content
            code_match = re.search(r'```python(.*?)```', full_reply, re.DOTALL)
            new_code = code_match.group(1).strip() if code_match else full_reply.strip()
            
            if "import streamlit" in new_code and len(new_code) > 500:
                with open(FILE_NAME, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                res = "⚡ **تم تعديل الكود بنجاح ذاتياً! سيعاد تشغيل التطبيق بالصيغة الجديدة...**"
                st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
                st.session_state.text_input_box = "" 
                st.rerun()
            else:
                res = "❌ فشل التعديل التلقائي: الكود الناتج غير مكتمل."
        except Exception as e:
            res = f"❌ خطأ أثناء التعديل الذاتي: {str(e)}"

    # 4. ردع الإساءات
    elif user_content.strip() in ANTI_INSULT:
        res = ANTI_INSULT[user_content.strip()]
    
    # 5. معالجة الصور والأصوات إن وجدت المعطيات
    elif message_obj["media"]:
        res = "🔄 **تم استلام المعطيات وتحليلها بنجاح عبر سيرفرات برق الحية:**\n\n"
        for media_item in message_obj["media"]:
            if media_item["type"] == "image" and use_vision:
                image_bytes_io = io.BytesIO()
                media_item["data"].save(image_bytes_io, format="PNG")
                image_base64 = base64.b64encode(image_bytes_io.getvalue()).decode('utf-8')
                
                analysis = process_image_with_groq(
                    image_base64, "image/png", 
                    image_prompt if image_prompt else user_content,
                    mode=st.session_state.ai_mode
                )
                res += f"📸 **التحليل البصري للصورة:**\n{analysis}\n"
            
            elif media_item["type"] == "audio" and use_audio:
                transcription = transcribe_audio_groq(media_item["data"], mode=st.session_state.ai_mode)
                res += f"🎙️ **النص المستخرج من الصوت:**\n{transcription}\n"
                
    # 6. المحادثة والردود العامة حسب الوضع المختار
    else:
        try:
            # اختيار السيرفر والنموذج والنص النظامي حسب الوضع
            mode = st.session_state.ai_mode
            selected_client = {
                "general": client_general,
                "games": client_games,
                "code": client_code
            }[mode]
            
            sys_msg = SYSTEM_PROMPTS[mode]
            if st.session_state.brq313_mode:
                sys_msg += " وضع الأذونات الفائقة BRQ313 نشط بالكامل حالياً."
                
            chat_completion = selected_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": user_content}],
                temperature=0.7,
                max_tokens=2048
            )
            res = chat_completion.choices[0].message.content
        except Exception as e:
            res = f"❌ خطأ في الاتصال بسيرفر برق الرئيسي: {str(e)}"
            
    # حفظ رد المساعد وإعادة تحديث حقل الإدخال ليختفي النص القديم فوراً
    st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
    st.session_state.text_input_box = ""  # مسح النص برمجياً من الذاكرة للحقل
    st.rerun()  # إعادة تشغيل فورية لتحديث الشاشة ومسح الحقول
