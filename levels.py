import pygame

def get_levels():
    return [
        {
            "name": "Level 1: The Frozen Outskirts",
            "theme": "arctic",
            "sky_color": (210, 230, 255),
            "ice_color": (170, 210, 245),
            "gravity_mod": 0.7,
            "rooms": [
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(400, 350, 200, 20)],
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(100, 300, 150, 20), pygame.Rect(500, 300, 150, 20)],
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(200, 250, 400, 20)],
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(100, 200, 100, 20), pygame.Rect(600, 200, 100, 20)],
                [pygame.Rect(0, 440, 800, 40)] # Boss Room
            ],
            "slimes": {
                0: [300, 550],
                1: [250, 600],
                2: [400],
                3: [350, 500]
            }
        },
        {
            "name": "Level 2: The Granite Grotto",
            "theme": "rocky",
            "sky_color": (50, 40, 35),      # Dark Brown/Cave
            "ice_color": (100, 90, 80),     # Dark Gray Rock
            "gravity_mod": 0.9,             # Heavier gravity
            "rooms": [
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(50, 320, 200, 20), pygame.Rect(500, 250, 200, 20)],
                [pygame.Rect(0, 440, 800, 40), pygame.Rect(300, 300, 200, 20), pygame.Rect(100, 180, 150, 20)],
                [pygame.Rect(0, 440, 800, 40)] # Boss Room
            ],
            "slimes": {
                0: [150, 450, 650],
                1: [200, 500]
            }
        },
        # --- NEW LAVA LEVEL ---
        {
            "name": "Level 3: The Molten Maw",
            "theme": "lava",
            "sky_color": (40, 10, 0),       # Deep volcanic red/black
            "ice_color": (180, 60, 20),     # Hardened magma rock
            "gravity_mod": 0.65,            # Lighter (thermal updrafts)
            "rooms": [
                # Room 0: Introduction with lava pit
                [pygame.Rect(0, 440, 300, 40), pygame.Rect(500, 440, 300, 40), pygame.Rect(350, 320, 100, 20)],
                # Room 1: High platforms
                [pygame.Rect(0, 440, 150, 40), pygame.Rect(200, 350, 150, 20), pygame.Rect(450, 260, 150, 20), pygame.Rect(650, 180, 150, 20)],
                # Room 2: Boss Arena (solid ground for the fight)
                [pygame.Rect(0, 440, 800, 40)]
            ],
            "hazards": {
                # Lava pits that the player can fall into (handled by your PlatformingManager)
                0: [pygame.Rect(300, 460, 200, 40)],
                1: [pygame.Rect(150, 460, 650, 40)]
            },
            "slimes": {
                0: [100, 600],
                1: [250, 500]
            }
        }
    ]
