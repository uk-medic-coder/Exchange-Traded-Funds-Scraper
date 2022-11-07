from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import time

# =========================================
# SELENIUM FUNCS
# =========================================

def initiateWebdriver():

    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=/home/{{USERNAME}}/.config/google-chrome/")
    options.add_argument(r"--profile-directory=Profile 1") #e.g. Profile 3
    driver = webdriver.Chrome(options=options)   
    
    return driver

# =========================================

def waitForElement(driver, elementtype, css, maxwaittime, ermsg, outputflag):

    if elementtype=="id":
        emmt = By.ID
    if elementtype=="class":
        emmt = By.CLASS_NAME
    if elementtype=="xpath":
        emmt = By.XPATH

    errflag = 0
    errmsg = ""
    
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

    try:
        tmpelm=WebDriverWait(driver,maxwaittime,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((emmt,css)))       
        
    except:
        errmsg = "\nTIMEOUT ERROR - ELEMENT NOT FOUND: waitForElement: "+elementtype+", "+css+"\n"+ermsg+"\n\n"
        errflag = 1

    # Finished, clean up bits
    if outputflag==1 and errflag==1:
        #include1.logoutput(errmsg)    
        dummy = 1
        
    return errflag, errmsg

# ==================================================

def gotoWebPageURL(driver, url, elementtype, css, maxwaittime, ermsg, outputflag):

    driver.get(url)
    errflag, errmsg = waitForElement(driver, elementtype, css, maxwaittime, "\n"+ermsg+", Get URL error for: "+url, outputflag)

    return errflag, errmsg

# ==================================================

def check_exists_by_xpath(driver, xpp):
    
    r = True
    
    try:
        driver.find_element(By.XPATH, xpp)
    except:
        r = False
    
    return r

# ==================================================

def buttonClick(driver, vl, method, waittime):
    
    if method==0:

        if waitForElement(driver, "xpath", vl, 20, "button wait to appear: "+vl, 1)==0:
            time.sleep(waittime)
            driver.find_element(By.XPATH, vl).send_keys(Keys.ENTER)
        
