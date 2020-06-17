# -*- coding:utf-8 -*-
import os, sys
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTRect, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator

_line = []
_tb = []
_content = {}
_header = []

def changeSorty(data, args, key = 'y0'):
  '''
    交换排序:key越大越靠前
  '''
  changedata = {}
  for i in range(len(data) - 1):
    max = i
    for j in range(max + 1, len(data), 1):
      if data[j][key] > data[max][key]:
        max = j
    if max != i:
      changedata = data[i]
      data[i] = ({
        arg : data[max][arg] for arg in args
      })
      data[max] = ({
        arg : changedata[arg] for arg in args
      })
     
def bubSortx(data, args, key = 'x0'):
  '''
    冒泡排序:y0一样大时,key越小越靠前
  '''
  changedata = {}
  for i in range(len(data) - 1):
    if data[i]['y0'] == data[i+1]['y0']:
      if data[i]['x0'] > data[i+1]['x0']:
        max = i + 1
        for j in range(i):
          if data[j]['y0'] != data[i+1]['y0']:
            continue
          if data[j][key] > data[i+1][key]:
            i = j
            break
        changedata = data[i]
        data[i] = ({
          arg : data[max][arg] for arg in args
        })
        data[max] = ({
          arg : changedata[arg] for arg in args
        })

def merge(data, args, key = 'offset', text = 'text'):
  '''
    同行内容合并:key一致合并
  '''
  da = {}
  revdata = []
  revdata.append(da)
  index = 0
  for i in range(len(args)):
    revdata[index][args[i]] = data[index][args[i]]
  for j in range(len(data) - 1): 
    if data[j][key] == data[j+1][key]:
      if text == 'text':
        revdata[index][text] += ' ' + data[j+1][text]
      if text == 'x1':
        revdata[index][text] = data[j+1][text]
    else:
      if j + 1 != len(data):
        da = {}
        revdata.append(da)
        index += 1
        for arg in args:
          revdata[index][arg] = data[j+1][arg]
  return revdata

def isThreeLineTable(ltpage):
  '''
    判断当前页面是否存在三线表
  '''
  global _line
  _line.clear()
  args = ['x0', 'x1', 'y0', 'y1']
  ltrect = []
  for obj in ltpage._objs:
    if isinstance(obj, LTRect):
      ltrect.append({
        args[0]: obj.x0,
        args[1]: obj.x1,
        args[2]: obj.y0,
        args[3]: obj.y1
      })
  changeSorty(ltrect, args, key = args[2])
  bubSortx(ltrect, args, key = args[0])
  lines = merge(
      ltrect, 
      args, 
      key = args[2], 
      text = args[1]
      )
  for line in lines:
    if (line[args[1]] - line[args[0]]) > 250:
      _line.append(line[args[2]])
  return _line

def dfsReadConts(_obj):
  '''
    递归寻值 计算表格中的值及坐标
    如果是第二条线到第三条线之间的内容 排序保存在 _tb.content 中
    如果是第一条线到第二条线之间的表头 保存在 _header 中
  '''
  global _content
  global _header
  for obj in _obj._objs:
    # hasattr(obj._objs[0], '_text')
    if obj.get_text().count('\n') == 1:
      text = obj.get_text()[:-1]
      while text[-1] == ' ':
        text = text[:-1]
      while text[0] == ' ':
        text = text[1:] 
      if text.isdigit() or text.count(' ') == 0: 
        _content.clear()
        _content = {
          'text': text,
          'x0': obj.x0,
          'x1': obj.x1,
          'y0': obj.y0,
          'y1': obj.y1
        }
        # 第一条线到第二条线之间的表头
        if _content['y1'] < _line[0] + 5 and _content['y0'] > _line[1] - 5:
          _header.append({
            'text': _content['text'],
            'x0': _content['x0'],
            'x1': _content['x1'],
            'y0': _content['y0'],
            'y1': _content['y1']
          })
        # 第二条线到第三条线之间的内容
        if _content['y1'] < _line[1] + 5 and _content['y0'] > _line[2] - 5:
         insertSort()
      else:
        texts = text.split(' ')
        offset = 0
        for textI in texts:
          _content.clear()
          _content = {
            'text': textI,
            'x0': obj._objs[offset].x0,
            'x1': obj._objs[offset + len(textI) -1].x1,
            'y0': obj.y0,
            'y1': obj.y1
          }
          # 第一条线到第二条线之间的表头
          if _content['y1'] < _line[0] + 5 and _content['y0'] > _line[1] - 5:
            _header.append({
              'text': _content['text'],
              'x0': _content['x0'],
              'x1': _content['x1'],
              'y0': _content['y0'],
              'y1': _content['y1']
            })
          # 第二条线到第三条线之间的内容
          if _content['y1'] < _line[1] + 5 and _content['y0'] > _line[2] - 5:
            insertSort()
          offset += (len(textI) + 1)
    else: 
      dfsReadConts(obj)

def rowSort(crow):
  '''
    行插入排序
  '''
  for rowI, controw in enumerate(_tb.content):
    if _tb.controw[rowI][1] < _content['y0'] + 5:
      continue
    _tb.controw.insert(rowI, [_content['y0'], _content['y1']])
    _tb.content.insert(rowI, crow)
    return rowI
  if len(_tb.content) - 1 == rowI:
    _tb.controw.append([_content['y0'], _content['y1']])
    _tb.content.append(crow)
  return rowI + 1

def colSort(row):
  '''
    列插入排序
  '''
  for colI, contcol in enumerate(_tb.content[row]):
    if _tb.contcol[colI][0] > _content['x1'] - 5:
      continue
    _tb.contcol.insert(colI, [_content['x0'], _content['x1']])
    for rowI in range(len(_tb.controw)):
      if rowI == row:
        _tb.content[row].insert(colI, _content['text'])
        continue
      _tb.content[rowI].insert(colI, '')
    return colI
  if len(_tb.content[row]) - 1 == colI:
    _tb.contcol.append([_content['x0'], _content['x1']])
    for rowI in range(len(_tb.controw)):
      if rowI == row:
        _tb.content[row].append(_content['text'])
        continue
      _tb.content[rowI].append('')
  return colI + 1

def insertSort():
  '''
    排序插入表格内容值
  '''
  if len(_tb.contcol) == 0 and len(_tb.controw) == 0:
    _tb.content = [[_content['text']]]
    _tb.contcol = [[_content['x0'], _content['x1']]]
    _tb.controw = [[_content['y0'], _content['y1']]]
    return
  avex = (_content['x0'] + _content['x1'])/2 
  avey = (_content['y0'] + _content['y1'])/2
  for col, x in enumerate(_tb.contcol):
    # 属于现有列 
    if (avex > x[0] and avex < x[1]) or (_content['x0'] < x[0] + 5 and _content['x1'] > x[1] - 5):
      for row, y in enumerate(_tb.controw):
        # 1.属于现有列 属于现有行
        if avey > y[0] and avey < y[1]:
          if _tb.content[row][col] == '':
            _tb.content[row][col] = _content['text']
          else:
            _tb.content[row][col] += ' ' + _content['text']
          _tb.contcol[col] = (_content['x0'] 
          if _content['x0'] < x[0] else x[0], 
          _content['x1'] 
          if _content['x1'] > x[1] else x[1])
          _tb.controw[row] = (_content['y0'] 
          if _content['y0'] < y[0] else y[0], 
          _content['y1'] 
          if _content['y1'] > y[1] else y[1]) 
          return
            # 2.属于现有列 不属于现有行
      crow = []
      for colI in range(len(_tb.contcol)):
        crow.append('')
      crow[col] = _content['text']
      # 行排序
      rowSort(crow)       
      _tb.contcol[col] = (_content['x0'] 
      if _content['x0'] < x[0] else x[0], 
      _content['x1'] 
      if _content['x1'] > x[1] else x[1])
      return
  for row, y in enumerate(_tb.controw):
    # 3.不属于现有列 属于现有行
    if avey > y[0] and avey < y[1]:
      # 列排序
      colSort(row)
      _tb.controw[row] = (_content['y0'] 
      if _content['y0'] < y[0] else y[0], 
      _content['y1'] 
      if _content['y1'] > y[1] else y[1]) 
      return
  # 4.不属于现有列 不属于现有行
  crow = []
  for colI in range(len(_tb.contcol)):
    crow.append('')
  # 行列排序
  rowI = rowSort(crow)
  colI = colSort(rowI)
  # 赋值
  _tb.content[rowI][colI] = _content['text']
  return

def intervalSort(headcolsort):
  '''
    列区间插入排序
  '''
  args = ['text', 'offset', 'x0', 'y0'] 
  col = len(_tb.contcol) 
  for h in _header:
    left = -1
    right = -len(_tb.contcol)
    if h[args[2]] > _tb.contcol[left][1]:
      for i in range(-1, -(col + 1), -1):
        if h[args[2]] > _tb.contcol[i][1]:
          continue
        break
      left = i
    if h['x1'] < _tb.contcol[right][0]:
      for j in range(left, -(col + 1), -1):
        if h['x1'] > _tb.contcol[j][0]:
          continue
        break
      right = j + 1
    headcolsort[left].append({
      args[0]: h[args[0]],
      args[1]: left - right,
      args[2]: h[args[2]],
      args[3]: h[args[3]]
    })
   
def readHeaderInfo():
  '''
    表头信息读取
  '''
  args = ['text', 'offset', 'x0', 'y0']
  col = len(_tb.contcol)
  # 二维 列排 列插
  headcolsort = []
  for i in range(col):
    headcolsort.append([])
  intervalSort(headcolsort)
  # 取列 一维 行排
  headrowsort = []
  for i in range(col):
    headrowsort.append([])
  he = []
  for j , he in enumerate(headcolsort):
    changeSorty(he, args, key = 'y0')
    bubSortx(he, args, key = 'x0')
    headrowsort[j] = merge(
        he, 
        args, 
        key = args[1], 
        text = args[0]
        ) 
  # 按列读取
  for m in range(col):
    # 读当前列取一行
    for n in range(-1, -(len(headrowsort[m]) + 1), -1):
      if (-n) > len(_tb.header):
        # 增加存储空间
        _tb.header.insert(0, [])
        _tb.hoffset.insert(0, [])
        for k in range(col):
          _tb.header[n].append('')
          _tb.hoffset[n].append(0)
      # 存入表头信息
      _tb.header[n][m] = headrowsort[m][n][args[0]]
      _tb.hoffset[n][m] = headrowsort[m][n][args[1]]

def readThreeLineTable(ltpage, tb):
  global _tb
  _header.clear()
  _tb = tb
  for index in range(-1, -(len(ltpage._objs) + 1), -1):
    # 判断类型
    if isinstance(ltpage._objs[index], LTTextBoxHorizontal):
      # 读取第一条线前的标题 
      if ltpage._objs[index].bbox[1] > _line[0] and len(_tb.title) < 2:
        _tb.title.append(ltpage._objs[index].get_text()[:-1])
      # 读取：第一条线到第二条线之间的表头 和 第二条线到第三条线之间的内容
      # 表内容：二维排序
      # 表头：保存信息
      if ltpage._objs[index].bbox[1] < _line[0] and ltpage._objs[index].bbox[1] > _line[2]: 
        dfsReadConts(ltpage._objs[index])
      # 标题读完则结束
      if len(_tb.title) == 2:
        break
  # 处理表头信息
  readHeaderInfo()
  return _tb