import streamlit as st
import os
import cv2
import numpy as np
import pandas as pd
from deepface import DeepFace
from typing import List, Union
import time

base_path = os.path.abspath(os.getcwd())
data_path = os.path.join(base_path, "data")
temp_path = os.path.join(data_path, "temp.png")

main_df_path = os.path.join(data_path, "df.csv")
backup_df_path = os.path.join(data_path, "backup.csv")

def get_rank_data():
    df = pd.read_csv(
        main_df_path,
        sep="$",
        na_values="None"
    )
    return df

def put_data(name: str, contect: str, score1: float, score2: float) -> None:
    name.replace('$', '_')
    contect.replace('$', '_')
    with open(main_df_path, 'a') as f:
        f.write("$".join([name, contect, str(score1), str(score2), time.time()])+'\n')
    with open(main_df_path, 'a') as f:
        f.write("$".join([name, contect, str(score1), str(score2), time.time()])+'\n')

def take_picture():
    # Function to capture picture from camera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # Save the image temporarily to get the 'happy' score
    cv2.imwrite(temp_path, frame)

def save_data(name, contect, score1, score2) -> List[Union[int, float, List[float]]]:
    # int, float, List[float], float, List[float]
    # history_buffer = get_buffer()
    history_buffer = st.session_state['cache']

    print(history_buffer)
    if history_buffer["name"] != name:
        history_buffer["name"] = name
        history_buffer["score1"] = []
        history_buffer["score2"] = []
    history_buffer["contect"] = contect
    history_buffer["score1"].append(score1)
    history_buffer["score2"].append(score2)
    if len(history_buffer) >= 3:
        put_data(
            name,
            contect,
            max(history_buffer["score1"]),
            max(history_buffer["score2"]),
        )

    return [
        len(history_buffer["score1"]),
        max(history_buffer["score1"]),
        history_buffer["score1"],
        max(history_buffer["score2"]),
        history_buffer["score2"],
    ]

def main():
    st.title("파이썬 웃음챌린지")
    side_r, side_l = st.columns(2)
    with side_r:
        img_file_buffer = st.camera_input("Take a picture")

        # Input fields for name and contect info
        name = st.text_input("Name:")
        contect = st.text_input("Phone Number (or email address):")

    with side_l:
        if img_file_buffer is not None:
            # To read image file buffer with OpenCV:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            cv2.imwrite(temp_path, cv2_img)
            # take_picture()
            try:
                result = DeepFace.analyze(
                    img_path=temp_path, actions=['emotion'], enforce_detection=False
                )
                st.header("도전자 정보")
                st.write(f"이름(Name): {name}")
                st.write(f"연락처(Contect): {contect}")
                process_data = save_data(
                    name,
                    contect,
                    result[0]['emotion']['happy'],
                    result[0]['emotion']['happy'] * 2 - sum(result[0]['emotion'].values())
                )
                print("DEBUG]", result[0]['emotion'])
                a = {"test": ""}
                
                if process_data[0] >= 3:
                    st.subheader("최종 결과")
                    col1, col2 = st.columns(2)
                    col1.metric(
                        label="Score",
                        value=round(process_data[1], 3),
                    )
                    col2.metric(
                        label="Score+",
                        value=round(process_data[3], 3)
                    )

                    st.markdown('<a href="/ranking" target="_self">🏆 Ranking 확인하기</a>', unsafe_allow_html=True)
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("시도(Try)", f"{process_data[0]}회", "+1회")
                col2.metric(
                    label="Score",
                    value=round(process_data[2][-1], 3),
                    delta=round(process_data[2][-2], 1) if len(process_data[2]) > 1 else None
                )
                col3.metric(
                    label="Score+",
                    value=round(process_data[4][-1], 3),
                    delta=round(process_data[4][-2], 1) if len(process_data[4]) > 1 else None
                )
                
            except ValueError:
                st.write('얼굴을 인식하지 못했어요 ㅠㅠ 다시 시도해 주세요!')

if __name__ == "__main__":
    if 'cache' not in st.session_state:
        st.session_state["cache"] = {"name":'???', "contect":'???????', "score1":[], "score2":[]}
    main()