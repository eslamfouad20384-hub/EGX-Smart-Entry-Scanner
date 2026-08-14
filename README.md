EGX Smart Entry Scanner PRO
Scanner لأسهم البورصة المصرية على Streamlit.
المزايا
تحميل قائمة الأسهم المصرية من مصدر خارجي مع CSV محلي كـ fallback.
فحص Daily أو Weekly.
EMA20 / EMA50 / EMA200
RSI
MACD
ADX
ATR و ATR%
OBV
MFI
Volume Ratio
Support / Resistance
إشارات Pullback / Breakout / Reversal / Trend
Entry range
Stop Loss
TP1 / TP2 / TP3
Risk/Reward
Score من 100
تصدير CSV
تشغيل محلي
pip install -r requirements.txt
streamlit run app.py
Streamlit Community Cloud
ارفع المشروع إلى GitHub ثم اختار app.py كملف التشغيل. وجود requirements.txt في root مهم لعملية تثبيت الاعتمادات.
ملاحظة البيانات
النسخة الأولى تستخدم Yahoo Finance عبر yfinance لبيانات الأسعار التاريخية، مع قائمة رموز خارجية وملف محلي احتياطي. قبل الاعتماد على إشارات مالية حقيقية، يفضل إضافة مصدر EGX مدفوع/موثوق للبيانات اللحظية والتحقق من الرموز التي لا يوفرها Yahoo.
تطويرات النسخة القادمة
Multi-Timeframe confirmation: Daily + Weekly + Monthly
Backtesting لكل نوع إشارة
Investment Score منفصل عن Trading Score
CAGR / EPS Growth / ROE / P/E / Dividend Yield
فلتر السوق العام EGX30
تنبيهات Telegram
حفظ النتائج اليومية
