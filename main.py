import json
import pygame
import os
import sys
import random 
from ghost import Hayalet
from player import Player
from ses_yoneticisi import SesYoneticisi  

pygame.init()

# --- YAZI TİPLERİ VE ARAYÜZ ---
pygame.font.init()
font = pygame.font.SysFont('Arial', 74, bold=True)
kucuk_font = pygame.font.SysFont('Arial', 36)

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Pac-Man Reverse")

TILE_SIZE = 40  

# --- PORTAL AYARLARI ---
PORTAL_RENK_1 = (0, 255, 255)
PORTAL_RENK_2 = (255, 0, 255)
TUNEL_SATIR_NO = 13

# --- MUTLAK DOSYA YOLU AYARI (Skorların güvenle kaydedilmesi için) ---
KLASOR_YOLU = os.path.dirname(os.path.abspath(__file__))
SKOR_DOSYASI = os.path.join(KLASOR_YOLU, "skorlar.json")

# =====================================================================
# SINIFLAR (SPRITES)
# =====================================================================

class Duvar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
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

class OzellikYemi(pygame.sprite.Sprite):
    def __init__(self, x, y, ozellik_turu):
        super().__init__()
        self.ozellik_turu = ozellik_turu 
        self.image = pygame.Surface((16, 16))
        
        if self.ozellik_turu == "CHRONOS":
            self.image.fill((0, 255, 0))     # Yeşil: Zaman Dondurma
        elif self.ozellik_turu == "PHASE":
            self.image.fill((255, 0, 255))   # Pembe/Mor: Duvar Geçişi
        elif self.ozellik_turu == "HIZ_ARTISI":
            self.image.fill((255, 128, 0))   # Turuncu: Hızlanma
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class YemKalkaniJoker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0)) # Fark edilmesi için Parlak Yeşil
        self.rect = self.image.get_rect()
        self.rect.centerx = x + (TILE_SIZE // 2)
        self.rect.centery = y + (TILE_SIZE // 2)

# =====================================================================
# GRUPLAR VE YÖNETİCİLER
# =====================================================================

tum_spriteler = pygame.sprite.Group()
duvar_grubu = pygame.sprite.Group()
yem_grubu = pygame.sprite.Group()
hayalet_grubu = pygame.sprite.Group()
ozellik_yemi_grubu = pygame.sprite.Group() 
joker_grubu = pygame.sprite.Group() 
sahte_bos_grup = pygame.sprite.Group() # Hayaletleri kandırmak için (Kalkan aktifken)

ses_yoneticisi = SesYoneticisi()

# =====================================================================
# SKOR TABLOSU FONKSİYONLARI
# =====================================================================

def isim_al_ekrani(puan):
    isim = ""
    bekliyor = True
    
    while bekliyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Isimsiz"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    if len(isim.strip()) == 0:
                        isim = "Oyuncu" 
                    return isim
                elif event.key == pygame.K_BACKSPACE: 
                    isim = isim[:-1]
                else:
                    if len(isim) < 12:
                        isim += event.unicode
        
        ekran.fill((0, 0, 0))
        baslik = font.render("SKORUNU KAYDET!", True, (255, 255, 0))
        ekran.blit(baslik, baslik.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 100)))
        
        alt_metin = kucuk_font.render(f"Puanin: {puan} - Adini Gir ve ENTER'a Bas:", True, (255, 255, 255))
        ekran.blit(alt_metin, alt_metin.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 20)))
        
        isim_metni = font.render(isim, True, (0, 255, 0))
        ekran.blit(isim_metni, isim_metni.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 50)))
        
        pygame.display.flip()

def skor_kaydet(isim, yeni_skor):
    skorlar = []
    if os.path.exists(SKOR_DOSYASI):
        try:
            with open(SKOR_DOSYASI, 'r', encoding='utf-8') as dosya_oku:
                okunan = json.load(dosya_oku)
                if isinstance(okunan, list):
                    for s in okunan:
                        if isinstance(s, dict) and "skor" in s and "isim" in s:
                            skorlar.append(s)
        except Exception as e:
            print(f"Skor okuma uyarisi: {e} (Dosya temizleniyor)")

    skorlar.append({"isim": isim, "skor": yeni_skor})
    skorlar.sort(key=lambda x: x["skor"], reverse=True) 
    skorlar = skorlar[:5]      
    
    try:
        with open(SKOR_DOSYASI, 'w', encoding='utf-8') as dosya_yaz:
            json.dump(skorlar, dosya_yaz, indent=4)
    except Exception as e:
        print(f"Skor kaydedilemedi: {e}")

def skor_tablosu_goster():
    skorlar = []
    if os.path.exists(SKOR_DOSYASI):
        try:
            with open(SKOR_DOSYASI, 'r', encoding='utf-8') as dosya_oku:
                skorlar = json.load(dosya_oku)
        except Exception as e:
            print(f"Skor okuma uyarısı: {e}")
            
    ekran.fill((0, 0, 0))
    baslik = font.render("EN IYI SKORLAR", True, (255, 255, 0))
    ekran.blit(baslik, baslik.get_rect(center=(GENISLIK // 2, 200)))
    
    y_pos = 350
    if not skorlar:
        metin = kucuk_font.render("Henuz kaydedilmis bir skor yok!", True, (255, 255, 255))
        ekran.blit(metin, metin.get_rect(center=(GENISLIK // 2, y_pos)))
    else:
        for i, veri in enumerate(skorlar):
            renk = (0, 255, 0) if i == 0 else (255, 255, 255)
            satir_metni = f"{i+1}. {veri['isim']} : {veri['skor']}"
            metin = kucuk_font.render(satir_metni, True, renk)
            ekran.blit(metin, metin.get_rect(center=(GENISLIK // 2, y_pos)))
            y_pos += 60
        
    cikis_metni = kucuk_font.render("Cikmak icin ESC tusuna basin...", True, (150, 150, 150))
    ekran.blit(cikis_metni, cikis_metni.get_rect(center=(GENISLIK // 2, YUKSEKLIK - 100)))
    pygame.display.flip()
    
    bekliyor = True
    while bekliyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                bekliyor = False

# =====================================================================
# YARDIMCI GÖRSEL VE SİSTEM FONKSİYONLARI
# =====================================================================

def seviye_yukle(seviye_no, pacman_nesnesi):
    tum_spriteler.empty()
    duvar_grubu.empty()
    yem_grubu.empty()
    hayalet_grubu.empty()
    ozellik_yemi_grubu.empty() 
    joker_grubu.empty()

    bos_yollar_listesi = [] 

    dosya_adi = f"level{seviye_no}.json"
    try:
        level_yolu = os.path.join(KLASOR_YOLU, dosya_adi)
        with open(level_yolu, 'r') as file:
            data = json.load(file)
            seviye_haritasi = data['map']
    except FileNotFoundError:
        return False, None, [] 

    buff_turleri = ["CHRONOS", "PHASE", "HIZ_ARTISI"]

    for satir_indeksi, satir in enumerate(seviye_haritasi):
        for sutun_indeksi, kutu_degeri in enumerate(satir):
            x_koordinati = sutun_indeksi * TILE_SIZE
            y_koordinati = satir_indeksi * TILE_SIZE
            
            if kutu_degeri == 1:
                yeni_duvar = Duvar(x_koordinati, y_koordinati)
                duvar_grubu.add(yeni_duvar)
                tum_spriteler.add(yeni_duvar)
            
            elif kutu_degeri == 0:
                bos_yollar_listesi.append((x_koordinati, y_koordinati))
                
                # %2 Şansla Özel Güç Yemi, değilse normal Yem
                if random.random() < 0.02: 
                    secilen_buff = random.choice(buff_turleri)
                    yeni_buff = OzellikYemi(x_koordinati + 12, y_koordinati + 12, secilen_buff)
                    ozellik_yemi_grubu.add(yeni_buff)
                    tum_spriteler.add(yeni_buff)
                else:
                    yeni_yem = Yem(x_koordinati + 16, y_koordinati + 16)
                    yem_grubu.add(yeni_yem)
                    tum_spriteler.add(yeni_yem)
                
            elif kutu_degeri == 3:
                yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
                hayalet_grubu.add(yeni_hayalet)
                tum_spriteler.add(yeni_hayalet)

    # Dinamik Pac-Man Başlangıç Noktası (Senin versiyonundaki en güvenli yöntem)
    max_satir = len(seviye_haritasi)
    max_sutun = len(seviye_haritasi[0])
    merkez_sutun = max_sutun // 2
    baslangic_bulundu = False
    
    for satir in range(max_satir - 2, 0, -1): 
        for ofset in range(merkez_sutun): 
            if seviye_haritasi[satir][merkez_sutun - ofset] == 0:
                pacman_nesnesi.rect.x = (merkez_sutun - ofset) * TILE_SIZE
                pacman_nesnesi.rect.y = satir * TILE_SIZE
                baslangic_bulundu = True
                break
            if merkez_sutun + ofset < max_sutun and seviye_haritasi[satir][merkez_sutun + ofset] == 0:
                pacman_nesnesi.rect.x = (merkez_sutun + ofset) * TILE_SIZE
                pacman_nesnesi.rect.y = satir * TILE_SIZE
                baslangic_bulundu = True
                break
        if baslangic_bulundu:
            break
            
    if not baslangic_bulundu: # B planı
        pacman_nesnesi.rect.x = 24 * TILE_SIZE
        pacman_nesnesi.rect.y = 22 * TILE_SIZE

    tum_spriteler.add(pacman_nesnesi)
    return True, seviye_haritasi, bos_yollar_listesi

def gecis_ekrani_goster(baslik, alt_metin, sure=2000):
    ekran.fill((0, 0, 0)) 
    mesaj = font.render(baslik, True, (255, 255, 0)) 
    mesaj_rect = mesaj.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 50))
    ekran.blit(mesaj, mesaj_rect)
    
    alt_mesaj = kucuk_font.render(alt_metin, True, (255, 255, 255)) 
    alt_mesaj_rect = alt_mesaj.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 50))
    ekran.blit(alt_mesaj, alt_mesaj_rect)
    
    pygame.display.flip()
    pygame.time.delay(sure) 

def draw_portal_visuals(screen):
    pulse = (pygame.time.get_ticks() // 200) % 2
    guncel_renk = PORTAL_RENK_1 if pulse == 0 else PORTAL_RENK_2
    tunel_y_piksel = TUNEL_SATIR_NO * TILE_SIZE
    
    sol_portal_rect = pygame.Rect(0, tunel_y_piksel, 8, TILE_SIZE) 
    pygame.draw.rect(screen, guncel_renk, sol_portal_rect)
    pygame.draw.circle(screen, guncel_renk, (15, tunel_y_piksel + 10), 4)
    pygame.draw.circle(screen, guncel_renk, (15, tunel_y_piksel + 30), 4)
    
    sag_portal_rect = pygame.Rect(GENISLIK - 8, tunel_y_piksel, 8, TILE_SIZE) 
    pygame.draw.rect(screen, guncel_renk, sag_portal_rect)
    pygame.draw.circle(screen, guncel_renk, (GENISLIK - 15, tunel_y_piksel + 10), 4)
    pygame.draw.circle(screen, guncel_renk, (GENISLIK - 15, tunel_y_piksel + 30), 4)

# =====================================================================
# ANA OYUN DÖNGÜSÜ
# =====================================================================

def main():
    calisiyor = True
    su_anki_seviye = 1
    
    # Senin Sistem: Can, Puan ve Süre Değişkenleri
    puan = 0
    can = su_anki_seviye
    kalan_sure = 180 
    frame_sayaci = 0
    
    pacman = Player(0, 0) 
    
    # Takım Arkadaşı 1: Özellik/Buff Değişkenleri
    aktif_ozellik = None      
    ozellik_sayaci = 0        

    gecis_ekrani_goster(f"LEVEL {su_anki_seviye}", "Hazirlan...", 2500)
    oyun_devam_ediyor_mu, anlik_harita, bos_yollar = seviye_yukle(su_anki_seviye, pacman)
    
    if not oyun_devam_ediyor_mu:
        print("Hata: Ilk bolum (level1.json) bulunamadi!")
        pygame.quit()
        sys.exit()

    # Takım Arkadaşı 2: Joker & Kalkan Değişkenleri
    joker_sahnedemi = False
    son_joker_dogma_zamani = pygame.time.get_ticks()
    joker_dogma_suresi = 15000  
    joker_kalma_suresi = 7000   
    kalkan_aktif = False
    kalkan_bitis_zamani = 0
    kalkan_suresi = 5000 

    while calisiyor:
        su_anki_zaman = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    calisiyor = False

        # --- SÜRE VE PUAN GÜNCELLEMESİ ---
        frame_sayaci += 1
        if frame_sayaci >= FPS: 
            frame_sayaci = 0
            if kalan_sure > 0:
                kalan_sure -= 1
                puan = max(0, puan - 10) # Her saniye 10 puan azalır

        # --- JOKER ÇIKARMA (SPAWN) MANTIĞI ---
        if not joker_sahnedemi and (su_anki_zaman - son_joker_dogma_zamani > joker_dogma_suresi):
            if bos_yollar: 
                secilen_koordinat = random.choice(bos_yollar)
                yeni_joker = YemKalkaniJoker(secilen_koordinat[0], secilen_koordinat[1])
                joker_grubu.add(yeni_joker)
                tum_spriteler.add(yeni_joker)
                joker_sahnedemi = True
                son_joker_dogma_zamani = su_anki_zaman 

        elif joker_sahnedemi and (su_anki_zaman - son_joker_dogma_zamani > joker_kalma_suresi):
            for j in joker_grubu:
                j.kill()
            joker_sahnedemi = False
            son_joker_dogma_zamani = su_anki_zaman 
            
        if pygame.sprite.spritecollide(pacman, joker_grubu, True):
            joker_sahnedemi = False
            son_joker_dogma_zamani = su_anki_zaman
            kalkan_aktif = True
            kalkan_bitis_zamani = su_anki_zaman + kalkan_suresi

        if kalkan_aktif and su_anki_zaman > kalkan_bitis_zamani:
            kalkan_aktif = False

        # --- ÖZELLİK/BUFF KONTROLÜ ---
        if aktif_ozellik is not None:
            if ozellik_sayaci > 0:
                ozellik_sayaci -= 1
            if ozellik_sayaci <= 0:
                if aktif_ozellik == "PHASE":
                    duvara_degiyor_mu = pygame.sprite.spritecollideany(pacman, duvar_grubu)
                    if not duvara_degiyor_mu:
                        aktif_ozellik = None
                else:
                    aktif_ozellik = None
        
        toplanan_bufflar = pygame.sprite.spritecollide(pacman, ozellik_yemi_grubu, True)
        for buff in toplanan_bufflar:
            if aktif_ozellik is None: 
                aktif_ozellik = buff.ozellik_turu
                if aktif_ozellik == "CHRONOS": ozellik_sayaci = 180  
                elif aktif_ozellik == "PHASE": ozellik_sayaci = 240  
                elif aktif_ozellik == "HIZ_ARTISI": ozellik_sayaci = 300  

        # --- KARAKTER GÜNCELLEMELERİ ---
        onceki_hayalet_sayisi = len(hayalet_grubu)

        # Karakter ve hayalet güncellemeleri (Buff değişkeni son parametre olarak gönderilir)
        pacman.update(duvar_grubu, yem_grubu, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi, aktif_ozellik)
        
        # Kalkan aktifse hayaletler yemleri görmezden gelir (sahte boş gruba odaklanırlar)
        hedef_yemler = sahte_bos_grup if kalkan_aktif else yem_grubu
        hayalet_grubu.update(duvar_grubu, hedef_yemler, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi, aktif_ozellik)
        
        guncel_hayalet_sayisi = len(hayalet_grubu)
        if guncel_hayalet_sayisi < onceki_hayalet_sayisi:
            avlanan_hayalet_sayisi = onceki_hayalet_sayisi - guncel_hayalet_sayisi
            puan += (avlanan_hayalet_sayisi * 1000) 

        # --- ÇİZİM EKRANI ---
        ekran.fill((0, 0, 0)) 
        tum_spriteler.draw(ekran)
        draw_portal_visuals(ekran)

        for hayalet in hayalet_grubu:
            if hayalet.kacis_modu:
                unlem_x = hayalet.rect.x + (TILE_SIZE // 2) - 3
                unlem_y = hayalet.rect.y - 22
                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y, 6, 12))
                pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y + 16, 6, 6))

        if kalkan_aktif:
            pygame.draw.circle(ekran, (0, 255, 0), pacman.rect.center, 25, 3)

        # Üst Bilgi Barı Çizimi (Senin Tasarımın)
        puan_metni = kucuk_font.render(f"Puan: {puan}", True, (255, 255, 255))
        sure_metni = kucuk_font.render(f"Sure: {kalan_sure}", True, (255, 255, 255))
        can_metni = kucuk_font.render(f"Can: {can}", True, (255, 0, 0))
        ekran.blit(puan_metni, (20, 20))
        ekran.blit(sure_metni, (GENISLIK // 2 - 50, 20))
        ekran.blit(can_metni, (GENISLIK - 120, 20))

        pygame.display.flip()
        saat.tick(FPS)
        
        # --- BÖLÜM GEÇME / KAZANMA KONTROLÜ ---
        if guncel_hayalet_sayisi == 0:
            puan += (kalan_sure * 10) 
            aktif_ozellik = None
            ozellik_sayaci = 0
            
            if su_anki_seviye == 3:
                oyuncu_ismi = isim_al_ekrani(puan)
                skor_kaydet(oyuncu_ismi, puan) 
                gecis_ekrani_goster("TEBRIKLER!", f"Oyunu Kazandin! Toplam Puan: {puan}")
                skor_tablosu_goster() 
                calisiyor = False
            else:
                su_anki_seviye += 1
                can = su_anki_seviye  
                kalan_sure = 180  
                kalkan_aktif = False 
                
                gecis_ekrani_goster(f"LEVEL {su_anki_seviye}", "Hazirlan...", 2500)
                basarili_mi, yeni_harita, yeni_bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                
                if basarili_mi:
                    anlik_harita = yeni_harita 
                    bos_yollar = yeni_bos_yollar
                else:
                    skor_kaydet("Bilinmeyen", puan)
                    gecis_ekrani_goster("TEBRIKLER!", f"Oyunu Kazandin! Toplam Puan: {puan}")
                    skor_tablosu_goster()
                    calisiyor = False
        
        # --- CAN KAYBETME / GAME OVER KONTROLÜ ---
        elif calisiyor and (len(yem_grubu) == 0 or kalan_sure <= 0):
            can -= 1
            aktif_ozellik = None
            kalkan_aktif = False
            
            if can > 0:
                gecis_ekrani_goster("DIKKAT!", f"Kalan Can: {can}")
                basarili_mi, _, yeni_bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                if basarili_mi:
                    bos_yollar = yeni_bos_yollar
                kalan_sure = 180  
            else:
                oyuncu_ismi = isim_al_ekrani(puan)
                skor_kaydet(oyuncu_ismi, puan) 
                gecis_ekrani_goster("GAME OVER!", f"Skorun: {puan}")
                skor_tablosu_goster() 
                calisiyor = False 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()