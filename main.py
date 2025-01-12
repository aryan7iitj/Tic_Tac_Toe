from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()


# Define allowed origins for CORS
origins = [
    "*",  # Allow all origins, change to specific origins if necessary
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    file_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=file_path.read_text(), status_code=200)

# Initial game state
game_state = {
    "board": [["" for _ in range(3)] for _ in range(3)],
    "winner": None,
    "is_draw": False,
    "current_player": "X",
}

class Move(BaseModel):
    row: int
    col: int

@app.get("/state")
def get_state():
    global game_state
    # Reset the game state whenever the state is fetched
    game_state = {
        "board": [["" for _ in range(3)] for _ in range(3)],
        "winner": None,
        "is_draw": False,
        "current_player": "X",
    }
    return game_state

@app.post("/move")
def make_move(move: Move):
    global game_state
    board = game_state["board"]
    if game_state["winner"] or game_state["is_draw"]:
        raise HTTPException(status_code=400, detail="Game has already ended.")
    if board[move.row][move.col] != "":
        raise HTTPException(status_code=400, detail="Cell already taken.")
    board[move.row][move.col] = game_state["current_player"]
    if check_winner():
        game_state["winner"] = game_state["current_player"]
    elif is_draw():
        game_state["is_draw"] = True
    else:
        game_state["current_player"] = "O" if game_state["current_player"] == "X" else "X"
    return game_state

@app.post("/reset")
def reset_game():
    global game_state
    game_state = {
        "board": [["" for _ in range(3)] for _ in range(3)],
        "winner": None,
        "is_draw": False,
        "current_player": "X",
    }
    return game_state

def check_winner():
    board = game_state["board"]
    lines = [
        # Rows
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # Columns
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # Diagonals
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]
    for line in lines:
        if all(board[x][y] == game_state["current_player"] for x, y in line):
            return True
    return False

def is_draw():
    return all(cell for row in game_state["board"] for cell in row)
