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
        self.tooltip_font = pygame.font.SysFont('Arial', 18)

        # Load component images
        self.components = {}
        self.load_component_images()

        # Try to load the real engine bay background
        try:
            self.engine_background = pygame.image.load("engine_bay.png")
            self.engine_background = pygame.transform.scale(self.engine_background, (700, 450))
        except:
            # Create a fallback engine background if image isn't available
            self.engine_background = pygame.Surface((700, 450))
            self.engine_background.fill((50, 50, 50))  # Dark gray background
            print("Warning: engine_bay.png not found. Using default background.")

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
        self.tooltip = None

        # Add difficulty levels
        self.difficulty = "normal"  # Options: "easy", "normal", "hard"
        self.time_per_question = 10  # Seconds per question (only used in hard mode)
        self.question_timer = 0
        self.show_labels = True  # Whether to show labels (hidden in hard mode)

        # Component descriptions for tooltips
        self.component_descriptions = {
            'A': "Holds fluid for cleaning your windshield. Check and refill regularly.",
            'B': "Stores brake fluid for the hydraulic braking system. Critical for safe braking.",
            'C': "Measures oil level in the engine. Check when engine is cool and on level ground.",
            'D': "Where you add oil to the engine. Use manufacturer recommended oil type.",
            'E': "Contains coolant mixture that regulates engine temperature. Check when engine is cool.",
            'F': "Provides electrical power to start the engine and run accessories. Check terminals for corrosion."
        }

        # Generate a list of components to ask about
        self.component_queue = list(self.components.keys())
        random.shuffle(self.component_queue)

        # Set the first question
        self.set_next_question()

    def load_component_images(self):
        # Component config: key, image path, display name, position, custom size
        component_data = [
            ('A', "washer_reservoir.png", "Windshield Washer Reservoir", (100, 120), (360, 60)),
            ('B', "brake_fluid.png", "Brake Fluid Reservoir", (50, 300), (70, 50)),
            ('C', "oil_dipstick.png", "Oil Dipstick", (250, 350), (20, 80)),
            ('D', "oil_cap.png", "Oil Cap", (300, 150), (50, 50)),
            ('E', "coolant_reservoir.png", "Coolant Reservoir", (450, 120), (70, 60)),
            ('F', "battery.png", "Battery", (550, 150), (90, 50))
        ]

        # Fallback colors
        colors = {
            'A': (0, 162, 232),  # Blue - Washer Reservoir
            'B': (128, 128, 128),  # Gray - Brake Fluid
            'C': (255, 201, 14),  # Yellow - Oil Dipstick
            'D': (0, 0, 0),  # Black - Oil Cap
            'E': (255, 242, 0),  # Yellow - Coolant Reservoir
            'F': (50, 50, 50)  # Dark Gray - Battery
        }

        for key, img_path, name, pos, size in component_data:
            width, height = size
            try:
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, size)  # Scale to custom size
            except:
                # Create fallback placeholder
                img = pygame.Surface(size, pygame.SRCALPHA)
                img.fill(colors[key])

                # Draw placeholder details
                if key == 'A':  # Washer reservoir
                    pygame.draw.rect(img, WHITE, (width * 0.3, height * 0.2, width * 0.4, height * 0.6))
                elif key == 'B':  # Brake fluid
                    pygame.draw.rect(img, WHITE, (10, 10, width - 20, height - 20))
                    pygame.draw.circle(img, BLACK, (width // 2, height // 2), min(width, height) // 4)
                elif key == 'C':  # Dipstick
                    pygame.draw.rect(img, colors[key], (width // 2 - 2, 0, 4, height))
                    pygame.draw.circle(img, colors[key], (width // 2, 10), 10)
                elif key == 'D':  # Oil cap
                    pygame.draw.circle(img, BLACK, (width // 2, height // 2), min(width, height) // 2)
                    pygame.draw.circle(img, WHITE, (width // 2, height // 2), min(width, height) // 2 - 5)
                    pygame.draw.circle(img, BLACK, (width // 2, height // 2), min(width, height) // 2 - 10)
                elif key == 'E':  # Coolant
                    pygame.draw.rect(img, WHITE, (5, 5, width - 10, height - 10))
                    pygame.draw.rect(img, colors[key], (10, 10, width - 20, height - 20))
                elif key == 'F':  # Battery
                    pygame.draw.rect(img, BLACK, (5, 5, width - 10, height - 10))
                    pygame.draw.circle(img, RED, (int(width * 0.3), 10), 5)
                    pygame.draw.circle(img, BLUE, (int(width * 0.7), 10), 5)

            rect = img.get_rect(center=pos)
            mask = pygame.mask.from_surface(img)

            self.components[key] = {
                'image': img,
                'name': name,
                'position': pos,
                'rect': rect,
                'mask': mask,
                'original': img.copy()
            }

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
            'position': self.components[selected_component]['position'],
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

                    # Adjust mouse position for engine area
                    engine_x = (SCREEN_WIDTH - self.engine_background.get_width()) // 2
                    engine_y = 80
                    adjusted_mouse_x = mouse_pos[0] - engine_x
                    adjusted_mouse_y = mouse_pos[1] - engine_y

                    # Only check for clicks if mouse is within engine boundaries
                    if (0 <= adjusted_mouse_x < self.engine_background.get_width() and
                            0 <= adjusted_mouse_y < self.engine_background.get_height()):

                        # Check for click on components using their masks for pixel-perfect detection
                        for component, data in self.components.items():
                            comp_rect = data['rect'].copy()
                            rel_x = adjusted_mouse_x - comp_rect.x
                            rel_y = adjusted_mouse_y - comp_rect.y

                            if (comp_rect.collidepoint(adjusted_mouse_x, adjusted_mouse_y) and
                                    0 <= rel_x < comp_rect.width and
                                    0 <= rel_y < comp_rect.height and
                                    data['mask'].get_at((rel_x, rel_y))):
                                self.check_answer(component)
                                break

    def update(self):
        # Update popup timer
        if self.popup_timer > 0:
            self.popup_timer -= 1
        else:
            self.popup = None

        # Update hovered component and tooltip
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_component = None
        self.tooltip = None

        if self.game_state == GAME_PLAYING:
            # Adjust mouse position for engine area
            engine_x = (SCREEN_WIDTH - self.engine_background.get_width()) // 2
            engine_y = 80
            adjusted_mouse_x = mouse_pos[0] - engine_x
            adjusted_mouse_y = mouse_pos[1] - engine_y

            # Only check for hover if mouse is within engine boundaries
            if (0 <= adjusted_mouse_x < self.engine_background.get_width() and
                    0 <= adjusted_mouse_y < self.engine_background.get_height()):

                # Check for hover on components using their rects and masks
                for component, data in self.components.items():
                    comp_rect = data['rect'].copy()
                    rel_x = adjusted_mouse_x - comp_rect.x
                    rel_y = adjusted_mouse_y - comp_rect.y

                    if (comp_rect.collidepoint(adjusted_mouse_x, adjusted_mouse_y) and
                            0 <= rel_x < comp_rect.width and
                            0 <= rel_y < comp_rect.height and
                            data['mask'].get_at((rel_x, rel_y))):
                        self.hovered_component = component

                        # Create tooltip with component description
                        if component in self.component_descriptions:
                            tooltip_text = f"{data['name']}: {self.component_descriptions[component]}"
                            self.tooltip = {
                                'text': tooltip_text,
                                'position': (
                                    data['position'][0] + engine_x,
                                    data['position'][1] + engine_y + 50
                                )
                            }
                        break

    def draw(self):
        self.screen.fill(WHITE)

        # Draw engine background
        engine_x = (SCREEN_WIDTH - self.engine_background.get_width()) // 2
        engine_y = 80
        self.screen.blit(self.engine_background, (engine_x, engine_y))

        # Draw components
        for component, data in self.components.items():
            # Prepare the image to draw
            img_to_draw = data['original'].copy()

            # Apply highlight effect for hovered component
            if component == self.hovered_component:
                # Create a highlighted version with a glowing border
                highlight_surface = pygame.Surface((data['rect'].width + 10, data['rect'].height + 10), pygame.SRCALPHA)
                highlight_surface.fill((0, 0, 0, 0))  # Transparent background

                # Draw a 5px glowing border
                pygame.draw.rect(highlight_surface, HIGHLIGHT_COLOR,
                                 (0, 0, highlight_surface.get_width(), highlight_surface.get_height()),
                                 5, border_radius=10)

                # Draw the component image in the center of the highlight
                highlight_surface.blit(img_to_draw, (5, 5))

                # Draw the highlighted version
                comp_pos = (data['position'][0] - highlight_surface.get_width() // 2 + engine_x,
                            data['position'][1] - highlight_surface.get_height() // 2 + engine_y)
                self.screen.blit(highlight_surface, comp_pos)
            else:
                # Draw the regular component
                comp_pos = (data['position'][0] - data['rect'].width // 2 + engine_x,
                            data['position'][1] - data['rect'].height // 2 + engine_y)
                self.screen.blit(img_to_draw, comp_pos)

            # Draw component label if enabled
            if self.show_labels:
                label_bg = pygame.Surface((30, 30))
                label_bg.fill(BLUE)
                label_bg.set_alpha(200)  # Semi-transparent

                # Position the label near the component
                label_pos = (data['position'][0] - 15 + engine_x,
                             data['position'][1] - data['rect'].height // 2 - 25 + engine_y)
                self.screen.blit(label_bg, label_pos)

                # Draw the label text
                label = self.font.render(component, True, WHITE)
                label_rect = label.get_rect(center=(label_pos[0] + 15, label_pos[1] + 15))
                self.screen.blit(label, label_rect)

        # Draw tooltip if component is being hovered over
        if self.tooltip:
            tooltip_text = self.tooltip['text']

            # Wrap text to multiple lines if needed
            max_width = 400
            words = tooltip_text.split(' ')
            lines = []
            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + ' ' + word
                test_width = self.tooltip_font.size(test_line)[0]
                if test_width < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)  # Add the last line

            # Calculate tooltip dimensions
            line_height = self.tooltip_font.get_linesize()
            tooltip_height = line_height * len(lines) + 20  # Add padding
            tooltip_width = min(max_width, max([self.tooltip_font.size(line)[0] for line in lines])) + 20

            # Create tooltip background with semi-transparency
            tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
            tooltip_surface.fill((0, 0, 0, 180))  # Semi-transparent black

            # Add border
            pygame.draw.rect(tooltip_surface, WHITE, (0, 0, tooltip_width, tooltip_height), 1)

            # Render and position text
            for i, line in enumerate(lines):
                text_surface = self.tooltip_font.render(line, True, WHITE)
                tooltip_surface.blit(text_surface, (10, 10 + i * line_height))

            # Position tooltip on screen, ensuring it stays within screen boundaries
            tooltip_x = min(self.tooltip['position'][0] - tooltip_width // 2, SCREEN_WIDTH - tooltip_width - 10)
            tooltip_y = min(self.tooltip['position'][1], SCREEN_HEIGHT - tooltip_height - 10)
            tooltip_x = max(10, tooltip_x)  # Ensure it doesn't go off left edge

            self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))

        # Draw popup if active with enhanced styling
        if self.popup and self.popup_timer > 0:
            popup_color = GREEN if self.popup.get('correct', False) else RED
            text = self.font.render(self.popup['text'], True, BLACK)

            # Position the popup above the component
            popup_x = self.popup['position'][0] + engine_x
            popup_y = self.popup['position'][1] - 60 + engine_y
            text_rect = text.get_rect(center=(popup_x, popup_y))

            # Create a more attractive popup with rounded corners effect
            bg_rect = text_rect.inflate(40, 20)

            # Draw a semi-transparent backdrop for better visibility
            backdrop = pygame.Surface((bg_rect.width + 20, bg_rect.height + 20))
            backdrop.fill(BLACK)
            backdrop.set_alpha(100)  # Semi-transparent
            self.screen.blit(backdrop, (bg_rect.x - 10, bg_rect.y - 10))

            # Main background with rounded corners
            pygame.draw.rect(self.screen, WHITE, bg_rect, border_radius=10)

            # Colored border based on correct/incorrect
            pygame.draw.rect(self.screen, popup_color, bg_rect, 3, border_radius=10)

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
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))

        # Draw current score with a nice box
        score_bg = pygame.Rect(20, 15, 100, 30)
        pygame.draw.rect(self.screen, WHITE, score_bg)
        pygame.draw.rect(self.screen, BLACK, score_bg, 2)
        score_text = self.font.render(f"Score: {self.correct_answers}/{self.total_questions}", True, BLACK)
        self.screen.blit(score_text, (25, 18))

        # Draw current question/instruction panel
        if self.game_state == GAME_PLAYING:
            question_bg = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 70, SCREEN_WIDTH // 2, 40)
            pygame.draw.rect(self.screen, WHITE, question_bg)
            pygame.draw.rect(self.screen, self.feedback_color, question_bg, 2)
            feedback = self.font.render(self.feedback_text, True, self.feedback_color)
            feedback_rect = feedback.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(feedback, feedback_rect)

        # Draw game state-specific UI
        if self.game_state == GAME_WON:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))

            # Create a result panel
            result_panel = pygame.Surface((400, 200))
            result_panel.fill(WHITE)
            panel_rect = result_panel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(result_panel, GREEN, (0, 0, 400, 50))

            # Add content to the panel
            win_text = self.large_font.render("✅ CONGRATULATIONS!", True, WHITE)
            result_panel.blit(win_text, (400 // 2 - win_text.get_width() // 2, 10))

            score_text = self.font.render(f"Your Score: {self.correct_answers}/{self.total_questions}", True, BLACK)
            result_panel.blit(score_text, (400 // 2 - score_text.get_width() // 2, 80))

            restart_text = self.font.render("Press R to play again", True, BLACK)
            result_panel.blit(restart_text, (400 // 2 - restart_text.get_width() // 2, 130))

            # Draw the panel
            self.screen.blit(result_panel, panel_rect)

        elif self.game_state == GAME_LOST:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))

            # Create a result panel
            result_panel = pygame.Surface((400, 200))
            result_panel.fill(WHITE)
            panel_rect = result_panel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(result_panel, RED, (0, 0, 400, 50))

            # Add content to the panel
            lose_text = self.large_font.render("❌ TRY AGAIN!", True, WHITE)
            result_panel.blit(lose_text, (400 // 2 - lose_text.get_width() // 2, 10))

            score_text = self.font.render(f"Your Score: {self.correct_answers}/{self.total_questions}", True, BLACK)
            result_panel.blit(score_text, (400 // 2 - score_text.get_width() // 2, 80))

            restart_text = self.font.render("Press R to restart", True, BLACK)
            result_panel.blit(restart_text, (400 // 2 - restart_text.get_width() // 2, 130))

            # Draw the panel
            self.screen.blit(result_panel, panel_rect)

        # Instructions at the bottom
        if self.game_state == GAME_PLAYING:
            instructions_bg = pygame.Rect(0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30)
            pygame.draw.rect(self.screen, (240, 240, 240), instructions_bg)
            instructions = self.small_font.render(
                "Click on components to identify them. Hover for info. Press ESC to quit.", True,
                BLACK)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 25))

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