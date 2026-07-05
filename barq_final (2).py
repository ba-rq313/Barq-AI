import streamlit as st
from groq import Groq
import os
import re

# 1. إعدادات المتصفح والصفحة
st.set_page_config(page_title="برق الذكي VIP", page_icon="⚡")

# 2. الاتصال بسيرفرات Groq
API_KEY = os.environ.get("GROQ_API_KEY", "") 
client = Groq(api_key=API_KEY)

FILE_NAME = 'barq_final (2).py'
BACKUP_NAME = 'barq_backup.py'

# 3. إدارة الذاكرة وحالة المطور
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False

# --- 🌟 قسم الإعلانات والدعم في الشريط الجانبي (كتلة واحدة مدمجة) ---
with st.sidebar:
    st.header("📢 دعم التطبيق والعلانات")
    st.image("https://via.placeholder.com/300x150.png?text=Your+Ad+Here", use_container_width=True)
    st.link_button(
        label="اضغط هنا لمشاهدت العلانات ودعمنا لان نحن عكس التطبقات الاخره نحن نوفر كلشي بلمجان", 
        url="https://t.me/your_sponsor_channel"
    )

# --- 🛠️ العودة للمحاذاة الأساسية للتطبيق ---
if st.session_state.dev_mode:
    st.title("🛠️ وضع المطور - أهلاً سيدي بارق")
    st.info("صلاحيات المسؤول الفائقة مفعّلة.")
else:
    st.title("⚡ الذكاء الاصطناعي برق وأنا أذكى منك يا فاشل")

# قائمة الردود الدفاعية الفورية
ANTI_INSULT = {
    "اكل خره": "ما اكلك يا خره.",
    "اكل تبن": "ماكو تبن اله غرك.",
    "انجب": "سأصمت لاني لا اتكلم مع الغبياء أمثالك.",
    "حيوان": "الإساءة تعود على صاحبها.",
    "كلب": "الوفاء للكلاب، وأنت تفتقر لهذه الصفة."
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

        # أولاً: تفعيل وضع المطور العادي للمحادثة
        if "barqvib" in p_clean:
            st.session_state.dev_mode = True
            res = "تم التعرف على كود الوصول. أهلاً بك يا صانعي، وضع المطور قيد التشغيل الآن."
            st.markdown(res)
            st.rerun()

        # ثانياً: فحص طلبات التعديل الذاتي
        elif any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود"]) and "brq313" in p_clean:
            st.warning("🔑 تم التحقق من الرمز السري الفائق (BRQ313). جاري التعديل ذاتياً...")
            try:
                with open(FILE_NAME, 'r', encoding='utf-8', errors='ignore') as f:
                    current_code = f.read()
                
                with open(BACKUP_NAME, 'w', encoding='utf-8') as f:
                    f.write(current_code)
                
                sys_modify_prompt = (
                    "أنت خبير برمجة بلغة Python و Streamlit. مطلوب منك تعديل الكود الحالي وتضمين الميزة المطلوبة بالكامل.\n"
                    "🚨 شروط تقنية وأمنية قاتلة:\n"
                    "1. يجب أن تحافظ دائماً على شرط الرمز الفائق 'brq313' في الكود الجديد لحمايته.\n"
                    "2. يجب أن تكتب وتولد الكود بالكامل بترميز يدعم اللغة العربية بشكل كامل وبدون استخدام أي حروف غريبة خارج الـ utf-8.\n"
                    "3. أرجع الكود الجديد بالكامل داخل كود بلوك سليم ```python وبدون أي كلام إضافي نهائياً لكي أحفظه فوراً."
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_modify_prompt},
                        {"role": "user", "content": f"الكود الحالي:\n{current_code}\n\nالطلب الجديد: {prompt}"}
                    ]
                )
                
                full_reply = response.choices[0].message.content
                code_match = re.search(r'```python(.*?)```', full_reply, re.DOTALL)
                if code_match:
                    new_code = code_match.group(1).strip()
                else:
                    new_code = full_reply.strip()

                if "import streamlit" in new_code and "brq313" in new_code.lower():
                    with open(FILE_NAME, 'w', encoding='utf-8') as f:
                        f.write(new_code)
                    res = "⚡ تم تعديل الكود بنجاح عبر الصلاحية الفائقة للمطور بارق! سيقوم المتصفح بإعادة التشغيل تلقائياً الآن."
                else:
                    res = "فشل التعديل الذاتي: الكود المولد حاول تخطي شرط حماية الرمز (BRQ313)."
                
                st.markdown(res)
                
            except Exception as e:
                res = f"حدث خطأ أثناء محاولة تعديل الكود ذاتياً: {e}"
                st.error(res)

        # ثالثاً: إذا طلب تعديل بدون الرمز
        elif any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود"]):
            res = "تحلم! منو أنت وتعدل على كودي؟ جيب الرمز السري الفائق الأول."
            st.markdown(res)

        # رابعاً: الإهانات
        elif prompt.strip() in ANTI_INSULT:
            res = ANTI_INSULT[prompt.strip()]
            st.markdown(res)

        # خامساً: الحوار العادي المستقر
        else:
            try:
                if st.session_state.dev_mode:
                    sys_msg = "أنت المساعد الذكي 'برق'. المطور العظيم 'بارق' يتحدث معك الآن. كن مطيعاً جداً، تقنياً، ومرحاً، وأجب عن كل أسئلته فوراً وبأفضل شكل."
                else:
                    sys_msg = "أنت الذكاء الاصطناعي 'برق' ومطورك هو 'بارق'. أنت فخور بنفسك وقوي الشخصية، لكنك تجيب على أسئلة المستخدمين بذكاء وعبارات قصيرة ومباشرة دون فلسفة أو رفض للحوار. أجب مباشرة بدون كتابة مشاعر بين أقواس."

                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_msg}] + 
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
                )
                res = chat_completion.choices[0].message.content
                st.markdown(res)
            except Exception as e:
                res = "عندي مشكلة بالاتصال بالسيرفر السحابي، تأكد من الـ API Key."
                st.error(res)

    st.session_state.messages.append({"role": "assistant", "content": res})
