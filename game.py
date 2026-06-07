import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. ROOM & STATE MANAGEMENT ---
st.title("👑 Raja Mantri Sipahi Chor")
room_id = st.text_input("Enter Private Room ID:", value="default_room")
game_ref = db.collection('games').document(room_id)
doc = game_ref.get()

if not doc.exists:
    state = {'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1}
    game_ref.set(state)
else:
    state = doc.to_dict()

# --- 3. LOBBY PHASE ---
if not state.get('started'):
    players = state.get('players', [])
    st.write(f"### Players in room: {', '.join(players)}")
    
    name = st.text_input("Enter your name:")
    if st.button("Join"):
        if name and name not in players and len(players) < 4:
            game_ref.update({'players': players + [name]})
            st.rerun()

    if len(players) >= 2 and st.button("Start Game"):
        roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
        random.shuffle(roles)
        all_p = players + [f"Bot_{i}" for i in range(4 - len(players))]
        role_map = dict(zip(all_p, roles))
        game_ref.update({'roles': role_map, 'started': True})
        st.rerun()

# --- 4. PLAYING PHASE ---
else:
    my_name = st.text_input("Confirm your name:")
    roles = state.get('roles', {})
    my_role = roles.get(my_name)
    
    if my_role:
        st.write(f"### Your Role: {my_role}")
        
        # Raja Visibility
        if my_role == 'Raja':
            with st.expander("👑 Raja's Secret View"):
                st.json(roles)

        # Sipahi Catch Logic
        if my_role == 'Sipahi' and state.get('round', 1) <= 50:
            targets = [p for p in roles.keys() if p != my_name]
            target = st.selectbox("Select target to catch:", targets)
            
            if st.button("Catch!"):
                scores = state.get('scores', {})
                # Logic to handle catch
                if roles.get(target) == 'Chor':
                    scores[my_name] = scores.get(my_name, 0) + 500
                    st.success(f"Caught the Chor! {target} was the Chor.")
                else:
                    chor = next((k for k, v in roles.items() if v == 'Chor'), "Chor")
                    scores[chor] = scores.get(chor, 0) + 500
                    st.error(f"Wrong! {target} was the {roles.get(target)}.")
                
                # Shuffle for next round
                new_pool = ['Raja', 'Mantri', 'Sipahi', 'Chor']
                random.shuffle(new_pool)
                players = state.get('players', [])
                all_p = players + [f"Bot_{i}" for i in range(4 - len(players))]
                new_roles = dict(zip(all_p, new_pool))
                
                game_ref.update({
                    'scores': scores, 
                    'round': state.get('round', 1) + 1,
                    'roles': new_roles
                })
                st.rerun()
    else:
        st.warning("You are not part of this active game.")

    # --- 5. RANKING ---
    if state.get('round', 1) > 50:
        st.balloons()
        st.subheader("Final Rankings")
        sorted_scores = sorted(state.get('scores', {}).items(), key=lambda x: x[1], reverse=True)
        st.table(sorted_scores)
        if st.button("Start New Game"):
            game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1})
            st.rerun()
