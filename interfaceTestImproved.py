import pygame

FILLED = 0
CONTOUR = 3


class Interface:
    def __init__(self, width, height):

        self.unitSize = 40

        self.screen = None

        self.background = None
        self.backgroundColor = pygame.Color("#ADADAD")

        # we add here a tuple formed of an object
        self.renderingUnit = {}

        self.running = True

        self.mousePosition = None
        self.keyPressed = None

        self.initRender(width, height)
        # self.render()

    def getScreenSize(self):
        return self.screen.get_size()

    def updateBackground(self, backgroundColor=None):

        if backgroundColor is not None:
            self.backgroundColor = backgroundColor
            self.background.fill(self.backgroundColor)

        self.screen.blit(self.background, (0, 0))

    def getClickPosition(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            return pygame.mouse.get_pos()
        return None

    def cleanClickPosition(self):
        self.mousePosition = None

    def getExitStatus(self, event):
        if event.type == pygame.QUIT:
            return False
        return True

    def getKeyPressed(self, event):
        if event.type == pygame.KEYUP:
            #print(event.key)
            return event.key
        return None

    def cleanKeyPressed(self):
        self.keyPressed = None

    def initRender(self, width, height):
        pygame.init()
        pygame.display.set_caption('Twelve men\'s morris')

        self.screen = pygame.display.set_mode((width, height))

        self.background = pygame.Surface(self.getScreenSize())
        self.updateBackground(self.backgroundColor)

        self.updateRender()

    def updateRender(self):
        pygame.display.update()

    def render(self, renderEverything):

        while self.running:

            for event in pygame.event.get():
                self.mousePosition = self.getClickPosition(event)
                self.running = self.getExitStatus(event)
                self.keyPressed = self.getKeyPressed(event)

            #print(self.keyPressed)
            renderEverything()
            self.updateRender()


class GameInterface(Interface):
    def __init__(self, width, height):

        self.tablePosition = (20, 20)
        self.translatePosition = {0: (0, 0), 1: (3, 0), 2: (6, 0), 3: (6, 3), 4: (6, 6), 5: (3, 6), 6: (0, 6),
                                  7: (0, 3),
                                  8: (1, 1), 9: (3, 1), 10: (5, 1), 11: (5, 3), 12: (5, 5), 13: (3, 5), 14: (1, 5),
                                  15: (1, 3),
                                  16: (2, 2), 17: (3, 2), 18: (4, 2), 19: (4, 3), 20: (4, 4), 21: (3, 4), 22: (2, 4),
                                  23: (2, 3)}
        self.pieces = []
        self.freePos = []
        self.validMoves = []

        self.selectedPiece = None
        self.selectedPosition = None

        self.deleteValue = None

        super().__init__(width, height)

        self.halfUnit = self.unitSize / 2

        # super().render(self.renderGame)

    def getClickedTablePosition(self):

        if self.mousePosition is not None:

            x = int((self.mousePosition[0] - self.tablePosition[0]) / self.unitSize)
            y = int((self.mousePosition[1] - self.tablePosition[1]) / self.unitSize)

            for key in self.translatePosition:
                if x == self.translatePosition[key][0] and y == self.translatePosition[key][1]:
                    return key

        return None

    def translate(self, position):
        return self.translatePosition[position]

    def getPieceToMove(self, playerColor, getValidMoves, playerAnterior):

        self.selectedPiece = self.getClickedTablePosition()
        self.cleanClickPosition()

        if self.selectedPiece is None:
            return None

        self.validMoves = getValidMoves(self.selectedPiece)
        #print(self.validMoves, playerAnterior)

        if playerAnterior is not None:
            if playerAnterior in self.validMoves:
                self.validMoves.remove(playerAnterior)

        if self.pieces[self.selectedPiece] is None:
            return None

        if playerColor != self.pieces[self.selectedPiece].playerColor:
            return None

        return self.selectedPiece

    def getPositionToMove(self):

        self.selectedPosition = self.getClickedTablePosition()
        self.cleanClickPosition()

        if self.selectedPosition in self.validMoves:
            return self.selectedPosition

        return None

    def getMove(self, playerColor, getValidMoves, playerAnterior):
        if self.selectedPiece is not None:
            self.getPositionToMove()

            if self.selectedPosition is not None:
                return self.selectedPiece, self.selectedPosition

        else:
            self.getPieceToMove(playerColor, getValidMoves, playerAnterior)

        return None

    def getPut(self):

        if self.selectedPosition is None:

            self.selectedPosition = self.getClickedTablePosition()
            #print(self.selectedPosition)
            self.cleanClickPosition()

            if self.selectedPosition is not None:
                #print(len(self.pieces))
                if self.pieces[self.selectedPosition] is None:
                    return self.selectedPosition

        return None

    def getDelete(self, playerColor):

        if self.selectedPosition is None:

            self.selectedPosition = self.getClickedTablePosition()
            self.cleanClickPosition()

            if self.selectedPosition is not None:
                if self.pieces[self.selectedPosition] is None:
                    return None
                elif self.pieces[self.selectedPosition].playerColor != playerColor:
                    return self.selectedPosition

        return None


    def clearRender(self):
        self.pieces = []
        self.freePos = []
        self.validMoves = []

        self.selectedPiece = None
        self.selectedPosition = None

    def renderGame(self):

        (x, y) = self.tablePosition

        self.renderTable(x, y)
        self.renderSpacesTable(x, y)
        self.renderValidMoves(x, y, self.validMoves)
        self.renderValidMoves(x, y, self.freePos)

        self.renderPlayerPieces(x, y, [i for i in range(0, len(self.pieces)) if self.pieces[i] is not None
                                       and self.pieces[i].playerColor is True], "#FFFFFF")
        self.renderPlayerPieces(x, y, [i for i in range(0, len(self.pieces)) if self.pieces[i] is not None
                                       and self.pieces[i].playerColor is False], "#000000")

    def updateRenderGame(self):
        self.validMoves = []

    def renderTable(self, posx, posy):
        table = pygame.Rect(posx, posy, 7 * self.unitSize, 7 * self.unitSize)
        pygame.draw.rect(self.screen, pygame.Color("#8B4513"), table, FILLED)
        # pygame.draw.rect(self.screen, pygame.Color("#451505"), table, CONTOUR)

    def renderPosition(self, posx, posy, position, color):

        (x, y) = self.translate(position)

        space = pygame.Rect(x * self.unitSize + posx, y * self.unitSize + posy, self.unitSize, self.unitSize)

        pygame.draw.rect(self.screen, pygame.Color(color), space, FILLED)
        pygame.draw.rect(self.screen, pygame.Color("#F5DEB3"), space, CONTOUR)

    def renderValidMoves(self, posx, posy, movesArray):
        for move in movesArray:
            self.renderPosition(posx, posy, move, "#32CD32")

    def renderSpacesTable(self, posx, posy):
        for key in self.translatePosition:
            self.renderPosition(posx, posy, key, "#CD853F")

    def renderPiece(self, posx, posy, piecePosition, color):
        (x, y) = self.translatePosition[piecePosition]

        radius = (self.unitSize * 2) / 5
        center = (x * self.unitSize + posx + self.halfUnit, y * self.unitSize + posy + self.halfUnit)

        pygame.draw.circle(self.screen, pygame.Color(color), center, radius, FILLED)

    def renderPlayerPieces(self, posx, posy, pieceArray, color):
        for piece in pieceArray:
            self.renderPiece(posx, posy, piece, color)


interface = GameInterface(600, 400)
