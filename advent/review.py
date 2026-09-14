"""A solved contact sheet for reviewing all 25 daily focal details."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
SUBJECTS=['Robin on a branch','Hanging Christmas bells','Dove in flight','Crescent moon and cloud','Hanging pine cone',
          'Snow-roofed cottage','Cottage and clock tower','Dormer cottage','Chapel window','Village houses',
          'Cottage beside the tree','Front-door wreath','Street lantern','Cottage windows','Snowy rooftop',
          'Bauble on the Christmas tree','Snowman in a scarf','Market stall','Winter market wares','Market and fir tree',
          'Wrapped gifts','Present-laden sleigh','Duck by the stream','Rabbit on the snowbank','Owl on a branch']
def write_review(out):
    out=Path(out);sheet=Image.new('RGB',(1600,1780),'#f3f1e9');draw=ImageDraw.Draw(sheet)
    rows=[]
    for i,subject in enumerate(SUBJECTS):
        r,c=divmod(i,5);x=c*320;y=r*356
        src=Image.open(out/f'day-{i+1:02}'/'source.png').crop((100,100,1100,1100)).resize((308,308))
        sheet.paste(src,(x+6,y+6));draw.text((x+9,y+320),f'{i+1}. {subject}',font=ImageFont.load_default(size=13),fill='#203a37')
        rows.append(f'<a href="day-{i+1:02}/index.html"><img src="day-{i+1:02}/source.svg" alt="Completed day {i+1}"><span>{i+1}. {subject}</span></a>')
    sheet.save(out/'tile-review.png')
    (out/'tile-review.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Daily artwork review</title><style>body{font:14px system-ui;background:#f3f1e9;color:#203a37;margin:20px}main{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}a{color:inherit;text-decoration:none}main a{background:white;padding:8px}img{width:100%;display:block}span{display:block;padding:8px}@media(max-width:700px){main{grid-template-columns:repeat(2,1fr)}}</style><p><a href="index.html">← Calendar</a></p><h1>One focal detail per day</h1><p>Completed tiles for artwork review. These captions are spoilers; daily puzzles open unsolved without subject names.</p><main>'+''.join(rows)+'</main>')
