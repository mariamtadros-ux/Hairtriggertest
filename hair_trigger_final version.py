"""
HAIR TRIGGER - a reactive character game (Pygame)

CODE ORIGIN AND ACKNOWLEDGEMENTS
-------------------------------
This project was developed by the student over approximately 2.5 weeks. The
student began without prior Python or game-development experience and learned
through experimentation, independent implementation, debugging, and the
learning resources listed below. These resources informed the student's
general understanding of Python/Pygame and game-development workflows. The
student also adapted ideas and examples while learning, then modified and
combined them for this project. A function-by-function record of which exact
example informed each implementation was not kept, so this file does not
misattribute a particular function to a tutorial without evidence. The game's
specific character, hair-cutting logic, reaction system, dialogue, interaction
zones, interface, and combination of features were developed for this project.

Learning resources consulted during development (video titles/authors should be
confirmed by the student before adding full bibliographic details):
- https://www.youtube.com/watch?v=dz9_-2G6o3o
- https://www.youtube.com/watch?v=H09PmP5tsy8
- https://www.youtube.com/watch?v=Ak1IDnP5IrI&list=PLlEgNdBJEO-muprNCDYiKLZ-Kc3-p8thS
- https://www.youtube.com/watch?v=yR_pLQHTlHI&t=180s

The game uses Pygame, an external library. Pygame provides the underlying
window, drawing, input, surface, font, and timing APIs; the game's use of those
APIs is implemented in this project. See https://www.pygame.org/docs/ .

If a specific block of code is later identified as directly adapted from a
source, add a more precise attribution immediately above that block, including
the source title, author/channel, URL, and what was adapted.

Core idea: whatever you do to the character, the character reacts.

Two systems work together:
  1. INTERACTION DETECTION - what did the player just do?
     (cut hair, scribble with the marker, wash the face)
  2. REACTIVE STATE - the character's mood (facial expression) and
     dialogue are chosen from that action, and from how many times
     the player has been annoying so far.

The game has three SCREENS (called "states" in the code):
  "title"   - the start screen with instructions
  "playing" - the main game
  "ending"  - shown when nearly all the hair has been cut off

Controls
  1 = scissors (click and drag across the hair)
  2 = marker   (click and drag on the face)
  W = wash the marker off      R = grow the hair back / restart
  ESC = quit

How to run:  python hair_trigger.py
(You need Pygame installed first: pip install pygame-ce)

All graphics are drawn with code (shapes and lines), so no image files
are needed.
"""

# ----------------------------------------------------------------------------
# IMPORTS
# An "import" loads a toolbox of ready-made code that someone else wrote.
#   math   - maths functions (square root, distance, pi)
#   random - random numbers (used so hair and dialogue vary every time)
#   sys    - lets us exit the program cleanly
#   pygame - the game library: windows, drawing, mouse, keyboard, timing
# ----------------------------------------------------------------------------
import math
import random
import sys

import pygame

# ----------------------------------------------------------------------------
# SETTINGS
# These are VARIABLES: names that store a value. Writing them in CAPITALS at
# the top is a habit that means "this is a setting, it never changes while the
# game runs". If I want a different window size, I change one number here
# instead of hunting through the whole file.
# ----------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 640          # window size in pixels
FPS = 60                          # frames (screen redraws) per second

CX, CY = 400, 330                 # centre of the face
FACE_RX, FACE_RY = 105, 135       # the face is an ellipse: half-width, half-height
HAIR_RX, HAIR_RY, HAIR_CY = 118, 150, CY - 5   # the arc that the hair grows from
HAIR_STRANDS = 70                 # how many hair strands the character has
CUT_RADIUS = 10                   # how close the scissors must be to cut a strand

ENDING_HAIR_LEFT = 0.10           # the game ends when 10% (or less) of the hair is left
LIVE_CUT_STEP = 300               # react while cutting after this many pixels of hair removed...
LIVE_CUT_GAP_MS = 700             # ...but never more often than once every 0.7 seconds
ANGER_MAX_SHOWN = 8.0             # anger value that fills the anger bar completely

# Colours are written as (red, green, blue), each from 0 to 255.
# A fourth number (like INK's 255) is "alpha" = how see-through it is.
BG = (250, 235, 242)
WALL_TOP = (252, 228, 240)        # top of the background gradient
WALL_BOTTOM = (244, 190, 218)     # bottom of the background gradient
SKIN = (240, 200, 160)
SKIN_SHADE = (222, 180, 140)
HAIR = (70, 40, 90)
SHIRT = (214, 75, 140)
DARK = (40, 30, 40)
WHITE = (255, 255, 255)
INK = (30, 60, 200, 255)
BLUSH = (232, 110, 110)           # red cheeks when angry
HAPPY_BLUSH = (246, 170, 165)     # soft pink cheeks when happy
TEAR = (120, 180, 255)
BAR_BACK = (236, 222, 230)        # empty part of a progress bar
GREEN = (110, 200, 140)
ORANGE = (250, 170, 70)
RED = (225, 70, 80)
SELECTED = (255, 190, 220)        # highlight colour for the chosen tool button

# Which colour the anger bar uses for each baseline mood.
# A DICTIONARY pairs a "key" (the mood name) with a "value" (the colour).
BAR_COLOURS = {"neutral": GREEN, "annoyed": ORANGE, "angry": RED}

# How long (in milliseconds) a reaction lasts before the character calms down
MOOD_MS = 2500
TEXT_MS = 3200


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# A FUNCTION is a named block of code that does one job. We "call" it by name
# whenever we need that job done, instead of copying the same code again.
# ----------------------------------------------------------------------------
def inside_face(x, y):
    """True if the point (x, y) is inside the face ellipse.
    Uses the ellipse equation: ((x-cx)/rx)^2 + ((y-cy)/ry)^2 <= 1."""
    return ((x - CX) / FACE_RX) ** 2 + ((y - CY) / FACE_RY) ** 2 <= 1


def zone_of(x, y):
    """Which part of the face is this point on? The answer decides which
    reaction the character gives (drawing on the eyes is worse than the cheek)."""
    # Check both eyes. math.hypot gives the distance between two points.
    for ex in (CX - 40, CX + 40):
        if math.hypot(x - ex, y - (CY - 15)) < 26:
            return "eyes"
    # Check the mouth area (a small rectangle around the mouth)
    if abs(x - CX) < 32 and abs(y - (CY + 48)) < 20:
        return "mouth"
    # Anywhere else on the face
    if inside_face(x, y):
        return "face"
    return None                    # not on the face at all


def interpolate(a, b, step=4):
    """Give back points along the line from a to b, one every `step` pixels.
    The mouse can move many pixels between two frames. Without this, the
    scissors would 'jump over' hair strands. This fills in the gaps.
    (`yield` hands back one point at a time instead of building a whole list.)"""
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(dist // step))              # how many small steps to take
    for i in range(1, n + 1):
        t = i / n                              # 0 -> 1 as we move from a to b
        yield (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def make_background():
    """Build the background picture ONCE (not every frame, which would be slow).
    A loop draws one horizontal line per row, slowly changing colour from
    WALL_TOP to WALL_BOTTOM. That makes a smooth gradient. Then a few soft
    circles are added for decoration."""
    surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT                         # 0.0 at the top, 1.0 at the bottom
        colour = tuple(int(WALL_TOP[i] + (WALL_BOTTOM[i] - WALL_TOP[i]) * t)
                       for i in range(3))      # blend each of R, G, B
        pygame.draw.line(surface, colour, (0, y), (WIDTH, y))
    maker = random.Random(7)                   # fixed seed = same circles every run
    for _ in range(14):
        x = maker.randint(0, WIDTH)
        y = maker.randint(0, HEIGHT)
        radius = maker.randint(20, 70)
        pygame.draw.circle(surface, (255, 240, 247), (x, y), radius)
    return surface


# ----------------------------------------------------------------------------
# HAIR
# Strand and Clump are project-specific classes for this game's hair behaviour.
# Their implementation was developed for Hair Trigger; general class and Pygame
# concepts were learned through the resources acknowledged in the file header.
# A CLASS is a blueprint for making objects. Each Strand object stores its own
# numbers (where it starts, where it ends, how much is left) and has its own
# functions (called METHODS). Making 70 strands = using the blueprint 70 times.
# ----------------------------------------------------------------------------
class Strand:
    """One hair strand: a straight line from its root (x0, y0) to its tip (x1, y1).
    `keep` is how much of it remains (1.0 = full length, 0.0 = gone)."""

    def __init__(self, x0, y0, x1, y1):
        # __init__ runs automatically when a new Strand is created.
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.length = math.hypot(x1 - x0, y1 - y0)
        self.keep = 1.0

    def point(self, t):
        """The point a fraction t of the way from root (t=0) to tip (t=1)."""
        return (self.x0 + (self.x1 - self.x0) * t,
                self.y0 + (self.y1 - self.y0) * t)

    def nearest(self, p):
        """Find the spot on this strand closest to point p.
        Returns (t, distance): t says WHERE on the strand, distance says HOW FAR.
        This is how the game detects 'the scissors touched the hair'."""
        dx, dy = self.x1 - self.x0, self.y1 - self.y0
        t = ((p[0] - self.x0) * dx + (p[1] - self.y0) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))              # keep t between 0 and 1
        q = self.point(t)
        return t, math.hypot(p[0] - q[0], p[1] - q[1])


class Clump:
    """A cut piece of hair that falls down the screen."""

    def __init__(self, p0, p1):
        self.p0, self.p1 = list(p0), list(p1)
        self.vx = random.uniform(-1.2, 1.2)    # sideways drift
        self.vy = 0.0                          # falling speed (starts at 0)

    def update(self):
        self.vy += 0.45                        # gravity: fall faster every frame
        for p in (self.p0, self.p1):
            p[0] += self.vx
            p[1] += self.vy

    def draw(self, screen):
        pygame.draw.line(screen, HAIR, self.p0, self.p1, 7)


def make_hair():
    """Build the hairstyle: short fringe in the middle, long at the sides.
    Returns a LIST of Strand objects (a list holds many items in order)."""
    strands = []
    for i in range(HAIR_STRANDS):
        dx = -HAIR_RX + 2 * HAIR_RX * i / (HAIR_STRANDS - 1)   # left to right
        frac = abs(dx) / HAIR_RX                # 0 at the centre ... 1 at the sides
        y0 = HAIR_CY - HAIR_RY * math.sqrt(max(0.0, 1 - frac ** 2))
        length = 55 + 150 * frac ** 2 + random.uniform(-10, 15)  # longer at the sides
        x1 = CX + dx + math.copysign(10 * frac, dx) + random.uniform(-5, 5)
        strands.append(Strand(CX + dx, y0, x1, y0 + length))
    return strands


# ----------------------------------------------------------------------------
# REACTION LOGIC (the "brain" of the game)
# Reactor's mood thresholds, counters, and dialogue responses are designed for
# Hair Trigger. They are not presented as a copied tutorial implementation.
# The Reactor remembers what the player has done and decides the character's
# mood and dialogue. It uses IF STATEMENTS to branch: "if this happened, react
# like this, otherwise react like that".
# ----------------------------------------------------------------------------
class Reactor:
    """Decides how the character reacts. Each on_* method returns a pair:
    (mood, dialogue line).

    `anger` is the character's grudge. It goes up with every annoying action
    and slowly cools down. The same action gets a worse reaction the more you
    repeat it - that is the 'hair trigger'."""

    def __init__(self):
        self.anger = 0.0
        self.cut_count = 0         # how many reactions to cutting so far
        self.scribble_count = 0    # how many reactions to drawing so far
        self.wash_count = 0        # how many times the face was washed
        self.last_line = ""        # remembered so we don't repeat the same line twice

    def baseline(self):
        """The mood the character settles back to when nothing is happening.
        It depends on how angry they are overall."""
        if self.anger >= 5:
            return "angry"
        if self.anger >= 2.5:
            return "annoyed"
        return "neutral"

    def mood_name(self):
        """A friendly word for the anger bar and the ending screen."""
        base = self.baseline()
        if base == "angry":
            return "Furious"
        if base == "annoyed":
            return "Annoyed"
        return "Calm"

    def verdict(self):
        """The character's final opinion of the player (ending screen)."""
        if self.anger >= 5:
            return "Furious. Do not expect a tip."
        if self.anger >= 2.5:
            return "Annoyed, but might forgive you."
        return "Strangely calm. Maybe they like it?"

    def _pick(self, lines):
        """Choose a random line from a list, avoiding the one used last time."""
        options = [line for line in lines if line != self.last_line] or lines
        self.last_line = random.choice(options)
        return self.last_line

    def on_cut(self, hair_left):
        """React to hair being cut. `hair_left` is between 0 and 1.
        The less hair is left, the stronger the reaction."""
        self.cut_count += 1
        self.anger += 0.7
        if hair_left < 0.12:
            return "sad", self._pick(["...I'm basically bald now.",
                                      "Was that really necessary?",
                                      "My beautiful hair... gone."])
        if hair_left < 0.4:
            return "angry", self._pick(["WHERE IS MY HAIR GOING?!",
                                        "STOP CUTTING!",
                                        "That was my favourite length!",
                                        "I just washed that!"])
        if hair_left < 0.7:
            return "shocked", self._pick(["Okay... that's a lot.",
                                          "Um. How much are you taking off?",
                                          "Is it supposed to be that short?",
                                          "Wait, wait, wait!"])
        if self.cut_count <= 2:
            return "happy", self._pick(["Ooh, a little trim. Nice!",
                                        "Just a trim, right? Right?",
                                        "That feels lighter already."])
        return "annoyed", self._pick(["Okay, that's enough trimming.",
                                      "You keep snipping...",
                                      "I said a TRIM."])

    def on_scribble(self, zones):
        """React to marker drawing. `zones` is the set of face areas touched
        (some of "eyes", "mouth", "face")."""
        self.scribble_count += 1
        if "eyes" in zones:                    # eyes are the worst place
            self.anger += 1.0
            return "angry", self._pick(["HEY! I can't see!",
                                        "Not on my eyes!",
                                        "It's dark in here!"])
        if "mouth" in zones:
            self.anger += 0.8
            return "shocked", self._pick(["Mmf! Not the mouth!",
                                          "Ew, ink in my mouth!",
                                          "Bleh! That tastes awful!"])
        self.anger += 0.5                      # just the cheeks or forehead
        if self.scribble_count >= 4:
            return "angry", self._pick(["STOP DRAWING ON ME!",
                                        "I'm not a notebook!",
                                        "That's enough art!"])
        if self.scribble_count == 1:
            return "shocked", self._pick(["Is that... marker?!",
                                          "Wait, is that permanent?"])
        return "annoyed", self._pick(["Seriously?", "Really? Again?",
                                      "Why are you like this?"])

    def on_wash(self, had_ink):
        """React to the face being washed. Washing calms the character down,
        but if they are still very angry they stay grumpy."""
        if not had_ink:
            return "neutral", "I'm already clean?"
        self.wash_count += 1
        self.anger = max(0.0, self.anger - 2.0)
        if self.anger >= 2.5:
            return "annoyed", self._pick(["Thanks... but I'm still mad at you.",
                                          "Cleaner, sure. Forgiven? Not yet."])
        return "happy", self._pick(["Ahh, thank you.", "Much better. Thanks.",
                                    "Fresh and clean!"])


# ----------------------------------------------------------------------------
# THE GAME
# The Game class and its event handling, tool interactions, drawing, and state
# transitions bring together the student's project-specific implementation.
# Pygame itself supplies the underlying library APIs (acknowledged above).
# The Game class holds everything: the window, the hair, the ink layer, the
# current screen ("state"), and the functions that run the game.
# ----------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()                          # start up Pygame
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))   # open the window
        pygame.display.set_caption("Hair Trigger")
        self.clock = pygame.time.Clock()       # used to keep the game at 60 FPS

        # Fonts: None means "use Pygame's built-in font"; the number is the size
        self.big = pygame.font.Font(None, 96)
        self.med = pygame.font.Font(None, 40)
        self.font = pygame.font.Font(None, 30)
        self.small = pygame.font.Font(None, 24)

        self.background = make_background()     # the pretty gradient (built once)
        # A see-through white sheet, drawn over the game on the ending screen
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((255, 255, 255, 150))
        # A transparent layer that the marker draws on (so it can be washed off)
        self.ink = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.mouse = (CX, CY + 250)            # latest mouse position
        self.prev = self.mouse                 # mouse position in the previous frame
        self.tool = "scissors"                 # which tool is selected
        self.dragging = False                  # is the mouse button held down?
        self.running = True                    # the main loop runs while this is True

        self.reset(greet=True)                 # set up a fresh game...
        self.state = "title"                   # ...but start on the title screen

    # ---- state ------------------------------------------------------------
    def reset(self, greet=False):
        """Start a fresh game: new hair, clean face, calm character."""
        self.state = "playing"                 # "title", "playing" or "ending"
        self.hair = make_hair()
        self.falling = []                      # cut hair that is falling
        self.snips = []                        # little rings shown where we cut
        self.ink.fill((0, 0, 0, 0))            # wipe the ink layer
        self.ink_used = False
        self.reactor = Reactor()               # a brand new, calm brain
        self.mood, self.mood_until = "neutral", 0
        self.text, self.text_until = "", 0
        self.ending_at = None                  # time when the ending screen appears
        self.last_cut_reaction = -10000        # time of the last reaction to cutting
        self.dragging = False
        self.begin_stroke()
        if greet:
            self.react("happy", "Hi! Be gentle with me.")
        else:
            self.react("happy", "Fresh start!")

    def begin_stroke(self):
        """A 'stroke' is one click-and-drag. Reset the counters for a new one."""
        self.cut_amount = 0.0                  # pixels of hair cut during this drag
        self.cut_reacted_at = 0.0              # how much had been cut at the last reaction
        self.stroke_points = 0                 # marker dots drawn during this drag
        self.stroke_zones = set()              # face zones touched during this drag
        self.reacted_zones = set()             # zones the character already reacted to
        self.stroke_reacted = False            # has the character reacted to this stroke?

    def hair_left(self):
        """What fraction of the hair is left? (1.0 = all, 0.0 = none)"""
        total = sum(s.length for s in self.hair)
        left = sum(s.length * s.keep for s in self.hair)
        return left / total

    def react(self, mood, line):
        """Show a mood and a speech bubble for a short time."""
        now = pygame.time.get_ticks()          # milliseconds since the game started
        self.mood, self.mood_until = mood, now + MOOD_MS
        self.text, self.text_until = line, now + TEXT_MS

    def current_mood(self):
        """The mood to draw right now: a recent reaction, or else the baseline."""
        if pygame.time.get_ticks() < self.mood_until:
            return self.mood
        return self.reactor.baseline()

    # ---- input ------------------------------------------------------------
    def handle_event(self, event):
        """Deal with ONE thing the player did (key press, mouse click, etc.).
        Pygame collects these as 'events'. What we do depends on the screen."""
        if event.type == pygame.QUIT:          # the window's close button
            self.running = False
            return
        if event.type == pygame.MOUSEMOTION:   # the mouse moved
            self.mouse = event.pos
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
            return

        # --- title screen: any click, SPACE or ENTER starts the game ---
        if self.state == "title":
            started_by_key = (event.type == pygame.KEYDOWN and
                              event.key in (pygame.K_SPACE, pygame.K_RETURN))
            started_by_click = (event.type == pygame.MOUSEBUTTONDOWN and
                                event.button == 1)
            if started_by_key or started_by_click:
                self.reset(greet=True)
            return

        # --- ending screen: only R (play again) works ---
        if self.state == "ending":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # --- playing ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.tool = "scissors"
            elif event.key == pygame.K_2:
                self.tool = "marker"
            elif event.key == pygame.K_w:      # wash the face
                self.react(*self.reactor.on_wash(self.ink_used))
                self.ink.fill((0, 0, 0, 0))
                self.ink_used = False
            elif event.key == pygame.K_r:      # grow the hair back
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left mouse button pressed: a new stroke starts
            self.mouse = self.prev = event.pos
            self.dragging = True
            self.begin_stroke()
            self.apply_tool(self.mouse)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Left mouse button released: the stroke is finished
            if self.dragging:
                self.end_stroke()
            self.dragging = False

    # ---- tools ------------------------------------------------------------
    def apply_tool(self, p):
        """Use whichever tool is selected at point p."""
        if self.tool == "scissors":
            self.snip(p)
        else:
            self.scribble(p)

    def snip(self, p):
        """Cut every strand the scissors touch, from the touch point down.
        This is the hair-cutting detection: for each strand we ask 'how far is
        the scissors point from this strand?'. If it is closer than CUT_RADIUS
        the strand is cut there."""
        cut_something = False
        for s in self.hair:                    # loop through all 70 strands
            if s.keep <= 0.02:                 # already (almost) gone
                continue
            t, d = s.nearest(p)
            if d < CUT_RADIUS and t < s.keep:
                # The lower part of the strand becomes a falling clump
                self.falling.append(Clump(s.point(t), s.point(s.keep)))
                self.cut_amount += (s.keep - t) * s.length
                s.keep = t                     # the strand is now shorter
                cut_something = True
        if cut_something:
            # A little ring that grows and fades where we cut (visual feedback)
            self.snips.append([p[0], p[1], pygame.time.get_ticks()])
            # LIVE REACTION: react while still cutting, not only at the end.
            # Two checks stop the character from reacting 20 times in one swipe:
            # enough hair must be cut AND enough time must have passed.
            now = pygame.time.get_ticks()
            enough_cut = self.cut_amount - self.cut_reacted_at >= LIVE_CUT_STEP
            enough_time = now - self.last_cut_reaction >= LIVE_CUT_GAP_MS
            if enough_cut and enough_time:
                self.cut_reacted_at = self.cut_amount
                self.last_cut_reaction = now
                self.react(*self.reactor.on_cut(self.hair_left()))

    def scribble(self, p):
        """Draw ink at point p, but only if p is on the face."""
        if not inside_face(*p):
            return
        pygame.draw.circle(self.ink, INK, (int(p[0]), int(p[1])), 3)
        self.ink_used = True
        self.stroke_points += 1
        zone = zone_of(*p)
        if zone:
            self.stroke_zones.add(zone)
        # LIVE REACTION: after a few dots the character reacts. If the stroke
        # later reaches the eyes or mouth for the first time, it reacts again.
        if self.stroke_points >= 6:
            new_important = [z for z in self.stroke_zones
                             if z in ("eyes", "mouth") and z not in self.reacted_zones]
            if not self.stroke_reacted or new_important:
                self.stroke_reacted = True
                self.reacted_zones.update(self.stroke_zones)
                self.react(*self.reactor.on_scribble(self.stroke_zones))

    def end_stroke(self):
        """The drag just ended. If some hair was cut since the last live
        reaction, the character reacts to that too."""
        if self.tool == "scissors" and self.cut_amount - self.cut_reacted_at > 20:
            self.last_cut_reaction = pygame.time.get_ticks()
            self.react(*self.reactor.on_cut(self.hair_left()))

    # ---- update -----------------------------------------------------------
    def update(self):
        """Change the game's state a little bit. Runs once per frame."""
        now = pygame.time.get_ticks()

        # While the mouse button is held, use the tool along the mouse path
        if self.state == "playing" and self.dragging:
            for p in interpolate(self.prev, self.mouse):
                self.apply_tool(p)
        self.prev = self.mouse

        # Move falling hair, and forget hair that has fallen off the screen
        for c in self.falling:
            c.update()
        self.falling = [c for c in self.falling if c.p0[1] < HEIGHT + 50]

        # Forget snip rings that are older than a quarter of a second
        self.snips = [s for s in self.snips if now - s[2] < 250]

        # The character slowly cools down
        self.reactor.anger = max(0.0, self.reactor.anger - 0.0015)

        # Has the player cut almost everything? Then wait 2.5 s and end the game.
        if self.state == "playing":
            if self.ending_at is None and self.hair_left() <= ENDING_HAIR_LEFT:
                self.ending_at = now + 2500
                self.react("sad", "It's... all gone.")
            if self.ending_at is not None and now >= self.ending_at:
                self.state = "ending"
                self.dragging = False

    # ---- drawing helpers --------------------------------------------------
    def text_at(self, text, font, colour, x, y, centered=True):
        """Draw text on the screen. If centered, (x, y) is the middle of the
        text; otherwise it is the top-left corner."""
        label = font.render(text, True, colour)
        rect = label.get_rect()
        if centered:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(label, rect)

    def draw_bar(self, x, y, w, h, fraction, colour):
        """A progress bar: an empty box, filled by `fraction` (0 to 1)."""
        fraction = max(0.0, min(1.0, fraction))
        pygame.draw.rect(self.screen, BAR_BACK, (x, y, w, h), border_radius=8)
        if fraction > 0:
            pygame.draw.rect(self.screen, colour, (x, y, int(w * fraction), h),
                             border_radius=8)
        pygame.draw.rect(self.screen, DARK, (x, y, w, h), 2, border_radius=8)

    # ---- drawing: the character ------------------------------------------
    def draw_character(self, mood):
        """Draw the whole character using only shapes. The `mood` decides the
        eyes, eyebrows and mouth. Order matters: things drawn later appear on top."""
        s = self.screen

        # body: neck and shirt
        pygame.draw.rect(s, SKIN_SHADE, (CX - 30, CY + 110, 60, 70))
        pygame.draw.ellipse(s, SHIRT, (CX - 150, CY + 150, 300, 200))

        # ears and face
        for side in (-1, 1):                   # -1 = left side, 1 = right side
            pygame.draw.circle(s, SKIN, (CX + side * FACE_RX, CY + 5), 18)
        pygame.draw.ellipse(s, SKIN, (CX - FACE_RX, CY - FACE_RY,
                                      2 * FACE_RX, 2 * FACE_RY))

        # cheeks
        if mood == "angry":
            for side in (-1, 1):
                pygame.draw.circle(s, BLUSH, (CX + side * 70, CY + 20), 12)
        elif mood == "happy":
            for side in (-1, 1):
                pygame.draw.circle(s, HAPPY_BLUSH, (CX + side * 70, CY + 22), 10)

        # eyes (the pupils follow the mouse)
        ey = CY - 15
        r = 20 if mood == "shocked" else 15    # shocked eyes are bigger
        for ex in (CX - 40, CX + 40):
            if mood == "happy":                # happy = closed, smiling eyes
                pygame.draw.arc(s, DARK, (ex - 14, ey - 8, 28, 24), 0, math.pi, 4)
                continue
            pygame.draw.circle(s, WHITE, (ex, ey), r)
            pygame.draw.circle(s, DARK, (ex, ey), r, 2)
            # Work out which direction the mouse is, to move the pupil that way
            dx, dy = self.mouse[0] - ex, self.mouse[1] - ey
            dist = max(1.0, math.hypot(dx, dy))
            k = min(5.0, dist / 20)            # how far the pupil can move
            pr = 4 if mood == "shocked" else 7  # shocked = tiny pupils
            pygame.draw.circle(s, DARK, (int(ex + dx / dist * k),
                                         int(ey + dy / dist * k)), pr)
            if mood == "annoyed":              # half-closed eyelid
                pygame.draw.rect(s, SKIN, (ex - r - 1, ey - r - 1, 2 * r + 2, r + 4))
                pygame.draw.line(s, DARK, (ex - r, ey + 3), (ex + r, ey + 3), 3)
            if mood == "sad":                  # a tear
                pygame.draw.circle(s, TEAR, (ex - 4, ey + r + 8), 5)

        # eyebrows: for each mood, (height of outer end, height of inner end)
        brows = {"neutral": (-45, -45), "shocked": (-60, -60),
                 "annoyed": (-38, -38), "angry": (-55, -36),
                 "sad": (-38, -52), "happy": (-50, -50)}
        outer, inner = brows[mood]
        for side in (-1, 1):
            pygame.draw.line(s, HAIR, (CX + side * 60, CY + outer),
                             (CX + side * 22, CY + inner), 5)

        # mouth: a different shape for each mood
        if mood == "neutral":
            pygame.draw.line(s, DARK, (CX - 14, CY + 50), (CX + 14, CY + 50), 3)
        elif mood == "shocked":
            pygame.draw.ellipse(s, (120, 40, 50), (CX - 12, CY + 40, 24, 30))
            pygame.draw.ellipse(s, DARK, (CX - 12, CY + 40, 24, 30), 3)
        elif mood == "annoyed":
            pygame.draw.line(s, DARK, (CX - 16, CY + 53), (CX + 14, CY + 48), 3)
        elif mood == "angry":                  # gritted teeth
            teeth = pygame.Rect(CX - 22, CY + 44, 44, 18)
            pygame.draw.rect(s, WHITE, teeth, border_radius=4)
            pygame.draw.rect(s, DARK, teeth, 3, border_radius=4)
            for tx in (CX - 11, CX, CX + 11):
                pygame.draw.line(s, DARK, (tx, teeth.top), (tx, teeth.bottom), 2)
        elif mood == "sad":                    # small frown
            pygame.draw.arc(s, DARK, (CX - 16, CY + 50, 32, 20), 0, math.pi, 4)
        elif mood == "happy":                  # big smile
            pygame.draw.arc(s, DARK, (CX - 24, CY + 30, 48, 34), math.pi, 2 * math.pi, 4)

        # ink goes on top of the face, then the hair goes on top of everything
        s.blit(self.ink, (0, 0))
        for st in self.hair:
            if st.keep > 0.02:
                pygame.draw.line(s, HAIR, st.point(0), st.point(st.keep), 7)
                pygame.draw.circle(s, HAIR, [int(v) for v in st.point(st.keep)], 3)
        for c in self.falling:
            c.draw(s)

    def draw_effects(self):
        """Little rings that grow and fade where the scissors just cut."""
        now = pygame.time.get_ticks()
        for x, y, born in self.snips:
            age = now - born                   # how old is this ring (ms)
            radius = 6 + age // 12             # older rings are bigger
            pygame.draw.circle(self.screen, SHIRT, (int(x), int(y)), radius, 2)

    def draw_bubble(self):
        """The speech bubble with the character's current line."""
        if pygame.time.get_ticks() > self.text_until:
            return                              # the line has expired: show nothing
        label = self.font.render(self.text, True, DARK)
        w, h = label.get_size()
        rect = pygame.Rect(0, 0, w + 36, h + 24)
        rect.center = (CX, 105)
        tail = [(CX - 12, rect.bottom - 1), (CX + 12, rect.bottom - 1),
                (CX, rect.bottom + 22)]
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=14)
        pygame.draw.rect(self.screen, DARK, rect, 2, border_radius=14)
        pygame.draw.polygon(self.screen, WHITE, tail)
        pygame.draw.lines(self.screen, DARK, False, tail, 2)
        pygame.draw.line(self.screen, WHITE, tail[0], tail[1], 3)   # hide the join
        self.screen.blit(label, (rect.x + 18, rect.y + 12))

    def draw_ui(self):
        """The tool buttons along the top. The selected tool is highlighted."""
        items = [("scissors", "[1] Scissors"), ("marker", "[2] Marker"),
                 (None, "[W] Wash face"), (None, "[R] Reset hair")]
        x = 16
        for tool, text in items:
            label = self.small.render(text, True, DARK)
            rect = pygame.Rect(x, 8, label.get_width() + 20, 28)
            colour = SELECTED if tool == self.tool else WHITE
            pygame.draw.rect(self.screen, colour, rect, border_radius=8)
            pygame.draw.rect(self.screen, DARK, rect, 1, border_radius=8)
            self.screen.blit(label, (rect.x + 10, rect.y + 6))
            x = rect.right + 10

        # The cursor: a ring for the scissors, a dot for the marker
        mx, my = int(self.mouse[0]), int(self.mouse[1])
        if self.tool == "scissors":
            pygame.draw.circle(self.screen, DARK, (mx, my), CUT_RADIUS, 2)
        else:
            pygame.draw.circle(self.screen, INK[:3], (mx, my), 4)

    def draw_hud(self):
        """HUD = 'heads-up display': two bars at the bottom of the screen.
        Left: how much hair is left. Right: how angry the character is."""
        left = self.hair_left()
        self.text_at("Hair left: " + str(round(left * 100)) + "%",
                     self.small, DARK, 16, 578, centered=False)
        self.draw_bar(16, 602, 220, 18, left, HAIR)

        base = self.reactor.baseline()
        self.text_at("Mood: " + self.reactor.mood_name(),
                     self.small, DARK, WIDTH - 236, 578, centered=False)
        self.draw_bar(WIDTH - 236, 602, 220, 18,
                      self.reactor.anger / ANGER_MAX_SHOWN, BAR_COLOURS[base])

    # ---- drawing: whole screens ------------------------------------------
    def draw_title(self):
        """The start screen: title, short instructions, and a start prompt."""
        self.screen.blit(self.background, (0, 0))
        self.text_at("HAIR TRIGGER", self.big, SHIRT, CX + 3, 103)   # shadow
        self.text_at("HAIR TRIGGER", self.big, HAIR, CX, 100)
        self.text_at("Whatever you do to the character, the character reacts.",
                     self.font, DARK, CX, 160)

        panel = pygame.Rect(140, 200, 520, 270)
        pygame.draw.rect(self.screen, WHITE, panel, border_radius=16)
        pygame.draw.rect(self.screen, DARK, panel, 2, border_radius=16)
        self.text_at("HOW TO PLAY", self.med, SHIRT, CX, 228)

        lines = ["[1]  Scissors: click and drag across the hair",
                 "[2]  Marker: click and drag on the face",
                 "[W]  Wash the marker off",
                 "[R]  Grow the hair back and restart",
                 "[ESC]  Quit"]
        y = 266
        for line in lines:
            self.text_at(line, self.font, DARK, panel.x + 40, y, centered=False)
            y += 34
        self.text_at("Goal: cut off almost all the hair... and see how it feels.",
                     self.small, DARK, CX, 442)

        # Blinking prompt: shown for half a second, hidden for half a second
        if (pygame.time.get_ticks() // 600) % 2 == 0:
            self.text_at("Click or press SPACE to start", self.med, HAIR, CX, 530)
        self.text_at("Be careful. Every action changes how the character feels.",
                     self.small, DARK, CX, 600)

    def draw_ending(self):
        """The end screen: a summary of what the player did."""
        self.screen.blit(self.overlay, (0, 0))
        panel = pygame.Rect(CX - 230, 150, 460, 340)
        pygame.draw.rect(self.screen, WHITE, panel, border_radius=16)
        pygame.draw.rect(self.screen, DARK, panel, 2, border_radius=16)
        self.text_at("ALL DONE!", self.big, SHIRT, CX, 205)

        r = self.reactor
        lines = ["Snips: " + str(r.cut_count),
                 "Marker scribbles: " + str(r.scribble_count),
                 "Times washed: " + str(r.wash_count),
                 "Final mood: " + r.mood_name()]
        y = 275
        for line in lines:
            self.text_at(line, self.font, DARK, CX, y)
            y += 34
        self.text_at(r.verdict(), self.small, HAIR, CX, 425)
        self.text_at("Press R to play again   |   ESC to quit",
                     self.small, DARK, CX, 465)

    def draw(self):
        """Draw one complete frame, then show it on the screen."""
        if self.state == "title":
            self.draw_title()
        else:
            self.screen.blit(self.background, (0, 0))
            self.draw_character(self.current_mood())
            self.draw_effects()
            self.draw_bubble()
            self.draw_ui()
            self.draw_hud()
            if self.state == "ending":
                self.draw_ending()
        pygame.display.flip()                  # show everything we just drew

    # ---- main loop --------------------------------------------------------
    def step(self):
        """ONE trip around the game loop (this happens 60 times a second):
        1) check input, 2) update the game, 3) draw it, 4) wait for the next frame."""
        for event in pygame.event.get():
            self.handle_event(event)
        self.update()
        self.draw()
        self.clock.tick(FPS)                   # limit the speed to FPS frames/second

    def run(self):
        """Keep running frames until the player quits."""
        while self.running:
            self.step()
        pygame.quit()


# This line means: only start the game if THIS file was run directly
# (and not if it was imported by another file).
if __name__ == "__main__":
    Game().run()
    sys.exit()
