from selenium import webdriver
import pandas as pd
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option('useAutomationExtension', False)

driver= webdriver.Chrome(options=chromeOptions, desired_capabilities=chromeOptions.to_capabilities(),executable_path='chromedriver.exe')
driver.get('https://www.sondadelivery.com.br/delivery/hotsite/tbl03a09/1/216/0')
flag = True
index = 1
matrix = []
while flag:
    try:
        nome = driver.find_element_by_xpath('/html/body/form/div[5]/div/main/div[2]/div[2]/div[2]/div/div['+str(index)+']/div/div[2]/a/h3/span').text
        preco = driver.find_element_by_xpath('/html/body/form/div[5]/div/main/div[2]/div[2]/div[2]/div/div['+str(index)+']/div/div[2]/div/div/span/span[3]/strong/span/span').text
        link = driver.find_element_by_xpath('/html/body/form/div[5]/div/main/div[2]/div[2]/div[2]/div/div['+str(index)+']/div/figure/a/img').get_attribute("srcset")
        matrix.append([nome, preco, link])
        index += 1
    except:
        flag = False
        
df = pd.DataFrame(matrix, columns = ['Produto', 'Preco','Link'])
df.to_excel('base_sonda.xlsx', index=False)