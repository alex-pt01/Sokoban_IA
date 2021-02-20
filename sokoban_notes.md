#### Sokoban Notes

- Player at x,y location
- Boxes and target stores
- The player can move horizontally or vertically (four directions - Up, Down,Left and Right). 
- The player can push at most a single box into an empty space that **is not a wall or another box.** 
- The player is not allowed to pull the boxes too.
- The player fails if a crate gets locked up in a corner or with another crate with the storage locations(or location) being unoccupied. (DEADLOCK)



- Start Stage: fornecido pelo programador;

- Goal stage: quando tds as caixas estiverem no lugar;

- Actions: Tds as direções com um custo associado 

  

- Moves are irreversible so making a bad move can make you lose the game.

- - Fatores para um bom algoritmo de pesquisa:

  - Algoritmo capaz de produzir um reduzido numero de movimentos;
  - Existem walls que restringem o caminho do player;
  - Podemos ter infinitas pesquisas em profundidade...

#### DFS

- Pára a pesquisa assim que o goal é alcançado.
- Pior caso: a complexidde espacial e temporal são as mesmas que o caso base;
- Oferece prioridade à máx. 
- Falha em níveis maiores;

#### BFS

- Existem muitos estados, logo a compleidade será muito grande.

#### UCS

- Consiste em termos uma priority queue onde o caminho da raiz até ao node é o elemento armazenado e a profundidade até um determinado node atua como sendo a prioridade.

- Tds os custos são positivos;

  