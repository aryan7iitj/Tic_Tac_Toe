const boardElement = document.getElementById('board');
const messageElement = document.getElementById('message');
const resetButton = document.getElementById('reset-btn');

// Set your API base URL
const API_BASE = "http://localhost:8000"; // Deployed API URL

// Fetch the game state from the server
async function fetchGameState() {
    try {
        const response = await fetch(`${API_BASE}/state`);
        if (!response.ok) {
            throw new Error("Failed to fetch game state");
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching game state:", error);
        messageElement.textContent = "Error fetching game state. Please try again.";
    }
}

// Make a move by sending it to the backend
async function makeMove(row, col) {
    try {
        const response = await fetch(`${API_BASE}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        return await response.json();
    } catch (error) {
        console.error("Error making move:", error);
        messageElement.textContent = error.message;
    }
}

// Reset the game by calling the reset API
async function resetGame() {
    try {
        const response = await fetch(`${API_BASE}/reset`, { method: 'POST' });
        if (!response.ok) {
            throw new Error("Failed to reset game");
        }
        const state = await response.json();
        renderBoard(state);
        messageElement.textContent = ''; // Clear any message
    } catch (error) {
        console.error("Error resetting game:", error);
        messageElement.textContent = "Error resetting game. Please try again.";
    }
}

// Render the board on the screen
function renderBoard(state) {
    boardElement.innerHTML = ''; // Clear previous board
    state.board.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            const cellElement = document.createElement('div');
            cellElement.classList.add('cell');
            if (cell) cellElement.classList.add('taken');
            cellElement.textContent = cell || ''; // Display 'X', 'O', or empty
            cellElement.addEventListener('click', async () => {
                if (!cell && !state.winner && !state.is_draw) {
                    const newState = await makeMove(rowIndex, colIndex);
                    if (newState) {
                        renderBoard(newState);
                        if (newState.winner) {
                            messageElement.textContent = `${newState.winner} wins!`;
                        } else if (newState.is_draw) {
                            messageElement.textContent = "It's a draw!";
                        }
                    }
                }
            });
            boardElement.appendChild(cellElement);
        });
    });
}

// Initialize the game
(async function initializeGame() {
    try {
        const state = await fetchGameState();
        if (state) {
            renderBoard(state);
        }
    } catch (error) {
        console.error("Error during initialization:", error);
        messageElement.textContent = "Error initializing game. Please try again.";
    }
})();

// Attach event listener to reset button
resetButton.addEventListener('click', resetGame);
