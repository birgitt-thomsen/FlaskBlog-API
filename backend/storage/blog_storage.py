""" This module handles the creation of the json data file. """
import json

FILE_PATH = '../data/data.json'

initial_data = [
  {
    "id": 1,
     "title": "Why My Coffee Deserves a Promotion",
        "content": "Today I discovered that my productivity is directly proportional to the quality of my coffee. After upgrading from instant coffee to a freshly brewed cup, I completed three tasks, answered five emails, and only got distracted by cat videos twice. At this rate, I expect my coffee machine to be asking for a corner office by the end of the week. Until then, I'll continue my highly scientific research one cup at a time.",
    "author": "Ada Byte",
    "date": "2026-06-03"
  },
  {
    "id": 2,
    "title": "The Day My Space Bar Took a Vacation",
        "content": "Disaster struck this morning when my space bar stopped responding. For nearly ten minutes, all my sentences looked like secret passwords. After a brief investigation involving compressed air, questionable tapping techniques, and a stern lecture, the space bar returned to duty. Productivity has resumed, and words once again have room to breathe.",
    "author": "Captain Keyboard",
    "date": "2026-06-09"
  }
]

try:
    with open(FILE_PATH, "x", encoding='utf-8') as f:  # "x" = create, fail if
        # exists
        json.dump(initial_data, f, indent=4)
except FileExistsError:
    pass  # if file already exists, do nothing
