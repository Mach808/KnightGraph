"""
KnightGraph Graph Schema

Defines the complete graph representation used throughout the project.

Changing anything here changes the graph representation version.
"""

import chess

# ============================================================
# Schema Version
# ============================================================

SCHEMA_VERSION = "v1"

# ============================================================
# Piece Encoding
# ============================================================

PIECE_NAMES = {
    chess.PAWN: "Pawn",
    chess.KNIGHT: "Knight",
    chess.BISHOP: "Bishop",
    chess.ROOK: "Rook",
    chess.QUEEN: "Queen",
    chess.KING: "King",
}

PIECE_TO_ONEHOT = {
    chess.PAWN:   [1, 0, 0, 0, 0, 0],
    chess.KNIGHT: [0, 1, 0, 0, 0, 0],
    chess.BISHOP: [0, 0, 1, 0, 0, 0],
    chess.ROOK:   [0, 0, 0, 1, 0, 0],
    chess.QUEEN:  [0, 0, 0, 0, 1, 0],
    chess.KING:   [0, 0, 0, 0, 0, 1],
}

# ============================================================
# Node Feature Schema
# ============================================================

NODE_FEATURES = [
    "pawn",
    "knight",
    "bishop",
    "rook",
    "queen",
    "king",
    "color",
    "file",
    "rank",
]

NODE_FEATURE_DIM = len(NODE_FEATURES)

NODE_IDX = {
    "PAWN": 0,
    "KNIGHT": 1,
    "BISHOP": 2,
    "ROOK": 3,
    "QUEEN": 4,
    "KING": 5,
    "COLOR": 6,
    "FILE": 7,
    "RANK": 8,
}

# ============================================================
# Edge Feature Schema
# ============================================================

EDGE_FEATURES = {
    "attack": [1, 0],
    "defend": [0, 1],
}

EDGE_FEATURE_NAMES = [
    "attack",
    "defend",
]

EDGE_FEATURE_DIM = len(EDGE_FEATURE_NAMES)

EDGE_IDX = {
    "ATTACK": 0,
    "DEFEND": 1,
}

# ============================================================
# Graph-Level Features
# ============================================================

GRAPH_FEATURE_NAMES = [
    "side_to_move",
    "white_kingside_castle",
    "white_queenside_castle",
    "black_kingside_castle",
    "black_queenside_castle",
    "en_passant_available",
    "en_passant_file",
]

GRAPH_FEATURE_DIM = len(GRAPH_FEATURE_NAMES)

GRAPH_IDX = {
    "SIDE_TO_MOVE": 0,
    "WHITE_KINGSIDE": 1,
    "WHITE_QUEENSIDE": 2,
    "BLACK_KINGSIDE": 3,
    "BLACK_QUEENSIDE": 4,
    "EP_AVAILABLE": 5,
    "EP_FILE": 6,
}

# ============================================================
# Label
# ============================================================

LABEL_NAME = "white_advantage_centipawns"

# ============================================================
# Debug Utility
# ============================================================

def print_schema():

    print("=" * 60)
    print(f"KnightGraph Schema ({SCHEMA_VERSION})")
    print("=" * 60)

    print("\nNode Features")
    for i, feature in enumerate(NODE_FEATURES):
        print(f"{i:2d}: {feature}")

    print("\nEdge Features")
    for i, feature in enumerate(EDGE_FEATURE_NAMES):
        print(f"{i:2d}: {feature}")

    print("\nGraph Features")
    for i, feature in enumerate(GRAPH_FEATURE_NAMES):
        print(f"{i:2d}: {feature}")

    print("\nDimensions")
    print(f"Node Features : {NODE_FEATURE_DIM}")
    print(f"Edge Features : {EDGE_FEATURE_DIM}")
    print(f"Graph Features: {GRAPH_FEATURE_DIM}")


if __name__ == "__main__":
    print_schema()