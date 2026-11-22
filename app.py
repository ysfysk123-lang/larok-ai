import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq
from duckduckgo_search import DDGS

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def internette_ara(sorgu):
    try:
        sonuclar = DDGS().text(sorgu, max_results=4)
        return "\n".join([f"- {s['title']}: {s['body']} ({s['href']})" for s in sonuclar])
    except Exception:
        return "Web araması yapılamadı."

HTML_SAYFASI = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Larok AI</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; height: 100vh; margin: 0; }
        header { width: 100%; padding: 15px 0; background: #1e293b; text-align: center; font-size: 24px; font-weight: bold; color: #38bdf8; }
        #chat-box { flex: 1; width: 90%; max-width: 800px; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        .msg { padding: 12px 16px; border-radius: 12px; max-width: 75%; line-height: 1.5; white-space: pre-wrap; }
        .user { background: #2563eb; align-self: flex-end; }
        .bot { background: #1e293b; border: 1px solid #334155; align-self: flex-start; }
        #input-area { width: 90%; max-width: 800px; display: flex; gap: 10px; padding: 15px 0; }
        input { flex: 1; padding: 14px; border-radius: 10px; border: 1px solid #334155; background: #1e293b; color: white; font-size: 16px; }
        button { padding: 14px 24px; border-radius: 10px; border: none; background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <header>⚡ LAROK AI</header>
    <div id="chat-box">
        <div class="msg bot">Merhaba! Ben Larok AI. İnternet sitelerini tarayabilir ve sorularını yanıtlayabilirim. Ne araştırmamı istersin?</div>
    </div>
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Larok AI'ya bir şey sor..." onkeypress="if(event.key==='Enter') mesajGonder()">
        <button onclick="mesajGonder()">Gönder</button>
    </div>
    <script>
        async function mesajGonder() {
            const input = document.getElementById("user-input");
            const chatBox = document.getElementById("chat-box");
            const text = input.value.trim();
            if (!text) return;
            chatBox.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = "";
            const loadingId = "load-" + Date.now();
            chatBox.innerHTML += `<div class="msg bot" id="${loadingId}">🔍 Siteler taranıyor...</div>`;
            const response = await fetch("/sor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mesaj: text })
            });
            const data = await response.json();
            document.getElementById(loadingId).innerText = data.cevap;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def ana_sayfa():
    return render_template_string(HTML_SAYFASI)

@app.route("/sor", methods=["POST"])
def sor():
    mesaj = request.json.get("mesaj", "")
    web_bilgisi = internette_ara(mesaj)
    sistem = "Senin adın Larok AI. İnternet sitelerini araştırıp güncel Türkçe cevaplar veren bir yapay zekasın. Asla başka bir model olduğunu söyleme."
    cevap = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": sistem},
            {"role": "user", "content": f"Soru: {mesaj}\n\nWeb Bilgileri:\n{web_bilgisi}"}
        ]
    )
    return jsonify({"cevap": cevap.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
