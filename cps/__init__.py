import numpy as np


COLORS = (WHITE, BLACK) = (0, 1)
PIECES = (PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING) = range(2, 8)
PIECE_NAMES = (None, None, "P", "N", "B", "R", "Q", "K")

FILE_NAMES = "abcdefgh"
RANK_NAMES = "12345678"
SQUARE_NAMES = [f + r for r in RANK_NAMES for f in FILE_NAMES]

BB_SQUARES = [1 << s for s in range(64)]
BB_FILES = [0x0101_0101_0101_0101 << s for s in range(8)]
BB_RANKS = [0x11 << s for s in range(8)]

CASTLING_SYMBOLS = "KQkq"

DEFAULT_STATE = np.array(
    [
        0x0000_0000_0000_FFFF,
        0xFFFF_0000_0000_0000,
        0x00FF_0000_0000_FF00,
        0x4200_0000_0000_0042,
        0x2400_0000_0000_0024,
        0x8100_0000_0000_0081,
        0x0800_0000_0000_0008,
        0x1000_0000_0000_0010,
    ],
    dtype=np.uint64,
)

STATE_FLAGS = (
    TURN := 0,
    CASTLING := 4,
    EP_STATUS := 8,
    EP_FILE := 12,
)

DEFAULT_STATE_FLAGS = 0b0000_0000_1111_0000


class State:
    def __init__(self, state_arr=DEFAULT_STATE, flags=DEFAULT_STATE_FLAGS) -> None:
        self._sarr = state_arr
        self._flags = flags

    def next(self, move: str):
        turn = self._flags & 1
        castling = 0b0011 << (2 * turn)

        new_sarr = self._sarr.copy()
        new_flags = self._flags ^ (1 << TURN | ~(1 << EP_STATUS))

        if move[0] == "O":
            new_flags ^= castling << CASTLING
            long = len(move) >= 5

            kfrom = 0x10 << (56 * turn)
            rfrom = (0x1 if long else 0x80) << (56 * turn)

            kto = kfrom >> (2 if long else -1)
            rto = rfrom << (3 if long else -2)

            new_sarr[KING] ^= np.uint64(kfrom | kto)
            new_sarr[ROOK] ^= np.uint64(rfrom | rto)
            new_sarr[turn] ^= np.uint64(kfrom | rfrom | kto | rto)
            return State(new_sarr, new_flags)

        m = []
        idx = 0
        for p in (
            "NBRQK",
            "abcdefgh",
            "12345678",
            "x",
            "abcdefgh",
            "12345678",
            "NBRQ",
        ):
            m.append(move[idx] if move[idx] in p else None)

        piece = PAWN
        if m[0]:
            piece = PIECE_NAMES.index(m[0])

        to_sq = BB_SQUARES[SQUARE_NAMES.index(m[4] + m[5])]

        capture = bool(m[3])
        promotion = PIECE_NAMES.index(m[6]) if m[6] else None

        if promotion and capture:
            from_sq = BB_FILES[FILE_NAMES.index(m[1])] & BB_RANKS[6]
            new_sarr[piece] ^= from_sq
            new_sarr[promotion] ^= to_sq
            new_sarr[turn] ^= from_sq | to_sq

            new_sarr[new_sarr & to_sq != 0] ^= to_sq

    def __repr__(self) -> str:
        turn = self._flags & 1 << TURN
        fmt_str = "\n  |{:^15}"

        s = "   A B C D E F G H\n"
        s += "   _______________\n"

        for rank in range(7, -1, -1):
            s += RANK_NAMES[rank] + " |"

            for file in range(8):
                sq = BB_SQUARES[rank * 8 + file]
                idx = np.nonzero(self._sarr & sq != 0)[0]

                if any(idx):
                    color, piece = idx
                    symbol = PIECE_NAMES[piece]
                    if color:
                        symbol = symbol.lower()

                    s += symbol + " "

                else:
                    s += ". "
            s += "\n"

        s += fmt_str.format(f"turn: {'black' if turn else 'white'}")

        s += fmt_str.format(
            f"castling: {''.join([CASTLING_SYMBOLS[i] for i in range(4) if self._flags & (1 << CASTLING + i)])}"
        )

        ep_square = 8 * (4 if turn else 3) + self._flags >> EP_FILE
        s += fmt_str.format(
            f"en passant: {SQUARE_NAMES[ep_square] if self._flags & 1 << EP_STATUS else '-'}"
        )

        return s

if __name__ == '__main__':
    state = State()
    state._sarr[KNIGHT] = 0x4200_0000_0000_0040
    state._sarr[BISHOP] = 0x2400_0000_0000_0020
    state._sarr[QUEEN]  = 0x0800_0000_0000_0000
    state._sarr[WHITE]  = 0x0000_0000_0000_FFF1
    state = state.next('O-O-O')
    print(state)

