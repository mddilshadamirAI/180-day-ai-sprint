import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random

# --- FIREBASE CONFIG ---
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
game_ref = db.collection('games').document('active_match')

st.title("👑 Raja Mantri Sipahi Chor")

# Fetch state
doc = game_ref.get()
state = doc.to_dict() if doc.exists else None

if not state:
    if st.button("Start New Game"):
        game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'round': 1, 'started': False})
        st.rerun()
else:
    # --- LOBBY PHASE ---
    if not state.get('started'):
        st.subheader("Waiting Room")
        st.write("Players joined:", ", ".join(state.get('players', [])))
        
        player_name = st.text_input("Enter your name to join:")
        if st.button("Join"):
            if player_name and player_name not in state.get('players', []):
                game_ref.update({
                    'players': firestore.ArrayUnion([player_name]),
                    f"scores.{player_name}": 0
                })
                st.rerun()
        
        if len(state.get('players', [])) >= 2:
            if st.button("Start Game Now!"):
                players = state['players']
                roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
                selected_roles = roles[:len(players)]
                random.shuffle(selected_roles)
                role_map = {players[i]: selected_roles[i] for i in range(len(players))}
                game_ref.update({'roles': role_map, 'started': True})
                st.rerun()

    # --- PLAYING PHASE ---
    else:
        player_name = st.text_input("Enter your name to play:")
        my_role = state.get('roles', {}).get(player_name)
        
        if my_role:
            st.write(f"### Your Role: {my_role}")

            if my_role == 'Sipahi' and state.get('round', 1) <= 50:
                targets = [p for p in state['players'] if p != player_name]
                target = st.selectbox("Select target to catch:", targets)
                
                if st.button("Catch!"):
                    target_role = state['roles'].get(target)
                    if target_role == 'Chor':
                        game_ref.update({f"scores.{player_name}": firestore.Increment(500)})
                        st.success(f"Caught the Chor! {target} was the Chor. +500 pts.")
                    else:
                        chor_name = next((k for k, v in state['roles'].items() if v == 'Chor'), None)
                        if chor_name:
                            game_ref.update({f"scores.{chor_name}": firestore.Increment(500)})
                        st.error(f"Wrong! That was {target_role}. Points to Chor.")
                    
                    game_ref.update({'round': state.get('round', 1) + 1})
                    st.rerun()
        
        # --- RANKING ---
        if state.get('round', 1) > 50:
            st.balloons()
            st.subheader("Final Rankings")
            sorted_scores = sorted(state['scores'].items(), key=lambda x: x[1], reverse=True)
            st.table(sorted_scores)
