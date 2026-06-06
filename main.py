import pygame
from ghost import Hayalet
import sys
from player import Player  
from ses_yoneticisi import SesYoneticisi  # 1. EKLEME: Ses yöneticisini içeri aktar

pygame.init()

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Pac-Man Reverse")

sol_yari = [
    "111111111111111111111111111111",
    "122222222222221111222222222222",
    "121111112111111111211111121111",
    "121111112111111111211111121111",
    "122222222222222222222222222222",
    "121111112112111111111111211111",
    "121111112112111111111111211111",
    "122222222112222112222222222222",
    "111111112111110110111111111111",
    "110000012111110110111111111111",
    "100000012110000000000000111111",
    "111111112110111111110011111111", 
    "122222222000100000000010000000", 
    "111111112110100033300010111111", 
    "100000012110111111111110111111", 
    "100000012110000000000000111111", 
    "111111112110111111111111111111",
    "122222222222222222222222222222",
    "121111112111111111211111121111",
    "121111112111111111211111121111",
    "122221112222221111222222222222",
    "111121112112111111111111211111",
    "111121112112111111111111211111",
    "122222222112222112222222222222",
    "121111111111112112111111111111",
    "121111111111112112111111111111",
    "122222222222222222222222222222",
    "111111111111111111111111111111",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000"
]

harita_taslagi = []
for sol in sol_yari:
    sag = sol[::-1] 
    harita_taslagi.append(sol + sag)

seviye_haritasi = []
for satir_metni in harita_taslagi:
    sayisal_satir = [int(karakter) for karakter in satir_metni]
    seviye_haritasi.append(sayisal_satir)


class Duvar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 0, 255)) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Yem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8,8))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
tum_spriteler = pygame.sprite.Group()
duvar_grubu = pygame.sprite.Group()
yem_grubu = pygame.sprite.Group()
hayalet_grubu = pygame.sprite.Group()

for satir_indeksi, satir in enumerate(seviye_haritasi):
    for sutun_indeksi, kutu_degeri in enumerate(satir):
        if kutu_degeri == 1:
            x_koordinati = sutun_indeksi * 32
            y_koordinati = satir_indeksi * 32
            
            yeni_duvar = Duvar(x_koordinati, y_koordinati)
            duvar_grubu.add(yeni_duvar)
            tum_spriteler.add(yeni_duvar)
        
        if kutu_degeri == 2:
            x_koordinati = (sutun_indeksi * 32)+12
            y_koordinati = (satir_indeksi * 32)+12
            
            yeni_yem = Yem(x_koordinati, y_koordinati)
            yem_grubu.add(yeni_yem)
            tum_spriteler.add(yeni_yem)
            
        if kutu_degeri == 3:
            x_koordinati = sutun_indeksi * 32
            y_koordinati = satir_indeksi * 32
            yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
            hayalet_grubu.add(yeni_hayalet)
            tum_spriteler.add(yeni_hayalet)
            
pacman = Player(928, 832)
tum_spriteler.add(pacman)

# 2. EKLEME: Ses Yöneticisini Başlatıyoruz
oyun_sesleri = SesYoneticisi() 

def main():
    calisiyor = True
    
    while calisiyor:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False

        # 3. EKLEME: oyun_sesleri parametresini update döngüsüne ekliyoruz
        tum_spriteler.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman, oyun_sesleri)
        
        ekran.fill((0, 0, 0)) 
        
        tum_spriteler.draw(ekran)

        pygame.display.flip()
        saat.tick(FPS)
        if len(hayalet_grubu) == 0:
            print("Tebrikler Oyuncu! Tüm hayaletleri avladın ve oyunu kazandın.")
            calisiyor = False  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()