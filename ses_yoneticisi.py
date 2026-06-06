import pygame

class SesYoneticisi:
    def __init__(self):
        # Mixer modülünü başlatıyoruz
        pygame.mixer.init()
        
        # Kanalları ayırıyoruz (Sesler birbirini kesmesin)
        self.kanal_yem = pygame.mixer.Channel(0)
        self.kanal_av = pygame.mixer.Channel(1)
        
        # 8-Bit Ses dosyalarını yüklüyoruz
        # Hata yakalama (try-except) bloğu sayesinde klasörde ses dosyası 
        # olmasa bile oyun çökmeden sessiz modda çalışmaya devam eder.
        try:
            self.ses_yem = pygame.mixer.Sound("yem_sesi.wav")
            self.ses_av = pygame.mixer.Sound("hayalet_avlandi.wav")
        except FileNotFoundError:
            self.ses_yem = None
            self.ses_av = None
            print("Uyarı: Ses dosyaları bulunamadı, oyun sessiz modda çalışıyor.")

    def yem_yendi_cal(self):
        # Eğer ses dosyası varsa ve o an kanal boşsa çal
        if self.ses_yem and not self.kanal_yem.get_busy():
            self.kanal_yem.play(self.ses_yem)

    def av_basarili_cal(self):
        if self.ses_av:
            self.kanal_av.play(self.ses_av)