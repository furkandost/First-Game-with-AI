import sys
import unittest.mock as mock

if 'tkinter' not in sys.modules:
    sys.modules['tkinter'] = mock.MagicMock()
    sys.modules['tkinter.ttk'] = mock.MagicMock()
    sys.modules['tkinter.messagebox'] = mock.MagicMock()

import streamlit as st
from idlegame import LoopKnight

st.set_page_config(
    page_title="LoopKnight - Online",
    page_icon="⚔️",
    layout="centered"
)

class StreamlitRootMock:
    def __init__(self): pass
    def title(self, t): pass
    def geometry(self, g): pass
    def configure(self, **kwargs): pass
    def after(self, ms, callback, *args): pass
    def mainloop(self): pass

if 'game_instance' not in st.session_state:
    root_mock = StreamlitRootMock()
    st.session_state.game = LoopKnight(root_mock)

game = st.session_state.game

# --- ARAYÜZ ---
st.title("🛡️ LoopKnight - Tarayıcı Sürümü")

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Altın", game.format_number(game.altin))
    st.metric("🛡️ Asker Hasarı", f"+{game.format_number(game.get_auto_dps())}/sn")
with col2:
    st.metric("🦴 Zones Bones", game.format_number(game.zones_bones))
    st.metric("🏰 Bölge", f"Zindan {game.asama} — Oda {game.kademe}/10")

st.divider()

is_boss_check = getattr(game, 'is_boss', (game.kademe == 10))
monster_name = game.get_monster_name(game.asama, game.kademe, is_boss_check)
st.subheader(monster_name)

max_hp = game.current_monster_max_hp if game.current_monster_max_hp > 0 else 1
cur_hp = max(0, game.current_monster_hp)
hp_percent = min(1.0, cur_hp / max_hp)
st.progress(hp_percent, text=f"HP: {game.format_number(cur_hp)} / {game.format_number(max_hp)}")

# SALDIRI BUTONU
click_dmg = game.get_click_damage()
if st.button(f"⚔️ SALDIR! (Tıklama Hasarı: {game.format_number(click_dmg)})", use_container_width=True, type="primary"):
    game.attack()
    st.rerun()

st.divider()

st.markdown("##### Satın Alma Çarpanı")
m_cols = st.columns(3)
with m_cols[0]:
    if st.button("x1", use_container_width=True):
        game.set_buy_multiplier(1)
        st.rerun()
with m_cols[1]:
    if st.button("x10", use_container_width=True):
        game.set_buy_multiplier(10)
        st.rerun()
with m_cols[2]:
    if st.button("x100", use_container_width=True):
        game.set_buy_multiplier(100)
        st.rerun()

st.write(f"Aktif Çarpan: **x{game.buy_multiplier}**")
st.divider()

tab_up, tab_sw, tab_un, tab_stg = st.tabs(["🗡️ Geliştirmeler", "⚔️ Kılıçlar", "🛡️ Askerler", "🏰 Zindanlar"])

with tab_up:
    st.markdown("### Temel Özellikler")
    for key, title, desc in [("hasar", "Temel Hasar", "Tıklama gücünü artırır."), 
                             ("sans", "Kritik Şansı", "Kritik oranı."), 
                             ("kritik_hasar", "Kritik Hasar", "Kritik ekstra çarpanı."), 
                             ("zirh_delme", "Zırh Delme", "Zırh yok sayma."), 
                             ("zehir", "Zehir Bulutu", "Saniyede zehir vurur.")]:
        val, cost, mult, limit = game.stats[key]
        target_buy = game.get_stat_buy_count(key)
        total_cost = game.get_multi_cost(cost, mult, target_buy) if target_buy > 0 else cost
        
        c1, c2 = st.columns([2, 1])
        with c1:
            val_str = f"%{val*100:.0f}" if key in ["sans", "zirh_delme"] else (f"{val:.1f}x" if key == "kritik_hasar" else game.format_number(val))
            st.write(f"**{title}** (Mevcut: {val_str})")
            st.caption(desc)
        with c2:
            if limit and val >= limit:
                st.button("MAKS", disabled=True, key=f"stat_max_{key}")
            else:
                btn_label = f"Yükselt (x{target_buy})\n💰 {game.format_number(total_cost)}"
                if st.button(btn_label, key=f"stat_{key}", disabled=(game.altin < total_cost or target_buy <= 0)):
                    game.buy_stat(key)
                    st.rerun()

with tab_sw:
    st.markdown("### Kılıç Mağazası")
    for sk, v in game.swords.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"{v[4]} **{v[0]}** (+{v[1]}x Hasار)")
            st.caption(v[5])
        with c2:
            if v[3]:
                st.success("Sahip Olundu")
            else:
                if st.button(f"Al\n💰 {game.format_number(v[2])}", key=f"sw_{sk}", disabled=(game.altin < v[2])):
                    game.buy_sword(sk)
                    st.rerun()

with tab_un:
    st.markdown("### Asker Kiralama")
    for uk, v in game.units.items():
        name, count, lvl, m_lvl, _, c_buy, c_lvl, c_mult, ico, desc_u = v
        total_buy_cost = game.get_multi_cost(c_buy, 1.35, game.buy_multiplier)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"{ico} **{name}** (Adet: {game.format_number(count)} | Lvl: {lvl})")
            st.caption(f"DPS: +{game.format_number(game.get_unit_dps(uk))}/sn | {desc_u}")
        with c2:
            if st.button(f"Kirala (x{game.buy_multiplier})\n💰 {game.format_number(total_buy_cost)}", key=f"un_{uk}", disabled=(game.altin < total_buy_cost)):
                cnt = game.buy_multiplier
                base_cost = game.units[uk][5]
                total_cost_val = game.get_multi_cost(base_cost, 1.35, cnt)
                if game.altin >= total_cost_val:
                    game.altin -= total_cost_val
                    game.units[uk][1] += cnt
                    game.units[uk][5] = int(base_cost * (1.35 ** cnt))
                    game.check_special_quests()
                st.rerun()

with tab_stg:
    st.markdown("### Zindan Seçimi")
    st.write(f"Ulaşılan En Yüksek Zindan: **{game.max_ulaşilan_asama}**")
    for stg_num in range(1, game.max_ulaşilan_asama + 1):
        dname = game.get_dungeon_name(stg_num)
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            st.write(f"🏰 Zindan {stg_num}: {dname}")
        with col_s2:
            if game.asama != stg_num:
                if st.button("Git", key=f"stg_{stg_num}"):
                    game.select_stage(stg_num)
                    st.rerun()
            else:
                st.info("Aktif")
