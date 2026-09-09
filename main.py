import pygame
import random
import time
import mysql.connector
import bcrypt
from database import connectDB
pygame.mixer.init(44100, -16, 2, 2048)
pygame.init()

#Initialises screen and loads all assets
screen = pygame.display.set_mode((1200, 675))
pygame.display.set_caption('Mygame')
clock = pygame.time.Clock()
ssfont = pygame.font.Font('font\MSGothic.ttf', 50)
chestFont=pygame.font.Font('font\MSGothic.ttf', 35)
title = pygame.image.load("graphics/fonts/title.png")
menubackground = pygame.transform.scale(pygame.image.load('graphics/backgrounds/menuBackground.png'), (1200, 675))
level1background= pygame.transform.scale(pygame.image.load('graphics/backgrounds/level1.png'), (1200, 675))
level1music=pygame.mixer.Sound("audio/track1.mp3")
level1music.set_volume(0.1)
level2background= pygame.transform.scale(pygame.image.load('graphics/backgrounds/level2.png'), (1200, 675))
level2music=pygame.mixer.Sound("audio/track2.mp3")
level2music.set_volume(0.1)
level3background= pygame.transform.scale(pygame.image.load('graphics/backgrounds/level3.png'), (1200, 675))
level3music=pygame.mixer.Sound("audio/track3.mp3")
level3music.set_volume(0.1)
hitSound=pygame.mixer.Sound("audio/hit.mp3")
hitSound.set_volume(0.2)
openChestSound=pygame.mixer.Sound("audio/openChest.flac")
mouseClickSound=pygame.mixer.Sound("audio/mouseClick.mp3")
deathSound=pygame.mixer.Sound("audio/death.mp3")
victorySound=pygame.mixer.Sound("audio/victory.wav")
victorySound.set_volume(0.5)
bgm = pygame.mixer.Sound("audio/backgroundMusic.mp3")
bgm.set_volume(0.1)
bg_X=0
totalScore=0
levelStartTime=pygame.time.get_ticks()
chestStartTime=pygame.time.get_ticks()
soundOn=pygame.image.load('graphics/soundOn.png')
soundOn=pygame.transform.scale(soundOn,(66,54))
soundOff=pygame.image.load('graphics/soundOff.png')
soundOff=pygame.transform.scale(soundOff,(66,54))
backButton=pygame.image.load('graphics/back.png')
backButton=pygame.transform.scale(backButton, (75, 53))

#Flags
soundState=True
paused=False
victory=False
currentScreen="menuScreen"

#Dictionary which stores the levels
levels = [
      {'level': 1, 'playable': True, 'completed': False},
      {'level': 2, 'playable': False, 'completed': False},
      {'level': 3, 'playable': False, 'completed': False}]

#Dictionary which stores the menu items
menuItems = [ {'text': 'New Game', 'position': (580, 270), 'image': 'graphics/fonts/newGame.png'},
  {'text': 'Controls', 'position': (580, 370), 'image': 'graphics/fonts/controls.png'},
  {'text': 'Continue', 'position': (580, 470), 'image': 'graphics/fonts/continue.png'},
  {'text': 'Quit Game', 'position': (580, 570), 'image': 'graphics/fonts/quitGame.png'},
  {'text': 'High Scores', 'position': (250, 370), 'image': 'graphics/fonts/highScores.png'}]

#Displays these items
for item in menuItems:
    if item['text'] != 'High Scores': 
        item['surface'] = ssfont.render(item['text'], False, (255, 255, 255))
        item['rect'] = item['surface'].get_rect(center=item['position'])
    else:
        item['surface'] = pygame.image.load(item['image'])
        item['rect'] = item['surface'].get_rect(center=item['position'])

#Dictionary which stores the controls
currentControls={'Move Left': 'A', 'Move Right': 'D',
    'Pause/Resume': 'P', 'Restart': 'R',
    'Punch': 'T', 'Kick': 'Y', 'Open Chest': 'O', 'Jump': 'W'}

class Chest:
    def __init__(self, x, y, player):
        #Attributes
        self.x = x
        self.y = y
        self.width = 72
        self.height = 72
        self.closedImage = pygame.transform.scale(pygame.image.load("graphics/closedChest.png"), (72, 72))
        self.openedImage = pygame.transform.scale(pygame.image.load("graphics/openChest.png"), (72, 72))
        self.player = player
        self.powerUpType = None
        self.chestText = None
        self.playerText = None
        self.textY = None
        self.powerUpStartTime = None
        self.disappear=False
        self.isOpened = False

    #Methods
    def draw(self, screen):
        if self.isOpened:
            image = self.openedImage 
        else :
            image = self.closedImage
        if not self.disappear:
            screen.blit(image, (self.x, self.y))
        if not paused and player.health>0 and not victory:
            self.y += 10
            if self.y > 603:
                self.y = 603
        if self.isOpened and self.chestText:
            if self.textY == None:
                self.textY=self.y-20
            chestTextSurface = chestFont.render(self.chestText, True, (255, 20, 20))
            screen.blit(chestTextSurface, (self.x, self.textY))
            self.textY -= 2
            if self.textY <= self.y - 52:
                self.chestText = None
        if self.powerUpType == "speed" and self.playerText:
            playerTextSurface = chestFont.render(self.playerText, True, (255, 20, 20))
            screen.blit(playerTextSurface, (self.player.x + 30, self.player.y))

    def interact(self, playerRect):
        chestRect = pygame.Rect(self.x, self.y, self.width, self.height)
        if playerRect.colliderect(chestRect) and pygame.key.get_pressed()[pygame.key.key_code(currentControls['Open Chest'])] and not self.isOpened and not paused:
            self.openChest()

    def openChest(self):
        global totalScore
        self.isOpened = True
        if soundState:
         openChestSound.play()
        self.powerUpType = random.choice(["speed","health","score"])
        if self.powerUpType == "speed":
            self.player.speed += 5
            self.chestText = "+5 Speed"
            self.powerUpStartTime = time.time()
            self.playerText = "10"
        elif self.powerUpType == "health":
            self.player.health += 5
            self.chestText = "+5 Health"
        elif self.powerUpType == "score":
            self.player.score += 5
            self.chestText = "+5 Score"
        self.openedTime = time.time()

    def resetChest(self):
        self.isOpened = False
        self.chestText = None
        self.playerText = None
        self.textY = None
        self.powerUpType = None
        self.powerUpStartTime = None

    def update(self):
        global elapsedTime
        if not paused and player.health>0 and not victory:
            if self.powerUpType == "speed" and self.powerUpStartTime:
                if not paused and player.health>0 and not victory:
                    elapsedTime = time.time() - self.powerUpStartTime
                    self.playerText = str(10 - int(elapsedTime))
                if elapsedTime > 10:
                    self.player.speed -= 5
                    self.powerUpType = None
                    self.powerUpStartTime = None
                    self.playerText = None
            if self.isOpened and self.openedTime:
                if time.time() - self.openedTime > 3:
                    self.disappear=True

class Player:
  def __init__(self, x, y):
      #Attributes
      self.x = x
      self.y = y
      self.width = 72
      self.height = 144
      self.speed = 10
      self.health = 50
      self.score = 0
      self.animationFrame = 0
      self.velocityY = 0
      self.idleImages = [self.scaleImage(pygame.image.load(f"graphics/playerAnimations/Idle/playerIdle{x}.png")) for x in range(4)]
      self.jumpImages = [self.scaleImage(pygame.image.load(f"graphics/playerAnimations/Jump/playerJump{x}.png")) for x in range(4)]
      self.kickImages = [self.scaleImage(pygame.image.load(f"graphics/playerAnimations/Kick/playerKick{x}.png")) for x in range(6)]
      self.runImages = [self.scaleImage(pygame.image.load(f"graphics/playerAnimations/Run/playerRun{x}.png")) for x in range(6)]
      self.punchImages = [self.scaleImage(pygame.image.load(f"graphics/playerAnimations/Punch/playerPunch{x}.png")) for x in range(8)]
      self.deathImages = [self.scaleImage(pygame.image.load(f"graphics//playerAnimations/Death/playerDeath{x}.png")) for x in range(6)]
      self.currentAnimation = self.idleImages
      self.flip = False
      self.isJumping = False
      self.isRunning = False

  #Methods
  def scaleImage(self, image):
    width, height = image.get_size()
    return pygame.transform.scale(image, (width * 3, height * 3))
  
  def getHealth(self):
        return self.health

  def update(self, keys, enemies):
      global soundState
      if paused or victory:
        return
      if self.health <= 0:
        self.death()
        return

    #Taking inputs
      if not paused and not victory:
        if keys[pygame.key.key_code(currentControls['Move Left'])]:
            self.x -= self.speed
            self.flip = True
            self.run()
        elif keys[pygame.key.key_code(currentControls['Move Right'])]:
            self.x += self.speed
            self.flip = False
            self.run()
        else:
            self.idle()
        if keys[pygame.key.key_code(currentControls['Jump'])]:
            if not self.isJumping:
                self.isJumping = True
                self.velocityY = -18
                self.jump()
        if keys[pygame.key.key_code(currentControls['Punch'])] and not (keys[pygame.key.key_code(currentControls['Move Left'])] or keys[pygame.key.key_code(currentControls['Move Right'])]):
           self.punch()
        elif keys[pygame.key.key_code(currentControls['Kick'])] and not (keys[pygame.key.key_code(currentControls['Move Left'])] or keys[pygame.key.key_code(currentControls['Move Right'])]):
           self.kick()
      if self.x < 0:
        self.x = 1200
      elif self.x > 1200:
        self.x = 0
      self.velocityY += 1
      self.y += self.velocityY
      if self.y > 675 - self.height:
        self.y = 675 - self.height
        self.velocityY = 0
        self.isJumping=False
      self.animationFrame += 1
      playerRect = pygame.Rect(self.x, self.y, self.width, self.height)
      for enemy in enemies:
        enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
        if playerRect.colliderect(enemyRect) and (keys[pygame.key.key_code(currentControls['Punch'])] or keys[pygame.key.key_code(currentControls['Kick'])]) and enemy.health > 0 and not paused:
            if soundState: hitSound.play()
            enemy.health -= 1.25
            if enemy.health <= 0:
                enemy.death()
                self.score+=5
                return
          
  def draw(self, screen):
      if self.animationFrame >= len(self.currentAnimation):
         self.animationFrame = 0
      currentFrame = self.currentAnimation[self.animationFrame]
      if self.flip:
          currentFrame = pygame.transform.flip(currentFrame, True, False)
          screen.blit(currentFrame, (self.x - self.width, self.y))
      else:
          screen.blit(currentFrame, (self.x, self.y))

  #Animating character
  def idle(self):
      self.currentAnimation = self.idleImages

  def jump(self):
      self.currentAnimation = self.jumpImages
      self.isJumping=True

  def kick(self):
      self.currentAnimation = self.kickImages

  def run(self):
      self.currentAnimation = self.runImages
      self.isRunning=True

  def punch(self):
      self.currentAnimation = self.punchImages

  def death(self):
    self.currentAnimation = self.deathImages
    self.animationFrame = len(self.currentAnimation) - 1
    self.speed = 0

class Enemy:
  def __init__(self, x, y):
      #Attributes
      self.x = x
      self.y = y
      self.width = 72
      self.height = 144
      self.speed = 10
      self.health = 50
      self.animationFrame = 0
      self.idleImages = [self.scaleImage(pygame.image.load(f"graphics/enemyAnimations/Idle/enemyIdle{x}.png")) for x in range(4)]
      self.kickImages = [self.scaleImage(pygame.image.load(f"graphics/enemyAnimations/Kick/enemyKick{x}.png")) for x in range(6)]
      self.runImages = [self.scaleImage(pygame.image.load(f"graphics/enemyAnimations/Run/enemyRun{x}.png")) for x in range(6)]
      self.punchImages = [self.scaleImage(pygame.image.load(f"graphics/enemyAnimations/Punch/enemyPunch{x}.png")) for x in range(8)]
      self.deathImages = [self.scaleImage(pygame.image.load(f"graphics/enemyAnimations/Death/enemyDeath{x}.png")) for x in range(6)]
      self.currentAnimation = self.idleImages
      self.flip = False
      self.isJumping = False
      self.isRunning = False
      self.isDead = False
      self.isAttacking = False

  #Methods
  def scaleImage(self, image):
    width, height = image.get_size()
    return pygame.transform.scale(image, (width * 3, height * 3))
  
  def getHealth(self):
        return self.health
  
  def update(self, playerX, playerY, playerWidth, playerHeight):
      if paused:
        return
      if self.health <= 0:
        self.death()
        return
      if self.isAttacking:
        player.health -= 0.125
        if player.health <= 0:
            player.death()
            return
      self.animationFrame += 1
      if self.animationFrame >= len(self.currentAnimation):
          self.animationFrame = 0
          if self.isAttacking:
              if self.currentAttack == "punch":
                  self.kick()
              else:
                  self.punch()

      if self.x < 0:
          self.x = 1200
      elif self.x > 1200:
          self.x = 0

      if self.y > 675 - self.height:
          self.y = 675 - self.height

      enemyRect = pygame.Rect(self.x, self.y, self.width, self.height)
      playerRect = pygame.Rect(playerX, playerY, playerWidth, playerHeight)
      if enemyRect.colliderect(playerRect):
          if not self.isAttacking:
              self.isAttacking = True
              if random.choice([True, False]):
                  self.punch()
              else:
                  self.kick()
      else:
          if self.isAttacking:
              self.isAttacking = False
              self.run()
          if self.x < playerX:
              self.x += self.speed
              self.flip = False
          elif self.x > playerX:
              self.x -= self.speed
              self.flip = True
      if not self.isAttacking:
          self.run()

  def draw(self, screen):
      currentFrame = self.currentAnimation[self.animationFrame]
      if self.flip:
          currentFrame = pygame.transform.flip(currentFrame, True, False)
          screen.blit(currentFrame, (self.x - self.width, self.y))
      else:
          screen.blit(currentFrame, (self.x, self.y))

  #Animating character
  def idle(self):
      if self.currentAnimation != self.idleImages:
          self.currentAnimation = self.idleImages
          self.animationFrame = 0

  def kick(self):
      if self.currentAnimation != self.kickImages:
          self.currentAnimation = self.kickImages
          self.animationFrame = 0
      self.currentAttack = "kick"

  def run(self):
    if not self.isAttacking:
        if self.currentAnimation != self.runImages:
            self.currentAnimation = self.runImages
            self.animationFrame = 0
        self.isRunning = True

  def punch(self):
      if self.currentAnimation != self.punchImages:
          self.currentAnimation = self.punchImages
          self.animationFrame = 0
      self.currentAttack = "punch"

  def death(self):
      self.currentAnimation = self.deathImages
      self.animationFrame = len(self.currentAnimation) - 1
      self.speed = 0

def registerUser(username, password, confirmPassword):
    global levels, currentUser
    #Error messages
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if password != confirmPassword:
        return "Passwords do not match."

    #Hashes password and connects to database
    passwordHash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connectDB()
    cursor = conn.cursor()

    #Inserts records into database
    try:
        cursor.execute("""
            INSERT INTO users (username, passwordHash, totalScore, 
                               level1Playable, level2Playable, level3Playable, 
                               level1Completed, level2Completed, level3Completed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, passwordHash, 0, 1, 0, 0, 0, 0, 0)) 
        conn.commit()
        currentUser=username
        levels = [
            {'level': 1, 'playable': True, 'completed': False},
            {'level': 2, 'playable': False, 'completed': False},
            {'level': 3, 'playable': False, 'completed': False}]
        return "Registration successful!"
    except mysql.connector.IntegrityError:
        return "Username taken."
    finally:
        cursor.close()
        conn.close()

def loginUser(username, password):
    global levels, currentUser, totalScore
    
    #Connects to database
    conn = connectDB()
    cursor = conn.cursor()
    
    #Retrieves records from database
    cursor.execute("""
    SELECT passwordHash, totalScore, level1Playable, level2Playable, level3Playable, 
           level1Completed, level2Completed, level3Completed 
    FROM users 
    WHERE username = %s
    """, (username,))
    result = cursor.fetchone()

    if result:
        storedPasswordHash, DBtotalScore, l1p, l2p, l3p, l1c, l2c, l3c = result
        storedPasswordHash = result[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), storedPasswordHash):
            currentUser=username
            totalScore=DBtotalScore
            levels = [
                {'level': 1, 'playable': l1p, 'completed': l1c},
                {'level': 2, 'playable': l2p, 'completed': l2c},
                {'level': 3, 'playable': l3p, 'completed': l3c}]
            return "Login successful!"
        else:
            return "Incorrect password."
    else:
        return "Username not found."

def saveProgress(totalScore, levels):
    global currentUser
    
    #Connects to database
    conn = connectDB()
    cursor = conn.cursor()
    
    #Updates records in database
    cursor.execute("""
        UPDATE users 
        SET totalScore = %s, 
            level1Playable = %s, level2Playable = %s, level3Playable = %s,
            level1Completed = %s, level2Completed = %s, level3Completed = %s
        WHERE username = %s
    """, (totalScore, levels[0]['playable'], levels[1]['playable'], levels[2]['playable'],
          levels[0]['completed'], levels[1]['completed'], levels[2]['completed'], currentUser))
    conn.commit()
    cursor.close()
    conn.close()

def drawPlayerHealthBar(health):
    for x in range(50):
        if x < health:
            pygame.draw.rect(screen, (0, 255, 0), (x * 4 + 50, 120, 4, 20))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (x * 4 + 50, 120, 4, 20))

def drawPlayerBox(health):
    global currentUser
    scoreText = ssfont.render(f"{player.score}", True, (255, 20, 20))
    screen.blit(scoreText, (120, 55))

    usernameText = ssfont.render(f"{currentUser}", True, (255, 20, 20))
    screen.blit(usernameText, (50, 5))

    playerIcon = pygame.image.load('graphics/playerIcon.png')
    playerIcon = pygame.transform.scale(playerIcon, (60, 60))
    screen.blit(playerIcon, (50, 55))
    drawPlayerHealthBar(health)

def drawEnemyHealthBar(health, y):
    for x in range(50):
        if x < health:
            pygame.draw.rect(screen, (0, 255, 0), (1150 - x * 4, y, 4, 20))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (1150 - x * 4, y, 4, 20))

def drawEnemyBox(health, y):
    enemyIcon = pygame.image.load('graphics/enemyIcon.png')
    enemyIcon = pygame.transform.scale(enemyIcon, (60, 60))
    screen.blit(enemyIcon, (1090, 55))
    drawEnemyHealthBar(health, y)

def drawBackground():
    global bg_X
    bg_X -= 2 
    if bg_X <= -1200:
        bg_X = 0
    screen.blit(menubackground, (bg_X, 0))
    screen.blit(menubackground, (bg_X + 1200, 0))

def drawSoundButton():
    if soundState:
        return screen.blit(soundOn, (100, 30))
    else:
        return screen.blit(soundOff, (100, 30))

def resetLevel():
    global player, enemies, levelStartTime, chests, victory
    victory=False
    player = Player(x=200, y=675)
    player.health=50
    player.score=0
    enemies=[Enemy(x=1000, y=675)]
    for enemy in enemies:
        enemy.health=50
    chests=[]
    levelStartTime = pygame.time.get_ticks()

def pauseScreen():
    surface=pygame.Surface((1200,675))
    surface.set_alpha(175)
    surface.fill((0, 0, 0))
    screen.blit(surface,(0,0))
    pausedText = ssfont.render(f"Press {currentControls['Pause/Resume']} to resume", True, (255, 255, 255))
    pausedTextRect = pausedText.get_rect(center=(600, 337))
    screen.blit(pausedText, pausedTextRect)

def deathScreen():
    global currentScreen
    if deathSound.get_num_channels()==0 and soundState==True:
        deathSound.play()
        
    keys = pygame.key.get_pressed()
    surface=pygame.Surface((1200,675))
    surface.set_alpha(175)
    surface.fill((0, 0, 0))
    screen.blit(surface, (0,0))
    deathText = ssfont.render(f"You died! Press {currentControls['Restart']} to try again", True, (255, 255, 255))
    deathTextRect = deathText.get_rect(center=(600, 337))
    screen.blit(deathText, deathTextRect)
    if keys[pygame.key.key_code(currentControls['Restart'])]:
     resetLevel()

def victoryScreen():
    global totalScore, currentScreen
    if victorySound.get_num_channels()==0 and soundState:
        victorySound.play()
    screen.blit(backButton,(10, 25))
    if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
          if pygame.mouse.get_pressed()[0]:
            currentScreen="levelSelection"
    for level in levels:
        if currentScreen == f"level{level['level']}" and not level['completed']:
            totalScore += player.score
            level['completed'] = True 
    surface=pygame.Surface((1200,675))
    surface.set_alpha(175)
    surface.fill((0, 0, 0))
    screen.blit(surface,(0,0))
    lines = [
        "Well done," + (currentUser) +  "!",
        f"Total score: {totalScore}",
        f"Remaining health: {int(player.getHealth())}"]
    yPos = 250
    for line in lines:
        textSurface = ssfont.render(line, True, (255, 255, 255))
        screen.blit(textSurface, textSurface.get_rect(center=(600, yPos)))
        yPos += 75
    saveProgress(totalScore, levels)  
    
def victory3Screen():
    global totalScore, currentScreen
    if victorySound.get_num_channels()==0 and soundState:
        victorySound.play()
    screen.blit(backButton, (10, 25))
    if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            for level in levels:
                if currentScreen == f"level{level['level']}":
                    totalScore += player.score
                    level['completed'] = True  
                    saveProgress(totalScore, levels)  
            currentScreen = "levelSelection"
    surface=pygame.Surface((1200,675))
    surface.set_alpha(175)
    surface.fill((0, 0, 0))
    screen.blit(surface,(0,0))
    lines = [
        "Congratulations," + (currentUser) +  "!",
        "You have conquered all.",
        "Go forth and see how your score compares."]
    yPos = 200
    for line in lines:
        textSurface = ssfont.render(line, True, (255, 255, 255))
        screen.blit(textSurface, textSurface.get_rect(center=(600, yPos)))
        yPos += 75
    highScoresButton=pygame.image.load("graphics/fonts/highScoresTitle.png")
    screen.blit(highScoresButton, highScoresButton.get_rect(center=(600, yPos + 30)))
    if highScoresButton.get_rect(center=(408, yPos + 30)).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        for level in levels:
            if currentScreen == f"level{level['level']}":
                totalScore += player.score
                level['completed'] = True  
                saveProgress(totalScore, levels)  
        currentScreen = "leaderboard"  

def menuScreen():
  drawBackground()
  soundButtonRect=drawSoundButton()
  screen.blit(title, (269, 45)) #Displays game title
  
  if soundState:
     soundButtonRect = screen.blit(soundOn, (100, 30))
     if bgm.get_num_channels()==0:
        pygame.mixer.stop()
        bgm.play(-1)
  else:
     soundButtonRect = screen.blit(soundOff, (100, 30))
     bgm.stop()

  for item in menuItems:
    if item['text'] == 'High Scores':
        item['surface'] = pygame.image.load(item['image'])
        item['rect'] = item['surface'].get_rect(center=item['position'])
    elif item['rect'].collidepoint(pygame.mouse.get_pos()):
        item['surface'] = pygame.image.load(item['image'])
        item['rect'] = item['surface'].get_rect(center=item['position'])
    else:
        item['surface'] = ssfont.render(item['text'], False, (255, 255, 255))
        item['rect'] = item['surface'].get_rect(center=item['position'])

    screen.blit(item['surface'], item['rect'])
  return soundButtonRect #Returns the value to the game loop

def registerScreen():
    global currentScreen, soundState
    username = ""
    password = ""
    confirmPassword = ""
    activeField = None
    inputBoxes = {
        "username": pygame.Rect(500, 200, 400, 50),
        "password": pygame.Rect(500, 300, 400, 50),
        "confirmPassword": pygame.Rect(500, 400, 400, 50)}

    while True:
        drawBackground()
        if soundState:
            screen.blit(soundOn, (100, 30))
            if bgm.get_num_channels() == 0:
                pygame.mixer.stop()
                bgm.play(-1)
        else:
            screen.blit(soundOff, (100, 30))
            bgm.stop()

        screen.blit(backButton, (10, 25))
        if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if soundState: mouseClickSound.play()
                global currentScreen
                currentScreen = "menuScreen"
                return

        registerText=pygame.image.load("graphics/fonts/register.png")
        screen.blit(registerText,(460, 15))
        screen.blit(ssfont.render("Username:", True, (255, 255, 255)), (250, 200))
        screen.blit(ssfont.render("Password:", True, (255, 255, 255)), (250, 300))
        screen.blit(ssfont.render("Confirm Password:", True, (255, 255, 255)), (50, 400))

        for field, rect in inputBoxes.items():
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=5)
            if field == "username":
              textToShow = username
            elif field == "password":
              textToShow = "*" * len(password)
            elif field == "confirmPassword":
              textToShow = "*" * len(confirmPassword)
            screen.blit(ssfont.render(textToShow, True, (0, 0, 0)), (rect.x + 10, rect.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for field, rect in inputBoxes.items():
                    if rect.collidepoint(event.pos):
                        activeField = field
                if pygame.Rect(100, 30, 66, 54).collidepoint(pygame.mouse.get_pos()):
                    soundState = not soundState

            elif event.type == pygame.KEYDOWN:
                if activeField:
                    if event.key == pygame.K_BACKSPACE:
                        if activeField == "username":
                            username = username[:-1]
                        elif activeField == "password":
                            password = password[:-1]
                        elif activeField == "confirmPassword":
                            confirmPassword = confirmPassword[:-1]
                    elif event.key == pygame.K_RETURN:
                        result = registerUser(username, password, confirmPassword)
                        if result == "Registration successful!":
                            currentScreen = "levelSelection"
                            return
                        elif result == "Password must be at least 8 characters.":
                            screen.blit(ssfont.render("Password must be at least 8 characters.", True, (255, 0, 0)), (150, 500))
                        elif result == "Passwords do not match.":
                            screen.blit(ssfont.render("Passwords don't match.", True, (255, 0, 0)), (370, 500))
                        elif result == "Username taken." :
                            screen.blit(ssfont.render("Username taken.", True, (255, 0, 0)), (400, 500))
                    else:
                        if activeField == "username":
                            username += event.unicode
                        elif activeField == "password":
                            password += event.unicode
                        elif activeField == "confirmPassword":
                            confirmPassword += event.unicode
        pygame.display.update()

def loginScreen():
    global currentScreen, soundState
    username = ""
    password = ""
    activeField = None
    inputBoxes = {
        "username": pygame.Rect(500, 200, 400, 50),
        "password": pygame.Rect(500, 300, 400, 50)}

    while True:
        drawBackground()
        if soundState:
            screen.blit(soundOn, (100, 30))
            if bgm.get_num_channels() == 0:
                pygame.mixer.stop()
                bgm.play(-1)
        else:
            screen.blit(soundOff, (100, 30))
            bgm.stop()

        screen.blit(backButton, (10, 25))
        if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if soundState: mouseClickSound.play()
                global currentScreen
                currentScreen = "menuScreen"
                return

        loginText=pygame.image.load("graphics/fonts/login.png")
        screen.blit(loginText,(497, 15))
        screen.blit(ssfont.render("Username:", True, (255, 255, 255)), (250, 200))
        screen.blit(ssfont.render("Password:", True, (255, 255, 255)), (250, 300))

        for field, rect in inputBoxes.items():
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=5)
            if field == "username":
                textToShow = username
            else:
                textToShow = "*" * len(password)
            screen.blit(ssfont.render(textToShow, True, (0, 0, 0)), (rect.x + 10, rect.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for field, rect in inputBoxes.items():
                    if rect.collidepoint(event.pos):
                        activeField = field
                if pygame.Rect(100, 30, 66, 54).collidepoint(pygame.mouse.get_pos()):
                    soundState = not soundState

            elif event.type == pygame.KEYDOWN:
                if activeField:
                    if event.key == pygame.K_BACKSPACE:
                        if activeField == "username":
                            username = username[:-1]
                        elif activeField == "password":
                            password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        result = loginUser(username, password)
                        if result == "Login successful!":
                            currentScreen = "levelSelection"
                            return
                        elif result == "Incorrect password.":
                            screen.blit(ssfont.render("Incorrect password", True, (255, 0, 0)), (450, 400))
                        elif result == "Username not found.":
                            screen.blit(ssfont.render("Username not found", True, (255, 0, 0)), (450, 400))
                    else:
                        if activeField == "username":
                            username += event.unicode
                        elif activeField == "password":
                            password += event.unicode
        pygame.display.update()

def leaderboard():
    drawBackground()
    soundButtonRect=drawSoundButton()
    if soundState:
        soundButtonRect = screen.blit(soundOn, (100, 30))
        if bgm.get_num_channels()==0:
            pygame.mixer.stop()
            bgm.play(-1)
    else:
        soundButtonRect = screen.blit(soundOff, (100, 30))
        bgm.stop()
    screen.blit(backButton, (10, 25))
    if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            if soundState: mouseClickSound.play()
            global currentScreen
            currentScreen = "menuScreen"
            return
        
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute("SELECT username, totalScore FROM users ORDER BY totalScore DESC LIMIT 10")
    highScores = cursor.fetchall()
    cursor.close()
    conn.close()

    highScoresTitle=pygame.image.load("graphics/fonts/highScoresTitle.png")
    screen.blit(highScoresTitle,(408, 15))
    usernameHeader = ssfont.render("Username", True, (255, 255, 255))
    scoreHeader = ssfont.render("Score", True, (255, 255, 255))
    screen.blit(usernameHeader, (330, 110))
    screen.blit(scoreHeader, (730, 110))

    yPos = 160
    rank = 1  
    for entry in highScores:
        username, score = entry  
        usernameText = ssfont.render(f"{rank}. {username}", True, (255, 255, 255))
        scoreText = ssfont.render(str(score), True, (255, 255, 255))
        screen.blit(usernameText, (350, yPos))
        screen.blit(scoreText, (750, yPos))
        yPos += 50  
        rank += 1
    return soundButtonRect

def controlScreen():
    global currentScreen, changingControl
    drawBackground()
    soundButtonRect=drawSoundButton()
    if soundState:
        soundButtonRect = screen.blit(soundOn, (100, 30))
        if bgm.get_num_channels()==0:
            pygame.mixer.stop()
            bgm.play(-1)
    else:
        soundButtonRect = screen.blit(soundOff, (100, 30))
        bgm.stop()
    screen.blit(backButton,(10, 25))
    if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
      if pygame.mouse.get_pressed()[0]:
          if soundState: mouseClickSound.play()
          global currentScreen
          currentScreen="menuScreen"
    yPos = 100
    for action, key in list(currentControls.items()):
        actionText = ssfont.render(f"{action}: ", True, (255, 255, 255))
        keyText = ssfont.render(key, True, (0, 0, 0))

        actionTextRect = actionText.get_rect(center=(600, yPos))
        keyTextRect = keyText.get_rect(left=actionTextRect.right + 10, top=actionTextRect.top)

        keyColor = (150, 150, 150)
        keyRect = pygame.Rect(keyTextRect.inflate(30, 10))

        if keyRect.collidepoint(pygame.mouse.get_pos()):
            keyColor = (255, 255, 255)
            if pygame.mouse.get_pressed()[0]:
                if soundState and mouseClickSound.get_num_channels()==0: mouseClickSound.play()
                changingControl = action
                displayText = ssfont.render("Press a valid key to assign", True, (255, 255, 255))
                displayTextRect = displayText.get_rect(center=(600, 30))
                screen.blit(displayText, displayTextRect)

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        newKey = pygame.key.name(event.key).upper()

                        if newKey in currentControls.values():
                            displayText = ssfont.render("Press a valid key to assign", True, (255, 0, 0))
                            screen.blit(displayText, displayTextRect)
                        else:
                            currentControls[changingControl] = newKey
                            key = newKey
                        break

        pygame.draw.rect(screen, keyColor, keyRect, border_radius=5)
        screen.blit(actionText, actionTextRect)
        screen.blit(keyText, keyTextRect)

        yPos += 75
    return soundButtonRect 

def levelSelectionScreen():
  global currentScreen, paused
  drawBackground()
  soundButtonRect = drawSoundButton()
  if soundState:
     soundButtonRect = screen.blit(soundOn, (100, 30))
     if bgm.get_num_channels()==0:
        pygame.mixer.stop()
        bgm.play(-1)
  else:
     soundButtonRect = screen.blit(soundOff, (100, 30))
     bgm.stop()
  screen.blit(backButton,(10, 25))
  if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
      if pygame.mouse.get_pressed()[0]:
          if soundState: mouseClickSound.play()
          global currentScreen
          currentScreen="menuScreen"
  
  lock=pygame.transform.scale(pygame.image.load("graphics/lock.png"), (133.3, 100))
 
 #Drawing level boxes on screen
  yPos = 150
  for level in levels:
      levelRect=pygame.Rect(150, yPos, 133.3, 100)
      if levelRect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and level['playable']:
          if level['level']==1 and currentScreen == "levelSelection":
              paused=False
              resetLevel()
              currentScreen="level1"
          if level['level']==2 and currentScreen == "levelSelection":
              paused=False
              resetLevel()
              currentScreen="level2"
          if level['level']==3 and currentScreen == "levelSelection":
              paused=False
              resetLevel()
              currentScreen="level3"
      if level['playable'] and levelRect.collidepoint(pygame.mouse.get_pos()):
        box_colour=(255, 255, 255)
        if level['level'] == 1:
            screen.blit(pygame.transform.scale(level1background, (600, 337)), (450, 181))
        elif level['level'] == 2:
            screen.blit(pygame.transform.scale(level2background, (600, 337)), (450, 181))
        elif level['level'] == 3:
            screen.blit(pygame.transform.scale(level3background, (600, 337)), (450, 181))
      else:
        box_colour=(150, 150, 150)

      pygame.draw.rect(screen, box_colour, levelRect, border_radius=10)

      textSurface = ssfont.render(str(level['level']), True, (0, 0, 0))
      textRect = textSurface.get_rect(center=levelRect.center)
      screen.blit(textSurface, textRect)

      if not level['playable']:
          screen.blit(lock, levelRect)

      yPos += 150

  return soundButtonRect

def level1Screen(levels):
    global levelStartTime, chestStartTime, victory, paused
    screen.blit(level1background, (0, 0))
    if soundState:
        if level1music.get_num_channels()==0:
            pygame.mixer.stop()
            level1music.play(-1)
    keys=pygame.key.get_pressed()
    player.update(keys, enemies) 
    player.draw(screen)
    drawPlayerBox(player.getHealth())

    for x in range(len(enemies)):
        enemies[x].speed=9 + x*2
        enemies[x].update(player.x, player.y, player.width, player.height)
        enemies[x].draw(screen)
        drawEnemyBox(enemies[x].getHealth(), y=120 + x*80)

    if not paused and player.health>0 and not victory:
     if pygame.time.get_ticks() - chestStartTime >= 10000:
         newChest = Chest(x=random.randint(72, 1128), y=0, player=player)
         chests.append(newChest) 
         chestStartTime = pygame.time.get_ticks()
    for chest in chests:
         chest.interact(pygame.Rect(player.x, player.y, player.width, player.height))
         chest.draw(screen)
         chest.update()

    if len(enemies) < 2 and not paused:
        if pygame.time.get_ticks() - levelStartTime >= 3000:
            enemies.append(Enemy(x=1199, y=675))
            levelStartTime=pygame.time.get_ticks()
    
    if all(enemy.getHealth() <= 0 for enemy in enemies):
        levels[1]['playable'] = True
        victoryScreen()
        victory=True
        
    if paused:
      pauseScreen()
      screen.blit(backButton,(10, 25))
      if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            global currentScreen
            currentScreen="levelSelection"
    if player.health<0:
        deathScreen()
        paused=False
    
def level2Screen(levels):
    global levelStartTime, chestStartTime, victory, paused
    screen.blit(level2background, (0, 0))
    if soundState:
        if level2music.get_num_channels()==0:
            pygame.mixer.stop()
            level2music.play(-1)
        
    keys = pygame.key.get_pressed()
    player.update(keys, enemies) 
    player.draw(screen)
    drawPlayerBox(player.getHealth())
    for x in range(len(enemies)):
        enemies[x].speed=7 + x*2
        enemies[x].update(player.x, player.y, player.width, player.height)
        enemies[x].draw(screen)
        drawEnemyBox(enemies[x].getHealth(), y=120 + x*80)

    if not paused and player.health>0 and not victory:
     if pygame.time.get_ticks() - chestStartTime >= 10000:
         newChest = Chest(x=random.randint(72, 1128), y=0, player=player)
         chests.append(newChest) 
         chestStartTime = pygame.time.get_ticks()
    for chest in chests:
         chest.interact(pygame.Rect(player.x, player.y, player.width, player.height))
         chest.draw(screen)
         chest.update()

    if len(enemies) < 4 and not paused:
        if pygame.time.get_ticks() - levelStartTime >= 3000:
            enemies.append(Enemy(x=1199, y=675))
            levelStartTime=pygame.time.get_ticks()
    
    if all(enemy.getHealth() <= 0 for enemy in enemies):
        levels[2]['playable'] = True
        victoryScreen()
        victory=True

    if paused:
      pauseScreen()
      screen.blit(backButton,(10, 25))
      if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            global currentScreen
            currentScreen="levelSelection"
    if player.health<0:
        deathScreen()
        paused=False

def level3Screen():
    global levelStartTime, chestStartTime, victory, paused
    screen.blit(level3background, (0, 0))
    if soundState:
        if level3music.get_num_channels()==0:
            pygame.mixer.stop()
            level3music.play(-1)    
    keys = pygame.key.get_pressed()
    player.update(keys, enemies) 
    player.draw(screen)
    drawPlayerBox(player.getHealth())
    for x in range(len(enemies)):
        enemies[x].speed=5 + x*2
        enemies[x].update(player.x, player.y, player.width, player.height)
        enemies[x].draw(screen)
        drawEnemyBox(enemies[x].getHealth(), y=120 + x*80)

    if not paused and player.health>0 and not victory:
     if pygame.time.get_ticks() - chestStartTime >= 10000:
         newChest = Chest(x=random.randint(72, 1128), y=0, player=player)
         chests.append(newChest) 
         chestStartTime = pygame.time.get_ticks()
    for chest in chests:
         chest.interact(pygame.Rect(player.x, player.y, player.width, player.height))
         chest.draw(screen)
         chest.update()

    if len(enemies) < 6 and not paused:
        if pygame.time.get_ticks() - levelStartTime >= 3000:
            enemies.append(Enemy(x=1199, y=675))
            levelStartTime=pygame.time.get_ticks()
    
    if all(enemy.getHealth() <= 0 for enemy in enemies):
        if not levels[2]['completed']:
            victory3Screen()
        else:
            victoryScreen()
        victory=True
    
    if paused:
      pauseScreen()
      screen.blit(backButton,(10, 25))
      if backButton.get_rect(topleft=(10, 25)).collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            global currentScreen
            currentScreen="levelSelection"
    if player.health<0:
        deathScreen()
        paused=False

while True: #Game loop
  for event in pygame.event.get():
      if event.type == pygame.QUIT: #Allows user to exit the game
          pygame.quit()
          exit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.key.key_code(currentControls['Pause/Resume']) and not victory:
            paused = not paused
      if event.type == pygame.MOUSEBUTTONDOWN:
          for item in menuItems:
              if item['text'] == 'New Game' and item['rect'].collidepoint(event.pos) and currentScreen=="menuScreen":
                if soundState: mouseClickSound.play()
                currentScreen="registerScreen"              
              if item['text'] == 'Controls' and item['rect'].collidepoint(event.pos) and currentScreen=="menuScreen":
                if soundState: mouseClickSound.play()
                currentScreen="controlScreen"
              if item['text'] == 'Continue' and item['rect'].collidepoint(event.pos) and currentScreen=="menuScreen":
                if soundState: mouseClickSound.play()
                currentScreen="loginScreen"
              if item['text'] == 'High Scores' and item['rect'].collidepoint(event.pos) and currentScreen=="menuScreen":
                if soundState: mouseClickSound.play()
                currentScreen="leaderboard"            
              if item['text'] == 'Quit Game' and item['rect'].collidepoint(event.pos):
                  if soundState: mouseClickSound.play()
                  pygame.quit() #Can quit by pressing 'Quit Game'
                  exit()
          soundButtonRect = menuScreen()
          if soundButtonRect.collidepoint(event.pos):  #Checks if the button was clicked
              soundState = not soundState  #Changes the state accordingly
  if currentScreen=="menuScreen":
    menuScreen() #Calls function
  elif currentScreen=="registerScreen":
    registerScreen()
  elif currentScreen=="controlScreen":
    controlScreen()
  elif currentScreen=="leaderboard":
    leaderboard()
  elif currentScreen=="loginScreen":
    loginScreen()
  elif currentScreen=="levelSelection":
    levelSelectionScreen()
  elif currentScreen=="level1":
    level1Screen(levels)
  elif currentScreen=="level2":
    level2Screen(levels)
  elif currentScreen=="level3":
    level3Screen()
  pygame.display.update() #Updates the screen for every frame
  clock.tick(60)