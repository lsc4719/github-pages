import os,sys,json,io,time,datetime
sys.path.insert(0,'engine-deps')
import chess,chess.pgn,chess.engine
from pathlib import Path
# Run beside analysis-data.json and sample-games.pgn. Requires python-chess==1.999.
# Set STOCKFISH_PATH to the official Stockfish 19 executable.
metadata=json.load(open('analysis-data.json'))['games']
selected=[]
with open('sample-games.pgn') as pgn_file:
 for row in metadata:
  parsed=chess.pgn.read_game(pgn_file)
  assert parsed is not None
  mine=row['color'];other='black' if mine=='white' else 'white'
  g={'pgn':str(parsed),'url':row['url'],'end_time':int(datetime.datetime.fromisoformat(row['end_time_kst']).timestamp())}
  g[mine]={'username':'lsc4719','rating':row['rating'],'result':row['result']}
  g[other]={'username':row['opponent'],'rating':int(parsed.headers['BlackElo' if mine=='white' else 'WhiteElo']),'result':'not_used'}
  selected.append((row['index'],g))
engine=chess.engine.SimpleEngine.popen_uci(os.environ.get('STOCKFISH_PATH','engine-deps/stockfish/stockfish-linux-x86-64-universal'))
engine.configure({'Threads':1,'Hash':64})
Path('engine-results').mkdir(exist_ok=True)
print(engine.id, 'games',len(selected),flush=True)
for idx,g in selected:
 outpath=Path(f'engine-results/{idx}.json')
 if outpath.exists():continue
 game=chess.pgn.read_game(io.StringIO(g['pgn']))
 assert not game.errors,game.errors
 color=chess.WHITE if g['white']['username'].lower()=='lsc4719' else chess.BLACK
 board=game.board();engine.configure({'Clear Hash':None})
 evaluations=[];moves=[]
 def evaluate(b):
  if b.is_game_over():return {'cp':0 if not b.is_checkmate() else (-10000 if b.turn==color else 10000),'mate':-1 if b.turn==color and b.is_checkmate() else 1 if b.is_checkmate() else None,'pv':[],'depth':0}
  info=engine.analyse(b,chess.engine.Limit(nodes=20000))
  s=info['score'].pov(color)
  return {'cp':s.score(mate_score=10000),'mate':s.mate(),'pv':[m.uci() for m in info.get('pv',[])[:8]],'depth':info.get('depth'),'nodes':info.get('nodes')}
 evaluations.append(evaluate(board))
 for ply,node in enumerate(game.mainline(),1):
  move=node.move;mine=board.turn==color
  rec={'ply':ply,'san':board.san(move),'uci':move.uci(),'fen':board.fen(),'mine':mine,'clock_after':node.clock()}
  board.push(move);evaluations.append(evaluate(board));rec['before']=evaluations[-2];rec['after']=evaluations[-1];rec['loss']=max(0,rec['before']['cp']-rec['after']['cp']) if mine else None
  moves.append(rec)
 p=g['white' if color else 'black'];o=g['black' if color else 'white']
 out={'index':idx,'group':'before' if idx<=379 else 'rise','url':g['url'],'end_time':g['end_time'],'color':'white' if color else 'black','rating':p['rating'],'result':p['result'],'opponent':o['username'],'opponent_rating':o['rating'],'opponent_result':o['result'],'moves':moves}
 outpath.write_text(json.dumps(out,ensure_ascii=False))
 print(idx,out['group'],out['result'],len(moves),'plies',flush=True)
engine.quit()
