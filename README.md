# selenium_taobao
使用selenium打开淘宝，读取商品全部评价  

# 流程
1.运行tuobao.py,selenium会打开chromedriver   
2.chromedriver跳转到淘宝的登录页面  
3.使用手机二维码扫码登录，登录后会保存cookies，下次可以从my_cookies.pkl加载cookies
4.扫码登录后，会根据'//*[@id="ice-container"]/div[2]/div[2]/div[2]/div[1]/div/ul/li[5]/div[2]/div/div/div[1]/div[4]/a[11]'跳转到指定url（可自行修改）
5.查找完毕后，会读取这页的所有内容，for循环打开url，打开url里面全部评价，然后保存












