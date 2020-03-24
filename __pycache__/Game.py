import pygame
import random
import math
from network import Network
import json
from threading import Thread
pygame.init()



#colours
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)




#setup
size = (500, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pong")
done = True
clock = pygame.time.Clock()
PI = 3.141592653




#idk what this does but i dont want to remove it
clientNumber = 0


#client side variables
bulletPos = 10
dead = True
bullet = None
astroid = None
bullets = []
astroids = []
newAstroidList = [[25,580]]
score = 0
allBulletPos = []
spawnTimer = 30

#some networking variables
n = None
oldData = None




class Astroid():
    def __init__(self):
        #set the speeds of the astroid
        self.xSpeed = random.randrange(-5,5)
        self.ySpeed = random.randrange(2,5)
        #set the starting position of the astroid
        self.xPos = random.randrange(0,500)
        self.yPos = 1
        #sets other variales you need
        self.alive = True
        self.found = False
        self.colour = (random.randrange(50,250),random.randrange(50,250),random.randrange(50,250))
        #for moving the astroid in a curve
        self.offset = 0
        
    def update(self):
        if self.alive:
            #adds the curve
            self.offset =  math.sin(pygame.time.get_ticks()*0.001) * 5
            #moves the astroid
            self.xSpeed = self.offset
            self.xPos +=self.xSpeed
            self.yPos += self.ySpeed
            #draws the astroid   
            pygame.draw.ellipse(screen, self.colour, [self.xPos, self.yPos, 50, 50])
    #givs the position of the astroid to send to the server
    def getPos(self):
        return [self.xPos,self.yPos,self.colour]
        
#the class for the bullets

class player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        #sets the position and movenment of the player
        self.xPos = x
        self.yPos = y
        self.xSpeed = 5
        self.ySpeed = 5
        global bullets
        #controlls
        self.upHeld = False
        self.downHeld = False
        self.leftHeld = False
        self.rightHeld =False
        #alternates the position of the bullets that are shot
        self.cannonFiring = True
        #defines the image
        self.spaceship = pygame.image.load("assets\\ship.png")
    def Move(self):
        #do inputs
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.upHeld = True
                if event.key == pygame.K_s:
                    self.downHeld = True
                if event.key == pygame.K_a:
                    self.leftHeld = True
                if event.key == pygame.K_d:
                    self.rightHeld = True        
                if event.key == pygame.K_SPACE:
                    self.Shoot()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.upHeld = False
                if event.key == pygame.K_s:
                    self.downHeld = False
                if event.key == pygame.K_a:
                    self.leftHeld = False
                if event.key == pygame.K_d:
                    self.rightHeld = False

        if self.upHeld:
            if not (self.yPos - self.ySpeed < 0):
                self.yPos -= self.ySpeed
        if self.downHeld:
            if not (self.yPos + self.ySpeed > 550):
                self.yPos += self.ySpeed
        if self.leftHeld:
            if not (self.xPos - self.xSpeed < 0):
                self.xPos -= self.xSpeed
        if self.rightHeld:
            if not (self.xPos + self.xSpeed > 450):
                self.xPos += self.xSpeed
        self.update()
    def update(self):
        screen.blit(self.spaceship, [self.xPos, self.yPos]) #draws the player

    def Shoot(self):
        bullets.append(Bullet(self.xPos,self.yPos,self.cannonFiring, self)) #adds a new bullet to the list


class Bullet():
    def __init__(self, x,y, cf, player):
        self.alive =True
        self.y = y +10
        if player.cannonFiring == True:
            self.x = x
            player.cannonFiring = False
        elif player.cannonFiring == False:
            self.x = x +40
            player.cannonFiring = True
        self.alive = True
        self.update()
    def update(self):
        if self.alive:
            pygame.draw.rect(screen,WHITE,[self.x,
                                           self.y,10,20])
            self.y -= 10
    
    def givePos(self):
        posLis = [self.x,self.y]
        return posLis
        

                 
                            
recData =''
def sendData():
    global ingame
    bulletPosList =[]
    for b in bullets:
        bulletPosList.append(b.givePos())
    astroidPosList = []
    for a in astroids:
        astroidPosList.append(a.getPos())
    playerData = {
        'pos' : [p.xPos,p.yPos],
        'bullets' : bulletPosList,
        'astroids' : astroidPosList,
        'inGame' : ingame
    }
    #print('local',playerData)
    return n.sendr(json.dumps(playerData))





#spawns the astroids  
def spawn(data):
    if data['inGame'] == True:
        currentAstroid = Astroid()
        astroids.append(currentAstroid)
    pass
#Draws the bullets
def drawServBullets(data):
    for b in data['bullets']:
        pygame.draw.rect(screen,WHITE,[b[0],
                                           b[1],10,20])
#Draws the astroids
def drawAstroids(data):
    for a in data['astroids']:
        #print('bruh')
        pygame.draw.ellipse(screen, a[2], [a[0], a[1], 50, 50])
        pass
    
#i dont think this does anything but idk if i need it
def getData():
    #print(n.getPos())
    pass
    
#calculates the collisions for the local bullets with the local and server astroids
def doAstroidCollision(a):
    global bullets
    global score
    found = False
    for bullet in bullets:
            for i in range(bullet.y,bullet.y+20) :
                if i in range(a[1],a[1]+50)and found == False:
                    for i in range(bullet.x,bullet.x+10):
                        if i in range(int(a[0]),int(a[0]+50))and found == False:
                            #a.alive = False
                            bullet.alive = False
                            found = True
                            score += 1
def doLocalAstroidCollision(a):
    global allBulletPos
    global score
    found = False
    for bullet in allBulletPos:
            for i in range(bullet[1],bullet[1]+20) :
                if i in range(a.yPos,a.yPos+50)and found == False:
                    for i in range(bullet[0],bullet[0]+10):
                        if i in range(int(a.xPos),int(a.xPos+50))and found == False:
                            #a.alive = False
                            #bullet.alive = False
                            found = True
                            a.alive = False
                            #score += 1


#startPos = read_pos(n.getPos())

startPos = [225,500]
p = player(startPos[0],startPos[1])
p2 = player(255,500)

ip = input('Ip: ')
n = Network(ip)


# -------- Main Program Loop -----------
while True:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                done = False
    ingame = False     
    while done == False:
        
        ingame = True
        screen.fill(BLACK)
        strData = sendData()
        
        try:
            from_pos = strData.find('{')
            to_pos = strData.find('}') + 1
            strData = strData[from_pos:to_pos]
            data = json.loads(strData)
            oldData = data
            
        except:
            data = oldData
            
        drawServBullets(data)
        drawAstroids(data)

        bulletPosList =[]
        for b in bullets:
            bulletPosList.append(b.givePos())
        allBulletPos = bulletPosList + data['bullets']
        #print(allBulletPos)
        astroidPosList = []
        for a in astroids:
            astroidPosList.append(a.getPos())
        allAstroidPos = data['astroids'] + astroidPosList
        for a in allAstroidPos:
            doAstroidCollision(a)
        for a in astroids:
            doLocalAstroidCollision(a)
        
        
        

        #clean the astroid and bullet list
        new_bullets = []
        for bullet in bullets:
            bullet.update()
            if bullet.alive:
                new_bullets.append(bullet)
        bullets = new_bullets

        newAstroids = []
        for astroid in astroids:
            astroid.update()
            if astroid.alive == True:
                newAstroids.append(astroid)
                newAstroidList.append([astroid.xPos,astroid.yPos])
        astroids = newAstroids

        #score renderer
        font = pygame.font.SysFont('Calibri', 50, True, False)
        scoreText = font.render(str(score), True, WHITE)
        scoreTextRect = scoreText.get_rect(center=(500/2, 25))
        screen.blit(scoreText, scoreTextRect)

        '''
        #detects player + astroid colision
        for a in astroids:
            for x in range(xPos, xPos + 50):
                if x in range(int(a.xPos),int(a.xPos+100)):
                    for y in range(yPos,yPos+50):
                        if y in range(a.yPos,a.yPos+100):
                            if not dead:
                                dead = True
                                #sorts and saves the scores
                                rF = open("assets\scores.txt", "w+")
                                scores.append(score)
                                for i in scores:
                                    rF.write(str(i)+"\n")
                                rF.close
                                scores.sort()
                                '''
        #p2Pos = read_pos(n.send(make_pos((p.xPos, p.yPos))))
        #print('recived',data)
        p2Pos = data['pos']
        p2.xPos = p2Pos[0]
        p2.yPos = p2Pos[1]
        p2.update()      
        p.Move()              
        
        #thins oit the astroid and bullet list to prevent lag
        if len(astroids) > 10:
            del astroids[0]
        if len(bullets) > 5:
            del bullets[0]

        #times spawning
        spawnTimer -=1
        if spawnTimer == 0:
            spawn(data)
            spawnTimer = 30
        
        #renders the ship
        


        

        pygame.display.flip()
        #allows the app to continue out of the game loop
        clock.tick(60)
    pygame.display.flip()
    #allows the app to continue out of the game loop
    clock.tick(60)
    
pygame.quit()