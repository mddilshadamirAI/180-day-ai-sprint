import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import pandas as pd

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. ROOM & STATE ---
st.title("👑 Raja Mantri Sipahi Chor")
room_id = st.text_input("Enter Private Room ID:", value="default_room")
game_ref = db.collection('games').document(room_id)
state = game_ref.get().to_dict() or {'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1}

# Initialize scores for all players in the lobby
players = state.get('players', [])
all_players = players + [f"Bot_{i}" for i in range(4 - len(players))]

# --- 3. LOBBY PHASE ---
if not state.get('started'):
    st.write(f"### Players in room: {', '.join(players)}")
    name = st.text_input("Enter your name:")
    if st.button("Join"):
        if name and name not in players and len(players) < 4:
            game_ref.update({'players': players + [name]})
            st.rerun()
    if len(players) >= 2 and st.button("Start Game"):
        roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
        random.shuffle(roles)
        # Initialize scores to 0 for everyone
        initial_scores = {p: 0 for p in all_players}
        game_ref.update({'roles': dict(zip(all_players, roles)), 'started': True, 'scores': initial_scores})
        st.rerun()

# --- 4. PLAYING PHASE ---
else:
    my_name = st.text_input("Confirm your name:")
    roles = state.get('roles', {})
    scores = state.get('scores', {})
    
    # Ensure Scorecard shows all 4 players
    full_scores = {p: scores.get(p, 0) for p in all_players}

    if state.get('round', 1) <= 50:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader(f"Round: {state.get('round')}")
        with c2:
            st.subheader("Scorecard")
            st.table(pd.DataFrame.from_dict(full_scores, orient='index', columns=['Points']))

        my_role = roles.get(my_name)
        
        # --- BOT LOGIC ---
        sipahi_name = next((k for k, v in roles.items() if v == 'Sipahi'), "")
        if "Bot_" in sipahi_name:
            chor = next((k for k, v in roles.items() if v == 'Chor'), None)
            mantri = next((k for k, v in roles.items() if v == 'Mantri'), None)
            target = random.choice([chor, mantri])
            st.write(f"🤖 Bot Sipahi chose: {target}")
            
            if st.button("Bot Auto-Catch"):
                # Scoring Logic
                if roles.get(target) == 'Chor':
                    scores[sipahi_name] = scores.get(sipahi_name, 0) + 500
                    scores[mantri] = scores.get(mantri, 0) + 800
                else:
                    scores[chor] = scores.get(chor, 0) + 500
                
                raja = next((k for k, v in roles.items() if v == 'Raja'), None)
                if raja: scores[raja] = scores.get(raja, 0) + 1000
                
                new_roles = dict(zip(roles.keys(), random.sample(['Raja', 'Mantri', 'Sipahi', 'Chor'], 4)))
                game_ref.update({'scores': scores, 'round': state.get('round', 1) + 1, 'roles': new_roles})
                st.rerun()

        # --- HUMAN SIPAHI LOGIC ---
        elif my_role == 'Sipahi':
            chor = next((k for k, v in roles.items() if v == 'Chor'), None)
            mantri = next((k for k, v in roles.items() if v == 'Mantri'), None)
            target = st.radio("Who is the Chor?", [chor, mantri])
            if st.button("Catch!"):
                if roles.get(target) == 'Chor':
                    scores[my_name] = scores.get(my_name, 0) + 500
                    scores[mantri] = scores.get(mantri, 0) + 800
                else:
                    scores[chor] = scores.get(chor, 0) + 500
                
                raja = next((k for k, v in roles.items() if v == 'Raja'), None)
                if raja: scores[raja] = scores.get(raja, 0) + 1000
                
                new_roles = dict(zip(roles.keys(), random.sample(['Raja', 'Mantri', 'Sipahi', 'Chor'], 4)))
                game_ref.update({'scores': scores, 'round': state.get('round', 1) + 1, 'roles': new_roles})
                st.rerun()
        else:
            st.write(f"Your role: **{my_role}**. Please wait for the Sipahi to act.")

    # --- 5. RANKING ---
    else:
        st.balloons()
        st.subheader("🏆 Final Leaderboard")
        df = pd.DataFrame.from_dict(full_scores, orient='index', columns=['Points'])
        df['Rank'] = df['Points'].rank(ascending=False, method='min').astype(int)
        st.table(df.sort_values(by='Rank'))
        if st.button("Restart Game"):
            game_ref.set({'players': [], 'roles': {}, 'scores': {}, 'started': False, 'round': 1})
            st.rerun()
