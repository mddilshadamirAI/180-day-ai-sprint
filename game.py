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

st.title("👑 Raja Mantri Sipahi Chor")

# --- 2. MATCHMAKER (ROOM SYSTEM) ---
def get_room():
    # Find any room that is not started and has < 4 players
    rooms = db.collection('games').where('started', '==', False).stream()
    for room in rooms:
        data = room.to_dict()
        if len(data.get('players', [])) < 4:
            return room
    
    # If no room found, create a new one
    new_room = db.collection('games').document()
    new_room.set({
        'players': [], 'roles': {}, 'scores': {}, 
        'started': False, 'round': 1
    })
    return new_room.get()

doc = get_room()
game_ref = doc.reference
state = doc.to_dict()

# --- 3. LOBBY ---
if not state.get('started'):
    st.write(f"Room ID: {game_ref.id}")
    players = state.get('players', [])
    st.write(f"Players: {', '.join(players)}")
    
    name = st.text_input("Enter your name:")
    if st.button("Join"):
        if name and name not in players:
            # Simple list update, no path nesting
            players.append(name)
            game_ref.update({'players': players})
            st.rerun()
            
    if len(players) >= 2 and st.button("Start Game"):
        roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
        random.shuffle(roles)
        # Fill empty spots with 'Bot'
        all_p = players + [f"Bot_{i}" for i in range(4 - len(players))]
        role_map = dict(zip(all_p, roles))
        game_ref.update({'roles': role_map, 'started': True})
        st.rerun()

# --- 4. GAME ENGINE ---
else:
    name = st.text_input("Enter your name to play:")
    roles = state.get('roles', {})
    my_role = roles.get(name)
    
    if my_role:
        st.write(f"### Role: {my_role}")
        if my_role == 'Sipahi':
            target = st.selectbox("Catch:", [p for p in roles.keys() if p != name])
            if st.button("Catch!"):
                scores = state.get('scores', {})
                if roles.get(target) == 'Chor':
                    scores[name] = scores.get(name, 0) + 500
                    st.success("Caught!")
                else:
                    chor = next((k for k, v in roles.items() if v == 'Chor'), "Chor")
                    scores[chor] = scores.get(chor, 0) + 500
                    st.error("Wrong!")
                game_ref.update({'scores': scores, 'round': state.get('round', 1) + 1})
                st.rerun()
    
    if state.get('round', 1) > 50:
        st.subheader("Leaderboard")
        st.table(sorted(state.get('scores', {}).items(), key=lambda x: x[1], reverse=True))
