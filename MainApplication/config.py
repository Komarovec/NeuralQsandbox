import json

game_settings_json = json.dumps([
    {"type": "title",
     "title": "Game settings"},

    {"type": "bool",
     "title": "Draw raycasts",
     "section": "Game",
     "key": "boolraycasts"},

    {"type": "numeric",
     "title": "Number of raycasts",
     "section": "Game",
     "key": "numraycasts"},

    {"type": "numeric",
     "title": "Angle of raycasts",
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
     "options": ["DQN","SGA"]},

    {"type": "options",
     "title": "Network type",
     "desc": "Change functional structure of neural network.",
     "section": "AI",
     "key": "network_type",
     "options": ["Sequential"]},


    {"type": "title",
     "title": "DQN settings"},
    {"type": "numeric",
     "title": "Discount factor",
     "desc": "Discout of future estimated reward. (Multiplier)",
     "section": "DQN",
     "key": "dqn_discount_factor"},

    {"type": "numeric",
     "title": "Exploration max",
     "desc": "Starting exploration value 1 (100%) - 0 (0%)",
     "section": "DQN",
     "key": "dqn_exploration_max"},

    {"type": "numeric",
     "title": "Exploration min",
     "desc": "Minimal exploration value 1 (100%) - 0 (0%)",
     "section": "DQN",
     "key": "dqn_exploration_min"},

    {"type": "numeric",
     "title": "Exploration decay",
     "desc": "How much will exploration decrease over time. (Multiplier)",
     "section": "DQN",
     "key": "dqn_exploration_decay"},

    {"type": "numeric",
     "title": "Batch size",
     "desc": "Change the batch size of experience replay",
     "section": "DQN",
     "key": "dqn_batch_size"},

    {"type": "options",
     "title": "Experience replay model",
     "desc": "Change model of ER",
     "section": "DQN",
     "key": "dqn_experience_type",
     "options": ["ER","HER","PER"]},


    {"type": "title",
     "title": "SGA settings"},
    {"type": "numeric",
     "title": "Mutation rate",
     "desc": "How often will mutation occur.",
     "section": "SGA",
     "key": "sga_mutation_rate"},

    {"type": "numeric",
     "title": "Population size",
     "desc": "How many individuals will be created.",
     "section": "SGA",
     "key": "sga_population_size"}
])