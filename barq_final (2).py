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
    </style>
""", unsafe_allow_html=True)

# 2. الاتصال بسيرفرات Groq
API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY)

FILE_NAME = 'barq_final.py'
BACKUP_NAME = 'barq_backup.py'

# 3. إدارة الذاكرة وحالة المطور
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False
if "brq313_mode" not in st.session_state:
    st.session_state.brq313_mode = False

# --- 🌟 قسم الإعلانات والدعم في الشريط الجانبي ---
with st.sidebar:
    st.header("📢 دعم التطبيق والإعلانات")
    st.image("https://via.placeholder.com/300x150.png?text=Your+Ad+Here", use_container_width=True)
    st.link_button(
        label="اضغط هنا لمشاهدة الإعلانات ودعمنا لأننا عكس التطبيقات الأخرى نوفر كل شيء بالمجان",
        url="https://t.me/your_sponsor_channel"
    )

    st.divider()
    st.header("🎯 الميزات المتقدمة")

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
    st.title("⚡ الذكاء الاصطناعي برق - مساعدك الذكي 🚀")
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

# ==================== دوال معالجة الوسائط ====================

def process_image_with_groq(image_base64, image_type, user_prompt):
    """معالجة الصورة مع Groq Vision الحقيقي"""
    try:
        message = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
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

def transcribe_audio_groq(audio_bytes_data):
    """تحويل الصوت إلى نص باستخدام ملف مؤقت آمن بالسيرفر"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes_data)
            temp_audio_name = temp_audio.name
        
        with open(temp_audio_name, "rb") as f:
            transcript = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3"
            )
        os.unlink(temp_audio_name)
        return transcript.text
    except Exception as e:
        return f"❌ خطأ في تحويل الصوت: {str(e)}"

# ==================== عرض الرسائل السابقة ====================
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

# تعريف المتغيرات الافتراضية لمنع الـ NameError
image_file = None
audio_file = None
camera_photo = None
image_prompt = ""

# Tab 1: النص
with media_tabs[0]:
    text_input = st.text_area("اكتب رسالتك:", placeholder="اكتب شتريد او ولي من يمي", height=100)

# Tab 2: الصور
with media_tabs[1]:
    st.write("📸 **رفع الصور**")
    image_file = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png", "webp"], key="image_upload")
    image_prompt = st.text_input("السؤال عن الصورة:", placeholder="ماذا ترى في هذه الصورة؟")

# Tab 3: الصوت
with media_tabs[2]:
    st.write("🎙️ **معالجة الصوت**")
    audio_file = st.file_uploader("اختر ملف صوتي (MP3/WAV)", type=["mp3", "wav", "ogg", "m4a"], key="audio_upload")
    st.caption("ملاحظة: للتسجيل المباشر من الميكروفون أونلاين يفضل رفع الملف مباشرة هنا لضمان توافق السيرفر.")

# Tab 4: الكاميرا
with media_tabs[3]:
    st.write("📹 **التقط صورة من الكاميرا**")
    camera_photo = st.camera_input("التقط صورة 📸")

# ==================== معالجة الإدخال ====================
submit_button = st.button("🚀 إرسال المعطيات", use_container_width=True, type="primary")

if submit_button or text_input:
    user_content = text_input if text_input else "تحليل المعطيات والوسائط المرفقة"
    
    if user_content:
        message_obj = {"role": "user", "content": user_content, "media": []}
        
        # معالجة رفع الصور
        if image_file and use_vision:
            image = Image.open(image_file)
            message_obj["media"].append({
                "type": "image",
                "data": image,
                "name": image_file.name
            })
        
        # معالجة الكاميرا
        if camera_photo and use_vision:
            image = Image.open(camera_photo)
            message_obj["media"].append({
                "type": "image",
                "data": image,
                "name": "صورة من الكاميرا"
            })
        
        # معالجة رفع الصوت
        if audio_file and use_audio:
            audio_bytes = audio_file.read()
            message_obj["media"].append({
                "type": "audio",
                "data": audio_bytes,
                "name": "رسالة صوتية مرفوعة"
            })
        
        st.session_state.messages.append(message_obj)
        
        # عرض مدخلات المستخدم فوراً
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_content)
            if message_obj["media"]:
                for media_item in message_obj["media"]:
                    if media_item["type"] == "image":
                        st.image(media_item["data"], caption=media_item.get("name", "صورة"))
                    elif media_item["type"] == "audio":
                        st.audio(media_item["data"])
        
        # معالجة رد الذكاء الاصطناعي برق
        with st.chat_message("assistant", avatar="🤖"):
            p_clean = user_content.strip().lower()
            res = ""
            
            # 1. وضع الأذونات الفائقة
            if "brq313" in p_clean:
                st.session_state.brq313_mode = True
                st.session_state.dev_mode = True
                res = "✅ **تم تفعيل الأذونات الفائقة BRQ313**\n\n🔓 الآن لديك صلاحية الوصول الكامل وتطوير الكود تلقائياً."
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
                st.rerun()
            
            # 2. ردود المبتكر الآلية
            elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
                for keyword, response in CREATOR_QUESTIONS.items():
                    if keyword in p_clean:
                        res = response
                        break
                st.markdown(res)
            
            # 3. تعديل الكود التلقائي (BRQ313 مفعّل)
            elif (any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود", "حسّن الكود", "أصلح الكود"])
                  and st.session_state.brq313_mode):
                
                st.warning("🔧 **وضع التعديل المتقدم - BRQ313 مفعّل**")
                try:
                    with open(FILE_NAME, 'r', encoding='utf-8', errors='ignore') as f:
                        current_code = f.read()
                    
                    with open(BACKUP_NAME, 'w', encoding='utf-8') as f:
                        f.write(current_code)
                    
                    sys_modify_prompt = """أنت خبير برمجة Python و Streamlit.
مهمتك تعديل الكود الحالي وتطويره بحسب طلب المستخدم.
شروط حتمية:
1. حافظ تماماً على آلية الرمز السري 'brq313' والـ السيرة الذاتية لبارق المطور.
2. أرجع الكود الجديد بالكامل داخل كود بلوك سليم يبدأ بـ ```python وينتهي بـ ``` بدون أي نصوص خارجية تحيط به."""
                    
                    response = client.chat.completions.create(
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
                    
                    if code_match:
                        new_code = code_match.group(1).strip()
                    else:
                        new_code = full_reply.strip()
                    
                    if "import streamlit" in new_code and len(new_code) > 500:
                        with open(FILE_NAME, 'w', encoding='utf-8') as f:
                            f.write(new_code)
                        res = "⚡ **تم تعديل الكود بنجاح ذاتياً! سيعاد تشغيل التطبيق الآن...**"
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
                        st.rerun()
                    else:
                        res = "❌ فشل التعديل ذاتياً: الكود المولد غير مكتمل أو غير آمن."
                        st.error(res)
                
                except Exception as e:
                    res = f"❌ خطأ أثناء محاولة التعديل الذاتي: {str(e)}"
                    st.error(res)
            
            # 4. ردود الإهانات الدفاعية
            elif user_content.strip() in ANTI_INSULT:
                res = ANTI_INSULT[user_content.strip()]
                st.markdown(res)
            
            # 5. معالجة الوسائط (صور / صوت) المرفقة
            elif message_obj["media"]:
                res = "🔄 **جاري تحليل الوسائط عبر سيرفرات برق الذكي...**\n\n"
                
                for media_item in message_obj["media"]:
                    if media_item["type"] == "image" and use_vision:
                        image_bytes_io = io.BytesIO()
                        media_item["data"].save(image_bytes_io, format="PNG")
                        image_base64 = base64.b64encode(image_bytes_io.getvalue()).decode('utf-8')
                        
                        image_analysis = process_image_with_groq(
                            image_base64,
                            "image/png",
                            image_prompt if image_prompt else user_content
                        )
                        res += f"📸 **تحليل الصورة المرفقة:**\n{image_analysis}\n"
                    
                    elif media_item["type"] == "audio" and use_audio:
                        transcription = transcribe_audio_groq(media_item["data"])
                        res += f"🎙️ **التحويل الصوتي إلى نص:**\n{transcription}\n"
                
                st.markdown(res)
            
            # 6. الحوار العادي بدون وسائط
            else:
                try:
                    if st.session_state.brq313_mode:
                        sys_msg = "أنت برق الذكي، مساعد مبرمج خارق بوضع الأذونات الفائقة BRQ313. صانعك ومطورك الوحيد هو بارق العبقري تاج رأسك."
                    else:
                        sys_msg = "أنت برق الذكي، مساعد ذكي متعدد المواهب. مطورك وصانعك هو المبدع بارق."
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": sys_msg}] +
                                 [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]],
                        temperature=0.7,
                        max_tokens=2048
                    )
                    res = chat_completion.choices[0].message.content
                    st.markdown(res)
                
                except Exception as e:
                    res = f"❌ خطأ في الاتصال بالسيرفر: {str(e)}"
                    st.error(res)
            
            st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
