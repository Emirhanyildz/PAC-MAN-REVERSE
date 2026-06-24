import os
import math
import wave
import struct
import pygame

class SesYoneticisi:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        
        self.ses_aktif = True # YENİ: Seslerin açık/kapalı durumunu tutan şalter
        
        self.kanal_yem = pygame.mixer.Channel(0)
        self.kanal_av = pygame.mixer.Channel(1)
        self.kanal_fark_etme = pygame.mixer.Channel(2)
        self.kanal_hareket = pygame.mixer.Channel(3)
        self.kanal_ui = pygame.mixer.Channel(4)
        self.kanal_muzik = pygame.mixer.Channel(5) 
        self.kanal_olay = pygame.mixer.Channel(6) 
        self.kanal_guc = pygame.mixer.Channel(7)
        self.kanal_portal = pygame.mixer.Channel(8)
        self.kanal_oynanis = pygame.mixer.Channel(9) # YENİ: Oynanış Müziği Kanalı
        
        self.kanal_yem.set_volume(0.2)  
        self.kanal_av.set_volume(0.4)   
        self.kanal_fark_etme.set_volume(0.3)  
        self.kanal_hareket.set_volume(0.15) 
        self.kanal_ui.set_volume(0.3)  
        self.kanal_muzik.set_volume(0.10)
        self.kanal_olay.set_volume(0.4) 
        self.kanal_guc.set_volume(0.5) 
        self.kanal_portal.set_volume(0.35) 
        self.kanal_oynanis.set_volume(0.40) # YENİ: Arka plan müziği ses seviyesi (diğer sesleri bastırmasın)
        
        self._prosedurel_waka_uret()
        self._ui_seslerini_uret()  
        self._tema_muzigi_uret() 
        self._oyun_sonu_seslerini_uret() 
        self._superguc_seslerini_uret() 
        self._portal_sesi_uret() 
        self._oynanis_muziklerini_uret() # YENİ: Oynanış müzikleri sentezleyicisi

        try: self.ses_yem = pygame.mixer.Sound("sesler/yem_sesi.wav")
        except FileNotFoundError: self.ses_yem = None

        try: self.ses_av = pygame.mixer.Sound("sesler/hayalet_avlandi.wav")
        except FileNotFoundError: self.ses_av = None

        try: self.ses_fark_etme = pygame.mixer.Sound("sesler/fark_etme.wav")
        except FileNotFoundError: self.ses_fark_etme = None

        try: self.ses_hareket = pygame.mixer.Sound("sesler/waka_sesi.wav")
        except FileNotFoundError: self.ses_hareket = None

        try: self.ses_hareket_hizli = pygame.mixer.Sound("sesler/waka_hizli.wav")
        except FileNotFoundError: self.ses_hareket_hizli = None

        try: self.ses_hover = pygame.mixer.Sound("sesler/menu_hover.wav")
        except FileNotFoundError: self.ses_hover = None

        try: self.ses_secme = pygame.mixer.Sound("sesler/menu_secme.wav")
        except FileNotFoundError: self.ses_secme = None

        try: self.ses_tema = pygame.mixer.Sound("sesler/giris_tema.wav")
        except FileNotFoundError: self.ses_tema = None

        try: self.ses_kazanma = pygame.mixer.Sound("sesler/level_gecme.wav")
        except FileNotFoundError: self.ses_kazanma = None

        try: self.ses_kaybetme = pygame.mixer.Sound("sesler/kaybetme_sesi.wav")
        except FileNotFoundError: self.ses_kaybetme = None

        try: self.ses_guc_alma = pygame.mixer.Sound("sesler/superguc_alma.wav")
        except FileNotFoundError: self.ses_guc_alma = None

        try: self.ses_guc_spawn = pygame.mixer.Sound("sesler/superguc_spawn.wav")
        except FileNotFoundError: self.ses_guc_spawn = None

        try: self.ses_guc_despawn = pygame.mixer.Sound("sesler/superguc_despawn.wav")
        except FileNotFoundError: self.ses_guc_despawn = None

        try: self.ses_guc_kacti = pygame.mixer.Sound("sesler/superguc_kacti.wav")
        except FileNotFoundError: self.ses_guc_kacti = None

        try: self.ses_portal = pygame.mixer.Sound("sesler/portal_gecme.wav")
        except FileNotFoundError: self.ses_portal = None

        # --- YENİ: OYNANIŞ MÜZİĞİ DOSYALARI ---
        try: self.ses_oynanis_1 = pygame.mixer.Sound("sesler/oynanis_track1.wav")
        except FileNotFoundError: self.ses_oynanis_1 = None

        try: self.ses_oynanis_2 = pygame.mixer.Sound("sesler/oynanis_track2.wav")
        except FileNotFoundError: self.ses_oynanis_2 = None

        try: self.ses_oynanis_3 = pygame.mixer.Sound("sesler/oynanis_track3.wav")
        except FileNotFoundError: self.ses_oynanis_3 = None

    def _muzik_yaz(self, dosya_yolu, frekanslar, adim_suresi, tekrar):
        # Basit chiptune arpej döngüleri üreten altyapı
        sample_rate = 22050
        sure = adim_suresi * len(frekanslar) * tekrar
        with wave.open(dosya_yolu, 'w') as w:
            w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
            faz = 0.0
            for i in range(int(sample_rate * sure)):
                t = i / sample_rate
                nota_indeksi = int((t % (adim_suresi * len(frekanslar))) / adim_suresi)
                frekans = frekanslar[nota_indeksi]
                yerel_t = t % adim_suresi
                envelope = 1.0 - (yerel_t / adim_suresi) # Tatlı bir Pluck (çekme) efekti
                faz += 2 * math.pi * frekans / sample_rate
                sinyal = 20 if math.sin(faz) > 0 else -20
                sinyal = int(sinyal * envelope)
                w.writeframes(struct.pack('B', sinyal + 128))

    def _oynanis_muziklerini_uret(self):
        os.makedirs("sesler", exist_ok=True)
        # Level 1: Eğlenceli Majör Tempo
        dosya_1 = "sesler/oynanis_track1.wav"
        if not os.path.exists(dosya_1): self._muzik_yaz(dosya_1, [261.63, 329.63, 392.00, 493.88], 0.20, 16)
        
        # Level 2: Daha Gergin Minör Tempo (Hızlı)
        dosya_2 = "sesler/oynanis_track2.wav"
        if not os.path.exists(dosya_2): self._muzik_yaz(dosya_2, [220.00, 261.63, 329.63, 440.00], 0.15, 20)
        
        # Level 3: Aşırı Hızlı Aksiyon (Diminished)
        dosya_3 = "sesler/oynanis_track3.wav"
        if not os.path.exists(dosya_3): self._muzik_yaz(dosya_3, [196.00, 233.08, 293.66, 392.00, 311.13, 261.63], 0.12, 24)

    # ... (Diğer üretim metotları: _prosedurel_waka_uret, vb. GİZLENDİ - AYNEN KALACAK!)
    def _prosedurel_waka_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_normal = "sesler/waka_sesi.wav"
        if not os.path.exists(dosya_normal): self._sinus_waka_yaz(dosya_normal, sure=0.15, bas_frekans=220, son_frekans=420)
        dosya_hizli = "sesler/waka_hizli.wav"
        if not os.path.exists(dosya_hizli): self._sinus_waka_yaz(dosya_hizli, sure=0.10, bas_frekans=440, son_frekans=700)

    def _sinus_waka_yaz(self, dosya_yolu, sure, bas_frekans, son_frekans):
        sample_rate = 22050
        with wave.open(dosya_yolu, 'w') as w:
            w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
            faz = 0.0
            for i in range(int(sample_rate * sure)):
                t = i / sample_rate
                envelope = math.sin((t / sure) * math.pi) 
                frekans = bas_frekans + ((son_frekans - bas_frekans) * (t / sure))
                faz += 2 * math.pi * frekans / sample_rate
                sinyal = int(math.sin(faz) * 60 * envelope)
                w.writeframes(struct.pack('B', sinyal + 128))

    def _ui_seslerini_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_hover = "sesler/menu_hover.wav"
        if not os.path.exists(dosya_hover):
            sample_rate = 22050; sure = 0.04 
            with wave.open(dosya_hover, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    frekans = 600 + (200 * (i / (sample_rate * sure)))
                    faz += 2 * math.pi * frekans / sample_rate
                    sinyal = int(math.sin(faz) * 30)
                    w.writeframes(struct.pack('B', sinyal + 128))
                    
        dosya_secme = "sesler/menu_secme.wav"
        if not os.path.exists(dosya_secme):
            sample_rate = 22050; sure = 0.15
            with wave.open(dosya_secme, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 400 + (300 * (t / sure))
                    faz += 2 * math.pi * frekans / sample_rate
                    envelope = 1.0 - (t / sure)
                    sinyal = int(math.sin(faz) * 50 * envelope)
                    w.writeframes(struct.pack('B', sinyal + 128))

    def _tema_muzigi_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_tema = "sesler/giris_tema.wav"
        if not os.path.exists(dosya_tema):
            sample_rate = 22050; sure = 1.6 
            with wave.open(dosya_tema, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                frekanslar = [261.63, 311.13, 392.00, 523.25, 392.00, 311.13, 261.63, 196.00]
                adim_suresi = sure / len(frekanslar)
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    nota_indeksi = min(int(t / adim_suresi), len(frekanslar)-1)
                    frekans = frekanslar[nota_indeksi]
                    yerel_t = t % adim_suresi
                    envelope = math.sin((yerel_t / adim_suresi) * math.pi)
                    faz += 2 * math.pi * frekans / sample_rate
                    sinyal = 30 if math.sin(faz) > 0 else -30
                    sinyal = int(sinyal * envelope)
                    w.writeframes(struct.pack('B', sinyal + 128))

    def _oyun_sonu_seslerini_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_kazanma = "sesler/level_gecme.wav"
        if not os.path.exists(dosya_kazanma):
            sample_rate = 22050; sure = 1.2
            with wave.open(dosya_kazanma, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                frekanslar = [261.63, 329.63, 392.00, 523.25] 
                adim_suresi = sure / len(frekanslar)
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    nota_indeksi = min(int(t / adim_suresi), len(frekanslar)-1)
                    frekans = frekanslar[nota_indeksi]
                    faz += 2 * math.pi * frekans / sample_rate
                    sinyal = int((math.sin(faz) * 0.5 + (1.0 if math.sin(faz) > 0 else -1.0) * 0.5) * 40)
                    w.writeframes(struct.pack('B', sinyal + 128))

        dosya_kaybetme = "sesler/kaybetme_sesi.wav"
        if not os.path.exists(dosya_kaybetme):
            sample_rate = 22050; sure = 1.5
            with wave.open(dosya_kaybetme, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 400 - (250 * (t / sure))
                    faz += 2 * math.pi * frekans / sample_rate
                    lfo = math.sin(2 * math.pi * 10 * t) 
                    sinyal = int((math.sin(faz) + lfo * 0.3) * 35)
                    w.writeframes(struct.pack('B', min(max(sinyal + 128, 0), 255)))

    def _superguc_seslerini_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_alma = "sesler/superguc_alma.wav"
        if not os.path.exists(dosya_alma):
            sample_rate = 22050; sure = 0.4
            with wave.open(dosya_alma, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 400 + (1600 * (t / sure)) 
                    faz += 2 * math.pi * frekans / sample_rate
                    sinyal = int(math.sin(faz) * 50)
                    w.writeframes(struct.pack('B', sinyal + 128))

        dosya_spawn = "sesler/superguc_spawn.wav"
        if not os.path.exists(dosya_spawn):
            sample_rate = 22050; sure = 0.3
            with wave.open(dosya_spawn, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 800 - (200 * (t / sure)) 
                    faz += 2 * math.pi * frekans / sample_rate
                    envelope = 1.0 - (t / sure) 
                    lfo = math.sin(2 * math.pi * 20 * t) 
                    sinyal = int(math.sin(faz) * 60 * envelope * (0.5 + 0.5 * lfo))
                    w.writeframes(struct.pack('B', sinyal + 128))

        dosya_despawn = "sesler/superguc_despawn.wav"
        if not os.path.exists(dosya_despawn):
            sample_rate = 22050; sure = 0.5
            with wave.open(dosya_despawn, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 800 - (600 * (t / sure)) 
                    faz += 2 * math.pi * frekans / sample_rate
                    envelope = 1.0 - (t / sure) 
                    sinyal = int(math.sin(faz) * 40 * envelope)
                    w.writeframes(struct.pack('B', sinyal + 128))

        dosya_kacti = "sesler/superguc_kacti.wav"
        if not os.path.exists(dosya_kacti):
            sample_rate = 22050; sure = 0.25
            with wave.open(dosya_kacti, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 500 - (400 * (t / sure)) 
                    faz += 2 * math.pi * frekans / sample_rate
                    envelope = 1.0 - (t / sure) 
                    sinyal = int(math.sin(faz) * 30 * envelope) 
                    w.writeframes(struct.pack('B', sinyal + 128))

    def _portal_sesi_uret(self):
        os.makedirs("sesler", exist_ok=True)
        dosya_portal = "sesler/portal_gecme.wav"
        if not os.path.exists(dosya_portal):
            sample_rate = 22050; sure = 0.25
            with wave.open(dosya_portal, 'w') as w:
                w.setnchannels(1); w.setsampwidth(1); w.setframerate(sample_rate)
                faz = 0.0
                for i in range(int(sample_rate * sure)):
                    t = i / sample_rate
                    frekans = 300 + math.sin(t * math.pi / sure) * 800
                    faz += 2 * math.pi * frekans / sample_rate
                    envelope = math.sin((t / sure) * math.pi) 
                    sinyal = int(math.sin(faz) * 50 * envelope)
                    w.writeframes(struct.pack('B', sinyal + 128))

    def yem_yendi_cal(self):
        if self.ses_yem and not self.kanal_yem.get_busy(): self.kanal_yem.play(self.ses_yem)

    def av_basarili_cal(self):
        if self.ses_av: self.kanal_av.play(self.ses_av)

    def fark_etme_cal(self):
        if self.ses_fark_etme: self.kanal_fark_etme.play(self.ses_fark_etme)

    def hareket_sesi_cal(self, hizli_mi=False):
        hedef_ses = self.ses_hareket_hizli if hizli_mi else self.ses_hareket
        if hedef_ses is None: return
        if self.kanal_hareket.get_busy():
            if self.kanal_hareket.get_sound() != hedef_ses:
                self.kanal_hareket.stop()
                self.kanal_hareket.play(hedef_ses, loops=-1)
        else:
            self.kanal_hareket.play(hedef_ses, loops=-1)

    def hareket_sesi_durdur(self):
        if self.kanal_hareket.get_busy(): self.kanal_hareket.stop()
            
    def hover_sesi_cal(self):
        if self.ses_hover: self.kanal_ui.play(self.ses_hover)

    def secme_sesi_cal(self):
        if self.ses_secme: self.kanal_olay.play(self.ses_secme)

    def tema_muzigi_cal(self):
        if self.ses_tema and not self.kanal_muzik.get_busy(): self.kanal_muzik.play(self.ses_tema, loops=-1) 

    def tema_muzigi_durdur(self):
        if self.kanal_muzik.get_busy(): self.kanal_muzik.stop()

    def tum_sesleri_durdur(self):
        pygame.mixer.stop()

    def level_gecme_cal(self):
        if self.ses_kazanma: self.kanal_olay.play(self.ses_kazanma)
            
    def kaybetme_sesi_cal(self):
        if self.ses_kaybetme: self.kanal_olay.play(self.ses_kaybetme)

    def superguc_alma_cal(self):
        if self.ses_guc_alma: self.kanal_guc.play(self.ses_guc_alma)

    def superguc_spawn_cal(self):
        if self.ses_guc_spawn: self.kanal_guc.play(self.ses_guc_spawn)

    def superguc_despawn_cal(self):
        if self.ses_guc_despawn: self.kanal_guc.play(self.ses_guc_despawn)

    def superguc_kacti_cal(self):
        if self.ses_guc_kacti: self.kanal_guc.play(self.ses_guc_kacti)

    def portal_sesi_cal(self):
        if self.ses_portal: self.kanal_portal.play(self.ses_portal)

    # --- YENİ EKLENDİ: OYNANIŞ MÜZİĞİ KONTROLLERİ ---
    def oynanis_muzigi_cal(self, seviye_no):
        if seviye_no == 1 and self.ses_oynanis_1:
            self.kanal_oynanis.play(self.ses_oynanis_1, loops=-1)
        elif seviye_no == 2 and self.ses_oynanis_2:
            self.kanal_oynanis.play(self.ses_oynanis_2, loops=-1)
        elif seviye_no == 3 and self.ses_oynanis_3:
            self.kanal_oynanis.play(self.ses_oynanis_3, loops=-1)
            
    def oynanis_muzigi_durdur(self):
        if self.kanal_oynanis.get_busy():
            self.kanal_oynanis.stop()
            
    def sesi_ac_kapat(self):
        self.ses_aktif = not self.ses_aktif
        
        if not self.ses_aktif:
            # Sesi kapat: Tüm kanalların sesini 0 yap
            for i in range(16):
                pygame.mixer.Channel(i).set_volume(0.0)
        else:
            # Sesi aç: Her kanalın sesini orijinal ayarına geri döndür
            self.kanal_yem.set_volume(0.2)  
            self.kanal_av.set_volume(0.4)   
            self.kanal_fark_etme.set_volume(0.3)  
            self.kanal_hareket.set_volume(0.15) 
            self.kanal_ui.set_volume(0.3)  
            self.kanal_muzik.set_volume(0.10)
            self.kanal_olay.set_volume(0.4) 
            self.kanal_guc.set_volume(0.5) 
            self.kanal_portal.set_volume(0.35) 
            self.kanal_oynanis.set_volume(0.40)