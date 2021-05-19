import pygame
import interfaceTestImproved

FILLED = 0
CONTOUR = 3


class Piece:
    def __init__(self, playerColor, position):
        self.position = position
        self.anteriorPosition = None
        self.isLocked = False
        self.playerColor = playerColor

    def changePosition(self, newPosition):
        self.anteriorPosition = self.position
        self.position = newPosition
        return self.anteriorPosition

    def isInLine(self):
        self.isLocked = True


class Player:
    def __init__(self, color, playerType, numberOfPieces=12):
        self.playerType = playerType
        self.color = color
        self.numberOfPieces = numberOfPieces
        self.anteriorMove = None

    # piece from 2 to 3 => oldPos = 2 and newPos = 3
    # next round, piece from 2 to 3 invalid because antMove(2, 3) and now the pair is (3, 2)

    # anteriorMove -> (pos, newPos)
    def verifyAnteriorMove(self, piece, newPos):
        #print(self.anteriorMove, piece.position, newPos)
        if self.anteriorMove is None:
            return False
        return piece.position == self.anteriorMove[1] and newPos == self.anteriorMove[0]

    def playerLose(self):
        return self.numberOfPieces == 0


class Game:
    def __init__(self, playerType1, playerType2, gameInterface=None):

        self.winPosValue = self.createWinCases()
        self.piece = [None for x in range(0, 24)]

        self.player1 = Player(True, playerType1)
        self.player2 = Player(False, playerType2)

        self.gameInterface = gameInterface

        self.turn = True
        self.option = None

    ### CRUD Functions for pieces ######################################################################################

    def movePiece(self, oldPos, newPos):
        self.piece[newPos] = self.piece[oldPos]
        self.piece[newPos].changePosition(newPos)
        self.deletePiece(oldPos)

    def deletePiece(self, pos):
        self.piece[pos] = None

    def putPiece(self, pos):
        self.piece[pos] = Piece(self.turn, pos)

    def getPieceColor(self, pos):
        return self.piece[pos].playerColor

    ###################################################################################################################

    def createWinCases(self):
        winPosValue = {}
        for i in range(0, 8):
            winPosValue[(i, i + 8, i + 16)] = 0

        for i in range(0, 3):
            winPosValue[(0 + 8 * i, 1 + 8 * i, 2 + 8 * i)] = 0
            winPosValue[(2 + 8 * i, 3 + 8 * i, 4 + 8 * i)] = 0
            winPosValue[(4 + 8 * i, 5 + 8 * i, 6 + 8 * i)] = 0
            winPosValue[(6 + 8 * i, 7 + 6 * i, 0 + 8 * i)] = 0
        return winPosValue

    def getValidMoves(self, pos):
        validMoves = []

        if pos - 8 > 0 and self.piece[pos - 8] is None:
            validMoves.append(pos - 8)
        if pos + 8 < 24 and self.piece[pos + 8] is None:
            validMoves.append(pos + 8)

        if pos == 0 or pos == 8 or pos == 16:
            if self.piece[pos + 7] is None:
                validMoves.append(pos + 7)
        else:
            if self.piece[pos - 1] is None:
                validMoves.append(pos - 1)

        if pos == 7 or pos == 15 or pos == 23:
            if self.piece[pos - 7] is None:
                validMoves.append(pos - 7)
        else:
            if self.piece[pos + 1] is None:
                validMoves.append(pos + 1)

        return validMoves

    def getFreePositions(self):
        return [i for i in range(0, 24) if self.piece[i] is None]

    def findPosition(self, tuple, pos):
        return tuple[0] == pos or tuple[1] == pos or tuple[2] == pos

    # give delete -1 to invert condition
    def updateWinCases(self, piece, delete=False):

        if self.turn:
            adder = 1
        else:
            adder = -1

        if not delete:

            for key in self.winPosValue:

                #print(piece)
                if self.findPosition(key, piece.anteriorPosition):
                    self.winPosValue[key] -= adder

                if self.findPosition(key, piece.position):
                    self.winPosValue[key] += adder
        else:

            for key in self.winPosValue:

                # print(piece)
                if self.findPosition(key, piece.position):
                    self.winPosValue[key] -= adder


    # TODO use isLocked to markdown a line already used
    def findPlayerWin(self):

        if self.turn:
            adder = 1
        else:
            adder = -1

        for key in self.winPosValue:

            if self.winPosValue[key] == adder * 3:

                allLocked = False

                for elem in key:
                    # TODO find how to update isLocked and resolve the locked problem
                    if self.piece[elem] is not None:

                        # if all are locked, allLocked is False
                        allLocked = allLocked or not self.piece[elem].isLocked
                        self.piece[elem].isLocked = True

                return allLocked

        return False

    # put -> (put, -1, newPos)
    # move -> (put, oldPos, newPos)
    def putPieceMove(self, player, newPos):

        if self.piece[newPos] is None:

            self.putPiece(newPos)
            self.updateWinCases(self.piece[newPos])

            player.anteriorMove = None

        else:
            raise Exception("Not a valid position")

    def movePieceMove(self, player, position, newPos):

        piece = self.piece[position]

        if newPos in self.getValidMoves(position) and not player.verifyAnteriorMove(piece, newPos):

            if self.piece[newPos] is None:

                self.movePiece(position, newPos)
                #print(self.piece[newPos])
                self.updateWinCases(self.piece[newPos])

                player.anteriorPiece = (position, newPos)

            else:
                raise Exception("Not a valid position")

        else:
            raise Exception("Not a valid position")

    def deletePieceMove(self, pos=None):

        if pos is None:
            return None

        if self.piece[pos] is not None:
            if self.getPieceColor(pos) != self.turn:
                self.updateWinCases(self.piece[pos], True)
                self.deletePiece(pos)
                return pos

        raise Exception("Not an opponent piece")

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

    def updateTurn(self, playerWithTurn, playerWithoutTurn):
        self.setPlayersByTurn(playerWithTurn, playerWithoutTurn)
        self.turn = not self.turn

    def makeMove(self, option, clickedPos, newPos=None, delPos=None):

        playerWithTurn, playerWithoutTurn = self.getPlayersByTurn()

        # there are 2 options: put a piece on the table("put") or move a piece("move")
        if option == "move":
            self.movePieceMove(playerWithTurn, clickedPos, newPos)
        elif option == "put":
            self.putPieceMove(playerWithTurn, clickedPos)
        elif option == "delete":
            self.deletePieceMove(clickedPos)

        if self.findPlayerWin():
            return True
        else:
            return False

    def gameLoop(self):

        # render pieces, table, etc.
        # self.gameInterface.updateRenderGame()
        self.gameInterface.pieces = self.piece

        # get key pressed as an option
        if self.gameInterface.keyPressed is not None:
            self.option = self.gameInterface.keyPressed

        #print(self.gameInterface)
        if self.option is not None:

            if self.option == pygame.K_p:
                # print("is putting")
                self.gameInterface.freePos = self.getFreePositions()

                put = self.gameInterface.getPut()
                # print(put)

                if put is not None:
                    #print(self.gameInterface.selectedPosition)

                    value = self.makeMove("put", put)
                    if self.gameInterface.deleteValue is None:
                        self.gameInterface.deleteValue = value

                    self.gameInterface.clearRender()
                    self.option = None

            elif self.option == pygame.K_m:
                # print("is moving")
                player = self.getPlayersByTurn()[0]

                if player.anteriorMove is not None:
                    anterior = player.anteriorMove[0]
                else:
                    anterior = None

                move = self.gameInterface.getMove(player.color, self.getValidMoves, anterior)

                if move is not None:
                    # print(self.gameInterface.selectedPiece, self.gameInterface.selectedPosition, self.gameInterface.validMoves)
                    value = self.makeMove("move", move[0], move[1])

                    if self.gameInterface.deleteValue is None:
                        self.gameInterface.deleteValue = value

                    self.gameInterface.clearRender()
                    self.option = None

        if self.gameInterface.deleteValue is not None:

            if self.gameInterface.deleteValue is True:
                self.gameInterface.freePos = [i for i in range(0, len(self.piece)) if self.piece[i] is not None and self.piece[i].playerColor != self.turn]
                pos = self.gameInterface.getDelete(self.turn)

                if pos is not None:
                    self.makeMove("delete", pos)
                    self.updateTurn(self.getPlayersByTurn()[0], self.getPlayersByTurn()[1])
                    self.gameInterface.clearRender()
                    self.gameInterface.deleteValue = None
            else:
                self.updateTurn(self.getPlayersByTurn()[0], self.getPlayersByTurn()[1])
                self.gameInterface.deleteValue = None


        #update turn after put/move and delete

        # render objects
        self.gameInterface.renderGame()

    def renderGameLoop(self):
        self.gameInterface.render(self.gameLoop)


g = Game("bot", "bot", interfaceTestImproved.GameInterface(600, 400))
g.renderGameLoop()
