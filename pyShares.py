"""
This is written and tested for python 2.7
"""

from yahoo_finance import Share
import datetime
import xml.etree.ElementTree
import curses
import traceback

MAX_LINES_OF_TERMINAL = 44


class TrailingStopPrinter:    

    def __init__(self):
        self.lineCounter = 1
        try:
            self.stdscr = curses.initscr()
        except:
            print('Could not init curses')   

    
    def printForAllShares(self):
                
        try:
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
        
            self.stdscr.addstr(0, 0, 'Supported keys: r = refresh | h = help\n')
            self.stdscr.addstr(0, 0, 'Refreshing ...')
        
            prettyPrintResult = ''
        
            xmlSharesRoot = xml.etree.ElementTree.parse('shares.xml').getroot()
        
            for xmlShare in xmlSharesRoot.findall('share'):
                xmlName = ''
                xmlTrailingStopDate = ''
                xmlTrailingStopPercentage = ''
                xmlTrailingStopAbsolute = ''
                xmlTrailingStopInit = ''
        
                for xmlNameTemp in xmlShare.findall('name'):
                    xmlName = str(xmlNameTemp.text)
                    self.printAndIncreaseLineCounter(xmlName + '\n')
                for xmlTrailingStopDateTemp in xmlShare.findall('trailingStopDate'):
                    xmlTrailingStopDate = str(xmlTrailingStopDateTemp.text)
                    self.printAndIncreaseLineCounter('-> Date {}\n'.format(xmlTrailingStopDate))
                for xmlTrailingStopPercentageTemp in xmlShare.findall('trailingStopPercentage'):
                    xmlTrailingStopPercentage = str(xmlTrailingStopPercentageTemp.text)
                    self.printAndIncreaseLineCounter('-> Percentage {}\n'.format(xmlTrailingStopPercentage))
                for xmlTrailingStopAbsoluteTemp in xmlShare.findall('trailingStopAbsolute'):
                    xmlTrailingStopAbsolute = str(xmlTrailingStopAbsoluteTemp.text)
                    self.printAndIncreaseLineCounter('-> Absolute {}\n'.format(xmlTrailingStopAbsolute))
                for xmlTrailingStopInitTemp in xmlShare.findall('trailingStopInit'):
                    xmlTrailingStopInit = str(xmlTrailingStopInitTemp.text)
                    self.printAndIncreaseLineCounter('-> Init {}\n'.format(xmlTrailingStopInit))
            
                share = Share(xmlName)
                prettyPrintResult = prettyPrintResult + share.get_name() + ': '
                self.printAndIncreaseLineCounter(share.get_name() + '\n')
                self.printAndIncreaseLineCounter(str(share.get_info()) + '\n')
        
                self.stdscr.refresh()
        
                if xmlTrailingStopDate != datetime.datetime.now().strftime('%Y-%m-%d'):
                    historicalDataMaximum = 0.0
                    historicalData = share.get_historical(xmlTrailingStopDate, datetime.datetime.now().strftime('%Y-%m-%d'))
        
                    for historicalDate in historicalData:
                        self.printAndIncreaseLineCounter(str(historicalDate) + '\n')
                        if historicalDataMaximum < float(historicalDate['High']):
                            historicalDataMaximum = float(historicalDate['High'])
        
                    self.printAndIncreaseLineCounter('historicalDataMaximum: \n'.format(historicalDataMaximum))
                    self.stdscr.refresh()
        
                    if xmlTrailingStopPercentage != 'None':
                        emptyValue = 0
        
                        if float(xmlTrailingStopInit) < (historicalDataMaximum - (historicalDataMaximum * (float(xmlTrailingStopPercentage) / 100))):
                            prettyPrintResult = prettyPrintResult + str((historicalDataMaximum - (historicalDataMaximum * (float(xmlTrailingStopPercentage) / 100)))) + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {}\n'.format((historicalDataMaximum - (historicalDataMaximum * (float(xmlTrailingStopPercentage) / 100)))))
                            self.stdscr.refresh()
                        else:
                            prettyPrintResult = prettyPrintResult + xmlTrailingStopInit + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {} - still on init value\n'.format(xmlTrailingStopInit))
        
                    if xmlTrailingStopAbsolute != 'None':
                        if float(xmlTrailingStopInit) < (historicalDataMaximum - float(xmlTrailingStopAbsolute)):
                            prettyPrintResult = prettyPrintResult + str((historicalDataMaximum - float(xmlTrailingStopAbsolute))) + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {}\n'.format((historicalDataMaximum - float(xmlTrailingStopAbsolute))))
                        else:
                            prettyPrintResult = prettyPrintResult + xmlTrailingStopInit + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {} (still on init value)\n'.format(xmlTrailingStopInit))
                else:
                    self.printAndIncreaseLineCounter('Trailing stop set today => no historical data available yet')
                    prettyPrintResult = prettyPrintResult + '\n'
        
                #prettyPrintResult = prettyPrintResult + ' --- '
        
                self.printAndIncreaseLineCounter('Open: {}\n'.format(share.get_open()))
                self.printAndIncreaseLineCounter('Current: {}\n'.format(share.get_price()))
                self.printAndIncreaseLineCounter('Update time: {}\n'.format(share.get_trade_datetime()))
                self.printAndIncreaseLineCounter('-----------------\n')
                self.printAndIncreaseLineCounter('\n')       
                
                self.stdscr.addstr(0, 0, 'Supported keys: r = refresh | h = help\n')
                self.stdscr.refresh()
                
            self.printAndIncreaseLineCounter(prettyPrintResult)
            self.lineCounter = self.lineCounter + prettyPrintResult.count('\n')
            
            self.printAndIncreaseLineCounter('Press a key to stop')
            self.stdscr.refresh()
            self.stdscr.getch()
        except BaseException as be:
            with open('errorlog.txt', 'w') as errorLog:
                errorLog.write(str(be))
                errorLog.write(str(traceback.print_exc()))
                errorLog.write('lineCounter was ' + str(self.lineCounter))
            self.printAndIncreaseLineCounter('exception {}'.format(be))
            self.stdscr.addstr(0, 0, 'Something went terribly wrong               ')
            self.stdscr.getch()
        finally:        
            #deinit stdscr
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
    
    def printAndIncreaseLineCounter(self, text):
        if self.lineCounter < MAX_LINES_OF_TERMINAL:
            self.stdscr.addstr(self.lineCounter, 0, text)
            self.lineCounter = self.lineCounter + 1
        else:
            self.stdscr.addstr(self.lineCounter, 0, 'Press a key to show the next page')
            self.stdscr.getch()
            self.stdscr.clear()
            self.lineCounter = 1
            self.stdscr.addstr(self.lineCounter, 0, text)
            self.lineCounter = self.lineCounter + 1
    
if __name__ == "__main__":
    #debugInput = raw_input('This is an entry point for remote debugging\n')
    
    tsp = TrailingStopPrinter()
    tsp.printForAllShares()