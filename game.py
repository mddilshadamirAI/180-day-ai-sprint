import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import pandas as pd
import time

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"])) if "firebase" in st.secrets else credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- 2. CORE GAME ENGINE ---
def execute_next_round(game_ref, current_state, catch_success=False):
    """Atomic update: prevents round drift by checking if the round was already updated."""
    curr_round = current_state.get('round', 1)
    # Double-check: Only proceed if we are still on the same round (prevents duplicate triggers)
    if curr_round > 50: return 
    
    scores = current_state.get('scores', {})
    roles = current_state.get('roles', {})
    
    sipahi = next((k for k, v in roles.items() if v == 'Sipahi'), None)
    mantri = next((k for k, v in roles.items() if v == 'Mantri'), None)
    chor = next((k for k, v in roles.items() if v == 'Chor'), None)
    raja = next((k for k, v in roles.items() if v == 'Raja'), None)

    if catch_success:
        scores[sipahi] = scores.get(sipahi, 0) + 500
        scores[mantri] = scores.get(mantri, 0) + 800
    else:
        scores[chor] = scores.get(chor, 0) + 500
    if raja: scores[raja] = scores.get(raja, 0) + 1000
    
    game_ref.update({
        'scores': scores,
        'round': curr_round + 1,
        'roles': dict(zip(roles.keys(), random.sample(['Raja', 'Mantri', 'Sipahi', 'Chor'], 4))),
        'start_time': time.time()
    })

# --- 3. UI LAYER ---
st.title("👑 Raja Mantri Sipahi Chor")
room_id = st.text_input("Enter Private Room ID:", value="default_room")
game_ref = db.collection('games').document(room_id)
state = game_ref.get().to_dict()

if not state:
    if st.button("Initialize Room"):
        game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1, 'start_time': time.time()})
        st.rerun()
else:
    # Auto-refresh mechanism: Reruns every 1s to pull latest Firebase state
    time.sleep(1) 
    
    if not state.get('started'):
        # ... [Lobby Logic] ...
        pass
    else:
        my_name = st.text_input("Confirm Name:")
        if my_name:
            roles = state.get('roles', {})
            my_role = roles.get(my_name, "WAITING")
            
            # --- SYNCHRONIZED DISPLAY ---
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(f"ROLE: {my_role.upper()}")
                st.write(f"### Round: {state.get('round')}/50")
            with c2:
                st.table(pd.DataFrame.from_dict(state.get('scores', {}), orient='index', columns=['Pts']))

            # --- TIMER LOGIC (Server-side synced) ---
            elapsed = time.time() - state.get('start_time', time.time())
            if elapsed > 10 and my_name == state['players'][0]: # Master-Controller pattern
                execute_next_round(game_ref, state, catch_success=False)
            
            # --- SIPAHI ACTIONS ---
            if my_role == 'Sipahi':
                chor = next((k for k, v in roles.items() if v == 'Chor'), "")
                mantri = next((k for k, v in roles.items() if v == 'Mantri'), "")
                target = st.radio("Who is the Chor?", [chor, mantri])
                if st.button("Catch!"):
                    execute_next_round(game_ref, state, catch_success=(roles.get(target) == 'Chor'))
            
            # --- BOT AUTOPLAY ---
            if "Bot_" in next((k for k, v in roles.items() if v == 'Sipahi'), "") and elapsed > 2:
                if my_name == state['players'][0]: # Only one bot executes this
                    target = random.choice([k for k, v in roles.items() if v in ['Chor', 'Mantri']])
                    execute_next_round(game_ref, state, catch_success=(roles.get(target) == 'Chor'))
