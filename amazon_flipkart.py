from flask import Flask, request, redirect, render_template, url_for

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import re


def func(x, name):
    dic = {0: 'pro', 1: 'max', 2: 'mini', 3: 't '}
    x = x.replace(' ', '')
    name = name.replace(' ', '')
    for i in range(4):
        print(x, dic[i], name)
        if bool(re.search(dic[i], name, re.IGNORECASE)) ^ bool(re.search(dic[i], x, re.IGNORECASE)):
            return False
        else:
            pass
    if re.search(name, x, re.IGNORECASE):
        return True
    else:
        return False


def func2(x, mem, clr):
    if (mem == '0' or re.search(mem, x, re.IGNORECASE)) and (re.search(clr, x, re.IGNORECASE) or clr == '0'):
        return True
    else:
        return False


def func3(x, typ):
    if typ == 1:
        if re.search('Renewed', x, re.IGNORECASE):
            return False
        else:
            return True
    elif typ == 0:
        if re.search('Renewed', x, re.IGNORECASE):
            return True
        else:
            return False
    else:
        return True


path = 'chromedriver.exe'


def amazon(name, mem, clr, typ):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.amazon.in/")
    s = driver.find_element_by_id("twotabsearchtextbox")
    s.send_keys(name)
    s.send_keys(Keys.RETURN)
    button = driver.find_element(
        By.XPATH, "//*[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
    actions = ActionChains(driver)
    actions.click(button)
    time.sleep(5)
    m = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search")))
    prices = []
    names = []
    time.sleep(5)
    for i in range(20):
        products = m.find_elements(
            By.XPATH, "//div[@class='sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20 s-list-col-right']")
        for product in products:
            try:
                prices.append(product.find_element(
                    By.CLASS_NAME, 'a-price-whole').text)
                names.append(product.find_element(By.TAG_NAME, 'h2').text)
            except:
                print("error")
                continue
        actions.perform()
        time.sleep(2)
    driver.quit()
    data = {'Product Name': names, 'Price': prices}
    df_amazon = pd.DataFrame(data)
    df_amazon['New_Price'] = pd.to_numeric(
        df_amazon['Price'].str.replace('[^.0-9]', ''))

    df_amazon = df_amazon[df_amazon['Product Name'].apply(
        lambda x:func(x, name))]
    df_amazon = df_amazon[df_amazon['Product Name'].apply(
        lambda x:func2(x, mem, clr))]
    df_amazon = df_amazon[df_amazon['Product Name'].apply(
        lambda x:func3(x, typ))]

    try:
        df_amazon = df_amazon.sort_values(by='Price').head()
        df_amazon.drop(columns=['New_Price'], inplace=True)
    except:
        if len(df_amazon) == 0:
            pass
        else:
            df_amazon.drop(columns=['New_Price'], inplace=True)
            print("Not sorted amazon table")
    return(df_amazon)


def flipkart(name, mem, clr, typ):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.flipkart.com/")
    time.sleep(5)
    s = driver.find_element(By.CLASS_NAME, "_3704LK")
    s.send_keys(name)
    s.send_keys(Keys.RETURN)
    time.sleep(5)
    close = driver.find_element(By.XPATH, "//*[@class='_2KpZ6l _2doB4z']")
    actions = ActionChains(driver)
    actions.click(close)
    actions.perform()
    names = []
    prices = []
    for i in range(20):
        try:
            products = driver.find_elements(By.CLASS_NAME, "_3pLy-c")
        except:
            print("Error in finding data list of mobile")
        for product in products:
            try:
                prices.append(product.find_element(
                    By.CLASS_NAME, '_3tbKJL').text.split('\n')[0])
                names.append(product.find_element(
                    By.CLASS_NAME, '_4rR01T').text)
            except:
                print("error")
                continue
        try:
            button = driver.find_element(By.XPATH, "//*[@class='_1LKTO3']")
            actions = ActionChains(driver)
            actions.click(button)
            actions.perform()
        except:
            break
        time.sleep(2)
    driver.quit()
    data = {'Product Name': names, 'Price': prices}
    df_flipkart = pd.DataFrame(data)
    df_flipkart['New_Price'] = pd.to_numeric(
        df_flipkart['Price'].str.replace('[^.0-9]', ''))
    df_flipkart = df_flipkart[df_flipkart['Product Name'].apply(
        lambda x:func(x, name))]
    df_flipkart = df_flipkart[df_flipkart['Product Name'].apply(
        lambda x:func2(x, mem, clr))]
    df_flipkart = df_flipkart[df_flipkart['Product Name'].apply(
        lambda x:func3(x, typ))]
    try:
        df_flipkart = df_flipkart.sort_values(by='New_Price').head()
        df_flipkart.drop(columns=['New_Price'], inplace=True)
    except:
        if len(df_flipkart) == 0:
            pass
        else:
            df_flipkart.drop(columns=['New_Price'], inplace=True)
            print("not sorted flipkart table")
    return(df_flipkart)


app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def data():
    if request.method == "GET":
        return render_template("web.html")
    elif request.method == "POST":
        name = request.form["nm"]
        memory = request.form["my"]
        color = request.form["cl"]
        type1 = str(request.form.get('Renewed or New'))
        if len(type1) == 0:
            type1 = 2
        elif type1 == "New":
            type1 = 1
        elif type1 == "Renewed":
            type1 = 0
        else:
            pass
        if len(memory) == 0:
            memory = '0'
        if len(color) == 0:
            color = '0'
        if len(name) != 0:
            return redirect(url_for("final", usr=name, mem=memory, clr=color, typ=type1))
        else:
            pass
    else:
        pass


@app.route("/<usr>/<mem>/<clr>/<typ>", methods=["GET"])
def final(usr, mem, clr, typ):
    df_amazon = amazon(usr, mem, clr, typ)
    df_flipkart = flipkart(usr, mem, clr, typ)
    return render_template('data.html',  tables=[df_amazon.to_html(classes='data'), df_flipkart.to_html(classes='data')], titles=df_amazon.columns.values)


if __name__ == "__main__":
    app.run(port=4996, debug=True)
