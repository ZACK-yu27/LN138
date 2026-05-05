#京东网址结构
item_name = input("请输入要搜索的商品名称: ")
site = 'http://search.jd.com/Search?keyword=' + item_name + '&enc=utf-8&spm=a.0.0&pvid=99a4a7a222cb48e39632ad8e7594a87d&spmTag=YTAyMTkuYjAwMjM1Ni5jMDAwMDQ2ODkuMw'

#输出结果
print("京东搜索链接: " + site)