import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import pandas as pd
import time

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. HELPERS ---
def get_state(game_ref):
    doc = game_ref.get()
    return doc.to_dict() if doc.exists else None

def next_round(game_ref, state, catch_success=False, target=None):
    scores = state.get('scores', {})
    roles = state.get('roles', {})
    
    # Identify key players
    sipahi = next((k for k, v in roles.items() if v == 'Sipahi'), None)
    mantri = next((k for k, v in roles.items() if v == 'Mantri'), None)
    chor = next((k for k, v in roles.items() if v == 'Chor'), None)
    raja = next((k for k, v in roles.items() if v == 'Raja'), None)

    # Scoring Logic
    if catch_success:
        scores[sipahi] = scores.get(sipahi, 0) + 500
        scores[mantri] = scores.get(mantri, 0) + 800
    else:
        scores[chor] = scores.get(chor, 0) + 500
    if raja: scores[raja] = scores.get(raja, 0) + 1000
    
    # Prep next round
    new_roles = dict(zip(roles.keys(), random.sample(['Raja', 'Mantri', 'Sipahi', 'Chor'], 4)))
    game_ref.update({
        'scores': scores, 
        'round': state.get('round', 1) + 1, 
        'roles': new_roles, 
        'start_time': time.time()
    })

# --- 3. APP UI ---
st.title("👑 Raja Mantri Sipahi Chor")
room_id = st.text_input("Enter Private Room ID:", value="default_room")
game_ref = db.collection('games').document(room_id)
state = get_state(game_ref)

if not state:
    if st.button("Initialize Room"):
        game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1, 'start_time': time.time()})
        st.rerun()
else:
    # --- LOBBY ---
    if not state.get('started'):
        st.write(f"Players: {', '.join(state.get('players', []))}")
        name = st.text_input("Enter your name:")
        if st.button("Join"):
            game_ref.update({'players': list(set(state.get('players', []) + [name]))})
            st.rerun()
        if len(state.get('players', [])) >= 2 and st.button("Start Game"):
            players = state.get('players', [])
            all_p = players + [f"Bot_{i}" for i in range(4 - len(players))]
            game_ref.update({'roles': dict(zip(all_p, random.sample(['Raja', 'Mantri', 'Sipahi', 'Chor'], 4))), 
                             'started': True, 'scores': {p:0 for p in all_p}, 'start_time': time.time()})
            st.rerun()
    
    # --- PLAYING PHASE ---
    else:
        my_name = st.text_input("Confirm your name:")
        if my_name:
            roles = state.get('roles', {})
            my_role = roles.get(my_name, "N/A")
            
            # Display
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(f"ROLE: {my_role.upper() if my_role != 'N/A' else 'WAITING...'}")
                st.write(f"Round: {state.get('round')}")
            with c2:
                st.table(pd.DataFrame.from_dict(state.get('scores', {}), orient='index', columns=['Points']))

            # Timer Check
            elapsed = time.time() - state.get('start_time', time.time())
            if elapsed > 10:
                st.warning("Time limit exceeded! Advancing...")
                next_round(game_ref, state, catch_success=False)

            # Sipahi Actions
            if my_role == 'Sipahi':
                chor = next((k for k, v in roles.items() if v == 'Chor'), "")
                mantri = next((k for k, v in roles.items() if v == 'Mantri'), "")
                target = st.radio("Who is the Chor?", [chor, mantri])
                if st.button("Catch!"):
                    next_round(game_ref, state, catch_success=(roles.get(target) == 'Chor'), target=target)
            
            # Bot Auto-Play
            sipahi = next((k for k, v in roles.items() if v == 'Sipahi'), "")
            if "Bot_" in sipahi and elapsed > 2:
                target = random.choice([k for k, v in roles.items() if v in ['Chor', 'Mantri']])
                next_round(game_ref, state, catch_success=(roles.get(target) == 'Chor'), target=target)
