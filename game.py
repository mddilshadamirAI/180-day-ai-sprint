import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random

# --- FIREBASE CONFIG ---
if not firebase_admin._apps:
    # If running on Streamlit Cloud, use st.secrets
    if "firebase" in st.secrets:
        # We store the JSON structure in a 'firebase' secret in Streamlit
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        # If running locally on your PC, use the file
        cred = credentials.Certificate("serviceAccountKey.json")
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
game_ref = db.collection('games').document('active_match')

# --- 2. GAME LOGIC HELPERS ---
def initialize_game():
    game_ref.set({
        'players': [], 'roles': {}, 'scores': {}, 
        'round': 1, 'active': True, 'last_move': None
    })

# --- 3. UI LAYOUT ---
st.title("👑 Raja Mantri Sipahi Chor")

# Handle Player Joining
state = game_ref.get().to_dict()
if not state:
    if st.button("Start New Game"):
        initialize_game()
        st.rerun()
else:
    player_name = st.text_input("Enter your name:")
    if st.button("Join"):
        if len(state['players']) < 4 and player_name not in state['players']:
            game_ref.update({'players': firestore.ArrayUnion([player_name])})
            game_ref.update({f"scores.{player_name}": 0})
            st.rerun()

    # --- 4. GAME ENGINE (PLAYING PHASE) ---
    if len(state.get('players', [])) == 4:
        # Auto-assign roles if not assigned
        if not state['roles']:
            roles = ['Raja', 'Mantri', 'Sipahi', 'Chor']
            random.shuffle(roles)
            role_map = {state['players'][i]: roles[i] for i in range(4)}
            game_ref.update({'roles': role_map})
            st.rerun()

        my_role = state['roles'].get(player_name)
        st.write(f"### Your Role: {my_role}")

        if my_role == 'Sipahi' and state['round'] <= 50:
            target = st.selectbox("Select target to catch:", [p for p in state['players'] if p != player_name])
            if st.button("Catch!"):
                # Logic: Check if target is Chor
                target_role = state['roles'][target]
                if target_role == 'Chor':
                    game_ref.update({f"scores.{player_name}": firestore.Increment(500)})
                    st.success("Caught the Chor! +500")
                else:
                    chor_name = [k for k, v in state['roles'].items() if v == 'Chor'][0]
                    game_ref.update({f"scores.{chor_name}": firestore.Increment(500)})
                    st.error(f"Wrong! That was {target_role}. Points to Chor.")
                
                # Increment Round
                game_ref.update({'round': state['round'] + 1})
                st.rerun()

    # --- 5. RANKING SYSTEM ---
    if state.get('round', 0) > 50:
        st.balloons()
        st.subheader("Final Rankings")
        scores = state.get('scores', {})
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        st.table(sorted_scores)
