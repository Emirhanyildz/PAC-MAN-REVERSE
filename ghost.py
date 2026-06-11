import pygame
import random
import heapq

TILE_SIZE = 40

class Hayalet(pygame.sprite.Sprite):
    _kisilik_sirasi = ["Kirmizi", "Pembe", "Mavi", "Turuncu"]
    _sayac = 0

    def __init__(self, x, y, kisilik=None):
        super().__init__()
        
        if kisilik is None:
            self.kisilik = Hayalet._kisilik_sirasi[Hayalet._sayac % 4]
            Hayalet._sayac += 1
        else:
            self.kisilik = kisilik

        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if self.kisilik == "Kirmizi":
            self.image.fill((255, 0, 0))
        elif self.kisilik == "Pembe":
            self.image.fill((255, 184, 255))
        elif self.kisilik == "Mavi":
            self.image.fill((0, 255, 255))
        elif self.kisilik == "Turuncu":
            self.image.fill((255, 184, 82))
            
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

    def scatter_kosesi_belirle(self):
        if self.kisilik == "Kirmizi": return (1, 46)
        elif self.kisilik == "Pembe": return (1, 1)
        elif self.kisilik == "Mavi": return (25, 46)
        elif self.kisilik == "Turuncu": return (25, 1)
        return (1, 1)

    def update(self, duvarlar, yemler, hayaletler, harita, oyuncu, ses_yoneticisi=None):
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

            delta_x = oyuncu_sutun - bulundugu_sutun
            delta_y = oyuncu_satir - bulundugu_satir
            mesafe = abs(delta_x) + abs(delta_y)

            # --- YENİ SNEAKY GÖRÜŞ SİSTEMİ (Line of Sight) ---
            gordumu = self.gorus_acisi_acik_mi(harita, bulundugu_satir, bulundugu_sutun, oyuncu_satir, oyuncu_sutun)

            if gordumu:
                # KRİTİK KONTROL: Eğer hayalet zaten panikte DEĞİLSE (Seni İLK kez görüyorsa)
                if not self.kacis_modu:
                    if ses_yoneticisi:
                        ses_yoneticisi.fark_etme_cal()  # Sesi sadece 1 kere tetikle
                
                self.kacis_modu = True
                self.hafizadaki_hedef = (oyuncu_satir, oyuncu_sutun) # Son gördüğü yeri hafızaya kazı
                self.panik_sayaci = self.MAX_PANIK

            hedef_yon = None

            if self.kacis_modu:
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

    def kacis_yonu_bul(self, harita, g_satir, g_sutun, tehlike_satir, tehlike_sutun):
        yonler = [(0, 1, self.hiz, 0), (0, -1, -self.hiz, 0), (1, 0, 0, self.hiz), (-1, 0, 0, -self.hiz)]
        ters_x, ters_y = -self.yon_x, -self.yon_y
        olasi_hamleler = []
    def gorus_acisi_acik_mi(self, harita, g_satir, g_sutun, o_satir, o_sutun):
        # 1. Düz bir hat üzerinde miyiz? (Aynı satır veya aynı sütun)
        if g_satir != o_satir and g_sutun != o_sutun:
            return False # Çaprazda kalıyorsa duvar arkası veya kör nokta sayılır

        # 2. Mesafe 6 kareden uzaksa ufuk çizgisini göremez
        mesafe = abs(g_satir - o_satir) + abs(g_sutun - o_sutun)
        if mesafe > 6:
            return False
            
        # 3. Aynı satırdaysak, aradaki sütunları (kareleri) tarayıp duvar var mı diye bak
        if g_satir == o_satir:
            min_sutun = min(g_sutun, o_sutun)
            max_sutun = max(g_sutun, o_sutun)
            for s in range(min_sutun + 1, max_sutun):
                if harita[g_satir][s] == 1:
                    return False # Arada duvar var, görüş kesildi!
                    
        # 4. Aynı sütundaysak, aradaki satırları tarayıp duvar var mı diye bak
        else:
            min_satir = min(g_satir, o_satir)
            max_satir = max(g_satir, o_satir)
            for s in range(min_satir + 1, max_satir):
                if harita[s][g_sutun] == 1:
                    return False # Arada duvar var, görüş kesildi!

        # 5. Görüş Yönü Kontrolü: Sadece baktığı yönü görebilir (Arkasını göremez)
        if self.yon_x > 0 and o_sutun < g_sutun: return False # Sağa giderken solu göremez
        if self.yon_x < 0 and o_sutun > g_sutun: return False # Sola giderken sağı göremez
        if self.yon_y > 0 and o_satir < g_satir: return False # Aşağı giderken yukarıyı göremez
        if self.yon_y < 0 and o_satir > g_satir: return False # Yukarı giderken aşağıyı göremez

        return True # Eğer hiçbir engele takılmadıysa, oyuncu net bir şekilde görülmüştür!
        
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
                    # ÖLÜM BÖLGESİ (DEATH ZONE): Oyuncunun 2 kare yakınına girme!
                    if abs(yeni_satir - oyuncu_satir) + abs(yeni_sutun - oyuncu_sutun) <= 2:
                        continue

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
                    # ÖLÜM BÖLGESİ (DEATH ZONE): Kaçarken bile oyuncunun 2 kare yakınına girme!
                    if abs(yeni_satir - oyuncu_satir) + abs(yeni_sutun - oyuncu_sutun) <= 2:
                        continue

                    if harita[yeni_satir][yeni_sutun] != 1 and (yeni_satir, yeni_sutun) not in ziyaret_edilenler:
                        ziyaret_edilenler.add((yeni_satir, yeni_sutun))
                        yeni_yol = yol.copy()
                        yeni_yol.append((y_x, y_y))
                        
                        g_cost = len(yeni_yol)
                        h_cost = abs(hedef_satir - yeni_satir) + abs(hedef_sutun - yeni_sutun)
                        f_cost = g_cost + h_cost
                        
                        heapq.heappush(kuyruk, (f_cost, (yeni_satir, yeni_sutun), yeni_yol))
        return None
