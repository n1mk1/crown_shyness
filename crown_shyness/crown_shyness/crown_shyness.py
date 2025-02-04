import math
import random
import string
import pygame
import numpy as np


class FractalTree:
    def __init__(self, width=1600, height=900, base_length=100, base_depth=3, base_angle=90):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fractal Tree with Crown Shyness Simulation")
        self.clock = pygame.time.Clock()

        # Centralized variables for easy adjustment
        self.base_length = base_length  # Length of the initial branches
        self.base_depth = base_depth  # Depth of recursion
        self.base_angle = base_angle  # Angle between branches
        self.tree_count = 0  # Counter to ensure unique identifiers for each tree
        self.trees = []  # Store branches of each tree separately
        self.intersecting_branches = []  # Store branches that participate in intersections
        self.labels_visible = True  # Toggle for showing/hiding labels
        self.zoom = 1.0  # Zoom factor
        self.offset_x = 0  # Horizontal offset for panning
        self.offset_y = 0  # Vertical offset for panning

    def draw_branch(self, x, y, length, current_angle, depth, tree_id, color=(0, 255, 0)):
        """Recursively draws branches of the fractal tree."""
        if depth == 0:
            return

        end_x, end_y = self.calculate_endpoint(x, y, length, current_angle)
        self.draw_and_store_branch(x, y, end_x, end_y, tree_id, depth, color, current_angle)
        self.draw_sub_branches(end_x, end_y, length, current_angle, depth, tree_id, color)

    def calculate_endpoint(self, x, y, length, angle):
        """Calculates the endpoint of a branch."""
        end_x = x + length * np.cos(np.radians(angle))
        end_y = y - length * np.sin(np.radians(angle))  # Subtract because Pygame's y-axis is inverted
        return end_x, end_y

    def draw_and_store_branch(self, x, y, end_x, end_y, tree_id, depth, color, current_angle):
        """Draws the branch and stores it for later use."""
        pygame.draw.line(self.screen, color, (x, y), (end_x, end_y), 2)
        branch = ((x, y), (end_x, end_y))
        self.check_intersections(branch, tree_id)
        self.trees[tree_id - 1].append((branch, color, depth, current_angle))
        self.draw_node(end_x, end_y)
        if self.labels_visible:
            self.label_branch(x, y, end_x, end_y, tree_id, depth, current_angle)

    def draw_sub_branches(self, end_x, end_y, length, current_angle, depth, tree_id, color):
        """Draws sub-branches from the given branch."""
        new_length = length * 0.8
        self.draw_branch(end_x, end_y, new_length, current_angle + self.base_angle, depth - 1, tree_id, color)
        self.draw_branch(end_x, end_y, new_length, current_angle - self.base_angle, depth - 1, tree_id, color)

    def draw_node(self, x, y):
        """Draws a node at the specified position."""
        pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 3)

    def label_branch(self, x, y, end_x, end_y, tree_id, depth, current_angle):
        """Labels the branch with depth and angle information."""
        font = pygame.font.Font(None, 24)
        branch_label = f"T{tree_id}_D{depth}_A{int(current_angle)}"
        label_surface = font.render(branch_label, True, (0, 0, 255))
        label_pos = ((x + end_x) / 2, (y + end_y) / 2)
        self.screen.blit(label_surface, label_pos)

    def draw_fractal_tree(self, x, y, tree_id):
        """Draws the initial branches of the fractal tree from a given starting point."""
        self.trees.append([])  # Add a new list for storing branches of the new tree
        for start_angle in [90, 210, 330]:  # 120 degree separation for triangle formation
            self.draw_branch(x, y, self.base_length, start_angle, self.base_depth, tree_id)

    def remove_intersecting_branches(self):
        """Removes intersecting branches from the data."""
        for branch in self.intersecting_branches:
            for tree_id, branches in enumerate(self.trees):
                if branch in [b[0] for b in branches]:
                    branches.remove(next(b for b in branches if b[0] == branch))
        self.intersecting_branches.clear()

    def check_intersections(self, new_branch, tree_id):
        """Checks if the new branch intersects with any branches from other trees."""
        for i, branches in enumerate(self.trees):
            if i == tree_id - 1:
                continue
            for branch, color, _, _ in branches:
                intersect = self.calculate_intersection(branch, new_branch)
                if intersect:
                    self.handle_intersection(intersect, branch, new_branch)

    def handle_intersection(self, intersect, branch, new_branch):
        """Handles the actions to take when an intersection is detected."""
        print(f"Intersection found at: {intersect}")
        pygame.draw.circle(self.screen, (128, 0, 128), (int(intersect[0]), int(intersect[1])), 5)
        self.redraw_branch(branch, (255, 165, 0))
        self.redraw_branch(new_branch, (255, 165, 0))
        if branch not in self.intersecting_branches:
            self.intersecting_branches.append(branch)
        if new_branch not in self.intersecting_branches:
            self.intersecting_branches.append(new_branch)

    def redraw_branch(self, branch, color):
        """Redraws a branch with a new color."""
        (x1, y1), (x2, y2) = branch
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)

    @staticmethod
    def calculate_intersection(branch1, branch2):
        """Calculates the intersection point of two line segments, if it exists."""
        (x1, y1), (x2, y2) = branch1
        (x3, y3), (x4, y4) = branch2

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None  # Parallel lines

        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        if (min(x1, x2) <= px <= max(x1, x2) and
                min(y1, y2) <= py <= max(y1, y2) and
                min(x3, x4) <= px <= max(x3, x4) and
                min(y3, y4) <= py <= max(y3, y4)):
            return px, py

        return None

    def run(self):
        """Main loop for the Pygame application."""
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Only create tree on left click
                    x, y = event.pos
                    self.tree_count += 1
                    self.draw_fractal_tree((x - self.offset_x) / self.zoom, (y - self.offset_y) / self.zoom, self.tree_count)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.remove_intersecting_branches()
                    elif event.key == pygame.K_l:
                        self.labels_visible = not self.labels_visible
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up to zoom in
                        mouse_x, mouse_y = event.pos
                        self.zoom *= 1.1
                        self.offset_x = mouse_x - (mouse_x - self.offset_x) * 1.1
                        self.offset_y = mouse_y - (mouse_y - self.offset_y) * 1.1
                    elif event.button == 5:  # Scroll down to zoom out
                        mouse_x, mouse_y = event.pos
                        self.zoom /= 1.1
                        self.offset_x = mouse_x - (mouse_x - self.offset_x) / 1.1
                        self.offset_y = mouse_y - (mouse_y - self.offset_y) / 1.1
                elif event.type == pygame.MOUSEMOTION:
                    if event.buttons[2]:  # Right mouse button to pan
                        self.offset_x += event.rel[0]
                        self.offset_y += event.rel[1]

            # Redraw all branches
            for tree_id, branches in enumerate(self.trees, start=1):
                for branch, color, depth, angle in branches:
                    (x1, y1), (x2, y2) = branch
                    x1 = x1 * self.zoom + self.offset_x
                    y1 = y1 * self.zoom + self.offset_y
                    x2 = x2 * self.zoom + self.offset_x
                    y2 = y2 * self.zoom + self.offset_y
                    pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
                    self.draw_node(x2, y2)
                    if self.labels_visible:
                        self.label_branch(x1, y1, x2, y2, tree_id, depth, angle)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    # Create an instance of FractalTree and run the Pygame application
    fractal_tree = FractalTree(width=1600, height=900, base_length=200, base_depth=4, base_angle=45)
    fractal_tree.run()