import pygame
import random
import math
from network import Network
import json
pygame.init()



#colours
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

PI = 3.141592653

astroidImg = pygame.image.load("assets\\Astroid.png")

playerImgs = {
'p1': pygame.image.load("assets\\TestShip.png"),
'p2': pygame.image.load("assets\\TestShip2.png"),
'null': pygame.image.load("assets\\NullShip.png")
}
#setup
n = None
size = (500, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pong")
done = True
clock = pygame.time.Clock()


spawnTimer = 30


clientNumber = 0


#various variables
bulletPos = 10
dead = True
bullet = None
astroid = None
bullets = []
astroids = []
newAstroidList = [[25,580]]

oldData = None
#current score
score = 0
allBulletPos = []


class Astroid():
    def __init__(self,icon):
        
        self.xSpeed = random.randrange(-5,5)
        self.ySpeed = random.randrange(2,5)
        self.xPos = random.randrange(0,500)
        self.yPos = 1
        self.img = icon
        self.alive = True
        self.found = False
        self.offset = 0
        
        self.colour = (random.randrange(50,250),random.randrange(50,250),random.randrange(50,250))
    def update(self):
        if self.alive:
            self.offset =  math.sin(pygame.time.get_ticks()*0.001) * 5
            self.xSpeed = self.offset
            self.xPos +=self.xSpeed
            self.yPos += self.ySpeed 
            screen.blit(self.img, [self.xPos, self.yPos])
            #pygame.draw.ellipse(screen, self.colour, [self.xPos, self.yPos, 50, 50])
    def getPos(self):
        return [self.xPos,self.yPos,self.colour]

    def detectCollisions(self):
        pass
        

class player(pygame.sprite.Sprite):
    def __init__(self,x,y,imgs):
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
        self.cannonFiring = True
        #self.spaceship.set_colorkey(WHITE)
        self.useNullImg = True
        self.isP1 = False
        self.imgs = imgs
        self.img = imgs['null']
    def Move(self):
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

        if self.useNullImg:
            self.img = self.imgs['null']
        elif self.isP1:
            self.img = self.imgs['p1']
        else:
            self.img = self.imgs['p2']
        screen.blit(self.img, [self.xPos, self.yPos])


    def Shoot(self):
        bullets.append(Bullet(self.xPos,self.yPos,self.cannonFiring, self))


class Bullet():
    def __init__(self, x,y, cf, player):
        cannonFiring = cf
        
        self.alive =True

        
        self.y = y +10
        if cannonFiring == True:
            self.x = x
            player.cannonFiring = False
        elif cannonFiring == False:
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
    return n.sendr(json.dumps(playerData))





#spawns the astroids  
def spawn(data):
    if data['inGame'] == True:
        currentAstroid = Astroid(astroidImg)
        astroids.append(currentAstroid)
    pass
#draws the bullets from the server
def drawServBullets(data):
    for b in data['bullets']:
        pygame.draw.rect(screen,WHITE,[b[0],
                                           b[1],10,20])
#draws the astroids from the server
def drawAstroids(data):
    for a in data['astroids']:
        screen.blit (astroidImg,[a[0], a[1]])
        #pygame.draw.ellipse(screen, a[2], [a[0], a[1], 50, 50])
        pass
    
def doAstroidCollision(a):
    global bullets
    global score
    found = False
    for bullet in bullets:
            for i in range(bullet.y,bullet.y+20) :
                if i in range(a[1],a[1]+50)and found == False:
                    for i in range(bullet.x,bullet.x+10):
                        if i in range(int(a[0]),int(a[0]+50))and found == False:
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
                            found = True
                            a.alive = False



startPos = [225,500]
p = player(startPos[0],startPos[1],playerImgs)
p2 = player(255,500,playerImgs)
ip = input('Ip: ')
n = Network(ip)

# -------- Main Program Loop -----------
while True:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                done = False
    #screen.blit(testIMG, [100, 100])
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
            
        p.useNullImg = False
        p.isP1 = data['player'] == 1
        p2.useNullImg = False
        p2.isP1 = not data['player'] == 1



        drawServBullets(data)
        drawAstroids(data)

        bulletPosList =[]
        for b in bullets:
            bulletPosList.append(b.givePos())
        allBulletPos = bulletPosList + data['bullets']

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
        


        

        pygame.display.flip()
        clock.tick(60)
    pygame.display.flip()
    #allows the app to continue out of the game loop
    clock.tick(60)
    
pygame.quit()