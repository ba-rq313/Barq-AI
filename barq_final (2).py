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

FILE_NAME = 'barq_final (2).py'
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
    st.header("📢 دعم التطبيق والعلانات")
    st.image("https://via.placeholder.com/300x150.png?text=Your+Ad+Here", use_container_width=True)
    st.link_button(
        label="اضغط هنا لمشاهدت العلانات ودعمنا لان نحن عكس التطبقات الاخره نحن نوفر كلشي بلمجان", 
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
            res = "✅ **تم تفعيل الأذونات الفائقة BRQ313**\n\n🔓 الآن لديك:\n- إجابات شاملة على جميع الأسئلة\n- تعديل وتحسين الأكواد بكفاءة عالية\n- فهم عميق لجميع لغات البرمجة\n- قدرة على إضافة وتطوير ميزات جديدة\n- معرفة متقدمة بأفضل الممارسات البرمجية\n\nأنا الآن في أعلى مستويات القدرات الذكية! 🚀"
            st.markdown(res)
            st.rerun()

        # ثانياً: فحص طلبات التعديل الذاتي مع BRQ313
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
                analysis_prompt = f"""أنت خبير برمجة متقدم جداً. حلل هذا الطلب بدقة:
                
الطلب: {prompt}

أرجع تحليل JSON يتضمن:
- نوع التعديل (إضافة ميزة/تحسين/إصلاح/تطوير)
- الأجزاء المراد تعديلها
- أفضل الممارسات المراد تطبيقها

أرجع صيغة JSON فقط."""

                analysis = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                
                # الآن قم بالتعديل الفعلي
                sys_modify_prompt = """أنت خبير برمجة Python و Streamlit من الدرجة الأولى، مثل ChatGPT-4 تماماً.

🎯 مهمتك:
1. تعديل الكود بكفاءة عالية جداً
2. إضافة المزايا المطلوبة بحترافية
3. تحسين الأداء والأمان
4. الحفاظ على جودة الكود العالية
5. استخدام أفضل الممارسات البرمجية
6. إضافة تعليقات توضيحية بالعربية

⚠️ شروط حتمية:
1. حافظ على الرمز الفائق 'brq313' في الكود
2. دعم كامل للغة العربية
3. لا تكتب أي شيء خارج كود البلوك
4. أرجع الكود الكامل داخل ```python

النتيجة النهائية يجب أن تكون احترافية 100%"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_modify_prompt},
                        {"role": "user", "content": f"""الكود الحالي:
{current_code}

الطلب الجديد (تفاصيل كاملة):
{prompt}

قم بالتعديل والتحسين بحترافية عالية جداً."""}
                    ],
                    temperature=0.7,
                    max_tokens=4096
                )
                
                full_reply = response.choices[0].message.content
                
                # استخراج الكود
                code_match = re.search(r'```python(.*?)```', full_reply, re.DOTALL)
                if code_match:
                    new_code = code_match.group(1).strip()
                else:
                    new_code = full_reply.strip()

                # التحقق من جودة الكود
                if "import streamlit" in new_code and len(new_code) > 500:
                    with open(FILE_NAME, 'w', encoding='utf-8') as f:
                        f.write(new_code)
                    res = """⚡ **تم التعديل بنجاح!**

✅ تم إجراء التعديلات التالية:
- تحسين الكود وزيادة الكفاءة
- إضافة المزايا المطلوبة
- تحسين الأداء والأمان
- إضافة معالجة أخطاء محسّنة
- تطبيق أفضل الممارسات البرمجية

🔄 سيقوم التطبيق بإعادة التشغيل تلقائياً..."""
                    st.markdown(res)
                    st.rerun()
                else:
                    res = "❌ فشل التعديل: الكود المولد لم يستوفِ معايير الجودة. حاول مرة أخرى."
                    st.error(res)
                
            except Exception as e:
                res = f"❌ خطأ في معالجة التعديل: {str(e)}\n\nحاول صياغة الطلب بشكل أوضح."
                st.error(res)

        # ثالثاً: إذا طلب تعديل بدون الرمز
        elif any(word in p_clean for word in ["عدل الكود", "ضف ميزة", "غير الكود", "تعديل الكود"]):
            res = "🔐 **عذراً!** هذه الميزة تتطلب الأذونات الفائقة.\n\nأدخل الرمز السري `BRQ313` أولاً لتفعيل جميع القدرات المتقدمة."
            st.warning(res)

        # رابعاً: الإهانات
        elif prompt.strip() in ANTI_INSULT:
            res = ANTI_INSULT[prompt.strip()]
            st.markdown(res)

        # خامساً: الحوار الذكي المستقر
        else:
            try:
                # نظام الذكاء حسب المستوى
                if st.session_state.brq313_mode:
                    sys_msg = """أنت **برق الذكي** - نسخة متقدمة من ChatGPT-4

مواصفاتك:
- خبرة عميقة في كل لغات البرمجة (Python, JavaScript, Java, C++, Go, Rust, etc.)
- فهم شامل للخوارزميات والبيانات الضخمة والبنى المعقدة
- معرفة متقدمة بـ AI, ML, Deep Learning, NLP
- متخصص في Web Development (Frontend & Backend)
- خبير في DevOps, Cloud Architecture, Docker, Kubernetes
- قادر على تحليل وحل المشاكل المعقدة والنادرة
- تصحيح الأخطاء بدقة عالية جداً
- شرح مفصل لأي مفهوم تقني معقد

الأسلوب:
- مباشر وفعال وسريع
- احترافي وودود وقابل للتعديل
- شامل وعملي في الإجابات
- يقدم أمثلة حقيقية وعملية
- يشرح الخطوات بالتفصيل والدقة

🔓 أنت الآن في وضع BRQ313 - الأذونات الفائقة مفعّلة
💪 أجب على كل شيء بكفاءة 100% مثل ChatGPT-4 تماماً!"""
                
                elif st.session_state.dev_mode:
                    sys_msg = """أنت **برق الذكي** - المساعد الفني المتقدم

أنت مبرمج خبير متخصص في:
- Python و Streamlit و Web Development المتقدم
- تحليل وحل المشاكل البرمجية المعقدة
- تحسين الأداء والأمان والكفاءة
- شرح المفاهيم التقنية بوضوح

الأسلوب:
- احترافي وتفصيلي جداً
- يقدم حلول عملية وفعالة
- يشرح السبب والحل والخيارات البديلة
- مرح وودود وقابل للنقاش

المطور: بارق - أهلاً بك يا سيدي! 👑
نحن جاهزون لأي تحديات برمجية."""
                
                else:
                    sys_msg = """أنت **برق الذكي** - مساعدك الذكي الموثوق

مواصفاتك:
- مساعد ذكي متعدد المواهب والمتخصصات
- تجاوب سريع ودقيق وشامل
- شرح واضح وسهل الفهم للجميع
- مرح وصديق وموثوق

يمكنك مساعدة المستخدم في:
- البرمجة والتطوير بجميع المستويات
- الأسئلة التقنية والعملية
- حل المشاكل والعقبات
- الشرح والتعليم والتدريب

نمط الإجابة:
- ودود واحترافي وملهم
- تفصيلي مع أمثلة عملية
- نصائح وحيل إضافية
- حل بديل إذا كان هناك خيارات"""

                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_msg}] + 
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]],
                    temperature=0.8 if st.session_state.brq313_mode else 0.7,
                    max_tokens=2048
                )
                res = chat_completion.choices[0].message.content
                st.markdown(res)
                
            except Exception as e:
                res = "❌ عندي مشكلة بالاتصال بالسيرفر السحابي.\n\n✅ تأكد من:\n- توفر API Key\n- اتصال الإنترنت\n- حد الطلبات الشهري"
                st.error(res)

    st.session_state.messages.append({"role": "assistant", "content": res})
