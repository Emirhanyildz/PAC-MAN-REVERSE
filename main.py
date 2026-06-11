import json
import pygame
from ghost import Hayalet
import sys
from player import Player  # Player sınıfını içeri aktar
from ses_yoneticisi import SesYoneticisi  

pygame.init()

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Pac-Man Reverse")

# --- YENİ EKLENEN KISIM: JSON HARİTA YÜKLEME ---
TILE_SIZE = 40  # 1080p ekrana tam oturması için hücre boyutu 40'a çıkarıldı

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
        # Boyutlar TILE_SIZE (40x40) ile güncellendi
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 0, 255)) # Mavi renk
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

# Grupları burada tanımlıyoruz
tum_spriteler = pygame.sprite.Group()
duvar_grubu = pygame.sprite.Group()
yem_grubu = pygame.sprite.Group()
hayalet_grubu = pygame.sprite.Group()

# Harita listesini okuyup nesneleri oluşturuyoruz (Döngüden ÖNCE)
for satir_indeksi, satir in enumerate(seviye_haritasi):
    for sutun_indeksi, kutu_degeri in enumerate(satir):
        
        # Piksel koordinatları TILE_SIZE (40) ile hesaplanıyor
        x_koordinati = sutun_indeksi * TILE_SIZE
        y_koordinati = satir_indeksi * TILE_SIZE
        
        if kutu_degeri == 1:
            # 1 ise Duvar oluştur
            yeni_duvar = Duvar(x_koordinati, y_koordinati)
            duvar_grubu.add(yeni_duvar)
            tum_spriteler.add(yeni_duvar)
        
        elif kutu_degeri == 0:
            # 0 ise Yem oluştur (Yemlerin hücrenin ortasında durması için +16 piksel eklendi)
            yem_x = x_koordinati + 16
            yem_y = y_koordinati + 16
            yeni_yem = Yem(yem_x, yem_y)
            yem_grubu.add(yeni_yem)
            tum_spriteler.add(yeni_yem)
            
        elif kutu_degeri == 3:
            # 3 ise Hayalet doğma noktası (Kapı)
            yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
            hayalet_grubu.add(yeni_hayalet)
            tum_spriteler.add(yeni_hayalet)

# -------- HARİTA DÖNGÜSÜ BİTTİ --------

# Pac-Man'i yeni haritaya göre orta-alt güvenli bölgeye (Sütun 23, Satır 20) yerleştiriyoruz
pacman_baslangic_x = 24 * TILE_SIZE
pacman_baslangic_y = 22 * TILE_SIZE
pacman = Player(pacman_baslangic_x, pacman_baslangic_y)
tum_spriteler.add(pacman)

# --- SES YÖNETİCİSİNİ BURADA BAŞLATIYORUZ ---
ses_yoneticisi = SesYoneticisi()

def main():
    calisiyor = True
    
    while calisiyor:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
            # ESC tuşuna basıldığında oyundan çıkmak için:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    calisiyor = False

        # --- GÜNCELLEME (UPDATE) BÖLÜMÜ DÜZENLENDİ ---
        # Duvar ve yemlerin güncellenmeye ihtiyacı olmadığı için sadece hareketli nesneleri güncelliyoruz
        
        # 1. Pac-Man'i Güncelle
        pacman.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman, ses_yoneticisi)
        
        # 2. Hayaletleri Güncelle (Hayaletler de muhtemelen aynı parametrelere ihtiyaç duyuyor)
        hayalet_grubu.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman, ses_yoneticisi)
        # ---------------------------------------------
        
        ekran.fill((0, 0, 0)) 
        
        # ÇİZİM (DRAW)
        tum_spriteler.draw(ekran)

        # --- YENİ: PANİK ÜNLEM İŞARETİ ÇİZİMİ ---
        for hayalet in hayalet_grubu:
            if hayalet.kacis_modu:
                # Ünlemin X ekseninde karakterin tam ortasına hizalanması
                unlem_x = hayalet.rect.x + (TILE_SIZE // 2) - 3
                # Ünlemin Y ekseninde hayaletin kafasının biraz üstünde başlaması
                unlem_y = hayalet.rect.y - 22

                # Üstteki uzun çubuk (Sarı renk: 255, 255, 0)
                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y, 6, 12))
                # Alttaki küçük nokta (Sarı renk)
                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y + 16, 6, 6))
        # ----------------------------------------

        pygame.display.flip()
        saat.tick(FPS)
        
        # Kazanma Kontrolü
        if len(hayalet_grubu) == 0:
            print("Tebrikler Oyuncu! Tüm hayaletleri avladın ve oyunu kazandın.")
            calisiyor = False  # Döngüyü kır ve programı sonlandır

        # --- YENİ EKLENEN KISIM: KAYBETME KONTROLÜ ---
        # 2. Kaybetme Kontrolü (Hayaletler tüm yemleri bitirirse)
        if len(yem_grubu) == 0:
            print("GAME OVER! Hayaletler tüm yemleri yedi ve haritayı temizledi.")
            calisiyor = False  # Döngüyü kır ve programı sonlandır

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
