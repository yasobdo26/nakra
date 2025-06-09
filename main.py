from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import google.generativeai as genai
import io

app = Flask(__name__)
CORS(app)

# إعداد Gemini API
genai.configure(api_key="AIzaSyAc9dvll1j2SRH68rDAIfPr9c2klraJeMs")  # استبدلي بمفتاحك
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def serve_welcome():
    return send_file('welcome.html')

@app.route('/index.html')
def serve_index():
    return send_file('index.html')

@app.route('/heart.html')
def serve_heart():
    return send_file('heart.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_file(path)

@app.route('/analyze', methods=['POST'])
def analyze_report():
    if 'image' not in request.files:
        return jsonify({"error": "يرجى رفع صورة"}), 400
    
    file = request.files['image']
    try:
        image = Image.open(io.BytesIO(file.read()))
        prompt = (
            "أنت خبير طبي. هذه صورة تقرير طبي أو إشاعة. "
            "قم بتحليل الصورة، استخراج النصوص إذا لزم الأمر، وشرح التقرير بلغة عربية بسيطة تناسب غير المتخصصين. "
            "قدم أيضًا نصائح صحية بناءً على النتائج. "
            "نظم الرد كالتالي:\n"
            "### الشرح ###\n"
            "اكتب الشرح هنا بطريقة واضحة ومختصرة، مع توضيح أي قيم غير طبيعية ومعناها.\n"
            "### النصائح ###\n"
            "اكتب النصائح الصحية هنا كنقاط (bullet points) إذا أمكن، مع التركيز على نصائح عملية.\n"
            "ملاحظة: هذا التطبيق لأغراض توعوية فقط، ويجب استشارة طبيب للتشخيص الدقيق."
        )

        response = model.generate_content([prompt, image])
        response_text = response.text

        explanation = "لا يمكن استخراج الشرح"
        advice = "لا يمكن استخراج نصائح"
        if "### الشرح ###" in response_text and "### النصائح ###" in response_text:
            parts = response_text.split("### النصائح ###")
            explanation = parts[0].replace("### الشرح ###", "").strip()
            advice = parts[1].strip()

        return jsonify({"explanation": explanation, "advice": advice})
    except Exception as e:
        return jsonify({"error": f"خطأ أثناء التحليل: {str(e)}"}), 500

@app.route('/save_heart_rate', methods=['POST'])
def save_heart_rate():
    data = request.json
    heart_rate = data.get('heart_rate')
    if not heart_rate:
        return jsonify({"error": "يرجى إرسال معدل دقات القلب"}), 400
    # هنا ممكن تخزني القيمة في قاعدة بيانات (زي SQLite) لاحقًا
    return jsonify({"message": "تم حفظ معدل دقات القلب", "heart_rate": heart_rate})

if __name__ == "__main__":
    app.run(debug=True)