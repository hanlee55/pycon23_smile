import streamlit as st
import os
import cv2
import sqlite3
import pandas as pd
from deepface import DeepFace
from sqlite3 import Error

DB_FILE = "rank.db"

def main():
    conn = create_connection()
    if conn is None:
      st.write("Error: Unable to create database connection")
      return
    else:
      if not os.path.exists(DB_FILE):   
        create_table(conn)

    st.title("Smile Rank App")
    
    # Input fields for name and phone number
    name = st.text_input("Name:")
    phone = st.text_input("Phone Number:")
    
    # Placeholder for storing scores
#    scores_df = pd.DataFrame(columns=["Picture", "Score"])
    
    # Loop for taking up to 3 pictures
    for i in range(3):
        st.write("------------------------------------------------")
        # Take a picture
        if st.button("Take a Picture", key=f'pic_{i}'):
            st.write(f"Taking Picture {i+1}")
            image, score = take_picture(f'pic_{name}_{i}')
#            scores_df = scores_df.append({"Picture": image, "Score": score}, ignore_index=True)
#            st.write(f"Picture {i+1} - Happy Score: {score}")
            
            # Display "One More Time?" and "Finish" buttons
            if i < 2:
                pass
                # one_more_time = st.button("One More Time?", key="one_more")
                # if not one_more_time:
                    #break
            else:
                st.write("You have reached the maximum number of pictures.")
                break

    # Sort and display scores
#    if not scores_df.empty:
#        sorted_scores_df = scores_df.sort_values(by="Score", ascending=False)
#        st.write("Rank:")
#        st.table(sorted_scores_df[["Picture", "Happy Score"]].reset_index(drop=True))
    
    conn.close()

def take_picture(file_name):
    # Function to capture picture from camera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    # Save the image temporarily to get the 'happy' score
    temp_path = "./" + file_name + ".png"
    cv2.imwrite(temp_path, frame)

    # DeepFace to get 'happy' score
    result = DeepFace.analyze(img_path=temp_path, actions=['emotion'])
    score = result[0]['emotion']['happy']

    st.write(score)
    return temp_path, score

def create_connection():
    # check file 
    try:
      conn = sqlite3.connect(DB_FILE)
      return conn
    except Error as e:
      print(e)

    return None

def create_table(conn):
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS rank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            picture TEXT NOT NULL,
            score REAL NOT NULL
        )
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
    except Error as e:
        print(e)

def insert_rank(conn, name, phone, picture, score):
    sql_insert_rank = """
        INSERT INTO rank (name, phone, picture, score)
        VALUES (?, ?, ?, ?)
    """
    try:
        c = conn.cursor()
        c.execute(sql_insert_rank, (name, phone, picture, score))
        conn.commit()
    except Error as e:
        print(e)

if __name__ == "__main__":
    main()