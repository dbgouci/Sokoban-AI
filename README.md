Get dependencies using:

`pip install -r {path to requirements.txt}`

## SKBMap.py Usage

#### SKBMap.display()
Prints a visualization of current board state on the terminal.
```
map = SKBMap('sokoban01.txt')
map.display()
```

#### SKBMap.moves
Returns a dictionary of boxes, which contains a dictionary of directions, which contains a list of inputs (including the pushing of the box).
This is a property, so parenthesis are not needed.
```
map = SKBMap('sokoban01.txt')
print(map.moves) # This is a property, so no need to add parenthesis
```
```
Content of map.moves:

map.moves
|
|--- (X, X) # Tuple location of box, will always have the four directions regardless if they can be pushed or not
     |
     |--- 'U': ['U', 'R', 'U'] # NOTE: the last move is the pushing of the box
     |
     |--- 'R': [] # If a path cannot be found, it will be empty
     |
     |--- 'D': []
     |
     |--- 'L': []
|
|--- (X, Y)
     ...
|
|--- (Y, X)
     ...
...
```

#### SKBMap.data
A list of stuff. Mainly used for deep copying. Also a property.
```
map1 = SKBMap('sokoban01.txt')
map2 = SKBMap(map1.data)
```

#### SKBMap.loc.{something}
Returns current locations of stuff on the board in the form of a tuple.
```
map = SKBMap('sokoban01.txt')
print(map.loc.boxes)
print(map.loc.storage)
print(map.loc.player)
```

#### SKBMap.size.{something}
Returns aggregated board data.
```
map = SKBMap('sokoban01.txt')
print(map.size.walls)
print(map.size.boxes)
print(map.size.storage)
print(map.size.bounds)
```
