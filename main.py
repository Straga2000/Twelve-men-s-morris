import pygame
import interfaceTest

FILLED = 0
CONTOUR = 3


class Piece:
    def __init__(self, position, id):
        self.position = position
        self.anteriorPosition = None
        self.id = id
        self.isLocked = False

    def changePosition(self, newPosition):
        self.anteriorPosition = self.position
        self.position = newPosition

    def isInLine(self):
        self.isLocked = True


class Player:
    def __init__(self, color, type):
        self.type = type
        self.color = color
        self.piece = [Piece(-1, x) for x in range(0, 12)]

    def movePiece(self, id, newPos):
        self.piece[self.getPieceById(id)].changePosition(newPos)

    def deletePiece(self, id):
        self.piece.pop(self.getPieceById(id))

    def getPieceById(self, id):

        for i in range(0, len(self.piece)):
            if self.piece[i].id == id:
                return i

    def getPieceByPos(self, pos):

        for i in range(0, len(self.piece)):
            if self.piece[i].position == pos:
                return i

    def findUnusedPiece(self):
        for piece in self.piece:
            if piece.anteriorPosition is None:
                return piece.id
        return None

    def putPiece(self, pos):
        id = self.findUnusedPiece()

        if id is not None:
            self.movePiece(id, pos)
        else:
            raise Exception("There are no pieces to put")

    def getPositionList(self):
        posList = []

        for piece in self.piece:
            posList.append(piece.position)

        return posList

    def choosePositionToDelete(self, posDelete):
        self.deletePiece(self.getPieceByPos(posDelete))

    def playerLose(self):
        return len(self.piece) == 0


class Game:
    def __init__(self, playerType1, playerType2, gameInterface=None):
        self.winPosValue = self.createWinCases()
        self.freePos = [True for x in range(0, 24)]
        self.player1 = Player(1, playerType1)
        self.player2 = Player(-1, playerType2)
        self.gameInterface = gameInterface
        self.turn = True
        self.option = None

    def createWinCases(self):
        winPosValue = {}
        for i in range(0, 8):
            winPosValue[(i, i + 8, i + 16)] = 0

        for i in range(0, 3):
            winPosValue[(0 + 8 * i, 1 + 8 * i, 2 + 8 * i)] = 0
            winPosValue[(2 + 8 * i, 3 + 8 * i, 4 + 8 * i)] = 0
            winPosValue[(4 + 8 * i, 5 + 8 * i, 6 + 8 * i)] = 0
            winPosValue[(6 + 8 * i, 7 + 6 * i, 0 + 8 * i)] = 0

        # print(winPosValue)
        return winPosValue

    def getValidMoves(self, pos):
        validMoves = []

        if pos - 8 > 0 and self.freePos[pos - 8]:
            validMoves.append(pos - 8)
        if pos + 8 < 24 and self.freePos[pos + 8]:
            validMoves.append(pos + 8)

        if pos == 0 or pos == 8 or pos == 16:
            if self.freePos[pos + 7]:
                validMoves.append(pos + 7)
        else:
            if self.freePos[pos - 1]:
                validMoves.append(pos - 1)

        if pos == 7 or pos == 15 or pos == 23:
            if self.freePos[pos - 7]:
                validMoves.append(pos - 7)
        else:
            if self.freePos[pos + 1]:
                validMoves.append(pos + 1)

        return validMoves

    def getPieceList(self):
        pass

    def findPosition(self, tuple, pos):
        return tuple[0] == pos or tuple[1] == pos or tuple[2] == pos

    def updateWinCases(self, oldPos, newPos, color):

        if oldPos != -1:
            self.freePos[oldPos] = True

        self.freePos[newPos] = False

        for key in self.winPosValue:

            if self.findPosition(key, oldPos):
                self.winPosValue[key] -= color

            if self.findPosition(key, newPos):
                self.winPosValue[key] += color

    # TODO use isLocked to markdown a line already used
    def findPlayerWin(self, player):

        for key in self.winPosValue:

            if self.winPosValue[key] == player.color * 3:

                for i in range(0, len(player.piece)):

                    if self.findPosition(key, player.piece[i].position):
                        player.piece[i].isLocked = True

                return True

        return False

    # put -> (put, -1, newPos)
    # move -> (put, oldPos, newPos)
    def putPieceMove(self, player, newPos):

        if self.freePos[newPos]:
            player.putPiece(newPos)
            self.updateWinCases(-1, newPos, player.color)

        else:
            raise Exception("Not a valid position")

    def movePieceMove(self, player, position, newPos):

        piece = player.piece[player.getPieceByPos(position)]

        if newPos in self.getValidMoves(piece.position) and piece.anteriorPosition != newPos:
            player.movePiece(piece.id, newPos)
            self.updateWinCases(piece.anteriorPosition, newPos, player.color)

        else:
            raise Exception("Not a valid position")

    def chooseToDeleteMove(self, player, pos=None):

        if pos is None:
            chosenValue = int(input())
        else:
            chosenValue = pos

        posList = player.getPositionList()

        if chosenValue in posList:
            player.choosePositionToDelete(chosenValue)
        else:
            raise Exception("Not a piece of the opponent")

    def getPlayersByTurn(self):
        if self.turn:
            return self.player1, self.player2
        else:
            return self.player2, self.player1

    def setPlayersByTurn(self, player1, player2):
        if self.turn:
            self.player1 = player1
            self.player2 = player2
        else:
            self.player2 = player1
            self.player1 = player2

    def makeMove(self, option, clickedPos, newPos=None, delPos=None):

        playerWithTurn, playerWithoutTurn = self.getPlayersByTurn()

        # there are 2 options: put a piece on the table("put") or move a piece("move")
        if option == "move":
            self.movePieceMove(playerWithTurn, clickedPos, newPos)
        elif option == "put":
            self.putPieceMove(playerWithTurn, clickedPos)

        if self.findPlayerWin(playerWithTurn):

            # we choose a enemy piece to eliminate
            if playerWithTurn.type == "bot":
                self.chooseToDeleteMove(playerWithoutTurn, delPos)
            else:
                self.chooseToDeleteMove(playerWithoutTurn)

        self.setPlayersByTurn(playerWithTurn, playerWithoutTurn)

        # update turn
        self.turn = not self.turn
        self.option = None

    def gameLoop(self):

        # render pieces, table, etc.
        self.gameInterface.player1Pieces = [x for x in self.player1.getPositionList() if x != - 1]
        self.gameInterface.player2Pieces = [x for x in self.player2.getPositionList() if x != - 1]

        self.gameInterface.selectedPosition = None
        self.gameInterface.selectedPiece = None

        # get key pressed as an option
        if self.gameInterface.keyPressed is not None:
            self.option = self.gameInterface.keyPressed

        # print("something")
        if self.gameInterface.mousePosition is not None:
            if self.option is not None:

                if self.option == pygame.K_p:
                    print("is putting")
                    put = self.gameInterface.getPut()

                    # def makeMove(self, option, clickedPos, newPos, delPos=None):
                    if put is not None:
                        self.makeMove("put", put)
                    # self.makeMove("put", self.gameInterface.getClickedTablePosition(), )
                elif self.option == pygame.K_m:
                    print("is moving")
                    move = self.gameInterface.getMove(self.getPlayersByTurn()[0].color, )

        # render objects
        self.gameInterface.renderGame()

    def renderGameLoop(self):
        self.gameInterface.render(self.gameLoop)


g = Game("bot", "bot", interfaceTest.GameInterface(600, 400))
g.renderGameLoop()
