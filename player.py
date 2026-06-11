import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, baslangic_x, baslangic_y):
        super().__init__()
        
        self.image = pygame.Surface((38, 38))
        self.image.fill((255, 255, 0)) 
        self.rect = self.image.get_rect()
        
        self.rect.x = baslangic_x
        self.rect.y = baslangic_y
        self.hiz = 3
        
        # SÜREKLİ HAREKET VE HAFIZA DEĞİŞKENLERİ
        self.yon_x = 0
        self.yon_y = 0
        self.istenen_x = 0
        self.istenen_y = 0

    # update metoduna ses_yoneticisi parametresi eklendi
    def update(self, duvarlar, yemler, hayaletler, harita, oyuncu=None, ses_yoneticisi=None):
        # ---------------- HAYALET AVLAMA ----------------
        avlanan_hayaletler = pygame.sprite.spritecollide(self, hayaletler, True)
        if avlanan_hayaletler:
            print("Av başarılı! Bir hayalet yok edildi.")
            # SES KANCASI: Hayalet avlandığında çal
            if ses_yoneticisi:
                ses_yoneticisi.av_basarili_cal()
            
        tuslar = pygame.key.get_pressed()
        
        # 1. KULLANICININ İSTEDİĞİ YÖNÜ HAFIZAYA AL
        if tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]:
            self.istenen_x = -self.hiz
            self.istenen_y = 0
        elif tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]:
            self.istenen_x = self.hiz
            self.istenen_y = 0
        elif tuslar[pygame.K_UP] or tuslar[pygame.K_w]:
            self.istenen_x = 0
            self.istenen_y = -self.hiz
        elif tuslar[pygame.K_DOWN] or tuslar[pygame.K_s]:
            self.istenen_x = 0
            self.istenen_y = self.hiz

        # 2. GELECEĞİ GÖRME (İstenen yöne dönülebilir mi?)
        test_rect = self.rect.copy()
        test_rect.x += self.istenen_x
        test_rect.y += self.istenen_y
        
        carpisma_var_mi = False
        for duvar in duvarlar:
            if test_rect.colliderect(duvar.rect):
                carpisma_var_mi = True
                break
                
        # Eğer istenen yönde duvar YOKSA, karakteri o yöne döndür
        if not carpisma_var_mi:
            self.yon_x = self.istenen_x
            self.yon_y = self.istenen_y

        # 3. FİZİK VE DUVAR SÜRTÜNMESİ (X Ekseni)
        self.rect.x += self.yon_x 
        carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvarlar, False)
        for duvar in carpisilan_duvarlar:
            if self.yon_x > 0: self.rect.right = duvar.rect.left 
            elif self.yon_x < 0: self.rect.left = duvar.rect.right 

        # 4. FİZİK VE DUVAR SÜRTÜNMESİ (Y Ekseni)
        self.rect.y += self.yon_y 
        carpisilan_duvarlar = pygame.sprite.spritecollide(self, duvarlar, False)
        for duvar in carpisilan_duvarlar:
            if self.yon_y > 0: self.rect.bottom = duvar.rect.top
            elif self.yon_y < 0: self.rect.top = duvar.rect.bottom
