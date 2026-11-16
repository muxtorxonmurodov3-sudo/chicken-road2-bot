RENDER UCHUN TAYYOR BOT

1) GitHub hisob oching: https://github.com
2) Yangi repository yarating, masalan chicken-road2-bot.
3) Ushbu ZIP ichidagi bot.py, requirements.txt va Procfile fayllarini repository'ga yuklang.
4) Render'ga kiring: https://render.com va GitHub orqali ro‘yxatdan o‘ting.
5) New + -> Web Service -> GitHub repository'ni ulang.
6) Runtime: Python 3; Build Command: pip install -r requirements.txt
   Start Command: python bot.py
   Instance Type: Free
7) Environment Variables bo‘limida:
   BOT_TOKEN = BotFather bergan token
   (RENDER_EXTERNAL_URL ni Render o‘zi odatda service uchun beradi; agar avtomatik berilmasa,
   deploydan keyin Render bergan https://....onrender.com URL'ni shu nom bilan kiriting.)
8) Deploy qiling. Logs bo‘limida xato yo‘qligini tekshiring.
9) Telegram'da botga /start yuboring.

XAVFSIZLIK:
- Tokenni GitHub fayllariga yozmang.
- Tokenni faqat Render -> Environment ichiga kiriting.
- Token oshkor bo‘lsa, @BotFather orqali /revoke qiling.

ESLATMA:
Render Free web service 15 daqiqa inbound trafik bo‘lmasa uxlaydi; keyingi so‘rovda
uyg‘onishi taxminan bir daqiqa olishi mumkin. Shuning uchun mutlaq 24/7 kafolat yo‘q.
Bot faqat matematik hisoblaydi; o‘yin natijalarini ko‘rmaydi yoki bashorat qilmaydi.
