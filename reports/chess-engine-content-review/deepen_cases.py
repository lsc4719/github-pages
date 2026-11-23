import sys,json,io,os
sys.path.insert(0,'engine-deps')
import chess,chess.engine,chess.pgn
from pathlib import Path
engine=chess.engine.SimpleEngine.popen_uci(os.environ.get('STOCKFISH_PATH','engine-deps/stockfish/stockfish-linux-x86-64-universal'))
engine.configure({'Threads':1,'Hash':128})
def line(board,pv,n=8):
 b=board.copy();out=[]
 for m in pv[:n]:
  prefix=str(b.fullmove_number)+('.' if b.turn else '...')
  out.append(prefix+b.san(m));b.push(m)
 return ' '.join(out)
def pack(info,b,color):
 s=info['score'].pov(color)
 return {'cp':s.score(mate_score=10000),'mate':s.mate(),'depth':info.get('depth'),'nodes':info.get('nodes'),'pv':[m.uci() for m in info.get('pv',[])[:10]],'line':line(b,info.get('pv',[]))}
allout=json.loads(Path('deep-cases.json').read_text()) if Path('deep-cases.json').exists() else []
for arg in sys.argv[1:]:
 idx,ply=map(int,arg.split(':'));g=json.loads(Path(f'engine-results/{idx}.json').read_text());m=g['moves'][ply-1];assert m['mine']
 b=chess.Board(m['fen']);color=b.turn;move=chess.Move.from_uci(m['uci'])
 engine.configure({'Clear Hash':None})
 infos=engine.analyse(b,chess.engine.Limit(nodes=2000000),multipv=3)
 best=[pack(i,b,color) for i in infos]
 after=b.copy();after.push(move)
 info=engine.analyse(after,chess.engine.Limit(nodes=2000000))
 played=pack(info,after,color)
 rec={'index':idx,'ply':ply,'url':g['url'],'opponent':g['opponent'],'result':g['result'],'color':g['color'],'fen':m['fen'],'san':m['san'],'uci':m['uci'],'clock_after':m['clock_after'],'best':best,'played':played,'loss':max(0,best[0]['cp']-played['cp'])}
 allout=[x for x in allout if (x['index'],x['ply'])!=(idx,ply)]
 allout.append(rec);print(json.dumps(rec,ensure_ascii=False),flush=True)
 Path('deep-cases.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2))
engine.quit()
