import streamlit as st
import os
import cv2
import numpy as np
import pandas as pd
from deepface import DeepFace
from typing import List, Union
import time
from shutil import copyfile

CAPTURE_BY_OPENCV = True

base_path = os.path.abspath(os.getcwd())
data_path = os.path.join(base_path, "data")
temp_path = os.path.join(data_path, "temp.png")

main_df_path = os.path.join(data_path, "df.csv")
backup_df_path = os.path.join(data_path, "backup.csv")

def get_rank_data():
    df = pd.read_csv(
        main_df_path,
        sep="$",
        na_values="None",
        encoding='utf-8'
    )
    return df

def put_data(name: str, contect: str, score1: float, score2: float) -> None:
    name.replace('$', '_')
    contect.replace('$', '_')
    with open(main_df_path, 'a', encoding='UTF-8') as f:
        f.write("$".join([name, contect, str(score1), str(score2), str(time.time())])+'\n')
    with open(main_df_path, 'a', encoding='UTF-8') as f:
        f.write("$".join([name, contect, str(score1), str(score2), str(time.time())])+'\n')

def take_picture(img_save_path):
    # Function to capture picture from camera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # Save the image temporarily to get the 'happy' score
    cv2.imwrite(temp_path, frame)
    copyfile(temp_path,img_save_path)

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
        st.write("위에 Take photo 버튼을 눌러 사진을 찍어요")

        # Input fields for name and contect info
        name = st.text_input("이름 Name:")
        contect = st.text_input("전화번호 또는 이메일 주소 Phone Number (or email address):")

    with side_l:
        if img_file_buffer is not None:
            # To read image file buffer with OpenCV:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            st.write("잠시만 기다려주세요! 5초 이내에 촬영됩니다.")
            img_save_name = f"{name}__{contect.replace('@', '+')}__{str(time.time()).replace('.', '_')}.png"
            img_save_path = os.path.join(data_path, "img", img_save_name)

            if CAPTURE_BY_OPENCV:
                take_picture(img_save_path)
                st.write("사진을 찍었어요!")
            else:
                cv2.imwrite(temp_path, cv2_img)
                copyfile(temp_path,img_save_path)
            
            try:
                result = DeepFace.analyze(
                    img_path=temp_path, actions=['emotion'], enforce_detection=False
                )
                st.header("도전자 정보")
                st.write(f"이름(Name): {name}")
                st.write(f"연락처(Contact): {contect}")
                process_data = save_data(
                    name,
                    contect,
                    result[0]['emotion']['happy'],
                    result[0]['emotion']['happy'] * 2 - sum(result[0]['emotion'].values())
                )
                score0 = result[0]['emotion']['happy']
                if score0 < 10:
                   st.write("웃어봐요!😊")
                elif score0 < 30:
                   st.write("활짝 웃어봐요!😊")
                elif score0 < 40:
                   st.write("조금 더 웃어봐요!😊")
                elif score0 < 70:
                    st.write("종아요! 조금 더 즐겁게 웃어봐요!😊")
                else:
                    st.write("아주 좋아요!")
                if process_data[0] >= 2:
                    st.subheader("수고하셨습니다!")
                    st.subheader("F5를 눌러주세요!")
                else:
                    st.subheader(f"{2-process_data[0]}번 남았어요!")
                    st.write("clear photo 누르시고 다시 찍어주세요")
                    st.write("도전을 마치시려면 F5를 눌러주세요")
                st.write("결과는 행사 종료후 집계하여 우승자에게 연락처로 상품 보내드려요~")
                st.divider()

                st.metric("시도(Try)", f"{process_data[0]}회")

                
            except ValueError:
                st.write('얼굴을 인식하지 못했어요 ㅠㅠ 다시 시도해 주세요!')


if __name__ == "__main__":
    if 'cache' not in st.session_state:
        st.session_state["cache"] = {"name":'???', "contect":'???????', "score1":[], "score2":[]}
    main()
