# KnightGraph

KnightGraph is an experimental chess engine. It represents positions as graphs, trains a Graph Neural Network (GNN) to evaluate them, and uses alpha-beta search to choose moves.

## The project in one diagram

```text
PGN -> sampled FENs -> Stockfish labels -> PyG graphs -> GINE model -> alpha-beta -> best move/UCI
```

The current repository contains a working research prototype of this complete flow.

## Repository layout

```text
dataset/
  generate_positions.py    Sample positions from PGN games
  label_positions.py       Evaluate FENs with Stockfish
  build_dataset.py         Create train/validation graph files
  dup_positions.py         Remove duplicate FENs
  test_games.py            Stockfish smoke test
graph/
  graph_schema.py          Feature names and dimensions
  node_features.py         Convert pieces into graph nodes
  edge_builder.py          Build attack/defense edges
  graph_builder.py         Create PyTorch Geometric graphs
models/
  gine.py                  GINE position evaluator
  train.py                 Train and save the model
  evaluate.py              Measure validation loss
engine/
  minimax.py               Alpha-beta, iterative deepening, quiescence
  play.py                  Search one position from the terminal
  uci.py                   Basic UCI protocol adapter
tests/validate_graphs.py   Graph validation examples
stockfish/stockfish.exe    Local Stockfish executable
```

## Installation

From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The default Stockfish path is `stockfish/stockfish.exe`. Another executable can be supplied to the labeling script.

## End-to-end workflow

### 1. Generate positions

The repository includes a PGN file in `dataset/raw/`. Generate 100 games with 10 positions per game:

```powershell
python -m dataset.generate_positions `
  --pgn dataset/raw/lichess_db_standard_rated_2014-01.pgn `
  --max-games 100 `
  --positions-per-game 10 `
  --output positions_100games.csv
```

The output CSV contains FEN, game and position IDs, ply progress, material, phase, result, ratings, ECO, and opening name. Opening, middlegame, and endgame positions are sampled separately. Terminal positions are skipped.

For a small test, use `--max-games 5 --output positions.csv`.

### 2. Label positions with Stockfish

```powershell
python -m dataset.label_positions `
  --input positions_100games.csv `
  --output positions_100games_labeled.csv `
  --depth 4 `
  --mate-score 1000 `
  --clip-score 1000
```

This adds `white_advantage_centipawns`. Positive values favor White; negative values favor Black. Mate and extreme values are clipped to ±1000 to prevent a few mate positions from dominating training. Increase `--depth` for stronger but slower labels.

### 3. Build graph files

```powershell
python -m dataset.build_dataset `
  --input positions_100games_labeled.csv `
  --output-dir dataset/graphs_100games `
  --val-fraction 0.2
```

This creates `dataset/graphs_100games/train.pt` and `dataset/graphs_100games/val.pt`. The split is by `game_id`, preventing positions from one game leaking into both sets.

### 4. Train and evaluate the GNN

```powershell
python -m models.train `
  --data-dir dataset/graphs_100games `
  --epochs 15 `
  --batch-size 64 `
  --output models/gine_100games.pt

python -m models.evaluate `
  --data dataset/graphs_100games/val.pt `
  --model models/gine_100games.pt
```

The current local experiment used about 1,000 positions and achieved about 278 centipawns validation RMSE. This validates the pipeline, not competitive playing strength.

## Graph representation

Every occupied square becomes one node; empty squares are not nodes.

Node features have 9 values:

```text
[pawn, knight, bishop, rook, queen, king, color, file, rank]
```

The first six values are piece one-hot encoding. White is `1`, Black is `0`, and file/rank are normalized to `[0, 1]`.

Edges are directed between occupied pieces that attack or defend one another:

```text
attack = [1, 0]
defend = [0, 1]
```

Graph-level features have 7 values:

```text
[side_to_move, white_kingside_castle, white_queenside_castle,
 black_kingside_castle, black_queenside_castle,
 en_passant_available, en_passant_file]
```

These definitions are centralized in `graph/graph_schema.py`.

## Model

`models/gine.py` uses two edge-aware GINE convolution layers. It mean-pools piece nodes, concatenates the seven graph-level features, and regresses one White-perspective centipawn score. It predicts evaluations, not moves.

## Search

`engine/minimax.py` provides White-perspective minimax, alpha-beta pruning, iterative deepening, time limits, capture/promotion/check move ordering, transposition caching, quiescence search, and terminal checkmate/draw handling.

Search one position:

```powershell
python -m engine.play --model models/gine_100games.pt --depth 2
```

Search for up to five seconds with iterative deepening:

```powershell
python -m engine.play --model models/gine_100games.pt --depth 6 --time 5
```

Search a custom FEN:

```powershell
python -m engine.play `
  --model models/gine_100games.pt `
  --fen "r1bqk2r/pppp1ppp/2n2n2/4p3/4P3/1B3N2/PPPP1PPP/RNBQ1RK1 w kq - 2 5" `
  --depth 3
```

Example output:

```text
best_move=a2a3 score=29.78 nodes=314
```

## UCI usage

Start the UCI adapter:

```powershell
python -m engine.uci --model models/gine_100games.pt
```

Then type:

```text
uci
isready
position startpos
go movetime 5000
```

For a custom position:

```text
position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
go depth 2
```

The engine returns `bestmove <uci-move>`. A GUI can launch it with Python as the executable, `-m engine.uci --model D:\code\KnightGraph\models\gine_100games.pt` as arguments, and `D:\code\KnightGraph` as the working directory.

Supported UCI commands are `uci`, `isready`, `ucinewgame`, `position`, `go depth`, `go movetime`, and `quit`.

## Validation

Run graph examples:

```powershell
$env:PYTHONPATH='.'
python -m tests.validate_graphs
```

Run syntax checks:

```powershell
python -m py_compile dataset/*.py graph/*.py models/*.py engine/*.py
```

Test the UCI handshake:

```powershell
@('uci','isready','position startpos','go depth 1','quit') |
  python -m engine.uci --model models/gine_100games.pt
```

## Current limitations

This is not yet a competitive engine. The dataset is small and labels are shallow. The graph does not explicitly encode empty-square mobility, legal moves, checks, pins, threats, or rich move history. Search is slow because every leaf requires graph construction and GNN inference. UCI is minimal and does not yet support asynchronous `stop`, engine options, ponder mode, or complete clock management. There is no opening book, endgame tablebase, or handcrafted fallback evaluator.

## Recommended next improvements

1. Generate many more positions with randomized game-level splits.
2. Use stronger Stockfish labels.
3. Add legal-move, mobility, check, pin, and threat features.
4. Add MAE, sign accuracy, and calibration metrics.
5. Batch and cache graph inference during search.
6. Add stronger transposition-table bounds, killer moves, and history heuristics.
7. Implement asynchronous UCI `stop` and proper clock management.
8. Add unit tests for FEN encoding, score perspective, terminal handling, and search legality.
