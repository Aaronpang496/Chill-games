import streamlit as st
import streamlit.components.v1 as components
import random
import json
import os
import math
import struct
import io
import base64

st.set_page_config(page_title="Chill Arcade", page_icon="🎮", layout="centered")

# ============================================================
# 🫧 DECLARE COMPONENT
# ============================================================
bubble_grid = components.declare_component(
    "bubble_grid",
    path="bubble_component",
)

# ============================================================
# 🔊 SOUNDS (small, only for non-bubble games)
# ============================================================
def make_wav_b64(freq=440, duration=0.15, volume=0.3, wave="sine", sweep_to=None):
    sr = 22050
    n = int(sr * duration)
    samples = []
    for i in range(n):
        t = i / sr
        f = freq + (sweep_to - freq) * (i / n) if sweep_to is not None else freq
        if wave == "sine":
            val = math.sin(2 * math.pi * f * t)
        elif wave == "square":
            val = 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0
        elif wave == "noise":
            val = random.uniform(-1, 1)
        else:
            val = math.sin(2 * math.pi * f * t)
        env = min(1.0, i / (sr * 0.005)) * math.exp(-3 * t / duration)
        samples.append(int(val * env * volume * 32767))
    buf = io.BytesIO()
    buf.write(b"RIFF")
    data_size = len(samples) * 2
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    for s in samples:
        buf.write(struct.pack("<h", s))
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_resource
def build_sounds():
    return {
        "hop":     make_wav_b64(400, 0.12, 0.3, "sine", sweep_to=700),
        "croc":    make_wav_b64(120, 0.4, 0.5, "square", sweep_to=60),
        "cashout": make_wav_b64(523, 0.4, 0.3, "sine"),
        "coins":   make_wav_b64(1047, 0.15, 0.3, "sine", sweep_to=1568),
        "achieve": make_wav_b64(660, 0.5, 0.3, "sine"),
        "balloon_pop": make_wav_b64(600, 0.12, 0.3, "noise", sweep_to=120),
    }

SOUNDS = build_sounds()

if "sound_queue" not in st.session_state:
    st.session_state.sound_queue = []

def play(name):
    st.session_state.sound_queue.append(name)

def play_sounds():
    if st.session_state.sound_queue:
        tags = ""
        for n in st.session_state.sound_queue:
            if n in SOUNDS:
                tags += f'<audio autoplay src="data:audio/wav;base64,{SOUNDS[n]}"></audio>'
        components.html(tags, height=0)
        st.session_state.sound_queue = []

# ============================================================
# 🐸 SVG FROG (unchanged from previous)
# ============================================================
def render_frog_svg(size=160, mood="happy", look_x=0, look_y=0, skin="green", animate=True):
    palettes = {
        "green":   {"body": "#4CAF50", "belly": "#A5D6A7", "spot": "#2E7D32", "cheek": "#F48FB1"},
        "royal":   {"body": "#66BB6A", "belly": "#C8E6C9", "spot": "#1B5E20", "cheek": "#FFB74D"},
        "crystal": {"body": "#4DD0E1", "belly": "#B2EBF2", "spot": "#00838F", "cheek": "#F48FB1"},
        "lizard":  {"body": "#8BC34A", "belly": "#DCEDC8", "spot": "#33691E", "cheek": "#FFAB91"},
    }
    p = palettes.get(skin, palettes["green"])
    px, py = look_x * 6, look_y * 6

    if mood == "dead":
        mouth = '<path d="M 38 78 Q 50 70 62 78" stroke="#1B5E20" stroke-width="3" fill="none" stroke-linecap="round"/>'
    elif mood == "jumping":
        mouth = '<path d="M 38 75 Q 50 90 62 75" stroke="#1B5E20" stroke-width="3" fill="none" stroke-linecap="round"/>'
    else:
        mouth = '<path d="M 36 74 Q 50 84 64 74" stroke="#1B5E20" stroke-width="3" fill="none" stroke-linecap="round"/>'

    if mood == "dead":
        left_eye = f'<circle cx="34" cy="38" r="13" fill="{p["body"]}"/><circle cx="34" cy="38" r="13" fill="white" opacity="0.9"/><line x1="28" y1="32" x2="40" y2="44" stroke="#1B5E20" stroke-width="3" stroke-linecap="round"/><line x1="40" y1="32" x2="28" y2="44" stroke="#1B5E20" stroke-width="3" stroke-linecap="round"/>'
        right_eye = f'<circle cx="66" cy="38" r="13" fill="{p["body"]}"/><circle cx="66" cy="38" r="13" fill="white" opacity="0.9"/><line x1="60" y1="32" x2="72" y2="44" stroke="#1B5E20" stroke-width="3" stroke-linecap="round"/><line x1="72" y1="32" x2="60" y2="44" stroke="#1B5E20" stroke-width="3" stroke-linecap="round"/>'
    else:
        left_eye = f'<circle cx="34" cy="38" r="13" fill="{p["body"]}"/><circle cx="34" cy="38" r="13" fill="white" opacity="0.95"/><circle cx="{34+px}" cy="{38+py}" r="5" fill="#1B1B1B"/><circle cx="{32+px}" cy="{36+py}" r="1.6" fill="white" opacity="0.9"/>'
        right_eye = f'<circle cx="66" cy="38" r="13" fill="{p["body"]}"/><circle cx="66" cy="38" r="13" fill="white" opacity="0.95"/><circle cx="{66+px}" cy="{38+py}" r="5" fill="#1B1B1B"/><circle cx="{64+px}" cy="{36+py}" r="1.6" fill="white" opacity="0.9"/>'

    anim_class = "frog-jump" if (animate and mood == "jumping") else "frog-dead" if (animate and mood == "dead") else "frog-idle" if animate else ""

    html = f"""
    <div style="display:flex; justify-content:center; align-items:center;">
      <svg viewBox="0 0 100 110" width="{size}" height="{int(size*1.1)}"
           class="{anim_class}" style="filter: drop-shadow(0 8px 12px rgba(0,0,0,0.25));">
        <ellipse cx="18" cy="98" rx="14" ry="6" fill="{p['spot']}"/>
        <ellipse cx="82" cy="98" rx="14" ry="6" fill="{p['spot']}"/>
        <ellipse cx="50" cy="72" rx="36" ry="28" fill="{p['body']}"/>
        <ellipse cx="50" cy="82" rx="24" ry="16" fill="{p['belly']}" opacity="0.85"/>
        <circle cx="24" cy="66" r="3.5" fill="{p['spot']}" opacity="0.6"/>
        <circle cx="76" cy="66" r="3.5" fill="{p['spot']}" opacity="0.6"/>
        <circle cx="30" cy="78" r="2.5" fill="{p['spot']}" opacity="0.5"/>
        <circle cx="70" cy="78" r="2.5" fill="{p['spot']}" opacity="0.5"/>
        <circle cx="34" cy="38" r="15" fill="{p['body']}"/>
        <circle cx="66" cy="38" r="15" fill="{p['body']}"/>
        {left_eye}
        {right_eye}
        {mouth}
        <circle cx="22" cy="66" r="5" fill="{p['cheek']}" opacity="0.55"/>
        <circle cx="78" cy="66" r="5" fill="{p['cheek']}" opacity="0.55"/>
        <ellipse cx="34" cy="100" rx="10" ry="4" fill="{p['spot']}"/>
        <ellipse cx="66" cy="100" rx="10" ry="4" fill="{p['spot']}"/>
      </svg>
    </div>
    <style>
      @keyframes frogBounce {{0%,100%{{transform:translateY(0) scale(1,1);}} 50%{{transform:translateY(-12px) scale(0.98,1.04);}}}}
      @keyframes frogJump {{0%{{transform:translateY(0) scale(1,1);}} 30%{{transform:translateY(-30px) scale(0.9,1.15);}} 70%{{transform:translateY(-10px) scale(1.05,0.95);}} 100%{{transform:translateY(0) scale(1,1);}}}}
      @keyframes frogDead {{0%,100%{{transform:rotate(-3deg);opacity:1;}} 50%{{transform:rotate(3deg);opacity:0.85;}}}}
      .frog-idle {{animation: frogBounce 1.6s ease-in-out infinite;}}
      .frog-jump {{animation: frogJump 0.5s ease-out;}}
      .frog-dead {{animation: frogDead 0.8s ease-in-out infinite;}}
    </style>
    """
    components.html(html, height=size + 40)

# ============================================================
# 🎈 SVG BALLOON
# ============================================================
def render_balloon_svg(size=70, color="#FF5252", popped=False, bob=True):
    if popped:
        html = f"""
        <div style="display:flex;justify-content:center;align-items:center;height:{size}px;">
          <svg viewBox="0 0 60 80" width="{size}" height="{int(size*1.3)}">
            <ellipse cx="30" cy="35" rx="20" ry="6" fill="{color}" opacity="0.3"/>
            <text x="30" y="45" text-anchor="middle" font-size="20" opacity="0.6">💥</text>
          </svg>
        </div>
        """
        components.html(html, height=size + 20)
        return

    bob_class = "balloon-bob" if bob else ""
    html = f"""
    <div style="display:flex;justify-content:center;align-items:center;height:{size}px;">
      <svg viewBox="0 0 60 100" width="{size}" height="{int(size*1.6)}" class="{bob_class}"
           style="filter:drop-shadow(0 4px 6px rgba(0,0,0,0.2));">
        <ellipse cx="30" cy="38" rx="22" ry="28" fill="{color}"/>
        <ellipse cx="22" cy="28" rx="6" ry="10" fill="white" opacity="0.35"/>
        <path d="M 26 66 L 30 72 L 34 66 Z" fill="{color}"/>
        <path d="M 30 72 Q 26 82 32 92" stroke="#666" stroke-width="1.5" fill="none"/>
      </svg>
    </div>
    <style>
      @keyframes bob {{0%,100%{{transform:translateY(0) rotate(-2deg);}} 50%{{transform:translateY(-8px) rotate(2deg);}}}}
      .balloon-bob {{animation: bob 2.5s ease-in-out infinite;}}
    </style>
    """
    components.html(html, height=size + 40)

# ============================================================
# 🧃 PARTICLES + SHAKE
# ============================================================
def render_particles(emoji="✨", count=12):
    parts = "".join([
        f'<span class="particle" style="left:{random.randint(10,90)}%;animation-delay:{random.uniform(0,0.5):.2f}s;">{emoji}</span>'
        for _ in range(count)
    ])
    html = f"""
    <div style="position:relative;height:180px;overflow:hidden;">{parts}</div>
    <style>
      .particle {{position:absolute;top:0;font-size:26px;animation:fall 1.4s ease-in forwards;opacity:0;}}
      @keyframes fall {{0%{{opacity:0;transform:translateY(-20px) rotate(0);}}20%{{opacity:1;}}100%{{opacity:0;transform:translateY(160px) rotate(360deg);}}}}
    </style>
    """
    components.html(html, height=180)

def render_screen_shake(strength=5, ms=400):
    html = f"""
    <style>
      @keyframes shakeScreen {{
        0%,100%{{transform:translate(0,0);}}10%{{transform:translate(-{strength}px,{strength}px);}}
        20%{{transform:translate({strength}px,-{strength}px);}}30%{{transform:translate(-{strength}px,-{strength}px);}}
        40%{{transform:translate({strength}px,{strength}px);}}50%{{transform:translate(-{strength}px,0);}}
        60%{{transform:translate({strength}px,0);}}70%{{transform:translate(0,-{strength}px);}}
        80%{{transform:translate(0,{strength}px);}}
      }}
      .stApp {{animation: shakeScreen {ms}ms ease-in-out;}}
    </style>
    """
    components.html(html, height=0)

# ============================================================
# 💾 SAVE
# ============================================================
SAVE_FILE = "chill_arcade_save.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "frog_best_run": 0, "frog_total_banked": 0, "frog_croc_deaths": 0,
        "bubble_total_pops": 0, "bubble_best_streak": 0,
        "balloon_popped": 0, "balloon_escaped": 0, "balloon_best": 0,
        "achievements": [], "frog_skin": "🐸",
        "unlocked_skins": ["🐸"], "coins": 0,
        "bubble_theme": "ocean",
    }

def persist():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.save, f)

if "save" not in st.session_state:
    st.session_state.save = load_save()

# ============================================================
# 🏆 ACHIEVEMENTS
# ============================================================
ACHIEVEMENTS = {
    "first_jump":     ("🐸 First Leap",       "Jump on your first lily pad."),
    "croc_survivor":  ("🐊 Croc Whisperer",   "Bank 100+ pts in one frog run."),
    "frog_legend":    ("👑 Frog Royalty",     "Bank 500+ pts total in frog."),
    "bubble_100":     ("🫧 Bubble Beginner",  "Pop 100 bubbles total."),
    "bubble_500":     ("💥 Bubble Maniac",    "Pop 500 bubbles total."),
    "streak_30":      ("🔥 Streak God",       "Hit a 30-pop bubble streak."),
    "combo_5":        ("⚡ Combo King",        "Reach a x5 combo."),
    "golden_hoard":   ("⭐ Golden Hoard",     "Pop 10 golden bubbles."),
    "rainbow_royalty":("🌈 Rainbow Royalty",  "Pop a rainbow bubble."),
    "balloon_10":     ("🎈 Balloon Rookie",   "Pop 10 balloons."),
    "balloon_50":     ("🎈🎈 Balloon Pro",    "Pop 50 balloons."),
}

def unlock(aid):
    if aid not in st.session_state.save["achievements"]:
        st.session_state.save["achievements"].append(aid)
        st.session_state.save["coins"] += 50
        persist()
        play("achieve")
        st.toast(f"🏆 {ACHIEVEMENTS[aid][0]}! +50 🪙")
        st.balloons()

# ============================================================
# 🛒 SHOP
# ============================================================
SKINS = {"🐸": 0, "🐸👑": 200, "🐸💎": 500, "🦎": 300}

# ============================================================
# NAV
# ============================================================
st.sidebar.title("🎮 Chill Arcade")
page = st.sidebar.radio("Menu:", ["🎮 Play", "🏆 Achievements", "🛒 Shop"])
save = st.session_state.save
st.sidebar.divider()
st.sidebar.metric("🪙 Coins", save["coins"])
ach_count = len(save["achievements"])
st.sidebar.progress(ach_count / len(ACHIEVEMENTS))
st.sidebar.caption(f"🏆 {ach_count}/{len(ACHIEVEMENTS)}")

# ============================================================
# ACHIEVEMENTS
# ============================================================
if page == "🏆 Achievements":
    st.title("🏆 Achievements")
    for aid, (name, desc) in ACHIEVEMENTS.items():
        (st.success if aid in save["achievements"] else st.info)(
            f"{'✅' if aid in save['achievements'] else '🔒'} **{name}** — {desc}"
        )
    st.divider()
    st.subheader("📊 Stats")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("🐸 Frog Best", save["frog_best_run"])
        st.metric("🐸 Total Banked", save["frog_total_banked"])
        st.metric("🫧 Total Pops", save["bubble_total_pops"])
        st.metric("🫧 Best Streak", save["bubble_best_streak"])
    with c2:
        st.metric("🎈 Balloons Popped", save["balloon_popped"])
        st.metric("🎈 Escaped", save["balloon_escaped"])
        st.metric("🎈 Best Score", save["balloon_best"])
        st.metric("🪙 Coins", save["coins"])

# ============================================================
# SHOP
# ============================================================
elif page == "🛒 Shop":
    st.title("🛒 Shop")

    st.subheader("🐸 Frog Skins")
    st.metric("🪙 Your Coins", save["coins"])
    cols = st.columns(len(SKINS))
    for i, (skin, cost) in enumerate(SKINS.items()):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center;font-size:60px;'>{skin}</h1>", unsafe_allow_html=True)
            if skin in save["unlocked_skins"]:
                if st.button("✅ Equipped" if save["frog_skin"] == skin else "Equip",
                             key=f"fsk{skin}", use_container_width=True):
                    save["frog_skin"] = skin
                    persist()
                    play("coins")
                    st.rerun()
            else:
                if st.button(f"Buy ({cost}🪙)", key=f"fbuy{skin}", use_container_width=True):
                    if save["coins"] >= cost:
                        save["coins"] -= cost
                        save["unlocked_skins"].append(skin)
                        save["frog_skin"] = skin
                        persist()
                        play("coins")
                        st.toast(f"Unlocked {skin}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Need more coins!")

    st.divider()
    st.subheader("🫧 Bubble Themes")
    THEMES = ["ocean", "pastel", "sunset", "holiday"]
    theme_icons = {"ocean": "🌊", "pastel": "🌸", "sunset": "🌅", "holiday": "🎄"}
    cols = st.columns(4)
    for i, t in enumerate(THEMES):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center;font-size:50px;'>{theme_icons[t]}</h1>", unsafe_allow_html=True)
            if st.button(
                "✅ Equipped" if save.get("bubble_theme", "ocean") == t else "Equip",
                key=f"th{t}", use_container_width=True
            ):
                save["bubble_theme"] = t
                persist()
                play("coins")
                st.rerun()

    st.divider()
    if st.button("🔴 RESET ALL"):
        if st.session_state.get("confirm_reset"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.session_state.save = load_save()
            st.session_state.confirm_reset = False
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.warning("⚠️ Click again to CONFIRM reset.")

# ============================================================
# PLAY
# ============================================================
elif page == "🎮 Play":
    game = st.sidebar.radio("Game:", ["🫧 Bubble Wrap", "🎈 Balloon Pop", "🐸 Frog Jump"])

    # --------------------------------------
    # 🫧 BUBBLE WRAP — THE STAR
    # --------------------------------------
    if game == "🫧 Bubble Wrap":
        st.title("🫧 Bubble Wrap")
        st.caption("Pop bubbles. Chain combos. Find the golden ones. Real SVG bubbles.")

        # Init session state
        if "bw_state" not in st.session_state:
            st.session_state.bw_state = [False] * 100
            st.session_state.bw_power_ups = {}
            st.session_state.bw_finished_reward = False
            st.session_state.bw_golden_popped = 0

        # Generate power-ups on fresh sheet
        if not any(st.session_state.bw_state) and not st.session_state.bw_power_ups:
            power = {}
            idxs = random.sample(range(100), 12)
            for i, idx in enumerate(idxs):
                power[idx] = "gold" if i < 8 else "rainbow"
            st.session_state.bw_power_ups = power

        # Render the component
        result = bubble_grid(
            rows=10,
            cols=10,
            state=st.session_state.bw_state,
            best_streak=save["bubble_best_streak"],
            total_pops=save["bubble_total_pops"],
            theme=save.get("bubble_theme", "ocean"),
            power_ups=st.session_state.bw_power_ups,
            key="bubblegrid",
            default=None,
        )

        # Sync back from component
        if result:
            # Update state
            if "state" in result:
                st.session_state.bw_state = [bool(x) for x in result["state"]]

            # Update totals
            new_total = result.get("total_pops", save["bubble_total_pops"])
            if new_total > save["bubble_total_pops"]:
                delta = new_total - save["bubble_total_pops"]
                save["bubble_total_pops"] = new_total
                save["coins"] += delta // 5

                # Track golden pop
                if "combo" in result and result["combo"] >= 5:
                    unlock("combo_5")
                if save["bubble_total_pops"] >= 100:
                    unlock("bubble_100")
                if save["bubble_total_pops"] >= 500:
                    unlock("bubble_500")

            new_streak = result.get("best_streak", save["bubble_best_streak"])
            if new_streak > save["bubble_best_streak"]:
                save["bubble_best_streak"] = new_streak
                if new_streak >= 30:
                    unlock("streak_30")

            # Finished sheet
            if result.get("finished") and not st.session_state.bw_finished_reward:
                st.session_state.bw_finished_reward = True
                save["coins"] += 20
                st.balloons()
                st.toast("🎉 Sheet cleared! +20 🪙")

            if not result.get("finished"):
                st.session_state.bw_finished_reward = False

            persist()

        # Stats row
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🫧 Total Pops", save["bubble_total_pops"])
        c2.metric("🔥 Best Streak", save["bubble_best_streak"])
        c3.metric("⚡ Combo", result.get("combo", 1) if result else 1)
        c4.metric("⭐ Gold Popped", st.session_state.bw_golden_popped)

        if st.button("🔄 Reset Sheet"):
            st.session_state.bw_state = [False] * 100
            st.session_state.bw_power_ups = {}
            st.session_state.bw_finished_reward = False
            st.rerun()

    # --------------------------------------
    # 🎈 BALLOON POP
    # --------------------------------------
    elif game == "🎈 Balloon Pop":
        st.title("🎈 Balloon Pop")
        st.caption("Pop balloons before they float away!")

        if "balloons" not in st.session_state:
            st.session_state.balloons = []
            st.session_state.balloon_score = 0
            st.session_state.balloon_missed = 0

        BALLOON_COLORS = ["#FF5252", "#FF9800", "#FFEB3B", "#4CAF50", "#2196F3", "#9C27B0", "#E91E63"]

        if random.random() < 0.6 and len(st.session_state.balloons) < 6:
            st.session_state.balloons.append({
                "id": random.randint(0, 999999),
                "color": random.choice(BALLOON_COLORS),
                "life": 6,
            })

        new_b = []
        for b in st.session_state.balloons:
            b["life"] -= 1
            if b["life"] > 0:
                new_b.append(b)
            else:
                st.session_state.balloon_missed += 1
                save["balloon_escaped"] += 1
        st.session_state.balloons = new_b

        if st.session_state.balloons:
            cols = st.columns(min(len(st.session_state.balloons), 6))
            for i, b in enumerate(st.session_state.balloons[:6]):
                with cols[i]:
                    render_balloon_svg(size=70, color=b["color"], popped=False, bob=True)
                    if st.button("🎈 POP", key=f"bp{b['id']}", use_container_width=True):
                        st.session_state.balloons.remove(b)
                        st.session_state.balloon_score += 1
                        save["balloon_popped"] += 1
                        if st.session_state.balloon_score > save["balloon_best"]:
                            save["balloon_best"] = st.session_state.balloon_score
                        play("balloon_pop")
                        render_particles("🎈", 6)
                        if save["balloon_popped"] == 10:
                            unlock("balloon_10")
                        if save["balloon_popped"] == 50:
                            unlock("balloon_50")
                        persist()
                        st.rerun()
        else:
            st.markdown("<h1 style='text-align:center;font-size:60px;'>☁️</h1>", unsafe_allow_html=True)

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("🎈 Popped", st.session_state.balloon_score)
        c2.metric("☁️ Escaped", st.session_state.balloon_missed)
        c3.metric("🏆 Best", save["balloon_best"])

        if st.button("🔄 Refresh Sky", use_container_width=True):
            st.rerun()

    # --------------------------------------
    # 🐸 FROG JUMP
    # --------------------------------------
    elif game == "🐸 Frog Jump":
        st.title("🐸 Frog on a Lily Pad")
        st.caption("Each jump = points. Crocs hide. Cash out or risk it?")

        if "frog_run" not in st.session_state:
            st.session_state.frog_run = 0
            st.session_state.frog_pads = []
            st.session_state.frog_msg = "Pick a lily pad..."
            st.session_state.frog_dead = False
            st.session_state.frog_flash = ""
            st.session_state.frog_look = "center"

        if not st.session_state.frog_pads and not st.session_state.frog_dead:
            danger = min(3, 1 + st.session_state.frog_run // 40)
            pads = ["croc" if random.random() < danger * 0.15 else "safe" for _ in range(3)]
            if "croc" not in pads:
                pads[random.randint(0, 2)] = "croc"
            st.session_state.frog_pads = pads

        skin_map = {"🐸": "green", "🐸👑": "royal", "🐸💎": "crystal", "🦎": "lizard"}
        current_skin = skin_map.get(save["frog_skin"], "green")

        if st.session_state.frog_dead:
            mood = "dead"
        elif st.session_state.frog_flash == "✨ HOP! ✨":
            mood = "jumping"
        else:
            mood = "happy"

        look_map = {"left": (-1, 0), "center": (0, 0), "right": (1, 0)}
        lx, ly = look_map.get(st.session_state.frog_look, (0, 0))

        render_frog_svg(size=160, mood=mood, look_x=lx, look_y=ly, skin=current_skin)

        if st.session_state.frog_flash:
            st.markdown(f"<h3 style='text-align:center;'>{st.session_state.frog_flash}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>{st.session_state.frog_msg}</h3>", unsafe_allow_html=True)

        if not st.session_state.frog_dead:
            cols = st.columns(3)
            for i, pad in enumerate(st.session_state.frog_pads):
                with cols[i]:
                    if st.button("🪷 JUMP", key=f"fp{i}", use_container_width=True):
                        st.session_state.frog_look = ["left", "center", "right"][i]
                        unlock("first_jump")
                        if pad == "croc":
                            lost = st.session_state.frog_run
                            st.session_state.frog_run = 0
                            st.session_state.frog_pads = []
                            st.session_state.frog_dead = True
                            st.session_state.frog_msg = f"🐊 CROCODILE! Lost {lost} pts!"
                            st.session_state.frog_flash = "💀 SPLASH 💀"
                            save["frog_croc_deaths"] += 1
                            persist()
                            play("croc")
                            render_screen_shake(8, 400)
                        else:
                            pts = random.randint(5, 15) + st.session_state.frog_run // 3
                            st.session_state.frog_run += pts
                            st.session_state.frog_pads = []
                            st.session_state.frog_msg = f"+{pts} pts! Keep going or cash out?"
                            st.session_state.frog_flash = "✨ HOP! ✨"
                            play("hop")
                            render_particles("✨", 6)
                        st.rerun()

            st.divider()
            if st.button("💰 CASH OUT", use_container_width=True, type="primary"):
                if st.session_state.frog_run > 0:
                    run = st.session_state.frog_run
                    save["frog_total_banked"] += run
                    if run > save["frog_best_run"]:
                        save["frog_best_run"] = run
                    save["coins"] += run // 2
                    st.session_state.frog_run = 0
                    st.session_state.frog_pads = []
                    st.session_state.frog_msg = f"💰 Banked {run} pts!"
                    st.session_state.frog_flash = "💰 CHA-CHING 💰"
                    play("cashout")
                    play("coins")
                    render_particles("💰", 15)
                    if run >= 100:
                        unlock("croc_survivor")
                    if save["frog_total_banked"] >= 500:
                        unlock("frog_legend")
                    persist()
                    st.rerun()
        else:
            st.error("💀 Splash! The frog got eaten.")
            if st.button("🐸 Try Again", use_container_width=True, type="primary"):
                st.session_state.frog_dead = False
                st.session_state.frog_pads = []
                st.session_state.frog_msg = "Pick a lily pad..."
                st.session_state.frog_flash = ""
                st.rerun()

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("🏆 Banked", save["frog_total_banked"])
        c2.metric("🔥 Run", st.session_state.frog_run)
        c3.metric("⭐ Best", save["frog_best_run"])

play_sounds()
