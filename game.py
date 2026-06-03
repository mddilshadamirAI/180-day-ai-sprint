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

# --- 2. MATCHMAKER ---
def get_room():
    # Find an open room
    rooms = db.collection('games').where('started', '==', False).limit(1).stream()
    for room in rooms:
        return room.reference
    # Create a new room if none exists
    new_room = db.collection('games').document()
    new_room.set({'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1})
    return new_room

game_ref = get_room()
state = game_ref.get().to_dict()

st.title("👑 Raja Raaj Karta Hai")
st.write(f"Room ID: {game_ref.id}")

# --- 3. LOBBY PHASE ---
if not state.get('started'):
    players = state.get('players', [])
    st.write(f"Players: {', '.join(players)}")
    
    player_name = st.text_input("Enter your name:")
    if st.button("Join"):
        if player_name and player_name not in players and len(players) < 4:
            game_ref.update({'players': players + [player_name]})
            st.rerun()
            
    if len(players) >= 2 and st.button("Start Game"):
        roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
        random.shuffle(roles)
        # Pad with bots to ensure 4 total
        all_p = players + [f"Bot_{i}" for i in range(4 - len(players))]
        role_map = dict(zip(all_p, roles))
        game_ref.set({'roles': role_map, 'started': True}, merge=True)
        st.rerun()

# --- 4. PLAYING PHASE ---
else:
    my_name = st.text_input("Enter your name to play:")
    roles = state.get('roles', {})
    my_role = roles.get(my_name)
    
    if my_role:
        st.write(f"### Your Role: {my_role}")
        # Sipahi can only play if they are a human
        if my_role == 'Sipahi' and state.get('round', 1) <= 50:
            targets = [p for p in roles.keys() if p != my_name]
            target = st.selectbox("Catch:", targets)
            if st.button("Catch!"):
                scores = state.get('scores', {})
                if roles.get(target) == 'Chor':
                    scores[my_name] = scores.get(my_name, 0) + 500
                else:
                    chor = next((k for k, v in roles.items() if v == 'Chor'), "Chor")
                    scores[chor] = scores.get(chor, 0) + 500
                game_ref.update({'scores': scores, 'round': state.get('round', 1) + 1})
                st.rerun()
    else:
        st.warning("Waiting for game data...")

    # --- 5. RANKING ---
    if state.get('round', 1) > 50:
        st.subheader("Leaderboard")
        st.table(sorted(state.get('scores', {}).items(), key=lambda x: x[1], reverse=True))
