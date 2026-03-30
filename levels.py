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
        }
    ]