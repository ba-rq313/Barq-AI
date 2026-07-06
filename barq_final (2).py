import streamlit as st
from groq import Groq
import os
import re
import json
import base64
import io
from PIL import Image
import pyaudio
import wave
import numpy as np
from datetime import datetime
import tempfile
import subprocess

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
    .voice-btn {
        margin: 5px;
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
if "media_history" not in st.session_state:
    st.session_state.media_history = []

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

def encode_image_to_base64(image_file):
    """تحويل الصورة إلى Base64"""
    image_data = image_file.read()
    return base64.b64encode(image_data).decode('utf-8')

def process_image_with_groq(image_base64, image_type, user_prompt):
    """معالجة الصورة مع Groq Vision"""
    try:
        message = client.chat.completions.create(
            model="llama-2-vision-90b",
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

def transcribe_audio_groq(audio_file):
    """تحويل الصوت إلى نص باستخدام Groq"""
    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3"
            )
        return transcript.text
    except Exception as e:
        return f"❌ خطأ في تحويل الصوت: {str(e)}"

def text_to_speech_groq(text):
    """تحويل النص إلى صوت"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        return response.content
    except Exception as e:
        st.error(f"❌ خطأ في تحويل النص إلى صوت: {str(e)}")
        return None

def record_audio(duration=10, sample_rate=16000):
    """تسجيل الصوت من الميكروفون"""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, input=True, frames_per_buffer=1024)
        
        st.info(f"🎤 جاري التسجيل... ({duration} ثانية)")
        frames = []
        for _ in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        audio_bytes = b''.join(frames)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)
        
        return temp_file.name
    except Exception as e:
        st.error(f"❌ خطأ في التسجيل: {str(e)}")
        return None

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
st.subheader("📤 مشاركة الوسائط")

media_tabs = st.tabs(["📝 النص", "📸 الصور", "🎙️ الصوت", "📹 الكاميرا"])

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
    audio_option = st.radio("اختر طريقة الإدخال الصوتي:", ["رفع ملف صوتي", "تسجيل مباشر"])
    
    if audio_option == "رفع ملف صوتي":
        audio_file = st.file_uploader("اختر ملف صوتي", type=["mp3", "wav", "ogg", "m4a"], key="audio_upload")
    else:
        duration = st.slider("مدة التسجيل (ثانية):", 1, 30, 10)
        if st.button("🔴 ابدأ التسجيل"):
            recorded_file = record_audio(duration=duration)
            if recorded_file:
                audio_file = recorded_file
                st.success("✅ تم التسجيل بنجاح!")

# Tab 4: الكاميرا
with media_tabs[3]:
    st.write("📹 **التقط صورة من الكاميرا**")
    camera_photo = st.camera_input("التقط صورة 📸")

# ==================== معالجة الإدخال ====================
submit_button = st.button("🚀 إرسال", use_container_width=True, type="primary")

if submit_button or text_input:
    user_content = text_input or "تحليل الوسائط المرفقة"
    
    if user_content:
        # إضافة الرسالة إلى السجل
        message_obj = {"role": "user", "content": user_content, "media": []}
        
        # معالجة الصور
        if image_file and use_vision:
            image = Image.open(image_file)
            image_bytes = io.BytesIO()
            image.save(image_bytes, format=image_file.type.split('/')[-1].upper())
            image_bytes.seek(0)
            
            message_obj["media"].append({
                "type": "image",
                "data": image,
                "name": image_file.name
            })
        
        if camera_photo and use_vision:
            image = Image.open(camera_photo)
            message_obj["media"].append({
                "type": "image",
                "data": image,
                "name": "صورة من الكاميرا"
            })
        
        # معالجة الصوت
        if audio_file and use_audio:
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            message_obj["media"].append({
                "type": "audio",
                "data": audio_bytes,
                "name": "رسالة صوتية"
            })
        
        st.session_state.messages.append(message_obj)
        
        # عرض الرسالة
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_content)
            if message_obj["media"]:
                for media_item in message_obj["media"]:
                    if media_item["type"] == "image":
                        st.image(media_item["data"], caption=media_item.get("name", "صورة"))
                    elif media_item["type"] == "audio":
                        st.audio(media_item["data"])
        
        # معالجة الرد
        with st.chat_message("assistant", avatar="🤖"):
            p_clean = user_content.strip().lower()
            res = ""
            
            # تفعيل وضع BRQ313
            if "brq313" in p_clean:
                st.session_state.brq313_mode = True
                st.session_state.dev_mode = True
                res = "✅ **تم تفعيل الأذونات الفائقة BRQ313**\n\n🔓 الآن لديك صلاحية الوصول الكامل وتطوير الكود تلقائياً."
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res, "media": []})
                st.rerun()
            
            # أسئلة المبتكر
            elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
                for keyword, response in CREATOR_QUESTIONS.items():
                    if keyword in p_clean:
                        res = response
                        break
                st.markdown(res)
            
            # طلبات تعديل الكود
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
            
            # الإهانات
            elif user_content.strip() in ANTI_INSULT:
                res = ANTI_INSULT[user_content.strip()]
                st.markdown(res)
            
            # معالجة الوسائط
            elif message_obj["media"]:
                res = "🔄 جاري معالجة الوسائط...\n\n"
                
                # معالجة الصور
                for media_item in message_obj["media"]:
                    if media_item["type"] == "image" and use_vision:
                        image_bytes = io.BytesIO()
                        media_item["data"].save(image_bytes, format="PNG")
                        image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
                        
                        image_analysis = process_image_with_groq(
                            image_base64,
                            "image/png",
                            image_prompt or user_content
                        )
                        res += f"\n📸 **تحليل الصورة:**\n{image_analysis}\n"
                    
                    elif media_item["type"] == "audio" and use_audio:
                        # حفظ الصوت مؤقتاً
                        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                        temp_audio.write(media_item["data"])
                        temp_audio.close()
                        
                        transcription = transcribe_audio_groq(temp_audio.name)
                        res += f"\n🎙️ **نص الصوت:**\n{transcription}\n"
                        
                        os.unlink(temp_audio.name)
                
                # محادثة عادية
                if res == "🔄 جاري معالجة الوسائط...\n\n":
                    try:
                        if st.session_state.brq313_mode:
                            sys_msg = "أنت برق الذكي، مساعد ذكي متقدم بصلاحيات فائقة. تعامل مع الوسائط والنصوص بمحترفية."
                        else:
                            sys_msg = "أنت برق الذكي، مساعد ذكي متعدد المواهب يدعم الصور والصوت والنصوص."
                        
                        chat_completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": sys_msg}] +
                                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]],
                            temperature=0.7,
                            max_tokens=2048
                        )
                        res = chat_completion.choices[0].message.content
                    except Exception as e:
                        res = f"❌ خطأ: {str(e)}"
                
                st.markdown(res)
            
            # الحوار العادي
            else:
                try:
                    if st.session_state.brq313_mode:
                        sys_msg = "أنت برق الذكي، مساعد ذكي متقدم بصلاحيات فائقة."
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
