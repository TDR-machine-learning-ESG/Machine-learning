import pygame
import numpy as np
import random
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (50, 200, 255)
FILL = BLACK
TEXT = WHITE

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
VIOLETA = (255, 0, 255)

pygame.init()


# Here you can specify the structure of the neural network. This includes the input layer and output layer.
# e.g 3 inputs, 5 node hidden layer, 4 outputs would be [3, 5, 4]
# Be sure to update this if you add inputs
layer_structure = [3,4,5,6]

# Initializing the display window
size = (800, 900)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("pong")

testCoefs = [np.array([[0.38238344, 0.7515745, 0.29565119, 0.35490288, 0.97040034],
                       [0.33545982, 0.0973694, 0.41539856, 0.76129553, 0.93089118],
                       [0.85154809, -0.0240888, 0.74555908, -0.34759429, 0.37355357],
                       [0.95104127, 0.29077331, 0.21244898, 0.78876218, 0.35243364]]),
             np.array([[0.25498077, 0.91735276, 0.76089995],
                       [0.36535132, 0.60519588, 0.08365677],
                       [0.12852428, 0.0156597, -0.03317768],
                       [0.1276382, 0.13700435, 0.6786845],
                       [0.71931642, 0.8930938, 0.24538791]])]


# Paddle class
class Pared(pygame.sprite.Sprite):
    """Esta clase representa la barra inferior que controla el protagonista """

    def __init__(self, x, y, largo, alto, color):
        """ Función Constructor """

        # Llama al constructor padre
        super().__init__()

        # Crea una pared AZUL, con las dimensiones especificadas en los parámetros
        self.image = pygame.Surface([largo, alto])
        self.image.fill(color)

        # Establece como origen la esquina superior izquierda.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x


class Paddle(pygame.sprite.Sprite):

    def __init__(self, x=30, y=450, xspeed=0, yspeed=0, coefs=0, intercepts=0):

        super().__init__()
        self.PosControl = 0
        self.poScore =0
        self.image = pygame.Surface([15, 15])
        self.image.fill(VIOLETA)
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
        self.score = self.rect.x -20
        self.command = 2
        self.winner = False
        if coefs == 0:
            self.coefs = self.generateCoefs(layer_structure)
        else:
            self.coefs = coefs
        if intercepts == 0:
            self.intercepts = self.generateIntercepts(layer_structure)
        else:
            self.intercepts = intercepts

    # Creates random coefficients for the neural network
    @staticmethod
    def generateCoefs(layer_structure):
        coefs = []
        for i in range(len(layer_structure) - 1):
            coefs.append(np.random.rand(layer_structure[i], layer_structure[i + 1]) * 2 - 1)
        return coefs

    # Creates random intercepts for the neural network
    @staticmethod
    def generateIntercepts(layer_structure):
        intercepts = []
        for i in range(len(layer_structure) - 1):
            intercepts.append(np.random.rand(layer_structure[i + 1]) * 2 - 1)
        return intercepts

    # Returns mutated coefs
    def mutateCoefs(self):
        newCoefs = self.coefs.copy()
        for i in range(len(newCoefs)):
            for row in range(len(newCoefs[i])):
                for col in range(len(newCoefs[i][row])):
                    newCoefs[i][row][col] = np.random.normal(newCoefs[i][row][col], 1)
        return newCoefs

    # Returns mutated intercepts
    def mutateIntercepts(self):
        newIntercepts = self.intercepts.copy()
        for i in range(len(newIntercepts)):
            for row in range(len(newIntercepts[i])):
                newIntercepts[i][row] = np.random.normal(newIntercepts[i][row], 1)
        return newIntercepts

    # Returns a paddle with mutated coefs and intercepts
    def mutate(self):
        return Paddle(coefs=self.mutateCoefs(), intercepts=self.mutateIntercepts())

    # Reset score, speed and position
    def reset(self):
        self.rect.x = 20
        self.rect.y = 450
        self.ylast = 30
        self.xlast = 450
        self.xspeed = 0
        self.yspeed = 0
        self.alive = True
        self.score = 0
        self.poScore = 0
        self.PosControl = 0

    # Update position based on speed
    def update(self, paredes):
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

        self.rect.y += self.yspeed
        lista_impactos_bloques = pygame.sprite.spritecollide(self, paredes, False)

        for bloque in lista_impactos_bloques:
            # Si nos estamos desplazando hacia la derecha, hacemos que nuestro lado derecho sea el lado izquierdo del objeto que hemos tocado.
            if self.yspeed > 0:
                self.rect.bottom = bloque.rect.top


            else:
                # En caso contrario, si nos desplazamos hacia la izquierda, hacemos lo opuesto.
                self.rect.top = self.rect.bottom


        # Desplazar arriba/izquierda

        self.rect.x += self.xspeed
        # Comprobamos si hemos chocado contra algo
        lista_impactos_bloques = pygame.sprite.spritecollide(self, paredes, False)

        for bloque in lista_impactos_bloques:

            # Reseteamos nuestra posición basándonos en la parte superior/inferior del objeto.
            if self.xspeed > 0:

                self.rect.right = bloque.rect.left

            else:
                self.rect.left = bloque.rect.right


        # print ((self.PosControl +1)%2 )
        # print (xPassControl[self.PosControl])


        if (self.PosControl) % 2 == 0:
            self.score = self.poScore + Scorey[self.PosControl] - self.rect.y + self.rect.x
        else:
            self.score = self.poScore + Scorey[self.PosControl] + self.rect.y + self.rect.x

        if (self.rect.x) > xPassControl[self.PosControl]:
            self.poScore = self.score + 302
            self.PosControl += 1
        self.xlast = self.rect.x
        self.ylast = self.rect.y

    def returnIndex (self):
        return self.PosControl

    # def Kill(self,pastx,pasty):
    #
    #
    #     if (pastx > self.rect.x or pastx == self.rect.x) and (pasty == self.rect.y):
    #         self.ShallDie = True
    #         self.alive = False
    # self.secondChance += 1
    # else:
    #     self.ShallDie = False
    #     self.secondChance =0

    # if self.ShallDie == True and self.secondChance == 2:
    #     self.alive = False

    # Draw the paddle to the screen

    def draw(self):
        if not self.winner:
            pygame.draw.rect(screen, BLACK, [self.rect.x, self.rect.y, 15, 15])
            pygame.draw.rect(screen, RED, [self.rect.x + 2, self.rect.y, 15 - 4, 15 - 4])
        else:
            pygame.draw.rect(screen, BLACK, [self.rect.x, self.rect.y, 15, 15])
            pygame.draw.rect(screen, BLUE, [self.rect.x + 2, self.rect.y, 15 - 4, 15 - 4])



# Ball class


class Cuarto:
    """ Clase base para todos los cuartos. """

    # Cada cuarto tiene una lista de paredes, y de los sprites enemigos.
    pared_lista = None
    sprites_enemigos = None

    def __init__(self):
        """ Constructor, creamos nuestras listas. """
        self.pared_lista = pygame.sprite.Group()
        self.sprites_enemigos = pygame.sprite.Group()


pparedes = []
Scorey = []
ReferenceY = []
xPassControl = []
class Cuarto1(Cuarto):
    """Esto crea todas las paredes del cuarto 1"""
    paredes = []

    def __init__(self):
        super().__init__()
        # Crear las paredes. (x_pos, y_pos, largo, alto)

        # Esta es la lista de las paredes. Cada una se especifica de la forma [x, y, largo, alto]
        varr = random
        dd = random.randint(140, 400)

        paredes = [[0, 100, 20, 350, VERDE],
                   [0, 450, 20, 250, VERDE],
                   [20, 100, 760, 20, VERDE],

                   [780, 100, 20, 250, VERDE],

                   [780, 450, 20, 250, VERDE],  # Paredes que si són paredes
                   [20, 680, 760, 20, VERDE, 0],
                   # Obstaculo
                   [50, 300, 10, 500, ROJO,0],
                   [100, 120, 10, 500, ROJO,1],
                   [150, varr.randint(140, 400), 10, 500, ROJO,2],
                   [200, 120, 10, 500, ROJO,3],
                   [250, varr.randint(140, 400), 10, 500, ROJO,4],
                   [300, 120, 10, 500, ROJO,5],
                   [350, varr.randint(140, 400), 10, 500, ROJO,6],
                   [400, 120, 10, 500, ROJO,7],
                   [450, varr.randint(140, 400), 10, 500, ROJO,8],
                   [500, 120, 10, 500, ROJO,9],
                   [550, varr.randint(140, 400), 10, 500, ROJO,10],
                   [600, 120, 10, 500, ROJO,11],
                   [650, varr.randint(140, 400), 10, 500, ROJO,12],
                   # pared
                   [700, 120, 10, 500, ROJO,13]
                   ]

        # Iteramos a través de la lista. Creamos la pared y la añadimos a la lista.
        ddd = 0
        for item in paredes:
            pared = Pared(item[0], item[1]+200, item[2], item[3], item[4])
            pparedes.append((item[0]-100, item[1]))
            if ddd > 5:
                Scorey.append(item[1]+200)

                xPassControl.append(item[0])
            self.pared_lista.add(pared)
            ddd += 1
        pparedes.append((780-100, 650))
        Scorey.append(650)
        xPassControl.append(820)

        # pparedes.append((820-100, 450))
        # Scorey.append(450)
        # xPassControl.append(820)



# Predicts the output for a given input given an array of coefficients and an array of intercepts
def calculateOutput(input, layer_structure, coefs, intercepts, g="identity"):
    # The values of the neurons for each layer will be stores in "layers", so here the input layer is added to start
    # (Stuff is transposed since we need columns for matrix multiplication)
    layers = [np.transpose(input)]
    # The current layer will be affected by the previous layer,
    # so here we define the starting previousLayer as the input
    previousLayer = np.transpose(input)

    reduced_layer_structure = layer_structure[1:]
    # Loops through the all the layers except the input
    for k in range(len(reduced_layer_structure)):
        # creates an empty array of the correct size
        currentLayer = np.empty((reduced_layer_structure[k], 1))
        # The resulting layer is a matrix multiplication of the previousLayer and the coefficients, plus the intercepts
        result = np.matmul(np.transpose(coefs[k]), previousLayer) + np.transpose(np.array([intercepts[k]]))
        # The value of each neuron is then put through a function g()
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
        # The current layer is then added to the layers list, and the previousLayer variable is updated
        layers.append(currentLayer)
        previousLayer = currentLayer.copy()

    # Returns the index of the highest value neuron in the output layer (aka layers[-1])
    # E.g. if the 7th neuron has the highest value, returns 7
    return layers[-1].tolist().index(max(layers[-1].tolist()))


# Returns a set of coefficients which are a mutation of the input
def mutateCoefs(coefs):
    newCoefs = []
    for array in coefs:
        newCoefs.append(np.copy(array))
    for i in range(len(newCoefs)):
        for row in range(len(newCoefs[i])):
            for col in range(len(newCoefs[i][row])):
                newCoefs[i][row][col] = np.random.normal(newCoefs[i][row][col], 1)
    return newCoefs


# Returns a set of intercepts which are a mutation of the input
def mutateIntercepts(intercepts):
    newIntercepts = []
    for array in intercepts:
        newIntercepts.append(np.copy(array))
    for i in range(len(newIntercepts)):
        for row in range(len(newIntercepts[i])):
            newIntercepts[i][row] = np.random.normal(newIntercepts[i][row], 1)
    return newIntercepts


# Displays the nodes of a network, along with weighted lines showing the coefficient influences
def displayNetwork(layer_sctructure, coefs):
    # Stores the larges coefficient, so we can scale the thicknesses accordingly.
    max_coef = np.max(coefs[0])

    # Determines how much space this visual network will take up
    height = 300
    width = 300

    inputs = []
    cdd = 0

    inputs = ["PosX","PosY","Distància"]
    outputs = ["Left", "Right", "X stop", "Up", "Down", "Y stop"]

    layerCount = len(layer_structure)
    # This will store the positions of all the nodes (organized with sub-lists of each layer)
    circle_positions = []

    # Label inputs
    for i in range(layer_structure[0]):
        font = pygame.font.SysFont('Calibri', 20, False, False)
        text = font.render(inputs[i], True, TEXT)
        screen.blit(text, [40, (i + 1) * int(height / (layer_structure[0] + 2))+40])

    # Label outputs
    for i in range(layer_structure[-1]):
        font = pygame.font.SysFont('Calibri', 20, False, False)
        text = font.render(str(outputs[i]), True, TEXT)
        screen.blit(text, [width + 85, (i + 1) * int(height / (layer_structure[-1] + 2))+35])

    # Calculates an appropriate spacing of the layers
    xspacing = int(width / layerCount)

    # Determine the location of the neurons for each layer, stores that in a list,
    # and stores those lists in circle_positions
    for i in range(layerCount):
        layer_circle_positions = []
        yspacing = int(height / (layer_structure[i] + 2))
        for j in range(layer_structure[i]):
            layer_circle_positions.append(((i + 1) * xspacing+60, (j + 1) * yspacing+50))
        circle_positions.append(layer_circle_positions)

    # Draws a line between every node in one layer and every node in the next layer
    for i in range(len(circle_positions) - 1):
        for j, circle_pos in enumerate(circle_positions[i]):
            for k, circle_pos2 in enumerate(circle_positions[i + 1]):
                thickness = int(coefs[i][j, k] / max_coef * 8)

                if thickness > 0:
                    pygame.draw.lines(screen, BLUE, False, [circle_pos, circle_pos2], thickness)
                else:
                    pygame.draw.lines(screen, RED, False, [circle_pos, circle_pos2], -thickness)

    # Draws circles in the positions of the nodes (over the lines)
    for layer in circle_positions:
        for circle_pos in layer:
            pygame.draw.circle(screen, BLACK, circle_pos, 20, 0)
            pygame.draw.circle(screen, GREEN, circle_pos, 16, 0)


done = False
score = 0
command = "stop"
clock = pygame.time.Clock()

COUNT = 100

# create sprites
paddles = []
# balls = []
cuartos = []

cuarto = Cuarto1()
cuartos.append(cuarto)
cuarto_actual_no = 0
cuarto_actual = cuartos[cuarto_actual_no]

for i in range(100):
    paddles.append(Paddle())
    # balls.append(Ball())

# The first winner is arbitrarily chosen to be the last one (just so the user has a network to watch on screen)
winner = paddles[-1]
# winnner = balls [-1]
paddles[-1].winner = True

# game's main loop
generation = 1
b = 0
MXScore=0
cu = 0
c = 0
finalisimo = False
while not done:
    screen.fill(FILL)
    cuarto_actual.pared_lista.draw(screen)
    # Track the number of paddles still alive in this generation
    still_alive = 0
    # Track the high score and the index of the highest scoring paddle
    highP = 0
    high_score = -9e99
    high_score_index = -1

    # Allow user to exit at any time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Loop through all the paddles

    for i, paddle in enumerate(paddles):
        # If you change the number of inputs, be sure to change the layer_structure at
        # the top and the input text in displayNetwork

        input = np.array([[paddle.rect.x, paddle.rect.y]])
        #Calculem el mòdul de la distancia entre el paddle i la punta de la paret més propera
        if paddle.returnIndex() % 2 == 0:
            distancia = -80 + math.sqrt((pparedes[paddle.returnIndex() + 6][0] - paddle.rect.x) ** 2 + (
                    pparedes[paddle.returnIndex() + 6][1] - paddle.rect.y) ** 2)
            distancia = -distancia
        else:
            distancia = -410 + math.sqrt(
                (pparedes[paddle.returnIndex() + 6][0] + 500 - paddle.rect.x) ** 2 + (
                        pparedes[paddle.returnIndex() + 6][1] + 500 - paddle.rect.y) ** 2)

        newa = np.array([[distancia]])

        input = np.append(input, newa, axis=1)


        layer_structure[0] = int(input.size)
        paddle.command = calculateOutput(input, layer_structure, paddle.coefs, paddle.intercepts)

        # 0=left, 1=right, 2=xstop, 3=up, 4=down, 5=ystop
        if paddle.command == 0:
            paddle.xspeed = -10
        elif paddle.command == 1:
            paddle.xspeed = 10
        elif paddle.command == 2:
            paddle.xspeed = 0
        elif paddle.command == 3:
            paddle.yspeed = -10
        elif paddle.command == 4:
            paddle.yspeed = 10
        elif paddle.command == 5:
            paddle.yspeed = 0

        # Actualitzem la posició dels jugadors

        if paddle.alive == True:
            paddle.update(cuarto_actual.pared_lista)  # poner: (cuarto_actual.pared_lista)
            still_alive += 1

        if paddle.rect.x > 784 and paddle.winner == True:
            finalisimo = True
            break

        # Els punts màxims pasen a ser el high score
        if paddle.score > high_score:
            high_score = paddle.score
            high_score_index = i
            winner = paddles[i]
            winner.winner = True

        if MXScore < high_score:
            MXScore = high_score

        # Dibuixa tot menys el guanyador
        if paddle.alive and paddle != winner:
            paddle.draw()
            paddle.winner = False

    # dibuixem el guanyador després, així fem que estigui al front
    paddles[high_score_index].draw()
    cuarto_actual.pared_lista.draw(screen)



    if still_alive == 0 or b > 3+generation/2:
        generation += 1
        winner.reset()
        paddles = []
        b=0
        for i in range(COUNT - 1):
            paddles.append(Paddle(coefs=mutateCoefs(winner.coefs), intercepts=mutateIntercepts(winner.intercepts)))
        paddles.append(winner)



    if cuarto_actual_no == c and finalisimo == True:
        cuarto_actual_no = c + 1
        c += 1
        cuarto = Cuarto1()
        cuartos.append(cuarto)
        cuarto_actual = cuartos[cuarto_actual_no]
        
        winner.reset()
        paddles = []
        b = 0
        for i in range(COUNT - 1):
            paddles.append(Paddle(coefs=mutateCoefs(winner.coefs), intercepts=mutateIntercepts(winner.intercepts)))
        paddles.append(winner)
        finalisimo = False

    b = b+(clock.get_time()/1000)
    font = pygame.font.SysFont('Calibri', 30, False, False)
    text = font.render("Score = " + str(math.trunc(high_score/10)), True, TEXT)
    screen.blit(text, [size[0] - 325, 30])
    text = font.render("MXScore = " + str(math.trunc(MXScore / 10)), True, TEXT)
    screen.blit(text, [size[0] - 325, 90])
    text2 = font.render("Generació = " + str(generation), True, TEXT)
    screen.blit(text2, [size[0] - 325, 150])
    text2 = font.render("Temps = " + str(math.trunc(b))+" de "+str(math.trunc(3+generation/2))+ " s", True, TEXT)
    screen.blit(text2, [size[0] - 325, 210])
    text2 = font.render("Xarxa neuronal del guanyador:", True, TEXT)
    screen.blit(text2, [size[0] - 790, 30])
    displayNetwork(layer_structure, winner.coefs)

    pygame.display.flip()
    clock.tick(60)
