import xlrd


data = xlrd.open_workbook('./command.xlsx')
table = data.sheets()[0]       #读取第一个（0）表单
#或者通过表单名称获取 table = data.sheet_by_name(u'Sheet1')
print(str(table.nrows))            #输出表格行数
print(str(table.ncols))            #输出表格列数
#print(str(table.row_values(0)))    #输出第一行
#print(str(table.col_values(1)))    #输出第一列
#print(str(table.cell(0,2).value))  #输出元素（0,2）的值

for i in range(1,15):
    print(str(table.cell(i,1).value))  #输出元素所有指令的值