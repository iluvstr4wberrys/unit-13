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

class Settings:
    """A class to store all game settings."""
    
    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        
        # Ship settings
        self.ship_speed = 1.5
        self.ship_limit = 3
        
        # Bullet settings
        self.bullet_speed = 2.0
        self.bullet_width = 15
        self.bullet_height = 3
        self.bullet_color = (255, 0, 0)
        self.bullets_allowed = 3
        
        # Alien settings
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # fleet_direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

class Ship(Sprite):
    """A class to manage the ship."""
    
    def __init__(self, ai_game, position='right'):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        
        # Load the ship image and get its rect.
        self.image = pygame.image.load('ship.png')
        self.rect = self.image.get_rect()
        
        # Start each new ship at the left or right center of the screen.
        self.position = position
        if position == 'left':
            self.rect.midleft = self.screen_rect.midleft
            # No need to rotate for left position as it faces right by default
        else:  # right position
            self.rect.midright = self.screen_rect.midright
            # Rotate the image 180 degrees to face left
            self.image = pygame.transform.rotate(self.image, 180)
        
        # Store a decimal value for the ship's vertical position.
        self.y = float(self.rect.y)
        
        # Movement flags
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
        
        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        
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
        pygame.draw.rect(self.screen, self.settings.bullet_color, self.rect)

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""
    
    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        
        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('alien.png')
        self.rect = self.image.get_rect()
        
        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        
        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)
    
    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
    
    def update(self):
        """Move the alien right or left."""
        self.x += (self.settings.alien_speed *
                   self.settings.fleet_direction)
        self.rect.x = self.x

class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        
        # Start Alien Invasion in an active state.
        self.game_active = True
    
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        
        # Create an instance to store game statistics.
        self.stats = GameStats(self)
        
        # Set ship position (can be 'left' or 'right')
        self.ship = Ship(self, position='right')
        self.bullets = Group()
        self.aliens = Group()
        
        self._create_fleet()
    
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
        
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
    
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
            # Decrement ships_left.
            self.stats.ships_left -= 1
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
    
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
    
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                                (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()