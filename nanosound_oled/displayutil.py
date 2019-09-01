
class ViewPort:

    linesPerPage = 4

    curOnLine = 1
    displayingPage = 1

    lines = []
    def __init__(self, lines):
        self.lines = lines

    def maxPage(self):
        return (len(self.lines) // self.linesPerPage) + 1

    def getPage(self, pageno):
        #check if out of bounds
        if(pageno>self.maxPage()):
            return None
        else:
            return self.lines[(pageno-1)*4:((pageno-1)*4)+4]

    def getDisplay(self):
        page = self.getPage(self.displayingPage)

        if(self.curOnLine > len(page)):
            return page
        else:
            page[self.curOnLine-1] = ">" + str(page[self.curOnLine-1])
            return page

    def selectNext(self):
        self.curOnLine = self.curOnLine + 1

        if(self.curOnLine>=(self.linesPerPage-1)):
            self.curOnLine = 1

        return self.getDisplay()
