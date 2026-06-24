import pygame
import os

def spritesheet_kes_dikey(dosya_yolu, kacinci_kare):
    try:
        gorsel = pygame.image.load(dosya_yolu).convert_alpha() 
        genislik = gorsel.get_width()
        tek_kare_yuksekligi = gorsel.get_height() // 3 
        kesim_alani = pygame.Rect(0, kacinci_kare * tek_kare_yuksekligi, genislik, tek_kare_yuksekligi)
        kesilen_parca = gorsel.subsurface(kesim_alani)
        return pygame.transform.scale(kesilen_parca, (38, 38)) 
    except Exception as e:
        yuzey = pygame.Surface((38, 38))
        yuzey.fill((255, 255, 0)) 
        return yuzey

def spritesheet_kes_yatay(dosya_yolu, kacinci_kare):
    try:
        gorsel = pygame.image.load(dosya_yolu).convert_alpha() 
        yukseklik = gorsel.get_height()
        tek_kare_genisligi = gorsel.get_width() // 3 
        kesim_alani = pygame.Rect(kacinci_kare * tek_kare_genisligi, 0, tek_kare_genisligi, yukseklik)
        kesilen_parca = gorsel.subsurface(kesim_alani)
        return pygame.transform.scale(kesilen_parca, (38, 38)) 
    except Exception as e:
        yuzey = pygame.Surface((38, 38))
        yuzey.fill((255, 255, 0)) 
        return yuzey

class Player(pygame.sprite.Sprite):
    def __init__(self, baslangic_x, baslangic_y, karakter_adi="imam_packman"):
        super().__init__()
        klasor_yolu = os.path.dirname(os.path.abspath(__file__))
        karakter_klasoru = os.path.join(klasor_yolu, "gorseller", "karakterler")
        
        if karakter_adi == "klasik":
            dosya_u = "klasik_pacman_u.png"
            dosya_d = "klasik_pacman_d.png"
            dosya_l = "klasik_pacman_l.png"
            dosya_r = "klasik_pacman_r.png"
        else:
            dosya_u = f"{karakter_adi}_u1.png"
            dosya_d = f"{karakter_adi}_d1.png"
            dosya_l = f"{karakter_adi}_l1.png"
            dosya_r = f"{karakter_adi}_r1.png"
            
        self.animasyonlar = {
            "up":    [spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_u), 0), 
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_u), 1),
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_u), 2),
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_u), 1)],
            "down":  [spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_d), 0), 
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_d), 1),
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_d), 2),
                      spritesheet_kes_dikey(os.path.join(karakter_klasoru, dosya_d), 1)],
            "left":  [spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_l), 0), 
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_l), 1),
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_l), 2),
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_l), 1)],
            "right": [spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_r), 0), 
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_r), 1),
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_r), 2),
                      spritesheet_kes_yatay(os.path.join(karakter_klasoru, dosya_r), 1)]
        }
        
        self.su_anki_yon = "right"
        self.kare_indeksi = 0
        self.animasyon_hizi = 4  
        self.hareket_sayaci = 0
        self.image = self.animasyonlar[self.su_anki_yon][self.kare_indeksi]
        self.rect = self.image.get_rect()
        self.rect.x = baslangic_x
        self.rect.y = baslangic_y
        self.hiz = 4
        self.yon_x = 0
        self.yon_y = 0
        self.istenen_x = 0
        self.istenen_y = 0

    def update(self, duvar_grubu, yem_grubu, hayalet_grubu, anlik_harita, pacman=None, ses_yoneticisi=None, aktif_ozellik=None, aktif_debuff=None):
        eski_x = self.rect.x
        eski_y = self.rect.y

        if self.rect.left > 1920:
            self.rect.right = 0
            if ses_yoneticisi: ses_yoneticisi.portal_sesi_cal() 
        elif self.rect.right < 0:
            self.rect.left = 1920
            if ses_yoneticisi: ses_yoneticisi.portal_sesi_cal() 
        
        eski_hiz = self.hiz
        
        # --- YAVASLA MANTIĞI BURADA ---
        if aktif_ozellik == "HIZ_ARTISI":
            self.hiz = 8
        elif aktif_debuff == "YAVASLA":
            self.hiz = 2
        else:
            self.hiz = 4
            
        if self.hiz != eski_hiz:
            if self.yon_x != 0: self.yon_x = (self.yon_x // abs(self.yon_x)) * self.hiz
            if self.yon_y != 0: self.yon_y = (self.yon_y // abs(self.yon_y)) * self.hiz
            if self.istenen_x != 0: self.istenen_x = (self.istenen_x // abs(self.istenen_x)) * self.hiz
            if self.istenen_y != 0: self.istenen_y = (self.istenen_y // abs(self.istenen_y)) * self.hiz
        
        avlanan_hayaletler = pygame.sprite.spritecollide(self, hayalet_grubu, True)
        if avlanan_hayaletler:
            if ses_yoneticisi:
                ses_yoneticisi.av_basarili_cal()
            
        tuslar = pygame.key.get_pressed()
        
        sol_basildi = tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]
        sag_basildi = tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]
        yukari_basildi = tuslar[pygame.K_UP] or tuslar[pygame.K_w]
        asagi_basildi = tuslar[pygame.K_DOWN] or tuslar[pygame.K_s]

        # --- TERS DEBUFF MANTIĞI BURADA ---
        if aktif_debuff == "TERS":
            sol_basildi, sag_basildi = sag_basildi, sol_basildi
            yukari_basildi, asagi_basildi = asagi_basildi, yukari_basildi

        if sol_basildi:
            self.istenen_x = -self.hiz
            self.istenen_y = 0
            self.su_anki_yon = "left"
        elif sag_basildi:
            self.istenen_x = self.hiz
            self.istenen_y = 0
            self.su_anki_yon = "right"
        elif yukari_basildi:
            self.istenen_x = 0
            self.istenen_y = -self.hiz
            self.su_anki_yon = "up"
        elif asagi_basildi:
            self.istenen_x = 0
            self.istenen_y = self.hiz
            self.su_anki_yon = "down"

        test_rect = self.rect.copy()
        test_rect.x += self.istenen_x
        test_rect.y += self.istenen_y
        
        carpisma_var_mi = False
        if aktif_ozellik != "PHASE":
            for duvar in duvar_grubu:
                if test_rect.colliderect(duvar.rect):
                    carpisma_var_mi = True
                    break
                
        if not carpisma_var_mi:
            self.yon_x = self.istenen_x
            self.yon_y = self.istenen_y

        self.rect.x += self.yon_x 
        if aktif_ozellik != "PHASE":
            carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvar_grubu, False)
            for duvar in carpisilan_duvarlar:
                if self.yon_x > 0: self.rect.right = duvar.rect.left 
                elif self.yon_x < 0: self.rect.left = duvar.rect.right 

        self.rect.y += self.yon_y 
        if aktif_ozellik != "PHASE":
            carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvar_grubu, False)
            for duvar in carpisilan_duvarlar:
                if self.yon_y > 0: self.rect.bottom = duvar.rect.top
                elif self.yon_y < 0: self.rect.top = duvar.rect.bottom

        if self.rect.x != eski_x or self.rect.y != eski_y:
            if ses_yoneticisi:
                hizli_mod = (aktif_ozellik == "HIZ_ARTISI")
                ses_yoneticisi.hareket_sesi_cal(hizli_mi=hizli_mod)
        else:
            if ses_yoneticisi:
                ses_yoneticisi.hareket_sesi_durdur()

        if self.rect.x != eski_x or self.rect.y != eski_y:
            self.hareket_sayaci += 1
            if self.hareket_sayaci >= self.animasyon_hizi:
                self.hareket_sayaci = 0
                self.kare_indeksi = (self.kare_indeksi + 1) % 4 
        else:
            self.kare_indeksi = 0 
            
        self.image = self.animasyonlar[self.su_anki_yon][self.kare_indeksi]