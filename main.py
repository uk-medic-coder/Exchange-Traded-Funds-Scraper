
import sys
import os
from datetime import datetime, timedelta
import time
import io
import shutil
import re

import generalFuncs as gnrl
import liststringsGeneral as aclst
import scraperCommonPY as scraperCommon

from selenium import webdriver
from selenium.webdriver.common.by import By

# ========================================================
# Globals

baseurl = "/home/{{USER}}/fknolScraperMk2/"       # slash on end needed - REPLACE {{USER}} with your username

# ========================================================
spdrnamesList = ["XLC","XLY","XLP","XLE","XLF","XLV","XLI","XLB","XLRE","XLK","XLU"]

spdrfullnames = ["Communication Services","Consumer Discretionary", "Consumer Staples","Energy","Financials","Health Care","Industrials","Materials","Real Estate","Technology","Utilities"]

extension_US = ".US"
extension_UK = ".UK"

driver = None
TotalSymbolsList = []
countries = []
allshares = []
usleveraged = []
usnonleveraged = []
ukleveraged = []
uknonleveraged = []
allleveraged = []
allnonleveraged = []
spdrlist = []   
ukallshares = []
usallshares = [] 
indexmasterlist = []

pagepauseLen = 5

# =========================================
# =========================================
def isSymLev(n):
    r = aclst.searchAStringForAnyOfThese(n, "2x, 3x, leverage, 5x, ultra", 1)
    return r

# =========================================
# =========================================

def scrapethispage(u, qq, ii, nn, ukorusflag):
    
    scraperCommon.gotoWebPageURL(driver, u, "xpath", "/html/body/footer[2]/p/a[4]", 30, "Page-"+str(nn), 1) 

    st = 3              # this is tr[x] div
    
    n = 0
    while n == 0:

        time.sleep(pagepauseLen)

        xp = "/html/body/article[1]/div[4]/table/tbody/tr["+str(st)+"]/td[2]"
        
        if scraperCommon.check_exists_by_xpath(driver, xp) == True:
        
            e1 = driver.find_element(By.XPATH, xp)
            
            # symbol is last element between brackets - some text's have more than one set of brackets so use the last set
            ss = e1.text
            res = re.findall(r'\(.*?\)', ss)
            s = res[-1:]        # get last list item
            rst = ''.join(s)        # list to string conversion
            symbol = rst.replace('(', '').strip().upper()
            symbol = symbol.replace(")", "")
            symbol = symbol.replace("◐  ", "")

            if ukorusflag==2:
                symbol += extension_UK
            
            if ukorusflag==1:
                symbol += extension_US

            # get name by removing all brackets text
            for w in res:
                ss = ss.replace(w, '')
            name = ss.replace("◐", "")
            name = name.strip()
            #name = re.sub(r'\W+', '', name)     # remove all nonalphanumeric


            # do before change name to (CURR) for UK stocks
            
            levtype = isSymLev(name)
            
            if symbol not in allleveraged:
                if levtype==1:
                    allleveraged.append(symbol)

            if symbol not in allnonleveraged:
                if levtype==0:
                    allnonleveraged.append(symbol)

            if ukorusflag==1:       # US
                if symbol not in usleveraged:
                    if levtype==1:
                        usleveraged.append(symbol)

                if symbol not in usnonleveraged:
                    if levtype==0:
                        usnonleveraged.append(symbol)                


            if ukorusflag==2:       # UK
                if symbol not in ukleveraged:
                    if levtype==1:
                        ukleveraged.append(symbol)

                if symbol not in uknonleveraged:
                    if levtype==0:
                        uknonleveraged.append(symbol)     

                
                # UK only - add currency to end
                e2 = driver.find_element(By.XPATH, "/html/body/article[1]/div[4]/table/tbody/tr["+str(st)+"]/td[4]")
                s2 = e2.text
                curr = s2.strip().upper()                
                name += " ("+curr+")"                

            prefix = "UK_" if ukorusflag==2 else "US_"
            gnrl.SaveFile(baseurl+prefix+qq+".tls", "a", symbol)

            # Avoid duplicates
            if symbol not in TotalSymbolsList:
                TotalSymbolsList.append(symbol)
                gnrl.SaveFile(baseurl+"ZZZZ____MasterImportCreate.tls", "a", symbol+","+name)

            if symbol not in allshares:
                allshares.append(symbol)

            if ukorusflag==1:
                if symbol not in usallshares:
                    usallshares.append(symbol)
            else:
                if symbol not in ukallshares:
                    ukallshares.append(symbol)
                
            # Also avoid duplicates for spdrlist
            if ukorusflag==1:
                if symbol not in spdrlist:
                    nmtemp = name.upper()
                    if nmtemp.find("SPDR") != -1:
                        spdrlist.append(symbol)
            
            st +=1
            
        else:
            n=1
    

# =========================================

def doutil(nm, ur, ii, ukorusflag):
    
    time.sleep(3)                   # pace it, server bans
    
    # Do this page then see if any other links
    scrapethispage(ur, nm, ii, 1, ukorusflag)
    
    n = 0
    dnflg = 0
    cnt = 1
    while n==0:
        xp = "/html/body/article[1]/p/a["+str(cnt)+"]"
        if scraperCommon.check_exists_by_xpath(driver, xp) == True:
            ee = driver.find_element(By.XPATH, xp)
            href = ee.get_attribute('href')
            scrapethispage(href, nm, ii, cnt+1, ukorusflag)
            cnt += 1
            dnflg = 1
        else:
            n = 1
    
    
    if dnflg==0:
        # Sometimes if just one set of new page links, eg: 26-50 this is it:
        xp = "/html/body/article[1]/p/a"
        if scraperCommon.check_exists_by_xpath(driver, xp) == True:
            ee = driver.find_element(By.XPATH, xp)
            href = ee.get_attribute('href')
            scrapethispage(href, nm, ii, 0, ukorusflag)      

# =========================================
# =========================================
def doMainApp(ukorusflag):

    global driver

    if ukorusflag==1:           # US
        startpage = "https://fknol.com/etf/list/"
        firstpagediv = "/html/body/article/div[3]/p["

    if ukorusflag==2:           # UK
        startpage = "https://fknol.com/uk/etf/"
        firstpagediv = "/html/body/article/div[3]/div/p["


    # 1st get a list of all watchlists and URLs
    wl = []
    wlurl = []


    # the "1" at the end means print() any errors - otherwise they need to be handled by this main --- see common files scraper
    scraperCommon.gotoWebPageURL(driver, startpage, "xpath", "/html/body/article/footer[2]/p/a[4]", 30, "Footer on initial ETF URL", 1) 
    
    n = 0
    cnt = 1
    while n==0:
        xp = firstpagediv+str(cnt)+"]"
        if scraperCommon.check_exists_by_xpath(driver, xp) == True:
            ee = driver.find_element(By.XPATH, xp)
            w = ee.text.replace("List of", "")
            
            # Replace a few bug bears
            w = w.replace("◐", "")                      # done separately in-case they drop the symbol from whole string above
            w = w.replace("ETFs", "ETF")
            w = w.replace("S&p", "S&P")
            w = w.replace("◐  ", "")
            #name = re.sub(r'\W+', '', name)     # remove all nonalphanumeric                   
            
            wl.append(w.strip())
            ah = driver.find_element(By.XPATH, xp+"/a")                  # easier to find subset div this way
            wlurl.append(ah.get_attribute('href'))            
            cnt += 1
        else:
            n = 1

    
    #Now got the list, can start each one

    for i in range(0, len(wl)):
        doutil(wl[i],wlurl[i], i, ukorusflag)
    
 

    # Now get a list of all countries - only for US DB
    
    if ukorusflag==1:

        scraperCommon.gotoWebPageURL(driver, "https://www.thebalance.com/region-etfs-and-etns-1215142", "xpath", "//*[@id='footer__dotdash-universal-nav_1-0']", 30, "Footer on Countries Page", 1)   
        
        body = driver.find_element(By.XPATH, '/html/body')
        all_li = body.find_elements(By.CSS_SELECTOR, 'li')
        for e in all_li:
            ee = e.text.upper()
            if "-" in ee:
                if "ETF" in ee:
                    espl = ee.split("-")
                    symbol = espl[0].strip()
                    name = espl[1].strip()
                    if len(symbol)<6:
                        levtype = isSymLev(name)
                        
                        if symbol not in usleveraged:
                            if levtype==1:
                                usleveraged.append(symbol)

                        if symbol not in usnonleveraged:
                            if levtype==0:
                                usnonleveraged.append(symbol)
                                
                        # Avoid duplicates
                        if symbol not in TotalSymbolsList:
                            TotalSymbolsList.append(symbol)
                            gnrl.SaveFile(baseurl+"ZZZZ____MasterImportCreate.tls", "a", symbol+","+name)

                        if symbol not in allshares:
                            allshares.append(symbol)
                        
                        if symbol not in usallshares:
                            usallshares.append(symbol)                            
    
                        if symbol not in countries:
                            countries.append(symbol)

    # all done, add all of wl[] to indexmasterlist []
    for x in wl:
        if ukorusflag==1:           # US
            indexmasterlist.append("US_"+x)
        else:
            indexmasterlist.append("UK_"+x)            

# =========================================
# =========================================
# MAIN ENTRY POINT
# =========================================
# =========================================
if __name__ == '__main__':
    
    # clear bash window
    os.system('clear')
    

    # Delete existing folder
    if baseurl.endswith("fknolScraperMk2/"):
        if os.path.isdir(baseurl)==True:
            shutil.rmtree(baseurl)            # remove folder and all its files
        os.mkdir(baseurl)    
    else:
        print("\nError - unsafe to delete baseurl folder!\n")
        exit()
    

    # Do UK, then US

    print("\n\nWorking....")

    driver = scraperCommon.initiateWebdriver()

    doMainApp(1)
    doMainApp(2)


    # Now do outputting

    for ii in range(0, len(spdrnamesList)):
        x = spdrnamesList[ii]
        if x not in TotalSymbolsList:
            gnrl.SaveFile(baseurl+"ZZZZ____MasterImportCreate.tls", "a", x+",SPDR Select "+spdrfullnames[ii])
        if x not in allshares:
            allshares.append(x)
        if x not in usallshares:
            usallshares.append(x)            
        if x not in spdrlist:
            spdrlist.append(x)

        gnrl.SaveFile(baseurl+"SPDR select.tls", "a", x)
        

    for rr in countries:
        gnrl.SaveFile(baseurl+"All Countries.tls", "a", rr)        

    for rr in spdrlist:
        gnrl.SaveFile(baseurl+"SPDR only.tls", "a", rr)

    for rr in allshares:
        gnrl.SaveFile(baseurl+"All Shares.tls", "a", rr)

    for rr in ukallshares:
        gnrl.SaveFile(baseurl+"All UK Shares.tls", "a", rr)

    for rr in usallshares:
        gnrl.SaveFile(baseurl+"All US Shares.tls", "a", rr)

    for rr in allleveraged:
        gnrl.SaveFile(baseurl+"All Leveraged.tls", "a", rr)

    for rr in allnonleveraged:
        gnrl.SaveFile(baseurl+"All Non-Leveraged.tls", "a", rr)      

    for rr in usleveraged:
        gnrl.SaveFile(baseurl+"US Leveraged.tls", "a", rr)

    for rr in usnonleveraged:
        gnrl.SaveFile(baseurl+"US Non-Leveraged.tls", "a", rr) 

    for rr in ukleveraged:
        gnrl.SaveFile(baseurl+"UK Leveraged.tls", "a", rr)

    for rr in uknonleveraged:
        gnrl.SaveFile(baseurl+"UK Non-Leveraged.tls", "a", rr) 

    
    # Now output sorted index.txt for amibroker
    
    slist = sorted(indexmasterlist, key=str.lower)
    
    slist.append("")
    slist.append("SPDR only")
    slist.append("SPDR select")
    slist.append("All Countries")
    slist.append("")
    slist.append("All Shares")
    slist.append("All US Shares")
    slist.append("All UK Shares")    
    slist.append("")    
    slist.append("All Non-Leveraged")
    slist.append("All Leveraged")
    slist.append("")    
    slist.append("US Non-Leveraged")
    slist.append("US Leveraged")    
    slist.append("")    
    slist.append("UK Non-Leveraged")
    slist.append("UK Leveraged")
    slist.append("")   

    for uu in slist:
        gnrl.SaveFile(baseurl+"index.txt", "a", uu)   

    # ~~~~~~~~~~~~~~
    # All done
    # ~~~~~~~~~~~~~~

    print("\n\nAll done!\n")
    # close all driver processes and quit
    driver.quit()    
