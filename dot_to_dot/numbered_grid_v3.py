"""Single-number points with explicit joins and border-only Sudoku addresses."""
from pathlib import Path
import json
import math
import random
from dot_to_dot.numbered_grid_v2 import sector, svg as previous_svg, print_book as previous_book

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/christmas-room-numbered-grid-v3'


def encode(path,labels):
    ops=[]
    for a,b in zip(path,path[1:]):
        if labels[b]==labels[a]+1:
            if ops and ops[-1]['kind']=='run':ops[-1]['count']+=1
            else:ops.append(dict(kind='run',count=1))
        else:ops.append(dict(kind='join',target=labels[b]))
    return ops


def decode(choice,inverse):
    label=choice['first'];result=[inverse[label]]
    for op in choice['ops']:
        if op['kind']=='run':
            result.extend(inverse[label+i] for i in range(1,op['count']+1))
            label+=op['count']
        else:
            label=op['target'];result.append(inverse[label])
    return result


def build_data():
    d=json.loads((ROOT/'runs/christmas-room-numbered-grid-v2/puzzle.json').read_text())
    rng=random.Random(18333);points=d['points'];real=d['real_paths']
    used=set();chains=[]
    for path in real:
        chain=[]
        for v in path:
            if v in used:
                if chain:chains.append(chain)
                chain=[]
            else:used.add(v);chain.append(v)
        if chain:chains.append(chain)
    real_nodes=set(used)
    free=set(range(len(points)))-used
    neighbours={v:[w for w in sorted(free) if v!=w and math.dist(points[v],points[w])<=3+1e-8] for v in sorted(free)}
    decoy_chains=[]
    while free:
        best=[]
        for _ in range(40):
            p=[rng.choice(sorted(free))];seen=set(p)
            while len(p)<100:
                options=[v for v in neighbours[p[-1]] if v in free and v not in seen]
                if not options:break
                v=rng.choice(options);p.append(v);seen.add(v)
            if len(p)>len(best):best=p
        free.difference_update(best);decoy_chains.append(best)
    chains+=decoy_chains;rng.shuffle(chains)
    labels=[0]*len(points);inverse=[None]
    for chain in chains:
        for v in chain:labels[v]=len(inverse);inverse.append(v)
    # Wrong answers mirror the correct run/join pattern, so a distinctive
    # join count does not identify the correct Sudoku digit in the lookup.
    def alternatives(ops):
        answers=[]
        def walk(node,oi,path):
            if oi==len(ops):return path
            op=ops[oi]
            if op['kind']=='run':
                ids=[inverse[k] for k in range(labels[node]+1,min(len(inverse),labels[node]+op['count']+1))]
                if len(ids)!=op['count'] or any(v in real_nodes for v in ids):return None
                if any(math.dist(points[a],points[b])>3+1e-8 for a,b in zip([node]+ids,ids)):return None
                return walk(ids[-1],oi+1,path+ids)
            options=[v for v in neighbours[node] if labels[v]!=labels[node]+1]
            rng.shuffle(options)
            for v in options:
                result=walk(v,oi+1,path+[v])
                if result:return result
            return None
        for v in rng.sample(sorted(neighbours),len(neighbours)):
            result=walk(v,0,[v])
            if result:answers.append(result)
            if len(answers)==8:return answers
        raise ValueError(f'Cannot make eight short-hop decoys with pattern {ops}; found {len(answers)}')
    instructions=[]
    for path,item in zip(real,d['instructions']):
        ops=encode(path,labels);wrong=iter(alternatives(ops));choices=[]
        for digit in range(1,10):
            nodes=path if digit==d['solution'][item['cell']] else next(wrong)
            choices.append(dict(digit=digit,first=labels[nodes[0]],sector=sector(points[nodes[0]]),
                                ops=encode(nodes,labels),nodes=nodes,length=len(nodes)-1))
        cell=item['cell']
        instructions.append(dict(id=item['id'],cell=cell,name=f'R{cell//9+1}C{cell%9+1}',choices=choices))
    correct=[i['choices'][d['solution'][i['cell']]-1] for i in instructions]
    joins=sum(sum(op['kind']=='join' for op in c['ops']) for c in correct)
    report={**d['report'],'printed_labels':len(points),'join_connections':joins,
            'consecutive_connections':331-joins,'instructions_with_joins':sum(any(op['kind']=='join' for op in c['ops']) for c in correct),
            'wrong_choices_match_run_join_pattern':True}
    report.pop('shortest_decoy_choice_pool',None)
    return {**d,'labels':labels,'inverse':inverse,'instructions':instructions,'report':report}


def op_text(op):
    return f'+{op["count"]}' if op['kind']=='run' else f'join {op["target"]}'


def op_lines(ops):
    lines=[];line=''
    for op in ops:
        token=op_text(op)
        if line and len(line+' · '+token)>18:lines.append(line);line=token
        else:line+=(' · ' if line else '')+token
    if line:lines.append(line)
    return lines


def print_book(d):
    # Reuse the established Sudoku print styling, with explicit page packing
    # for the now variable-length run/join entries.
    old=previous_book({**d,'instructions':[]})
    css=old[old.index('<style>')+7:old.index('</style>')]
    css+=' .lookup{font-size:11px}.lookup td div{line-height:14px;white-space:nowrap}.lookup th:first-child{width:67px}.sudoku th{font-size:12px}'
    grid='<table class="sudoku"><tr><th></th>'+''.join(f'<th>C{c}</th>' for c in range(1,10))+'</tr>'
    for r in range(9):grid+=f'<tr><th>R{r+1}</th>'+''.join(f'<td class="c{c} r{r}">{d["sudoku"][r*9+c] or ""}</td>' for c in range(9))+'</tr>'
    grid+='</table>'
    cover=f'<section class="page"><h1>Day 18 · single-number dots</h1><p>Solve the Sudoku, use its cell address and answer to look up a drawing instruction, then draw on the separate sheet.</p>{grid}<ol><li><b>Solve the Sudoku.</b> Read row and column labels from its borders: row 1, column 2 is <b>R1C2</b>. Every originally blank cell has one lookup row.</li><li><b>Find that cell in the lookup.</b> Rows are grouped R1–R9. Read across to the column headed by its solved digit.</li><li><b>Find the starting number in the drawing sector.</b> Drawing sectors A–F / 1–6 are separate from Sudoku addresses.</li><li><b>Follow the commands left to right.</b> <b>+6</b> means draw six consecutive-number connections. <b>join 127</b> means draw one line directly to dot 127. If another + command follows, continue counting from 127. Do not lift at a join.</li><li><b>Lift only at the end of the lookup entry.</b> Tick the row, then continue to the next blank Sudoku cell.</li></ol><p><b>Notation example:</b> E3 / 305 · +8 · join 127 · +2 means start at 305 in sector E3, connect through 313, connect directly to 127, then 128 and 129. Lift. This example is not an answer.</p><p>Every dot has one number. Joining a numbered point lets strokes meet without moving junctions or adding gaps. All connections, including joins, remain short.</p></section>'
    pages=[cover];blocks=[];height=75;current_row=None
    def header(r):return f'<h2>Sudoku row R{r+1}</h2><table class="lookup"><thead><tr><th>Cell</th>'+''.join(f'<th>{i}</th>' for i in range(1,10))+'</tr></thead><tbody>'
    def flush():
        nonlocal blocks,height,current_row
        if current_row is not None:blocks.append('</tbody></table>')
        pages.append('<section class="page"><h1>Lookup · single-number drawing</h1><p>Cell down the left → solved digit across the top. Entry: <b>sector / start</b>, then commands. Lift after the complete entry.</p>'+''.join(blocks)+'</section>')
        blocks=[];height=75;current_row=None
    for item in d['instructions']:
        r=item['cell']//9
        lines=[op_lines(c['ops']) for c in item['choices']]
        row_height=8+14*(1+max(map(len,lines)))
        extra=53 if r!=current_row else 0
        if height+extra+row_height>640 and blocks:flush();extra=53
        if r!=current_row:
            if current_row is not None:blocks.append('</tbody></table>')
            blocks.append(header(r));current_row=r
        cells=''.join('<td><div><b>'+c['sector']+'</b> / '+str(c['first'])+'</div>'+''.join('<div>'+line+'</div>' for line in ls)+'</td>' for c,ls in zip(item['choices'],lines))
        blocks.append(f'<tr><th>□ {item["name"]}</th>{cells}</tr>');height+=extra+row_height
    if blocks:flush()
    d['report']['lookup_pdf_pages']=len(pages)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Day 18 Sudoku and join lookup</title><style>'+css+'</style>'+''.join(pages)+'</html>'


def build():
    OUT.mkdir(parents=True,exist_ok=True);d=build_data()
    for mode in ('blank','connected','answer','original'):
        svg=previous_svg({**d,'labels':[[v,v] for v in d['labels']]},mode)
        # Exactly one visible text label per dot, with the same style everywhere.
        for v,label in enumerate(d['labels']):
            x,y=[100+t*36 for t in d['points'][v]]
            svg=svg.replace(f'<text x="{x}" y="{y+12}">{label}</text>','')
        (OUT/f'{mode}.svg').write_text(svg)
    (OUT/'lookup.html').write_text(print_book(d))
    (OUT/'puzzle.json').write_text(json.dumps(d,indent=2));(OUT/'report.json').write_text(json.dumps(d['report'],indent=2))
    (OUT/'index.html').write_text(Path(__file__).with_name('numbered_grid_v3.html').read_text().replace('__DATA__',json.dumps(d)))
    (OUT/'drawing.html').write_text('<!doctype html><meta charset="utf-8"><title>Day 18 drawing</title><style>@page{size:420mm 594mm;margin:10mm}body{font:14px Arial}img{width:380mm;height:380mm}</style><h1>Day 18 · single-number drawing</h1><p>Find starts in sectors A–F / 1–6. Follow + commands and explicit joins. Lift at the end of each lookup entry.</p><img src="blank.svg">')
    review=(ROOT/'runs/christmas-room-numbered-grid-v2/review.html').read_text().replace('numbered-grid feasibility','single-number join').replace('38 lookup rows','38 R/C lookup rows')
    (OUT/'review.html').write_text(review)
    print(json.dumps(d['report'],indent=2))


if __name__=='__main__':build()
