import streamlit as st
import os
import pandas as pd
from typing import List


st.set_page_config(page_title="Ranking", page_icon="🏆")

base_path = os.path.abspath(os.getcwd())
data_path = os.path.join(base_path, "data")
temp_path = os.path.join(data_path, "temp.png")

main_df_path = os.path.join(data_path, "df.csv")
cache_path = os.path.join(data_path, "cache.pkl")

def get_rank_data():
    df = pd.read_csv(
        main_df_path,
        sep="$",
        na_values="None"
    )
    return df

st.title("파이썬 웃음챌린지")

st.markdown('<a href="/" target="_self">도전하러 가기</a>', unsafe_allow_html=True)

st.dataframe(
    data=get_rank_data().sort_values("score2", ascending=False),
    hide_index=True,
    column_order=("name", "score2")
)
