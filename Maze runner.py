# Declarem les llibreries que utilitzarem
import pygame
import numpy as np
import random
import math

# Definim les variables que deprés ens serivarn com a colors. Els valors són valors RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (50, 200, 255)

FILL = BLACK
TEXT = WHITE
# Inicialitzem la llibreria pygame
pygame.init()

# Especifiquem l'estructura de la xarxa neuronal. Aquí incluim la capa d'entrada i la de sortida.
# Exemple: 3 neurones a la capa d'entrada, 6 neurones a la capa de sortida i 2 capes ocultes amb 4 i 5 neurones
# cadascuna. En cas de voler canviar l'arquitectura de la xarxa, es primordial canviar aquests valors
# sempre es poden afegir més capes ocultes a la xarxa.

layer_structure = [3, 4, 5, 6]

# Inicialitzem la pantalla amb una mida 800x800
size = (800, 800)
screen = pygame.display.set_mode(size)
# Definim el nom de la finestra.
pygame.display.set_caption("ESG IA")

# Definim els coeficients amb els quals mutarem el nostre genoma.
testCoefs = [np.array([[0.38238344, 0.7515745, 0.29565119, 0.35490288, 0.97040034],
                       [0.33545982, 0.0973694, 0.41539856, 0.76129553, 0.93089118],
                       [0.85154809, -0.0240888, 0.74555908, -0.34759429, 0.37355357],
                       [0.95104127, 0.29077331, 0.21244898, 0.78876218, 0.35243364]]),
             np.array([[0.25498077, 0.91735276, 0.76089995],
                       [0.36535132, 0.60519588, 0.08365677],
                       [0.12852428, 0.0156597, -0.03317768],
                       [0.1276382, 0.13700435, 0.6786845],
                       [0.71931642, 0.8930938, 0.24538791]])]


# La calsse "Pared" ens permetrà mostrar les parets
class Pared(pygame.sprite.Sprite):
    # Creem la funció del constructor
    def __init__(self, x, y, llargada, altura, color):
        # Cridem al constructor pare de la llibreria pygame
        super().__init__()

        # Creem una paret amb les característiques que haguem definit
        self.image = pygame.Surface([llargada, altura])
        self.image.fill(color)

        # Establim el punt de referència en la cantonada superior esquerra.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x


# La classe "Player" ens permetrà crear diversos objectes player que seràn qui jugaran al joc.
class Player(pygame.sprite.Sprite):
    # Creem el constructor de la classe.
    def __init__(self, x=30, y=350, xspeed=0, yspeed=0, coefs=0, intercepts=0):
        # Tornem a cridar al constructor pare per la classe Player.
        super().__init__()
        # Definim totes les variables que actuaran a la calsse Player, és a dir,
        # les característiques dels objectes.
        self.PosControl = 0
        self.poScore = 0
        self.image = pygame.Surface([15, 15])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.secondChance = 0
        self.ShallDie = False
        self.rect.x = x
        self.rect.y = y
        self.ylast = y - yspeed
        self.xlast = x - xspeed
        self.yspeed = yspeed
        self.xspeed = xspeed
        self.alive = True
        self.score = self.rect.x - 20
        self.command = 2
        self.winner = False
        # Generem els coeficients per a l'objecte.
        if coefs == 0:
            self.coefs = self.generateCoefs(layer_structure)
        else:
            self.coefs = coefs
        if intercepts == 0:
            self.intercepts = self.generateIntercepts(layer_structure)
        else:
            self.intercepts = intercepts

    # Creem coeficients aletoris per a la xarxa neuronal
    @staticmethod
    def generateCoefs(layer_structure):
        coefs = []
        for i in range(len(layer_structure) - 1):
            # Afegim els valors creats al vector coefs
            coefs.append(np.random.rand(layer_structure[i], layer_structure[i + 1]) * 2 - 1)
        return coefs

    # Creem interceptors aletoris per a la xarxa neuronal
    @staticmethod
    def generateIntercepts(layer_structure):
        intercepts = []
        for i in range(len(layer_structure) - 1):
            intercepts.append(np.random.rand(layer_structure[i + 1]) * 2 - 1)
        return intercepts

    # Retorna els coeficients mutats
    def mutateCoefs(self):
        newCoefs = self.coefs.copy()
        for i in range(len(newCoefs)):
            for row in range(len(newCoefs[i])):
                for col in range(len(newCoefs[i][row])):
                    newCoefs[i][row][col] = np.random.normal(newCoefs[i][row][col], 1)
        return newCoefs

    # Retorna els interceptors mutats
    def mutateIntercepts(self):
        newIntercepts = self.intercepts.copy()
        for i in range(len(newIntercepts)):
            for row in range(len(newIntercepts[i])):
                newIntercepts[i][row] = np.random.normal(newIntercepts[i][row], 1)
        return newIntercepts

    # Actualitzem els coeficients i els interceptors dels jugador amb els nous mutats
    def mutate(self):
        return Player(coefs=self.mutateCoefs(), intercepts=self.mutateIntercepts())

    # Aquest mètode reseteja els valors predeterminats del objecte.
    def reset(self):
        self.rect.x = 30
        self.rect.y = 350
        self.ylast = 30
        self.xlast = 350
        self.xspeed = 0
        self.yspeed = 0
        self.alive = True
        self.score = 0
        self.poScore = 0
        self.PosControl = 0

    # Actualitzem la posició basant-nos en la velocitat
    def update(self, parets):
        self.xlast = self.rect.x
        self.ylast = self.rect.y

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > size[0]:
            self.rect.x = size[0]
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > size[1]:
            self.rect.y = size[1] - 35
        # Comprovem que l'objecte no hagi col·lisionat amb res
        self.rect.y += self.yspeed
        llista_impactes_blocs = pygame.sprite.spritecollide(self, parets, False)
        # Comprovem cada bloc
        for bloc in llista_impactes_blocs:
            # Si l'objecte es desplaça cap a la dreta i toca un objecte, detectem la col·lisió fent que el costat dret del jugador sigui el costat
            # esquerra del bloc amb el que hem col·lisionat.
            if self.yspeed > 0:
                self.rect.bottom = bloc.rect.top

            else:
                # En el cas contrari, fem l'oposat.
                self.rect.top = self.rect.bottom

        # Fem el mateix que anteriorment, però pels impactes d'adalt a baix

        self.rect.x += self.xspeed

        llista_impactes_blocs = pygame.sprite.spritecollide(self, parets, False)

        for bloc in llista_impactes_blocs:

            if self.xspeed > 0:

                self.rect.right = bloc.rect.left

            else:
                self.rect.left = bloc.rect.right

        if (self.PosControl) % 2 == 0:
            self.score = self.poScore + Scorey[self.PosControl] - self.rect.y + self.rect.x
        else:
            self.score = self.poScore + Scorey[self.PosControl] + self.rect.y + self.rect.x

        if (self.rect.x) > xPassControl[self.PosControl]:
            self.poScore = self.score + 352
            self.PosControl += 1
        self.xlast = self.rect.x
        self.ylast = self.rect.y

    def returnIndex(self):
        return self.PosControl

    # Dibuixem la figura del jugador

    def draw(self):
        if not self.winner:
            pygame.draw.rect(screen, BLACK, [self.rect.x, self.rect.y, 15, 15])
            pygame.draw.rect(screen, RED, [self.rect.x + 2, self.rect.y, 15 - 4, 15 - 4])
        else:
            pygame.draw.rect(screen, BLACK, [self.rect.x, self.rect.y, 15, 15])
            pygame.draw.rect(screen, BLUE, [self.rect.x + 2, self.rect.y, 15 - 4, 15 - 4])


class Nivell:
    """ Classe base per a tots els nivells"""

    # Tots els nivells tenen una llista amb la posició de les parets
    pared_lista = None

    def __init__(self):
        """ Constructor, creem les variables generals. """
        self.pared_lista = pygame.sprite.Group()


# Definim uns vectors que utilitzarem més tard

Parets1 = []
Scorey = []
ReferenceY = []
xPassControl = []


class Nivell1(Nivell):
    """Aquesta classe crea totes les parets del nivell 1"""

    def __init__(self):
        super().__init__()

        # Creem la llista amb les parets de cada nivell, on les dades signifiquen [x, y, largo, alto]
        varr = random
        parets = [[0, 0, 20, 350, GREEN],
                  [0, 350, 20, 250, GREEN],
                  [20, 0, 760, 20, GREEN],

                  [780, 0, 20, 250, GREEN],

                  [780, 350, 20, 250, GREEN],  # Parets que delimiten l'espai de joc
                  [20, 580, 760, 20, GREEN, 0],
                  # Obstacles
                  [50, 200, 10, 500,RED, 0],
                  [100, 20, 10, 500, RED, 1],
                  [150, varr.randint(40, 300), 10, 500, RED, 2],
                  [200, 20, 10, 500, RED, 3],
                  [250, varr.randint(40, 300), 10, 500, RED, 4],
                  [300, 20, 10, 500, RED, 5],
                  [350, varr.randint(40, 300), 10, 500, RED, 6],
                  [400, 20, 10, 500, RED, 7],
                  [450, varr.randint(40, 300), 10, 500, RED, 8],
                  [500, 20, 10, 500, RED, 9],
                  [550, varr.randint(40, 300), 10, 500, RED, 10],
                  [600, 20, 10, 500, RED, 11],
                  [650, varr.randint(40, 300), 10, 500, RED, 12],
                  # pared
                  [700, 20, 10, 500, RED, 13],[20, 580, 760, 20, GREEN]
                  ]

        # iterem  a través de la llista. Creem un objecte pared i l'afegim a la llista.
        ddd = 0
        for item in parets:
            pared = Pared(item[0], item[1] + 200, item[2], item[3], item[4])
            Parets1.append((item[0] - 100, item[1]))
            # Per a tots els obstacles extrellem la cordenada x i y per tal de poder calcular més tard 
            # els punts amb que conta cada jugador. 
            if ddd > 5 and ddd<20:
                Scorey.append(item[1] + 100)
                xPassControl.append(item[0])
            self.pared_lista.add(pared)
            ddd += 1
        Parets1.append((780 - 100, 550))
        Scorey.append(550)
        xPassControl.append(820)


# Prediu els valors de sortida per a un cert valor d'entrada donat un vector de coeficients i un vector d'interceptors
def calculateOutput(input, layer_structure, coefs, intercepts, g="identity"):
    # g es la funció d'activació que utilitzarem
    # Els valors de les neurones de cada capa, estaran guardades en "layers", així que la capa d'entrada s'afegeix al principi d'aquestes capes
    # (Transposem la matriu entrada per a obtenir columnes per a fer una multiplicació matricial)
    layers = [np.transpose(input)]

    # Cada capa es veurà affectada per la capa anterior, així que definim
    # la "previousLayer" inicial com el input (valor d'entrada.)
    previousLayer = np.transpose(input)

    reduced_layer_structure = layer_structure[1:]
    # Fem un bucle per totes les capes excepte la capa d'entrada.
    for k in range(len(reduced_layer_structure)):

        # Creem un vector buit de la mida correcta.
        currentLayer = np.empty((reduced_layer_structure[k], 1))

        # La capa resultant es el resultat de la multiplicació matricial de previousLayer i els coefficients més la matriu interceptos.
        result = np.matmul(np.transpose(coefs[k]), previousLayer) + np.transpose(np.array([intercepts[k]]))

        # Passem el valor de cada neurona per la funció d'activació g()       
        for i in range(len(currentLayer)):
            if g == "identity":
                currentLayer[i] = result[i]
            elif g == "relu":
                currentLayer[i] = max(0, result[i])
            elif g == "tanh":
                currentLayer[i] = np.tanh(result[i])
            elif g == "logistic":
                try:
                    currentLayer[i] = 1 / (1 + np.exp(-1 * result[i]))
                except OverflowError:
                    currentLayer[i] = 0

        # Afegim currentLayer a la llista de capes (layers) i actualitzem la variable previousLayer
        layers.append(currentLayer)
        previousLayer = currentLayer.copy()

    # Retornem l'index de la neurona amb màxim valor a la capa de sortida (layers[-1])
    # Exemple: si la neurona 5 te el màxim valor, retorna 5
    return layers[-1].tolist().index(max(layers[-1].tolist()))


# Retorna una varietat de coefficients que són una mutació dels inputs
def mutateCoefs(coefs):
    newCoefs = []
    for array in coefs:
        newCoefs.append(np.copy(array))
    for i in range(len(newCoefs)):
        for row in range(len(newCoefs[i])):
            for col in range(len(newCoefs[i][row])):
                newCoefs[i][row][col] = np.random.normal(newCoefs[i][row][col], 1)
    return newCoefs


# Retorna una varietat de interceptors que són una mutació dels inputs

def mutateIntercepts(intercepts):
    newIntercepts = []
    for array in intercepts:
        newIntercepts.append(np.copy(array))
    for i in range(len(newIntercepts)):
        for row in range(len(newIntercepts[i])):
            newIntercepts[i][row] = np.random.normal(newIntercepts[i][row], 1)
    return newIntercepts


# Mostra els nodes de la xarxa, així com els pesos (weights) representat amb linies i la influencia del coeficient.
def displayNetwork(layer_sctructure, coefs):
    # Gurada el coeficient més gran, cosa que ens permet escalar el grossor de les linies.
    max_coef = np.max(coefs[0])
    # Determina l'espai que ocupa la xarxa a la pantalla
    height = 200
    width = 300

    inputs = []
    cdd = 0

    inputs = ["PosX", "PosY", "Distància"]
    outputs = ["Left", "Right", "X stop", "Up", "Down", "Y stop"]

    layerCount = len(layer_structure)
    # Guarda les posicións de tots els nodes
    circle_positions = []

    # Etiquetes dels inputs
    for i in range(layer_structure[0]):
        font = pygame.font.SysFont('Calibri', 20, False, False)
        text = font.render(inputs[i], True, TEXT)
        screen.blit(text, [40, (i + 1) * int(height / (layer_structure[0] + 2)) + 20])

    # Etiquetes dels outputs
    for i in range(layer_structure[-1]):
        font = pygame.font.SysFont('Calibri', 20, False, False)
        text = font.render(str(outputs[i]), True, TEXT)
        screen.blit(text, [width + 85, (i + 1) * int(height / (layer_structure[-1] + 2)) + 15])
    # Calcula l'espai entre capes
    xspacing = int(width / layerCount)
    # Determina la posició de les neuornes per cada capa, guarda aquesta posició a una llista
    # i guarda aquesta llista en circle_positions
    for i in range(layerCount):
        layer_circle_positions = []
        yspacing = int(height / (layer_structure[i] + 2))
        for j in range(layer_structure[i]):
            layer_circle_positions.append(((i + 1) * xspacing + 60, (j + 1) * yspacing + 30))
        circle_positions.append(layer_circle_positions)
    # Dibuixa una linia entre cada neurona en una capa, i cada neurona a la capa següent.
    for i in range(len(circle_positions) - 1):
        for j, circle_pos in enumerate(circle_positions[i]):
            for k, circle_pos2 in enumerate(circle_positions[i + 1]):
                thickness = int(coefs[i][j, k] / max_coef * 8)

                if thickness > 0:
                    pygame.draw.lines(screen, BLUE, False, [circle_pos, circle_pos2], thickness)
                else:
                    pygame.draw.lines(screen, RED, False, [circle_pos, circle_pos2], -thickness)

    # Dibuixa els cercles en la posició pertinent.
    for layer in circle_positions:
        for circle_pos in layer:
            pygame.draw.circle(screen, BLACK, circle_pos, 20, 0)
            pygame.draw.circle(screen, GREEN, circle_pos, 16, 0)


done = False
score = 0
command = "stop"
clock = pygame.time.Clock()

COUNT = 100

# Crea els spties jugador
players = []
# Crea els spties nivells
cuartos = []

cuarto = Nivell1()
cuartos.append(cuarto)
cuarto_actual_no = 0
cuarto_actual = cuartos[cuarto_actual_no]

for i in range(100):
    players.append(Player())

# El primer guanyador es escollit arbitrariament per a ser l'ultima instancia de l'objecte (per a mostrar alguna cosa)
winner = players[-1]
players[-1].winner = True

# Comença el bucle principal del joc
victory = 0
generation = 1
b = 0
MXScore = 0
cu = 0
c = 0
finalisimo = False
while not done:
    screen.fill(FILL)
    cuarto_actual.pared_lista.draw(screen)
    still_alive = 0
    # Porta un recompte de la puntuació màxima
    highP = 0
    high_score = -9e99
    high_score_index = -1

    # Permet a l'usuari sortir del joc en qualsevol moment

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Fa un bulce per totes les instancies de jugador

    for i, player in enumerate(players):
        # Recull els inputs de cada jugador

        input = np.array([[player.rect.x, player.rect.y]])
        # Calculem el mòdul de la distancia entre el paddle i la punta de la paret més propera
        if player.returnIndex() % 2 == 0:
            distancia = -80 + math.sqrt((Parets1[player.returnIndex() + 6][0] - player.rect.x) ** 2 + (
                    Parets1[player.returnIndex() + 6][1] - player.rect.y) ** 2)
            distancia = -distancia
        else:
            distancia = -410 + math.sqrt(
                (Parets1[player.returnIndex() + 6][0] + 500 - player.rect.x) ** 2 + (
                        Parets1[player.returnIndex() + 6][1] + 500 - player.rect.y) ** 2)

        newa = np.array([[distancia]])

        input = np.append(input, newa, axis=1)

        layer_structure[0] = int(input.size)
        player.command = calculateOutput(input, layer_structure, player.coefs, player.intercepts)

        # 0=left, 1=right, 2=xstop, 3=up, 4=down, 5=ystop
        if player.command == 0:
            player.xspeed = -10
        elif player.command == 1:
            player.xspeed = 10
        elif player.command == 2:
            player.xspeed = 0
        elif player.command == 3:
            player.yspeed = -10
        elif player.command == 4:
            player.yspeed = 10
        elif player.command == 5:
            player.yspeed = 0

        # Actualitzem la posició dels jugadors

        if player.alive == True:
            player.update(cuarto_actual.pared_lista)  # poner: (cuarto_actual.pared_lista)
            still_alive += 1

        if player.rect.x > 784 and player.winner == True:
            finalisimo = True
            break

        # Els punts màxims pasen a ser el high score
        if player.score > high_score:
            high_score = player.score
            high_score_index = i
            winner = players[i]
            winner.winner = True

        if MXScore < high_score:
            MXScore = high_score

        # Dibuixa tot menys el guanyador
        if player.alive and player != winner:
            player.draw()
            player.winner = False

    # dibuixem el guanyador després, així fem que estigui al front
    players[high_score_index].draw()
    cuarto_actual.pared_lista.draw(screen)
    # Condició per a canviar de generació
    if still_alive == 0 or b > 3 + generation / 2:
        generation += 1
        winner.reset()
        players = []
        b = 0
        for i in range(COUNT - 1):
            players.append(Player(coefs=mutateCoefs(winner.coefs), intercepts=mutateIntercepts(winner.intercepts)))
        players.append(winner)
    # Condició per a canviar de nivell
    if cuarto_actual_no == c and finalisimo == True:
        cuarto_actual_no = c + 1
        c += 1
        cuarto = Nivell1()
        cuartos.append(cuarto)
        cuarto_actual = cuartos[cuarto_actual_no]
        victory += 1
        winner.reset()
        players = []
        b = 0
        for i in range(COUNT - 1):
            players.append(Player(coefs=mutateCoefs(winner.coefs), intercepts=mutateIntercepts(winner.intercepts)))
        players.append(winner)
        finalisimo = False
    # Mostrem informació útil per a l'usuari
    b = b + (clock.get_time() / 1000)
    font = pygame.font.SysFont('Calibri', 25, False, False)
    # Punts del guanyador
    text = font.render("Score = " + str(math.trunc(high_score / 10)), True, TEXT)
    screen.blit(text, [size[0] - 325, 0])
    # Punts màxims obtinguts en el nivell
    text = font.render("MXScore = " + str(math.trunc(MXScore / 10)), True, TEXT)
    screen.blit(text, [size[0] - 325, 30])
    # Generació actual
    text2 = font.render("Generació = " + str(generation), True, TEXT)
    screen.blit(text2, [size[0] - 325, 60])
    # Temps que porta en la partida, i temps restant per a actualitzar la generació
    text2 = font.render("Temps = " + str(math.trunc(b)) + " de " + str(math.trunc(3 + generation / 2)) + " s", True,
                        TEXT)
    screen.blit(text2, [size[0] - 325, 90])
    # Nivell
    text = font.render(("Nivell:  " + str(victory)), True, TEXT)
    screen.blit(text, [size[0] - 325, 120])
    text2 = font.render("Xarxa neuronal del guanyador:", True, TEXT)
    screen.blit(text2, [size[0] - 790, 0])
    displayNetwork(layer_structure, winner.coefs)

    pygame.display.flip()
    clock.tick(60)
