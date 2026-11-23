"""Reanalyse the supplied completed games with Stockfish 19.

Install: python -m pip install python-chess==1.999
Run: python reproduce.py /absolute/path/to/stockfish
Output: reanalysis.json (not Chess.com accuracy or blunder labels).
The report's deeper representative cases use 1,000,000 nodes per position.
"""
import sys, json, pathlib
import chess, chess.pgn, chess.engine

root = pathlib.Path(__file__).resolve().parent
engine = chess.engine.SimpleEngine.popen_uci(sys.argv[1])
engine.configure({'Threads': 1, 'Hash': 64})
rows = []
try:
    with (root / 'sample-games.pgn').open() as source:
        while (game := chess.pgn.read_game(source)) is not None:
            color = game.headers['White'].lower() == 'seungkeon543'
            engine.configure({'Clear Hash': None})
            nodes = [game] + list(game.mainline())
            evaluations = []
            infos = []
            for node in nodes:
                board = node.board()
                if board.is_game_over():
                    result = -10000 if board.is_checkmate() and board.turn == color else 10000 if board.is_checkmate() else 0
                    info = {'pv': [], 'depth': 0}
                else:
                    info = engine.analyse(board, chess.engine.Limit(nodes=30000))
                    result = info['score'].pov(color).score(mate_score=10000)
                evaluations.append(result)
                infos.append(info)
            turns = []
            previous_clock = 600
            for i, node in enumerate(nodes[1:]):
                board = node.parent.board()
                if board.turn != color:
                    continue
                clock = node.clock()
                spent = round(previous_clock - clock, 1) if clock is not None else None
                if clock is not None:
                    previous_clock = clock
                before, after = evaluations[i:i+2]
                pv = infos[i]['pv']
                turns.append({'ply': i+1, 'move': board.fullmove_number,
                              'san': board.san(node.move), 'uci': node.move.uci(),
                              'fen': board.fen(), 'before': before, 'after': after,
                              'loss': max(0, before-after),
                              'best': board.san(pv[0]) if pv else '',
                              'pv': board.variation_san(pv[:5]) if pv else '',
                              'clock': clock, 'spent': spent, 'depth': infos[i].get('depth')})
            rows.append({'url': game.headers.get('Link'), 'color': 'white' if color else 'black', 'turns': turns})
            print(len(rows), game.headers.get('Link'), flush=True)
    (root / 'reanalysis.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
finally:
    engine.quit()
