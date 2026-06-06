import pygame
import random

class Hayalet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hiz = 2  # 32'ye tam bölünebilen kritik hız değeri!
        self.yon_x = self.hiz
        self.yon_y = 0
        
        # Hayaletin anlık ruh halini tutan durum değişkeni
        self.kacis_modu = False
        self.eski_mod = False # Mod değişimini algılamak için
        
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
                    
                    # 1. KURAL: U-DÖNÜŞÜ KESİNLİKLE YASAK! (Titremeyi engeller)
                    if y_x == ters_x and y_y == ters_y:
                        continue 
                        
                    yeni_mesafe = abs(yeni_sutun - p_sutun) + abs(yeni_satir - p_satir)
                    olasi_hamleler.append((yeni_mesafe, y_x, y_y))

        if olasi_hamleler:
            # TIE-BREAKING (EŞİTLİK BOZMA) - ZAR ATMA (RNG)
            en_iyi_mesafe = max(olasi_hamleler, key=lambda x: x[0])[0]
            # Bu en iyi mesafeyi veren tüm yönleri bir listeye al (Eşitlik durumu olabilir)
            en_iyi_hamleler = [h for h in olasi_hamleler if h[0] == en_iyi_mesafe]
            
            # Eğer birden fazla eşit kaçış yolu varsa rastgele birini seçerek öngörülemezliği artır
            secilen_hamle = random.choice(en_iyi_hamleler) 
            return (secilen_hamle[1], secilen_hamle[2])
            
        # 2. KURAL: Eğer çıkmaz sokaktaysa ve başka yol yoksa mecburen geri döner
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
        
        # Hayaletlerin aynı yollara girmemesi için rastgelelik
        random.shuffle(yonler)
        
        # Hayaletin o anki yönünün tam tersini (U-dönüşünü) hesapla
        ters_x = -self.yon_x
        ters_y = -self.yon_y

        while len(kuyruk) > 0:
            guncel_satir, guncel_sutun, yol = kuyruk.pop(0)

            # Suyu yayarken bir yeme (2) denk geldik mi?
            if harita[guncel_satir][guncel_sutun] == 2:
                if len(yol) > 0:
                    return yol[0] # Hedefe giden ilk adımı döndür
                return None

            # Etraftaki 4 komşuya bak
            for d_satir, d_sutun, y_x, y_y in yonler:
                
                # ----- BFS İÇİN 180 DERECE YASAĞI -----
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
    
    # update metoduna ses_yoneticisi parametresi eklendi
    def update(self, duvarlar, yemler, hayaletler, harita, oyuncu, ses_yoneticisi=None):
        yenen_yemler = pygame.sprite.spritecollide(self, yemler, True)
        
        # SES KANCASI (Event Hook): Yem yenildiği anda ses tetikle
        if yenen_yemler and ses_yoneticisi:
            ses_yoneticisi.yem_yendi_cal()
            
        for yem in yenen_yemler:
            satir = yem.rect.y // 32
            sutun = yem.rect.x // 32
            harita[satir][sutun] = 0

        # 1. KAVŞAK KONTROLÜ
        if self.rect.x % 32 == 0 and self.rect.y % 32 == 0:
            
            bulundugu_sutun = self.rect.x // 32
            bulundugu_satir = self.rect.y // 32
            
            oyuncu_sutun = oyuncu.rect.x // 32
            oyuncu_satir = oyuncu.rect.y // 32

            # MANHATTAN MESAFESİ DELTA (FARK) HESAPLARI
            delta_x = oyuncu_sutun - bulundugu_sutun
            delta_y = oyuncu_satir - bulundugu_satir
            mesafe = abs(delta_x) + abs(delta_y)

            # --- FIELD OF VIEW (GÖRÜŞ ALANI) MEKANİZMASI ---
            # Varsayılan sezgi eşiği (Oyuncu arkadaysa veya yandaysa)
            tehlike_esigi = 3 
            
            # Eğer hayaletin hareket yönü ile Pac-Man'in bulunduğu yön aynıysa (Göz göze geldilerse)
            if (self.yon_x > 0 and delta_x > 0) or \
               (self.yon_x < 0 and delta_x < 0) or \
               (self.yon_y > 0 and delta_y > 0) or \
               (self.yon_y < 0 and delta_y < 0):
                tehlike_esigi = 6 # Görüş mesafesini artır (Uzaklardan fark et)

            if mesafe <= tehlike_esigi:
                self.kacis_modu = True 
            elif mesafe >= 9:
                self.kacis_modu = False 

            # DÜZELTİLMİŞ 180 DERECE KURALI
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
                        if harita[bulundugu_satir + d_satir][bulundugu_sutun + d_sutun] != 1:
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