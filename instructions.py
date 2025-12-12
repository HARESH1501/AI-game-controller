import streamlit as st

def show_instructions():
    st.title("🖐️ Hand-Controlled Snake Game")

    st.markdown("""
    ## 🎮 How to Play

    ### 🐍 Control
    - Show your **hand** to the camera.
    - Move your **index finger** – the snake follows.

    ### 🍎 Food Types
    - 🔴 Red: +1 score  
    - ⭐ Gold: +5 score  
    - 🔵 Blue: speed boost (short time)  
    - ⚪ White: invisible mode (can pass through body & rocks briefly)

    ### ⚠️ Avoid
    - Screen borders (walls)  
    - Moving stone balls (obstacles)  
    - Your own snake body  
    - 👹 Boss (appears from Level 10)

    ### 💡 Tips
    - Good lighting = better hand tracking  
    - Move your hand smoothly  
    """)

    st.markdown("---")
    start = st.button("🚀 Start Game", use_container_width=True)
    return start
