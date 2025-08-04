"""
Lab11_bryandiaz.py
Spaceship Repositioning Game
Author: Bryan Diaz Revilla
Purpose: Modify the spaceship game to position ship on left/right border facing center with up/down movement
Date: 7/19/25
"""

import sys
import pygame
from pygame.sprite import Sprite, Group
from time import sleep
import pygame.font

class Button:
    def __init__(self, ai_game, msg, width=200, height=50, button_color=(0, 255, 0), text_color=(255, 255, 255)):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set dimensions and properties of the button.
        self.width = width
        self.height = height
        self.button_color = button_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 48)

        # Build the button's rect object and center it.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # The button message needs to be prepped only once.
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turn msg into a rendered image and center text on the button."""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        # Draw blank button and then draw message.
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

class Settings:
    """A class to store all game settings."""
    
    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        
        # Ship settings
        self.ship_speed = 1.0
        self.ship_limit = 3
        
        # Bullet settings
        self.bullet_speed = 3.0
        self.bullet_width = 20
        self.bullet_height = 50
        self.bullet_color = (255, 0, 0)
        self.bullets_allowed = 3
        
        # Alien settings
        self.alien_speed = 0.4
        self.fleet_drop_speed = 5
        # fleet_direction of 1 represents down; -1 represents up
        self.fleet_direction = 1
        
        # How quickly the game speeds up
        self.speedup_scale = 1.1
        
        # How quickly the alien point values increase
        self.score_scale = 1.5
        
        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.0
        self.bullet_speed = 3.0
        self.alien_speed = 0.5
        
        # fleet_direction of 1 represents down; -1 represents up
        self.fleet_direction = 1
        
        # Scoring
        self.alien_points = 50
    
    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        
        self.alien_points = int(self.alien_points * self.score_scale)

class Ship(Sprite):
    """A class to manage the ship."""
    
    def __init__(self, ai_game, position='right'):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        
        # Load the ship image and scale it smaller
        original_image = pygame.image.load('2ndchip.png')
        
        # For example, scale to 50% of original size
        scale_factor = 0.15
    
        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        
        self.image = pygame.transform.smoothscale(original_image, (new_width, new_height))
        self.rect = self.image.get_rect()
        
        # Rest of your code unchanged...
        self.position = position
        if position == 'left':
            self.rect.midleft = self.screen_rect.midleft
        else:
            self.rect.midright = self.screen_rect.midright
            self.image = pygame.transform.rotate(self.image, 90)
        
        self.y = float(self.rect.y)
        self.moving_up = False
        self.moving_down = False

    
    def update(self):
        """Update the ship's position based on movement flags."""
        # Update the ship's y value, not the x.
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed
            
        # Update rect object from self.y
        self.rect.y = self.y
    
    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
    
    def center_ship(self):
        """Center the ship on the left or right side of the screen."""
        if self.position == 'left':
            self.rect.midleft = self.screen_rect.midleft
        else:
            self.rect.midright = self.screen_rect.midright
        self.y = float(self.rect.y)

class Bullet(Sprite):
    """A class to manage bullets fired from the ship."""
    
    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.ship = ai_game.ship
        
        # Load the laser image
        original_image = pygame.image.load('2ndlazer.png')
        scale_factor = 0.1
        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        self.image = pygame.transform.smoothscale(original_image, (new_width, new_height))
        
        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = self.image.get_rect()
        
        # Set bullet position based on ship position
        if self.ship.position == 'left':
            self.rect.midleft = self.ship.rect.midright
        else:  # right position
            self.rect.midright = self.ship.rect.midleft
        
        # Store the bullet's position as a decimal value.
        self.x = float(self.rect.x)
    
    def update(self):
        """Move the bullet across the screen."""
        # Update the decimal position of the bullet.
        if self.ship.position == 'left':
            self.x += self.settings.bullet_speed
        else:  # right position
            self.x -= self.settings.bullet_speed
            
        # Update the rect position.
        self.rect.x = self.x
    
    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect)

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""
    
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        original_image = pygame.image.load('2ndALIENship.png')
        scale_factor = 0.03
        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        self.image = pygame.transform.smoothscale(original_image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.y = float(self.rect.y)

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.bottom >= screen_rect.bottom or self.rect.top <= 0:
            return True
    
    def update(self):
        """Move the alien up or down."""
        self.y += (self.settings.alien_speed *
                   self.settings.fleet_direction)
        self.rect.y = self.y

class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        
        # Start Alien Invasion in an inactive state.
        self.game_active = False
    
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        self.high_score = 0

class Scoreboard:
    """A class to report scoring information."""
    
    def __init__(self, ai_game):
        """Initialize scorekeeping attributes."""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        
        # Font settings for scoring information.
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        
        # Prepare the initial score images.
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()
    
    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True,
                self.text_color, self.settings.bg_color)
        
        # Display the score at the top right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20
    
    def prep_high_score(self):
        """Turn the high score into a rendered image."""
        high_score = round(self.stats.high_score, -1)
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True,
                self.text_color, self.settings.bg_color)
        
        # Center the high score at the top of the screen.
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top
    
    def prep_level(self):
        """Turn the level into a rendered image."""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True,
                self.text_color, self.settings.bg_color)
        
        # Position the level below the score.
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10
    
    def prep_ships(self):
        """Show how many ships are left."""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)
    
    def check_high_score(self):
        """Check to see if there's a new high score."""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()
    
    def show_score(self):
        """Draw scores, level, and ships to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

class AlienInvasion:
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer for audio
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self, position='right')
        self.bullets = Group()
        self.aliens = Group()

        # Create the Play button
        self.play_button = Button(self, "Play")

        # Font for lives display
        self.font = pygame.font.SysFont(None, 36)
        
        # Load and play background music
        try:
            pygame.mixer.music.load('234126__zagi2__chord-bassline-loop.wav')
            pygame.mixer.music.set_volume(0.3)  # Set background music volume to 30%
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except:
            print("Could not load background music")
        
        # Load laser sound effect
        try:
            self.laser_sound = pygame.mixer.Sound('Assets/sound/laser.mp3')
            self.laser_sound.set_volume(0.5)  # Set laser sound volume to 50%
        except:
            print("Could not load laser sound effect")
            self.laser_sound = None

    
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
    
    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            
            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)
            
            # Small delay to give player time to react
            sleep(0.5)
    
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            sys.exit()
    
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            # Play laser sound effect
            if hasattr(self, 'laser_sound') and self.laser_sound:
                self.laser_sound.play()
    
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.right <= 0 or bullet.rect.left >= self.settings.screen_width:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()
    
    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
    
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause for 2 seconds to reset positions.
            sleep(2.0)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
    
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Don't end the game, just let them continue their pattern
                break
    
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # We want exactly 30 aliens
        total_aliens = 30
        
        # Calculate how many aliens fit in a row
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # If we can't fit enough in a row, adjust spacing
        if number_aliens_x < 6:
            number_aliens_x = 6
            spacing = available_space_x // (number_aliens_x - 1)
        else:
            spacing = 2 * alien_width
        
        # Calculate number of rows needed to get exactly 30 aliens
        number_rows = (total_aliens + number_aliens_x - 1) // number_aliens_x
        
        # Create exactly 30 aliens
        alien_count = 0
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                if alien_count < total_aliens:
                    self._create_alien(alien_number, row_number, spacing)
                    alien_count += 1
    
    def _create_alien(self, alien_number, row_number, spacing):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        # Start aliens from the left side of the screen
        alien.rect.x = 50 + spacing * alien_number
        # Start aliens higher up and with more spacing from top
        alien.rect.y = 100 + 2 * alien.rect.height * row_number
        alien.y = float(alien.rect.y)
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Move the entire fleet right and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.x += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()