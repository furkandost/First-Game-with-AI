import tkinter as tk
from tkinter import ttk, messagebox
import random, json, os, time

class LoopKnight:
    def __init__(self, root):
        self.root = root
        self.root.title("LoopKnight - Lag-Free Story Edition")
        self.root.geometry("900x1080")
        self.root.configure(bg="#121212")

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TNotebook", background="#121212", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#1E1E1E", foreground="#B0BEC5", padding=[6, 4], font=("Arial", 7, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", "#8E0000")], foreground=[("selected", "#FFFFFF")])
        self.style.configure("red.Horizontal.TProgressbar", foreground='#FF1744', background='#FF1744', troughcolor='#263238', borderwidth=0)

        self.altin = self.zones_bones = 0
        self.asama = self.kademe = self.max_ulaşilan_asama = self.max_ulaşilan_kademe = 1
        self.farm_modu = tk.BooleanVar(value=False)
        self.buy_multiplier = 1
        self.total_clicks = self.total_kills = self.total_crits = self.total_gold_earned = self.total_boss_kills = 0
        self.stage_completions = {}

        self.poison_active_until = self.poison_last_tick = self.poison_tick_damage = 0
        self.poison_loop_running = False
        self.pyro_active_until = self.pyro_last_tick = 0
        self.pyro_cost, self.pyro_loop_running = 10000000, False
        self.fuzuli_active_until, self.fuzuli_kills_counter = 0, 300
        self.darkness_active_until = self.darkness_cd_until = 0

        self.dungeon_themes = ["Karanlık Orman", "Derin Orman", "Gölge Mağarası", "Lurker İni", "Volkanik Geçit", "Sessiz Mahzen", "Mistik Tapınak", "Koyu Zindan", "Obsidyen Zirve", "Kozmik Boyut", "Astra Krallığı", "Kızıl Çöl", "Buzul İni", "Ruhlar Vadisi", "Sonsuzluk Boşluğu", "Uçurum Tapınağı", "Gök Gürültüsü Zirvesi", "Vahşet Ormanı"]
        
        self.story_fragments = {
            1: "İlk aşama: Karanlık Orman. Ağaçların arasından sızan soluk ay ışığı, buranın yıllardır yolunu kaybetmiş ruhların mezarı olduğunu fısıldıyor. Yerdeki kırık zırh parçaları, senden önce buraya gelenlerin sonunu simgeliyor. Tehlike çok yakın...",
            2: "Ağaçlar sıklaşıyor, gökyüzü tamamen kayboluyor. Derin Orman'ın sakinleri yabancıları sevmez. Daha karanlık yollara doğru ilerliyorsun.",
            3: "Gölge Mağarası'na adım attığında duvarlardaki eski yazılar gözüne çarpıyor: 'Döngüden kaçış yok, sadece savaş var.'",
            4: "Lurker İni'nin kokusu mideni bulandırıyor. Karanlıkta parlayan yüzlerce aç göz üzerine dikildi.",
            5: "Volkanik Geçit'in sıcaklığı demir zırhını eritmek üzere. Ateşin içinden gelen yaratıklar kükrüyor.",
            6: "Sessiz Mahzen'de ölüm sessizliği hakim. Burada zaman yavaş akıyor gibi hissediliyor.",
            7: "Mistik Tapınak'ın kalıntılarında unutulmuş tanrıların enerjisi hala yankılanıyor.",
            8: "Koyu Zindan'ın derinliklerine indikçe zihnin bululanıyor. Gerçek ile rüya birbirine karıştı.",
            9: "Obsidyen Zirve'ye tırmandın; rüzgar bıçak gibi kesiyor. Zirvenin efendisi seni bekliyor.",
            10: "Kozmik Boyut'un kapısındasın. Fiziksel kuralların geçerli olmadığı bu yerde evrenin sınırlarını zorluyorsun."
        }

        self.m_prefixes = ["Zehirli", "Kadim", "Lanetli", "Obsidyen", "Astra", "Kaos", "Kanlı", "Gölge", "Bozuk", "Kör", "Alevli", "Buzul", "Mistik", "Ruhani", "Karanlık", "Vahşi", "Zirfiri", "Dev", "Yıkıcı", "Ölümcül", "Kozmik", "Volkanik", "Koyu", "Cehennem", "Zümrüt", "Mermer", "Kristal", "Kızgın", "Sessiz", "Büyülü"]
        self.m_species = ["Kertenkele", "Engerek", "Golem", "İblis", "Drake", "Chimera", "Leviathan", "Akrep", "Troglodit", "Sarmaşık", "Örümcek", "Çakal", "Sırtlan", "Kurt", "Gargoyle", "Manticore", "Minotor", "Yarasa", "Tayf", "Troll", "İskelet", "Zombi", "Ejderha", "Wurm", "Hydra", "Banshee", "Harpy", "Kraken", "Basilisk", "Wyvern"]
        self.m_suffixes = ["Muhafızı", "Sürüneni", "Katili", "Tiranı", "Avcısı", "Kraliçesi", "Ruhu", "Efendisi", "Yutanı", "Kıranı", "Hükümdarı", "Gözcüsü", "Savaşçısı", "Efsanesi", "Çığırtkanı", "Hakimi", "Lideri", "Kozmik Beyi", "Koruyucusu", "Sömüreni", "Celladı", "Mimarı", "Bükücüsü", "Süvarisi", "Öncüsü"]

        self.perm_upgrades = {
            "mistik_sovalye": [False, "🔮 Mistik Şövalye", "Zehir bulutunun hasarını 10 katına çıkarır.", 15000000, 15000, 5],
            "karanliga_kulak_veren": [False, "👤 Karanlığa Kulak Veren", "Gölge askerler gelir, asker hasarı 10 kat artar.", 75000000, 35000, 1],
            "eflatun": [False, "💜 Eflatun", "Tüm hasarı 5x, altını 3x yapar, başlanıç tık hasarını 1000 sabitler.", 50000000, 25000, 1]
        }

        self.stats_defaults = {"hasar": [5, 15, 1.35, None], "sans": [0.05, 75, 1.45, 0.85], "kritik_hasar": [1.5, 150, 1.55, 300.0], "zirh_delme": [0.00, 350, 2.1, 1.00], "zehir": [0, 1500, 3.2, 10]}
        self.stats = {k: v[:] for k, v in self.stats_defaults.items()}

        self.swords = {
            "bakir": ["Bakır Kılıç", 5.0, 150000, False, "🗡️", "Temel bronz."],
            "elmas": ["Elmas Kılıç", 7.0, 3000000, False, "💎", "Keskin elmas."],
            "uranyum": ["Uranyum Kılıç", 10.0, 60000000, False, "☢️", "Radyoaktif."],
            "banelyum": ["Banelyum Kılıç", 15.0, 1200000000, False, "🔮", "Mistik karanlık."],
            "kozmik": ["Kozmik Kılıç", 30.0, 25000000000, False, "🌌", "Evrenin gücü."],
            "titanyum": ["Titanyum Kılıç", 50.0, 500000000000, False, "🛡️", "Sağlam titanyum."],
            "cehennem": ["Cehennem Kılıcı", 90.0, 10000000000000, False, "🔥", "Alev seli."],
            "yildiz": ["Yıldız Kılıcı", 150.0, 220000000000000, False, "🌟", "Yıldız tozu."],
            "ebedi": ["Ebedi Kılıç", 300.0, 4500000000000000, False, "⏳", "Zamanı büken."],
            "tanrisal": ["Tanrısal Kılıç", 700.0, 90000000000000000, False, "⚡", "Yaradan gücü."]
        }
        
        self.units_defaults = {
            "okcu": ["Okçu", 0, 1, 0, 5, 20, 40, 750, "🏹", "Hızlı atış."],
            "savasci": ["Savaşçı", 0, 1, 0, 30, 160, 280, 4500, "⚔️", "Dengeli."],
            "buyucu": ["Büyücü", 0, 1, 0, 200, 1400, 2200, 30000, "🧙‍♂️", "Büyü hasarı."],
            "suikastci": ["Suikastçı", 0, 1, 0, 1200, 11000, 18000, 220000, "🗡️", "Zırh deler."],
            "ejderha": ["Ejderha", 0, 1, 0, 8000, 70000, 110000, 1500000, "🐉", "Alev gücü."],
            "fenix": ["Anka Kuşu", 0, 1, 0, 45000, 420000, 650000, 12000000, "🔥", "Küllerinden."],
            "kraken": ["Karanlık Kraken", 0, 1, 0, 250000, 2500500, 3800000, 90000000, "🐙", "Okyanus dehşeti."],
            "valkyrie": ["Valkyrie", 0, 1, 0, 1500000, 15000000, 22000000, 750000000, "🦅", "Göksel savaşçı."],
            "behemoth": ["Behemoth", 0, 1, 0, 10000000, 90000000, 130000000, 6000000000, "🦣", "Durdurulamaz dev."],
            "kronos": ["Kronos", 0, 1, 0, 75000000, 600000000, 900000000, 45000000000, "⏳", "Zaman efendisi."]
        }
        self.units = {k: v[:] for k, v in self.units_defaults.items()}

        self.rb_defaults = {
            "hasar": [1.0, 8, "⚔️ Hasar Çarpanı (+1.0x)", "Tıklama ve asker hasarını katlar.", 1.35],
            "sans": [1.0, 15, "🎯 Kritik Şans Çarpanı (+0.2x)", "Kritik şansı katlar.", 1.35],
            "kritik_hasar": [1.0, 25, "💥 Kritik Hasar Çarpanı (+1.0x)", "Kritik çarpanı yükseltir.", 1.35],
            "bones": [1.0, 30, "🦴 Zones Bones Çarpanı (+x5.0)", "Bones kazancını artırır.", 1.35],
            "skill_power": [1.0, 150000, "🌀 Yetenek Gücü (+2.0x)", "Yetenek çarpanlarını katlar.", 1.35],
            "skill_cd": [0.0, 150, "⏱️ Bekleme İndirimi (+%10)", "Yetenek CD indirir.", 1.35],
            "gold_mult": [1.0, 75, "💰 Altın Çarpanı (+1.0x)", "Altın miktarını artırır.", 1.35],
            "unit_speed": [0, 150, "⚡ Asker Hızı Seviyesi", "Vuruş aralığını düşürür.", 1.35]
        }
        self.rb = {k: v[:] for k, v in self.rb_defaults.items()}
        self.skills = {
            "temiz_zihin": ["Temiz Zihin", False, 0, 0, 15, 60, "👁️", "#1A237E", "Tıklama ve asker hasarını artırır."],
            "ellion": ["Ellion Kutsaması", False, 0, 0, 30, 180, "✨", "#880E4F", "Saldırı hızını artırır."],
            "eflatun_muhru": ["Eflatun Mührü", False, 0, 0, 60, 300, "💜", "#4A148C", "Saldırı hızı ve hasarı devasa artırır."]
        }

        self.special_quests = {}
        base_quests = [
            ("c_100", "👆 Tık Acemisi", "100 Tık yap.", lambda: self.total_clicks >= 100, lambda: f"{self.total_clicks} / 100"),
            ("c_500", "👆 Tık Çırağı", "500 Tık yap.", lambda: self.total_clicks >= 500, lambda: f"{self.total_clicks} / 500"),
            ("c_1000", "👆 Tık Ustası", "1,000 Tık yap.", lambda: self.total_clicks >= 1000, lambda: f"{self.total_clicks} / 1,000"),
            ("c_5000", "👆 Tık Canavarı", "5,000 Tık yap.", lambda: self.total_clicks >= 5000, lambda: f"{self.total_clicks} / 5,000"),
            ("c_10000", "👆 Tık Efsanesi", "10,000 Tık yap.", lambda: self.total_clicks >= 10000, lambda: f"{self.total_clicks} / 10,000"),
            ("k_50", "👾 Yaratık Avcısı I", "50 Canavar kes.", lambda: self.total_kills >= 50, lambda: f"{self.total_kills} / 50"),
            ("k_250", "👾 Yaratık Avcısı II", "250 Canavar kes.", lambda: self.total_kills >= 250, lambda: f"{self.total_kills} / 250"),
            ("k_1000", "👾 Yaratık Avcısı III", "1,000 Canavar kes.", lambda: self.total_kills >= 1000, lambda: f"{self.total_kills} / 1,000"),
            ("k_5000", "👾 Yaratık Avcısı IV", "5,000 Canavar kes.", lambda: self.total_kills >= 5000, lambda: f"{self.total_kills} / 5,000"),
            ("k_10000", "👾 Yaratık Avcısı V", "10,000 Canavar kes.", lambda: self.total_kills >= 10000, lambda: f"{self.total_kills} / 10,000"),
            ("b_1", "👑 Boss Katili I", "1 Boss kes.", lambda: self.total_boss_kills >= 1, lambda: f"{self.total_boss_kills} / 1"),
            ("b_5", "👑 Boss Katili II", "5 Boss kes.", lambda: self.total_boss_kills >= 5, lambda: f"{self.total_boss_kills} / 5"),
            ("b_15", "👑 Boss Katili III", "15 Boss kes.", lambda: self.total_boss_kills >= 15, lambda: f"{self.total_boss_kills} / 15"),
            ("b_50", "👑 Boss Katili IV", "50 Boss kes.", lambda: self.total_boss_kills >= 50, lambda: f"{self.total_boss_kills} / 50"),
            ("cr_10", "💥 Şanslı Vuruş", "10 Kritik yap.", lambda: self.total_crits >= 10, lambda: f"{self.total_crits} / 10"),
            ("cr_100", "💥 Ölümcül Vuruş", "100 Kritik yap.", lambda: self.total_crits >= 100, lambda: f"{self.total_crits} / 100"),
            ("cr_500", "💥 Yıkıcı Kritik", "500 Kritik yap.", lambda: self.total_crits >= 500, lambda: f"{self.total_crits} / 500"),
            ("cr_2000", "💥 Kritik Üstadı", "2,000 Kritik yap.", lambda: self.total_crits >= 2000, lambda: f"{self.total_crits} / 2,000"),
            ("g_10k", "💰 İlk Servet", "10k Altın kazan.", lambda: self.total_gold_earned >= 10000, lambda: f"{self.format_number(self.total_gold_earned)} / 10K"),
            ("g_500k", "💰 Zenginlik", "500k Altın kazan.", lambda: self.total_gold_earned >= 500000, lambda: f"{self.format_number(self.total_gold_earned)} / 500K"),
            ("g_10m", "💰 Milyoner", "10M Altın kazan.", lambda: self.total_gold_earned >= 10000000, lambda: f"{self.format_number(self.total_gold_earned)} / 10M"),
            ("g_1b", "💰 Milyarder", "1B Altın kazan.", lambda: self.total_gold_earned >= 1000000000, lambda: f"{self.format_number(self.total_gold_earned)} / 1B"),
            ("rb_1", "🔄 Yeniden Doğuş", "İlk Rebirth yap.", lambda: self.zones_bones > 0, lambda: f"{self.zones_bones} / 1"),
            ("zb_50", "🦴 Kemik Toplayıcı", "50 Bones kazan.", lambda: self.zones_bones >= 50, lambda: f"{self.zones_bones} / 50"),
            ("zb_500", "🦴 Kemik Avcısı", "500 Bones kazan.", lambda: self.zones_bones >= 500, lambda: f"{self.zones_bones} / 500"),
            ("zb_2500", "🦴 Koleksiyoncu", "2,500 Bones kazan.", lambda: self.zones_bones >= 2500, lambda: f"{self.zones_bones} / 2,500"),
            ("sw_1", "🗡️ Kılıç Kuşan", "1 Kılıç al.", lambda: any(v[3] for v in self.swords.values()), lambda: f"{sum(1 for v in self.swords.values() if v[3])} / 1"),
            ("sw_3", "⚔️ Koleksiyoner", "3 Kılıç al.", lambda: sum(1 for v in self.swords.values() if v[3]) >= 3, lambda: f"{sum(1 for v in self.swords.values() if v[3])} / 3"),
            ("sw_5", "🌌 Kozmik Efendi", "Tüm Kılıçları al.", lambda: all(v[3] for v in self.swords.values()), lambda: f"{sum(1 for v in self.swords.values() if v[3])} / 10"),
            ("u_10", "🏹 Küçük Birlik", "10 Asker kirala.", lambda: sum(v[1] for v in self.units.values()) >= 10, lambda: f"{sum(v[1] for v in self.units.values())} / 10"),
            ("u_50", "🏹 Asker Ordusu", "50 Asker kirala.", lambda: sum(v[1] for v in self.units.values()) >= 50, lambda: f"{sum(v[1] for v in self.units.values())} / 50"),
            ("u_200", "🏹 Dev Ordu", "200 Asker kirala.", lambda: sum(v[1] for v in self.units.values()) >= 200, lambda: f"{sum(v[1] for v in self.units.values())} / 200"),
            ("u_dragon", "🐉 Ejderha Terbiyecisi", "1 Ejderha kirala.", lambda: self.units["ejderha"][1] >= 1, lambda: f"{self.units['ejderha'][1]} / 1"),
            ("p_1", "🧪 Zehir Teması", "Zehir aç.", lambda: self.stats["zehir"][0] >= 1, lambda: f"{self.stats['zehir'][0]} / 1"),
            ("p_5", "🧪 Simyacı", "Zehir Lvl 5 yap.", lambda: self.stats["zehir"][0] >= 5, lambda: f"{self.stats['zehir'][0]} / 5"),
            ("p_10", "🧪 Usta Zehirci", "Zehir Lvl 10 yap.", lambda: self.stats["zehir"][0] >= 10, lambda: f"{self.stats['zehir'][0]} / 10"),
            ("st_2", "🏔️ Yükseliş I", "2. Zindana ulaş.", lambda: self.max_ulaşilan_asama >= 2, lambda: f"{self.max_ulaşilan_asama} / 2"),
            ("st_3", "🏔️ Yükseliş II", "3. Zindana ulaş.", lambda: self.max_ulaşilan_asama >= 3, lambda: f"{self.max_ulaşilan_asama} / 3"),
            ("st_5", "🏔️ Yükseliş III", "5. Zindana ulaş.", lambda: self.max_ulaşilan_asama >= 5, lambda: f"{self.max_ulaşilan_asama} / 5"),
            ("st_7", "🏔️ Yükseliş IV", "7. Zindana ulaş.", lambda: self.max_ulaşilan_asama >= 7, lambda: f"{self.max_ulaşilan_asama} / 7")
        ]
        for qk, title, desc, cond, prog_func in base_quests:
            self.special_quests[qk] = [title, desc, False, False, cond, False, prog_func]

        for i in range(1, 31):
            qk = f"extra_{i}"
            clicks_req = i * 2500
            self.special_quests[qk] = [f"🏆 Azim Görevi {i}", f"{clicks_req:,} toplam tık yap.", False, False, lambda cr=clicks_req: self.total_clicks >= cr, False, lambda cr=clicks_req: f"{self.total_clicks} / {cr:,}"]

        for stg_i in range(1, 19):
            qk = f"stg_quest_{stg_i}"
            theme_name = self.dungeon_themes[(stg_i - 1) % len(self.dungeon_themes)]
            self.special_quests[qk] = [f"🏰 {theme_name} Fatihi", f"{theme_name} zindanını 3,500 defa tamamla.", False, False, lambda s=stg_i: self.stage_completions.get(str(s), 0) >= 3500, True, lambda s=stg_i: f"{self.stage_completions.get(str(s), 0)} / 3,500"]

        self.current_monster_max_hp = self.current_monster_hp = self.current_monster_defense = 0
        self.is_boss = False
        self.last_click_time = 0

        self.setup_ui()
        self.load_game(silent=True)
        self.spawn_monster()
        self.ui_guncelle()
        self.auto_attack_loop()
        self.auto_save_loop()

    def format_number(self, n):
        if n < 1000:
            return str(n)
        suffixes = ["", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc"]
        i = 0
        while n >= 1000 and i < len(suffixes) - 1:
            n /= 1000.0
            i += 1
        return f"{n:.1f}{suffixes[i]}" if i > 0 else str(int(n))

    def get_dungeon_name(self, stg):
        t_idx = (stg - 1) % len(self.dungeon_themes)
        tier = (stg - 1) // len(self.dungeon_themes)
        return f"{self.dungeon_themes[t_idx]} " + (f"IV" if tier == 3 else ("III" if tier == 2 else ("II" if tier == 1 else (f"v{tier+1}" if tier > 3 else "")))).strip()

    def get_monster_name(self, stg, kdm, is_boss):
        seed = stg * 100 + kdm
        rnd = random.Random(seed)
        p = rnd.choice(self.m_prefixes)
        s = rnd.choice(self.m_species)
        if is_boss:
            suf = rnd.choice(self.m_suffixes)
            return f"👑 {p} {s} {suf}"
        return f"👾 {p} {s}"

    def set_buy_multiplier(self, mult):
        self.buy_multiplier = mult
        for m, btn in self.mult_btns.items(): btn.config(bg="#8E0000" if m == mult else "#263238", fg="#FFF" if m == mult else "#B0BEC5")
        self.ui_guncelle()

    def get_multi_cost(self, base_cost, rate, count):
        t, c = 0, base_cost
        for _ in range(count): t += c; c = int(c * rate)
        return t

    def get_stat_buy_count(self, k):
        val, _, _, limit = self.stats[k]
        if limit is None: return self.buy_multiplier
        if k in ["sans", "zirh_delme"]: max_possible = int(round((limit - val) / 0.05))
        elif k == "kritik_hasar": max_possible = int(round((limit - val) / 1.0))
        elif k == "zehir": max_possible = int(limit - val)
        return max(0, min(self.buy_multiplier, max_possible))

    def create_card_frame(self, parent, pady=3):
        card = tk.Frame(parent, bg="#1E1E1E", bd=1, relief="solid"); card.pack(fill="x", pady=pady, padx=5)
        info = tk.Frame(card, bg="#1E1E1E"); info.pack(side="left", fill="both", expand=True, padx=8, pady=4)
        return card, info

    def open_story_window(self):
        story_win = tk.Toplevel(self.root)
        story_win.title(f"Hikaye Günlüğü - {self.get_dungeon_name(self.asama)}")
        story_win.geometry("550x400")
        story_win.configure(bg="#121212")

        tk.Label(story_win, text=f"📖 {self.get_dungeon_name(self.asama)} — Hikaye Arşivi", font=("Arial", 12, "bold"), fg="#FFD700", bg="#121212").pack(pady=10)

        f_content = tk.Frame(story_win, bg="#1E1E1E", bd=1, relief="solid")
        f_content.pack(fill="both", expand=True, padx=15, pady=10)

        story_text = self.story_fragments.get(self.asama, "Bu bölge henüz keşfedilmemiş karanlık sırlarla dolu...")
        
        lbl_story_detail = tk.Label(f_content, text=story_text, font=("Arial", 10), fg="#E0E0E0", bg="#1E1E1E", wraplength=500, justify="left")
        lbl_story_detail.pack(padx=15, pady=15)

        tk.Button(story_win, text="KAPAT", command=story_win.destroy, bg="#B71C1C", fg="#FFF", font=("Arial", 9, "bold"), width=15, relief="flat").pack(pady=10)

    def show_stage_complete_story_popup(self, completed_stage):
        pop = tk.Toplevel(self.root)
        pop.title("Zindan Tamamlandı / Yeni Aşama!")
        pop.geometry("500x350")
        pop.configure(bg="#121212")

        dname = self.get_dungeon_name(completed_stage)
        tk.Label(pop, text=f"🏰 {dname} Geçildi!", font=("Arial", 13, "bold"), fg="#00E676", bg="#121212").pack(pady=15)

        f_txt = tk.Frame(pop, bg="#1E1E1E", bd=1, relief="solid")
        f_txt.pack(fill="both", expand=True, padx=15, pady=5)

        next_story = self.story_fragments.get(self.asama, "Daha karanlık yollara doğru ilerliyorsun. Tehlike katlanarak artıyor...")
        full_msg = f"Tebrikler! {dname} bölgesindeki tüm tehlikeleri alt ettin.\n\nYeni Bölüm Atmosferi:\n\"{next_story}\""

        tk.Label(f_txt, text=full_msg, font=("Arial", 9, "italic"), fg="#CFD8DC", bg="#1E1E1E", wraplength=450, justify="left").pack(padx=15, pady=15)

        tk.Button(pop, text="MACERAYA DEVAM ET", command=pop.destroy, bg="#2E7D32", fg="#FFF", font=("Arial", 10, "bold"), relief="flat", cursor="hand2").pack(pady=15)

    def setup_ui(self):
        f_h = tk.Frame(self.root, bg="#1E1E1E", bd=1, relief="ridge"); f_h.pack(fill="x", padx=12, pady=6)
        self.label_resources = tk.Label(f_h, text="", font=("Arial", 12, "bold"), fg="#FFD700", bg="#1E1E1E"); self.label_resources.pack(pady=4)
        self.label_dps = tk.Label(f_h, text="", font=("Arial", 9, "bold"), fg="#00E676", bg="#1E1E1E"); self.label_dps.pack(pady=2)

        f_n = tk.Frame(self.root, bg="#121212"); f_n.pack(pady=2)
        bs = {"bg": "#263238", "fg": "#ECEFF1", "activebackground": "#37474F", "activeforeground": "#FFF", "relief": "flat", "font": ("Arial", 8, "bold")}
        self.btn_prev_stage = tk.Button(f_n, text="◀ Zindan", command=self.prev_stage, **bs); self.btn_prev_stage.pack(side="left", padx=2)
        self.btn_prev_kdm = tk.Button(f_n, text="◀ Oda", command=self.prev_kademe, **bs); self.btn_prev_kdm.pack(side="left", padx=2)
        self.label_asama = tk.Label(f_n, text="", font=("Arial", 13, "bold"), fg="#FF5252", bg="#121212"); self.label_asama.pack(side="left", padx=10)
        self.btn_next_kdm = tk.Button(f_n, text="Oda ▶", command=self.next_kademe, **bs); self.btn_next_kdm.pack(side="left", padx=2)
        self.btn_next_stage = tk.Button(f_n, text="Zindan ▶", command=self.next_stage, **bs); self.btn_next_stage.pack(side="left", padx=2)

        f_top_actions = tk.Frame(self.root, bg="#121212")
        f_top_actions.pack(pady=2)
        tk.Checkbutton(f_top_actions, text="🌾 Farm Modu", variable=self.farm_modu, font=("Arial", 9, "bold"), fg="#81C784", bg="#121212", selectcolor="#1E1E1E", activebackground="#121212", command=self.ui_guncelle).pack(side="left", padx=10)
        tk.Button(f_top_actions, text="📖 Hikaye Günlüğü", command=self.open_story_window, bg="#37474F", fg="#FFD700", font=("Arial", 8, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=10)

        f_m = tk.LabelFrame(self.root, text=" 👾 DÜŞMAN ", font=("Arial", 10, "bold"), fg="#B0BEC5", bg="#1E1E1E", padx=10, pady=5, bd=1, relief="solid"); f_m.pack(fill="x", padx=15, pady=4)
        self.label_m_name = tk.Label(f_m, text="", font=("Arial", 12, "bold"), fg="#FF1744", bg="#1E1E1E"); self.label_m_name.pack()
        self.label_m_stats = tk.Label(f_m, text="", font=("Arial", 9), fg="#CFD8DC", bg="#1E1E1E"); self.label_m_stats.pack(pady=2)
        self.hp_bar = ttk.Progressbar(f_m, orient="horizontal", length=440, mode="determinate", style="red.Horizontal.TProgressbar"); self.hp_bar.pack(pady=4)
        self.label_poison_status = tk.Label(f_m, text="", font=("Arial", 9, "bold"), fg="#69F0AE", bg="#1E1E1E"); self.label_poison_status.pack()

        self.btn_attack = tk.Button(self.root, text="", command=self.attack, bg="#B71C1C", fg="#FFFFFF", font=("Arial", 14, "bold"), height=2, relief="flat", cursor="hand2"); self.btn_attack.pack(fill="x", padx=20, pady=4)
        self.label_battle_log = tk.Label(self.root, text="", font=("Arial", 9, "bold"), fg="#FFAB40", bg="#121212"); self.label_battle_log.pack(pady=1)

        f_mbuy = tk.Frame(self.root, bg="#121212"); f_mbuy.pack(fill="x", padx=15, pady=(2, 0))
        tk.Label(f_mbuy, text="Satın Alma Modu:", font=("Arial", 9, "bold"), fg="#B0BEC5", bg="#121212").pack(side="left", padx=5)
        self.mult_btns = {m: tk.Button(f_mbuy, text=f"x{m}", command=lambda mult=m: self.set_buy_multiplier(mult), font=("Arial", 9, "bold"), width=5, bg="#8E0000" if m == 1 else "#263238", fg="#FFF", relief="flat", cursor="hand2") for m in [1, 10, 100]}
        for b in self.mult_btns.values(): b.pack(side="left", padx=2)

        self.notebook = ttk.Notebook(self.root); self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self.tabs = {name: tk.Frame(self.notebook, bg="#121212") for name in ["upgrades", "swords", "mercenaries", "skills", "stages", "quests", "perm", "rebirth"]}
        for name, title in [("upgrades", "🗡️ Silah"), ("swords", "⚔️ Kılıçlar"), ("mercenaries", "🛡️ Askerler"), ("skills", "🌀 Yetenekler"), ("stages", "🏰 Bölümler"), ("quests", "📜 Görevler"), ("perm", "🏛️ Kalıcı"), ("rebirth", "🔄 Rebirth")]:
            self.notebook.add(self.tabs[name], text=title)

        self.stat_cards = {}
        for key, title, desc in [("hasar", "🗡️ Temel Hasar", "Tıklama gücünü artırır."), ("sans", "🎯 Kritik Şansı", "Kritik oranı (Maks %85)."), ("kritik_hasar", "💥 Kritik Hasar", "Kritik ekstra çarpanı."), ("zirh_delme", "🛡️ Zırh Delme", "Zırh yok sayma (Maks %100)."), ("zehir", "🧪 Zehir Bulutu", "Saniyede zehir vurur.")]:
            card, info = self.create_card_frame(self.tabs["upgrades"])
            tk.Label(info, text=title, font=("Arial", 10, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x")
            lbl_val = tk.Label(info, text="", font=("Arial", 9, "bold"), fg="#FFD700", bg="#1E1E1E", anchor="w"); lbl_val.pack(fill="x")
            tk.Label(info, text=desc, font=("Arial", 8), fg="#78909C", bg="#1E1E1E", anchor="w").pack(fill="x")
            btn_buy = tk.Button(card, command=lambda k=key: self.buy_stat(k), font=("Arial", 9, "bold"), width=16, relief="flat", cursor="hand2"); btn_buy.pack(side="right", padx=8, pady=6)
            self.stat_cards[key] = (lbl_val, btn_buy)

        # ⚔️ KILIÇLAR SEKMESİ (5 Sütun)
        canvas_sw = tk.Canvas(self.tabs["swords"], bg="#121212", highlightthickness=0)
        scroll_sw = ttk.Scrollbar(self.tabs["swords"], orient="vertical", command=canvas_sw.yview)
        self.scroll_sw_frame = tk.Frame(canvas_sw, bg="#121212")
        self.scroll_sw_frame.bind("<Configure>", lambda e: canvas_sw.configure(scrollregion=canvas_sw.bbox("all")))
        canvas_sw.create_window((0, 0), window=self.scroll_sw_frame, anchor="nw")
        canvas_sw.configure(yscrollcommand=scroll_sw.set)
        canvas_sw.pack(side="left", fill="both", expand=True, padx=(5, 0)); scroll_sw.pack(side="right", fill="y")
        
        self.sword_cards = {}
        row, col = 0, 0
        for k, v in self.swords.items():
            card = tk.Frame(self.scroll_sw_frame, bg="#1E1E1E", bd=1, relief="solid", width=165, height=130)
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            card.pack_propagate(False)
            
            tk.Label(card, text=f"{v[4]} {v[0]}", font=("Arial", 8, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4, pady=(4, 2))
            tk.Label(card, text=f"+{v[1]}x Hasar", font=("Arial", 7, "bold"), fg="#FFD700", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4)
            tk.Label(card, text=v[5], font=("Arial", 6), fg="#78909C", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4)
            
            btn_buy = tk.Button(card, command=lambda sk=k: self.buy_sword(sk), font=("Arial", 7, "bold"), relief="flat", cursor="hand2")
            btn_buy.pack(fill="x", padx=4, pady=(4, 4))
            self.sword_cards[k] = btn_buy
            
            col += 1
            if col > 4:
                col = 0
                row += 1

        # 🛡️ ASKERLER SEKMESİ (5 Sütun)
        canvas_un = tk.Canvas(self.tabs["mercenaries"], bg="#121212", highlightthickness=0)
        scroll_un = ttk.Scrollbar(self.tabs["mercenaries"], orient="vertical", command=canvas_un.yview)
        self.scroll_un_frame = tk.Frame(canvas_un, bg="#121212")
        self.scroll_un_frame.bind("<Configure>", lambda e: canvas_un.configure(scrollregion=canvas_un.bbox("all")))
        canvas_un.create_window((0, 0), window=self.scroll_un_frame, anchor="nw")
        canvas_un.configure(yscrollcommand=scroll_un.set)
        canvas_un.pack(side="left", fill="both", expand=True, padx=(5, 0)); scroll_un.pack(side="right", fill="y")

        self.unit_cards = {}
        row, col = 0, 0
        for k, v in self.units.items():
            card = tk.Frame(self.scroll_un_frame, bg="#1E1E1E", bd=1, relief="solid", width=165, height=175)
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            card.pack_propagate(False)

            tk.Label(card, text=f"{v[8]} {v[0]}", font=("Arial", 8, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4, pady=(4, 2))
            lbl_stats = tk.Label(card, text="", font=("Arial", 7, "bold"), fg="#FFD700", bg="#1E1E1E", anchor="w"); lbl_stats.pack(fill="x", padx=4)
            lbl_dps = tk.Label(card, text="", font=("Arial", 6), fg="#78909C", bg="#1E1E1E", anchor="w"); lbl_dps.pack(fill="x", padx=4)

            f_btns = tk.Frame(card, bg="#1E1E1E")
            f_btns.pack(fill="x", padx=4, pady=2)
            btn_buy = tk.Button(f_btns, command=lambda u=k: self.buy_unit(u), font=("Arial", 6, "bold"), relief="flat", cursor="hand2"); btn_buy.pack(side="top", fill="x", pady=1)
            btn_lvl = tk.Button(f_btns, command=lambda u=k: self.lvl_unit(u), font=("Arial", 6, "bold"), bg="#4A148C", fg="#FFF", relief="flat", cursor="hand2"); btn_lvl.pack(side="top", fill="x", pady=1)
            btn_mult = tk.Button(f_btns, command=lambda u=k: self.mult_unit(u), font=("Arial", 6, "bold"), bg="#FF6F00", fg="#FFF", relief="flat", cursor="hand2"); btn_mult.pack(side="top", fill="x", pady=1)
            
            self.unit_cards[k] = (lbl_stats, lbl_dps, btn_buy, btn_lvl, btn_mult)
            col += 1
            if col > 4:
                col = 0
                row += 1

        f_skills_main = tk.Frame(self.tabs["skills"], bg="#121212")
        f_skills_main.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(f_skills_main, text="⚡ AKTİF YETENEKLER", font=("Arial", 11, "bold"), fg="#FFD700", bg="#121212").pack(anchor="w", pady=(0, 5))
        self.skill_btns = {}
        for k, v in self.skills.items():
            f_sk_card = tk.Frame(f_skills_main, bg="#1E1E1E", bd=1, relief="solid")
            f_sk_card.pack(fill="x", pady=4, padx=2)
            
            f_sk_info = tk.Frame(f_sk_card, bg="#1E1E1E")
            f_sk_info.pack(side="left", fill="both", expand=True, padx=10, pady=6)
            tk.Label(f_sk_info, text=f"{v[6]} {v[0]}", font=("Arial", 10, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x")
            tk.Label(f_sk_info, text=v[8], font=("Arial", 8), fg="#9E9E9E", bg="#1E1E1E", anchor="w").pack(fill="x")

            btn = tk.Button(f_sk_card, command=lambda sk=k: self.use_skill(sk), bg=v[7], fg="#FFF", font=("Arial", 9, "bold"), width=18, relief="flat", cursor="hand2")
            btn.pack(side="right", padx=10, pady=8)
            self.skill_btns[k] = btn

        tk.Label(f_skills_main, text="🔮 ÖZEL GÜÇLER & BÜYÜLER", font=("Arial", 11, "bold"), fg="#FFD700", bg="#121212").pack(anchor="w", pady=(15, 5))
        for key, name, desc, bg, cmd in [("pyro", "🔥 Ateş Yağmuru", "300s boyunca saniyede Tık Hasarının 100x katını vurur.", "#BF360C", self.use_pyrokinesis),
                                        ("fuzuli", "⚡ Fuzuli", "10s boyunca Kritik Çarpanı x500 yapar. (Şart: 300 Canavar)", "#FFA000", self.use_fuzuli),
                                        ("darkness", "🌑 Karanlığın Çağrısı", "30s boyunca Asker Hasarını 10 katına çıkarır.", "#4A148C", self.use_darkness)]:
            f_sp_card = tk.Frame(f_skills_main, bg="#1E1E1E", bd=1, relief="solid")
            f_sp_card.pack(fill="x", pady=4, padx=2)

            f_sp_info = tk.Frame(f_sp_card, bg="#1E1E1E")
            f_sp_info.pack(side="left", fill="both", expand=True, padx=10, pady=6)
            tk.Label(f_sp_info, text=name, font=("Arial", 10, "bold"), fg="#FFD700" if key == "fuzuli" else ("#FF3D00" if key == "pyro" else "#7B1FA2"), bg="#1E1E1E", anchor="w").pack(fill="x")
            tk.Label(f_sp_info, text=desc, font=("Arial", 8), fg="#B0BEC5", bg="#1E1E1E", anchor="w").pack(fill="x")

            btn = tk.Button(f_sp_card, command=cmd, font=("Arial", 9, "bold"), width=18, bg=bg, fg="#FFF", relief="flat", cursor="hand2")
            btn.pack(side="right", padx=10, pady=8)
            setattr(self, f"btn_{key}", btn)

        canvas_stg = tk.Canvas(self.tabs["stages"], bg="#121212", highlightthickness=0)
        scroll_stg = ttk.Scrollbar(self.tabs["stages"], orient="vertical", command=canvas_stg.yview)
        self.scroll_stg_frame = tk.Frame(canvas_stg, bg="#121212")
        self.scroll_stg_frame.bind("<Configure>", lambda e: canvas_stg.configure(scrollregion=canvas_stg.bbox("all")))
        canvas_stg.create_window((0, 0), window=self.scroll_stg_frame, anchor="nw")
        canvas_stg.configure(yscrollcommand=scroll_stg.set)
        canvas_stg.pack(side="left", fill="both", expand=True, padx=(5, 0)); scroll_stg.pack(side="right", fill="y")
        self.stage_widgets = {}

        f_q_header = tk.Frame(self.tabs["quests"], bg="#1E1E1E", bd=1, relief="solid"); f_q_header.pack(fill="x", padx=5, pady=5)
        tk.Label(f_q_header, text="🎁 ÖDÜLLER: Normal (+0.5x Hasar/Kr.Hasar) | Zindan (x2 Hasar, x2 Kr.Hasar, Asker Hızı -0.5s)", font=("Arial", 8, "bold"), fg="#FFD700", bg="#1E1E1E", padx=5, pady=6).pack()

        # 📜 GÖREVLER SEKMESİ (5 Sütun ve Butonların Sığması İçin Genişletilmiş Yükseklik)
        canvas_q = tk.Canvas(self.tabs["quests"], bg="#121212", highlightthickness=0)
        scroll_q = ttk.Scrollbar(self.tabs["quests"], orient="vertical", command=canvas_q.yview)
        scroll_q_frame = tk.Frame(canvas_q, bg="#121212")
        scroll_q_frame.bind("<Configure>", lambda e: canvas_q.configure(scrollregion=canvas_q.bbox("all")))
        canvas_q.create_window((0, 0), window=scroll_q_frame, anchor="nw")
        canvas_q.configure(yscrollcommand=scroll_q.set)
        canvas_q.pack(side="left", fill="both", expand=True, padx=(5, 0)); scroll_q.pack(side="right", fill="y")

        self.spec_q_widgets = {}
        self.spec_q_prog_labels = {}
        
        q_row, q_col = 0, 0
        for qk, qdata in self.special_quests.items():
            card = tk.Frame(scroll_q_frame, bg="#1E1E1E", bd=1, relief="solid", width=165, height=115)
            card.grid(row=q_row, column=q_col, padx=4, pady=4, sticky="nsew")
            card.pack_propagate(False)

            tk.Label(card, text=f"{qdata[0]}", font=("Arial", 7, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4, pady=(4, 1))
            
            lbl_prog = tk.Label(card, text="", font=("Arial", 6, "bold"), fg="#00E676", bg="#1E1E1E", anchor="w")
            lbl_prog.pack(fill="x", padx=4)
            self.spec_q_prog_labels[qk] = lbl_prog

            reward_txt = "Ödül: Zindan" if qdata[5] else "Ödül: Normal"
            tk.Label(card, text=reward_txt, font=("Arial", 6), fg="#81C784", bg="#1E1E1E", anchor="w").pack(fill="x", padx=4, pady=(1, 2))
            
            btn_claim = tk.Button(card, text="ÖDÜLÜ AL", command=lambda key=qk: self.claim_quest_reward(key), font=("Arial", 7, "bold"), bg="#37474F", fg="#B0BEC5", state="disabled", relief="flat", cursor="hand2")
            btn_claim.pack(fill="x", padx=4, pady=(2, 4))
            self.spec_q_widgets[qk] = btn_claim

            q_col += 1
            if q_col > 4:
                q_col = 0
                q_row += 1

        tk.Label(self.tabs["perm"], text="🏛️ KALICI YÜKSELTMELER", font=("Arial", 11, "bold"), fg="#FFD700", bg="#121212").pack(pady=6)
        self.perm_widgets = {}
        for pk, (bought, title, desc, gold_c, bone_c, req_stg) in self.perm_upgrades.items():
            card, info = self.create_card_frame(self.tabs["perm"], pady=4)
            tk.Label(info, text=title, font=("Arial", 10, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w").pack(fill="x")
            tk.Label(info, text=desc, font=("Arial", 8), fg="#78909C", bg="#1E1E1E", anchor="w").pack(fill="x")
            tk.Label(info, text=f"Gereksinim: {self.format_number(gold_c)} A | {self.format_number(bone_c)} Bones" + (f" | Zindan {req_stg}" if req_stg > 1 else ""), font=("Arial", 8, "bold"), fg="#FFAB40", bg="#1E1E1E", anchor="w").pack(fill="x")
            btn_buy = tk.Button(card, command=lambda key=pk: self.buy_perm_upgrade(key), font=("Arial", 8, "bold"), width=16, bg="#2E7D32", fg="#FFF", relief="flat", cursor="hand2"); btn_buy.pack(side="right", padx=8, pady=6)
            self.perm_widgets[pk] = btn_buy

        tk.Label(self.tabs["rebirth"], text="Rebirth için en az 2. Zindan, Oda 1 gerekli.", font=("Arial", 9), fg="#B0BEC5", bg="#121212").pack(pady=5)
        self.btn_do_rebirth = tk.Button(self.tabs["rebirth"], command=self.do_rebirth, bg="#B71C1C", fg="white", font=("Arial", 11, "bold"), relief="flat"); self.btn_do_rebirth.pack(fill="x", pady=5, padx=5)
        tk.Frame(self.tabs["rebirth"], height=1, bg="#37474F").pack(fill="x", pady=5)
        
        self.rb_btn_widgets = {}
        for k in self.rb:
            f_rb_card = tk.Frame(self.tabs["rebirth"], bg="#1E1E1E", bd=1, relief="solid")
            f_rb_card.pack(fill="x", pady=3, padx=5)
            
            f_rb_info = tk.Frame(f_rb_card, bg="#1E1E1E")
            f_rb_info.pack(side="left", fill="both", expand=True, padx=8, pady=4)
            lbl_rb_title = tk.Label(f_rb_info, text=self.rb[k][2], font=("Arial", 9, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w")
            lbl_rb_title.pack(fill="x")
            lbl_rb_desc = tk.Label(f_rb_info, text=f"ℹ️ {self.rb[k][3]}", font=("Arial", 7), fg="#9E9E9E", bg="#1E1E1E", anchor="w")
            lbl_rb_desc.pack(fill="x")

            btn_rb = tk.Button(f_rb_card, command=lambda rk=k: self.buy_rb(rk), font=("Arial", 8, "bold"), width=18, relief="flat", cursor="hand2")
            btn_rb.pack(side="right", padx=8, pady=6)
            self.rb_btn_widgets[k] = btn_rb

        f_save = tk.Frame(self.root, bg="#121212"); f_save.pack(fill="x", padx=15, pady=5)
        for name, cmd, color in [("💾 Kaydet", self.save_game, "#1565C0"), ("📂 Yükle", self.load_game, "#00695C"), ("🗑️ Sıfırla", self.reset_game, "#C62828")]:
            tk.Button(f_save, text=name, command=cmd, bg=color, fg="white", font=("Arial", 9, "bold"), relief="flat").pack(side="left" if color != "#C62828" else "right", expand=True, fill="x", padx=2)

    def get_claimed_quests_count(self): 
        return sum(1 for qk, v in self.special_quests.items() if v[3] and not v[5])

    def get_dungeon_quest_multipliers(self):
        dmg_mult = 1.0
        crit_mult = 1.0
        speed_reduction = 0.0
        for qk, v in self.special_quests.items():
            if v[3] and v[5]:
                dmg_mult *= 2.0
                crit_mult *= 2.0
                speed_reduction += 0.5
        return dmg_mult, crit_mult, speed_reduction

    def get_sword_multiplier(self): return max([v[1] for v in self.swords.values() if v[3]], default=1.0)
    
    def get_skill_multipliers(self):
        now, hm, sm, sp = time.time(), 1.0, 1.0, self.rb["skill_power"][0]
        if self.skills["temiz_zihin"][1] and now < self.skills["temiz_zihin"][2]: hm *= (3.0 * sp)
        if self.skills["ellion"][1] and now < self.skills["ellion"][2]: sm *= (5.0 * sp)
        if self.skills["eflatun_muhru"][1] and now < self.skills["eflatun_muhru"][2]: hm *= (10.0 * sp); sm *= (10.0 * sp)
        return hm, sm

    def get_unit_attack_interval(self):
        lvl = int(self.rb["unit_speed"][0])
        base = 10.0 if lvl == 0 else (5.0 if lvl == 1 else (3.0 if lvl == 2 else (2.0 if lvl == 3 else max(0.5, round(2.0 - ((lvl - 3) * 0.1), 2)))))
        _, _, speed_red = self.get_dungeon_quest_multipliers()
        return max(0.1, round((base - speed_red) / self.get_skill_multipliers()[1], 2))

    def get_click_damage(self):
        hm, sm = self.get_skill_multipliers()
        d_dmg_m, _, _ = self.get_dungeon_quest_multipliers()
        base = self.stats["hasar"][0] * self.get_sword_multiplier() * self.rb["hasar"][0] * hm * (1.0 + (sm - 1.0) * 0.2) * (1.0 + self.get_claimed_quests_count() * 0.5) * d_dmg_m
        if self.perm_upgrades["eflatun"][0]: base = max(1000, base * 5.0)
        return int(base)

    def get_unit_dps(self, u_key):
        _, count, lvl, m_lvl, base, _, _, _, _, _ = self.units[u_key]
        if count == 0: return 0
        d_dmg_m, _, _ = self.get_dungeon_quest_multipliers()
        u_dps = base * count * (1.0 + (lvl - 1) * 0.15) * (2 ** (lvl // 10)) * (5 ** m_lvl) * self.rb["hasar"][0] * d_dmg_m
        if time.time() < self.darkness_active_until: u_dps *= 10.0
        if self.perm_upgrades["karanliga_kulak_veren"][0]: u_dps *= 10.0
        if self.perm_upgrades["eflatun"][0]: u_dps *= 5.0
        return int(u_dps)

    def get_auto_dps(self): return int(sum(self.get_unit_dps(k) for k in self.units) * self.get_skill_multipliers()[0])

    def spawn_monster(self):
        self.is_boss = (self.kademe == 10); c = (self.asama - 1) * 10 + self.kademe
        self.current_monster_max_hp = self.current_monster_hp = int(75 * (1.48 ** (c - 1)) * (4.5 if self.is_boss else 1.0))
        self.current_monster_defense = int((c - 1) * 15 * (2.0 if self.is_boss else 1.0))
        m_name = self.get_monster_name(self.asama, self.kademe, self.is_boss)
        self.label_m_name.config(text=m_name, fg="#FF1744" if self.is_boss else "#ECEFF1")
        self.hp_bar["maximum"] = self.current_monster_max_hp; self.hp_bar["value"] = self.current_monster_hp

    def attack(self):
        now = time.time()
        if now - self.last_click_time < 0.07:
            return
        self.last_click_time = now

        self.total_clicks += 1; t_dmg = self.get_click_damage()
        crit = random.random() <= min(0.85, self.stats["sans"][0] * self.rb["sans"][0])
        if crit: self.total_crits += 1
        _, d_crit_m, _ = self.get_dungeon_quest_multipliers()
        crit_mult = 500.0 if now < self.fuzuli_active_until else (self.stats["kritik_hasar"][0] * (1.0 + self.get_claimed_quests_count() * 0.5) * d_crit_m)
        hit = int(t_dmg * (min(500.0, crit_mult * self.rb["kritik_hasar"][0]) if crit else 1.0))
        arm = int(self.current_monster_defense * (1.0 - self.stats["zirh_delme"][0]))
        self.current_monster_hp -= max(1, hit - arm)

        if self.stats["zehir"][0] > 0:
            self.poison_active_until = now + 10.0
            self.poison_tick_damage = max(1, int(((t_dmg * (self.stats["zehir"][0] * 5)) / 5) * (10.0 if self.perm_upgrades["mistik_sovalye"][0] else 1.0)))
            if not self.poison_loop_running: self.poison_loop_running = True; self.poison_tick_loop()

        self.label_battle_log.config(text=f"{'⚡ KRİTİK!' if crit else '⚔️'} {self.format_number(max(1, hit - arm))} Hasar")
        if self.current_monster_hp <= 0: self.monster_defeated()
        self.check_special_quests()
        self.ui_guncelle()

    def use_fuzuli(self):
        if self.fuzuli_kills_counter >= 300: self.fuzuli_kills_counter = 0; self.fuzuli_active_until = time.time() + 10.0; self.ui_guncelle()

    def use_darkness(self):
        now = time.time()
        if now >= self.darkness_cd_until: self.darkness_active_until = now + 30.0; self.darkness_cd_until = now + 180.0; self.ui_guncelle()

    def use_pyrokinesis(self):
        if self.altin >= self.pyro_cost:
            self.altin -= self.pyro_cost; self.pyro_active_until = time.time() + 300.0; self.pyro_cost *= 5
            if not self.pyro_loop_running: self.pyro_loop_running = True; self.pyro_tick_loop()
            self.check_special_quests(); self.ui_guncelle()

    def pyro_tick_loop(self):
        now = time.time()
        if now < self.pyro_active_until and self.current_monster_hp > 0:
            if now - self.pyro_last_tick >= 1.0:
                self.pyro_last_tick = now; arm = int(self.current_monster_defense * (1.0 - self.stats["zirh_delme"][0]))
                self.current_monster_hp -= max(1, (self.get_click_damage() * 100) - arm)
                if self.current_monster_hp <= 0: self.monster_defeated()
                self.ui_guncelle()
            self.root.after(250, self.pyro_tick_loop)
        else: self.pyro_loop_running = False

    def poison_tick_loop(self):
        now = time.time()
        if now < self.poison_active_until and self.current_monster_hp > 0:
            if now - self.poison_last_tick >= 0.25:
                self.poison_last_tick = now; arm = int(self.current_monster_defense * (1.0 - self.stats["zirh_delme"][0]))
                self.current_monster_hp -= max(1, self.poison_tick_damage - int(arm / 5))
                if self.current_monster_hp <= 0: self.monster_defeated()
                self.ui_guncelle()
            self.root.after(250, self.poison_tick_loop)
        else: self.poison_loop_running = False

    def auto_attack_loop(self):
        dps, interval = self.get_auto_dps(), self.get_unit_attack_interval()
        if dps > 0 and self.current_monster_hp > 0:
            arm = int(self.current_monster_defense * (1.0 - self.stats["zirh_delme"][0]))
            self.current_monster_hp -= max(1, int((dps * interval) - arm))
            if self.current_monster_hp <= 0: self.monster_defeated()
            self.ui_guncelle()
        self.root.after(int(interval * 1000), self.auto_attack_loop)

    def monster_defeated(self):
        self.total_kills += 1
        if self.fuzuli_kills_counter < 300: self.fuzuli_kills_counter += 1
        if self.is_boss: self.total_boss_kills += 1
        
        gold_gain = int((8 * (1.11 ** ((self.asama - 1) * 10 + self.kademe))) * (2.0 if self.is_boss else 1.0) * self.rb["gold_mult"][0] * (3.0 if self.perm_upgrades["eflatun"][0] else 1.0))
        self.altin += gold_gain; self.total_gold_earned += gold_gain
        
        if not self.farm_modu.get():
            if self.kademe < 10: 
                self.kademe += 1
            else: 
                stg_key = str(self.asama)
                self.stage_completions[stg_key] = self.stage_completions.get(stg_key, 0) + 1
                
                completed_stage = self.asama
                self.asama += 1
                self.kademe = 1
                self.show_stage_complete_story_popup(completed_stage)

            if self.asama > self.max_ulaşilan_asama or (self.asama == self.max_ulaşilan_asama and self.kademe > self.max_ulaşilan_kademe):
                self.max_ulaşilan_asama, self.max_ulaşilan_kademe = self.asama, self.kademe
        self.check_special_quests(); self.spawn_monster()

    def check_special_quests(self):
        claimed_count = 0
        for qk, qdata in self.special_quests.items():
            if not qdata[2] and qdata[4](): self.special_quests[qk][2] = True
            btn = self.spec_q_widgets[qk]
            lbl_prog = self.spec_q_prog_labels[qk]
            lbl_prog.config(text=f"İlerleme: {qdata[6]()}")
            if self.special_quests[qk][2] and not qdata[3]: btn.config(state="normal", bg="#2E7D32", fg="#FFF", text="ÖDÜLÜ AL")
            elif qdata[3]: claimed_count += 1; btn.config(state="disabled", bg="#1B5E20", fg="#B0BEC5", text="ALINDI ✓")
        self.notebook.tab(self.tabs["quests"], text=f"📜 Görevler ({claimed_count})")

    def claim_quest_reward(self, qk):
        if self.special_quests[qk][2] and not self.special_quests[qk][3]: self.special_quests[qk][3] = True; self.check_special_quests(); self.ui_guncelle()

    def buy_perm_upgrade(self, pk):
        bought, _, _, gold_c, bone_c, req_stg = self.perm_upgrades[pk]
        if not bought and self.altin >= gold_c and self.zones_bones >= bone_c and self.max_ulaşilan_asama >= req_stg:
            self.altin -= gold_c; self.zones_bones -= bone_c; self.perm_upgrades[pk][0] = True; self.ui_guncelle()

    def buy_stat(self, k):
        val, cost, mult, limit = self.stats[k]
        target_buy = self.get_stat_buy_count(k)
        if target_buy <= 0: return
        total_cost = self.get_multi_cost(cost, mult, target_buy)
        if self.altin >= total_cost:
            self.altin -= total_cost
            if k == "hasar": self.stats[k][0] += 3 * target_buy
            elif k in ["sans", "zirh_delme"]: self.stats[k][0] = min(limit, round(val + (0.05 * target_buy), 2))
            elif k == "kritik_hasar": self.stats[k][0] = min(limit, round(val + (1.0 * target_buy), 1))
            elif k == "zehir": self.stats[k][0] = min(limit, val + target_buy)
            self.stats[k][1] = int(cost * (mult ** target_buy)); self.check_special_quests(); self.ui_guncelle()

    def buy_sword(self, sk):
        if not self.swords[sk][3] and self.altin >= self.swords[sk][2]: self.altin -= self.swords[sk][2]; self.swords[sk][3] = True; self.check_special_quests(); self.ui_guncelle()

    def buy_unit(self, u):
        cnt, base_cost = self.buy_multiplier, self.units[u][5]
        total_cost = self.get_multi_cost(base_cost, 1.35, cnt)
        if self.altin >= total_cost: self.altin -= total_cost; self.units[u][1] += cnt; self.units[u][5] = int(base_cost * (1.35 ** cnt)); self.check_special_quests(); self.ui_guncelle()

    def lvl_unit(self, u):
        if self.altin >= self.units[u][6]: self.altin -= self.units[u][6]; self.units[u][2] += 1; self.units[u][6] = int(self.units[u][6] * 1.45); self.ui_guncelle()

    def mult_unit(self, u):
        if self.altin >= self.units[u][7]: self.altin -= self.units[u][7]; self.units[u][3] += 1; self.units[u][7] = int(self.units[u][7] * 10); self.ui_guncelle()

    def use_skill(self, sk):
        now, eff_cd = time.time(), self.skills[sk][5] * (1.0 - self.rb["skill_cd"][0])
        if now >= self.skills[sk][3]: self.skills[sk][1] = True; self.skills[sk][2] = now + self.skills[sk][4]; self.skills[sk][3] = now + eff_cd; self.ui_guncelle()

    def get_potansiyel_bones(self): return 0 if self.max_ulaşilan_asama < 2 else int(((self.max_ulaşilan_asama - 1) * 10 + self.kademe) * 1.2 * self.rb["bones"][0])

    def do_rebirth(self):
        gain = self.get_potansiyel_bones()
        if gain > 0:
            self.zones_bones += gain; self.altin = self.asama = self.kademe = self.max_ulaşilan_asama = self.max_ulaşilan_kademe = 1
            self.pyro_cost = 10000000; self.pyro_active_until = self.darkness_active_until = self.darkness_cd_until = 0
            for sk in self.skills: self.skills[sk][1] = False; self.skills[sk][2] = self.skills[sk][3] = 0
            self.stats = {k: v[:] for k, v in self.stats_defaults.items()}
            self.units = {k: v[:] for k, v in self.units_defaults.items()}
            for sk in self.swords: self.swords[sk][3] = False
            self.spawn_monster(); self.check_special_quests(); self.ui_guncelle(); self.save_game(silent=True)

    def buy_rb(self, k):
        val, cost, _, _, mult = self.rb[k]
        if self.zones_bones >= cost:
            if k == "skill_cd" and val >= 0.70: return
            self.zones_bones -= cost
            if k == "sans": self.rb[k][0] += 0.2
            elif k == "bones": self.rb[k][0] += 5.0
            elif k == "skill_power": self.rb[k][0] += 2.0
            elif k == "skill_cd": self.rb[k][0] = min(0.70, round(val + 0.10, 2))
            elif k == "gold_mult": self.rb[k][0] += 1.0
            elif k == "unit_speed": self.rb[k][0] += 1
            else: self.rb[k][0] += 1.0
            self.rb[k][1] = int(cost * mult); self.ui_guncelle()

    def select_stage(self, stg_num):
        if stg_num <= self.max_ulaşilan_asama:
            self.asama = stg_num
            self.kademe = 1
            self.spawn_monster()
            self.update_stages_tab()
            self.ui_guncelle()

    def prev_stage(self):
        if self.asama > 1: self.asama -= 1; self.kademe = 1; self.spawn_monster(); self.ui_guncelle()
    def next_stage(self):
        if self.asama < self.max_ulaşilan_asama: self.asama += 1; self.kademe = 1; self.spawn_monster(); self.ui_guncelle()
    def prev_kademe(self):
        if self.kademe > 1: self.kademe -= 1; self.spawn_monster(); self.ui_guncelle()
    def next_kademe(self):
        if self.asama < self.max_ulaşilan_asama or (self.asama == self.max_ulaşilan_asama and self.kademe < self.max_ulaşilan_kademe):
            if self.kademe < 10: self.kademe += 1; self.spawn_monster(); self.ui_guncelle()

    def reset_game(self):
        if messagebox.askyesno("Sıfırla", "Tüm ilerleme silinecek!"):
            if os.path.exists("yaratik_avcisi_kayit.json"): os.remove("yaratik_avcisi_kayit.json")
            self.__init__(self.root)

    def save_game(self, silent=False):
        data = {"altin": self.altin, "zones_bones": self.zones_bones, "asama": self.asama, "kademe": self.kademe, "max_ulaşilan_asama": self.max_ulaşilan_asama, "max_ulaşilan_kademe": self.max_ulaşilan_kademe, "farm_modu": self.farm_modu.get(), "stats": self.stats, "swords": self.swords, "units": self.units, "rb": self.rb, "pyro_cost": self.pyro_cost, "total_clicks": self.total_clicks, "total_kills": self.total_kills, "total_crits": self.total_crits, "total_gold_earned": self.total_gold_earned, "total_boss_kills": self.total_boss_kills, "fuzuli_kills_counter": self.fuzuli_kills_counter, "stage_completions": self.stage_completions, "perm_upgrades": {k: v[0] for k, v in self.perm_upgrades.items()}, "claimed_quests": [k for k, v in self.special_quests.items() if v[3]]}
        try:
            with open("yaratik_avcisi_kayit.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
            if not silent: messagebox.showinfo("Başarılı", "Kaydedildi!")
        except Exception as e:
            if not silent: messagebox.showerror("Hata", f"Hata: {e}")

    def load_game(self, silent=False):
        if os.path.exists("yaratik_avcisi_kayit.json"):
            try:
                with open("yaratik_avcisi_kayit.json", "r", encoding="utf-8") as f: data = json.load(f)
                self.altin, self.zones_bones, self.asama, self.kademe = data.get("altin", 0), data.get("zones_bones", 0), data.get("asama", 1), data.get("kademe", 1)
                self.max_ulaşilan_asama, self.max_ulaşilan_kademe = data.get("max_ulaşilan_asama", 1), data.get("max_ulaşilan_kademe", 1)
                self.farm_modu.set(data.get("farm_modu", False))
                self.pyro_cost, self.total_clicks, self.total_kills = data.get("pyro_cost", 10000000), data.get("total_clicks", 0), data.get("total_kills", 0)
                self.total_crits, self.total_gold_earned, self.total_boss_kills = data.get("total_crits", 0), data.get("total_gold_earned", 0), data.get("total_boss_kills", 0)
                self.fuzuli_kills_counter = data.get("fuzuli_kills_counter", 300)
                self.stage_completions = data.get("stage_completions", {})
                if "perm_upgrades" in data:
                    for k, bought in data["perm_upgrades"].items():
                        if k in self.perm_upgrades: self.perm_upgrades[k][0] = bought
                if "claimed_quests" in data:
                    for qk in data["claimed_quests"]:
                        if qk in self.special_quests: self.special_quests[qk][2] = self.special_quests[qk][3] = True
                if "stats" in data:
                    for k, default_val in self.stats_defaults.items(): self.stats[k] = data["stats"].get(k, default_val[:])
                if "swords" in data:
                    saved_swords = data["swords"]
                    for sk in self.swords:
                        if sk in saved_swords:
                            self.swords[sk] = saved_swords[sk]
                if "units" in data:
                    saved_units = data["units"]
                    for uk in self.units:
                        if uk in saved_units:
                            self.units[uk] = saved_units[uk]
                if "rb" in data:
                    for k, default_val in self.rb_defaults.items():
                        if k in data["rb"]:
                            item = data["rb"][k]
                            if len(item) == 4: item.append(default_val[4])
                            self.rb[k] = item
                        else: self.rb[k] = default_val[:]
                self.spawn_monster(); self.check_special_quests(); self.update_stages_tab(); self.ui_guncelle()
                if not silent: messagebox.showinfo("Başarılı", "Yüklendi!")
            except Exception as e:
                if not silent: messagebox.showerror("Hata", f"Hata: {e}")

    def auto_save_loop(self): self.save_game(silent=True); self.root.after(15000, self.auto_save_loop)

    def update_stages_tab(self):
        if not hasattr(self, "stage_widgets_dict"):
            self.stage_widgets_dict = {}

        for stg in range(1, 19):
            stg_key = str(stg)
            completions = self.stage_completions.get(stg_key, 0)
            dname = self.get_dungeon_name(stg)
            
            if stg not in self.stage_widgets_dict:
                if stg > self.max_ulaşilan_asama:
                    continue
                card, info = self.create_card_frame(self.scroll_stg_frame, pady=3)
                lbl_title = tk.Label(info, text="", font=("Arial", 10, "bold"), fg="#ECEFF1", bg="#1E1E1E", anchor="w")
                lbl_title.pack(fill="x")
                lbl_comp = tk.Label(info, text="", font=("Arial", 9, "bold"), fg="#FFD700", bg="#1E1E1E", anchor="w")
                lbl_comp.pack(fill="x")
                
                btn_go = tk.Button(card, text="GİT", command=lambda s=stg: self.select_stage(s), font=("Arial", 8, "bold"), width=10, relief="flat", cursor="hand2")
                btn_go.pack(side="right", padx=8, pady=6)
                self.stage_widgets_dict[stg] = (card, lbl_title, lbl_comp, btn_go)

            if stg in self.stage_widgets_dict:
                card, lbl_title, lbl_comp, btn_go = self.stage_widgets_dict[stg]
                if stg <= self.max_ulaşilan_asama:
                    card.pack(fill="x", pady=3, padx=5)
                    lbl_title.config(text=f"🏰 Zindan {stg}: {dname}")
                    lbl_comp.config(text=f"Tamamlanma: {completions:,} defa")
                    btn_go.config(bg="#2E7D32" if self.asama != stg else "#1B5E20")
                else:
                    card.pack_forget()

    def ui_guncelle(self):
        self.label_asama.config(text=f"🏰 {self.get_dungeon_name(self.asama)} — Oda {self.kademe}/10")
        self.btn_prev_stage.config(state="normal" if self.asama > 1 else "disabled")
        self.btn_next_stage.config(state="normal" if self.asama < self.max_ulaşilan_asama else "disabled")
        self.btn_prev_kdm.config(state="normal" if self.kademe > 1 else "disabled")
        self.btn_next_kdm.config(state="normal" if self.asama < self.max_ulaşilan_asama or (self.asama == self.max_ulaşilan_asama and self.kademe < self.max_ulaşilan_kademe) else "disabled")

        arm = int(self.current_monster_defense * (1.0 - self.stats["zirh_delme"][0]))
        self.label_resources.config(text=f"💰 Altın: {self.format_number(self.altin)} | 🦴 Zones Bones: {self.format_number(self.zones_bones)}")
        interval = self.get_unit_attack_interval()
        self.label_dps.config(text=f"🛡️ Asker Hasarı: +{self.format_number(self.get_auto_dps())}/sn (Hız: {interval}s)")
        self.label_m_stats.config(text=f"HP: {self.format_number(max(0, self.current_monster_hp))}/{self.format_number(self.current_monster_max_hp)} | Savunma: {self.format_number(self.current_monster_defense)}")
        self.hp_bar["value"] = max(0, self.current_monster_hp)

        now = time.time(); p_status = ""
        if now < self.poison_active_until: p_status += f"🧪 Zehir: {round(self.poison_active_until - now, 1)}s ({self.format_number(self.poison_tick_damage*5)}/sn) "
        if now < self.pyro_active_until: p_status += f"🔥 Ateş: {round(self.pyro_active_until - now, 1)}s "
        if now < self.fuzuli_active_until: p_status += f"⚡ Fuzuli: {round(self.fuzuli_active_until - now, 1)}s "
        if now < self.darkness_active_until: p_status += f"🌑 Karanlık: {round(self.darkness_active_until - now, 1)}s "
        self.label_poison_status.config(text=p_status)

        self.btn_attack.config(text=f"⚔️ SALDIR! (Tıklama Hasarı: {self.format_number(self.get_click_damage())})")
        pot = self.get_potansiyel_bones()
        self.btn_do_rebirth.config(text=f"🔄 REBIRTH YAP! (+{self.format_number(pot)} Zones Bones)", state="normal" if pot > 0 else "disabled", bg="#B71C1C" if pot > 0 else "#263238")

        for k, (lbl_val, btn_buy) in self.stat_cards.items():
            val, cost, mult, limit = self.stats[k]
            target_buy = self.get_stat_buy_count(k)
            total_cost = self.get_multi_cost(cost, mult, target_buy) if target_buy > 0 else cost
            val_str = f"%{val*100:.0f}" if k in ["sans", "zirh_delme"] else (f"{val:.1f}x" if k == "kritik_hasar" else (f"Lvl {val}/10 ({val*5}x/sn)" if k == "zehir" else self.format_number(val)))
            lbl_val.config(text=f"Mevcut: {val_str}")
            if limit and val >= limit: btn_buy.config(text="MAKSİMUM", state="disabled", bg="#263238", fg="#757575")
            else:
                can_afford = target_buy > 0 and self.altin >= total_cost
                btn_buy.config(text=f"YÜKSEL (x{target_buy})\n💰 {self.format_number(total_cost)}" if target_buy > 1 else f"YÜKSEL\n💰 {self.format_number(total_cost)}", state="normal" if can_afford else "disabled", bg="#2E7D32" if can_afford else "#37474F", fg="#FFF" if can_afford else "#B0BEC5")

        for k, btn_buy in self.sword_cards.items():
            bought = self.swords[k][3]
            btn_buy.config(text="SAHİP OLUNDU" if bought else f"SATIN AL\n💰 {self.format_number(self.swords[k][2])}", state="disabled" if bought else ("normal" if self.altin >= self.swords[k][2] else "disabled"), bg="#1B5E20" if bought else ("#2E7D32" if self.altin >= self.swords[k][2] else "#37474F"), fg="#FFF" if (bought or self.altin >= self.swords[k][2]) else "#B0BEC5")

        for k, (lbl_stats, lbl_dps, btn_buy, btn_lvl, btn_mult) in self.unit_cards.items():
            name, count, lvl, m_lvl, _, c_buy, c_lvl, c_mult, ico, _ = self.units[k]
            total_buy_cost = self.get_multi_cost(c_buy, 1.35, self.buy_multiplier)
            lbl_stats.config(text=f"Adet: {self.format_number(count)} | Lvl: {lvl} | Boost: {m_lvl}x")
            lbl_dps.config(text=f"DPS: +{self.format_number(self.get_unit_dps(k))}/sn ({interval}s)")
            btn_buy.config(text=f"AL (x{self.buy_multiplier})\n💰 {self.format_number(total_buy_cost)}", state="normal" if self.altin >= total_buy_cost else "disabled", bg="#2E7D32" if self.altin >= total_buy_cost else "#37474F", fg="#FFF" if self.altin >= total_buy_cost else "#B0BEC5")
            btn_lvl.config(text=f"⬆️ Lvl {lvl+1}\n💰 {self.format_number(c_lvl)}", state="normal" if self.altin >= c_lvl else "disabled", bg="#4A148C" if self.altin >= c_lvl else "#37474F", fg="#FFF" if self.altin >= c_lvl else "#B0BEC5")
            btn_mult.config(text=f"⚡ Boost x5\n💰 {self.format_number(c_mult)}", state="normal" if self.altin >= c_mult else "disabled", bg="#FF6F00" if self.altin >= c_mult else "#37474F", fg="#FFF" if self.altin >= c_mult else "#B0BEC5")

        cd_discount = self.rb["skill_cd"][0]
        for k, btn in self.skill_btns.items():
            name, _, end, cd_end, dur, cd, ico, _, _ = self.skills[k]
            eff_cd = int(cd * (1.0 - cd_discount))
            if now < end: btn.config(text=f"AKTİF: {int(end - now)}s", state="disabled", bg="#00838F", fg="#FFF")
            elif now < cd_end: btn.config(text=f"CD: {int(cd_end - now)}s", state="disabled", bg="#37474F", fg="#90A4AE")
            else: btn.config(text=f"KULLAN (CD: {eff_cd}s)", state="normal", bg=self.skills[k][7], fg="#FFF")

        if now < self.pyro_active_until: self.btn_pyro.config(text=f"AKTİF ({int(self.pyro_active_until - now)}s)", state="disabled", bg="#E65100")
        else: self.btn_pyro.config(text=f"KULLAN\n💰 {self.format_number(self.pyro_cost)}", state="normal" if self.altin >= self.pyro_cost else "disabled", bg="#BF360C" if self.altin >= self.pyro_cost else "#37474F", fg="#FFF" if self.altin >= self.pyro_cost else "#B0BEC5")

        if now < self.fuzuli_active_until: self.btn_fuzuli.config(text=f"AKTİF ({int(self.fuzuli_active_until - now)}s)", state="disabled", bg="#FF8F00")
        else: self.btn_fuzuli.config(text=f"KULLAN ({self.fuzuli_kills_counter}/300)", state="normal" if self.fuzuli_kills_counter >= 300 else "disabled", bg="#FF6F00" if self.fuzuli_kills_counter >= 300 else "#37474F", fg="#FFF" if self.fuzuli_kills_counter >= 300 else "#B0BEC5")

        if now < self.darkness_active_until: self.btn_darkness.config(text=f"AKTİF ({int(self.darkness_active_until - now)}s)", state="disabled", bg="#6A1B9A")
        elif now < self.darkness_cd_until: self.btn_darkness.config(text=f"BEKLEME ({int(self.darkness_cd_until - now)}s)", state="disabled", bg="#37474F", fg="#90A4AE")
        else: self.btn_darkness.config(text="KULLAN", state="normal", bg="#4A148C", fg="#FFF")

        for pk, btn_buy in self.perm_widgets.items():
            bought, _, _, gold_c, bone_c, req_stg = self.perm_upgrades[pk]
            can_buy = self.altin >= gold_c and self.zones_bones >= bone_c and self.max_ulaşilan_asama >= req_stg
            btn_buy.config(text="ALINDI ✓" if bought else "YÜKSEL", state="disabled" if bought else ("normal" if can_buy else "disabled"), bg="#1B5E20" if bought else ("#2E7D32" if can_buy else "#37474F"), fg="#FFF" if (bought or can_buy) else "#B0BEC5")

        for k, btn in self.rb_btn_widgets.items():
            val, cost, title, _, _ = self.rb[k]
            if k == "skill_cd" and val >= 0.70: 
                btn.config(text=f"[MAKSİMUM %70]", state="disabled", bg="#1E1E1E", fg="#757575")
            else:
                val_str = f"%{val*100:.0f}" if k == "skill_cd" else (f"Lvl {val} ({interval}s)" if k == "unit_speed" else f"{val:.1f}x")
                can_afford = self.zones_bones >= cost
                btn.config(text=f"{val_str} — {self.format_number(cost)} B", state="normal" if can_afford else "disabled", bg="#4E342E" if can_afford else "#1E1E1E", fg="#FFF" if can_afford else "#757575")

        self.update_stages_tab()

if __name__ == "__main__":
    root = tk.Tk(); app = LoopKnight(root); root.mainloop()