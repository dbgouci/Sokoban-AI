import SKBMap

class SKBGame:
    """
    Runs the game.
    """

    def __init__(self, skb_data: str | list, history: list = []):
        """
        Loads a SKBMap.
        """
        self._map = SKBMap.SKBMap(skb_data)
        self._moves = self._get_moves()
        self._all_moves = self._get_all_moves()
        self._history = history.copy()
        self._heuristics = self._create_heuristics(self._map)

# Public definitions
    def display(self):
        """
        Prints a visualization of current board state on the terminal and displays choices.
        """
        self._map.display()
        for i, move in enumerate(self._moves):
            print(f'{i}: {move[2]}{move[1]}')

    @property
    def map(self):
        """
        Returns the SKBMap if needed for anything.
        """
        return self._map

    def history(self):
        """
        Returns a list of previous moves.
        """
        return self._history

    def win(self) -> int:
        """
        Returns 1 if won, 2 if dead end (lose), 0 if not yet determined.
        """
        storage_set = set(self._map.loc.storage)
        for box in self._map.loc.boxes:
            if box not in storage_set:
                if not self._moves:
                    return 2
                return 0
        return 1

    @property
    def heuristics(self):
        """
        Returns various heuristics.
        """
        return self._heuristics

    @property
    def choices_all(self) -> list:
        """
        Returns list of all boxes.
        """
        return self._all_moves
    
    @property
    def choices(self) -> list:
        """
        Returns list of pushable boxes.
        """
        return self._moves

    def pick(self, choice: int):
        """
        returns a new SKBGame updated by the pushable choices.
        """
        new_map = [layer[:] for layer in self._map.data] # Deep copy
        new_history = self._history[:] # Deep copy
        
        move = self._moves[choice]
        box = new_map[2][move[0]]
        direction = {'R': (0, 1), 'U': (-1, 0), 'L': (0, -1), 'D': (1, 0)}.get(move[1])
        new_history += self._map.moves[box][move[1]]
        new_map[2][move[0]] = tuple(x + y for x, y in zip(box, direction))
        new_map[4] = box
        new_game = SKBGame(new_map, new_history)
        return new_game

    def pick_all(self, choice: int):
        """
        returns a new SKBGame updated by any choice. Second parameter
        is 1 when valid, 0 when invalid.
        """
        new_map = [layer[:] for layer in self._map.data] # Deep copy
        new_history = self._history[:] # Deep copy
        valid = 0
        
        move = self._all_moves[choice]
        
        if self._map.moves[move[2]][move[1]]:
            box = new_map[2][move[0]]
            direction = {'R': (0, 1), 'U': (-1, 0), 'L': (0, -1), 'D': (1, 0)}.get(move[1])
            new_history += self._map.moves[box][move[1]]
            new_map[2][move[0]] = tuple(x + y for x, y in zip(box, direction))
            new_map[4] = box
            valid = 1
            
        new_game = SKBGame(new_map, new_history)
        return new_game, valid

# Private definitions
    def _get_moves(self):
        """
        Gets available boxes to push.
        """
        pushable = []
        for index, (box, push) in enumerate(self._map.moves.items()):
            for direction, path in self._map.moves[box].items():
                if self._map.moves[box][direction]:
                    pushable.append((index, direction, box))
        return pushable

    def _get_all_moves(self):
        """
        Gets all boxes to push.
        """
        boxes = []
        for index, (box, push) in enumerate(self._map.moves.items()):
            for direction, path in self._map.moves[box].items():
                boxes.append((index, direction, box))
        return boxes

    def _create_heuristics(self, skbmap):
        class _Heuristics:
            """
            Holds heuristic information about the board.
            """
            def __init__(self, skbmap):
                self._close = skbmap.close
                self._dead = skbmap.dead
            @property
            def close(self):
                return self._close
            @property
            def dead(self):
                return self._dead
        return _Heuristics(skbmap)