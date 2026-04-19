import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import sys
from core.dialect_messages import DialectMessages

class GameModule:
    def __init__(self, dialect=None):
        pygame.init()
        self.dialect = dialect
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.sprites = {}  # Store loaded sprites
        self.sounds = {}   # Store loaded sounds

        self.METHOD_DIALECTS = {
            #ukrainian latin
            'stvoryty_vikno': 'ukrainian_latin',
            'vstanovyty_ikonku': 'ukrainian_latin',
            'onovyty': 'ukrainian_latin',
            'vstanovyty_fps': 'ukrainian_latin',
            'zalyty': 'ukrainian_latin',
            'namalyuvaty_pryamokutnyk': 'ukrainian_latin',
            'namalyuvaty_kolo': 'ukrainian_latin',
            'namalyuvaty_liniyu': 'ukrainian_latin',
            'klavisha_natysnuta': 'ukrainian_latin',
            'pozytsiya_myshi': 'ukrainian_latin',
            'mysha_natysnuta': 'ukrainian_latin',
            'napysaty_tekst': 'ukrainian_latin',
            'zavantazhyty_zobrazhennya': 'ukrainian_latin',
            'namalyuvaty_zobrazhennya': 'ukrainian_latin',
            'zavantazhyty_zvuk': 'ukrainian_latin',
            'vidtvoryty_zvuk': 'ukrainian_latin',
            'zakryty': 'ukrainian_latin',

            #english
            'create_window': 'english',
            'set_icon': 'english',
            'update': 'english',
            'set_fps': 'english',
            'fill': 'english',
            'draw_rect': 'english',
            'draw_circle': 'english',
            'draw_line': 'english',
            'key_pressed': 'english',
            'mouse_position': 'english',
            'mouse_pressed': 'english',
            'draw_text': 'english',
            'load_image': 'english',
            'draw_image': 'english',
            'load_sound': 'english',
            'play_sound': 'english',
            'close': 'english',

            #russian latin
            'sozdat_okno': 'russian_latin',
            'ustanovit_ikonku': 'russian_latin',
            'obnovit': 'russian_latin',
            'ustanovit_fps': 'russian_latin',
            'zalit': 'russian_latin',
            'narisovat_pryamougolnik': 'russian_latin',
            'narisovat_krug': 'russian_latin',
            'narisovat_liniyu': 'russian_latin',
            'klavisha_nazhata': 'russian_latin',
            'pozitsiya_myshi': 'russian_latin',
            'mysh_nazhata': 'russian_latin',
            'napisat_tekst': 'russian_latin',
            'zagruzit_izobrazhenie': 'russian_latin',
            'narisovat_izobrazhenie': 'russian_latin',
            'zagruzit_zvuk': 'russian_latin',
            'vosproizvesti_zvuk': 'russian_latin',
            'zakryt': 'russian_latin',

            #ukrainian cyrillic
            'створити_вікно' : 'ukrainian_cyrillic',
            'встановити_іконку': 'ukrainian_cyrillic',
            'оновити': 'ukrainian_cyrillic',
            'встановити_фпс': 'ukrainian_cyrillic',
            'залити': 'ukrainian_cyrillic',
            'намалювати_прямокутник': 'ukrainian_cyrillic',
            'намалювати_коло': 'ukrainian_cyrillic',
            'намалювати_лінію': 'ukrainian_cyrillic',
            'клавіша_натиснута': 'ukrainian_cyrillic',
            'позиція_миші': 'ukrainian_cyrillic',
            'миша_натиснута': 'ukrainian_cyrillic',
            'написати_текст': 'ukrainian_cyrillic',
            'завантажити_зображення': 'ukrainian_cyrillic',
            'намалювати_зображення': 'ukrainian_cyrillic',
            'завантажити_звук': 'ukrainian_cyrillic',
            'відтворити_звук': 'ukrainian_cyrillic',
            'закрити': 'ukrainian_cyrillic',

            #russian cyrillic
            'создать_окно': 'russian_cyrillic',
            'установить_иконку': 'russian_cyrillic',
            'обновить': 'russian_cyrillic',
            'установить_фпс': 'russian_cyrillic',
            'залить': 'russian_cyrillic',
            'нарисовать_прямоугольник': 'russian_cyrillic',
            'нарисовать_круг': 'russian_cyrillic',
            'нарисовать_линию': 'russian_cyrillic',
            'клавиша_нажата': 'russian_cyrillic',
            'позиция_мыши': 'russian_cyrillic',
            'мышь_нажата': 'russian_cyrillic',
            'написать_текст': 'russian_cyrillic',
            'загрузить_изображение': 'russian_cyrillic',
            'нарисовать_изображение': 'russian_cyrillic',
            'загрузить_звук': 'russian_cyrillic',
            'воспроизвести_звук': 'russian_cyrillic',
            'закрыть': 'russian_cyrillic',           
        }

        
        
        # Color constants - Ukrainian
        self.CHORNYY = self.ЧОРНИЙ = (0, 0, 0)
        self.BILYY = self.БІЛИЙ = (255, 255, 255)
        self.CHERVONYY = self.ЧЕРВОНИЙ = (255, 0, 0)
        self.ZELENYY = self.ЗЕЛЕНИЙ = (0, 255, 0)
        self.SYNIY = self.СИНІЙ = (0, 0, 255)
        self.ZHOVTYY = self.ЖОВТИЙ = (255, 255, 0)
        self.POMARANCHEVYY = self.ПОМАРАНЧЕВИЙ = (255, 165, 0)
        self.FIOLETOVYY = self.ФІОЛЕТОВИЙ = (128, 0, 128)
        self.SIRYY = self.СІРИЙ = (128, 128, 128)

        # Color constants - Russian
        self.CHERNYY = self.ЧЕРНЫЙ = (0, 0, 0)
        self.BELYY = self.БЕЛЫЙ = (255, 255, 255)
        self.KRASNYY = self.КРАСНЫЙ = (255, 0, 0)
        self.ZELENYY = self.ЗЕЛЕНЫЙ = (0, 255, 0)
        self.SINIY = self.СИНИЙ = (0, 0, 255)
        self.ZHELTYY = self.ЖЕЛТЫЙ = (255, 255, 0)
        self.ORANZHEVYY = self.ОРАНЖЕВЫЙ = (255, 165, 0)
        self.FIOLETOVYY = self.ФИОЛЕТОВЫЙ = (128, 0, 128)
        self.SERYY = self.СЕРЫЙ = (128, 128, 128)

        # Color constants - English
        self.BLACK = (0,0,0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.GRAY = (128, 128, 128)

        # Add inside __init__, after the colour definitions:

        self.COLOUR_DIALECTS = {
            # Shared Latin Slavic — allowed in both ukrainian_latin and russian_latin
            'ZELENYY':    'shared_slavic',
            'FIOLETOVYY': 'shared_slavic',

            # Ukrainian Latin
            'CHORNYY': 'ukrainian_latin',  'BILYY': 'ukrainian_latin',
            'CHERVONYY': 'ukrainian_latin', 'SYNIY': 'ukrainian_latin',
            'ZHOVTYY': 'ukrainian_latin',  'POMARANCHEVYY': 'ukrainian_latin',
            'SIRYY': 'ukrainian_latin',

            # Russian Latin
            'CHERNYY': 'russian_latin',  'BELYY': 'russian_latin',
            'KRASNYY': 'russian_latin',  'SINIY': 'russian_latin',
            'ZHELTYY': 'russian_latin',  'ORANZHEVYY': 'russian_latin',
            'SERYY': 'russian_latin',

            # Ukrainian Cyrillic
            'ЧОРНИЙ': 'ukrainian_cyrillic',  'БІЛИЙ': 'ukrainian_cyrillic',
            'ЧЕРВОНИЙ': 'ukrainian_cyrillic', 'ЗЕЛЕНИЙ': 'ukrainian_cyrillic',
            'СИНІЙ': 'ukrainian_cyrillic',   'ЖОВТИЙ': 'ukrainian_cyrillic',
            'ПОМАРАНЧЕВИЙ': 'ukrainian_cyrillic', 'ФІОЛЕТОВИЙ': 'ukrainian_cyrillic',
            'СІРИЙ': 'ukrainian_cyrillic',

            # Russian Cyrillic
            'ЧЕРНЫЙ': 'russian_cyrillic',  'БЕЛЫЙ': 'russian_cyrillic',
            'КРАСНЫЙ': 'russian_cyrillic', 'ЗЕЛЕНЫЙ': 'russian_cyrillic',
            'СИНИЙ': 'russian_cyrillic',   'ЖЕЛТЫЙ': 'russian_cyrillic',
            'ОРАНЖЕВЫЙ': 'russian_cyrillic', 'ФИОЛЕТОВЫЙ': 'russian_cyrillic',
            'СЕРЫЙ': 'russian_cyrillic',

            # English
            'BLACK': 'english',  'WHITE': 'english',  'RED': 'english',
            'GREEN': 'english',  'BLUE': 'english',   'YELLOW': 'english',
            'ORANGE': 'english', 'PURPLE': 'english', 'GRAY': 'english',
        }

# Window management
    def stvoryty_vikno(self, shyryna, vysota, nazva="KozakScript Game"):
        self._dialect_guard('stvoryty_vikno')
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
        self._dialect_guard('create_window')
        return self.stvoryty_vikno(width, height, title)
    
    def sozdat_okno(self, shirina, vysota, nazvanie="KozakScript Game"):
        self._dialect_guard('sozdat_okno')
        return self.stvoryty_vikno(shirina, vysota, nazvanie)
    
    def vstanovyty_ikonku(self, shlyakh):
        self._dialect_guard('vstanovyty_ikonku')
        try:
            icon = pygame.image.load(shlyakh)
            pygame.display.set_icon(icon)
            return True
        except Exception as e:
            friendly = DialectMessages.friendly_term(self.dialect)
            raise ValueError(f"Failed to load icon '{shlyakh}', {friendly}: {e}")

    def set_icon(self, path):
        self._dialect_guard('set_icon')
        return self.vstanovyty_ikonku(path)

    def ustanovit_ikonku(self, put):
        self._dialect_guard('ustanovit_ikonku')
        return self.vstanovyty_ikonku(put)
    
    # Main game loop
    def onovyty(self):
        self._dialect_guard('onovyty')
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
        self._dialect_guard('update')
        return self.onovyty()
    
    def obnovit(self):
        self._dialect_guard('obnovit')
        return self.onovyty()
    
    # FPS control
    def vstanovyty_fps(self, fps):
        self._dialect_guard('vstanovyty_fps')
        self.clock.tick(fps)
    
    def set_fps(self, fps):
        self._dialect_guard('set_fps')
        self.vstanovyty_fps(fps)
    
    def ustanovit_fps(self, fps):
        self._dialect_guard('ustanovit_fps')
        self.vstanovyty_fps(fps)
    
    # Drawing functions
    def zalyty(self, kolir):
        self._dialect_guard('zalyty')
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            self.screen.fill(kolir)
        else:
            raise ValueError(self._color_error())
    
    def fill(self, color):
        self._dialect_guard('fill')
        self.zalyty(color)
    
    def zalit(self, tsvet):
        self._dialect_guard('zalit')
        self.zalyty(tsvet)
    
    def namalyuvaty_pryamokutnyk(self, kolir, x, y, shyryna, vysota):
        self._dialect_guard('namalyuvaty_pryamokutnyk')
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.rect(self.screen, kolir, (x, y, shyryna, vysota))
        else:
            raise ValueError(self._color_error())
    
    def draw_rect(self, color, x, y, width, height):
        self._dialect_guard('draw_rect')
        self.namalyuvaty_pryamokutnyk(color, x, y, width, height)
    
    def narisovat_pryamougolnik(self, tsvet, x, y, shirina, vysota):
        self._dialect_guard('narisovat_pryamougolnik')
        self.namalyuvaty_pryamokutnyk(tsvet, x, y, shirina, vysota)
    
    def namalyuvaty_kolo(self, kolir, x, y, radius):
        self._dialect_guard('namalyuvaty_kolo')
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.circle(self.screen, kolir, (x, y), radius)
        else:
            raise ValueError(self._color_error())
    
    def draw_circle(self, color, x, y, radius):
        self._dialect_guard('draw_circle')
        self.namalyuvaty_kolo(color, x, y, radius)
    
    def narisovat_krug(self, tsvet, x, y, radius):
        self._dialect_guard('narisovat_krug')
        self.namalyuvaty_kolo(tsvet, x, y, radius)
    
    def namalyuvaty_liniyu(self, kolir, x1, y1, x2, y2, tovshchyna=1):
        self._dialect_guard('namalyuvaty_liniyu')
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            pygame.draw.line(self.screen, kolir, (x1, y1), (x2, y2), tovshchyna)
        else:
            raise ValueError(self._color_error())
    
    def draw_line(self, color, x1, y1, x2, y2, width=1):
        self._dialect_guard('draw_line')
        self.namalyuvaty_liniyu(color, x1, y1, x2, y2, width)
    
    def narisovat_liniyu(self, tsvet, x1, y1, x2, y2, tolshchina=1):
        self._dialect_guard('narisovat_liniyu')
        self.namalyuvaty_liniyu(tsvet, x1, y1, x2, y2, tolshchina)
    
    # Input handling
    def klavisha_natysnuta(self, klavisha_nazva):
        self._dialect_guard('klavisha_natysnuta')
        keys = pygame.key.get_pressed()
        key_map = {
            'vverkh': pygame.K_UP, 'up': pygame.K_UP, 'vgoru': pygame.K_UP, 'вгору': pygame.K_UP, 'вверх': pygame.K_UP,
            'vnyz': pygame.K_DOWN, 'down': pygame.K_DOWN, 'vniz': pygame.K_DOWN, 'вниз': pygame.K_DOWN,
            'vlivo': pygame.K_LEFT, 'left': pygame.K_LEFT, 'nalevo': pygame.K_LEFT, 'вліво': pygame.K_LEFT, 'налево': pygame.K_LEFT,
            'vpravo': pygame.K_RIGHT, 'right': pygame.K_RIGHT, 'napravo': pygame.K_RIGHT, 'вправо': pygame.K_RIGHT, 'направо': pygame.K_RIGHT,
            'probil': pygame.K_SPACE, 'space': pygame.K_SPACE, 'probel': pygame.K_SPACE, 'пробіл': pygame.K_SPACE, 'пробел': pygame.K_SPACE, 
            'enter': pygame.K_RETURN,
            'escape': pygame.K_ESCAPE, 'esc': pygame.K_ESCAPE,
            'w': pygame.K_w, 'a': pygame.K_a, 's': pygame.K_s, 'd': pygame.K_d, 'q': pygame.K_q, 'e': pygame.K_e, 'r': pygame.K_r, 't': pygame.K_t, 'y': pygame.K_y, 'u': pygame.K_u, 'i': pygame.K_i, 'o': pygame.K_o, 'p': pygame.K_p, 'l': pygame.K_l, 'k': pygame.K_k, 'j': pygame.K_j, 'h': pygame.K_h, 'f': pygame.K_f, 'g': pygame.K_g, 'z': pygame.K_z, 'x': pygame.K_x, 'c': pygame.K_c, 'v': pygame.K_v, 'b': pygame.K_b, 'n': pygame.K_n, 'm': pygame.K_m,
            'shift': pygame.K_LSHIFT, 'ctrl': pygame.K_LCTRL, 'alt': pygame.K_LALT, 'enter': pygame.K_RETURN, 'enterKP': pygame.K_KP_ENTER
        }
        key_code = key_map.get(klavisha_nazva.lower())
        if key_code:
            return keys[key_code]
        return False
    
    def key_pressed(self, key_name):
        self._dialect_guard('key_pressed')
        return self.klavisha_natysnuta(key_name)
    
    def klavisha_nazhata(self, imya_klavishi):
        self._dialect_guard('klavisha_nazhata')
        return self.klavisha_natysnuta(imya_klavishi)
    
    def pozytsiya_myshi(self):
        self._dialect_guard('pozytsiya_myshi')
        pos = pygame.mouse.get_pos()
        return list(pos)  # Return as array [x, y]
    
    def mouse_position(self):
        self._dialect_guard('mouse_position')
        return self.pozytsiya_myshi()
    
    def pozitsiya_myshi(self):
        self._dialect_guard('pozitsiya_myshi')
        return self.pozytsiya_myshi()
    
    def mysha_natysnuta(self, knopka=0):
        self._dialect_guard('mysha_natysnuta')
        buttons = pygame.mouse.get_pressed()
        if knopka < len(buttons):
            return buttons[knopka]
        return False
    
    def mouse_pressed(self, button=0):
        self._dialect_guard('mouse_pressed')
        return self.mysha_natysnuta(button)
    
    def mysh_nazhata(self, knopka=0):
        self._dialect_guard('mysh_nazhata')
        return self.mysha_natysnuta(knopka)
    
    # Text rendering
    def napysaty_tekst(self, text, x, y, kolir, rozmir=24):
        self._dialect_guard('napysaty_tekst')
        font = pygame.font.Font(None, rozmir)
        if isinstance(kolir, (list, tuple)) and len(kolir) == 3:
            text_surface = font.render(str(text), True, kolir)
            self.screen.blit(text_surface, (x, y))
        else:
            raise ValueError(self._color_error())
    
    def draw_text(self, text, x, y, color, size=24):
        self._dialect_guard('draw_text')
        self.napysaty_tekst(text, x, y, color, size)
    
    def napisat_tekst(self, text, x, y, tsvet, razmer=24):
        self._dialect_guard('napisat_tekst')
        self.napysaty_tekst(text, x, y, tsvet, razmer)
    
    # Sprite/Image handling
    def zavantazhyty_zobrazhennya(self, shlyakh, nazva):
        self._dialect_guard('zavantazhyty_zobrazhennya')
        try:
            image = pygame.image.load(shlyakh)
            self.sprites[nazva] = image
            return True
        except:
            return False
    
    def load_image(self, path, name):
        self._dialect_guard('load_image')
        return self.zavantazhyty_zobrazhennya(path, name)
    
    def zagruzit_izobrazhenie(self, put, imya):
        self._dialect_guard('zagruzit_izobrazhenie')
        return self.zavantazhyty_zobrazhennya(put, imya)
    
    def namalyuvaty_zobrazhennya(self, nazva, x, y):
        self._dialect_guard('namalyuvaty_zobrazhennya')
        if nazva in self.sprites:
            self.screen.blit(self.sprites[nazva], (x, y))
        else:
            friendly = DialectMessages.friendly_term(self.dialect)
            raise ValueError(f"Image '{nazva}' not loaded, {friendly}!")
    
    def draw_image(self, name, x, y):
        self._dialect_guard('draw_image')
        self.namalyuvaty_zobrazhennya(name, x, y)
    
    def narisovat_izobrazhenie(self, imya, x, y):
        self._dialect_guard('narisovat_izobrazhenie')
        self.namalyuvaty_zobrazhennya(imya, x, y)
    
    # Sound handling
    def zavantazhyty_zvuk(self, shlyakh, nazva):
        self._dialect_guard('zavantazhyty_zvuk')
        try:
            sound = pygame.mixer.Sound(shlyakh)
            self.sounds[nazva] = sound
            return True
        except:
            return False
    
    def load_sound(self, path, name):
        self._dialect_guard('load_sound')
        return self.zavantazhyty_zvuk(path, name)
    
    def zagruzit_zvuk(self, put, imya):
        self._dialect_guard('zagruzit_zvuk')
        return self.zavantazhyty_zvuk(put, imya)
    
    def vidtvoryty_zvuk(self, nazva):
        self._dialect_guard('vidtvoryty_zvuk')
        if nazva in self.sounds:
            self.sounds[nazva].play()
        else:
            friendly = DialectMessages.friendly_term(self.dialect)
            raise ValueError(f"Sound '{nazva}' not loaded, {friendly}!")
    
    def play_sound(self, name):
        self._dialect_guard('play_sound')
        self.vidtvoryty_zvuk(name)
    
    def vosproizvesti_zvuk(self, imya):
        self._dialect_guard('vosproizvesti_zvuk')
        self.vidtvoryty_zvuk(imya)
    
    # Cleanup
    def zakryty(self):
        self._dialect_guard('zakryty')
        self.running = False
        if pygame.get_init():
            try:
                pygame.quit()
            except:
                pass
    
    def close(self):
        self._dialect_guard('close')
        self.zakryty()
    
    def zakryt(self):
        self._dialect_guard('zakryt')
        self.zakryty()

    # --- CYRILLIC WRAPPERS ---

    def створити_вікно(self, ширина, висота, назва="KozakScript Game"):
        self._dialect_guard('створити_вікно')
        return self.stvoryty_vikno(ширина, висота, назва)

    def встановити_іконку(self, шлях):
        self._dialect_guard('встановити_іконку')
        return self.vstanovyty_ikonku(шлях)

    def оновити(self):
        self._dialect_guard('оновити')
        return self.onovyty()

    def встановити_фпс(self, фпс):
        self._dialect_guard('встановити_фпс')
        self.vstanovyty_fps(фпс)

    def залити(self, колір):
        self._dialect_guard('залити')
        self.zalyty(колір)

    def намалювати_прямокутник(self, колір, x, y, ширина, висота):
        self._dialect_guard('намалювати_прямокутник')
        self.namalyuvaty_pryamokutnyk(колір, x, y, ширина, висота)

    def намалювати_коло(self, колір, x, y, радіус):
        self._dialect_guard('намалювати_коло')
        self.namalyuvaty_kolo(колір, x, y, радіус)

    def намалювати_лінію(self, колір, x1, y1, x2, y2, товщина=1):
        self._dialect_guard('намалювати_лінію')
        self.namalyuvaty_liniyu(колір, x1, y1, x2, y2, товщина)

    def клавіша_натиснута(self, назва_клавіші):
        self._dialect_guard('клавіша_натиснута')
        return self.klavisha_natysnuta(назва_клавіші)

    def позиція_миші(self):
        self._dialect_guard('позиція_миші')
        return self.pozytsiya_myshi()

    def миша_натиснута(self, кнопка=0):
        self._dialect_guard('миша_натиснута')
        return self.mysha_natysnuta(кнопка)

    def написати_текст(self, текст, x, y, колір, розмір=24):
        self._dialect_guard('написати_текст')
        self.napysaty_tekst(текст, x, y, колір, розмір)

    def завантажити_зображення(self, шлях, назва):
        self._dialect_guard('завантажити_зображення')
        return self.zavantazhyty_zobrazhennya(шлях, назва)

    def намалювати_зображення(self, назва, x, y):
        self._dialect_guard('намалювати_зображення')
        self.namalyuvaty_zobrazhennya(назва, x, y)

    def завантажити_звук(self, шлях, назва):
        self._dialect_guard('завантажити_звук')
        return self.zavantazhyty_zvuk(шлях, назва)

    def відтворити_звук(self, назва):
        self._dialect_guard('відтворити_звук')
        self.vidtvoryty_zvuk(назва)

    def закрити(self):
        self._dialect_guard('закрити')
        self.zakryty()

    def создать_окно(self, ширина, высота, название="KozakScript Game"):
        self._dialect_guard('создать_окно')
        return self.stvoryty_vikno(ширина, высота, название)

    def установить_иконку(self, путь):
        self._dialect_guard('установить_иконку')
        return self.vstanovyty_ikonku(путь)

    def обновить(self):
        self._dialect_guard('обновить')
        return self.onovyty()

    def установить_фпс(self, фпс):
        self._dialect_guard('установить_фпс')
        self.vstanovyty_fps(фпс)

    def залить(self, цвет):
        self._dialect_guard('залить')
        self.zalyty(цвет)

    def нарисовать_прямоугольник(self, цвет, x, y, ширина, высота):
        self._dialect_guard('нарисовать_прямоугольник')
        self.namalyuvaty_pryamokutnyk(цвет, x, y, ширина, высота)

    def нарисовать_круг(self, цвет, x, y, радиус):
        self._dialect_guard('нарисовать_круг')
        self.namalyuvaty_kolo(цвет, x, y, радиус)

    def нарисовать_линию(self, цвет, x1, y1, x2, y2, толщина=1):
        self._dialect_guard('нарисовать_линию')
        self.namalyuvaty_liniyu(цвет, x1, y1, x2, y2, толщина)

    def клавиша_нажата(self, имя_клавиши):
        self._dialect_guard('клавиша_нажата')
        return self.klavisha_natysnuta(имя_клавиши)

    def позиция_мыши(self):
        self._dialect_guard('позиция_мыши')
        return self.pozytsiya_myshi()

    def мышь_нажата(self, кнопка=0):
        self._dialect_guard('мышь_нажата')
        return self.mysha_natysnuta(кнопка)

    def написать_текст(self, текст, x, y, цвет, размер=24):
        self._dialect_guard('написать_текст')
        self.napysaty_tekst(текст, x, y, цвет, размер)

    def загрузить_изображение(self, путь, имя):
        self._dialect_guard('загрузить_изображение')
        return self.zavantazhyty_zobrazhennya(путь, имя)

    def нарисовать_изображение(self, имя, x, y):
        self._dialect_guard('нарисовать_изображение')
        self.namalyuvaty_zobrazhennya(имя, x, y)

    def загрузить_звук(self, путь, имя):
        self._dialect_guard('загрузить_звук')
        return self.zavantazhyty_zvuk(путь, имя)

    def воспроизвести_звук(self, имя):
        self._dialect_guard('воспроизвести_звук')
        self.vidtvoryty_zvuk(имя)

    def закрыть(self):
        self._dialect_guard('закрыть')
        self.zakryty()

    def _dialect_guard(self, method_name):
        effective_dialect = self.dialect
        if effective_dialect == 'symbolic':
            effective_dialect = 'english'

        if self.dialect is None:
            return

        required = self.METHOD_DIALECTS.get(method_name)
        if required and required != effective_dialect:
            friendly = DialectMessages.friendly_term(self.dialect)
            MESSAGES = {
                'ukrainian_latin':  (
                    f"Metod '{method_name}' nalezhyt' dialektu '{required}', "
                    f"ale tvoya prohrama vykorystovuye '{self.dialect}'. "
                    f"Vykorystovuy vidpovidnyk dlya '{self.dialect}', {friendly}!"
                ),
                'ukrainian_cyrillic': (
                    f"Метод '{method_name}' належить діалекту '{required}', "
                    f"але твоя програма використовує '{self.dialect}'. "
                    f"Використовуй відповідник для '{self.dialect}', {friendly}!"
                ),
                'russian_latin': (
                    f"Metod '{method_name}' prinadlezhit dialektu '{required}', "
                    f"no tvoya programma ispol'zuyet '{self.dialect}'. "
                    f"Ispol'zuy ekvivalent dlya '{self.dialect}', {friendly}!"
                ),
                'russian_cyrillic': (
                    f"Метод '{method_name}' принадлежит диалекту '{required}', "
                    f"но твоя программа использует '{self.dialect}'. "
                    f"Используй эквивалент для '{self.dialect}', {friendly}!"
                ),
                'symbolic': (
                    f"METHOD_DIALECT_MISMATCH: '{method_name}' requires dialect='{required}', "
                    f"current dialect='{self.dialect}'. Use correct dialect equivalent."
                ),
                'english': (
                    f"Method '{method_name}' belongs to the '{required}' dialect, "
                    f"but your program uses '{self.dialect}'. "
                    f"Use the '{self.dialect}' equivalent instead, {friendly}!"
                ),
            }
            raise ValueError(MESSAGES.get(self.dialect, MESSAGES['english']))

    def _color_error(self):
        """Return a dialect-aware error message for invalid color arguments."""
        friendly = DialectMessages.friendly_term(self.dialect)
        MESSAGES = {
            'ukrainian_latin':   f"Kolir povynen buty [R, G, B] masyvom, {friendly}!",
            'ukrainian_cyrillic': f"Колір повинен бути масивом [R, G, B], {friendly}!",
            'russian_latin':     f"Tsvet dolzhen byt' massivom [R, G, B], {friendly}!",
            'russian_cyrillic':  f"Цвет должен быть массивом [R, G, B], {friendly}!",
            'symbolic':          "INVALID_COLOR: expected [R,G,B] array.",
            'english':           f"Color must be a [R, G, B] array, {friendly}!",
        }
        return MESSAGES.get(self.dialect, MESSAGES['english'])
    
    def _emergency_quit(self):
        """Called when an error occurs mid-game to prevent freeze."""
        self.running = False
        if pygame.get_init():
            try:
                pygame.quit()
            except:
                pass

    
    def __getattribute__(self, name):
        """Intercept colour constant access to enforce dialect."""
        # Get COLOUR_DIALECTS safely without recursing
        colour_dialects = object.__getattribute__(self, 'COLOUR_DIALECTS') \
            if 'COLOUR_DIALECTS' in object.__getattribute__(self, '__dict__') \
            else {}

        if name in colour_dialects:
            dialect = object.__getattribute__(self, 'dialect')
            if dialect is not None:
                effective = 'english' if dialect == 'symbolic' else dialect
                required = colour_dialects[name]

                allowed = (
                    required == effective
                    or required == 'shared_slavic'
                    and effective in ('ukrainian_latin', 'russian_latin')
                )
                if not allowed:
                    friendly = DialectMessages.friendly_term(dialect)
                    if dialect == 'english':
                        raise ValueError(
                            f"Colour '{name}' belongs to the '{required}' dialect, "
                            f"but your program uses '{dialect}'. "
                            f"Use the '{dialect}' equivalent, {friendly}!"
                        )
                    elif dialect == 'ukrainian_cyrillic':
                        raise ValueError(
                            f"Колір '{name}' belongs to the '{required}' dialect, "
                            f"but your program uses '{dialect}'. "
                            f"Use the '{dialect}' equivalent, {friendly}!"
                        )
                    elif dialect == 'ukrainian_latin':
                        raise ValueError(
                            f"COLIR'{name}' belongs to the '{required}' dialect, "
                            f"but your program uses '{dialect}'. "
                            f"Use the '{dialect}' equivalent, {friendly}!"
                        )
                    elif dialect == 'russian_latin':
                        raise ValueError(
                            f"TSVET'{name}' belongs to the '{required}' dialect, "
                            f"but your program uses '{dialect}'. "
                            f"Use the '{dialect}' equivalent, {friendly}!"
                        )
                    elif dialect == 'russian_cyrillic':
                        raise ValueError(
                            f"ЦВЕТ'{name}' belongs to the '{required}' dialect, "
                            f"but your program uses '{dialect}'. "
                            f"Use the '{dialect}' equivalent, {friendly}!"
                        )

        return object.__getattribute__(self, name)