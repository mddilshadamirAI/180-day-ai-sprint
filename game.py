import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random

# --- 1. FIREBASE CONFIG ---
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

# --- 2. DATA FETCH ---
doc = game_ref.get()
state = doc.to_dict() if doc.exists else {
    'players': [], 'roles': {}, 'scores': {}, 'round': 1, 'started': False
}

# --- 3. AUTO-RESET (If game ends) ---
if state.get('round', 0) > 50:
    game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'round': 1, 'started': False}, merge=True)
    st.rerun()

# --- 4. LOBBY / JOINING ---
if not state.get('started', False):
    st.subheader("Waiting Room")
    players = state.get('players', [])
    st.write(f"Players joined: {', '.join(players)}")
    
    player_name = st.text_input("Enter your name:")
    if st.button("Join"):
        if player_name and player_name not in players:
            # Use merge=True to prevent path errors
            game_ref.set({
                'players': players + [player_name],
                f"scores.{player_name}": 0
            }, merge=True)
            st.rerun()
            
    if len(players) >= 2:
        if st.button("Start Game Now!"):
            roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
            random.shuffle(roles)
            # Create a full list of 4: players + bots
            all_participants = players + [f"Bot {i}" for i in range(4 - len(players))]
            # Pair them using zip (Safe from IndexError)
            role_map = dict(zip(all_participants, roles))
            
            game_ref.set({'roles': role_map, 'started': True}, merge=True)
            st.rerun()

# --- 5. PLAYING PHASE ---
else:
    player_name = st.text_input("Confirm your name to play:")
    roles = state.get('roles', {})
    my_role = roles.get(player_name)
    
    if my_role:
        st.write(f"### Your Role: {my_role}")
        
        if my_role == 'Sipahi':
            targets = [p for p in roles.keys() if p != player_name]
            target = st.selectbox("Select target to catch:", targets)
            
            if st.button("Catch!"):
                if roles.get(target) == 'Chor':
                    game_ref.set({f"scores.{player_name}": firestore.Increment(500)}, merge=True)
                    st.success(f"Caught the Chor! {target} was the Chor.")
                else:
                    chor = next((k for k, v in roles.items() if v == 'Chor'), "Chor")
                    game_ref.set({f"scores.{chor}": firestore.Increment(500)}, merge=True)
                    st.error(f"Wrong! {target} was {roles.get(target)}.")
                
                game_ref.set({'round': state.get('round', 1) + 1}, merge=True)
                st.rerun()
    else:
        st.warning("Please enter your registered name.")

    # --- 6. LEADERBOARD ---
    st.divider()
    st.subheader("Leaderboard")
    scores = state.get('scores', {})
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    st.table(sorted_scores)
