import SKBMap
from IPython.display import clear_output
import time

class SKBView:
    """
    Animates a valid sokoban solution.
    """
    
    def __init__(self, skbmap: str, history: list[str]):
        """
        Load a txt sokoban file and a list of moves
        """
        self._skbmap = SKBMap.SKBMap(skbmap)
        self._history = history

# Public definitions
    def play(self, speed: float = 0.1):
        """
        Prints an animated visualization of the sokoban
        solution on the terminal. Can set the speed in
        seconds. (default is 0.1 sec)
        """
        for move in self._history:
            clear_output(wait=True)
            self._skbmap.display()
            self._update(move)
            time.sleep(speed)
        clear_output(wait=True)
        self._skbmap.display()

#Private definitions
    def _update(self, direction: str):
        """
        Updates a single move to the map. Takes into
        account the player and any boxes moved, but
        nothing else.
        """
        new_skbmap = [layer[:] for layer in self._skbmap.data]
        player_move = {'R': (0, 1), 'U': (-1, 0), 'L': (0, -1), 'D': (1, 0)}.get(direction)
        new_skbmap[4] = tuple(x + y for x, y in zip(self._skbmap.data[4], player_move))
        for i, box in enumerate(new_skbmap[2]):
            if new_skbmap[4] == box:
                new_skbmap[2][i] = tuple(x + y for x, y in zip(new_skbmap[2][i], player_move))
        self._skbmap = SKBMap.SKBMap(new_skbmap)
        
if __name__ == '__main__':
    skbmap_txt = 'sokoban05a.txt'
    history = ['U', 'U', 'U', 'R', 'R', 'R', 'R', 'U', 'U', 'L', 'L', 'D', 'U',
               'R', 'R', 'D', 'D', 'L', 'D', 'L', 'U', 'R', 'R', 'R', 'D', 'L',
               'U', 'U', 'U', 'L', 'L', 'D', 'D', 'D', 'D', 'U', 'R', 'U', 'R',
               'R', 'D', 'L', 'U', 'L', 'L', 'D', 'D', 'L', 'D', 'R', 'U', 'U',
               'U', 'R', 'R', 'D', 'L', 'U', 'L', 'L', 'D', 'D', 'R', 'D', 'R',
               'L', 'U', 'L', 'U', 'U', 'R', 'D', 'L', 'D', 'D', 'R', 'R', 'R',
               'L', 'L', 'L', 'U', 'U', 'R', 'D', 'L', 'D', 'R', 'R']
    view = SKBView(skbmap_txt, history)
    view.play()