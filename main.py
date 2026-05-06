import pygame
from ghost import Hayalet
import sys
from player import Player  # 1. EKLEME: Player sınıfını içeri aktar

pygame.init()




saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Pac-Man Reverse")
# 60 Sütun x 33 Satır 1080p Harita (Kusursuz Simetri ve Bol Kaçış Yolu)
# 60 Sütun x 33 Satır Kusursuz 1080p Klasik Pac-Man Haritası
# Tüneller, kaçış yolları ve ortada kapısı açık gerçek bir hayalet kutusu var!
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
    "111111112110111111110011111111", # Hayalet kutusu üst duvarı ve kapısı (00)
    "122222222000100000000010000000", # Ortadaki uzun tünel koridoru
    "111111112110100033300010111111", # Hayaletlerin doğduğu yer (3)
    "100000012110111111111110111111", # Hayalet kutusu alt duvarı
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
# Simetriyi otomatik oluşturuyoruz (Aynalama yöntemi)
for sol in sol_yari:
    sag = sol[::-1] 
    harita_taslagi.append(sol + sag)

# Taslağı bilgisayarın okuyacağı sayısal matrise (listeye) çeviriyoruz
seviye_haritasi = []
for satir_metni in harita_taslagi:
    sayisal_satir = [int(karakter) for karakter in satir_metni]
    seviye_haritasi.append(sayisal_satir)


class Duvar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
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
        


# Duvarları ayrı tutacağımız bir grup oluşturuyoruz
# Grupları burada tanımlıyoruz
tum_spriteler = pygame.sprite.Group()
duvar_grubu = pygame.sprite.Group()
yem_grubu = pygame.sprite.Group()
hayalet_grubu = pygame.sprite.Group()

# Harita listesini okuyup Duvar nesnelerini oluşturuyoruz (Döngüden ÖNCE)
for satir_indeksi, satir in enumerate(seviye_haritasi):
    for sutun_indeksi, kutu_degeri in enumerate(satir):
        if kutu_degeri == 1:
            x_koordinati = sutun_indeksi * 32
            y_koordinati = satir_indeksi * 32
            
            # Pikselleri boyamak yerine, yeni bir Duvar nesnesi üretiyoruz
            yeni_duvar = Duvar(x_koordinati, y_koordinati)
            
            # Bu duvarı hem genel çizim grubuna hem de çarpışma grubuna ekliyoruz
            duvar_grubu.add(yeni_duvar)
            tum_spriteler.add(yeni_duvar)
        
        if kutu_degeri == 2:
            x_koordinati = (sutun_indeksi * 32)+12
            y_koordinati = (satir_indeksi * 32)+12
            
            # Pikselleri boyamak yerine, yeni bir Duvar nesnesi üretiyoruz
            yeni_yem = Yem(x_koordinati, y_koordinati)
            
            # Bu duvarı hem genel çizim grubuna hem de çarpışma grubuna ekliyoruz
            yem_grubu.add(yeni_yem)
            tum_spriteler.add(yeni_yem)
            
        if kutu_degeri == 3:
            x_koordinati = sutun_indeksi * 32
            y_koordinati = satir_indeksi * 32
            yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
            hayalet_grubu.add(yeni_hayalet)
            tum_spriteler.add(yeni_hayalet)
            
# -------- HARİTA DÖNGÜSÜ BİTTİ --------

# Pac-Man'i harita oluşturulduktan SONRA ekliyoruz ki en üst katmanda çizilsin!
pacman = Player(928, 832)
tum_spriteler.add(pacman)
            

def main():
    calisiyor = True
    
    while calisiyor:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False

        # 3. EKLEME: GÜNCELLEME (UPDATE)
        # Bu satır, gruptaki tüm nesnelerin (şu an sadece pacman var) update() metodunu çalıştırır.
        # Pac-Man'in update metoduna duvar_grubu'nu parametre olarak yolluyoruz
        # Eskiden 4 parametreydi, şimdi pacman'i de ekliyoruz
        tum_spriteler.update(duvar_grubu, yem_grubu, hayalet_grubu, seviye_haritasi, pacman)

        
        ekran.fill((0, 0, 0)) 
        
        # 4. EKLEME: ÇİZİM (DRAW)
        # Gruptaki tüm nesneleri ekrana, kendi rect(koordinat) konumlarına göre çizer.
        tum_spriteler.draw(ekran)

        pygame.display.flip()
        saat.tick(FPS)
        if len(hayalet_grubu) == 0:
            print("Tebrikler Oyuncu! Tüm hayaletleri avladın ve oyunu kazandın.")
            calisiyor = False  # Döngüyü kır ve programı sonlandır

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()