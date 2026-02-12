import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(
    page_title="UIA好厝邊-長照補助小幫手", 
    page_icon="🏡",
    layout="centered" 
)

# --- CSS 樣式 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif; }
    h1 { color: #F39800 !important; font-size: 1.8rem !important; text-align: center; }
    .main-intro { text-align: center; color: #555; line-height: 1.6; margin-bottom: 1.5rem; }
    .stCheckbox, .stRadio, .stSlider, .stSelectbox {
        background-color: #FDF7EF; padding: 15px; border-radius: 12px; margin-bottom: 5px; border: 1px solid #FFE4B5;
    }
    .stButton>button {
        background-color: #F39800; color: white; border-radius: 15px; padding: 0.8rem 1rem;
        font-size: 1.2rem; font-weight: bold; width: 100%; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-box { text-align: center; padding: 20px; background-color: #FFF; border: 2px solid #F39800; border-radius: 20px; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>長照補助資格測評器</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-intro">請完成下方所有評估項目，好厝邊將為您精準推估補助資格。</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 第一步：基本身分
# ---------------------------------------------------------
st.subheader("一、 瞭解基本狀況")
age = st.slider("親屬年齡", 0, 125, 65)
is_rich = False 

col_check1, col_check2 = st.columns(2)
with col_check1:
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明")
with col_check2:
    is_pac = st.checkbox("急性後期照護計畫(PAC)")
    dementia = st.checkbox("有失智症狀 (確診或疑似)")

with st.expander("💰 點此評估補助比例 (選填)"):
    is_rich = st.checkbox("去年所得稅率達 20% 以上或股利所得採分開計稅者")

# ---------------------------------------------------------
# 4. 第二步：日常生活評估 (改為單一頁面 + 必填視覺感)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("二、 日常生活評估 (ADL & IADL)")
st.info("💡 請確保下方三個類別皆已完成選取")

# 每一組題目都預設一個「請選擇」選項，用來判斷是否有漏填
placeholder = "--- 請選擇狀況 ---"

# --- 類別 1：身體照顧 ---
st.markdown("#### 📍 類別 1：身體照顧")
with st.container():
    a1 = st.selectbox("進食：自己吃飯的能力", [placeholder, "可自行取食", "需人幫忙", "完全無法"])
    a2 = st.selectbox("洗澡：全身洗浴的能力", [placeholder, "可獨立完成", "需人協助"])
    a3 = st.selectbox("個人衛生：刷牙洗臉梳頭", [placeholder, "可自行完成", "需人協助"])
    a4 = st.selectbox("穿脫衣服：包含鞋襪與支架", [placeholder, "可自行穿好", "需人幫忙一半", "完全無法"])
    a5 = st.selectbox("排便/尿控制：控制力狀況", [placeholder, "可自行控制", "偶爾失禁", "完全失禁"])
    a6 = st.selectbox("如廁：上下馬桶與清理", [placeholder, "可獨立完成", "需人扶持", "需完全幫忙"])

# --- 類別 2：居家生活 ---
st.markdown("#### 📍 類別 2：居家生活")
with st.container():
    b1 = st.selectbox("移位/走動：從床上坐起、站立、走動", [placeholder, "健步如飛", "需要扶持", "需輪椅", "臥床"])
    b2 = st.selectbox("上下樓梯：垂直移動能力", [placeholder, "可自行上下", "需人稍微指導", "無法上下"])
    b3 = st.selectbox("上街購物：買菜或買日常用品", [placeholder, "獨力完成", "需人陪同", "完全無法"])
    b4 = st.selectbox("外出活動：搭乘公車/捷運", [placeholder, "能搭公車/捷運", "需人陪伴", "完全不能"])
    b5 = st.selectbox("食物烹調：煮飯或加熱食物", [placeholder, "獨力完成", "可幫忙加熱", "需人煮好"])
    b6 = st.selectbox("家務維持：整理家務或鋪床", [placeholder, "獨力完成", "需人幫忙"])

# --- 類別 3：健康管理 ---
st.markdown("#### 📍 類別 3：健康與管理")
with st.container():
    c1 = st.selectbox("洗衣服：獨立洗衣物", [placeholder, "獨力完成", "僅能洗小件", "完全無法"])
    c2 = st.selectbox("服用藥物：準時吃正確劑量", [placeholder, "自己負責", "需人提醒", "完全無法"])
    c3 = st.selectbox("電話使用：撥號與應答", [placeholder, "獨力撥號應答", "僅能接聽", "完全無法"])
    c4 = st.selectbox("財務管理：理財或支付帳單", [placeholder, "獨力理財", "僅能處理小錢", "完全無法"])

# ---------------------------------------------------------
# 5. 邏輯運算與檢查機制
# ---------------------------------------------------------
def calculate_3_0_logic(all_ans):
    help_needed = sum(1 for x in all_ans if "需" in x or "無法" in x or "不能" in x or "失禁" in x or "輔助" in x or "輪椅" in x or "臥床" in x)
    z = -5.0
    if dementia or has_disability_card: z += 4.0
    if is_pac: z += 3.5
    if (age >= 65) or (is_aboriginal and age >= 55): z += 1.5
    z += help_needed * 0.8
    return 1 / (1 + np.exp(-z))

# 6. 送出按鈕與防呆檢查
st.markdown("---")
if st.button("✨ 點我得知推估結果"):
    all_selections = [a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, c1, c2, c3, c4]
    
    # 檢查是否有任何一題未選
    if placeholder in all_selections:
        st.error("❌ 哎呀！還有題目沒有選到喔，請往上捲動檢查標註為『--- 請選擇狀況 ---』的欄位。")
    else:
        prob = calculate_3_0_logic(all_selections)
        res_color = "#E67E22" if is_rich else "#F39800"
        cms_label = "2 級以上 (符合補助)" if prob >= 0.5 else "1 級 (目前尚健康)"
        
        st.markdown(f"""
        <div class="result-box" style="border-color: {res_color};">
            <h2 style='color:{res_color}; margin:0;'>推估 CMS 等級：{cms_label}</h2>
            <div style='font-size: 3.5rem; font-weight: bold; color:{res_color};'>{prob*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

        if prob >= 0.5:
            st.markdown("### 💡 補助權益小筆記")
            col1, col2 = st.columns(2)
            with col1:
                if is_rich: st.info("**🏠 居家/社區照顧**\n\n自付額約為 **16%**。")
                else: st.success("**🏠 居家/社區照顧**\n\n您可能符合**中低收入**，自付額僅 **0%~5%**！")
            with col2:
                if is_rich: st.error("**🏨 住宿機構補助**\n\n因稅率達 20%，**不符合** 12 萬補助。")
                else: st.success("**🏨 住宿機構補助**\n\n符合所得門檻！最高可領 **12 萬元**。")
            st.success("✅ 符合機率高！建議撥打 **1966** 預約正式評估。")
            st.balloons()
        else:
            st.info("⚪ 目前評估結果較為健康。如有急性出院需求(PAC)，建議仍諮詢醫院個管師。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊關心您｜蓋解憂專案</div>', unsafe_allow_html=True)
