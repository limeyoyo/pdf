class Table(object):
  def __init__(self):
    '''
        :param title: 表题 title[0]保存英文标题 title[1]保存中文表题
        :param header: 表头 
        :param hoffset: 偏移
        :param content: 表格内容 content[0][0]保存表格最右下角的内容
        :param contcol: 表格内容的每列的x坐标最大区间 x0 x1 越大 下标越小
        :param controw: 表格内容的每行的y坐标最大区间 y0 y1 越大 下标越大
    '''
    self.title = []
    self.header = []
    self.hoffset = []
    self.content = []
    self.contcol = []
    self.controw = []

    

