import streamlit as st
import pandas as pd

st.set_page_config(page_title="商品定價計算器", layout="wide")

st.title("📦 商品定價計算器（銷量比例分攤固定成本 + 自動建議售價）")

st.sidebar.header("⚙️ 全局設定")

# ===============================
# 固定成本輸入
# ===============================
fixed_cost = st.sidebar.number_input("每月固定成本總額", min_value=0, value=100000, step=1000)

# ===============================
# 目標毛利率設定
# ===============================
target_margin = st.sidebar.slider("🎯 目標毛利率（%）", min_value=0, max_value=90, value=40, step=5)
target_margin_decimal = target_margin / 100

st.write("### ✍ 請輸入商品資料")

# 建立輸入表格
num_products = st.number_input("商品數量", min_value=1, value=3, step=1)

product_list = []

for i in range(num_products):
    st.write(f"#### 商品 {i+1}")

    col1, col2, col3, col4 = st.columns(4)

    name = col1.text_input("商品名稱", value=f"商品{i+1}", key=f"name{i}")
    volume = col2.number_input("月銷量（件）", min_value=0, value=0, key=f"vol{i}")
    var_cost = col3.number_input("變動成本/件", min_value=0, value=0, key=f"var{i}")
    price = col4.number_input("目前售價/件（可留 0）", min_value=0, value=0, key=f"price{i}")

    product_list.append([name, volume, var_cost, price])

df = pd.DataFrame(product_list, columns=["商品", "銷量", "變動成本/件", "售價/件"])

# ===============================
# 計算開始
# ===============================

total_volume = df["銷量"].sum()

if total_volume > 0:
    df["銷量比例"] = df["銷量"] / total_volume
else:
    df["銷量比例"] = 0

# 固定成本分攤
df["固定成本分攤額"] = df["銷量比例"] * fixed_cost

# 每件固定成本
df["固定成本/件"] = df.apply(
    lambda x: x["固定成本分攤額"] / x["銷量"] if x["銷量"] > 0 else 0,
    axis=1
)

# 完整成本/件
df["完整成本/件"] = df["變動成本/件"] + df["固定成本/件"]

# ===============================
# ⭐ 自動建議售價（依目標毛利率）
# ===============================
df["建議售價（含目標毛利）"] = df["完整成本/件"].apply(
    lambda c: c / (1 - target_margin_decimal) if (1 - target_margin_decimal) > 0 else 0
)

# 利潤
df["每件利潤（依目前售價）"] = df["售價/件"] - df["完整成本/件"]

# 總月利潤
df["總利潤（依目前售價）"] = df["每件利潤（依目前售價）"] * df["銷量"]

st.write("### 📊 計算結果")
st.dataframe(df, use_container_width=True)

total_profit = df["總利潤（依目前售價）"].sum()

st.write("### 💡 結論")
st.metric("📈 目前價格下的總月利潤", f"{total_profit:,.0f} 元")

st.info("💡 若售價欄位為 0，請直接參考右側「建議售價」欄位作為售價設定依據。")

