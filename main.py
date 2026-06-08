import json
import pygame
from ghost import Hayalet
import sys
<<<<<<< Updated upstream
from player import Player  
from ses_yoneticisi import SesYoneticisi  # 1. EKLEME: Ses yöneticisini içeri aktar
=======
from player import Player  # Player sınıfını içeri aktar
>>>>>>> Stashed changes

pygame.init()

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Pac-Man Reverse")
<<<<<<< Updated upstream

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
=======

# --- YENİ EKLENEN KISIM: JSON HARİTA YÜKLEME ---
TILE_SIZE = 40  # 1080p ekrana tam oturması için hücre boyutu 40'a çıkarıldı
>>>>>>> Stashed changes

# map.json dosyasını oku ve seviye_haritasi listesine aktar
try:
    with open('map.json', 'r') as file:
        data = json.load(file)
        seviye_haritasi = data['map']
except FileNotFoundError:
    print("Hata: 'map.json' dosyası bulunamadı! Lütfen dosyanın aynı dizinde olduğundan emin olun.")
    pygame.quit()
    sys.exit()
# -----------------------------------------------

class Duvar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
<<<<<<< Updated upstream
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 0, 255)) 
=======
        # Boyutlar TILE_SIZE (40x40) ile güncellendi
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 0, 255)) # Mavi renk
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        
=======

# Grupları burada tanımlıyoruz
>>>>>>> Stashed changes
tum_spriteler = pygame.sprite.Group()
duvar_grubu = pygame.sprite.Group()
yem_grubu = pygame.sprite.Group()
hayalet_grubu = pygame.sprite.Group()

<<<<<<< Updated upstream
=======
# Harita listesini okuyup nesneleri oluşturuyoruz (Döngüden ÖNCE)
>>>>>>> Stashed changes
for satir_indeksi, satir in enumerate(seviye_haritasi):
    for sutun_indeksi, kutu_degeri in enumerate(satir):
        
        # Piksel koordinatları TILE_SIZE (40) ile hesaplanıyor
        x_koordinati = sutun_indeksi * TILE_SIZE
        y_koordinati = satir_indeksi * TILE_SIZE
        
        if kutu_degeri == 1:
<<<<<<< Updated upstream
            x_koordinati = sutun_indeksi * 32
            y_koordinati = satir_indeksi * 32
            
=======
            # 1 ise Duvar oluştur
>>>>>>> Stashed changes
            yeni_duvar = Duvar(x_koordinati, y_koordinati)
            duvar_grubu.add(yeni_duvar)
            tum_spriteler.add(yeni_duvar)
        
<<<<<<< Updated upstream
        if kutu_degeri == 2:
            x_koordinati = (sutun_indeksi * 32)+12
            y_koordinati = (satir_indeksi * 32)+12
            
            yeni_yem = Yem(x_koordinati, y_koordinati)
=======
        elif kutu_degeri == 0:
            # 0 ise Yem oluştur (Yemlerin hücrenin ortasında durması için +16 piksel eklendi)
            yem_x = x_koordinati + 16
            yem_y = y_koordinati + 16
            yeni_yem = Yem(yem_x, yem_y)
>>>>>>> Stashed changes
            yem_grubu.add(yeni_yem)
            tum_spriteler.add(yeni_yem)
            
        elif kutu_degeri == 3:
            # 3 ise Hayalet doğma noktası (Kapı)
            yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
            hayalet_grubu.add(yeni_hayalet)
            tum_spriteler.add(yeni_hayalet)
<<<<<<< Updated upstream
            
pacman = Player(928, 832)
tum_spriteler.add(pacman)

# 2. EKLEME: Ses Yöneticisini Başlatıyoruz
oyun_sesleri = SesYoneticisi() 
=======

# -------- HARİTA DÖNGÜSÜ BİTTİ --------

# Pac-Man'i yeni haritaya göre orta-alt güvenli bölgeye (Sütun 23, Satır 20) yerleştiriyoruz
pacman_baslangic_x = 23 * TILE_SIZE
pacman_baslangic_y = 20 * TILE_SIZE
pacman = Player(pacman_baslangic_x, pacman_baslangic_y)
tum_spriteler.add(pacman)

>>>>>>> Stashed changes

def main():
    calisiyor = True
    
    while calisiyor:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False

<<<<<<< Updated upstream
        # 3. EKLEME: oyun_sesleri parametresini update döngüsüne ekliyoruz
        tum_spriteler.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman, oyun_sesleri)
        
        ekran.fill((0, 0, 0)) 
        
=======
        # GÜNCELLEME (UPDATE)
        # Gruptaki tüm nesnelerin (şu an sadece pacman var) update() metodunu çalıştırır.
        tum_spriteler.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman)
        
        ekran.fill((0, 0, 0)) 
        
        # ÇİZİM (DRAW)
        # Gruptaki tüm nesneleri ekrana çizer
>>>>>>> Stashed changes
        tum_spriteler.draw(ekran)

        pygame.display.flip()
        saat.tick(FPS)
        
        # Kazanma Kontrolü
        if len(hayalet_grubu) == 0:
            print("Tebrikler Oyuncu! Tüm hayaletleri avladın ve oyunu kazandın.")
            calisiyor = False  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()