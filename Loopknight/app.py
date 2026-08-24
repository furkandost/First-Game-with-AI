import streamlit as st
import time
import os
import sys

# Tkinter bağımlılığını web ortamında patlamaması için mock'luyoruz (oyun motoru Tkinter çağırsa bile hata vermez)
import unittest.mock as mock
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.ttk'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()

# Orijinal oyun dosyanı içeri aktarıyoruz
from idlegame import LoopKnight

# Sayfa Yapılandırması
st.set_page_config(
    page_title="LoopKnight - Online",
    page_icon="⚔️",
    layout="centered"
)

# Streamlit Session State içinde oyun nesnesini saklıyoruz (Sayfa yenilendiğinde oyun sıfırlanmasın diye)
class StreamlitRootMock:
    def __init__(self):
        self.title_text = ""
        self.geometry_val = ""
        self.bg_color = ""
    def title(self, t): self.title_text = t
    def geometry(self, g): self.geometry_val = g
    def configure(self, **kwargs): pass
    def after(self, ms, callback, *args):
        # Streamlit döngüsünde 'after' timer'larını manuel tetikleyeceğiz
        pass
    def mainloop(self): pass

if 'game_instance' not in st.session_state:
    root_mock = StreamlitRootMock()
    st.session_state.game = LoopKnight(root_mock)
    # Otomatik döngüleri simüle etmek için zaman kaydedici
    st.session_state.last_tick = time.time()

game = st.session_state.game

# Arka plan otomatik saldırı ve zehir döngülerini her sayfa etkileşiminde güncelleyelim
now = time.time()
if now - st.session_state.last_tick >= 1.0:
    # Saniyelik döngüler (Zehir, Ateş, Otomatik Asker vuruşları)
    if game.current_monster_hp > 0:
        dps = game.get_auto_dps()
        if dps > 0:
            arm = int(game.current_monster_defense * (1.0 - game.stats["zirh_delme"][0]))
            game.current_monster_hp -= max(1, int(dps - arm))
            if game.current_monster_hp <= 0:
                game.monster_defeated()
    st.session_state.last_tick = now

# --- ARAYÜZ (UI) ---
st.title("🛡️ LoopKnight - Tarayıcı Sürümü")

# Üst Bilgiler (Altın, Bones, DPS)
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Altın", game.format_number(game.altin))
    st.metric("🛡️ Asker Hasarı", f"+{game.format_number(game.get_auto_dps())}/sn")
with col2:
    st.metric("🦴 Zones Bones", game.format_number(game.zones_bones))
    st.metric("🏰 Bölge", f"Zindan {game.asama} — Oda {game.kademe}/10")

st.divider()

# Düşman Kartı
st.subheader(f"👾 {game.get_monster_name(game.asama, game.kademe, game.is_boss)}")
hp_percent = max(0.0, min(1.0, game.current_monster_hp / game.current_monster_max_hp if game.current_monster_max_hp > 0 else 0))
st.progress(hp_percent, text=f"HP: {game.format_number(max(0, game.current_monster_hp))} / {game.format_number(game.current_monster_max_hp)}")

# Saldırı Butonu
if st.button(f"⚔️ SALDIR! (Tıklama Hasarı: {game.format_number(game.get_click_damage())})", use_container_width=True, type="primary"):
    game.attack()
    st.rerun()

st.divider()

# Sekmeler (Tablar) halinde oyun menüleri
tab_up, tab_sw, tab_un, tab_stg = st.tabs(["🗡️ Geliştirmeler", "⚔️ Kılıçlar", "🛡️ Askerler", "🏰 Zindanlar"])

with tab_up:
    st.markdown("### Temel Özellikler")
    for key, title, desc in [("hasar", "Temel Hasar", "Tıklama gücünü artırır."), 
                             ("sans", "Kritik Şansı", "Kritik oranı."), 
                             ("kritik_hasar", "Kritik Hasar", "Kritik ekstra çarpanı."), 
                             ("zirh_delme", "Zırh Delme", "Zırh yok sayma."), 
                             ("zehir", "Zehir Bulutu", "Saniyede zehir vurur.")]:
        val, cost, mult, limit = game.stats[key]
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"**{title}** (Mevcut: {val})")
            st.caption(desc)
        with c2:
            if st.button(f"Yükselt\n💰 {game.format_number(cost)}", key=f"stat_{key}"):
                if game.altin >= cost:
                    game.altin -= cost
                    if key == "hasar": game.stats[key][0] += 3
                    elif key in ["sans", "zirh_delme"]: game.stats[key][0] = min(limit, round(val + 0.05, 2))
                    elif key == "kritik_hasar": game.stats[key][0] = min(limit, round(val + 1.0, 1))
                    elif key == "zehir": game.stats[key][0] = min(limit, val + 1)
                    game.stats[key][1] = int(cost * mult)
                    st.rer()

with tab_sw:
    st.markdown("### Kılıç Mağazası")
    for sk, v in game.swords.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"{v[4]} **{v[0]}** (+{v[1]}x Hasar)")
            st.caption(v[5])
        with c2:
            if v[3]:
                st.success("Sahip Olundu")
            else:
                if st.button(f"Al: {game.format_number(v[2])}", key=f"sw_{sk}"):
                    if game.altin >= v[2]:
                        game.altin -= v[2]
                        game.swords[sk][3] = True
                        st.rerun()

with tab_un:
    st.markdown("### Asker Kiralama")
    for uk, v in game.units.items():
        name, count, lvl, m_lvl, _, c_buy, c_lvl, c_mult, ico, _ = v
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"{ico} **{name}** (Adet: {count} | Lvl: {lvl})")
            st.caption(f"DPS: +{game.format_number(game.get_unit_dps(uk))}/sn")
        with c2:
            if st.button(f"Kirala\n💰 {game.format_number(c_buy)}", key=f"un_{uk}"):
                if game.altin >= c_buy:
                    game.altin -= c_buy
                    game.units[uk][1] += 1
                    game.units[uk][5] = int(c_buy * 1.35)
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
                    game.asama = stg_num
                    game.kademe = 1
                    game.spawn_monster()
                    st.rerun()
            else:
                st.info("Aktif")

# Otomatik sayfa yenileme (Saniye başı oyun akışı ve canavar hareketleri için)
time.sleep(1)
st.rerun()