

# ===============================================
def searchAStringForAnyOfThese(searchme, findany, makeAllUpperCaseFlag):
    
    # Search string for csv of these
    
    searchme2 = searchme.upper() if makeAllUpperCaseFlag==1 else searchme
    findanythese = findany.upper() if makeAllUpperCaseFlag==1 else findany
    lst = findanythese.split(",")
    
    n = 0
    for it in lst:
        it2 = it.strip()
        if it2 != "":
            it3 = it2.upper() if makeAllUpperCaseFlag==1 else it2
            if searchme2.find(it3) != -1:
                n = 1
    
    return n
    
# ===============================================
