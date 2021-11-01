import random

class new_maze:
    def __init__(self,maze):
        self.gridList = maze.read().split()
        for i in range(len(self.gridList[-1])):
            if self.gridList[-1][i]=='^':
                self.current = i
        self.layer = -1
        self.checkpoint = []
        self.moves = []
        self.close = False
    
    def findEnd(self):
        if self.close:
            return -1           
        if abs(self.layer) == len(self.gridList):
            self.moves.append([self.layer,self.current])
            return 1
        else:
            self.search()
            return 0
        
    def search(self):
        intersection = 0
        self.openSpots = []
        #print(abs(self.layer),self.current+1)
        if abs(self.layer)<len(self.gridList) and self.gridList[self.layer-1][self.current] == '^' and (not[self.layer-1,self.current] in self.moves):
            intersection+=1
            self.openSpots.append([self.layer-1,self.current])
        if self.current<len(self.gridList[self.layer])-1 and self.gridList[self.layer][self.current+1] == '^' and (not [self.layer,self.current+1] in self.moves):
            intersection+=1
            self.openSpots.append([self.layer,self.current+1])
        if self.current>0 and self.gridList[self.layer][self.current-1] == '^' and (not [self.layer,self.current-1] in self.moves):
            intersection+=1
            self.openSpots.append([self.layer,self.current-1])
        if abs(self.layer)>1 and self.gridList[self.layer+1][self.current] == '^' and (not [self.layer+1,self.current] in self.moves):
            intersection+=1
            self.openSpots.append([self.layer+1,self.current])
            
        self.moves.append([self.layer,self.current])
        if intersection>1:
            self.checkpoint.append([self.layer,self.current])
            self.makeMove()
        elif intersection==1:
            self.makeMove()      
        else:
            try:
                jumpTo = self.checkpoint.pop()
                self.layer = jumpTo[0]
                self.current = jumpTo[1]
            except:
                print("Not Solvable")
                self.close = True
                
    def makeMove(self):
        # self.layer, self.current = self.openSpots[random.randrange(0,len(self.openSpots))]
        self.layer, self.current = self.openSpots[0]
        
    def displayRoute(self):
        maze,layer = [],[]
        for i in range(len(self.gridList)):
            for j in range(len(self.gridList[0])):
                layer.append('0')            
            maze.append(layer)
            layer=[]
        
        for i in range(len(self.moves)):
            maze[self.moves[i][0]][self.moves[i][1]] = '*'
        for i in maze:
            for j in i:
                print(j,end='')
            print()

    def saveSolution(self):
        maze,layer = [],[]
        for i in range(len(self.gridList)):
            for j in range(len(self.gridList[0])):
                layer.append('#')            
            maze.append(layer)
            layer=[]
        
        for i in range(len(self.moves)):
            maze[self.moves[i][0]][self.moves[i][1]] = '^'
        
        with open('solution.txt', 'w') as f:
            for i in maze:
                for j in i:
                    f.write(j)
                f.write('\n')
            
def main():
    fileMaze = open('maze_test.txt')
    maze = new_maze(fileMaze)
    fileMaze.close()
    found = False
    while found == 0:
        found = maze.findEnd()
    if found == -1:
        print("Program ended")
    else:
        print("Solved")
        # maze.displayRoute()
        maze.saveSolution()
main()