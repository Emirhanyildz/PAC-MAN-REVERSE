import pygame
import random
import heapq
import os

TILE_SIZE = 40

# --- HAYALETLER İÇİN GÜVENLİ RESİM YÜKLEYİCİ ---
# --- HAYALETLER İÇİN GERÇEK AKILLI RESİM YÜKLEYİCİ (OTOMATİK KARE HESAPLAMA) ---
def hayalet_resmi_yukle(dosya_adi):
    klasor_yolu = os.path.dirname(os.path.abspath(__file__))
    tam_yol = os.path.join(klasor_yolu, "gorseller", "karakterler", dosya_adi)
    try:
        gorsel = pygame.image.load(tam_yol).convert_alpha()
        genislik = gorsel.get_width()
        yukseklik = gorsel.get_height()
        
        # Resim yan yana dizilmişse (Genişlik yükseklikten büyükse)
        if genislik > yukseklik:
            # Genişliği yüksekliğe bölerek kaç kare olduğunu OTOMATİK bul! (Örn: 2 veya 3)
            kare_sayisi = genislik // yukseklik
            tek_kare_genisligi = genislik // kare_sayisi
            
            kesim_alani = pygame.Rect(0, 0, tek_kare_genisligi, yukseklik)
            gorsel = gorsel.subsurface(kesim_alani)
            
        # Resim alt alta dizilmişse (Yükseklik genişlikten büyükse)
        elif yukseklik > genislik:
            # Yüksekliği genişliğe bölerek kaç kare olduğunu bul
            kare_sayisi = yukseklik // genislik
            tek_kare_yuksekligi = yukseklik // kare_sayisi
            
            kesim_alani = pygame.Rect(0, 0, genislik, tek_kare_yuksekligi)
            gorsel = gorsel.subsurface(kesim_alani)
            
        # Kesilmiş veya zaten normal olan resmi oyun boyutuna ayarla
        return pygame.transform.scale(gorsel, (TILE_SIZE, TILE_SIZE ))
        
    except Exception as e:
        print(f"HAYALET RESMİ BULUNAMADI: {dosya_adi} - Hata: {e}")
        return None

class Hayalet(pygame.sprite.Sprite):
    _kisilik_sirasi = ["Kirmizi", "Pembe", "Mavi", "Turuncu"]
    _sayac = 0

    def __init__(self, x, y, kisilik=None, hayalet_kostumu="klasik"):
        super().__init__()
        
        if kisilik is None:
            self.kisilik = Hayalet._kisilik_sirasi[Hayalet._sayac % 4]
            Hayalet._sayac += 1
        else:
            self.kisilik = kisilik

        self.hayalet_kostumu = hayalet_kostumu
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if self.kisilik == "Kirmizi": self.varsayilan_renk = (255, 0, 0)
        elif self.kisilik == "Pembe": self.varsayilan_renk = (255, 184, 255)
        elif self.kisilik == "Mavi": self.varsayilan_renk = (0, 255, 255)
        elif self.kisilik == "Turuncu": self.varsayilan_renk = (255, 184, 82)
            
        self.gorseller = {"sol": None, "sag": None}
        
        # --- CASUS YAZDIRICI: Arka planda ne dönüyor görelim! ---
        print(f"-> GHOST BİLGİSİ: Kostüm='{self.hayalet_kostumu}', Kişilik='{self.kisilik}'")
        
        if self.hayalet_kostumu == "klasik":
            if self.kisilik == "Kirmizi":
                self.gorseller["sol"] = hayalet_resmi_yukle("blinky_ghost_l.png")
                self.gorseller["sag"] = hayalet_resmi_yukle("blinky_ghost_r.png")
            elif self.kisilik == "Pembe":
                self.gorseller["sol"] = hayalet_resmi_yukle("pinky_ghost_l.png")
                self.gorseller["sag"] = hayalet_resmi_yukle("pinky_ghost_r.png")
            elif self.kisilik == "Mavi":
                self.gorseller["sol"] = hayalet_resmi_yukle("inky_ghost_l.png")
                self.gorseller["sag"] = hayalet_resmi_yukle("inky_ghost_r.png")
            elif self.kisilik == "Turuncu":
                self.gorseller["sol"] = hayalet_resmi_yukle("clyde_ghost_l.png")
                self.gorseller["sag"] = hayalet_resmi_yukle("clyde_ghost_r.png")

        elif self.hayalet_kostumu == "gul_ghost":
            self.gorseller["sol"] = hayalet_resmi_yukle("gul_ghost_la.png")
            self.gorseller["sag"] = hayalet_resmi_yukle("gul_ghost_ra.png")
            
        elif self.hayalet_kostumu == "hacli_ghost":
            self.gorseller["sol"] = hayalet_resmi_yukle("hacli_ghost_l.png")
            self.gorseller["sag"] = hayalet_resmi_yukle("hacli_ghost_r.png")

        self.guncel_yon = "sag"
        self.gorunum_guncelle()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hiz = 4  
        self.yon_x = self.hiz
        self.yon_y = 0
        
        self.kacis_modu = False
        self.eski_mod = False 
        self.hafizadaki_hedef = None
        self.panik_sayaci = 0
        self.MAX_PANIK = 120
        self.durum = "SCATTER"
        self.durum_sayaci = 0
        self.SCATTER_SURESI = 60 * 5
        self.FORAGE_SURESI = 60 * 15

        self.scatter_hedefi = self.scatter_kosesi_belirle()

    def gorunum_guncelle(self):
        if self.gorseller[self.guncel_yon] is not None:
            self.image = self.gorseller[self.guncel_yon]
        else:
            self.image.fill(self.varsayilan_renk)

    def scatter_kosesi_belirle(self):
        if self.kisilik == "Kirmizi": return (1, 46)
        elif self.kisilik == "Pembe": return (1, 1)
        elif self.kisilik == "Mavi": return (25, 46)
        elif self.kisilik == "Turuncu": return (25, 1)
        return (1, 1)

    def update(self, duvarlar, yemler, hayaletler, harita, oyuncu, ses_yoneticisi=None, aktif_ozellik=None, aktif_debuff=None):
        if aktif_ozellik == "CHRONOS": return

        yenen_yemler = pygame.sprite.spritecollide(self, yemler, True)
        if yenen_yemler and ses_yoneticisi:
            ses_yoneticisi.yem_yendi_cal()
            
        for yem in yenen_yemler:
            satir = yem.rect.y // TILE_SIZE
            sutun = yem.rect.x // TILE_SIZE
            harita[satir][sutun] = 4

        self.durum_sayaci += 1
        if self.durum == "SCATTER" and self.durum_sayaci >= self.SCATTER_SURESI:
            self.durum = "FORAGE"
            self.durum_sayaci = 0
            self.yon_x, self.yon_y = -self.yon_x, -self.yon_y
        elif self.durum == "FORAGE" and self.durum_sayaci >= self.FORAGE_SURESI:
            self.durum = "SCATTER"
            self.durum_sayaci = 0
            self.yon_x, self.yon_y = -self.yon_x, -self.yon_y

        if self.panik_sayaci > 0:
            self.panik_sayaci -= 1
        else:
            self.hafizadaki_hedef = None
            self.kacis_modu = False

        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            max_sutun = len(harita[0]) - 1
            max_satir = len(harita) - 1
            
            bulundugu_sutun = max(0, min(self.rect.x // TILE_SIZE, max_sutun))
            bulundugu_satir = max(0, min(self.rect.y // TILE_SIZE, max_satir))
            
            oyuncu_sutun = max(0, min(oyuncu.rect.x // TILE_SIZE, max_sutun))
            oyuncu_satir = max(0, min(oyuncu.rect.y // TILE_SIZE, max_satir))

            gordumu = self.gorus_acisi_acik_mi(harita, bulundugu_satir, bulundugu_sutun, oyuncu_satir, oyuncu_sutun)

            if gordumu:
                if not self.kacis_modu and aktif_debuff != "KAC":
                    if ses_yoneticisi: ses_yoneticisi.fark_etme_cal()  
                if aktif_debuff != "KAC":
                    self.kacis_modu = True
                    self.hafizadaki_hedef = (oyuncu_satir, oyuncu_sutun) 
                    self.panik_sayaci = self.MAX_PANIK

            hedef_yon = None
            if aktif_debuff == "KAC":
                hedef_yon = self.a_star_ile_rota_bul(harita, bulundugu_satir, bulundugu_sutun, oyuncu_satir, oyuncu_sutun, -10, -10)
            elif self.kacis_modu:
                hedef_satir, hedef_sutun = self.scatter_hedefi
                hedef_yon = self.a_star_ile_rota_bul(harita, bulundugu_satir, bulundugu_sutun, hedef_satir, hedef_sutun, oyuncu_satir, oyuncu_sutun)
                if hedef_yon is None and self.hafizadaki_hedef:
                    t_satir, t_sutun = self.hafizadaki_hedef
                    hedef_yon = self.kacis_yonu_bul(harita, bulundugu_satir, bulundugu_sutun, t_satir, t_sutun)
            else:
                if self.durum == "SCATTER":
                    hedef_satir, hedef_sutun = self.scatter_hedefi
                    hedef_yon = self.a_star_ile_rota_bul(harita, bulundugu_satir, bulundugu_sutun, hedef_satir, hedef_sutun, oyuncu_satir, oyuncu_sutun)
                else: 
                    hedef_yon = self.bfs_ile_hedef_bul(harita, bulundugu_satir, bulundugu_sutun, oyuncu_satir, oyuncu_sutun)

            if hedef_yon is not None:
                self.yon_x, self.yon_y = hedef_yon[0], hedef_yon[1]
            else:
                gecerli_yonler = []
                ters_x, ters_y = -self.yon_x, -self.yon_y
                olasi_yonler = [(0, 1, self.hiz, 0), (0, -1, -self.hiz, 0), (1, 0, 0, self.hiz), (-1, 0, 0, -self.hiz)]
                for d_satir, d_sutun, y_x, y_y in olasi_yonler:
                    k_satir, k_sutun = bulundugu_satir + d_satir, bulundugu_sutun + d_sutun
                    if 0 <= k_satir <= max_satir and 0 <= k_sutun <= max_sutun:
                        if harita[k_satir][k_sutun] != 1:
                            if y_x != ters_x or y_y != ters_y:
                                gecerli_yonler.append((y_x, y_y))
                if len(gecerli_yonler) == 0:
                    gecerli_yonler.append((ters_x, ters_y))
                secilen_yon = random.choice(gecerli_yonler)
                self.yon_x, self.yon_y = secilen_yon[0], secilen_yon[1]

        self.rect.x += self.yon_x
        self.rect.y += self.yon_y

        carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvarlar, False)
        for duvar in carpisilan_duvarlar:
            if self.yon_x > 0:
                self.rect.right = duvar.rect.left
                self.yon_x = -self.hiz
            elif self.yon_x < 0:
                self.rect.left = duvar.rect.right
                self.yon_x = self.hiz

        carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvarlar, False)
        for duvar in carpisilan_duvarlar:
            if self.yon_y > 0:
                self.rect.bottom = duvar.rect.top
                self.yon_y = -self.hiz
            elif self.yon_y < 0:
                self.rect.top = duvar.rect.bottom
                self.yon_y = self.hiz

        if self.rect.x < 0: self.rect.x = 0
        elif self.rect.x > (len(harita[0]) * TILE_SIZE) - self.rect.width: self.rect.x = (len(harita[0]) * TILE_SIZE) - self.rect.width
        if self.rect.y < 0: self.rect.y = 0
        elif self.rect.y > (len(harita) * TILE_SIZE) - self.rect.height: self.rect.y = (len(harita) * TILE_SIZE) - self.rect.height

        if self.yon_x > 0:
            self.guncel_yon = "sag"
        elif self.yon_x < 0:
            self.guncel_yon = "sol"
            
        self.gorunum_guncelle()

    def gorus_acisi_acik_mi(self, harita, g_satir, g_sutun, o_satir, o_sutun):
        if g_satir != o_satir and g_sutun != o_sutun: return False
        mesafe = abs(g_satir - o_satir) + abs(g_sutun - o_sutun)
        if mesafe > 6: return False
        if g_satir == o_satir:
            min_sutun = min(g_sutun, o_sutun)
            max_sutun = max(g_sutun, o_sutun)
            for s in range(min_sutun + 1, max_sutun):
                if harita[g_satir][s] == 1: return False 
        else:
            min_satir = min(g_satir, o_satir)
            max_satir = max(g_satir, o_satir)
            for s in range(min_satir + 1, max_satir):
                if harita[s][g_sutun] == 1: return False 

        if self.yon_x > 0 and o_sutun < g_sutun: return False 
        if self.yon_x < 0 and o_sutun > g_sutun: return False 
        if self.yon_y > 0 and o_satir < g_satir: return False 
        if self.yon_y < 0 and o_satir > g_satir: return False 
        return True 

    def kacis_yonu_bul(self, harita, g_satir, g_sutun, tehlike_satir, tehlike_sutun):
        yonler = [(0, 1, self.hiz, 0), (0, -1, -self.hiz, 0), (1, 0, 0, self.hiz), (-1, 0, 0, -self.hiz)]
        ters_x, ters_y = -self.yon_x, -self.yon_y
        olasi_hamleler = []
        for d_satir, d_sutun, y_x, y_y in yonler:
            yeni_satir, yeni_sutun = g_satir + d_satir, g_sutun + d_sutun
            if 0 <= yeni_satir < len(harita) and 0 <= yeni_sutun < len(harita[0]):
                if harita[yeni_satir][yeni_sutun] != 1:
                    if y_x == ters_x and y_y == ters_y: continue
                    yeni_mesafe = abs(yeni_sutun - tehlike_sutun) + abs(yeni_satir - tehlike_satir)
                    olasi_hamleler.append((yeni_mesafe, y_x, y_y))
        if olasi_hamleler:
            en_iyi_mesafe = max(olasi_hamleler, key=lambda x: x[0])[0]
            en_iyi_hamleler = [h for h in olasi_hamleler if h[0] == en_iyi_mesafe]
            secilen_hamle = random.choice(en_iyi_hamleler)
            return (secilen_hamle[1], secilen_hamle[2])
        return (ters_x, ters_y)

    def bfs_ile_hedef_bul(self, harita, baslangic_satir, baslangic_sutun, oyuncu_satir, oyuncu_sutun):
        kuyruk = [(baslangic_satir, baslangic_sutun, [])]
        ziyaret_edilenler = set([(baslangic_satir, baslangic_sutun)])
        yonler = [(0, 1, self.hiz, 0), (0, -1, -self.hiz, 0), (1, 0, 0, self.hiz), (-1, 0, 0, -self.hiz)]

        ileri_yon = None
        for y in yonler:
            if y[2] == self.yon_x and y[3] == self.yon_y and (self.yon_x != 0 or self.yon_y != 0):
                ileri_yon = y
                break
        if ileri_yon:
            yonler.remove(ileri_yon)
            yonler.insert(0, ileri_yon)
        ters_x, ters_y = -self.yon_x, -self.yon_y

        while len(kuyruk) > 0:
            guncel_satir, guncel_sutun, yol = kuyruk.pop(0)
            if harita[guncel_satir][guncel_sutun] == 0:
                if len(yol) > 0: return yol[0]
                return None
            for d_satir, d_sutun, y_x, y_y in yonler:
                if len(yol) == 0 and y_x == ters_x and y_y == ters_y: continue
                yeni_satir, yeni_sutun = guncel_satir + d_satir, guncel_sutun + d_sutun

                if 0 <= yeni_satir < len(harita) and 0 <= yeni_sutun < len(harita[0]):
                    if abs(yeni_satir - oyuncu_satir) + abs(yeni_sutun - oyuncu_sutun) <= 2: continue
                    if harita[yeni_satir][yeni_sutun] != 1 and (yeni_satir, yeni_sutun) not in ziyaret_edilenler:
                        ziyaret_edilenler.add((yeni_satir, yeni_sutun))
                        yeni_yol = yol.copy()
                        yeni_yol.append((y_x, y_y))
                        kuyruk.append((yeni_satir, yeni_sutun, yeni_yol))
        return None

    def a_star_ile_rota_bul(self, harita, baslangic_satir, baslangic_sutun, hedef_satir, hedef_sutun, oyuncu_satir, oyuncu_sutun):
        kuyruk = []
        heapq.heappush(kuyruk, (0, (baslangic_satir, baslangic_sutun), []))
        ziyaret_edilenler = set([(baslangic_satir, baslangic_sutun)])
        yonler = [(0, 1, self.hiz, 0), (0, -1, -self.hiz, 0), (1, 0, 0, self.hiz), (-1, 0, 0, -self.hiz)]

        while kuyruk:
            f_maliyet, (g_satir, g_sutun), yol = heapq.heappop(kuyruk)
            if g_satir == hedef_satir and g_sutun == hedef_sutun:
                if len(yol) > 0: return yol[0]
                return None

            for d_satir, d_sutun, y_x, y_y in yonler:
                yeni_satir, yeni_sutun = g_satir + d_satir, g_sutun + d_sutun

                if 0 <= yeni_satir < len(harita) and 0 <= yeni_sutun < len(harita[0]):
                    if abs(yeni_satir - oyuncu_satir) + abs(yeni_sutun - oyuncu_sutun) <= 2: continue
                    if harita[yeni_satir][yeni_sutun] != 1 and (yeni_satir, yeni_sutun) not in ziyaret_edilenler:
                        ziyaret_edilenler.add((yeni_satir, yeni_sutun))
                        yeni_yol = yol.copy()
                        yeni_yol.append((y_x, y_y))
                        
                        g_cost = len(yeni_yol)
                        h_cost = abs(hedef_satir - yeni_satir) + abs(hedef_sutun - yeni_sutun)
                        f_cost = g_cost + h_cost
                        heapq.heappush(kuyruk, (f_cost, (yeni_satir, yeni_sutun), yeni_yol))
        return None
