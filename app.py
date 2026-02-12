import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(page_title="UIA好厝邊-長照補助小幫手", page_icon="🏡", layout="centered")

# --- CSS 樣式優化 ---
st.markdown("""
    <style>
    h1 { color: #F39800 !important; text-align: center; }
    .stSelectbox div[data-baseweb="select"] { border: 1px solid #F39800; }
    .must-fill { color: #E74C3C; font-weight: bold; }
    .result-box { text-align: center; padding: 20px; border: 2px solid #F39800; border-radius: 20px; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>長照補助資格測評器 (2026最新版)</h1>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#555;">依據長照 3.0 法規，結合 ADL 與 IADL 全量表評估。</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 第一步：基本身分 (收案對象確認)
# ---------------------------------------------------------
st.subheader("一、 確定申請身分")
age = st.slider("親屬年齡", 0, 125, 65)

col1, col2 = st.columns(2)
with col1:
    is_aboriginal = st.checkbox("具有原住民身分 (55歲以上適用)")
    has_disability_card = st.checkbox("領有身心障礙證明 (115年起納入)")
with col2:
    is_pac = st.checkbox("急性後期整合照護計畫 (PAC) 對象")
    dementia = st.checkbox("經醫師診斷為失智症者 (不限年齡)")

is_rich = False
with st.expander("💰 點此評估補助比例 (選填排富條款)"):
    is_rich = st.checkbox("去年所得稅率達 20% 以上或股利分開計稅者")

# ---------------------------------------------------------
# 4. 第二步：日常生活評估 (18題必選防呆)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("二、 日常生活評估 (ADL & IADL)")
st.error("❗ 請確保下方「每一題」皆已選取狀況，不可保留在『--- 請選擇 ---』。")

placeholder = "--- 請選擇狀況 ---"

# 分類 1
st.markdown("#### 📍 身體照顧 (基礎生理)")
a1 = st.selectbox("進食能力：", [placeholder, "可自行取食", "需人幫忙或只會用湯匙", "無法自行取食"], key="a1")
a2 = st.selectbox("洗澡能力：", [placeholder, "可獨立完成", "需人協助"], key="a2")
a3 = st.selectbox("個人衛生：", [placeholder, "可自行完成", "需人協助"], key="a3")
a4 = st.selectbox("穿脫衣服：", [placeholder, "可自行完成", "需人幫忙一半", "需完全幫忙"], key="a4")
a5 = st.selectbox("排便控制：", [placeholder, "不會失禁", "偶爾失禁", "完全失禁"], key="a5")
a6 = st.selectbox("如廁能力：", [placeholder, "可自行進出清理", "需人扶持", "需人完全幫忙"], key="a6")

# 分類 2
st.markdown("#### 📍 居家生活 (移動與家務)")
b1 = st.selectbox("移位狀況：", [placeholder, "可獨立完成", "需些微協助", "需大半協助", "需兩人幫忙"], key="b1")
b2 = st.selectbox("步行狀況：", [placeholder, "健步如飛(50公尺以上)", "需扶持或口頭指導", "需推輪椅", "完全臥床"], key="b2")
b3 = st.selectbox("上下樓梯：", [placeholder, "可自行上下", "需稍微協助", "無法上下"], key="b3")
b4 = st.selectbox("上街購物：", [placeholder, "獨力完成", "獨立買日用品", "需人陪同", "完全無法"], key="b4")
b5 = st.selectbox("外出活動：", [placeholder, "能搭公車捷運", "需人陪伴搭車", "完全不能"], key="b5")
b6 = st.selectbox("食物烹調：", [placeholder, "獨力完成", "可加熱飯菜", "需人煮好"], key="b6")

# 分類 3
st.markdown("#### 📍 健康管理 (通訊與認知)")
c1 = st.selectbox("家務維持：", [placeholder, "能做家事", "僅能做輕便家事", "完全無法"], key="c1")
c2 = st.selectbox("洗衣服：", [placeholder, "獨力完成", "僅能洗小件", "完全無法"], key="c2")
c3 = st.selectbox("服用藥物：", [placeholder, "自己負責", "需人提醒", "完全無法"], key="c3")
c4 = st.selectbox("使用電話：", [placeholder, "獨力撥號應答", "僅能接聽", "完全無法"], key="c4")
c5 = st.selectbox("財務管理：", [placeholder, "獨力理財", "僅能處理小錢", "完全無法"], key="c5")
# (註：PAC 對象通常在此區塊得分較低，需特別注意)

# ---------------------------------------------------------
# 5. 邏輯運算 (精確對應法規)
# ---------------------------------------------------------
def calculate_3_0_logic(ans_list):
    # 判斷是否符合 3.0 收案族群
    is_group_match = (
        (age >= 65) or 
        (is_aboriginal and age >= 55) or 
        dementia or 
        has_disability_card or 
        is_pac
    )
    
    # 計算失能權重
    help_count = sum(1 for x in ans_list if "需" in x or "無法" in x or "不能" in x or "失禁" in x or "臥床" in x)
    z = -5.0 + (help_count * 0.9)
    if is_pac: z += 1.0 # PAC 對象優先銜接權重
    
    prob = 1 / (1 + np.exp(-z))
    return is_group_match, prob

# 6. 送出結果
if st.button("✨ 點我開始評估"):
    all_ans = [a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, c1, c2, c3, c4, c5]
    
    if placeholder in all_ans:
        st.error("⚠️ 還有題目漏掉囉！請檢查上方是否有尚未選取的下拉選單。")
    else:
        is_match, prob = calculate_3_0_logic(all_ans)
        
        # 判定 CMS 2 級 (機率 0.5 以上模擬為 2 級)
        is_cms2 = prob >= 0.5
        
        st.markdown(f"""
        <div class="result-box">
            <h2>推估結果</h2>
            <div style='font-size: 3.5rem; font-weight: bold; color: #F39800;'>{prob*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_match and is_cms2:
            st.success("✅ **符合長照 3.0 補助資格！**")
            st.write("您的身分與失能狀況(CMS 2級以上)已達收案門檻。")
            # 顯示補助小筆記...
            st.balloons()
        elif is_match and not is_cms2:
            st.warning("🟡 **身分符合，但失能等級可能未達 2 級。**")
            st.write("雖然您屬於收案族群，但目前自理能力尚佳。若狀況惡化，請隨時重新評估。")
        else:
            st.info("⚪ **目前尚未符合長照 3.0 資格。**")
            st.write("建議維持健康生活，或洽詢 UIA好厝邊 的預防性照護資訊。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊：蓋解憂(Catch You)專案團隊</div>', unsafe_allow_html=True)
