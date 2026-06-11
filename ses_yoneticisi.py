import pygame

class SesYoneticisi:
    def __init__(self):
        # Mixer modülünü başlatıyoruz
        pygame.mixer.init()
        
        # Kanalları ayırıyoruz (Sesler birbirini kesmesin)
        # Kanalları ayırıyoruz (Sesler birbirini kesmesin)
        self.kanal_yem = pygame.mixer.Channel(0)
        self.kanal_av = pygame.mixer.Channel(1)
        self.kanal_fark_etme = pygame.mixer.Channel(2)  # YENİ: Fark etme kanalı
        
        # --- SES SEVİYESİ AYARLARI ---
        self.kanal_yem.set_volume(0.2)  
        self.kanal_av.set_volume(0.4)   
        self.kanal_fark_etme.set_volume(0.3)  # YENİ: Fark etme ses seviyesi %50
        
        # 8-Bit Ses dosyalarını yüklüyoruz
        try:
            self.ses_yem = pygame.mixer.Sound("sesler/yem_sesi.wav")
        except FileNotFoundError:
            self.ses_yem = None
            print("Uyarı: 'sesler/yem_sesi.wav' dosyası bulunamadı!")

        try:
            self.ses_av = pygame.mixer.Sound("sesler/hayalet_avlandi.wav")
        except FileNotFoundError:
            self.ses_av = None
            print("Uyarı: 'sesler/hayalet_avlandi.wav' dosyası bulunamadı! Bu ses şu an çalmayacak.")

        # YENİ: Fark etme (Alert) sesini yükle
        try:
            self.ses_fark_etme = pygame.mixer.Sound("sesler/fark_etme.wav")
        except FileNotFoundError:
            self.ses_fark_etme = None
            print("Uyarı: 'sesler/fark_etme.wav' dosyası bulunamadı! Fark etme sesi çalmayacak.")

    def yem_yendi_cal(self):
        if self.ses_yem and not self.kanal_yem.get_busy():
            self.kanal_yem.play(self.ses_yem)

    def av_basarili_cal(self):
        if self.ses_av:
            self.kanal_av.play(self.ses_av)

    # YENİ: Fark etme sesini tetikleyen fonksiyon
    def fark_etme_cal(self):
        if self.ses_fark_etme:
            self.kanal_fark_etme.play(self.ses_fark_etme)
