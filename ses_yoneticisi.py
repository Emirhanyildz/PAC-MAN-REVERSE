import pygame

class SesYoneticisi:
    def __init__(self):
        # Mixer modülünü başlatıyoruz
        pygame.mixer.init()
        
        # Kanalları ayırıyoruz (Sesler birbirini kesmesin)
        self.kanal_yem = pygame.mixer.Channel(0)
        self.kanal_av = pygame.mixer.Channel(1)
        
        # --- SES SEVİYESİ AYARLARI ---
        self.kanal_yem.set_volume(0.2)  # Yem yeme sesi biraz arkada kalsın diye %20 yaptık
        self.kanal_av.set_volume(0.2)   # Hayalet avlama efekti daha vurucu olsun diye %60 yaptık
        
        # 8-Bit Ses dosyalarını yüklüyoruz
        # Hata yakalama (try-except) bloğu sayesinde klasörde ses dosyası 
        # olmasa bile oyun çökmeden sessiz modda çalışmaya devam eder.
        try:
            self.ses_yem = pygame.mixer.Sound("sesler/yem_sesi.wav")
        except FileNotFoundError:
            self.ses_yem = None
            print("Uyarı: 'sesler/yem_sesi.wav' dosyası bulunamadı!")

        # Hayalet avlama sesini yükle
        try:
            self.ses_av = pygame.mixer.Sound("sesler/hayalet_avlandi.wav")
        except FileNotFoundError:
            self.ses_av = None
            print("Uyarı: 'sesler/hayalet_avlandi.wav' dosyası bulunamadı! Bu ses şu an çalmayacak.")

    def yem_yendi_cal(self):
        # Eğer ses dosyası varsa ve o an kanal boşsa çal
        if self.ses_yem and not self.kanal_yem.get_busy():
            self.kanal_yem.play(self.ses_yem)

    def av_basarili_cal(self):
        if self.ses_av:
            self.kanal_av.play(self.ses_av)
