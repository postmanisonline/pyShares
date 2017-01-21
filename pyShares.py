"""
This is written and tested for python 2.7
"""

from yahoo_finance import Share
import datetime
import xml.etree.ElementTree
import curses
import traceback
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
import matplotlib.patches as mpatches

MAX_LINES_OF_TERMINAL = 44
NUMBER_OF_HORIZONTAL_CHARACTERS = 200


class TrailingStopPrinter:    

    def __init__(self):
        self.lineCounter = 1
        try:
            self.stdscr = curses.initscr()
            curses.start_color()
            #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
            #curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
            #curses.use_default_colors()
        except:
            print('Could not init curses')   

    
    def printForAllShares(self):
                
        try:
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
        
            self.stdscr.addstr(0, 0, 'pyShares')
            self.stdscr.addstr(0, 0, 'Refreshing ...')
        
            prettyPrintResult = ''
        
            xmlSharesRoot = xml.etree.ElementTree.parse('shares.xml').getroot()
        
            for xmlShare in xmlSharesRoot.findall('share'):
                xmlName = ''
                xmlBuyPrice = ''
                xmlTrailingStopDate = ''
                xmlTrailingStopPercentage = ''
                xmlTrailingStopAbsolute = ''
                xmlTrailingStopInit = ''
        
                for xmlNameTemp in xmlShare.findall('name'):
                    xmlName = str(xmlNameTemp.text)
                    self.printAndIncreaseLineCounter(xmlName + '\n')
                for xmlBuyPriceTemp in xmlShare.findall('buyPrice'):
                    xmlBuyPrice = str(xmlBuyPriceTemp.text)
                    self.printAndIncreaseLineCounter('-> BuyPrice {}\n'.format(xmlBuyPrice))
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
                #self.printAndIncreaseLineCounter(str(share.get_info()) + '\n')
        
                self.stdscr.refresh()
        
                if xmlTrailingStopDate != datetime.datetime.now().strftime('%Y-%m-%d'):
                    historicalDataMaximum = 0.0
                    historicalData = share.get_historical(xmlTrailingStopDate, datetime.datetime.now().strftime('%Y-%m-%d'))
        
                    #self.drawPlot(share, xmlTrailingStopDate)
                    
        
                    for historicalDate in historicalData:
                        #self.printAndIncreaseLineCounter(str(historicalDate) + '\n')
                        if historicalDataMaximum < float(historicalDate['High']):
                            historicalDataMaximum = float(historicalDate['High'])
        
                    self.printAndIncreaseLineCounter('historicalDataMaximum: {}\n'.format(historicalDataMaximum))
                    self.stdscr.refresh()
        
                    if xmlTrailingStopPercentage != 'None':
                        emptyValue = 0
                        possibleTrailingStop = historicalDataMaximum - (historicalDataMaximum * (float(xmlTrailingStopPercentage) / 100))
                        
                        if float(xmlTrailingStopInit) < possibleTrailingStop:
                            prettyPrintResult = prettyPrintResult + str(possibleTrailingStop) + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {}\n'.format(possibleTrailingStop))
                            self.stdscr.refresh()
                        else:
                            prettyPrintResult = prettyPrintResult + xmlTrailingStopInit + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {} - still on init value\n'.format(xmlTrailingStopInit), curses.A_BOLD)
        
                    if xmlTrailingStopAbsolute != 'None':
                        possibleTrailingStop = historicalDataMaximum - float(xmlTrailingStopAbsolute)
                        
                        if float(xmlTrailingStopInit) < possibleTrailingStop:
                            prettyPrintResult = prettyPrintResult + str(possibleTrailingStop) + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {}\n'.format(possibleTrailingStop))
                        else:
                            prettyPrintResult = prettyPrintResult + xmlTrailingStopInit + '\n'
                            self.printAndIncreaseLineCounter('trailingStop {} (still on init value)\n'.format(xmlTrailingStopInit), curses.A_BOLD)
                    if (xmlTrailingStopPercentage == 'None') and (xmlTrailingStopAbsolute == 'None'):
                        prettyPrintResult = prettyPrintResult + 'No stop set\n'
                else:
                    self.printAndIncreaseLineCounter('Trailing stop set today => no historical data available yet')
                    prettyPrintResult = prettyPrintResult + 'Trailing stop set today => no historical data available yet\n'
        
                #prettyPrintResult = prettyPrintResult + ' --- '
        
                self.printAndIncreaseLineCounter('Open: {}\n'.format(share.get_open()))
                self.printAndIncreaseLineCounter('Current: {}\n'.format(share.get_price()))
                self.printAndIncreaseLineCounter('Update time: {}\n'.format(share.get_trade_datetime()))
                #self.printAndIncreaseLineCounter('-----------------\n')
                self.stdscr.hline(self.lineCounter,0, '-', NUMBER_OF_HORIZONTAL_CHARACTERS)
                self.lineCounter = self.lineCounter + 1
                self.printAndIncreaseLineCounter('\n')       
                
                self.plotCandleStickDiagram(xmlName, share, xmlBuyPrice, xmlTrailingStopDate)
                
            self.stdscr.addstr(0, 0, 'pyShares              - has_colors(){} - can_change_color(){}'.format(curses.has_colors(), curses.can_change_color()))
            self.stdscr.refresh()
                
            self.printAndIncreaseLineCounter(prettyPrintResult, curses.A_BOLD)
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
    
    def printAndIncreaseLineCounter(self, text, mode = curses.A_NORMAL):
        if self.lineCounter < MAX_LINES_OF_TERMINAL:
            self.stdscr.addstr(self.lineCounter, 0, text, mode)
            self.lineCounter = self.lineCounter + 1
        else:
            self.stdscr.addstr(self.lineCounter, 0, 'Press a key to show the next page')
            self.stdscr.getch()
            self.stdscr.clear()
            self.lineCounter = 1
            self.stdscr.addstr(self.lineCounter, 0, text, mode)
            self.lineCounter = self.lineCounter + 1
    
    
    def plotCandleStickDiagram(self, shareSymbole, share, buyPrice, startDate):
        dt = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        today = datetime.datetime.now()
        
        date1 = (dt.year, dt.month, dt.day)
        date2 = (today.year, today.month, today.day)
                
        mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        alldays = DayLocator()              # minor ticks on the days
        weekFormatter = DateFormatter('%d. %b')  # e.g., 12. Jan
        dayFormatter = DateFormatter('%d')      # e.g., 12
        
        quotes = quotes_historical_yahoo_ohlc(shareSymbole, date1, date2)
        if len(quotes) == 0:
            raise SystemExit
        
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        ax.xaxis.set_major_locator(mondays)
        ax.xaxis.set_minor_locator(alldays)
        ax.xaxis.set_major_formatter(weekFormatter)
        #ax.xaxis.set_minor_formatter(dayFormatter)
        
        #plot_day_summary(ax, quotes, ticksize=3)
        candlestick_ohlc(ax, quotes, width=0.6, colorup='#83F52C', colordown='r')
        
        ax.xaxis_date()
        ax.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        
        plt.axhline(y=float(buyPrice), linewidth=4, color='r')      
        
        ax.grid(True)
        ax.margins(0.05) # 5% padding in all directions
        
        ax.set_title(share.get_name() + ' - buy price: ' + buyPrice)
        red_patch = mpatches.Patch(color='red', label='buy price') 
        plt.legend(handles=[red_patch])
        plt.show()
    
if __name__ == "__main__":
    #debugInput = raw_input('This is an entry point for remote debugging\n')
    
    tsp = TrailingStopPrinter()
    tsp.printForAllShares()
    