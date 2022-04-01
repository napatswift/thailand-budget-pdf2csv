import numpy as np
import re

def to_gregorian(input):
  if input:
    return int(input) - 543
  return input

def isthaichar(string):
  return len(string) - len([c for c in string if 3585 <= ord(c) < 3676])

def tn_to_arb(line):
  fline = ''
  for char in line:
    if ord(char) >= ord('๐') and ord(char) <= ord('๙'):
      fline += str(ord(char) - ord('๐'))
    else:
      fline += char
  return fline

def get_patern_of_bullet(String):
  regx = [('[1-9][0-9]*(\.[1-9][0-9]*)*\)$', 20),
   ('\(\d*(\.?\d*)*\)$', 50),
   ('[1-9][0-9]*(\.[1-9][0-9]*)+$', 2),
   ('[1-9][0-9]*\.$', 1),
   ('[1-9][0-9]*$', 30)]

  for r, l in regx:
    if re.match(r, String):
      if l in [2, 20, 50]:
        l = String.count('.') + l
      return r, l
  return 0

def mode(lst):
  if isinstance(lst, np.ndarray):
    lst = lst.tolist()
  return max(set(lst), key=lst.count)

def getBlock(blocks):
  cleanedBlocks = []
  allNormalizedVertices = []

  for block in blocks:
    for paragraph in block['paragraphs']:
      for word in paragraph['words']:   

        text = []
        for symbol in word['symbols']:
          symbol.pop('confidence', None)
          text.append(symbol['text'])
          if 'property' in symbol.keys() and 'detectedBreak' in symbol['property'].keys():
            text.append(' ')
        
        vertices = word['boundingBox']['normalizedVertices']
        normalizedVertices = [(v['x'], v['y']) for v in vertices]
        
        allNormalizedVertices.append(normalizedVertices)
        
        cleanedBlocks.append({
          'normalizedVertices': normalizedVertices,
          # 'symbols': word['symbols'],
          'baseLine': np.max(normalizedVertices, axis=0).tolist(),
          'text': ''.join(text)
        })
  return cleanedBlocks, allNormalizedVertices

def blocksInLine(dix, page, contained):
  line = []
  
  for ii in dix:
    # if block is contained then skip
    if contained[ii]: continue
    line.append(page[ii])
    contained[ii] = True

  line.sort(key=lambda b: np.mean(b['normalizedVertices'], axis=0)[0].mean())
  text = [block['text'] for block in line]

  return {'blocks': line, 'text': ''.join(text)}

def lineInPage(page, BaseLines):
  # TODO: https://stackoverflow.com/a/48277234/15538794
  pageBaseLine = BaseLines[:, :, 1].mean(axis=1)
  contained = np.zeros(pageBaseLine.size, dtype=bool)
  lines = []
  text = ''
  for ii in range(pageBaseLine.size):
    # if contained then skip
    if (contained[ii]): continue
    # calculate the line diff
    lineDiff = np.abs(pageBaseLine-pageBaseLine[ii])/pageBaseLine[ii]
    # get index of boxes that has diff less than 3 percents
    dix = np.argwhere(lineDiff <= .01).reshape(-1)
    blocks = blocksInLine(dix, page, contained)
    text += blocks['text']
    lines.append(blocks)

  lines.sort(key=lambda line: np.mean([block['normalizedVertices'][2][1] for block in line['blocks']]))
  return {'lines': lines, 'text': text}

def printPage(doc, pageNum):
  for line in doc[pageNum]:
    print(line['text'])
  print('------')

# with open('alllinesinpages_filtered.json', 'w') as f:
#     json.dump(pagesLines, f, ensure_ascii=False)

# xy = []
# for baseL in BaseLines:
#     if len(xy) == 0:
#         xy = baseL.max(axis=1)
#     else:
#         diff = xy.max(axis=0)[0]-baseL[:, :, 0].max()
#         baseLmax = baseL.max(axis=1)
#         baseLmax[:, 0] = baseLmax[:, 0] + diff
#         xy = np.concatenate((xy, baseLmax ))

# plt.scatter(xy[:, 0], 1-xy[:, 1], c='r', alpha=.05)
# plt.show()