import argparse
import chess
import chess.pgn
from dataclasses import dataclass
import random
import csv

random.seed(42)

OPENING_PERCENT = 0.20
ENDGAME_MATERIAL = 24


@dataclass
class Position:
    ply: int
    fen: str

    progress: float = 0.0
    material: int = 0
    phase: str = ""

    game_id: int = 0

def compute_material(board: chess.Board) -> int:
    """
    Total remaining non-pawn material.
    Kings and pawns are ignored.
    """

    piece_values = {
        chess.QUEEN: 9,
        chess.ROOK: 5,
        chess.BISHOP: 3,
        chess.KNIGHT: 3,
    }

    total = 0

    for piece_type, value in piece_values.items():
        total += len(board.pieces(piece_type, chess.WHITE)) * value
        total += len(board.pieces(piece_type, chess.BLACK)) * value

    return total

def classify_phase(progress: float, material: int) -> str:

    if material <= ENDGAME_MATERIAL:
        return "endgame"

    if progress < OPENING_PERCENT:
        return "opening"

    return "middlegame"

def replay_game(game: chess.pgn.Game) -> tuple[list[Position], int]:

    """
    Replay a PGN game and return all non-terminal positions.
    """

    board = game.board()

    positions: list[Position] = []
    ply = 0

    for move in game.mainline_moves():

        board.push(move)
        ply += 1

        # Skip terminal positions
        if (
            board.is_checkmate()
            or board.is_stalemate()
            or board.is_insufficient_material()
        ):
            continue

        positions.append(
            Position(
                ply=ply,
                fen=board.fen()
            )
        )

    return positions, ply

def board_from_position(position: Position) -> chess.Board:
    """
    Reconstruct a chess.Board from a stored position.
    """
    return chess.Board(position.fen)

def enrich_positions(
    positions: list[Position],
    total_plies: int,
) -> None:

    for position in positions:

        board = board_from_position(position)

        position.progress = position.ply / total_plies

        position.material = compute_material(board)

        position.phase = classify_phase(
            position.progress,
            position.material,
        )

def print_game_summary(
    game_number: int,
    headers,
    positions: list[Position],
    total_plies: int,
    game: chess.pgn.Game,
):

    print("=" * 70)
    print(f"Game {game_number}")
    print("=" * 70)

    print(f"White            : {headers.get('White')}")
    print(f"Black            : {headers.get('Black')}")
    print(f"White Elo        : {headers.get('WhiteElo')}")
    print(f"Black Elo        : {headers.get('BlackElo')}")
    print(f"Result           : {headers.get('Result')}")
    print(f"ECO              : {headers.get('ECO')}")
    print(f"Opening          : {headers.get('Opening')}")

    print()

    print(f"Total Plies      : {total_plies}")
    print(f"Sampled Positions : {len(positions)}")


    opening = sum(p.phase == "opening" for p in positions)
    middlegame   = sum(p.phase == "middlegame" for p in positions)
    endgame = sum(p.phase == "endgame" for p in positions)

    print()
    print("Phase Distribution")
    print(f"Opening    : {opening}")
    print(f"Middlegame : {middlegame}")
    print(f"Endgame    : {endgame}")

    if positions:

        print("\nEarliest Sampled Position")
        print(positions[0].fen)

        print("\nLast Position")
        print(positions[-1].fen)

        print("\nSample Features")
        print("--------------------------------------")

        first = positions[0]
        last = positions[-1]

        print(
            f"First : Ply={first.ply}, "
            f"Progress={first.progress:.2f}, "
            f"Material={first.material}, "
            f"Phase={first.phase}"
        )

        print(
            f"Last  : Ply={last.ply}, "
            f"Progress={last.progress:.2f}, "
            f"Material={last.material}, "
            f"Phase={last.phase}"
        )

    board = game.board()

    for move in game.mainline_moves():
        board.push(move)

    print("\nFinal Board")
    print(board)

    print("\nTerminal Status")

    print(f"Checkmate             : {board.is_checkmate()}")
    print(f"Stalemate             : {board.is_stalemate()}")
    print(f"Insufficient Material : {board.is_insufficient_material()}")

    print()

def bucket_positions(
    positions: list[Position],
) -> tuple[list[Position], list[Position], list[Position]]:

    opening: list[Position] = []
    middlegame: list[Position] = []
    endgame: list[Position] = []

    for position in positions:

        if position.phase == "opening":
            opening.append(position)

        elif position.phase == "middlegame":
            middlegame.append(position)

        else:
            endgame.append(position)

    return opening, middlegame, endgame

def sample_bucket(
    bucket: list[Position],
    count: int,
) -> list[Position]:

    if len(bucket) <= count:
        return bucket.copy()

    return random.sample(bucket, count)

def sample_positions(
    positions: list[Position],
) -> list[Position]:

    opening, middlegame, endgame = bucket_positions(positions)

    sampled = []

    sampled.extend(sample_bucket(opening, 1))
    sampled.extend(sample_bucket(middlegame, 2))
    sampled.extend(sample_bucket(endgame, 2))

    # Fill any remaining slots (up to 5 total)
    remaining = 5 - len(sampled)

    if remaining > 0:

        used = {p.fen for p in sampled}

        leftovers = [
            p
            for p in positions
            if p.fen not in used
        ]

        if len(leftovers) <= remaining:
            sampled.extend(leftovers)
        else:
            sampled.extend(
                random.sample(leftovers, remaining)
            )

    sampled.sort(key=lambda p: p.ply)

    return sampled

def write_positions_csv(
    writer,
    positions: list[Position],
    game_id: int,
    headers,
    total_plies: int,
) -> None:

    for i, position in enumerate(positions):

        writer.writerow({
            "game_id": game_id,
            "position_id": f"{game_id}_{position.ply}",
            "fen": position.fen,
            "ply": position.ply,
            "total_plies": total_plies,
            "progress": round(position.progress, 4),
            "material": position.material,
            "phase": position.phase,

            "result": headers.get("Result"),
            "white_elo": int(headers["WhiteElo"]),
            "black_elo": int(headers["BlackElo"]),
            "eco": headers.get("ECO"),
            "opening": headers.get("Opening"),
        })

def main():

    parser = argparse.ArgumentParser(
        description="Generate KnightGraph positions from PGN."
    )

    parser.add_argument(
        "--pgn",
        type=str,
        required=True,
        help="Path to PGN file",
    )

    parser.add_argument(
        "--max-games",
        type=int,
        default=10,
        help="Maximum number of games to process",
    )

    args = parser.parse_args()

    fieldnames = [
        "game_id",
        "position_id",
        "fen",
        "ply",
        "total_plies",
        "progress",
        "material",
        "phase",
        "result",
        "white_elo",
        "black_elo",
        "eco",
        "opening",
    ]

    with open(
        "positions.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
        )

        writer.writeheader()

        with open(
            args.pgn,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as pgn:

            game_count = 0

            while game_count < args.max_games:

                game = chess.pgn.read_game(pgn)

                if game is None:
                    break

                game_count += 1

                # Replay game
                positions, total_plies = replay_game(game)

                # Compute features
                enrich_positions(
                    positions,
                    total_plies,
                )

                # Sample positions
                positions = sample_positions(positions)

                # Save sampled positions
                write_positions_csv(
                    writer,
                    positions,
                    game_count,
                    game.headers,
                    total_plies,
                )

                # Optional: keep while debugging
                print_game_summary(
                    game_count,
                    game.headers,
                    positions,
                    total_plies,
                    game,
                )

            print(f"\nFinished processing {game_count} game(s).")
            print("Saved sampled positions to positions.csv")




if __name__ == "__main__":
    main()