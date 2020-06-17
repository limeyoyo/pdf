import os, sys
import tkinter
import tkinter.filedialog
from concurrent.futures import ThreadPoolExecutor
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTRect, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator
try:
  import src.table as Tb
except:
  pass
from src.pdfTools import isThreeLineTable, readThreeLineTable

def setWindowSizeAndCenter(win, width, height):
  screenWidth = win.winfo_screenwidth()
  screenHeight = win.winfo_screenheight()
  x = (screenWidth-width) / 2
  y = (screenHeight-height) / 2
  win.geometry('%dx%d+%d+%d' %(width,height,x,y))

def openFile():
  fileName = tkinter.filedialog.askopenfilename(title='PDF文件选择')
  if fileName:
    pdfFileEntry.delete(0, tkinter.END)
    pdfFileEntry.insert(0, fileName)

def openDir():
  path = tkinter.filedialog.askdirectory(title='保存路径选择')
  if path:
    savePathEntry.delete(0, tkinter.END)
    savePathEntry.insert(0, path)

def doButton():
  doTableButton.config(state='disable')
  pdfFile = pdfFileEntry.get()
  savePath = savePathEntry.get()
  # 检查合法情况 to do

  # 调用 doTable
  #th.submit(doTable, pdfFile, savePath)
  doTable(pdfFile, savePath)

def doTable(pdfFile, savePath):
  with open(pdfFile, 'rb') as fp:
    # 创建PDF文档解析器对象
    parser = PDFParser(fp)
    # 创建PDF文档对象
    doucument = PDFDocument()
    # 连接分析器和文档对象
    parser.set_document(doucument)
    doucument.set_parser(parser)
    # 初始化
    doucument.initialize()

    # 创建PDF资源管理对象
    rsrcmgr = PDFResourceManager()
    # 创建PDF设备对象
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams = laparams)
    # 创建PDF解析器对象
    interpreter = PDFPageInterpreter(rsrcmgr, device)

  for page in doucument.get_pages():
      # 解析
      interpreter.process_page(page)
      # 获取页面的LTPage对象
      ltpage = device.get_result()
      # 判断是否有三线表
      line = isThreeLineTable(ltpage)
      if len(line) == 3:
        tb = Tb.Table()
        # 读表
        readThreeLineTable(ltpage, tb)
        # 写表 to do
        jiay = []
        del ltpage
        del tb

  

th = ThreadPoolExecutor(max_workers = 1)
root = tkinter.Tk()
root.title('PDF表格读取')
setWindowSizeAndCenter(root, 800, 560)
root.resizable(width = False, height = False)

frameTop = tkinter.Frame(root)
frameTop['borderwidth'] = 1
frameTop['relief'] = 'solid'
pdfFileLabel = tkinter.Label(frameTop, text='PDF文件：',bd=2)
pdfFileEntry = tkinter.Entry(frameTop)
pdfFileOpenButton = tkinter.Button(frameTop, text='选择文件', width=11)
savePathLabel = tkinter.Label(frameTop, text='保存路径：',bd=2)
savePathEntry = tkinter.Entry(frameTop)
savePathButton = tkinter.Button(frameTop, text='选择路径', width=11)
doTableButton = tkinter.Button(frameTop, text='生成表格', width=11)

frameLog = tkinter.Frame(root)
frameLog['borderwidth'] = 1
frameLog['relief'] = 'solid'
log = tkinter.Text(frameLog, bg='#EDEDED')

frameTop.place(x=5,y=10,width=790,height=120)
frameLog.place(x=5,y=140,width=790,height=410)
log.place(x=5,y=10,width=780,height=385)
pdfFileLabel.place(x=10,y=20)
pdfFileEntry.place(x=85,y=20,width=470,height=24)
pdfFileOpenButton.place(x=580,y=20,height=24)

savePathLabel.place(x=10,y=70)
savePathEntry.place(x=85,y=70,width=470,height=24)
savePathButton.place(x=580,y=70,height=24)
doTableButton.place(x=680,y=70,height=24)

pdfFileOpenButton.config(command = openFile)
savePathButton.config(command = openDir)
doTableButton.config(command = doButton)

root.mainloop()