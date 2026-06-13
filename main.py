import json
import pygame
from ghost import Hayalet
import sys
from player import Player  # Player sınıfını içeri aktar
from ses_yoneticisi import SesYoneticisi  

pygame.init()

# --- YENİ: YAZI TİPLERİ (Loading Ekranı İçin) ---
pygame.font.init()
font = pygame.font.SysFont('Arial', 74, bold=True)
kucuk_font = pygame.font.SysFont('Arial', 36)
# ------------------------------------------------

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Pac-Man Reverse")

TILE_SIZE = 40  # 1080p ekrana tam oturması için hücre boyutu 40'a çıkarıldı

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

# --- SES YÖNETİCİSİNİ BURADA BAŞLATIYORUZ ---
ses_yoneticisi = SesYoneticisi()

# --- YENİ EKLENEN KISIM: SEVİYE YÜKLEME FONKSİYONU ---
def seviye_yukle(seviye_no, pacman_nesnesi):
    # Eski seviyeden kalanları temizle
    tum_spriteler.empty()
    duvar_grubu.empty()
    yem_grubu.empty()
    hayalet_grubu.empty()

    dosya_adi = f"level{seviye_no}.json"
    
    # Yeni JSON dosyasını oku
    try:
        with open(dosya_adi, 'r') as file:
            data = json.load(file)
            seviye_haritasi = data['map']
    except FileNotFoundError:
        return False, None 

    # Yeni haritayı oluştur
    for satir_indeksi, satir in enumerate(seviye_haritasi):
        for sutun_indeksi, kutu_degeri in enumerate(satir):
            x_koordinati = sutun_indeksi * TILE_SIZE
            y_koordinati = satir_indeksi * TILE_SIZE
            
            if kutu_degeri == 1:
                yeni_duvar = Duvar(x_koordinati, y_koordinati)
                duvar_grubu.add(yeni_duvar)
                tum_spriteler.add(yeni_duvar)
            
            elif kutu_degeri == 0:
                yem_x = x_koordinati + 16
                yem_y = y_koordinati + 16
                yeni_yem = Yem(yem_x, yem_y)
                yem_grubu.add(yeni_yem)
                tum_spriteler.add(yeni_yem)
                
            elif kutu_degeri == 3:
                yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
                hayalet_grubu.add(yeni_hayalet)
                tum_spriteler.add(yeni_hayalet)

    # Pac-Man'i gruba ekle ve koordinatını sıfırla
    pacman_nesnesi.rect.x = 24 * TILE_SIZE
    pacman_nesnesi.rect.y = 22 * TILE_SIZE
    tum_spriteler.add(pacman_nesnesi)

    return True, seviye_haritasi
# -----------------------------------------------------

# --- YENİ EKLENEN KISIM: GEÇİŞ (LOADING) EKRANI ---
def gecis_ekrani_goster(seviye_no):
    ekran.fill((0, 0, 0)) # Siyah ekran
    
    mesaj = font.render(f"LEVEL {seviye_no}", True, (255, 255, 0)) # Sarı renk
    mesaj_rect = mesaj.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 50))
    ekran.blit(mesaj, mesaj_rect)
    
    alt_mesaj = kucuk_font.render("Hazirlan...", True, (255, 255, 255)) # Beyaz renk
    alt_mesaj_rect = alt_mesaj.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 50))
    ekran.blit(alt_mesaj, alt_mesaj_rect)
    
    pygame.display.flip()
    pygame.time.delay(2500) # 2.5 saniye bekle
# --------------------------------------------------

def main():
    calisiyor = True
    su_anki_seviye = 1
    
    # Oyun başlamadan önce Pac-Man nesnesini oluştur
    pacman = Player(0, 0) # Gerçek koordinatlar seviye_yukle içinde verilecek
    
    # OYUN BAŞLANGICI: İlk seviyeyi yükle
    gecis_ekrani_goster(su_anki_seviye)
    oyun_devam_ediyor_mu, anlik_harita = seviye_yukle(su_anki_seviye, pacman)
    
    if not oyun_devam_ediyor_mu:
        print("Hata: İlk bölüm (level1.json) bulunamadı! Lütfen dosya adını kontrol edin.")
        pygame.quit()
        sys.exit()

    while calisiyor:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
            # ESC tuşuna basıldığında oyundan çıkmak için:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    calisiyor = False

        # --- GÜNCELLEME (UPDATE) BÖLÜMÜ ---
        pacman.update(duvar_grubu, yem_grubu, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi)
        hayalet_grubu.update(duvar_grubu, yem_grubu, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi)
        
        ekran.fill((0, 0, 0)) 
        
        # ÇİZİM (DRAW)
        tum_spriteler.draw(ekran)

        # --- PANİK ÜNLEM İŞARETİ ÇİZİMİ ---
        for hayalet in hayalet_grubu:
            if hayalet.kacis_modu:
                unlem_x = hayalet.rect.x + (TILE_SIZE // 2) - 3
                unlem_y = hayalet.rect.y - 22

                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y, 6, 12))
                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y + 16, 6, 6))
        # ----------------------------------------

        pygame.display.flip()
        saat.tick(FPS)
        
        # --- SEVİYE GEÇİŞ / KAZANMA KONTROLÜ ---
        if len(hayalet_grubu) == 0:
            print(f"Harika! Level {su_anki_seviye} tamamlandı.")
            su_anki_seviye += 1
            
            gecis_ekrani_goster(su_anki_seviye)
            basarili_mi, yeni_harita = seviye_yukle(su_anki_seviye, pacman)
            
            if basarili_mi:
                anlik_harita = yeni_harita 
            else:
                print("TEBRİKLER OYUNCU! Tüm bölümleri tamamladın ve oyunu kazandın!")
                calisiyor = False
        
        # --- KAYBETME KONTROLÜ ---
        if len(yem_grubu) == 0:
            print("GAME OVER! Hayaletler tüm yemleri yedi ve haritayı temizledi.")
            calisiyor = False 


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()