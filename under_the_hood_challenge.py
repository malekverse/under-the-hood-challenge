import pygame
import sys
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
HIGHLIGHT_COLOR = (255, 165, 0)  # Orange highlight for hover

# Game states
GAME_PLAYING = 0
GAME_WON = 1
GAME_LOST = 2


class UnderTheHoodGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Under the Hood Challenge")
        self.clock = pygame.time.Clock()
        # Use bold fonts for better readability
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)
        self.large_font = pygame.font.SysFont('Arial', 36, bold=True)

        # Load game assets
        try:
            self.engine_image = pygame.image.load("car_engine.png")
            # Scale image to fit screen if needed
            img_ratio = self.engine_image.get_width() / self.engine_image.get_height()
            img_width = min(SCREEN_WIDTH, 700)
            img_height = int(img_width / img_ratio)
            self.engine_image = pygame.transform.scale(self.engine_image, (img_width, img_height))
        except pygame.error:
            print("Warning: Could not load car_engine.png")
            # Create a placeholder image
            self.engine_image = pygame.Surface((700, 400))
            self.engine_image.fill(GRAY)

        # Load sound effects (optional)
        try:
            self.correct_sound = pygame.mixer.Sound("correct.wav")
            self.wrong_sound = pygame.mixer.Sound("wrong.wav")
            self.win_sound = pygame.mixer.Sound("win.wav")
            self.lose_sound = pygame.mixer.Sound("lose.wav")
            self.sounds_loaded = True
        except:
            self.sounds_loaded = False
            print("Warning: Sound files not found. Continuing without sound.")

        # Define component regions (x, y, width, height)
        # These coordinates are matched to the actual components in the image
        self.components = {
            'A': {'rect': pygame.Rect(130, 155, 60, 60), 'name': 'Windshield Washer Reservoir'},
            'B': {'rect': pygame.Rect(30, 320, 60, 60), 'name': 'Brake Fluid Reservoir'},
            'C': {'rect': pygame.Rect(105, 380, 60, 60), 'name': 'Oil Dipstick'},
            'D': {'rect': pygame.Rect(255, 150, 60, 60), 'name': 'Oil Cap'},
            'E': {'rect': pygame.Rect(410, 120, 60, 60), 'name': 'Coolant Reservoir'},
            'F': {'rect': pygame.Rect(580, 150, 60, 60), 'name': 'Battery'}
        }

        # Game state variables
        self.game_state = GAME_PLAYING
        self.current_question = None
        self.correct_answers = 0
        self.total_questions = 0
        self.max_questions = 6
        self.feedback_text = "Identify the car components!"
        self.feedback_color = BLACK
        self.hovered_component = None
        self.popup = None
        self.popup_timer = 0

        # Add difficulty levels
        self.difficulty = "normal"  # Options: "easy", "normal", "hard"
        self.time_per_question = 10  # Seconds per question (only used in hard mode)
        self.question_timer = 0
        self.show_labels = True  # Whether to show A-F labels (hidden in hard mode)

        # Generate a list of components to ask about
        self.component_queue = list(self.components.keys())
        random.shuffle(self.component_queue)

        # Set the first question
        self.set_next_question()

    def set_next_question(self):
        if self.component_queue:
            self.current_question = self.component_queue.pop()
            component_name = self.components[self.current_question]['name']
            self.feedback_text = f"Click on: {component_name}"
            self.feedback_color = BLACK
        else:
            # All questions asked, evaluate the game result
            if self.correct_answers >= 4:  # Win condition
                self.game_state = GAME_WON
                self.feedback_text = "✅ You Win! Press R to play again."
                self.feedback_color = GREEN
                if self.sounds_loaded:
                    self.win_sound.play()
            else:  # Lose condition
                self.game_state = GAME_LOST
                self.feedback_text = f"❌ Try Again! Score: {self.correct_answers}/6. Press R to restart."
                self.feedback_color = RED
                if self.sounds_loaded:
                    self.lose_sound.play()

    def check_answer(self, selected_component):
        if self.game_state != GAME_PLAYING:
            return

        self.total_questions += 1
        component_name = self.components[selected_component]['name']

        if selected_component == self.current_question:
            self.correct_answers += 1
            self.feedback_text = f"Correct! That was the {component_name}."
            self.feedback_color = GREEN
            if self.sounds_loaded:
                self.correct_sound.play()
        else:
            self.feedback_text = f"Wrong! That was the {component_name}."
            self.feedback_color = RED
            if self.sounds_loaded:
                self.wrong_sound.play()

        # Set a timer for the popup with enhanced styling
        self.popup = {
            'component': selected_component,
            'position': self.components[selected_component]['rect'].center,
            'text': component_name,
            'correct': selected_component == self.current_question
        }
        self.popup_timer = 120  # frames to show popup (2 seconds at 60 FPS)

        # Wait a moment before setting the next question, shorter delay for better flow
        pygame.time.delay(800)
        self.set_next_question()

    def restart_game(self):
        self.game_state = GAME_PLAYING
        self.correct_answers = 0
        self.total_questions = 0
        self.feedback_text = "Identify the car components!"
        self.feedback_color = BLACK
        self.component_queue = list(self.components.keys())
        random.shuffle(self.component_queue)
        self.set_next_question()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Handle key presses
            elif event.type == KEYDOWN:
                if event.key == K_r and (self.game_state == GAME_WON or self.game_state == GAME_LOST):
                    self.restart_game()
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # Handle mouse events
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                if self.game_state == GAME_PLAYING:
                    mouse_pos = pygame.mouse.get_pos()
                    # Adjust mouse position to account for image position
                    image_x = (SCREEN_WIDTH - self.engine_image.get_width()) // 2
                    image_y = 80
                    adjusted_mouse_x = mouse_pos[0] - image_x
                    adjusted_mouse_y = mouse_pos[1] - image_y

                    # Only check for clicks if mouse is within image boundaries
                    if (0 <= adjusted_mouse_x < self.engine_image.get_width() and
                            0 <= adjusted_mouse_y < self.engine_image.get_height()):
                        for component, data in self.components.items():
                            if data['rect'].collidepoint(adjusted_mouse_x, adjusted_mouse_y):
                                self.check_answer(component)
                                break

    def update(self):
        # Update popup timer
        if self.popup_timer > 0:
            self.popup_timer -= 1
        else:
            self.popup = None

        # Update hovered component
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_component = None
        if self.game_state == GAME_PLAYING:
            # Adjust mouse position to account for image position
            image_x = (SCREEN_WIDTH - self.engine_image.get_width()) // 2
            image_y = 80
            adjusted_mouse_x = mouse_pos[0] - image_x
            adjusted_mouse_y = mouse_pos[1] - image_y

            # Only check for hover if mouse is within image boundaries
            if (0 <= adjusted_mouse_x < self.engine_image.get_width() and
                    0 <= adjusted_mouse_y < self.engine_image.get_height()):
                for component, data in self.components.items():
                    if data['rect'].collidepoint(adjusted_mouse_x, adjusted_mouse_y):
                        self.hovered_component = component
                        break

    def draw(self):
        self.screen.fill(WHITE)

        # Draw engine image
        # Position the image a bit higher to make room for components at the bottom
        image_x = (SCREEN_WIDTH - self.engine_image.get_width()) // 2
        image_y = 80
        self.screen.blit(self.engine_image, (image_x, image_y))

        # Draw component regions with labels
        for component, data in self.components.items():
            rect = data['rect'].move(image_x, image_y)  # Adjust rect position to match image position

            # Highlight the hovered component with a thicker, more visible border
            if component == self.hovered_component:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect, 4)
                # Draw a semi-transparent overlay to make it more visible
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill((255, 165, 0, 50))  # Semi-transparent orange
                self.screen.blit(overlay, rect)
            else:
                pygame.draw.rect(self.screen, BLUE, rect, 2)

            # Draw component label with a background for better visibility
            label = self.font.render(component, True, BLACK)
            label_rect = label.get_rect(center=rect.center)

            # Draw label background
            bg_rect = label_rect.inflate(10, 6)
            pygame.draw.rect(self.screen, WHITE, bg_rect)
            pygame.draw.rect(self.screen, BLACK, bg_rect, 1)

            self.screen.blit(label, label_rect)

        # Draw popup if active with enhanced styling
        if self.popup and self.popup_timer > 0:
            popup_color = GREEN if self.popup.get('correct', False) else RED
            text = self.font.render(self.popup['text'], True, BLACK)
            text_rect = text.get_rect(center=(
                image_x + self.popup['position'][0],
                image_y + self.popup['position'][1] - 40
            ))

            # Create a more attractive popup with rounded corners effect
            bg_rect = text_rect.inflate(40, 20)

            # Main background
            pygame.draw.rect(self.screen, WHITE, bg_rect)

            # Colored border based on correct/incorrect
            pygame.draw.rect(self.screen, popup_color, bg_rect, 3)

            # Top highlight to simulate 3D effect
            pygame.draw.line(self.screen, (240, 240, 240),
                             (bg_rect.left + 3, bg_rect.top + 3),
                             (bg_rect.right - 3, bg_rect.top + 3), 2)

            # Add a small icon for correct/incorrect
            icon_text = "✓" if self.popup.get('correct', False) else "✗"
            icon = self.font.render(icon_text, True, popup_color)
            self.screen.blit(icon, (bg_rect.left + 10, text_rect.top))

            # Center the text a bit more to the right to make room for the icon
            adjusted_text_rect = text_rect.move(10, 0)
            self.screen.blit(text, adjusted_text_rect)

        # Draw game stats and feedback with improved UI

        # Draw title with background
        title_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (240, 240, 240), title_bg)
        pygame.draw.line(self.screen, (200, 200, 200), (0, 60), (SCREEN_WIDTH, 60), 2)

        title_text = self.large_font.render("Under the Hood Challenge", True, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))

        # Draw current score with a nice box
        score_bg = pygame.Rect(20, 15, 100, 30)
        pygame.draw.rect(self.screen, WHITE, score_bg)
        pygame.draw.rect(self.screen, BLACK, score_bg, 2)
        score_text = self.font.render(f"Score: {self.correct_answers}/{self.total_questions}", True, BLACK)
        self.screen.blit(score_text, (23, 15))

        # Draw feedback text with background
        feedback_bg = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 70, SCREEN_WIDTH // 2, 40)
        pygame.draw.rect(self.screen, WHITE, feedback_bg)
        pygame.draw.rect(self.screen, self.feedback_color, feedback_bg, 2)
        feedback = self.font.render(self.feedback_text, True, self.feedback_color)
        feedback_rect = feedback.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(feedback, feedback_rect)

        # Draw game state-specific UI
        if self.game_state == GAME_WON:
            win_text = self.large_font.render("✅ You Win!", True, GREEN)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = self.font.render("Press R to play again", True, BLACK)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        elif self.game_state == GAME_LOST:
            lose_text = self.large_font.render("❌ Try Again!", True, RED)
            self.screen.blit(lose_text, (SCREEN_WIDTH // 2 - lose_text.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = self.font.render("Press R to restart", True, BLACK)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        # Instructions at the bottom
        instructions = self.small_font.render("Click on components to identify them. Press ESC to quit.", True, BLACK)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 35))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


# Run the game
if __name__ == "__main__":
    game = UnderTheHoodGame()
    game.run()