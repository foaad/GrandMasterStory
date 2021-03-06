import random
from move import ChessMove
from board import Piece

games = []

def loadGameData(dataFile):
   global games
   try:
      games = eval(open(dataFile,"rb").read())
   except Exception, e:
      print 'Unable to load gameData.'

loadGameData("chess/gameData.chs")

def randomGame():
   if games:
      return ChessGame(random.choice(games))
   else:
      print "No games loaded."
      return None

class ChessGame(object):
   """docstring for ChessGame"""
   def __init__(self, gamedict):
      super(ChessGame, self).__init__()
      self.gameDict = gamedict
      self.whiteMoves = []
      self.blackMoves = []
      self.totalMoves = 0
      self.pieceActivity = {}
      self.finalScore = (0,0)
      self.__setup__()

   def __setup__(self):
      lastMove = None
      for move in self.gameDict['moves'][:-1]:
         if len(self.blackMoves) > 0:
            lastMove = self.blackMoves[-1]
         whiteMove = ChessMove(move[0], lastMove)
         blackMove = ChessMove(move[1], whiteMove, False)
         self.__gatherStats__(whiteMove,blackMove)
         self.whiteMoves.append(whiteMove)
         self.blackMoves.append(blackMove)

      # handle last move (contains results)
      move = self.gameDict['moves'][-1:][0]
      whiteMove = ChessMove(move[0], self.blackMoves[-1])
      if len(move) > 2:
         blackMove = ChessMove(move[1], whiteMove, False)
      else:
         blackMove = None
      self.__gatherStats__(whiteMove,blackMove)
      self.whiteMoves.append(whiteMove)
      if blackMove:
         self.blackMoves.append(blackMove)

      # get totalMoves
      self.totalMoves = len(self.whiteMoves) + len(self.blackMoves)
      if self.gameDict["Result"] == '1-0':
         self.outcome = (1,0)
      elif self.gameDict["Result"] == '0-1':
         self.outcome = (0,1)
      else:
         self.outcome = (1,1)

      # determine final score
      if (self.totalMoves % 2):
         self.finalScore = (self.whiteMoves[-1].whiteScore, self.whiteMoves[-1].blackScore)
      else: 
         self.finalScore = (self.blackMoves[-1].whiteScore, self.blackMoves[-1].blackScore)

   def __gatherStats__(self, whiteMove, blackMove):
      if whiteMove and whiteMove.piece:
         if whiteMove.piece in self.pieceActivity:
            self.pieceActivity[whiteMove.piece] += 1
         else:
            self.pieceActivity[whiteMove.piece] = 1
      if blackMove and blackMove.piece:
         if blackMove.piece in self.pieceActivity:
            self.pieceActivity[blackMove.piece] += 1
         else:
            self.pieceActivity[blackMove.piece] = 1

   def getMoveTuples(self):
      moves = [(self.whiteMoves[i], self.blackMoves[i]) for i in range(len(self.blackMoves))]
      if len(self.whiteMoves) > len(self.blackMoves):
         moves.append((self.whiteMoves[-1], None))
      return moves

   def mostActivePieces(self, num):
      activityTuples = [(p, self.pieceActivity[p]) for p in self.pieceActivity]
      mostActive = sorted(activityTuples, key=lambda t: t[1], reverse=True)
      if num > len(mostActive):
         num = len(mostActive)

      return [p for p, c in mostActive[:num]]

   def movesForPiece(self, piece):
      if Piece.isWhite(piece):
         return [move for move in self.whiteMoves if move.piece == piece]
      else:
         return [move for move in self.blackMoves if move.piece == piece]

   def getMove(self, num):
      if num >= self.totalMoves:
         return None
      while num < 0:
         num += self.totalMoves
      if (num % 2 == 0):
         return self.whiteMoves[num/2]
      else:
         return self.blackMoves[num/2]

   def makePGN(self):
     moves = self.gameDict['moves']

     pgn = ''
     for i in range(len(moves)):
       pgn = pgn + str(i) + '. ' + moves[i][0] + ' ' +  moves[i][1] + ' '

     return pgn[:-1]

   def printMoves(self):
      for i in range(self.totalMoves):
         self.getMove(i).printMove()

   def info(self):
      info = str(self.totalMoves) + ' moves.\n'
      info += 'Final Score: ' + str(self.finalScore[0]) + '-' + str(self.finalScore[1]) + '\n'
      mostActive = [Piece.name[p] for p in self.mostActivePieces(4)]
      info += 'Most Active Pieces:' + ', '.join(mostActive)
      return info

   def gameStats(self):
      moves = self.gameDict['moves']
      stats = {}     

      # checks
      stats['wCheck'] = len(filter(lambda x: "+" in x[0], moves))
      stats['bCheck'] = len(filter(lambda x: "+" in x[1], moves))
      stats['wToBCheckRatio'] = max(1.0, float(stats['wCheck']))/max(1.0, float(stats['bCheck']))

      # promotions (pawn => queen)
      stats['wPromote'] = len(filter(lambda x: "=" in x[0], moves))
      stats['bPromote'] = len(filter(lambda x: "=" in x[1], moves))
      stats['wToBPromoteRatio'] = max(1.0, float(stats['wPromote']))/max(1.0, float(stats['bPromote']))

      # capture of pieces
      stats['wCapture'] = len(filter(lambda x: 'x' in x[0], moves))
      stats['bCapture'] = len(filter(lambda x: 'x' in x[1], moves))
      stats['wToBCaptureRatio'] = max(1.0, float(stats['wCapture']))/max(1.0, float(stats['bCapture']))

      # castles 
      stats['wKCastle'] = len(filter(lambda x: 'O-O' in x[0] and 'O-O-O' not in x[0], moves))
      stats['bKCastle'] = len(filter(lambda x: 'O-O' in x[1] and 'O-O-O' not in x[1], moves))

      stats['wQCastle'] = len(filter(lambda x: 'O-O-O' in x[0], moves))
      stats['bQCastle'] = len(filter(lambda x: 'O-O-O' in x[1], moves))

      # specific parts of the game
      # ==== EARLY (FIRST 1/3) ====
      stats['wEarlyCap'] = len(filter(lambda x: 'x' in x[0], moves[:len(moves)/3]))
      stats['bEarlyCap'] = len(filter(lambda x: 'x' in x[1], moves[:len(moves)/3]))

      stats['wEarlyCheck'] = len(filter(lambda x: '+' in x[0], moves[:len(moves)/3]))
      stats['bEarlyCheck'] = len(filter(lambda x: '+' in x[1], moves[:len(moves)/3]))

   # ==== LATE (LAST 1/3) ====
      stats['wLateCap'] = len(filter(lambda x: 'x' in x[0], moves[2*len(moves)/3:]))
      stats['bLateCap'] = len(filter(lambda x: 'x' in x[1], moves[2*len(moves)/3:]))

      stats['wLatePromote'] = len(filter(lambda x: '=' in x[0], moves[2*len(moves)/3:]))
      stats['bLatePromote'] = len(filter(lambda x: '=' in x[1], moves[2*len(moves)/3:]))


      # Outcome
      if '1/2' in self.gameDict['Result']:
        stats['outcome'] = "tie"
      elif '1-0' in self.gameDict['Result']:
        stats['outcome'] = "white"
      elif '0-1' in self.gameDict['Result']:
        stats['outcome'] = "black"
      else: 
        stats['outcome'] = None

      print sorted(stats.iteritems(), key=lambda x: x[0])
      return stats
