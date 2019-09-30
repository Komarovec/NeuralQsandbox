import json

settings_json = json.dumps([
    {"type": "title",
     "title": "Debug menu"},

    {"type": "bool",
     "title": "Draw raycasts",
     "section": "Debug",
     "key": "boolraycasts"},

    {"type": "numeric",
     "title": "Number of raycasts",
     "section": "Debug",
     "key": "numraycasts"},

    {"type": "numeric",
     "title": "Angle of raycasts",
     "section": "Debug",
     "key": "angleraycasts"}
])