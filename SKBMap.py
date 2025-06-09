from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class SKBMap:
    """
    Contains all the data to define a sokoban game with convenient getters.
    """
    
    def __init__(self, skb_data: str | list):
        """
        Loads and parses a text file with sokoban data.
        """        
        self._skbm = []
        if type(skb_data) == str:
            self._load_skb_file(skb_data)
            self._format_check()

            # Pairing one-liner
            for line in [1, 2, 3]:
                self._skbm[line] = [(self._skbm[line][i], self._skbm[line][i+1]) for i in range(1, len(self._skbm[line]), 2)]
        else:
            self._skbm = skb_data
        
        # Define actual class attributes
        self._bounds = (self._skbm[0][0], self._skbm[0][1])
        self._loc = self._create_loc([self._skbm[2], self._skbm[3], tuple(self._skbm[4])])
        self._size = self._create_size([len(self._skbm[1]), len(self._skbm[2]), len(self._skbm[3]), self._bounds])

        # Convert to grid
        self._skbm_grid = self._to_grid()

        # Find moves
        self._moves = self._find_moves()

        # Find heuristics
        self._close = self._find_close()


# Public definitions
    @property
    def size(self):
        """
        Returns how many of a certain item (e.g. amount.boxes).
        """
        return self._size

    @property
    def loc(self) -> tuple:
        """
        Returns location of a certain item (e.g. (2, 2))
        """
        return self._loc

    @property
    def moves(self) -> dict[list]:
        """
        Returns a dictionary of boxes, which contains a dictionary 
        of directions, which contains a list of inputs (including 
        the pushing of the box).
        """
        moves = dict()
        for i in range(self._size.boxes):
            box = {'U': self._moves[i][0], 'R': self._moves[i][1], 'D': self._moves[i][2], 'L': self._moves[i][3],}
            moves[self._loc.boxes[i]] = box
        return moves

    @property
    def close(self) -> list[int]:
        """
        Returns a list of how close each box is to the closest
        storage space.
        """
        return self._close

    @property
    def data(self):
        """
        Returns parsed data of the current board state.
        """
        return self._skbm
    
    def display(self):
        """
        Prints a visualization of current board state on the terminal.
        """
        for row in self._skbm_grid:
            for piece in row:
                match piece:
                    case '_':
                        print(' ', end='')
                    case 'W':
                        print('#', end='')
                    case 'B':
                        print('$', end='')
                    case 'S':
                        print('.', end='')
                    case 'P':
                        print('@', end='')
            print()


# Private definitions
    def _find_moves(self) -> list:
        """
        Displays a list of moves
        """
        # Very spaghetti, never forgetti
        moves = []
        matrix = [[1 if piece == '_' or piece == 'S' or piece == 'P' else 0 for piece in row]for row in self._skbm_grid]
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never) # Initialize A*
        for box in self._loc.boxes:
            grid = Grid(matrix = matrix)
            moves_dir = []
            for direction in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
                side = tuple(x + y for x, y in zip(box, direction))
                other_side = tuple(x - y for x, y in zip(box, direction))
                if (self._within_bounds(side) and matrix[side[0]-1][side[1]-1] == 1 and
                    self._within_bounds(other_side) and matrix[other_side[0]-1][other_side[1]-1] == 1):
                    start = grid.node(self._loc.player[1]-1, self._loc.player[0]-1)
                    end = grid.node(side[1]-1, side[0]-1)
                    path, runs = finder.find_path(start, end, grid)
                    for i in range(len(path)-1):
                        path[i] = {(1, 0): 'R', (0, -1): 'U', (-1, 0): 'L', (0, 1): 'D'}\
                                  .get((path[i+1].x - path[i].x, path[i+1].y - path[i].y))
                    if path:
                        path[-1] = {(1, 0): 'U', (0, -1): 'R', (-1, 0): 'D', (0, 1): 'L'}\
                                   .get(direction)
                    moves_dir.append(path)
                else:
                    moves_dir.append([])
            moves.append(moves_dir)
        return moves

    def _find_close(self) -> list:
        """
        Returns how close each box is with respect to walls.
        """
        # Very spaghetti, never forgetti
        distance = []
        matrix = [[1 if piece == '_' or piece == 'S' or piece == 'P' else 0 for piece in row]for row in self._skbm_grid]
        grid = Grid(matrix = matrix)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never) # Initialize A*
        storage_nodes = {storage: grid.node(storage[1]-1, storage[0]-1) for storage in self._loc.storage}
        for box in self._loc.boxes:
            start = grid.node(box[1]-1, box[0]-1)
            potential = [len(finder.find_path(start, end, grid)[0]) for end in storage_nodes.values()]
            distance.append(min(potential))
        return distance
    
    def _to_grid(self) -> list[list]:
        """
        Converts sokoban data into a usable grid layout.
        Each grid will be represented as:
        '_' - empty
        'W' - wall
        'B' - box
        'S' - storage location
        'P' - player location
        """
        skbm = [['_' for _ in range(self._bounds[1])] for _ in range(self._bounds[0])]
        piece_type = ['W', 'B', 'S', 'P']
        for i in range(2):
            for piece in self._skbm[i+1]:
                if not self._within_bounds(piece):
                    raise self.SKBOutofBoundsError(self._bounds, piece)
                if skbm[piece[0]-1][piece[1]-1] != '_':
                    raise self.SKBConflictingPieceError(skbm[piece[0]-1][piece[1]-1], piece, piece_type[i])
                skbm[piece[0]-1][piece[1]-1] = piece_type[i]
        # Exception for Storage Locations
        for piece in self._skbm[3]:
            if not self._within_bounds(piece):
                raise self.SKBOutofBoundsError(self._bounds, piece)
            if skbm[piece[0]-1][piece[1]-1] != '_':
                if skbm[piece[0]-1][piece[1]-1] != 'B':
                    raise self.SKBConflictingPieceError(skbm[piece[0]-1][piece[1]-1], piece, piece_type[2])
            elif skbm[piece[0]-1][piece[1]-1] == '_':
                skbm[piece[0]-1][piece[1]-1] = piece_type[2]
        # Player location
        player = self._skbm[4]
        if not self._within_bounds(player):
            raise self.SKBOutofBoundsError(self._bounds, player)
        if skbm[player[0]-1][player[1]-1] == 'W' or skbm[player[0]-1][player[1]-1] == 'B':
            raise self.SKBConflictingPieceError(skbm[player[0]-1][player[1]-1], player, piece_type[3])
        skbm[player[0]-1][player[1]-1] = piece_type[3]
        return skbm
    
    def _within_bounds(self, piece: tuple) -> bool:
        """
        Checks to see if an item is within bounds.
        """
        return 1 <= piece[0] <= self._bounds[0] and 1 <= piece[1] <= self._bounds[1]

    def _load_skb_file(self, skb_file: str) -> None:
        """
        Loads sokoban text file, helps with __init__ readability.
        """
        with open(skb_file, 'r') as file:
            err_index = 0
            for line in file:
                int_line = []
                for num in line.split():
                    if not num.isdigit(): # Check if all are numbers
                        raise self.SKBFileValueError(err_index)
                    int_line.append(int(num))
                self._skbm.append(int_line)
                err_index += 1

    def _create_size(self, size: list):
        class _Size:
            """
            Holds aggregated board data.
            """
            def __init__(self, size: list):
                self._size = size
            @property
            def walls(self) -> int:
                return self._size[0]
            @property
            def boxes(self) -> int:
                return self._size[1]
            @property
            def storage(self) -> int:
                return self._size[2]
            @property
            def bounds(self) -> tuple:
                return self._size[3]
        return _Size(size)

    def _create_loc(self, loc: list):
        class _Loc:
            """
            Holds current board piece locations.
            """
            def __init__(self, loc: list):
                self._loc = loc
            @property
            def boxes(self) -> list[tuple]:
                return self._loc[0]
            @property
            def storage(self) -> list[tuple]:
                return self._loc[1]
            @property
            def player(self) -> tuple:
                return self._loc[2]
        return _Loc(loc)
                

    def _format_check(self) -> None:
        """
        Includes any necessary formatting exceptions.
        """
        if len(self._skbm) != 5:
            raise self.SKBLineCountError(len(self._skbm))
        format_messages = ['[numRows numColumns]',
                           '[nWallSquares, list of wall square coordinates].\nWas',
                           '[nBoxes, list of box coordinates].\nWas',
                           '[nStorageLocations, list of wall storage location coordinates].\nWas',
                           'initial location [x, y]']
        for i in [0, 4]:
            if len(self._skbm[i]) != 2:
                raise self.SKBLineFormatError(i, format_messages[i], self._skbm[i])
        for i in [1, 2, 3]:
            if (len(self._skbm[i])-1)/2 != self._skbm[i][0]:
                raise self.SKBLineFormatError(1, f'{format_messages[i]} {self._skbm[i][0]} pairs long',
                                              f'{(len(self._skbm[i])-1)/2} pairs')
                    
      
# Exceptions for file formatting
    class SKBFileValueError(Exception):
        def __init__(self, index: int):
            super().__init__(f'Non-integer (or non-positive integer) at line {index}.')
    class SKBLineCountError(Exception):
        def __init__(self, length: int):
            super().__init__(f'Line count must be 5. Currently it\'s {length}.')
    class SKBLineFormatError(Exception):
        def __init__(self, index: int, message: str, line: str):
            super().__init__(f'Line {index} should be {message} but instead got {line}.')

# Exceptions for incorrect pieces
    class SKBOutofBoundsError(Exception):
        def __init__(self, map_size: tuple, piece: tuple):
            super().__init__(f'Map size is {map_size} but {piece} is not within its domain.')
    class SKBConflictingPieceError(Exception):
        def __init__(self, existing_piece: str, piece: tuple, incoming_piece: str):
            super().__init__(f'Existing \'{existing_piece}\' at {piece} is in conflict with incoming \'{incoming_piece}\'.')


if __name__ == "__main__":
    map = SKBMap('sokoban00.txt')
    data = map.data
    map = SKBMap(data)
    # Visualize
    map.display()

    print('\nBoxes and their pushable paths')
    for box, push in map.moves.items():
        print(box, '', end='')
        for direction, path in map.moves[box].items():
            if map.moves[box][direction]:
                print(f'{direction}: {path} ', end='')
        print()

    print('\nThe actual dictionary "map.moves":')
    print(map.moves)