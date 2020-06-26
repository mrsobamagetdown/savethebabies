import pygame
import math
import random



def debug(do=True):
	#print(game.frames)
	pass
	

def roundto(x, base):
	return base*round(float(x)/base)
	

def aspect_scale(img, size):
	""" Scales 'img' to fit into box bx/by.
	This method will retain the original image's aspect ratio """
	if type(size) == tuple or type(size) == list:
		bx = round(size[0])
		by = round(size[1])
	else:
		bx = round(size)
		by = round(size)
	# http://www.pygame.org/pcr/transform_scale/
	
	ix,iy = img.get_size()
	if ix > iy:
		# fit to width
		scale_factor = bx/float(ix)
		sy = scale_factor * iy
		if sy > by:
			scale_factor = by/float(iy)
			sx = scale_factor * ix
			sy = by
		else:
			sx = bx
	else:
		# fit to height
		scale_factor = by/float(iy)
		sx = scale_factor * ix
		if sx < bx:
			scale_factor = bx/float(ix)
			sx = bx
			sy = scale_factor * iy
		else:
			sy = by

	return pygame.transform.scale(img, (round(sx), round(sy)))
	

def restrict(value, minvalue, maxvalue):
	return max(minvalue, min(value, maxvalue))
	

def loadImage(image, size):
	image = pygame.image.load(image).convert_alpha()
	image = aspect_scale(image, size)
	return image
	

def fillImage(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b, a = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))
	

def getRect(instance):
	x = round(instance.x)
	y = round(instance.y)
	width = round(instance.width)
	height = round(instance.height)
	
	rect = pygame.Rect(x, y, width, height)
	
	return rect
	

def getImageRect(image):
	width = image.get_width()
	height = image.get_height()
	return width, height
	




class Game:
	
	def __init__(self):
		pygame.init()
		self.defaultwidth = 1000
		self.defaultheight = 750
		self.screen = pygame.display.set_mode((self.defaultwidth, self.defaultheight))
		pygame.display.set_caption("Look after them for a while!")
		self.color = (25, 175, 100)
		
		self.running = True
		self.events = None
		pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
		self.keys = None
		self.MOUSECLICKED = False
		self.MOUSEPRESSED = False
		self.KEYTAPPED = False
		self.KEYPRESSED = False
		self.LEFT = 0
		self.RIGHT = 2
		self.MIDDLE = 1
		self.dragging = False
		
		self.seconds = 0
		self.minutes = 0

		self.hacking = False
		self.command = ''
		self.docheats = True
		
		self.spawners = []
		self.babies = []
		self.deadbabies = []
		self.enemies = []
		
		self.level = 0
		self.won = False
		self.lost = False
		self.deceased = []
		
		self.pg = False
		
		self.theme = 0
		
	
	def setup(self):
		self.babies.clear()
		self.enemies.clear()
		
		size = Baby.size
		
		baby1 = Baby(size, 'baby1.png', 1.5)
		baby2 = Baby(size, 'baby2.png', 1.25, randomness=10)
		baby3 = Baby(size, 'baby3.png', 3, randomness=20)
		
		creeper = Baby(size, 'creeper.png', 2, randomness=30, spawner=chest)
		
		doggo = Baby(size, 'doggo.png', 5, randomness=40, spawner=doghouse)
		doggo2 = Baby(size, 'doggo2.png', 5, randomness=50, spawner=doghouse)
		tabby = Baby(size, 'tabby.png', 3.5, canpause=True, randomness=50, spawner=catbed)
		tabby2 = Baby(size*2, 'tabby2.png', 6, canpause = True, randomness=100, spawner=catbed)
		
		
		size *= 1.5
		
		paulbro = Enemy(size, 'paulbro.png')
		ninja = Enemy(size, 'ninja.png')
		
		bike = Enemy(size*1.5, 'bike.png')
		knife = Enemy(size*0.75, 'sword.png', flip=True)
		
		shark = Enemy(size*2, 'shark.png')
		lion = Enemy(size, 'lion.png')
		
		rock = Enemy(size*0.65, 'kawaiistone.png')
		volcano = Enemy(size*1.5, 'volcano.png')
		
		#bandage = Enemy(size*0.75, 'bandage.png', 1, timer=500)
		#firstaid = Enemy(size*0.75, 'firstaid.png', 2, timer=1000)
		# = Enemy(size*0.75, '', 0, timer=500, flip=True)
		
		
		
		self.frames = 0
		self.level = 0
		
	
	def play(self):
		self.loop()
		self.draw()
		
	
	def draw(self):
		self.screen.fill(self.color)
		
		for spawner in self.spawners:
			spawner.draw()
			
		for baby in self.babies:
			if baby.shown:
				baby.draw()
			
		for enemy in reversed(self.enemies):
			if enemy.shown:
				enemy.draw()
				
		pygame.display.flip()
		
	
	def loop(self):
		self.checkEvents()
		
		if not self.lost:
			for spawner in self.spawners:
				spawner.loop()
			
			for enemy in self.enemies:
				enemy.loop()
				
			for baby in self.babies:
				if baby.shown:
					baby.loop()
				
		self.resetInput()
		self.frames += 1
		
	
	def checkEvents(self):
		self.events = pygame.event.get()
		self.keys = pygame.key.get_pressed()
		self.mouse = pygame.mouse.get_pressed()
		self.mouseX = pygame.mouse.get_pos()[0]
		self.mouseY = pygame.mouse.get_pos()[1]
		
		for event in self.events:
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				#print(pygame.mouse.get_pos())
				self.MOUSECLICKED = True
				self.MOUSEPRESSED = True
			elif event.type == pygame.MOUSEBUTTONUP:
				self.MOUSEPRESSED = False
			elif event.type == pygame.KEYDOWN:
				self.KEYTAPPED = True
				self.KEYPRESSED = True
				self.checkKeys()
		
	
	def resetInput(self):
		self.MOUSECLICKED = False
		self.KEYTAPPED = False
		
	
	def checkKeys(self):
		if self.keys[pygame.K_ESCAPE]:
			pygame.display.iconify()
		if self.keys[pygame.K_r]:
			self.setup()
			
		if self.keys[pygame.K_LCTRL] or self.keys[pygame.K_RCTRL]:
			if self.keys[pygame.K_r]:
				self.setup()
			if self.keys[pygame.K_k]:
				self.hacking = not self.hacking
			if self.keys[pygame.K_g]:
				self.pg = not self.pg
			if self.keys[pygame.K_e]:
				Spawner.interval = Spawner.easy
			if self.keys[pygame.K_m]:
				Spawner.interval = Spawner.medium
			if self.keys[pygame.K_h]:
				Spawner.interval = Spawner.hard
			if self.keys[pygame.K_i]:
				Spawner.interval = Spawner.insane
		
	
	def get_size(self):
		return pygame.display.get_surface().get_size()
	
	
	def get_width(self):
		return self.get_size()[0]
		
	
	def get_height(self):
		return self.get_size()[1]
	
	def randX(self):
		x = random.randint(startX, game.get_width())
		return x
		
	def randY(self):
		y = random.randint(startY, game.get_height())
		return y
	

game = Game()




class Spawner:
	
	startx = 25
	x = startx
	y = 25
	
	startdelay = 200
	
	easy = 400
	medium = 300
	hard = 200
	insane = 100
	interval = medium
	
	warningdelay = 50
	
	def __init__(self, size, image1, image2=None):
		game.spawners.append(self)
		self.image1 = loadImage(image1, size)
		if image2:
			self.image2 = loadImage(image2, size)
		else:
			self.image2 = None
		self.image = self.image1
		
		self.width = getImageRect(self.image)[0]
		self.height = getImageRect(self.image)[1]
		self.x = Spawner.x
		Spawner.x += size*1.25
		if self.x + self.width > game.get_width():
			Spawner.y += self.height*1.5
			Spawner.x = Spawner.startx
		self.y = Spawner.y
		
	
	def draw(self):
		if self.image2:
			self.changeImage()
		game.screen.blit(self.image, self.rect)
		
	
	def changeImage(self):
		if game.frames > ((Spawner.interval)*game.level)-Spawner.warningdelay+Spawner.startdelay and game.level < len(game.babies) and game.babies[game.level].spawner == self:
			self.image = self.image2
		else:
			self.image = self.image1
		
	
	def loop(self):
		self.rect = getRect(self)
		if not game.lost:
			self.spawn()
		
	
	def spawn(self):
		if game.frames > (Spawner.interval*game.level)+Spawner.startdelay and game.level < len(game.babies):
			game.babies[game.level].shown = True
			game.level += 1
	

furnace = Spawner(100, 'furnace.png', 'furnace_active.png')
chest = Spawner(100, 'chest.png', 'chest_open.png')
doghouse = Spawner(100, 'doghouse.png', 'doghouse_eyes.png')
catbed = Spawner (100, 'bed.png', 'bed_empty.png')




class Baby:
	
	size = 65
		
	heart = loadImage('pacifier.png', size/4)
	skeleton = loadImage('skeleton.png', size)
	ghost = loadImage('ghost.png', size)


	def __init__(self, size, image, speed, randomness=0, spawner=game.spawners[0], canpause=False, turnrange=(-1, 1), health=5, boss=False):
		game.babies.append(self)
		self.spawner = spawner
		self.image = loadImage(image, size)
		self.width = getImageRect(self.image)[0]
		self.height = getImageRect(self.image)[1]
		self.x = self.spawner.x + (spawner.width/2) - (self.width/2)
		self.y = self.spawner.y + (spawner.height/2) - (self.height/2)
		self.health = health
		self.maxhealth = health
		self.speed = speed
		self.distance = 0
		self.shown = False
		self.living = True
		self.randomness = randomness
		self.canpause = canpause
		self.turnrange = turnrange
		self.touching = set([])
		self.frames = 0
		self.boss = boss
		if self.boss:
			self.aura = loadImage('aura.png', (size))
			color = pygame.Color(255, 0, 0)
			fillImage(self.aura, color)
			
		self.bloodspot = loadImage('bloodspot.png', size)	
		self.bloodpool = loadImage('bloodpool.png', size*1.5)
		
		self.slopeX = self.get_random_slope()
		self.slopeY = self.get_random_slope()
		
	
	def draw(self):
		if not self.living:
			self.drawDeath()
		else:
			if self.boss:
				game.screen.blit(self.aura, self.rect)
			game.screen.blit(self.image, self.rect)
			self.healthIndicator()
		
	
	def drawDeath(self):
		if game.pg:
			game.screen.blit(Baby.ghost, self.rect)
		else:
			bloodpool = pygame.transform.rotate(self.bloodpool, self.angle)
			game.screen.blit(bloodpool, self.rect.move(-bloodpool.get_width()*0.175, -bloodpool.get_width()*0.175))
		
	
	def healthIndicator(self):
		if game.pg:
			for i in range(self.health-1):
				width = self.width/5
				height = width
				x = self.x + (width*i)+(width/4)
				y = self.y - (self.height/2)-height
					
				rect = pygame.Rect(x, y+(height*2), height, width)
				game.screen.blit(Baby.heart, rect)
				
		else:
			marks = (self.maxhealth-self.health)/self.maxhealth
			print(marks)
			angle = 0
			for i in range(int(marks*5)):#(self.maxhealth - self.health)):
				image = pygame.transform.rotate(self.bloodspot, angle)
				game.screen.blit(image, self.rect)
				angle -= 90
		
	
	def loop(self):
		self.frames += 1
		self.rect = getRect(self)
		if self.frames > 0:
			self.collision()
		self.checkHealth()
		if self.living:
			self.move()
		elif game.pg: # Floats up if image is ghost
			self.y -= 3
		
	
	def move(self):
		speed = self.speed
		for baby in game.deceased:
			if baby in self.touching:
				speed *= 0.75
		
		self.x += self.slopeX * speed
		self.y += self.slopeY * speed
		
		self.x = restrict(self.x, 0, game.get_width()-self.width)
		self.y = restrict(self.y, 0, game.get_height()-self.height)
		
		innerrect = game.screen.get_rect().inflate(-(self.size*2)-1, -(self.size*2)-1)
		if not self.rect.colliderect(innerrect) or random.randint(0, 1000) < self.randomness:
			# Turns around when x or y is closer than half of baby's width or height to the edge of the screen
			self.slopeX = self.get_random_slope()
			self.slopeY = self.get_random_slope()
		
	
	def get_random_slope(self):
		num = 0
		if not self.canpause:
			while num == 0: # Skips over 0, which makes the baby pause, unless canpause == True
				num = random.randint(self.turnrange[0], self.turnrange[1])
		if self.canpause:
			num = random.randint(self.turnrange[0], self.turnrange[1])
		return num
		
	
	def checkHealth(self):
		self.health = restrict(self.health, 0, self.maxhealth)
		if self.health <= 0 and self.living:
			self.living = False
			game.deceased.append(self)
			game.babies.insert(0, game.babies.pop(game.babies.index(self)))
			self.angle = random.choice((0, 90, 180, 270))
	
	
	def collision(self):
		for baby in game.babies:
			if baby.frames > 0:
				if self.rect.colliderect(baby.rect):
					self.touching.add(baby)
				else:
					self.touching.discard(baby)
				
		for enemy in game.enemies:
			if self.rect.colliderect(enemy.rect):
				if not enemy in self.touching or enemy.damage >= 0:
					if (enemy.damage > 0 and self.health > 0 and self.health < self.maxhealth) or enemy.damage <= 0:
						self.health += enemy.damage
						if enemy.disappear:
							enemy.shown = False
							enemy.setRandPos()
						if enemy.flip:
							self.slopeX *= -1
							self.slopeY *= -1
					self.touching.add(enemy)
			else:
				self.touching.discard(enemy)
	



class Enemy:
	
	def __init__(self, size, image, damage=-1, timer=0, flip=False):
		self.image = loadImage(image, size)
		game.enemies.append(self)
		self.width = getImageRect(self.image)[0]
		self.height = getImageRect(self.image)[1]
		self.setRandPos()
				
		self.damage = damage
		self.item = damage >= 0
		self.timer = timer
		if self.timer > 0:
			self.disappear = True
		else:
			self.disappear = False
		if not self.disappear:
			self.shown = True
		else:
			self.shown = False
		
		self.flip = flip
		if self.item:
			self.aura = loadImage('aura.png', (size))
			if self.damage > 0:
				color = pygame.Color(0, 255, 0)
				fillImage(self.aura, color)
				
	
	def draw(self):
		if self.item:
			game.screen.blit(self.aura, self.rect)#.move(self.width/, self.height))
		game.screen.blit(self.image, self.rect)
		
	
	def loop(self):
		#self.rect = pygame.Rect(round(self.x), round(self.y), self.width, self.height)
		self.rect = getRect(self)
		if self.shown:
			self.drag()
		self.x = restrict(self.x, 0, game.get_width()-self.width)
		self.y = restrict(self.y, 0, game.get_height()-self.height)
		
		if self.disappear and game.frames % self.timer == 0 and game.frames > 0:
			self.shown = True
			self.bringToFront()
		
	
	def setRandPos(self):
		self.x = random.randint(round(self.width/2), round(game.get_width()-(self.width/2)))
		self.y = random.randint(round(self.height/2)+150, round(game.get_height()-(self.height/2)))
	
	
	def drag(self):
		if game.MOUSECLICKED and self.rect.collidepoint(pygame.mouse.get_pos()) and not game.dragging:
			game.dragging = self
		if not game.MOUSEPRESSED:
			game.dragging = None
		if game.dragging == self:
			self.x = game.mouseX-self.width/2
			self.y = game.mouseY-self.height/2
			self.bringToFront()
	
	def bringToFront(self):
		game.enemies.insert(0, game.enemies.pop(game.enemies.index(self)))
	



game.setup()
while game.running:
	game.play()
	debug()
