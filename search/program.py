# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor, BOARD_N
from .utils import render_board
from collections import deque


def search(
    board: dict[Coord, CellState]
) -> list[Action] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to `CellState` instances (each with a `.color` and
            `.height` attribute).

    Returns:
        A list of actions (MoveAction, EatAction, or CascadeAction), or `None`
        if no solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # Using BFS to find shortest path to goal
    if goal_state(board):
        return []

    queue = deque([(board,[])])
    visited = {state_to_tuple(board)}

    while queue:
        current_board, path = queue.popleft()
        for action in legal_actions(current_board, PlayerColor.RED): 
            next_board = apply_action(current_board, action)
            hash_state = state_to_tuple(next_board)
            if hash_state not in visited:
                if goal_state(next_board):
                    return path + [action]
                visited.add(hash_state)
                queue.append((next_board, path + [action])) 

    return None
    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    #return [
        #MoveAction(Coord(3, 3), Direction.Down),
        #EatAction(Coord(4, 3), Direction.Down),
    #]

def state_to_tuple(board: dict[Coord, CellState]) -> tuple:
    state_list = []

    for coord in board:
        cell = board[coord]
        state_list.append((coord.r, coord.c, cell.color, cell.height))

    state_list.sort()
    return tuple(state_list)


def copy_board(board: dict[Coord, CellState]) -> dict[Coord, CellState]:
    new_board = {}

    for coord in board:
        new_board[coord] = board[coord]

    return new_board

def goal_state(board: dict[Coord, CellState]) -> bool:
    # returns true if no more blue pieces on the board
    return not any(s.color == PlayerColor.BLUE for s in board.values())

def legal_actions(board: dict[Coord, CellState], color: PlayerColor) -> list[Action]:
    # generates valid moves for the player
    actions = []
    for coord, state in board.items():
        if state.color != color:
            continue
    
        for d in Direction:
            destination = coord + d
            on_board = 0 <= destination.r < BOARD_N and 0 <= destination.c < BOARD_N

            if on_board:
                target = board.get(destination)
                if target is None or target.color == color:
                    actions.append(MoveAction(coord, d))
                elif target.color != color and state.height >= target.height:
                    actions.append(EatAction(coord, d))
            
            if state.height > 1:
                actions.append(CascadeAction(coord, d))


    return actions

def apply_action(board: dict[Coord, CellState], action: Action) -> dict[Coord, CellState]:
    new_board = copy_board(board)

    if isinstance(action, MoveAction) or isinstance(action, EatAction):
        moving_stack = new_board[action.coord]
        del new_board[action.coord]

        target_coord = action.coord + action.direction

        if isinstance(action, MoveAction) and target_coord in new_board:
            existing_stack = new_board[target_coord]
            new_board[target_coord] = CellState(
                moving_stack.color,
                moving_stack.height + existing_stack.height
            )
        else:
            new_board[target_coord] = moving_stack

    elif isinstance(action, CascadeAction):
        origin_stack = new_board[action.coord]
        del new_board[action.coord]

        h = origin_stack.height

        for i in range(1, h + 1):
            try:
                landing_site = action.coord + (action.direction * i)
            except ValueError:
                continue

            if 0 <= landing_site.r < BOARD_N and 0 <= landing_site.c < BOARD_N:
                if landing_site in new_board:
                    push_chain = []
                    current_pos = landing_site

                    while current_pos in new_board:
                        push_chain.append((current_pos, new_board[current_pos]))
                        del new_board[current_pos]

                        try:
                            current_pos = current_pos + action.direction
                        except ValueError:
                            break

                    for old_pos, stack in reversed(push_chain):
                        try:
                            new_pos = old_pos + action.direction
                            if 0 <= new_pos.r < BOARD_N and 0 <= new_pos.c < BOARD_N:
                                new_board[new_pos] = stack
                        except ValueError:
                            pass

                new_board[landing_site] = CellState(origin_stack.color, 1)

    return new_board