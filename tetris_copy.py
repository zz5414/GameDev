#!/usr/bin/python3

"""
ZetCode PyQt5 tutorial

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com
"""

import random
import sys

import numpy as np

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        """initiates application UI"""

        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.tboard.start()

        self.resize(180*3, 380*3)
        # self.center()
        self.setWindowTitle('Tetris')
        self.show()

    # def center(self):
    #     """centers the window on the screen"""
    #
    #     screen = QDesktopWidget().screenGeometry()
    #     size = self.geometry()
    #     self.move(int((screen.width() - size.width()) / 2),
    #               int((screen.height() - size.height()) / 2))


class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)

    BoardWidth = 10
    BoardHeight = 22
    # BoardWidth = 5
    # BoardHeight = 10
    Speed = 1000

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):
        """initiates board"""

        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = None

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()

    def shapeAt(self, r, c):
        """determines shape at the board position"""
        return self.board[r][c]

    def setShapeAt(self, r, c, shape):
        """sets a shape at the board"""

        self.board[r][c] = shape

    def squareWidth(self):
        """returns the width of one square"""

        return self.contentsRect().width() // Board.BoardWidth

    def squareHeight(self):
        """returns the height of one square"""

        return self.contentsRect().height() // Board.BoardHeight

    def start(self):
        """starts game"""

        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        # self.clearBoard()

        # self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.newPiece()
        self.timer.start(Board.Speed, self)
#
#     def pause(self):
#         """pauses game"""
#
#         if not self.isStarted:
#             return
#
#         self.isPaused = not self.isPaused
#
#         if self.isPaused:
#             self.timer.stop()
#             self.msg2Statusbar.emit("paused")
#
#         else:
#             self.timer.start(Board.Speed, self)
#             self.msg2Statusbar.emit(str(self.numLinesRemoved))
#
#         self.update()
#


    def drawGrid(self, painter):
        pen = painter.pen()

        rect = self.contentsRect()
        painter.setPen(QPen(Qt.gray, 10))

        painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
        painter.drawLine(rect.right(), rect.bottom(), rect.left(), rect.bottom())
        painter.drawLine(rect.left(), rect.bottom(), rect.left(), rect.top())

        for i in range(1, Board.BoardWidth):
            x = self.squareWidth() * i
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for i in range(1, Board.BoardHeight):
            y = self.squareHeight() * i
            painter.drawLine(rect.left(), y, rect.right(), y)

        painter.setPen(pen)


    def paintEvent(self, event):
        """paints all shapes of the game"""

        painter = QPainter(self)
        rect = self.contentsRect()

        # boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

        self.drawGrid(painter)

        # draw bg
        for r in range(Board.BoardHeight):
            for c in range(Board.BoardWidth):
                shape = self.shapeAt(r, c)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter, rect, r, c, shape)


        #draw current piece
        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                c = self.curC + self.curPiece.c(i)
                r = self.curR + self.curPiece.r(i)
                self.drawSquare(painter, rect, r, c, self.curPiece.shape())


    # def move(self, c, r):
    #     if (c<0) or (c>=Board.BoardWidth) or (r<0) or (r>=Board.BoardHeight):
    #         return
    #
    #     self.board[(Board.BoardHeight - 1 - y)*Board.BoardWidth + x] = Tetrominoe.ZShape
    #     self.curX, self.curY = x, y
    #     self.update()

    def keyPressEvent(self, event):
         """processes key press events"""

         # if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
         #     super(Board, self).keyPressEvent(event)
         #     return

         if not self.isStarted:
            super(Board, self).keyPressEvent(event)
            return

         key = event.key()

         if key == Qt.Key_Left:
             # self.move(self.curX - 1, self.curY)
             self.tryMove(self.curPiece, self.curC - 1, self.curR)

         elif key == Qt.Key_Right:
             # self.move(self.curX + 1, self.curY)
             self.tryMove(self.curPiece, self.curC + 1, self.curR)

             # self.tryMove(self.curPiece, self.curX + 1, self.curY)

         elif key == Qt.Key_Down:
             # self.move(self.curX, self.curY+1)
             self.tryMove(self.curPiece, self.curC, self.curR + 1)
             # self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

         elif key == Qt.Key_Up:
             # self.tryMove(self.curPiece, self.curC, self.curR - 1)
             self.tryMove(self.curPiece.rotateLeft(), self.curC, self.curR)


         # if key == Qt.Key_P:
         #     self.pause()
         #     return
         #
         # if self.isPaused:
         #     return
         #
         # elif key == Qt.Key_Left:
         #     self.tryMove(self.curPiece, self.curX - 1, self.curY)
         #
         # elif key == Qt.Key_Right:
         #     self.tryMove(self.curPiece, self.curX + 1, self.curY)
         #
         # elif key == Qt.Key_Down:
         #     self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
         #
         # elif key == Qt.Key_Up:
         #     self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
         #
         elif key == Qt.Key_Space:
             self.dropDown()
         #
         # elif key == Qt.Key_D:
         #     self.oneLineDown()

         else:
             super(Board, self).keyPressEvent(event)


    def timerEvent(self, event):
        """handles timer event"""

        if event.timerId() == self.timer.timerId():
            # self.move(self.curC, self.curR+1)

            if self.isWaitingAfterLine:
               self.isWaitingAfterLine = False
               self.newPiece()
            else:
               self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)

    def clearBoard(self):
        """clears shapes from the board"""
        # zero is NoShape
        self.board = np.zeros((Board.BoardHeight, Board.BoardWidth))


        # for i in range(Board.BoardHeight * Board.BoardWidth):
        #     self.board.append(Tetrominoe.NoShape)
        # self.board[0] = Tetrominoe.ZShape
        # self.board[(Board.BoardHeight-1)*Board.BoardWidth] = Tetrominoe.ZShape

        # 움직일 수 있는 좌표를 생성
        # self.curX = Board.BoardWidth // 2
        # self.curY = Board.BoardHeight // 2
        # self.board[0] = Tetrominoe.ZShape


    def dropDown(self):
        """drops down a shape"""

        newR = self.curR

        while newR < Board.BoardHeight:
            if not self.tryMove(self.curPiece, self.curC, newR + 1):
                break
            newR += 1

        self.pieceDropped()

    def oneLineDown(self):
        """goes one line down with a shape"""

        if not self.tryMove(self.curPiece, self.curC, self.curR + 1):
            self.pieceDropped()

    def pieceDropped(self):
        """after dropping shape, remove full lines and create new shape"""

        for i in range(4):
            c = self.curC + self.curPiece.c(i)
            r = self.curR + self.curPiece.r(i)
            self.setShapeAt(r, c, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    # https://stackoverflow.com/questions/56700417/how-to-shift-a-2d-numpy-array-in-python
    # num으로 입력받은 만큼 행렬을 아래로 shift
    def shift_array(self, arr, num):
        arr[1:num+1, :] = arr[:num, :]
        arr[:1, :] = np.zeros(arr[0].shape)
        return arr

    def removeFullLines(self):
        """removes all full lines from the board"""

        A = np.array([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9],
                      [10, 11, 12]])

        A[1:, :] = A[:3, :]
        A[:1, :] = np.zeros(A[0].shape)


        numFullLines = 0
        for r in range(Board.BoardHeight):
            count = len(np.where(self.board[r] > 0)[0])
            if count == Board.BoardWidth:
                numFullLines += 1
                self.board = self.shift_array(self.board, r)

        #
        # numFullLines = 0
        # rowsToRemove = []
        #
        # for i in range(Board.BoardHeight):
        #
        #     n = 0
        #     for j in range(Board.BoardWidth):
        #         if not self.shapeAt(j, i) == Tetrominoe.NoShape:
        #             n = n + 1
        #
        #     if n == 10:
        #         rowsToRemove.append(i)
        #
        # rowsToRemove.reverse()
        #
        # for m in rowsToRemove:
        #
        #     for k in range(m, Board.BoardHeight):
        #         for l in range(Board.BoardWidth):
        #             self.setShapeAt(l, k, self.shapeAt(l, k + 1))
        #
        # numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()
#
    def newPiece(self):
        """creates a new shape"""

        self.curPiece = Shape()
        # self.curPiece.setShape(Tetrominoe.LineShape)
        self.curPiece.setRandomShape()
        self.curC = (Board.BoardWidth - 1) // 2
        self.curR = 0 - self.curPiece.minR()

        if not self.tryMove(self.curPiece, self.curC, self.curR):
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")


    def tryMove(self, newPiece, newC, newR):
        """tries to move a shape"""
        for i in range(4):
            c = newC + newPiece.c(i)
            r = newR + newPiece.r(i)

            # 범위를 벗어낫다면
            if (c<0) or (c>=Board.BoardWidth) or (r<0) or (r>=Board.BoardHeight):
                return False

            # 해당 위치에 다른 무엇인가가 있을 경우
            if self.shapeAt(r, c) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curC = newC
        self.curR = newR
        self.update()

        return True




    # def tryMove(self, newPiece, newC, newR):
    #     """tries to move a shape"""
    #
    #     for i in range(4):
    #
    #         x = newX + newPiece.x(i)
    #         y = newY + newPiece.y(i)
    #
    #         if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
    #             return False
    #
    #         if self.shapeAt(x, y) != Tetrominoe.NoShape:
    #             return False
    #
    #     self.curPiece = newPiece
    #     self.curX = newX
    #     self.curY = newY
    #     self.update()
    #
    #     return True
#
    def drawSquare(self, painter, rect, r, c, shape):
        """draws a square of a shape"""
        color = QColor(0xCC6666)
        painter.fillRect(rect.left() + (c * self.squareWidth()),
                         rect.top() + (r * self.squareHeight()),
                         self.squareWidth(), self.squareHeight(),
                         color)
#
#
class Tetrominoe(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):

        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)

    def shape(self):
        """returns shape"""

        return self.pieceShape

    def setShape(self, shape):
        """sets a shape"""

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):
        """chooses a random shape"""

        self.setShape(random.randint(1, 7))

    def c(self, index):
        """returns x coordinate"""

        return self.coords[index][0]

    def r(self, index):
        """returns y coordinate"""

        return self.coords[index][1]

    def setC(self, index, c):
        """sets x coordinate"""

        self.coords[index][0] = c

    def setR(self, index, r):
        """sets y coordinate"""

        self.coords[index][1] = r
#
#     def minX(self):
#         """returns min x value"""
#
#         m = self.coords[0][0]
#         for i in range(4):
#             m = min(m, self.coords[i][0])
#
#         return m
#
#     def maxX(self):
#         """returns max x value"""
#
#         m = self.coords[0][0]
#         for i in range(4):
#             m = max(m, self.coords[i][0])
#
#         return m
#
    def minR(self):
        """returns min y value"""

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m
#
#     def maxY(self):
#         """returns max y value"""
#
#         m = self.coords[0][1]
#         for i in range(4):
#             m = max(m, self.coords[i][1])
#
#         return m
#
    def rotateLeft(self):
        """rotates shape to the left"""

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setC(i, self.r(i))
            result.setR(i, -self.c(i))

        return result
#
#     def rotateRight(self):
#         """rotates shape to the right"""
#
#         if self.pieceShape == Tetrominoe.SquareShape:
#             return self
#
#         result = Shape()
#         result.pieceShape = self.pieceShape
#
#         for i in range(4):
#             result.setX(i, -self.y(i))
#             result.setY(i, self.x(i))
#
#         return result


def main():
    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()