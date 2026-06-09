import pygame
import random

TILE_SIZE = 40

class Hayalet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hiz = 4  
        self.yon_x = self.hiz
        self.yon_y = 0
        
        self.kacis_modu = False
        self.eski_mod = False 
        
        # --- YENİ: HAFIZA VE PSİKOLOJİ SİSTEMİ ---
        self.hafizadaki_hedef = None  # Oyuncunun son görüldüğü koordinatları tutar
        self.panik_sayaci = 0         # Oyuncu gözden kaybolduğunda ne kadar süre daha kaçacağını belirler
        self.MAX_PANIK = 120          # 60 FPS'de 120 frame = 2 saniye boyunca hafızasında tutar

    def kacis_yonu_bul(self, harita, g_satir, g_sutun, tehlike_satir, tehlike_sutun):
        # Artık doğrudan oyuncudan değil, hafızasındaki tehlike noktasından kaçıyor!
        yonler = [
            (0, 1, self.hiz, 0),   
            (0, -1, -self.hiz, 0), 
            (1, 0, 0, self.hiz),   
            (-1, 0, 0, -self.hiz)  
        ]
        
        ters_x = -self.yon_x
        ters_y = -self.yon_y
        
        olasi_hamleler = []
        for d_satir, d_sutun, y_x, y_y in yonler:
            yeni_satir = g_satir + d_satir
            yeni_sutun = g_sutun + d_sutun
            
            if 0 <= yeni_satir < len(harita) and 0 <= yeni_sutun < len(harita[0]):
                if harita[yeni_satir][yeni_sutun] != 1:
                    if y_x == ters_x and y_y == ters_y:
                        continue 
                        
                    yeni_mesafe = abs(yeni_sutun - tehlike_sutun) + abs(yeni_satir - tehlike_satir)
                    olasi_hamleler.append((yeni_mesafe, y_x, y_y))

        if olasi_hamleler:
            en_iyi_mesafe = max(olasi_hamleler, key=lambda x: x[0])[0]
            en_iyi_hamleler = [h for h in olasi_hamleler if h[0] == en_iyi_mesafe]
            secilen_hamle = random.choice(en_iyi_hamleler) 
            return (secilen_hamle[1], secilen_hamle[2])
            
        return (ters_x, ters_y)

    def bfs_ile_hedef_bul(self, harita, baslangic_satir, baslangic_sutun):
        kuyruk = [(baslangic_satir, baslangic_sutun, [])]
        ziyaret_edilenler = set()
        ziyaret_edilenler.add((baslangic_satir, baslangic_sutun))

        yonler = [
            (0, 1, self.hiz, 0),   
            (0, -1, -self.hiz, 0), 
            (1, 0, 0, self.hiz),   
            (-1, 0, 0, -self.hiz)  
        ]

        # BFS Momentum: Önceki yönü koruyarak titremeyi engelle
        ileri_yon = None
        for y in yonler:
            if y[2] == self.yon_x and y[3] == self.yon_y and (self.yon_x != 0 or self.yon_y != 0):
                ileri_yon = y
                break
        
        if ileri_yon:
            yonler.remove(ileri_yon)
            yonler.insert(0, ileri_yon)

        ters_x = -self.yon_x
        ters_y = -self.yon_y

        while len(kuyruk) > 0:
            guncel_satir, guncel_sutun, yol = kuyruk.pop(0)

            # Hedef yem (2)
            if harita[guncel_satir][guncel_sutun] == 2:
                if len(yol) > 0:
                    return yol[0] 
                return None

            for d_satir, d_sutun, y_x, y_y in yonler:
                if len(yol) == 0 and y_x == ters_x and y_y == ters_y:
                    continue 

                yeni_satir = guncel_satir + d_satir
                yeni_sutun = guncel_sutun + d_sutun

                if 0 <= yeni_satir < len(harita) and 0 <= yeni_sutun < len(harita[0]):
                    if harita[yeni_satir][yeni_sutun] != 1 and (yeni_satir, yeni_sutun) not in ziyaret_edilenler:
                        ziyaret_edilenler.add((yeni_satir, yeni_sutun))
                        
                        yeni_yol = yol.copy()
                        yeni_yol.append((y_x, y_y))
                        kuyruk.append((yeni_satir, yeni_sutun, yeni_yol))

        return None
    
    def update(self, duvarlar, yemler, hayaletler, harita, oyuncu, ses_yoneticisi=None):
        yenen_yemler = pygame.sprite.spritecollide(self, yemler, True)
        
        if yenen_yemler and ses_yoneticisi:
            ses_yoneticisi.yem_yendi_cal()
            
        for yem in yenen_yemler:
            satir = yem.rect.y // TILE_SIZE
            sutun = yem.rect.x // TILE_SIZE
            harita[satir][sutun] = 0

        # --- HAFIZA VE PANİK SAYAÇ GÜNCELLEMESİ ---
        # Eğer panikliyse sayacı her frame 1 düşür
        if self.panik_sayaci > 0:
            self.panik_sayaci -= 1
        else:
            # Sayaç sıfırlandıysa (2 saniye geçtiyse) tehlikeyi unut ve sakinleş
            self.hafizadaki_hedef = None
            self.kacis_modu = False


        # 1. KAVŞAK KONTROLÜ
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

            tehlike_esigi = 3 
            
            # Görüş Alanı (FoV)
            if (self.yon_x > 0 and delta_x > 0) or \
               (self.yon_x < 0 and delta_x < 0) or \
               (self.yon_y > 0 and delta_y > 0) or \
               (self.yon_y < 0 and delta_y < 0):
                tehlike_esigi = 6 

            # --- GÖRSEL TEMAS KONTROLÜ ---
            # Eğer oyuncu görüş alanı (FoV) içine girdiyse:
            if mesafe <= tehlike_esigi:
                self.kacis_modu = True 
                self.hafizadaki_hedef = (oyuncu_satir, oyuncu_sutun) # Gördüğü yeri hafızaya yaz
                self.panik_sayaci = self.MAX_PANIK # Sayacı fulle (2 saniye kaçacak)

            # Karar Aşamasında Durum Değişiklikleri
            if self.kacis_modu and not self.eski_mod:
                self.yon_x = -self.yon_x
                self.yon_y = -self.yon_y
                self.eski_mod = True
                
            else:
                self.eski_mod = self.kacis_modu
                
                # --- YAPAY ZEKA KARAR AĞACI ---
                if self.kacis_modu and self.hafizadaki_hedef:
                    # Hafızasındaki tehlikeden kaçıyor
                    tehlike_satir, tehlike_sutun = self.hafizadaki_hedef
                    hedef_yon = self.kacis_yonu_bul(harita, bulundugu_satir, bulundugu_sutun, tehlike_satir, tehlike_sutun)
                else:
                    # Hafızasında tehlike yoksa, sakin sakin yem arıyor
                    hedef_yon = self.bfs_ile_hedef_bul(harita, bulundugu_satir, bulundugu_sutun)

                # Rotayı Uygulama Kodu (Aynı)
                if hedef_yon is not None:
                    self.yon_x = hedef_yon[0]
                    self.yon_y = hedef_yon[1]
                else:
                    gecerli_yonler = []
                    ters_x = -self.yon_x
                    ters_y = -self.yon_y
                    
                    olasi_yonler = [
                        (0, 1, self.hiz, 0),
                        (0, -1, -self.hiz, 0),
                        (1, 0, 0, self.hiz),
                        (-1, 0, 0, -self.hiz)
                    ]

                    for d_satir, d_sutun, y_x, y_y in olasi_yonler:
                        kontrol_satir = bulundugu_satir + d_satir
                        kontrol_sutun = bulundugu_sutun + d_sutun
                        
                        if 0 <= kontrol_satir < len(harita) and 0 <= kontrol_sutun < len(harita[0]):
                            if harita[kontrol_satir][kontrol_sutun] != 1:
                                if y_x != ters_x or y_y != ters_y: 
                                    gecerli_yonler.append((y_x, y_y))

                    if len(gecerli_yonler) == 0:
                        gecerli_yonler.append((ters_x, ters_y))

                    if gecerli_yonler:
                        secilen_yon = random.choice(gecerli_yonler)
                        self.yon_x = secilen_yon[0]
                        self.yon_y = secilen_yon[1]

        # 2. HAREKETİ UYGULA
        self.rect.x += self.yon_x
        self.rect.y += self.yon_y

        # 3. DUVAR ÇARPIŞMALARI
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

        # Ekran Sınırları (Görünmez Duvarlar)
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > (len(harita[0]) * TILE_SIZE) - self.rect.width:
            self.rect.x = (len(harita[0]) * TILE_SIZE) - self.rect.width
            
        if self.rect.y < 0:
            self.rect.y = 0  
        elif self.rect.y > (len(harita) * TILE_SIZE) - self.rect.height:
            self.rect.y = (len(harita) * TILE_SIZE) - self.rect.height