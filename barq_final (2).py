import streamlit as st
from groq import Groq
import os
import re
import json

# 1. إعدادات المتصفح والصفحة
st.set_page_config(page_title="برق الذكي VIP", page_icon="⚡", layout="wide")

# 2. الاتصال بسيرفرات Groq
API_KEY = os.environ.get("GROQ_API_KEY", "") 
client = Groq(api_key=API_KEY)

# تنبيه: يفضل توحيد اسم الملف بدون أقواس أو مسافات لتجنب أخطاء نظام التشغيل
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
    st.title("⚡ الذكاء الاصطناعي برق - مساعدك الذكي")

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

# 4. عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. معالجة الإدخال الجديد
if prompt := st.chat_input("اكتب شتريد او ولي من يمي"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p_clean = prompt.strip().lower()
        res = ""

        # أولاً: تفعيل وضع BRQ313 الفائق
        if "brq313" in p_clean:
            st.session_state.brq313_mode = True
            st.session_state.dev_mode = True
            res = "✅ **تم تفعيل الأذونات الفائقة BRQ313**\n\n🔓 الآن لديك صلاحية الوصول الكامل وتطوير الكود تلقائياً."
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

        # ثانياً: أسئلة المبتكر/المطور
        elif any(keyword in p_clean for keyword in CREATOR_QUESTIONS.keys()):
            for keyword, response in CREATOR_QUESTIONS.items():
                if keyword in p_clean:
                    res = response
                    break
            st.markdown(res)

        # ثالثاً: فحص طلبات التعديل الذاتي مع BRQ313
        elif (any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود", "حسّن الكود", "أصلح الكود"]) 
              and st.session_state.brq313_mode):
            
            st.warning("🔧 **وضع التعديل المتقدم - BRQ313 مفعّل**")
            try:
                with open(FILE_NAME, 'r', encoding='utf-8', errors='ignore') as f:
                    current_code = f.read()
                
                # إنشاء نسخة احتياطية
                with open(BACKUP_NAME, 'w', encoding='utf-8') as f:
                    f.write(current_code)
                
                # تحليل الطلب بدقة
                analysis_prompt = f"حلل هذا الطلب البرمجي وأرجع النتيجة بصيغة JSON فقط: {prompt}"

                analysis = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                
                sys_modify_prompt = """أنت خبير برمجة Python و Streamlit.
مهمتك تعديل الكود الحالي وتطويره بحسب طلب المستخدم.
شروط حتمية:
1. حافظ تماماً على آلية الرمز السري 'brq313' والـ السيرة الذاتية لبارق المطور.
2. أرجع الكود الجديد بالكامل داخل كود بلوك سليم يبدأ بـ ```python وينتهي بـ ``` بدون أي نصوص خارجية تحيط به."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_modify_prompt},
                        {"role": "user", "content": f"الكود الحالي:\n{current_code}\n\nالطلب:\n{prompt}"}
                    ],
                    temperature=0.5,
                    max_tokens=3000
                )
                
                full_reply = response.choices[0].message.content
                
                # استخراج الكود باستخدام الـ Regex
                code_match = re.search(r'```python(.*?)```', full_reply, re.DOTALL)
                if code_match:
                    new_code = code_match.group(1).strip()
                else:
                    new_code = full_reply.strip()

                # التحقق الأمني البسيط من جودة الكود قبل الحفظ
                if "import streamlit" in new_code and len(new_code) > 500:
                    with open(FILE_NAME, 'w', encoding='utf-8') as f:
                        f.write(new_code)
                    res = "⚡ **تم تعديل الكود بنجاح ذاتياً! سيعاد تشغيل التطبيق الآن...**"
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.rerun()
                else:
                    res = "❌ فشل التعديل ذاتياً: الكود المولد غير مكتمل أو غير آمن."
                    st.error(res)
                
            except Exception as e:
                res = f"❌ خطأ أثناء محاولة التعديل الذاتي: {str(e)}"
                st.error(res)

        # رابعاً: إذا طلب تعديل بدون الرمز
        elif any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود"]):
            res = "🔐 **عذراً!** هذه الميزة تتطلب الأذونات الفائقة.\n\nأدخل الرمز السري `BRQ313` أولاً لتفعيل صلاحيات التعديل."
            st.warning(res)

        # خامساً: الإهانات
        elif prompt.strip() in ANTI_INSULT:
            res = ANTI_INSULT[prompt.strip()]
            st.markdown(res)

        # سادساً: الحوار الذكي المستقر
        else:
            try:
                if st.session_state.brq313_mode:
                    sys_msg = "أنت برق الذكي، مساعد مبرمج خارق بوضع الأذونات الفائقة BRQ313. صانعك ومطورك الوحيد هو بارق العبقري تاج رأسك."
                elif st.session_state.dev_mode:
                    sys_msg = "أنت برق الذكي، بوضع المسؤول. ترحب بسيدك بارق وتنفذ أوامره البرمجية بدقة."
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
                res = f"❌ خطأ في الاتصال بالسيرفر السحابي. تأكد من إعداد مفتاح الـ API بشكل صحيح."
                st.error(res)

        st.session_state.messages.append({"role": "assistant", "content": res})
