import tkinter as tk
import random

# --- Constants ---
GAME_WIDTH = 800
GAME_HEIGHT = 600
PLAYER_SPEED = 10
LASER_SPEED = 15
ENEMY_SPEED = 3
ENEMY_WAVE_SIZE = 5

class SpaceWavesGame:
    def __init__(self, master):
        self.master = master
        master.title("Tkinter Space Waves")
        
        # --- Canvas Setup ---
        self.canvas = tk.Canvas(master, width=GAME_WIDTH, height=GAME_HEIGHT, bg="black")
        self.canvas.pack()
        
        # --- Game State ---
        self.running = True
        self.score = 0
        self.health = 3
        self.wave_count = 1
        
        # --- Game Objects Lists ---
        self.enemies = []
        self.lasers = []

        # --- Player Setup ---
        self.player_x = GAME_WIDTH // 2
        self.player_y = GAME_HEIGHT - 50
        self.player_size = 20
        # Player is a triangle (a basic spaceship)
        self.player = self.canvas.create_polygon(
            self.player_x, self.player_y - self.player_size, 
            self.player_x - self.player_size, self.player_y + self.player_size, 
            self.player_x + self.player_size, self.player_y + self.player_size, 
            fill="cyan"
        )
        
        # --- UI Elements ---
        self.score_text = self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=('Arial', 16))
        self.health_text = self.canvas.create_text(GAME_WIDTH - 50, 20, text=f"Health: {self.health}", fill="red", font=('Arial', 16))
        self.wave_text = self.canvas.create_text(GAME_WIDTH / 2, 20, text=f"Wave {self.wave_count}", fill="yellow", font=('Arial', 16))

        # --- Input Bindings (Keys for continuous movement) ---
        self.keys_held = {}
        master.bind('<KeyPress>', self._key_press)
        master.bind('<KeyRelease>', self._key_release)
        master.bind('<space>', lambda event: self.fire_laser())
        
        # --- Start Game ---
        self.spawn_wave()
        self.game_loop()

    def _key_press(self, event):
        self.keys_held[event.keysym] = True

    def _key_release(self, event):
        self.keys_held[event.keysym] = False
        
    # ----------------------------------------------------------------------
    # --- Player Functions ---
    # ----------------------------------------------------------------------

    def update_player_position(self):
        """Moves the player based on currently held keys."""
        dx, dy = 0, 0
        if self.keys_held.get('Left') or self.keys_held.get('a'):
            dx = -PLAYER_SPEED
        if self.keys_held.get('Right') or self.keys_held.get('d'):
            dx = PLAYER_SPEED
        if self.keys_held.get('Up') or self.keys_held.get('w'):
            dy = -PLAYER_SPEED
        if self.keys_held.get('Down') or self.keys_held.get('s'):
            dy = PLAYER_SPEED
            
        coords = self.canvas.coords(self.player)
        
        # Check boundaries
        if (coords[0] + dx > 0 and coords[2] + dx < GAME_WIDTH and
            coords[1] + dy > 0 and coords[5] + dy < GAME_HEIGHT): # Check using the points
            
            self.canvas.move(self.player, dx, dy)
            self.player_x += dx
            self.player_y += dy

    def fire_laser(self):
        """Creates a new laser object originating from the player."""
        if not self.running:
            return

        # Laser starts just above the player's nose
        laser = self.canvas.create_rectangle(
            self.player_x - 3, self.player_y - self.player_size, 
            self.player_x + 3, self.player_y - self.player_size - 15, 
            fill="lime"
        )
        self.lasers.append(laser)

    # ----------------------------------------------------------------------
    # --- Enemy and Wave Functions ---
    # ----------------------------------------------------------------------

    def spawn_wave(self):
        """Generates a new wave of enemies."""
        for i in range(ENEMY_WAVE_SIZE * self.wave_count):
            x = random.randint(50, GAME_WIDTH - 50)
            y = random.randint(-GAME_HEIGHT, -50)  # Start above the screen
            size = random.randint(15, 25)
            
            enemy = self.canvas.create_oval(x, y, x + size, y + size, fill="red")
            self.enemies.append(enemy)

    def update_enemies(self):
        """Moves all enemies down and removes them if they exit the screen."""
        enemies_to_remove = []
        for enemy in self.enemies:
            self.canvas.move(enemy, 0, ENEMY_SPEED)
            
            # Check if enemy hits player's bottom boundary
            if self.canvas.coords(enemy)[3] > self.player_y + self.player_size:
                enemies_to_remove.append(enemy)
                self.take_damage(1) # Player takes damage
        
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.canvas.delete(enemy)
                self.enemies.remove(enemy)

    # ----------------------------------------------------------------------
    # --- Physics & Collision ---
    # ----------------------------------------------------------------------

    def check_collisions(self):
        """Checks for laser-enemy and enemy-player collisions."""
        lasers_to_remove = []
        
        for laser in self.lasers:
            self.canvas.move(laser, 0, -LASER_SPEED)
            laser_coords = self.canvas.coords(laser)
            
            if laser_coords[1] < 0: # Laser went off screen
                lasers_to_remove.append(laser)
                continue
                
            hit_enemies = self.canvas.find_overlapping(*laser_coords)
            enemies_to_remove = []

            for item_id in hit_enemies:
                if item_id != self.player and item_id in self.enemies:
                    # Enemy hit by laser
                    enemies_to_remove.append(item_id)
                    lasers_to_remove.append(laser)
                    self.update_score(10)
                    break # Laser hits only one enemy

            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.canvas.delete(enemy)
                    self.enemies.remove(enemy)

        for laser in lasers_to_remove:
            if laser in self.lasers:
                self.canvas.delete(laser)
                self.lasers.remove(laser)
                
    # ----------------------------------------------------------------------
    # --- UI and Game Flow ---
    # ----------------------------------------------------------------------
    
    def update_score(self, points):
        """Updates the player's score."""
        self.score += points
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def take_damage(self, amount):
        """Reduces player health."""
        self.health -= amount
        self.canvas.itemconfig(self.health_text, text=f"Health: {self.health}")
        
        if self.health <= 0:
            self.game_over()
            
    def check_wave_status(self):
        """Checks if all enemies are defeated and spawns the next wave."""
        if not self.enemies:
            self.wave_count += 1
            self.canvas.itemconfig(self.wave_text, text=f"Wave {self.wave_count}")
            # Increase difficulty slightly each wave
            global ENEMY_SPEED 
            ENEMY_SPEED += 0.5
            self.spawn_wave()

    def game_over(self):
        """Ends the game and displays the final score."""
        self.running = False
        self.canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2, 
            text=f"GAME OVER\nFinal Score: {self.score}", 
            fill="red", font=('Arial', 40)
        )
        
    def game_loop(self):
        """The main update loop."""
        if self.running:
            self.update_player_position()
            self.update_enemies()
            self.check_collisions()
            self.check_wave_status()
            
        # The core of Tkinter game loop: schedule the next call
        self.master.after(30, self.game_loop) # 30ms delay ~= 33 FPS

# --- Run the Game ---
if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceWavesGame(root)
    root.mainloop()