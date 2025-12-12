import streamlit as st

SND_EAT_NORMAL = 1172
SND_EAT_GOLD   = 1173
SND_BOOST      = 1717
SND_GAME_OVER  = 1389

def play_sound(sound_id: int):
    html = f"""
    <audio autoplay>
        <source src="https://assets.mixkit.co/sfx/preview/mixkit-{sound_id}.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)
