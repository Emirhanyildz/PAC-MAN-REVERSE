import pygame
import random

# TILE_SIZE'ı 40 olarak sabitliyoruz
TILE_SIZE = 40

class Hayalet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Boyutu TILE_SIZE (40) ile güncelledik
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Hız 2. 40'a tam bölünür (40 % 2 == 0), bu yüzden harika bir hız!
        self.hiz = 3  
        self.yon_x = self.hiz
        self.yon_y = 0
        
        # Hayaletin anlık ruh halini tutan durum değişkeni
        self.kacis_modu = False
        self.eski_mod = False 
        
    def kacis_yonu_bul(self, harita, g_satir, g_sutun, p_satir, p_sutun):
        yonler = [
            (0, 1, self.hiz, 0),   # Sağ
            (0, -1, -self.hiz, 0), # Sol
            (1, 0, 0, self.hiz),   # Aşağı
            (-1, 0, 0, -self.hiz)  # Yukarı
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
                        
                    yeni_mesafe = abs(yeni_sutun - p_sutun) + abs(yeni_satir - p_satir)
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
            (0, 1, self.hiz, 0),   # Sağ
            (0, -1, -self.hiz, 0), # Sol
            (1, 0, 0, self.hiz),   # Aşağı
            (-1, 0, 0, -self.hiz)  # Yukarı
        ]
        
        random.shuffle(yonler)
        ters_x = -self.yon_x
        ters_y = -self.yon_y

        while len(kuyruk) > 0:
            guncel_satir, guncel_sutun, yol = kuyruk.pop(0)

            if harita[guncel_satir][guncel_sutun] == 0:
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
            # // 32'ler // TILE_SIZE (40) olarak değiştirildi
            satir = yem.rect.y // TILE_SIZE
            sutun = yem.rect.x // TILE_SIZE
            harita[satir][sutun] = 0

        # 1. KAVŞAK KONTROLÜ
        # % 32'ler % TILE_SIZE (40) olarak değiştirildi
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            
            # Matristeki yerler 40'a bölünerek doğru bulunuyor
            bulundugu_sutun = self.rect.x // TILE_SIZE
            bulundugu_satir = self.rect.y // TILE_SIZE
            
            oyuncu_sutun = oyuncu.rect.x // TILE_SIZE
            oyuncu_satir = oyuncu.rect.y // TILE_SIZE

            delta_x = oyuncu_sutun - bulundugu_sutun
            delta_y = oyuncu_satir - bulundugu_satir
            mesafe = abs(delta_x) + abs(delta_y)

            tehlike_esigi = 3 
            
            if (self.yon_x > 0 and delta_x > 0) or \
               (self.yon_x < 0 and delta_x < 0) or \
               (self.yon_y > 0 and delta_y > 0) or \
               (self.yon_y < 0 and delta_y < 0):
                tehlike_esigi = 6 

            if mesafe <= tehlike_esigi:
                self.kacis_modu = True 
            elif mesafe >= 9:
                self.kacis_modu = False 

            if self.kacis_modu and not self.eski_mod:
                self.yon_x = -self.yon_x
                self.yon_y = -self.yon_y
                self.eski_mod = True
                
            else:
                self.eski_mod = self.kacis_modu
                
                if self.kacis_modu:
                    hedef_yon = self.kacis_yonu_bul(harita, bulundugu_satir, bulundugu_sutun, oyuncu_satir, oyuncu_sutun)
                else:
                    hedef_yon = self.bfs_ile_hedef_bul(harita, bulundugu_satir, bulundugu_sutun)

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
                        # HATA DÜZELTMESİ: Harita sınırları dışına çıkmayı engelleyen kontrol eklendi
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