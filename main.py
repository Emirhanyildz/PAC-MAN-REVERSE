import json
import pygame
import os
import sys
import random 
import math 
from ghost import Hayalet
from player import Player
from ses_yoneticisi import SesYoneticisi  

pygame.init()

KLASOR_YOLU = os.path.dirname(os.path.abspath(__file__))
SKOR_DOSYASI = os.path.join(KLASOR_YOLU, "oyuncu_skorlari.json") 

pygame.font.init()

font_yolu = os.path.join(KLASOR_YOLU, "joystixmonospace.otf")

try:
    font = pygame.font.Font(font_yolu, 74)
    kucuk_font = pygame.font.Font(font_yolu, 36)
except FileNotFoundError:
    print("HATA: Font dosyasi bulunamadi! Arial'e dönülüyor.")
    font = pygame.font.SysFont('Arial', 74, bold=True)
    kucuk_font = pygame.font.SysFont('Arial', 36)

saat = pygame.time.Clock()
FPS = 60

GENISLIK, YUKSEKLIK = 1920, 1080
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Pac-Man Reverse")

TILE_SIZE = 40  

PORTAL_RENK_1 = (0, 255, 255)
PORTAL_RENK_2 = (255, 0, 255)
TUNEL_SATIR_NO = 13

# Buff / Debuff kümeleri (global sabitler)
DEBUFF_TURLERI = {"YAVASLA", "KORUL", "TERS", "KAC"}
BUFF_TURLERI   = {"CHRONOS", "PHASE", "HIZ_ARTISI"}
DEBUFF_SURESI  = 300  # 5 saniye @ 60 FPS

# =====================================================================
# GÖRSELLERİN YÜKLENMESİ
# =====================================================================
def gorsel_yukle(dosya_adi):
    yol = os.path.join(KLASOR_YOLU, "gorseller", "ekranlar", dosya_adi)
    try:
        # --- PERFORMANS ÇÖZÜMÜ: .convert_alpha() EKLENDİ ---
        gorsel = pygame.image.load(yol).convert_alpha()
        return pygame.transform.scale(gorsel, (GENISLIK, YUKSEKLIK))
    except pygame.error as e:
        print(f"HATA: {dosya_adi} yuklenemedi! - {e}")
        yuzey = pygame.Surface((GENISLIK, YUKSEKLIK))
        yuzey.fill((0, 0, 0))
        return yuzey
    
def ikon_yukle(dosya_adi, boyut=(120, 120)):
    yol1 = os.path.join(KLASOR_YOLU, "gorseller","simgeler", dosya_adi)
    yol2 = os.path.join(KLASOR_YOLU, dosya_adi)
    
    for yol in [yol1, yol2]:
        if os.path.exists(yol):
            gorsel = pygame.image.load(yol).convert_alpha()
            with pygame.PixelArray(gorsel) as px_array:
                gen, yuk = gorsel.get_size()
                for x in range(gen):
                    for y in range(yuk):
                        r, g, b, a = gorsel.unmap_rgb(px_array[x, y])
                        if a < 255: px_array[x, y] = (0, 0, 0, 0)
            return pygame.transform.scale(gorsel, boyut)
    
    print(f"HATA: İkon bulunamadı -> {dosya_adi}")
    return pygame.Surface(boyut, pygame.SRCALPHA)

def kopru_yukle(dosya_adi, kare_sayisi=3, scale_carpani=1.3):
    yol1 = os.path.join(KLASOR_YOLU, "gorseller", "simgeler", dosya_adi)
    gorsel = None
    for yol in [yol1]:
        if os.path.exists(yol):
            gorsel = pygame.image.load(yol).convert_alpha()
            # --- YİNE NEON SİLİCİ DEVREDE --- 
            # Orijinal pixel art netliğini bozmamak için yarı saydamlıkları siliyoruz
            with pygame.PixelArray(gorsel) as px_array:
                gen, yuk = gorsel.get_size()
                for x in range(gen):
                    for y in range(yuk):
                        r, g, b, a = gorsel.unmap_rgb(px_array[x, y])
                        if a < 255: px_array[x, y] = (0, 0, 0, 0)
            break
            
    if gorsel is None:
        print(f"HATA: Köprü bulunamadı -> {dosya_adi}")
        return [pygame.Surface((80, 80), pygame.SRCALPHA) for _ in range(kare_sayisi)]
        
    gen, yuk = gorsel.get_size()
    kare_gen = gen // kare_sayisi # Resmi 3 eşit parçaya (frame) bölüyoruz
    kareler = []
    
    for i in range(kare_sayisi):
        kare = gorsel.subsurface(pygame.Rect(i * kare_gen, 0, kare_gen, yuk))
        # Köprüler çok küçük kalmasın diye "scale_carpani" ile boyutlandırıyoruz (Şu an 2 katı)
        kare = pygame.transform.scale(kare, (kare_gen * scale_carpani, yuk * scale_carpani))
        kareler.append(kare)
        
    return kareler

# OYUN BAŞLARKEN İKİ KÖPRÜYÜ DE HAFIZAYA (RAM) 3 KARE OLARAK ÇEKİYORUZ
img_kopru_l = kopru_yukle("isikli_kopru_l.png")
img_kopru_r = kopru_yukle("isikli_kopru_r.png")

img_ses_acik = ikon_yukle("ses_acik.png", (160, 160))
img_ses_kapali = ikon_yukle("ses_kapalı.png", (160, 160))

img_menu = gorsel_yukle("ana_menu.png")
img_arkaplan = gorsel_yukle("arkaplan.png")  # Bu zaten var, dokunma

# YENİ: Seviyeye özel arkaplanlar
img_arkaplan_listesi = {
    1: gorsel_yukle("level_1_arkaplan.png"),
    2: gorsel_yukle("level_2_arkaplan.png"),
    3: gorsel_yukle("level_3_arkaplan.png")
}
img_ayarlar = gorsel_yukle("ayarlar.png")
img_kaybettin = gorsel_yukle("kaybettin.png")
img_kazandin = gorsel_yukle("kazandin.png")
img_puan_tablosu = gorsel_yukle("puan_tablosu.png")
img_skor_kaydet = gorsel_yukle("puan_kaydet.png")
img_karakter_sec = gorsel_yukle("pacman_sec_menu.png") 
img_durduruldu=gorsel_yukle("durduruldu.png")
img_level_gecisler = {
    1: gorsel_yukle("level_1_gecis.png"),
    2: gorsel_yukle("level_2_gecis.png"),
    3: gorsel_yukle("level_3_gecis.png")
}


# =====================================================================
# SINIFLAR (SPRITES)
# =====================================================================

# --- YENİ: DUVAR RESMİ YÜKLEME (Yol güncellendi) ---


class Duvar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Tamamen şeffaf — arka plan görseli duvarları zaten çiziyor
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




# =====================================================================
# SINIFLAR (SPRITES)
# =====================================================================






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
        
        # --- ÖZEL TASARIM: Sadece "KAÇ" debuff'ı devasa ve kırmızı olur ---
        if self.ozellik_turu == "KAC":
            self.image = pygame.Surface((28, 28)) # Standart 16'ya göre dev gibi (28x28)
            self.image.fill((255, 0, 0))          # Uyarıcı saf kırmızı renk
            
            self.rect = self.image.get_rect()
            # Yemin oyun ızgarasından (40x40) taşmaması ve tam ortaya oturması için merkezliyoruz
            self.rect.centerx = x + 8
            self.rect.centery = y + 8
            
        # --- DİĞER YEMLER: Standart boyut ve gizli renkler ---
        else:
            self.image = pygame.Surface((16, 16)) 
            
            if self.ozellik_turu in ("CHRONOS", "YAVASLA"):
                self.image.fill((0, 255, 0))        # Yeşil
            elif self.ozellik_turu in ("PHASE", "KORUL"):
                self.image.fill((255, 0, 255))      # Mor
            elif self.ozellik_turu in ("HIZ_ARTISI", "TERS"):
                self.image.fill((255, 128, 0))      # Turuncu
                
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

class YemKalkaniJoker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0)) 
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
sahte_bos_grup = pygame.sprite.Group() 

ses_yoneticisi = SesYoneticisi()

# =====================================================================
# YARDIMCI FONKSİYON: TÜM GRUPLARI TEMİZLE
# =====================================================================

def gruplari_temizle():
    tum_spriteler.empty()
    duvar_grubu.empty()
    yem_grubu.empty()
    hayalet_grubu.empty()
    ozellik_yemi_grubu.empty()
    joker_grubu.empty()

# =====================================================================
# SKOR TABLOSU FONKSİYONLARI
# =====================================================================

def isim_al_ekrani(puan, arkaplan_gorseli):
    isim = ""
    bekliyor = True

    puan_koordinat = (1200, 415)  
    isim_koordinat = (1200, 655)  
    btn_kaydet = pygame.Rect(735, 905, 450, 100) 
    son_hover = False

    while bekliyor:
        fare_pos = pygame.mouse.get_pos()
        
        su_anki_hover = btn_kaydet.collidepoint(fare_pos)
        if su_anki_hover and not son_hover:
            ses_yoneticisi.hover_sesi_cal()
        son_hover = su_anki_hover

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
                    if len(isim) < 12 and event.unicode.isalnum():
                        isim += event.unicode
                        
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if btn_kaydet.collidepoint(fare_pos):
                    ses_yoneticisi.secme_sesi_cal()
                    if len(isim.strip()) == 0:
                        isim = "Oyuncu"
                    return isim

        ekran.fill((0, 0, 0))
        ekran.blit(img_skor_kaydet, (0, 0))
        
        puan_metni = font.render(str(puan), True, (255, 255, 255))
        ekran.blit(puan_metni, puan_metni.get_rect(center=puan_koordinat))
        
        isim_metni = font.render(isim.upper(), True, (255, 255, 0))
        ekran.blit(isim_metni, isim_metni.get_rect(center=isim_koordinat))

        pygame.display.flip()
        saat.tick(FPS)

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
            print(f"Skor okuma uyarisi: {e}")

    skorlar.append({"isim": isim, "skor": yeni_skor})
    skorlar.sort(key=lambda x: x["skor"], reverse=True) 
    skorlar = skorlar[:3]      
    
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
            
    btn_skor_menu = pygame.Rect(GENISLIK // 2 - 235, 910, 470, 100)
    son_hover = False
            
    bekliyor = True
    while bekliyor:
        fare_pos = pygame.mouse.get_pos()
        
        su_anki_hover = btn_skor_menu.collidepoint(fare_pos)
        if su_anki_hover and not son_hover:
            ses_yoneticisi.hover_sesi_cal()
        son_hover = su_anki_hover

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                    ses_yoneticisi.secme_sesi_cal()
                    bekliyor = False
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if btn_skor_menu.collidepoint(fare_pos):
                    ses_yoneticisi.secme_sesi_cal()
                    bekliyor = False

        ekran.fill((0, 0, 0))
        ekran.blit(img_puan_tablosu, (0, 0))
        
        y_koordinatlari = [415, 593, 775] 
        x_merkez = GENISLIK // 2 + 20
        
        if not skorlar:
            metin = kucuk_font.render("Henuz kaydedilmis bir skor yok!", True, (255, 255, 255))
            ekran.blit(metin, metin.get_rect(center=(x_merkez, y_koordinatlari[0])))
        else:
            for i, veri in enumerate(skorlar[:3]):
                renk = (255, 255, 0) if i == 0 else (255, 255, 255)
                satir_metni = f"{veri['isim'].upper()} : {veri['skor']}"
                metin = kucuk_font.render(satir_metni, True, renk)
                y_pos = y_koordinatlari[i]
                ekran.blit(metin, metin.get_rect(center=(x_merkez, y_pos)))
        
        pygame.display.flip()
        saat.tick(FPS)

# =====================================================================
# SİSTEM FONKSİYONLARI (GÜNCELLENMİŞ SEVİYE YÜKLEME)
# =====================================================================

def seviye_yukle(seviye_no, pacman_nesnesi):
    gruplari_temizle()

    bos_yollar_listesi = [] 

    dosya_adi = f"level{seviye_no}.json"
    try:
        level_yolu = os.path.join(KLASOR_YOLU, dosya_adi)
        with open(level_yolu, 'r') as file:
            data = json.load(file)
            seviye_haritasi = data['map']
    except FileNotFoundError:
        return False, None, [] 

    # --- DENGELEME ADIMI ---
    # Özellikleri avantaj ve dezavantaj olarak ikiye ayırıyoruz
    buff_havuzu = ["CHRONOS", "PHASE", "HIZ_ARTISI"]
    debuff_havuzu = ["YAVASLA", "KORUL", "TERS", "KAC"]

    for satir_indeksi, satir in enumerate(seviye_haritasi):
        for sutun_indeksi, kutu_degeri in enumerate(satir):
            x_koordinati = sutun_indeksi * TILE_SIZE
            y_koordinati = satir_indeksi * TILE_SIZE
            if kutu_degeri == 1:
                yeni_duvar = Duvar(x_koordinati, y_koordinati)
                duvar_grubu.add(yeni_duvar)
                tum_spriteler.add(yeni_duvar)
            
            # İŞTE SİLİNEN VE YEMLERİ OLUŞTURAN ASIL BLOK BURASI!
            elif kutu_degeri == 0:
                bos_yollar_listesi.append((x_koordinati, y_koordinati))
                
                # Toplam özel yem çıkma ihtimali %2 olarak kalıyor
                if random.random() < 0.02: 
                    # %75 ihtimalle iyi bir şey (Buff), %25 ihtimalle kötü bir şey (Debuff) gelsin
                    if random.random() < 0.75:
                        secilen_tur = random.choice(buff_havuzu)
                    else:
                        secilen_tur = random.choice(debuff_havuzu)
                        
                    yeni_yem = OzellikYemi(x_koordinati + 12, y_koordinati + 12, secilen_tur)
                    ozellik_yemi_grubu.add(yeni_yem)
                    tum_spriteler.add(yeni_yem)
                else:
                    yeni_yem = Yem(x_koordinati + 16, y_koordinati + 16)
                    yem_grubu.add(yeni_yem)
                    tum_spriteler.add(yeni_yem)
                
            # HAYALETLERİN VE KOSTÜMLERİN OLUŞTURULDUĞU BLOK
            elif kutu_degeri == 3:
                secilen_kostum = "klasik"
                
                if hasattr(pacman_nesnesi, 'hayalet_kostumu'):
                    if pacman_nesnesi.hayalet_kostumu == "imam_packman":
                        secilen_kostum = "gul_ghost"
                    elif pacman_nesnesi.hayalet_kostumu == "fesli_pacman":
                        secilen_kostum = "hacli_ghost"
                
                yeni_hayalet = Hayalet(x_koordinati, y_koordinati, hayalet_kostumu=secilen_kostum)
                hayalet_grubu.add(yeni_hayalet)
                tum_spriteler.add(yeni_hayalet)
                
                # Toplam özel yem çıkma ihtimali %2 olarak kalıyor
                if random.random() < 0.02: 
                    # %75 ihtimalle iyi bir şey (Buff), %25 ihtimalle kötü bir şey (Debuff) gelsin
                    if random.random() < 0.75:
                        secilen_tur = random.choice(buff_havuzu)
                    else:
                        secilen_tur = random.choice(debuff_havuzu)
                        
                    yeni_yem = OzellikYemi(x_koordinati + 12, y_koordinati + 12, secilen_tur)
                    ozellik_yemi_grubu.add(yeni_yem)
                    tum_spriteler.add(yeni_yem)
                else:
                    yeni_yem = Yem(x_koordinati + 16, y_koordinati + 16)
                    yem_grubu.add(yeni_yem)
                    tum_spriteler.add(yeni_yem)
                
            elif kutu_degeri == 3:
                yeni_hayalet = Hayalet(x_koordinati, y_koordinati)
                hayalet_grubu.add(yeni_hayalet)
                tum_spriteler.add(yeni_hayalet)

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
            
    if not baslangic_bulundu: 
        pacman_nesnesi.rect.x = 24 * TILE_SIZE
        pacman_nesnesi.rect.y = 22 * TILE_SIZE

    tum_spriteler.add(pacman_nesnesi)
    return True, seviye_haritasi, bos_yollar_listesi

def gecis_ekrani_goster(seviye_no, sure=2500):
    ekran.fill((0, 0, 0))
    if seviye_no in img_level_gecisler:
        ekran.blit(img_level_gecisler[seviye_no], (0, 0))
    pygame.display.flip()
    pygame.time.delay(sure)

def draw_portal_visuals(screen, seviye_no):
    pulse = (pygame.time.get_ticks() // 200) % 3
    y_merkez = (TUNEL_SATIR_NO * TILE_SIZE) + (TILE_SIZE // 2)
    
    y_kaydirma = 29 
    
    if seviye_no == 3:
        x_kaydirma_sol = -95
        x_kaydirma_sag = -95
    else:
        x_kaydirma_sol = -15 
        x_kaydirma_sag = -15 
    
    frame_l = img_kopru_r[pulse]
    frame_r = img_kopru_l[pulse]
    
    rect_l = frame_r.get_rect(midleft=(0 + x_kaydirma_sol, y_merkez - y_kaydirma))
    rect_r = frame_l.get_rect(midright=(GENISLIK - x_kaydirma_sag, y_merkez - y_kaydirma))
    
    screen.blit(frame_l, rect_l)
    screen.blit(frame_r, rect_r)
    
    

# =====================================================================
# ANA DÖNGÜ
# =====================================================================

def main():
    durum = "MENU"
    onceki_durum="MENU"
    calisiyor = True
    
    su_anki_seviye = 1
    puan = 0
    kalan_sure = 180 
    frame_sayaci = 0
    
    pacman = Player(0, 0) 
    aktif_ozellik = None
    ozellik_sayaci = 0

    aktif_debuff = None
    debuff_sayaci = 0

    joker_sahnedemi = False
    son_joker_dogma_zamani = pygame.time.get_ticks()
    joker_dogma_suresi = 15000  
    joker_kalma_suresi = 7000    
    kalkan_aktif = False
    kalkan_bitis_zamani = 0
    kalkan_suresi = 5000 

    son_hover_edilen_buton = None

    anlik_harita = None
    bos_yollar = []

    btn_oyna = pygame.Rect(GENISLIK // 2 - 235, 560, 470, 80)       
    btn_skorlar = pygame.Rect(GENISLIK // 2 - 235, 678, 470, 80)    
    btn_ayarlar = pygame.Rect(GENISLIK // 2 - 235, 800, 470, 80)    
    btn_cikis = pygame.Rect(GENISLIK // 2 - 235, 920, 470, 80)      

    btn_go_yeni_oyun = pygame.Rect(GENISLIK // 2 - 235, 790, 470, 100)
    btn_go_ana_menu = pygame.Rect(GENISLIK // 2 - 235, 910, 470, 100)
    
    # --- EKSİK OLAN SEÇİM BUTONLARI EKLENDİ ---
    btn_sec_klasik = pygame.Rect(400, 580, 220, 220)
    btn_sec_fesli   = pygame.Rect(850, 580, 220, 220)
    btn_sec_imam    = pygame.Rect(1295, 580, 220, 220)

    gruplari_temizle()

    while calisiyor:
        su_anki_zaman = pygame.time.get_ticks()
        fare_pos = pygame.mouse.get_pos()
        
        # -----------------------------------------------------------------
        # DURUM 1: ANA MENÜ
        # -----------------------------------------------------------------
        if durum == "MENU":
            gruplari_temizle()
            ses_yoneticisi.tema_muzigi_cal()

            ekran.fill((0, 0, 0))
            ekran.blit(img_menu, (0, 0))

            su_anki_buton = None
            if btn_oyna.collidepoint(fare_pos): su_anki_buton = "OYNA"
            elif btn_skorlar.collidepoint(fare_pos): su_anki_buton = "SKORLAR"
            elif btn_ayarlar.collidepoint(fare_pos): su_anki_buton = "AYARLAR"
            elif btn_cikis.collidepoint(fare_pos): su_anki_buton = "CIKIS"

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:  
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # --- DÜZELTİLDİ: OYNA'YA BASINCA ARTIK CHAR_SELECT'E GİDER ---
                    if btn_oyna.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()  
                        durum = "CHAR_SELECT" 
                        break 
                    
                    elif btn_skorlar.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()  
                        skor_tablosu_goster()
                        break
                    
                    elif btn_ayarlar.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()  
                        durum = "SETTINGS"
                        break
                    
                    elif btn_cikis.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()  
                        calisiyor = False
                        break

        # -----------------------------------------------------------------
        # DURUM 1.5: KARAKTER SEÇİM EKRANI (TAM OLMASI GEREKEN YERDE)
        # -----------------------------------------------------------------
        elif durum == "CHAR_SELECT":
            ekran.fill((0, 0, 0)) 
            ekran.blit(img_karakter_sec, (0, 0))
            
            su_anki_buton = None
            
            # Neon çerçeve
            if btn_sec_klasik.collidepoint(fare_pos):
                su_anki_buton = "KLASIK"
                pygame.draw.rect(ekran, (0, 255, 255), btn_sec_klasik, 5, border_radius=25)
            elif btn_sec_fesli.collidepoint(fare_pos):
                su_anki_buton = "FESLI"
                pygame.draw.rect(ekran, (0, 255, 255), btn_sec_fesli, 5, border_radius=25)
            elif btn_sec_imam.collidepoint(fare_pos):
                su_anki_buton = "IMAM"
                pygame.draw.rect(ekran, (0, 255, 255), btn_sec_imam, 5, border_radius=25)

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT: calisiyor = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                    ses_yoneticisi.secme_sesi_cal()
                    durum = "MENU"
                
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    secim_yapildi = False
                    
                    if btn_sec_klasik.collidepoint(fare_pos):
                        secilen_karakter_adi = "klasik"
                        secim_yapildi = True
                    elif btn_sec_fesli.collidepoint(fare_pos):
                        secilen_karakter_adi = "fesli_pacman"
                        secim_yapildi = True
                    elif btn_sec_imam.collidepoint(fare_pos):
                        secilen_karakter_adi = "imam_packman"
                        secim_yapildi = True

                    if secim_yapildi:
                        ses_yoneticisi.secme_sesi_cal()
                        ses_yoneticisi.tema_muzigi_durdur()
                        
                        su_anki_seviye = 1
                        puan = 0
                        kalan_sure = 180
                        aktif_ozellik = None
                        aktif_debuff = None
                        debuff_sayaci = 0
                        kalkan_aktif = False
                        
                        pacman = Player(0, 0, secilen_karakter_adi)
                        pacman.hipnoz_aktif = False
                        pacman.hayalet_kostumu = secilen_karakter_adi # Kostüm bilgisini gizlice içeri sokuyoruz!
                        
                        gecis_ekrani_goster(su_anki_seviye, 2500)
                        _, anlik_harita, bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                        
                        ses_yoneticisi.oynanis_muzigi_cal(su_anki_seviye)
                        durum = "PLAYING"
                        break

        # -----------------------------------------------------------------
        # DURUM 2: AYARLAR MENÜSÜ
        # -----------------------------------------------------------------
        elif durum == "SETTINGS":
            ses_yoneticisi.tema_muzigi_cal()

            ekran.fill((0, 0, 0))
            ekran.blit(img_ayarlar, (0, 0))
            
            btn_ayarlar_menu = pygame.Rect(GENISLIK // 2 - 235, 910, 470, 100)
            btn_ses_ikon = pygame.Rect(370, 550, 160, 160)
            
            if ses_yoneticisi.ses_aktif:
                ekran.blit(img_ses_acik, btn_ses_ikon.topleft)
            else:
                ekran.blit(img_ses_kapali, btn_ses_ikon.topleft)

            su_anki_buton = None
            if btn_ayarlar_menu.collidepoint(fare_pos): su_anki_buton = "AYARLAR_MENU"
            elif btn_ses_ikon.collidepoint(fare_pos): su_anki_buton = "SES_IKON"

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                    ses_yoneticisi.secme_sesi_cal()
                    durum = onceki_durum
                
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if btn_ayarlar_menu.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()  
                        durum = onceki_durum
                        break
                    elif btn_ses_ikon.collidepoint(fare_pos):
                        ses_yoneticisi.sesi_ac_kapat()
                        ses_yoneticisi.secme_sesi_cal()

        # -----------------------------------------------------------------
        # DURUM 3: AKTİF OYUN (PLAYING)
        # -----------------------------------------------------------------
        elif durum == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                if event.type == pygame.KEYDOWN:
                    
                    # YENİ ESC MANTIĞI: Oyunu durdur ve PAUSED durumuna geç
                    if event.key == pygame.K_ESCAPE:
                        ses_yoneticisi.secme_sesi_cal()
                        onceki_durum = "PLAYING"
                        durum = "PAUSED"
                    
                    if event.key == pygame.K_F9:
                        ses_yoneticisi.tum_sesleri_durdur()  
                        ses_yoneticisi.level_gecme_cal()     
                        
                        aktif_ozellik = None
                        aktif_debuff = None
                        debuff_sayaci = 0
                        pacman.yon_x = 0; pacman.yon_y = 0
                        pacman.istenen_x = 0; pacman.istenen_y = 0
                        
                        ekran.fill((0, 0, 0))
                        ekran.blit(img_kazandin, (0, 0))
                        puan_gosterge = font.render(str(puan), True, (255, 255, 0))
                        ekran.blit(puan_gosterge, puan_gosterge.get_rect(center=(GENISLIK // 2, 700)))
                        pygame.display.flip()
                        
                        pygame.time.delay(2500)
                        durum = "GAME_WON"
                        
                    if event.key == pygame.K_F3:
                        ses_yoneticisi.tum_sesleri_durdur()  
                        
                        su_anki_seviye = 3
                        kalan_sure = 180
                        kalkan_aktif = False
                        aktif_ozellik = None
                        aktif_debuff = None
                        debuff_sayaci = 0
                        
                        pacman.yon_x = 0; pacman.yon_y = 0
                        pacman.istenen_x = 0; pacman.istenen_y = 0
                        
                        gecis_ekrani_goster(su_anki_seviye, 1000) 
                        basarili_mi, yeni_harita, yeni_bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                        
                        if basarili_mi:
                            anlik_harita = yeni_harita 
                            bos_yollar = yeni_bos_yollar
                            ses_yoneticisi.oynanis_muzigi_cal(su_anki_seviye)

            if durum != "PLAYING":
                pacman.yon_x = 0; pacman.yon_y = 0
                pacman.istenen_x = 0; pacman.istenen_y = 0
                continue
            
            frame_sayaci += 1
            if frame_sayaci >= FPS: 
                frame_sayaci = 0
                if kalan_sure > 0:
                    kalan_sure -= 1
                    puan = max(0, puan - 10)

            if not joker_sahnedemi and (su_anki_zaman - son_joker_dogma_zamani > joker_dogma_suresi):
                if bos_yollar: 
                    secilen_koordinat = random.choice(bos_yollar)
                    yeni_joker = YemKalkaniJoker(secilen_koordinat[0], secilen_koordinat[1])
                    joker_grubu.add(yeni_joker)
                    tum_spriteler.add(yeni_joker)
                    joker_sahnedemi = True
                    son_joker_dogma_zamani = su_anki_zaman 
                    ses_yoneticisi.superguc_spawn_cal() 

            elif joker_sahnedemi and (su_anki_zaman - son_joker_dogma_zamani > joker_kalma_suresi):
                for j in joker_grubu: j.kill()
                joker_sahnedemi = False
                son_joker_dogma_zamani = su_anki_zaman 
                ses_yoneticisi.superguc_kacti_cal()
                
            if pygame.sprite.spritecollide(pacman, joker_grubu, True):
                joker_sahnedemi = False
                son_joker_dogma_zamani = su_anki_zaman
                kalkan_aktif = True
                kalkan_bitis_zamani = su_anki_zaman + kalkan_suresi
                ses_yoneticisi.superguc_alma_cal()

            if kalkan_aktif and su_anki_zaman > kalkan_bitis_zamani:
                kalkan_aktif = False

            if aktif_ozellik is not None:
                if ozellik_sayaci > 0: 
                    ozellik_sayaci -= 1
                if ozellik_sayaci <= 0:
                    ses_yoneticisi.superguc_despawn_cal()
                    if aktif_ozellik == "PHASE":
                        duvara_degiyor_mu = pygame.sprite.spritecollideany(pacman, duvar_grubu)
                        if not duvara_degiyor_mu: aktif_ozellik = None
                    else:
                        aktif_ozellik = None

            if aktif_debuff is not None:
                if debuff_sayaci > 0:
                    debuff_sayaci -= 1
                else:
                    aktif_debuff = None


            toplanan_ozellikler = pygame.sprite.spritecollide(pacman, ozellik_yemi_grubu, True)
            for yem in toplanan_ozellikler:
                ses_yoneticisi.superguc_alma_cal()

                if yem.ozellik_turu in BUFF_TURLERI:
                    if aktif_ozellik is None:
                        aktif_ozellik = yem.ozellik_turu
                        if aktif_ozellik == "CHRONOS":      ozellik_sayaci = 180
                        elif aktif_ozellik == "PHASE":      ozellik_sayaci = 240
                        elif aktif_ozellik == "HIZ_ARTISI": ozellik_sayaci = 300

                elif yem.ozellik_turu in DEBUFF_TURLERI:
                    if aktif_debuff is None:
                        aktif_debuff = yem.ozellik_turu
                        debuff_sayaci = DEBUFF_SURESI

            onceki_hayalet_sayisi = len(hayalet_grubu)
            pacman.update(duvar_grubu, yem_grubu, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi, aktif_ozellik, aktif_debuff)
            
            hedef_yemler = sahte_bos_grup if kalkan_aktif else yem_grubu
            
            hayalet_grubu.update(duvar_grubu, hedef_yemler, hayalet_grubu, anlik_harita, pacman, ses_yoneticisi, aktif_ozellik, aktif_debuff)
            
            if aktif_debuff == "KAC":
                if pygame.sprite.spritecollide(pacman, hayalet_grubu, False):
                    kalan_sure = 0 
            
            guncel_hayalet_sayisi = len(hayalet_grubu)
            if guncel_hayalet_sayisi < onceki_hayalet_sayisi:
                puan += ((onceki_hayalet_sayisi - guncel_hayalet_sayisi) * 1000)

            ekran.fill((0, 0, 0))
            ekran.blit(img_arkaplan_listesi.get(su_anki_seviye, img_arkaplan_listesi[1]), (0, 0)) 
            
            tum_spriteler.draw(ekran)
            draw_portal_visuals(ekran, su_anki_seviye)
            hayalet_grubu.draw(ekran)
            ekran.blit(pacman.image, pacman.rect)

            if aktif_debuff == "KORUL":
                karanlik = pygame.Surface((GENISLIK, YUKSEKLIK))
                karanlik.fill((0, 0, 0)) 
                ekran.blit(karanlik, (0, 0))
                aydinlik = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
                pygame.draw.circle(aydinlik, (0, 0, 0, 0), pacman.rect.center, 120)
                ekran.blit(aydinlik, (0, 0))

            for hayalet in hayalet_grubu:
                if hayalet.kacis_modu:
                    unlem_x = hayalet.rect.x + (TILE_SIZE // 2) - 3
                    unlem_y = hayalet.rect.y - 22
                    pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y, 6, 12))
                    pygame.draw.rect(ekran, (255, 255, 0), (unlem_x, unlem_y + 16, 6, 6))

            if kalkan_aktif:
                pygame.draw.circle(ekran, (0, 255, 0), pacman.rect.center, 25, 3)

            hud_genislik = 1200
            hud_yukseklik = 40
            hud_x = (GENISLIK - hud_genislik) // 2
            hud_y = 0
            hud_rect = pygame.Rect(hud_x, hud_y, hud_genislik, hud_yukseklik)
            
            pygame.draw.rect(ekran, (0, 0, 0), hud_rect)
            pygame.draw.rect(ekran, (0, 0, 255), hud_rect, 3, border_radius=15)

            puan_metni = kucuk_font.render(f"PUAN:{puan}", True, (255, 255, 255))            
            baslik_metni = kucuk_font.render("PAC-MAN: REVERSE", True, (255, 255, 0))   
            sure_metni = kucuk_font.render(f"SURE:{kalan_sure}", True, (255, 255, 255))

            ekran.blit(puan_metni, puan_metni.get_rect(midleft=(hud_x + 20, hud_y + hud_yukseklik // 2)))
            ekran.blit(baslik_metni, baslik_metni.get_rect(center=(GENISLIK // 2, hud_y + hud_yukseklik // 2)))
            ekran.blit(sure_metni, sure_metni.get_rect(midright=(hud_x + hud_genislik - 20, hud_y + hud_yukseklik // 2)))

            if aktif_debuff is not None:
                zaman = pygame.time.get_ticks()
                pulse = int(155 + (100 * abs(math.sin(zaman / 150.0)))) 
                renk = (pulse, 0, 0) 
                
                kutu_genislik = 220
                kutu_yukseklik = 80
                kutu_x = GENISLIK - kutu_genislik - 20
                kutu_y = 20
                
                pygame.draw.rect(ekran, (0, 0, 0), (kutu_x, kutu_y, kutu_genislik, kutu_yukseklik))
                pygame.draw.rect(ekran, renk, (kutu_x, kutu_y, kutu_genislik, kutu_yukseklik), 4, border_radius=10)
                
                debuff_isimleri = {"YAVASLA": "YAVAŞ!", "KORUL": "KÖR!", "TERS": "TERS!", "KAC": "KAÇ!"}
                debuff_metni = kucuk_font.render(debuff_isimleri.get(aktif_debuff, ""), True, renk)
                ekran.blit(debuff_metni, debuff_metni.get_rect(center=(kutu_x + kutu_genislik // 2, kutu_y + 30)))
                
                kalan_oran = debuff_sayaci / float(DEBUFF_SURESI)  
                bar_genislik = 180
                guncel_bar_genislik = int(bar_genislik * kalan_oran)
                bar_x = kutu_x + (kutu_genislik - bar_genislik) // 2
                bar_y = kutu_y + 60
                
                pygame.draw.rect(ekran, (50, 0, 0), (bar_x, bar_y, bar_genislik, 8))
                pygame.draw.rect(ekran, renk, (bar_x, bar_y, max(0, guncel_bar_genislik), 8))
            
            # --- OYUNU KAZANMA ---
            if guncel_hayalet_sayisi == 0:
                ses_yoneticisi.tum_sesleri_durdur()  
                ses_yoneticisi.level_gecme_cal()     
                
                puan += (kalan_sure * 10) 
                aktif_ozellik = None
                aktif_debuff = None
                debuff_sayaci = 0
                
                pacman.yon_x = 0; pacman.yon_y = 0
                pacman.istenen_x = 0; pacman.istenen_y = 0
                
                if su_anki_seviye == 3:
                    ekran.fill((0, 0, 0))
                    ekran.blit(img_kazandin, (0, 0))
                    puan_gosterge = font.render(str(puan), True, (255, 255, 0))
                    ekran.blit(puan_gosterge, puan_gosterge.get_rect(center=(GENISLIK // 2, 700)))
                    pygame.display.flip()
                    
                    pygame.time.delay(2500)
                    gruplari_temizle()
                    durum = "GAME_WON"
                else:
                    su_anki_seviye += 1
                    kalan_sure = 180  
                    kalkan_aktif = False 
                    
                    gecis_ekrani_goster(su_anki_seviye, 2500)
                    basarili_mi, yeni_harita, yeni_bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                    
                    if basarili_mi:
                        anlik_harita = yeni_harita 
                        bos_yollar = yeni_bos_yollar
                        ses_yoneticisi.oynanis_muzigi_cal(su_anki_seviye)
                    else:
                        skor_kaydet("Bilinmeyen", puan)
                        skor_tablosu_goster()
                        gruplari_temizle()
                        durum = "MENU"
            
            # --- OYUNU KAYBETME (GAME OVER) ---
            elif len(yem_grubu) == 0 or kalan_sure <= 0:
                ses_yoneticisi.tum_sesleri_durdur()  
                ses_yoneticisi.kaybetme_sesi_cal()   
                
                aktif_ozellik = None
                aktif_debuff = None
                debuff_sayaci = 0
                kalkan_aktif = False
                
                pacman.yon_x = 0; pacman.yon_y = 0
                pacman.istenen_x = 0; pacman.istenen_y = 0

                ekran.fill((0, 0, 0))
                ekran.blit(img_kaybettin, (0, 0))
                puan_gosterge = font.render(str(puan), True, (255, 255, 0))
                ekran.blit(puan_gosterge, puan_gosterge.get_rect(center=(GENISLIK // 2, 700)))
                pygame.display.flip()
                
                pygame.time.delay(2500)
                gruplari_temizle()
                durum = "GAME_OVER"
                
# -----------------------------------------------------------------
        # DURUM 3.5: DURDURULDU (PAUSE) EKRANI
        # -----------------------------------------------------------------
        elif durum == "PAUSED":
            ekran.fill((0, 0, 0))
            ekran.blit(img_durduruldu, (0, 0))
            
            # Tasarımdaki butonların görünmez tıklama alanları (Hizalamalar 1080p'ye göre ayarlandı)
            btn_pause_devam = pygame.Rect(GENISLIK // 2 - 300, 500, 600, 110)
            btn_pause_ayarlar = pygame.Rect(GENISLIK // 2 - 300, 690, 600, 110)
            btn_pause_menu = pygame.Rect(GENISLIK // 2 - 300, 850, 600, 110)

            su_anki_buton = None
            if btn_pause_devam.collidepoint(fare_pos): su_anki_buton = "DEVAM"
            elif btn_pause_ayarlar.collidepoint(fare_pos): su_anki_buton = "AYARLAR"
            elif btn_pause_menu.collidepoint(fare_pos): su_anki_buton = "MENU"

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                
                # ESC'ye tekrar basılırsa oyuna devam et
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    ses_yoneticisi.secme_sesi_cal()
                    durum = "PLAYING"
                    
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if btn_pause_devam.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        durum = "PLAYING"
                        
                    elif btn_pause_ayarlar.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        onceki_durum = "PAUSED"
                        durum = "SETTINGS"
                        
                    elif btn_pause_menu.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        ses_yoneticisi.tum_sesleri_durdur()
                        gruplari_temizle()
                        onceki_durum = "MENU"
                        durum = "MENU"                

        # -----------------------------------------------------------------
        # DURUM 4: GAME OVER (KAYBETME) EKRANI 
        # -----------------------------------------------------------------
        elif durum == "GAME_OVER":
            ekran.fill((0, 0, 0))
            ekran.blit(img_kaybettin, (0, 0))
            
            puan_gosterge = font.render(str(puan), True, (255, 255, 0))
            ekran.blit(puan_gosterge, puan_gosterge.get_rect(center=(GENISLIK // 2, 700))) 
            
            su_anki_buton = None
            if btn_go_yeni_oyun.collidepoint(fare_pos): su_anki_buton = "GO_YENI"
            elif btn_go_ana_menu.collidepoint(fare_pos): su_anki_buton = "GO_MENU"

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    
                    if btn_go_yeni_oyun.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        
                        siyah_ekran = pygame.Surface((GENISLIK, YUKSEKLIK))
                        siyah_ekran.fill((0, 0, 0))
                        oyuncu_ismi = isim_al_ekrani(puan, siyah_ekran)
                        skor_kaydet(oyuncu_ismi, puan)
                        
                        su_anki_seviye = 1
                        puan = 0
                        kalan_sure = 180
                        aktif_ozellik = None
                        aktif_debuff = None
                        debuff_sayaci = 0
                        kalkan_aktif = False
                        
                        # pacman'i varsayılan olarak yaratıyoruz, çünkü Game Over'dan gelindi 
                        # oyuncu isterse menüye dönüp karakter seçebilir.
                        pacman = Player(0, 0, "imam_packman")
                        
                        gecis_ekrani_goster(su_anki_seviye, 2500)
                        _, anlik_harita, bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                        
                        ses_yoneticisi.oynanis_muzigi_cal(su_anki_seviye)
                        durum = "PLAYING"
                        
                    elif btn_go_ana_menu.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        
                        siyah_ekran = pygame.Surface((GENISLIK, YUKSEKLIK))
                        siyah_ekran.fill((0, 0, 0))
                        oyuncu_ismi = isim_al_ekrani(puan, siyah_ekran)
                        skor_kaydet(oyuncu_ismi, puan)
                        
                        gruplari_temizle()
                        durum = "MENU"

        # -----------------------------------------------------------------
        # DURUM 5: GAME WON (KAZANMA) EKRANI 
        # -----------------------------------------------------------------
        elif durum == "GAME_WON":
            ekran.fill((0, 0, 0))
            ekran.blit(img_kazandin, (0, 0))
            
            puan_gosterge = font.render(str(puan), True, (255, 255, 0))
            ekran.blit(puan_gosterge, puan_gosterge.get_rect(center=(GENISLIK // 2, 700))) 
            
            su_anki_buton = None
            if btn_go_yeni_oyun.collidepoint(fare_pos): su_anki_buton = "GO_YENI"
            elif btn_go_ana_menu.collidepoint(fare_pos): su_anki_buton = "GO_MENU"

            if su_anki_buton != son_hover_edilen_buton:
                if su_anki_buton is not None:
                    ses_yoneticisi.hover_sesi_cal()
                son_hover_edilen_buton = su_anki_buton

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    
                    if btn_go_yeni_oyun.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        
                        siyah_ekran = pygame.Surface((GENISLIK, YUKSEKLIK))
                        siyah_ekran.fill((0, 0, 0))
                        oyuncu_ismi = isim_al_ekrani(puan, siyah_ekran)
                        skor_kaydet(oyuncu_ismi, puan)
                        
                        su_anki_seviye = 1
                        puan = 0
                        kalan_sure = 180
                        aktif_ozellik = None
                        aktif_debuff = None
                        debuff_sayaci = 0
                        kalkan_aktif = False
                        
                        pacman = Player(0, 0, "imam_packman")
                        
                        gecis_ekrani_goster(su_anki_seviye, 2500)
                        _, anlik_harita, bos_yollar = seviye_yukle(su_anki_seviye, pacman)
                        
                        ses_yoneticisi.oynanis_muzigi_cal(su_anki_seviye)
                        durum = "PLAYING"
                        
                    elif btn_go_ana_menu.collidepoint(fare_pos):
                        ses_yoneticisi.secme_sesi_cal()
                        
                        siyah_ekran = pygame.Surface((GENISLIK, YUKSEKLIK))
                        siyah_ekran.fill((0, 0, 0))
                        oyuncu_ismi = isim_al_ekrani(puan, siyah_ekran)
                        skor_kaydet(oyuncu_ismi, puan)
                        
                        gruplari_temizle()
                        durum = "MENU"

        pygame.display.flip()
        saat.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()