import sys
from PyQt6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, QRect, QPoint
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
import random
import os

# The base path 
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

class Pet(QWidget):
    def __init__(self, pet_name, parent=None):
        super().__init__(parent)
        self.pet_name = pet_name
        self.setFixedSize(100, 100)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Variables to handle window dragging
        self.mousePressPos = None
        self.windowPos = None
        self.walking_direction = 1  # 1 for right, -1 for left

        # Timer to update image for walking/eating/dragging animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_activity)
        self.timer.start(100)  # Change the timeout value as needed

        # Flag to indicate whether the pet is eating
        self.is_walking = False
        self.is_eating = False
        self.is_dragging = False

        # Set initial position
        screen_geometry = QApplication.primaryScreen().geometry()
        self.current_pos_x = random.randint(0, screen_geometry.width() - self.width())
        self.current_pos_y = random.randint(0, screen_geometry.height() - self.height())
        self.move(self.current_pos_x, self.current_pos_y)

        # Initialize variables for image paths and index
        # self.walk_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_walk-{i}.png' for i in range(16)]
        # self.eat_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_eat-{i}.png' for i in range(56)]
        # self.drag_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_drag-{i}.png' for i in range(10)]
        # self.sleep_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_sleep-{i}.png' for i in range(30)]
        # self.front_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_front-{i}.png' for i in range(12)]
        # self.bone_paths = [f'/home/prasad/Storage/Documents/Projects/Desktop-pet/milo/assets/milo_bone-{i}.png' for i in range(44)]
        
        # Use relative paths for assets
        self.walk_paths = [os.path.join(base_path, f'assets/milo_walk-{i}.png') for i in range(16)]
        self.eat_paths = [os.path.join(base_path, f'assets/milo_eat-{i}.png') for i in range(56)]
        self.drag_paths = [os.path.join(base_path, f'assets/milo_drag-{i}.png') for i in range(10)]
        self.sleep_paths = [os.path.join(base_path, f'assets/milo_sleep-{i}.png') for i in range(30)]
        self.front_paths = [os.path.join(base_path, f'assets/milo_front-{i}.png') for i in range(12)]
        self.bone_paths = [os.path.join(base_path, f'assets/milo_bone-{i}.png') for i in range(44)]

        self.current_image_index = 0

        # Initialize qimg
        self.qimg = QImage()

        # Falling Animation
        self.falling_animation = QPropertyAnimation(self, b"geometry")
        self.falling_animation.setDuration(2000)  # Adjust the duration as needed
        self.falling_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.falling_animation.finished.connect(self.animation_finished)

        # Delay between state changes in seconds (adjust as needed)
        self.state_change_delay = {
            'walk': 40 * 1000,   # 40 seconds
            'eat': 10 * 1000,   # 10 seconds
            'sleep': 15 * 1000,  # 15 seconds
            'front': 20 * 1000, # 20 seconds
            'bone': 12 * 1000   # 12 seconds
        }
        self.current_state = 'walk'  # Initial state

        # Set initial remaining delay for the first state
        self.remaining_state_delay = self.state_change_delay[self.current_state]

        # Create a context menu
        self.context_menu = self.create_context_menu()

        self.start_falling_animation()
    
    def create_context_menu(self):
        context_menu = QMenu(self)

        # Add "Clear" action to the context menu
        clear_action = context_menu.addAction("Clear")
        clear_action.triggered.connect(self.clear_pet)

        return context_menu

    def contextMenuEvent(self, event):
        # Show the context menu at the current mouse position
        self.context_menu.exec(event.globalPos())
    def clear_pet(self):
        print(f"Clearing {self.pet_name}")
        self.close()

    def start_falling_animation(self):
        self.is_dragging = True
        self.drag()
        # Set the start value for falling animation based on the initial position
        start_rect = QRect(self.current_pos_x, self.current_pos_y, self.width(), self.height())
        self.falling_animation.setStartValue(start_rect)

        # Set the end value for falling animation to be the ground
        self.falling_animation.setEndValue(self.falling_end_position())

        # Start falling animation
        self.falling_animation.start()

    def falling_end_position(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        return QRect(self.x(), screen_geometry.height() - self.height(), self.width(), self.height())

    def update_activity(self):
        # Check if there is a delay between state changes
        if self.is_dragging:
            self.is_eating = False
            self.is_walking = False
            self.drag()
            return
        if self.remaining_state_delay > 0:
            self.remaining_state_delay -= 100  # Decrease the timer resolution
        else:
            # Choose a random state
            # actions = list(self.state_change_delay.keys())
            actions = ['walk','eat','front','bone', 'sleep']
            actions.remove(self.current_state)
            # action = random.choice(actions)
            action = random.choice(actions)
            self.current_state = action
            self.remaining_state_delay = self.state_change_delay[action]

            # Perform the selected action
            if action == 'walk':
                self.is_walking = True
                self.is_eating = False
                self.is_dragging = False
                self.walk()
            elif action == 'eat':
                self.is_walking = False
                self.is_eating = True
                self.is_dragging = False
                self.eat()
            elif action == 'sleep':
                self.is_walking = False
                self.is_eating = False
                self.is_dragging = False
                self.sleep()
            elif action == 'front':
                self.is_walking = False
                self.is_eating = False
                self.is_dragging = False
                self.front()
            elif action == 'bone':
                self.is_walking = False
                self.is_eating = False
                self.is_dragging = False
                self.bone()
            else:
                # Default to walking if an invalid state is chosen
                self.is_walking = True
                self.is_eating = False
                self.is_dragging = False
                self.walk()

        # Continue the animation based on the current state
        if self.is_walking:
            self.walk()
        elif self.is_eating:
            self.eat()
        elif self.is_dragging:
            self.drag()
        elif self.current_state == 'sleep':
            self.sleep()
        elif self.current_state == 'front':
            self.front()
        elif self.current_state == 'bone':
            self.bone()

    def walk(self):
        print("walk")
        # Update the image to create a walking animation
        self.current_image_index = (self.current_image_index + 1) % len(self.walk_paths)
        original_image = QImage(self.walk_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        self.qimg = original_image.copy()  # Create a copy to avoid modifying the original image

        # Get the screen width
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()

        # Move the window to create the walking effect
        new_x = self.x() + 5 * self.walking_direction  # Adjust the value based on your preference
        new_y = self.y()

        # Check if the window is near the screen edge
        if new_x < 0 or new_x + self.width() > screen_width:
            self.walking_direction *= -1  # Reverse the walking direction

        self.move(new_x, new_y)
        self.repaint()

    def eat(self):
        print("eat")
        # Update the image to create an eating animation
        self.current_image_index = (self.current_image_index + 1) % len(self.eat_paths)
        original_image = QImage(self.eat_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        self.qimg = original_image.copy()  # Create a copy to avoid modifying the original image

        # Get the screen width
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()

        # Move the window randomly during eating
        new_x = self.x()   # Adjust the range based on your preference
        new_y = self.y() 

        # Ensure the window stays within the screen bounds
        new_x = max(0, min(new_x, screen_width - self.width()))

        self.move(new_x, new_y)
        self.repaint()

    def sleep(self):
        print("sleep")
        # Update the image to create an eating animation
        self.current_image_index = (self.current_image_index + 1) % len(self.sleep_paths)
        original_image = QImage(self.sleep_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        self.qimg = original_image.copy()  # Create a copy to avoid modifying the original image

        # Get the screen width
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()

        # Move the window randomly during eating
        new_x = self.x()   # Adjust the range based on your preference
        new_y = self.y() 

        # Ensure the window stays within the screen bounds
        new_x = max(0, min(new_x, screen_width - self.width()))

        self.move(new_x, new_y)
        self.repaint()

    def front(self):
        print("front")
        # Update the image to create an eating animation
        self.current_image_index = (self.current_image_index + 1) % len(self.front_paths)
        original_image = QImage(self.front_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        self.qimg = original_image.copy()  # Create a copy to avoid modifying the original image

        # Get the screen width
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()

        # Move the window randomly during eating
        new_x = self.x()   # Adjust the range based on your preference
        new_y = self.y() 

        # Ensure the window stays within the screen bounds
        new_x = max(0, min(new_x, screen_width - self.width()))

        self.move(new_x, new_y)
        self.repaint()

    def bone(self):
        print("bone ")
        # Update the image to create an eating animation
        self.current_image_index = (self.current_image_index + 1) % len(self.bone_paths)
        original_image = QImage(self.bone_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        self.qimg = original_image.copy()  # Create a copy to avoid modifying the original image

        # Get the screen width
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()

        # Move the window randomly during eating
        new_x = self.x()   # Adjust the range based on your preference
        new_y = self.y() 

        # Ensure the window stays within the screen bounds
        new_x = max(0, min(new_x, screen_width - self.width()))

        self.move(new_x, new_y)
        self.repaint()

    def drag(self):
        # Update the image to create a dragging animation
        self.current_image_index = (self.current_image_index + 1) % len(self.drag_paths)
        original_image = QImage(self.drag_paths[self.current_image_index])

        # Flip the image horizontally if walking towards the left
        if self.walking_direction == -1:
            original_image = original_image.mirrored(True, False)

        # Create a copy to avoid modifying the original image
        self.qimg = original_image.copy()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = event.rect()
        painter.drawImage(rect, self.qimg)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressPos = event.globalPosition()
            self.windowPos = self.pos()
            self.is_dragging = True

    def mouseMoveEvent(self, event):
        self.is_dragging = True
        self.update()
        current_pos = self.pos()

        if self.mousePressPos is not None:
            delta = event.globalPosition() - self.mousePressPos
            new_pos = self.windowPos + delta.toPoint()  # Convert delta to QPoint
            self.move(new_pos)

            # Print Milo's current position
            self.current_pos_x = current_pos.x()
            self.current_pos_y = current_pos.y()
            print("Milo's current position:", current_pos.x(), current_pos.y())



    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.update()
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressPos = None
            self.windowPos = None
            self.is_dragging = False
            self.clone_image()

    def clone_image(self):
        print(f"Cloning {self.pet_name}")
        print(self.geometry())
        print(QRect(self.current_pos_x, self.current_pos_y, self.width(), self.height()))

        # Stop other animations when cloning
        self.timer.stop()
        self.is_walking = False
        self.is_eating = False
        self.is_dragging = False

        # Clone the current image to create a stationary image after dragging
        self.qimg = QImage(self.qimg)

        # Set the start value for falling animation based on the release position
        start_rect = QRect(self.current_pos_x, self.current_pos_y, self.width(), self.height())
        self.falling_animation.setStartValue(start_rect)

        # Set the end value for falling animation to be the ground
        self.falling_animation.setEndValue(self.falling_end_position())

        # Start falling animation after cloning
        self.falling_animation.start()

    def animation_finished(self):
        print("animation finished")
        self.is_dragging = False
        self.update_activity()
        self.walk()
        # Reset the window position after the falling animation is finished
        self.setGeometry(self.falling_end_position())
        self.is_walking = True
        self.timer.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    pet1 = Pet("milo")
    pet1.show()
    # pet1 = Pet("milo2")
    # pet1.show()


    sys.exit(app.exec())
