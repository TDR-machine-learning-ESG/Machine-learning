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
aaa = 0
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
VIOLETA = (255, 0, 255)

x1 = 750
y1 = 100
resetea = False

pygame.init()

# Here you can specify the structure of the neural network. This includes the input layer and output layer.
# e.g 3 inputs, 5 node hidden layer, 4 outputs would be [3, 5, 4]
# Be sure to update this if you add inputs
layer_structure = [42, 6]

# Initializing the display window
size = (800, 700)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("pong")

testCoefs = [np.array([[0.38238344, 0.7515745, 0.29565119, 0.35490288, 0.97040034],
                       [0.33545982, 0.0973694, 0.41539856, 0.76129553, 0.93089118],
                       [0.85154809, 0.0240888, 0.74555908, 0.34759429, 0.37355357],
                       [0.95104127, 0.29077331, 0.21244898, 0.78876218, 0.35243364]]),
             np.array([[0.25498077, 0.03853811, 0.76089995],
                       [0.36535132, 0.60519588, 0.08365677],
                       [0.12852428, 0.0156597, 0.03317768],
                       [0.1276382, 0.13700435, 0.6786845],
                       [0.71931642, 0.8930938, 0.24983195]])]


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

    def __init__(self, x=20, y=250, xspeed=0, yspeed=0, coefs=0, intercepts=0):

        super().__init__()

        self.image = pygame.Surface([15, 15])
        self.image.fill(VIOLETA)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.ylast = y - yspeed
        self.xlast = x - xspeed
        self.yspeed = yspeed
        self.xspeed = xspeed
        self.alive = True
        self.score = 0
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
        self.rect.y = 250
        self.ylast = 20
        self.xlast = 250
        self.xspeed = 0
        self.yspeed = 0
        self.alive = True
        self.score = 0

    # Update position based on speed
    def update(self, paredes):
        self.xlast = self.rect.x
        self.ylast = self.rect.y
        self.rect.x += self.xspeed
        self.rect.y += self.yspeed
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > size[0] - 100:
            self.rect.x = size[0] - 100
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > size[1]:
            self.rect.y = size[1] - 35

        lista_impactos_bloques = pygame.sprite.spritecollide(self, paredes, False)

        for bloque in lista_impactos_bloques:
            # Si nos estamos desplazando hacia la derecha, hacemos que nuestro lado derecho sea el lado izquierdo del
            # objeto que hemos tocado.
            if self.xspeed > 0:
                paddle.alive = False
                paddle.score -= round(abs((self.rect.x + 50) - bloque.rect.x) / 100, 2)
                score = -1
            else:
                # En caso contrario, si nos desplazamos hacia la izquierda, hacemos lo opuesto.
                paddle.alive = False
                paddle.score -= round(abs((self.rect.x + 50) - bloque.rect.x) / 100, 2)
                score = -1

        # Desplazar arriba/izquierda

        # Comprobamos si hemos chocado contra algo
        lista_impactos_bloques = pygame.sprite.spritecollide(self, paredes, False)

        for bloque in lista_impactos_bloques:

            # Reseteamos nuestra posición basándonos en la parte superior/inferior del objeto.
            if self.yspeed > 0:
                paddle.alive = False
                paddle.score -= round(abs((self.rect.y + 50) - bloque.rect.y) / 100, 2)
                score = -1
            else:
                paddle.alive = False
                paddle.score -= 1
                paddle.score -= round(abs((self.rect.y + 50) - bloque.rect.y) / 100, 2)

        self.xlast = self.rect.x
        self.ylast = self.rect.y

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

                   # Obstaculo
                   [50, varr.randint(140, 400), 10, 500, ROJO],
                   [100, 120, 10, 500, ROJO],
                   [150, varr.randint(140, 400), 10, 500, ROJO],
                   [200, 120, 10, 500, ROJO],
                   [250, varr.randint(140, 400), 10, 500, ROJO],
                   [300, 120, 10, 500, ROJO],
                   [350, varr.randint(140, 400), 10, 500, ROJO],
                   [400, 120, 10, 500, ROJO],
                   [450, varr.randint(140, 400), 10, 500, ROJO],
                   [500, 120, 10, 500, ROJO],
                   [550, varr.randint(140, 400), 10, 500, ROJO],
                   [600, 120, 10, 500, ROJO],
                   [650, varr.randint(140, 400), 10, 500, ROJO],
                   [20, 680, 760, 20, VERDE],  # pared
                   [700, 120, 10, 500, ROJO]
                   ]

        # Iteramos a través de la lista. Creamos la pared y la añadimos a la lista.
        for item in paredes:
            pared = Pared(item[0], item[1], item[2], item[3], item[4])

            pparedes.append(item[0])
            pparedes.append(item[1])
            self.pared_lista.add(pared)
        print (len(pparedes))

class Ball:

    def __init__(self, x=50, y=50, xspeed=5, yspeed=5):
        self.recty = None
        self.x = x
        self.y = y
        self.winner = False
        self.xlast = x - xspeed
        self.ylast = y - yspeed
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.alive = True

    # Update position based on speed
    def update(self, paddle):
        self.xlast = self.x
        self.ylast = self.y

        self.x += self.xspeed
        self.y += self.yspeed

        # Accounts for bouncing off walls and paddle
        if self.x < 0:
            self.x = 0
            self.xspeed = self.xspeed * -1
        elif self.x > size[0] - 15:
            self.x = size[0] - 15
            self.xspeed = self.xspeed * -1
        elif self.y < 0:
            self.y = 0
            self.yspeed = self.yspeed * -1
        elif paddle.rect.x < self.x < paddle.rect.x + 15 and self.ylast < paddle.rect.y - 35 <= self.recty:
            self.yspeed = self.yspeed * -1
            paddle.score = paddle.score + 1
        elif self.y > size[1]:
            self.yspeed = self.yspeed * -1
            paddle.alive = False
            paddle.score -= round(abs((paddle.rect.x + 50) - self.x) / 100, 2)

    # Draw ball to screen
    def draw(self):
        if not self.winner:
            pygame.draw.rect(screen, WHITE, [self.x, self.y, 15, 15])
        else:
            pygame.draw.rect(screen, VIOLETA, [self.x, self.y, 15, 15])


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
    while cdd < input.size:
        inputs.append (" ")
        print (inputs[cdd])
        cdd +=1
    outputs = ["left", "right", "x stop", "up", "down", "y stop"]

    layerCount = len(layer_structure)
    # This will store the positions of all the nodes (organized with sub-lists of each layer)
    circle_positions = []

    # Label inputs
    for i in range(layer_structure[0]):
        font = pygame.font.SysFont('Calibri', 30, False, False)
        text = font.render(inputs[i], True, TEXT)
        screen.blit(text, [0, (i + 1) * int(height / (layer_structure[0] + 2))])

    # Label outputs
    for i in range(layer_structure[-1]):
        font = pygame.font.SysFont('Calibri', 30, False, False)
        text = font.render(str(outputs[i]), True, TEXT)
        screen.blit(text, [width + 50, (i + 1) * int(height / (layer_structure[-1] + 2))])

    # Calculates an appropriate spacing of the layers
    xspacing = int(width / layerCount)

    # Determine the location of the neurons for each layer, stores that in a list,
    # and stores those lists in circle_positions
    for i in range(layerCount):
        layer_circle_positions = []
        yspacing = int(height / (layer_structure[i] + 2))
        for j in range(layer_structure[i]):
            layer_circle_positions.append(((i + 1) * xspacing, (j + 1) * yspacing))
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
while not done:
    screen.fill(FILL)
    cuarto_actual.pared_lista.draw(screen)
    # Track the number of paddles still alive in this generation
    still_alive = 0
    # Track the high score and the index of the highest scoring paddle
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

        newa = np.array([pparedes])
        print (input)
        input = np.append(input,newa,axis=1)
        print (newa)
        print (input)

        layer_structure [0] = int(input.size)
        paddle.command = calculateOutput(input, layer_structure, paddle.coefs, paddle.intercepts)

        # 0=left, 1=right, 2=stop, 3=up, 4=down
        if paddle.command == 0:
            paddle.xspeed = -5
        elif paddle.command == 1:
            paddle.xspeed = 5
        elif paddle.command == 2:
            paddle.xspeed = 0
        elif paddle.command == 3:
            paddle.yspeed = -5
        elif paddle.command == 4:
            paddle.yspeed = 5
        elif paddle.command == 5:
            paddle.yspeed = 0

        # Update position of all living paddles
        if paddle.alive:
            paddle.update(cuarto_actual.pared_lista)  # poner: (cuarto_actual.pared_lista)
            # balls[i].update(paddle)
            still_alive += 1

        # Update high_score and high_scorer
        if paddle.score > high_score:
            high_score = paddle.score
            high_score_index = i
            winner = paddles[i]
            # winnner = balls [i]
            # balls [i].draw()
            winner.winner = True
            # winnner.winner = True

        # Draw everything but the winner
        if paddle.alive and paddle != winner:
            paddle.draw()
            # balls[i].winner = False
            # balls[i].draw()
            paddle.winner = False

    # draw the winner last (so that it is not hidden behind other paddles)
    paddles[high_score_index].draw()
    # balls[high_score_index].draw()

    # If all the paddles are dead, reproduce the most fit one
    if still_alive == 0:
        generation += 1
        winner.reset()
        # print(high_score_index)
        # clear the generation
        paddles = []
        balls = []
        # Fill it with mutations of the winner
        for i in range(COUNT - 1):
            paddles.append(Paddle(coefs=mutateCoefs(winner.coefs), intercepts=mutateIntercepts(winner.intercepts)))
            # balls.append(Ball())
        # add the winner itself
        paddles.append(winner)
        # balls.append(Ball())

    # score board
    font = pygame.font.SysFont('Calibri', 30, False, False)
    text = font.render("Score = " + str(high_score), True, TEXT)
    screen.blit(text, [size[0] - 325, 30])
    text2 = font.render("Still alive = " + str(still_alive), True, TEXT)
    screen.blit(text2, [size[0] - 325, 90])
    text2 = font.render("Generation = " + str(generation), True, TEXT)
    screen.blit(text2, [size[0] - 325, 150])
    displayNetwork(layer_structure, winner.coefs)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
