import json

game_settings_json = json.dumps([
    {"type": "title",
     "title": "Game settings"},

    {"type": "bool",
     "title": "Draw raycasts",
     "section": "Game",
     "key": "boolraycasts"},

    {"type": "raycasts",
     "title": "Number of raycasts. 1 - 20",
     "section": "Game",
     "key": "numraycasts"},

    {"type": "angle",
     "title": "Angle of raycasts. 1 - 180",
     "section": "Game",
     "key": "angleraycasts"}
])

ai_settings_json = json.dumps([
    {"type": "title",
     "title": "AI settings"},
    {"type": "options",
     "title": "Learning type",
     "desc": "Change the way neural network is learned.",
     "section": "AI",
     "key": "learn_type",
     "options": ["DQN"]},

    {"type": "options",
     "title": "Network type",
     "desc": "Change functional structure of neural network.",
     "section": "AI",
     "key": "network_type",
     "options": ["Sequential"]},


    {"type": "title",
     "title": "DQN settings"},
    {"type": "multiplier",
     "title": "Discount factor",
     "desc": "Discout of future estimated reward. <0,1>",
     "section": "DQN",
     "key": "dqn_discount_factor"},

    {"type": "multiplier",
     "title": "Exploration max",
     "desc": "Starting exploration value. <0,1>",
     "section": "DQN",
     "key": "dqn_exploration_max"},

    {"type": "multiplier",
     "title": "Exploration min",
     "desc": "Minimal exploration value. <0,1>",
     "section": "DQN",
     "key": "dqn_exploration_min"},

    {"type": "multiplier",
     "title": "Exploration decay",
     "desc": "How much will exploration decrease over time. <0,1>",
     "section": "DQN",
     "key": "dqn_exploration_decay"},

    {"type": "batch",
     "title": "Batch size",
     "desc": "Change the batch size of experience replay. 10 - 100",
     "section": "DQN",
     "key": "dqn_batch_size"},

    {"type": "options",
     "title": "Experience replay model",
     "desc": "Change model of ER",
     "section": "DQN",
     "key": "dqn_experience_type",
     "options": ["ER"]},
])