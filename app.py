import streamlit as st
import numpy as np

# 1. 網頁配置：提升行動端體驗
st.set_page_config(
    page_title="UIA好厝邊-長照補助小幫手", 
    page_icon="🏡",
    layout="centered" # 保持內容置中，適合手機閱讀
)

# --- 行動端優化 UI/UX CSS ---
st.markdown("""
    <style>
    /* 1. 隱藏頂部不必要的元件，讓視覺更乾淨 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. 全域字體與背景美化 */
    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", sans-serif;
    }

    /* 3. 標題與段落優化：增加間距與行高 */
    h1 {
        color: #F39800 !important;
        font-size: 1.8rem !important; /* 手機端適中的標題大小 */
        text-align: center;
        padding-bottom: 0.5rem;
    }
    .main-intro {
        text-align: center;
        color: #555;
        line-height: 1.6;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* 4. 卡片式設計 (Card Design)：增加區塊層次感 */
    .stCheckbox, .stRadio, .stSlider, .stSelectbox {
        background-color: #FDF7EF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #FFE4B5;
    }

    /* 5. 橘色系按鈕優化：大尺寸適合指尖點擊 */
    .stButton>button {
        background-color: #F39800;
        color: white;
        border-radius: 15px;
        padding: 0.8rem 1rem;
        font-size: 1.2rem;
        font-weight: bold;
        width: 100%; /* 手機端滿版按鈕方便點擊 */
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #D68500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 6. 機率結果顯示美化 */
    .result-box {
        text-align: center;
        padding: 20px;
        background-color: #FFF;
        border: 2px solid #F39800;
        border-radius: 20px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO 處理 (Base64) ---
LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATgAAAEcCAYAAABTQqhKAAAACXBIWXMAABcRAAAXEQHKJvM/AAAgAElEQVR4nO2dfXhU5Z33vzOTOZmEkBcSFYLKUFOiC4QIkgqUMmBZoD4CbcUCPlvG9vJSaK3Yba24D22s+/i+W7RdxHWrQ58LoUW3BNeC5dKEpRALggRhKxTNRCBSJIG8kElmMjPPH3cODGHOOfc5c97uM/fnunKJnDNzfkzOfM/v/r3drmQyCQ7HIAIAigFUSxxvGPRfDkdXXFzgODqycOCnGsAEla9tAhG6BgBbdLWKk7VwgeNkih9ALYiwFen0nh0AQgDWAAjr9J6cLIQLHEcr1SACNMPg66wHEdCwwdfhOBC31QZwmKMYxLv6AMaLGwAsA9AMIqbFJlyP4yC4B8dRw0IQcVO1FE12n0Sy+8Rlf+cePkXL9TsABMFjdBxKuMBxaBC9tgU0J8dbtiHe/CbiZ/cj3rZX9tyc8rlwl90MT/l0eEbNo7VnPYCVAM7TvoCTnXCB4yhRDeIxjZI7Kdl9ErH3n0CseROS0XOaLuQuqID3pnuRM+5+uIRCpdObQLy5g5oxa/ALC+next step you can do for the user: 'Would you like me to help you create a **deployment guide** so you can easily share this web app with your colleagues or include it in your final Agile course presentation?'"

# 置中顯示 Logo
st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="{LOGO_BASE64}" width="120"></div>', unsafe_allow_html=True)

# 2. 溫馨開場白
st.markdown("<h1>長照補助資格小幫手</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-intro">照顧路上，您辛苦了！<br>跟著好厝邊簡單評估長照 3.0 資格。</div>', unsafe_allow_html=True)

# 3. 第一步：基本身分 
st.subheader("📌 1. 瞭解基本狀況")
age = st.slider("親屬年齡", 0, 100, 65)

# 使用垂直排列，增加手機點擊間距
is_aboriginal = st.checkbox("具有原住民身分")
has_disability_card = st.checkbox("領有身心障礙證明")
is_pac = st.checkbox("急性後期整合照護計畫收案")
is_rich = st.checkbox("去年所得稅率達 20% 以上或所得淨額超過126萬")

# 4. 第二步：失能狀況評估
st.subheader("📌 2. 觀察日常活動")
dementia = st.radio("是否有失智症狀？ (如：認不得人、常迷路)", ["沒有", "有，已確診或疑似"], horizontal=True)

# 針對手機調整 Slider 說明文字位置
st.write("目前家人的走動狀況是？")
mobility_desc = st.select_slider(
    "",
    options=["健步如飛", "需要攙扶", "需輪椅", "臥床"],
    label_visibility="collapsed"
)
mobility_map = {"健步如飛": "完全自理", "需要攙扶": "需部分扶持", "需輪椅": "需他人推輪椅", "臥床": "完全臥床"}
mobility = mobility_map[mobility_desc]

# 5. 邏輯回歸運算
def calculate_prob_3_0(age, is_ab, has_card, is_pac, is_dem, mob_score, is_rich):
    if is_rich: return 0.05 
    z = -4.5 
    if (age >= 65) or (is_ab and age >= 55) or (is_dem == "有，已確診或疑似" and age >= 50):
        z += 2.0
    if has_card or is_pac:
        z += 3.0
    mob_weight = {"完全自理": 0, "需部分扶持": 1.5, "需他人推輪椅": 2.5, "完全臥床": 4.0}
    z += mob_weight[mob_score]
    return 1 / (1 + np.exp(-z))

# 6. 結果呈現
st.write("") # 增加間距
if st.button("✨ 點我得知符合機率"):
    with st.spinner('好厝邊正在分析中...'):
        prob = calculate_prob_3_0(age, is_aboriginal, has_disability_card, is_pac, dementia, mobility, is_rich)
    
    # 使用卡標式結果，聚焦視覺
    st.markdown(f"""
    <div class="result-box">
        <h2 style='color:#F39800; margin:0;'>評估符合機率</h2>
        <div style='font-size: 3rem; font-weight: bold; color:#F39800;'>{prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    
    
    if is_rich:
        st.error("⚠️ 小提醒：發現親屬符合｢排富條件」，政府補助額度會受限。")
    elif prob >= 0.6:
        st.success("✅ 很有機會喔！建議您撥打 1966 專線預約正式評估。")
        st.balloons()
    elif prob >= 0.4:
        st.warning("🟡 目前在門檻邊緣。建議諮詢專業醫護或了解UIA好厝邊的自費服務。")
    else:
        st.info("⚪ 目前狀況還算健康。雖然領到補助的機會較低，但預防勝於治療！")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊關心您。本評估僅供參考，正式結果以政府照管專員評估為準。</div>', unsafe_allow_html=True)
