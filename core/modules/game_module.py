import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import sys

class GameModule:
    def __init__(self):
        pygame.init()
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.sprites = {}
        self.sounds = {}

    # Predefined colors
        self.CHORNYY = (0, 0, 0)
        self.BILYY = (255, 255, 255)
        self.CHERVONYY = (255, 0, 0)
        self.ZELENYY = (0, 255, 0)
        self.SYNIY = (0, 0, 255)
        self.ZHOVTYY = (255, 255, 0)
        self.FIOLYETOVYY = (255, 0, 255)
        self.BIRYUZOVYY = (0, 255, 255)
        self.SIRYY = (128, 128, 128)
        self.KORYCHNEVYY = (165, 42, 42)
        self.POMARANCHEVYY = (255, 165, 0)
        self.ROZHEVYY = (255, 192, 203)
        self.TEMNOZELENYY = (0, 100, 0)
        self.TEMNOSYNIY = (0, 0, 139)
        self.TEMNOFIOLETOVYY = (75, 0, 130)
        self.TEMNOROZHEVYY = (199, 21, 133)
        self.TEMNOPOMARANCHEVYY = (255, 140, 0)
        self.TEMNOKORYCHNEVYY = (101, 67, 33)
        self.SVITLOZELENYY = (144, 238, 144)
        self.SVITLOSYNIY = (173, 216, 230)
        self.SVITLOFIOLETOVYY = (216, 191, 216)
        self.SVITLOROZHEVYY = (255, 182, 193)
        self.SVITLOPOMARACHEVYY = (255, 200, 124)
        self.SVITLOKORYCHNEVYY = (210, 180, 140)
        self.SVITLOSIRYY = (192, 192, 192)
        self.TEMNOSIRYY = (64, 64, 64)
        self.ZOLOTYY = (255, 215, 0)
        self.SRIBLYY = (192, 192, 192)
        self.BRONZOVYY = (205, 127, 50)

    #Main game loop

    def stvoryty_vikno(self, shyryna, vysota, nazva = "KozakScript Game"):
        try:
            ikonka = pygame.image.load("..\icon.png")
            pygame.display.set_icon(ikonka)
        except:
            pass
        self.screen = pygame.display.set_mode((shyryna, vysota))
        pygame.display.set_caption(nazva)
        self.running = True
        return True
    
    def create_window(self, width, height, title="KozakScript Game"):
        return self.stvoryty_vikno(width, height, title)
    
    def sozdat_okno(self, shirina, visota, nazvanie = "KozakScript Game"):
        return self.stvoryty_vikno(shirina, visota, nazvanie)
    
    def vstanovyty_ikonku(self, shlyakh):
        try:
            ikonka = pygame.image.load(shlyakh)
            pygame.display.set_icon(ikonka)
            return True
        except Exception as e:
            raise ValueError(f"Failed to set icon: {shlyakh}, kozache: {e}")
        
    def ustanovit_ikonku(self, put):
        return self.vstanovyty_ikonku(put)
    
    def set_icon(self, path):
        return self.vstanovyty_ikonku(path)
        
    def onovyty(self):
        """Update display and handle events - Ukrainian"""
        if not self.running:
            return False
        try: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
            if self.running:
                pygame.display.flip()
            return self.running
        except pygame.error:
            self.running = False
            return False
    
    def update(self):
        """Update display and handle events - English"""
        return self.onovyty()
    
    def obnovit(self):
        """Update display and handle events - Russian"""
        return self.onovyty()
    
    # FPS control
    def vstanovyty_fps(self, fps):
        """Set FPS - Ukrainian"""
        self.clock.tick(fps)
    
    def set_fps(self, fps):
        """Set FPS - English"""
        self.vstanovyty_fps(fps)
    
    def ustanovit_fps(self, fps):
        """Set FPS - Russian"""
        self.vstanovyty_fps(fps)
    
    # Drawing functions
    def zalyty(self, kolir):
        """Fill screen with color - Ukrainian"""
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            self.screen.fill(kolir)
        else:
            raise ValueError("Color must be [R, G, B] array, kozache!")
    
    def fill(self, color):
        """Fill screen with color - English"""
        self.zalyty(color)
    
    def zalit(self, tsvet):
        """Fill screen with color - Russian"""
        self.zalyty(tsvet)
    
    def namalyuvaty_pryamokutnyk(self, kolir, x, y, shyryna, vysota):
        """Draw rectangle - Ukrainian"""
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.rect(self.screen, kolir, (x, y, shyryna, vysota))
        else:
            raise ValueError("Color must be [R, G, B] array, kozache!")
    
    def draw_rect(self, color, x, y, width, height):
        """Draw rectangle - English"""
        self.namalyuvaty_pryamokutnyk(color, x, y, width, height)
    
    def narisovat_pryamougolnik(self, tsvet, x, y, shirina, vysota):
        """Draw rectangle - Russian"""
        self.namalyuvaty_pryamokutnyk(tsvet, x, y, shirina, vysota)
    
    def namalyuvaty_kolo(self, kolir, x, y, radius):
        """Draw circle - Ukrainian"""
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.circle(self.screen, kolir, (x, y), radius)
        else:
            raise ValueError("Color must be [R, G, B] array, kozache!")
    
    def draw_circle(self, color, x, y, radius):
        """Draw circle - English"""
        self.namalyuvaty_kolo(color, x, y, radius)
    
    def narisovat_krug(self, tsvet, x, y, radius):
        """Draw circle - Russian"""
        self.namalyuvaty_kolo(tsvet, x, y, radius)
    
    def namalyuvaty_liniyu(self, kolir, x1, y1, x2, y2, tovshchyna=1):
        """Draw line - Ukrainian"""
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.line(self.screen, kolir, (x1, y1), (x2, y2), tovshchyna)
        else:
            raise ValueError("Color must be [R, G, B] array, kozache!")
    
    def draw_line(self, color, x1, y1, x2, y2, width=1):
        """Draw line - English"""
        self.namalyuvaty_liniyu(color, x1, y1, x2, y2, width)
    
    def narisovat_liniyu(self, tsvet, x1, y1, x2, y2, tolshchina=1):
        """Draw line - Russian"""
        self.namalyuvaty_liniyu(tsvet, x1, y1, x2, y2, tolshchina)
    
    # Input handling
    def klavisha_natysnuta(self, klavisha_nazva):
        """Check if key is pressed - Ukrainian"""
        keys = pygame.key.get_pressed()
        key_map = {
            'vverkh': pygame.K_UP, 'up': pygame.K_UP,
            'vnyz': pygame.K_DOWN, 'down': pygame.K_DOWN, 'vniz': pygame.K_DOWN,
            'vlivo': pygame.K_LEFT, 'left': pygame.K_LEFT, 'nalevo': pygame.K_LEFT,
            'vpravo': pygame.K_RIGHT, 'right': pygame.K_RIGHT, 'napravo': pygame.K_RIGHT,
            'probil': pygame.K_SPACE, 'space': pygame.K_SPACE, 'probel': pygame.K_SPACE,
            'enter': pygame.K_RETURN,
            'escape': pygame.K_ESCAPE,
            'w': pygame.K_w, 'a': pygame.K_a, 's': pygame.K_s, 'd': pygame.K_d, 'q': pygame.K_q, 'e': pygame.K_e, 'r': pygame.K_r, 't': pygame.K_t, 'y': pygame.K_y, 'u': pygame.K_u, 'i': pygame.K_i, 'o': pygame.K_o, 'p': pygame.K_p, 'l': pygame.K_l, 'k': pygame.K_k, 'j': pygame.K_j, 'h': pygame.K_h, 'f': pygame.K_f, 'g': pygame.K_g, 'z': pygame.K_z, 'x': pygame.K_x, 'c': pygame.K_c, 'v': pygame.K_v, 'b': pygame.K_b, 'n': pygame.K_n, 'm': pygame.K_m,
            'shift': pygame.K_LSHIFT, 'ctrl': pygame.K_LCTRL, 'alt': pygame.K_LALT, 'enter': pygame.K_RETURN, 'enterKP': pygame.K_KP_ENTER
        }
        key_code = key_map.get(klavisha_nazva.lower())
        if key_code:
            return keys[key_code]
        return False
    
    def key_pressed(self, key_name):
        """Check if key is pressed - English"""
        return self.klvisha_natysnuty(key_name)
    
    def klavisha_nazhata(self, imya_klavishi):
        """Check if key is pressed - Russian"""
        return self.klvisha_natysnuty(imya_klavishi)
    
    def pozytsiya_myshi(self):
        """Get mouse position - Ukrainian"""
        pos = pygame.mouse.get_pos()
        return list(pos)  # Return as array [x, y]
    
    def mouse_position(self):
        """Get mouse position - English"""
        return self.pozitsiya_myshi()
    
    def pozitsiya_myshi(self):
        """Get mouse position - Russian"""
        return self.pozitsiya_myshi()
    
    def mysha_natysnuta(self, knopka=0):
        """Check if mouse button pressed - Ukrainian"""
        buttons = pygame.mouse.get_pressed()
        if knopka < len(buttons):
            return buttons[knopka]
        return False
    
    def mouse_pressed(self, button=0):
        """Check if mouse button pressed - English"""
        return self.mysha_natysnuta(button)
    
    def mysh_nazhata(self, knopka=0):
        """Check if mouse button pressed - Russian"""
        return self.mysha_natysnuta(knopka)
    
    # Text rendering
    def napysaty_tekst(self, text, x, y, kolir, rozmir=24):
        """Draw text - Ukrainian"""
        font = pygame.font.Font(None, rozmir)
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            text_surface = font.render(str(text), True, kolir)
            self.screen.blit(text_surface, (x, y))
        else:
            raise ValueError("Color must be [R, G, B] array, kozache!")
    
    def draw_text(self, text, x, y, color, size=24):
        """Draw text - English"""
        self.napysaty_tekst(text, x, y, color, size)
    
    def napisat_tekst(self, text, x, y, tsvet, razmer=24):
        """Draw text - Russian"""
        self.napysaty_tekst(text, x, y, tsvet, razmer)
    
    # Sprite/Image handling
    def zavantazhyty_zobrazhennya(self, shlyakh, nazva):
        """Load image - Ukrainian"""
        try:
            image = pygame.image.load(shlyakh)
            self.sprites[nazva] = image
            return True
        except:
            return False
    
    def load_image(self, path, name):
        """Load image - English"""
        return self.zavantazhyty_zobrazhennya(path, name)
    
    def zagruzit_izobrazhenie(self, put, imya):
        """Load image - Russian"""
        return self.zavantazhyty_zobrazhennya(put, imya)
    
    def namalyuvaty_zobrazhennya(self, nazva, x, y):
        """Draw loaded image - Ukrainian"""
        if nazva in self.sprites:
            self.screen.blit(self.sprites[nazva], (x, y))
        else:
            raise ValueError(f"Image '{nazva}' not loaded, kozache!")
    
    def draw_image(self, name, x, y):
        """Draw loaded image - English"""
        self.namalyuvaty_zobrazhennya(name, x, y)
    
    def narisovat_izobrazhenie(self, imya, x, y):
        """Draw loaded image - Russian"""
        self.namalyuvaty_zobrazhennya(imya, x, y)
    
    # Sound handling
    def zavantazhyty_zvuk(self, shlyakh, nazva):
        """Load sound - Ukrainian"""
        try:
            sound = pygame.mixer.Sound(shlyakh)
            self.sounds[nazva] = sound
            return True
        except:
            return False
    
    def load_sound(self, path, name):
        """Load sound - English"""
        return self.zavantazhyty_zvuk(path, name)
    
    def zagruzit_zvuk(self, put, imya):
        """Load sound - Russian"""
        return self.zavantazhyty_zvuk(put, imya)
    
    def vidtvoryty_zvuk(self, nazva):
        """Play sound - Ukrainian"""
        if nazva in self.sounds:
            self.sounds[nazva].play()
        else:
            raise ValueError(f"Sound '{nazva}' not loaded, kozache!")
    
    def play_sound(self, name):
        """Play sound - English"""
        self.vidtvoryty_zvuk(name)
    
    def vosproizvesti_zvuk(self, imya):
        """Play sound - Russian"""
        self.vidtvoryty_zvuk(imya)
    
    # Cleanup
    def zakryty(self):
        """Close game window - Ukrainian"""
        self.running = False
        if pygame.get_init():
            try:
                pygame.quit()
            except:
                pass
    
    def close(self):
        """Close game window - English"""
        self.zakryty()
    
    def zakryt(self):
        """Close game window - Russian"""
        self.zakryty()