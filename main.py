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
    def __init__(self, playerType1, playerType2):
        self.winPosValue = self.createWinCases()
        self.freePos = [True for x in range(0, 24)]
        self.player1 = Player(1, playerType1)
        self.player2 = Player(-1, playerType2)
        self.turn = True

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

    def movePieceMove(self, player, id, newPos):

        piece = player.piece[player.getPieceById(id)]

        if newPos in self.getValidMoves(piece.position) and piece.anteriorPosition != newPos:
            player.movePiece(id, newPos)
            self.updateWinCases(oldPos, newPos, player.color)

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

    def makeMove(self, option, id, newPos, delPos=None):

        if self.turn:
            playerWithTurn = self.player1
            playerWithoutTurn = self.player2

        else:
            playerWithTurn = self.player2
            playerWithoutTurn = self.player1

        # there are 2 options: put a piece on the table("put") or move a piece("move")
        if option is "move":
            self.movePieceMove(playerWithTurn, id, newPos)
        elif option is "put":
            self.putPieceMove(playerWithTurn, newPos)

        if self.findPlayerWin(playerWithTurn):

            # we choose a enemy piece to eliminate
            if playerWithTurn.type == "bot":
                self.chooseToDeleteMove(playerWithoutTurn, delPos)
            else:
                self.chooseToDeleteMove(playerWithoutTurn)

        if self.turn:
            self.player1 = playerWithTurn
            self.player2 = playerWithoutTurn

        else:
            self.player2 = playerWithTurn
            self.player1 = playerWithoutTurn

        # update turn
        self.turn = not self.turn


g = Game("bot", "bot")
