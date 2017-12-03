"""
This is written and tested for python 2.7
matplotlib uses http://ichart.yahoo.com
"""

import datetime
import curses
import traceback
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import urllib2
import re


from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY, date2num
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from yahoo_finance import Share, YQLQueryError, YQLResponseMalformedError

import xml_share_repository as xsr
from xml_share import xml_share
from next_action import next_action


CLOSING_VALUE_POSITION = 4
DATE_POSITION = 0
LABEL_ROTATION = 45
MAX_LINES_OF_TERMINAL = 44
NUMBER_OF_HORIZONTAL_CHARACTERS = 200
PADDING = 0.05
VLINE_LOW_SCALE = 0.9
VLINE_HIGH_SCALE = 1.1


class TrailingStopPrinter:
    """
    This class is used to determine the current trailing stop value.
    """

    def __init__(self):
        self.line_counter = 1
        try:
            self.stdscr = curses.initscr()
        except curses.error:
            print 'Could not init curses'

    def tradegateLiveData(self):
        """
        This function prints all the textual information about a share.
        """            
        
        try:
            curses.start_color()
            curses.use_default_colors()
            
            for i in range(0, curses.COLORS):
                curses.init_pair(i + 1, i, -1)         
            
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self.line_counter = 0
            share_repository = xsr.xml_share_repository()
            
            if len(sys.argv)==1:
                share_repository.built_up_repository()
            elif len(sys.argv)==2 and sys.argv[1]=='-w':
                share_repository.built_up_repository(share_file='watchlist.xml')
            else:
                self.my_print('Arguments cannot be processed', colorPair=curses.color_pair(0))

            shareCounter = 0
            
            while True:
                req = urllib2.Request('http://www.tradegate.de/indizes.php?art=aktien&index=DE000A1EXRV0') 
                response = urllib2.urlopen(req) 
                page = response.read()
                
                #parse the website for shares
                tradegateWebsiteShares = re.findall('name_[0-9]*.*isin=.*</td>\s*<td.*bid_[0-9]*.*</td>',page)
                daxShares = {}
                
                #foreach share get the name and current value
                for tradegateWebsiteShare in tradegateWebsiteShares:
                    tradegateWebsiteShareNameUncout = re.search('">.+<',(re.search('>.+</a></td>', tradegateWebsiteShare).group(0))).group(0)
                    tradegateWebsiteShareName = tradegateWebsiteShareNameUncout[2:len(tradegateWebsiteShareNameUncout)-5]
                    tradegateWebsiteSharePrice = re.search('[0-9]+,[0-9]+', (re.search('>[0-9]+,[0-9]+</td>', tradegateWebsiteShare).group(0))).group(0)
                    daxShares [tradegateWebsiteShareName] = tradegateWebsiteSharePrice.replace(',','.')
                
                for xml_share in share_repository.xml_shares:
                    try:    
                        shareCounter = shareCounter + 1
                        
                        currentBid = daxShares.get(xml_share.xml_name.replace('&', '&amp;'))
                                                                       
                        current_win_or_loss = 0
                    
                        if int(xml_share.xml_units) != 0:
                            if xml_share.xml_buy_price != 'None':
                                current_win_or_loss = (int(xml_share.xml_units) * float(currentBid)) - \
                                                (int(xml_share.xml_units) * float(xml_share.xml_buy_price))
                            
                            # No stop set at all
                            if xml_share.xml_stop_expiration == 'None':
                                self.my_print('No stop set for ' + xml_share.xml_name, curses.color_pair(4))
                            else:   
                                # Stop is about to expire
                                expirationDate = datetime.date(int(xml_share.xml_stop_expiration.split("-")[0]),
                                                 int(xml_share.xml_stop_expiration.split("-")[1]),
                                                 int(xml_share.xml_stop_expiration.split("-")[2]))
                                
                                if expirationDate < (datetime.date.today() + (datetime.timedelta(days=20))):
                                    self.my_print('Stop is about to expire for ' + xml_share.xml_name, curses.color_pair(5))
                                
                            if current_win_or_loss >= 0:
                                self.my_print(str(shareCounter) + ': ' + xml_share.xml_name + ' (' + xml_share.xml_buy_price + ' -> ' + currentBid + ')' + ' => ' + str(current_win_or_loss) + '\n', curses.color_pair(3))
                            else:
                                self.my_print(str(shareCounter) + ': ' + xml_share.xml_name + ' (' + xml_share.xml_buy_price + ' -> ' + currentBid + ')' + ' => ' + str(current_win_or_loss) + '\n', curses.color_pair(2))
                            #self.my_print(str(share.get_info()) + '\n')
                    except:
                        with open('error_log.txt', 'a') as error_log:
                            error_log.write(str(traceback.print_exc()) + '\n')
                            error_log.write('xml_share was' + str(xml_share) + '\n')
                            error_log.write('currentBid was ' + str(currentBid) + '\n')
                        self.my_print('xml_share', colorPair=curses.color_pair(0))
                        self.stdscr.addstr(0, 0, 'Something went terribly wrong => xml_share unknown exception              ')
                        self.stdscr.getch()

                self.my_print(str(datetime.datetime.now()), curses.color_pair(1))
                self.stdscr.refresh()
                time.sleep(15)
                self.stdscr.clear()
                shareCounter = 0
                self.line_counter = 0
            
        except Exception as e:
            with open('error_log.txt', 'a') as error_log:
                error_log.write(str(traceback.print_exc()) + '\n')
                error_log.write(str(e) + '\n')
                error_log.write('line_counter was ' + str(self.line_counter) + '\n')
            self.my_print('unknown exception', colorPair=curses.color_pair(0))
            self.my_print(str(e), colorPair=curses.color_pair(0))
            self.stdscr.addstr(0, 0, 'Something went terribly wrong => unknown exception              ')
            self.stdscr.getch()
        finally:
            #deinit stdscr
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
       
            
    def print_for_all_shares(self):
        """
        This function prints all the textual information about a share.
        """
        try:
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self.stdscr.addstr(0, 0, 'pyShares')

            pretty_print_result = ''

            share_repository = xsr.xml_share_repository()
            
            if len(sys.argv)==1:
                share_repository.built_up_repository()
            elif len(sys.argv)==2 and sys.argv[1]=='-w':
                share_repository.built_up_repository(share_file='watchlist.xml')
            else:
                self.my_print('Arguments cannot be processed')

            shareCounter = 0
            
            for xml_share in share_repository.xml_shares:
                try:
                    self.stdscr.addstr(0, 0, 'Refreshing - share ' + str(shareCounter))
                    self.stdscr.refresh()
    
                    shareCounter = shareCounter + 1
                    share = Share(xml_share.xml_name)
                    pretty_print_result = pretty_print_result + str(shareCounter) + ': ' + share.get_name() + ': '
                    self.my_print(str(shareCounter) + ': ' + share.get_name() + '\n')
                    #self.my_print(str(share.get_info()) + '\n')
                except:
                    with open('error_log.txt', 'a') as error_log:
                        error_log.write(str(traceback.print_exc()) + '\n')
                        error_log.write('xml_share was' + str(xml_share) + '\n')
                    self.my_print('xml_share')
                    self.stdscr.addstr(0, 0, 'Something went terribly wrong => xml_share unknown exception              ')
                    self.stdscr.getch()

            self.my_print('Select a share or press \'e\' to exit')
            self.stdscr.refresh()

            next_action = self.wait_for_next_action()
            
            while next_action.quit_pyShares == False:    
                xml_share = share_repository.xml_shares[int(next_action.next_share)-1]
                share = Share(xml_share.xml_name) # user selections start with 1 
                
                today = datetime.datetime.now()

                if (xml_share.xml_trailing_stop_date != 'None') and (xml_share.xml_trailing_stop_date != today.strftime('%Y-%m-%d')):
                    historical_data_maximum = 0.0
                    historical_data = share.get_historical(xml_share.xml_trailing_stop_date,
                                                           today.strftime('%Y-%m-%d'))

                    for historical_date in historical_data:
                        if historical_data_maximum < float(historical_date['High']):
                            historical_data_maximum = float(historical_date['High'])

                    #self.my_print('historical_data_maximum: {}\n'\
                     #                                .format(historical_data_maximum))
                    self.stdscr.refresh()

                    if xml_share.xml_trailing_stop_percentage != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        (historical_data_maximum * (float(xml_share.xml_trailing_stop_percentage) / 100))

                        if float(xml_share.xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + \
                                str(possible_trailing_stop) + '\n'
                            #self.my_print('trailingStop {}\n'\
                            #                                 .format(possible_trailing_stop))
                            self.stdscr.refresh()
                        else:
                            pretty_print_result = pretty_print_result + xml_share.xml_trailing_stop_init + '\n'
                            #self.my_print('trailingStop {} - still on init value\n'\
                            #.format(xml_share.xml_trailing_stop_init), curses.A_BOLD)

                    if xml_share.xml_trailing_stop_absolute != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        float(xml_share.xml_trailing_stop_absolute)

                        if float(xml_share.xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + str(possible_trailing_stop) + '\n'
                        else:
                            pretty_print_result = pretty_print_result + xml_share.xml_trailing_stop_init + '\n'

                    if (xml_share.xml_trailing_stop_percentage == 'None') and\
                        (xml_share.xml_trailing_stop_absolute == 'None'):
                        pretty_print_result = pretty_print_result + 'No stop set\n'
                else:
                    pretty_print_result = pretty_print_result + \
                    'Trailing stop set today => no historical data available yet\n'

                self.line_counter = self.line_counter + 1

                current_win_or_loss = 0
                
                if xml_share.xml_buy_price != 'None':
                    current_win_or_loss = (int(xml_share.xml_units) * float(share.get_price())) - \
                                        (int(xml_share.xml_units) * float(xml_share.xml_buy_price))

                self.stdscr.refresh()
                
                try:
                    self.plot_candle_stick_diagram(xml_share=xml_share,
                                               share=share,
                                               current_price=share.get_price(),
                                               today_open=share.get_open(),
                                               win_or_loss=current_win_or_loss)
                except:
                    with open('error_log.txt', 'a') as error_log:
                        error_log.write(str(traceback.print_exc()) + '\n')
                        error_log.write('line_counter was ' + str(self.line_counter) + '\n')
                        error_log.write(str(xml_share) + '\n')
                        error_log.write(str(share) + '\n')
                        error_log.write(str(share.get_price) + '\n')
                        error_log.write(str(share.get_open) + '\n')
                        error_log.write(str(current_win_or_loss) + '\n')
                    self.my_print('unknown exception')
                    self.stdscr.addstr(0, 0, 'Something went terribly wrong => unknown exception              ')
                    self.stdscr.getch()
                
                next_action = self.wait_for_next_action()

            self.my_print(pretty_print_result, curses.A_BOLD)
            self.line_counter = self.line_counter + pretty_print_result.count('\n')

            self.my_print('Press ENTER to exit')
            self.stdscr.refresh()
            self.stdscr.getch()
        except BaseException as base_exception:
            with open('error_log.txt', 'a') as error_log:
                error_log.write(str(base_exception) + '\n')
                error_log.write(str(traceback.print_exc()) + '\n')
                error_log.write('line_counter was ' + str(self.line_counter) + '\n')
            self.stdscr.addstr(0, 0, 'Something went terribly wrong               ')
            self.stdscr.getch()
        except YQLQueryError as yql_err:
            with open('error_log.txt', 'a') as error_log:
                error_log.write(str(yql_err) + '\n')
                error_log.write(str(traceback.print_exc()) + '\n')
                error_log.write('line_counter was ' + str(self.line_counter) + '\n')
            self.stdscr.addstr(0, 0, 'Something went terribly wrong => could not receive data from server              ')
            self.stdscr.getch()
        except YQLResponseMalformedError as yql_err:
            with open('error_log.txt', 'a') as error_log:
                error_log.write(str(yql_err) + '\n')
                error_log.write(str(traceback.print_exc()) + '\n')
                error_log.write('line_counter was ' + str(self.line_counter) + '\n')
            self.stdscr.addstr(0, 0, 'Something went terribly wrong => could not receive data from server              ')
            self.stdscr.getch()
        except:
            with open('error_log.txt', 'a') as error_log:
                error_log.write(str(traceback.print_exc()) + '\n')
                error_log.write('line_counter was ' + str(self.line_counter) + '\n')
            self.my_print('unknown exception')
            self.stdscr.addstr(0, 0, 'Something went terribly wrong => unknown exception              ')
            self.stdscr.getch()
        finally:
            #deinit stdscr
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()


    def wait_for_next_action(self):
        nextActionDetermined = False
        return_next = next_action(next_share='-1', quit_pyShares=False)
                
        while nextActionDetermined == False:
            nextActionString = self.stdscr.getstr()
        
            try:
                int(nextActionString)
                nextActionDetermined = True
                return_next = next_action(next_share=nextActionString, quit_pyShares=False)
                self.stdscr.addstr(0, 0, 'pyShares')
            except ValueError:                
                if nextActionString == 'e':
                    return_next = next_action(next_share='-1', quit_pyShares=True)
                    nextActionDetermined = True
                    self.stdscr.addstr(0, 0, 'pyShares - quitting')
                else:
                    nextActionDetermined = False
                    self.stdscr.addstr(0, 0, 'pyShares - unknown input')
        
            self.stdscr.refresh()
            
        return return_next  
    
    
    def my_print(self, text, colorPair, mode=curses.A_NORMAL):
        """
        This method is used for printing one line
        to the console and increment the line counter.
        """
        if self.line_counter < MAX_LINES_OF_TERMINAL:
            self.stdscr.addstr(self.line_counter, 0, text, colorPair)
            #self.stdscr.addstr(self.line_counter, 0, text, mode)
            self.line_counter = self.line_counter + 1
        else:
            self.stdscr.addstr(self.line_counter, 0, 'Press a key to show the next page')
            self.stdscr.getch()
            self.stdscr.clear()
            self.line_counter = 1
            self.stdscr.addstr(self.line_counter, 0, text, mode)
            self.line_counter = self.line_counter + 1


    def plot_candle_stick_diagram(self, xml_share, share, current_price, today_open, win_or_loss):
        """
        This method is used for printing a single candle stick diagram.
        """       

        today = datetime.datetime.now()
        converted_buy_date = today
        
        if xml_share.xml_buy_date!='None':    
            converted_buy_date = datetime.datetime.strptime(xml_share.xml_buy_date, "%Y-%m-%d")
        
        mondays = WeekdayLocator(MONDAY,interval=4)     # major ticks on the mondays
        alldays = DayLocator()                          # minor ticks on the days
        week_formatter = DateFormatter('%Y-%m-%d')      # e.g., 12. Jan

        with open('error_log.txt', 'a') as error_log:
                error_log.write(xml_share.xml_name + '\n')
                
        quotes = quotes_historical_yahoo_ohlc(xml_share.xml_name, 
                                              today - datetime.timedelta(12*365/12),
                                              (today.year, today.month, today.day),adjusted=False)

        #fake the candle of today
        #d, open, high, low, close, volume
        temp_high = 0.0
        temp_low = 0.0
        temp_close = 0.0

        if today_open <= current_price:
            temp_low = float(today_open)
            temp_high = float(current_price)
            temp_close = float(current_price)
        else:
            temp_low = float(current_price)
            temp_high = float(today_open)
            temp_close = float(current_price)

        values_of_today = (date2num(today), float(today_open),
                           temp_high,
                           temp_low,
                           temp_close)
         
        quotes.append(values_of_today)

        if len(quotes) == 0:
            raise SystemExit

        fig, axes = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        axes.xaxis.set_major_locator(mondays)
        axes.xaxis.set_minor_locator(alldays)
        axes.xaxis.set_major_formatter(week_formatter)

        candlestick_ohlc(axes, quotes, width=1, colorup='#83F52C', colordown='r')

        axes.xaxis_date()
        axes.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=LABEL_ROTATION, horizontalalignment='right')

        # print the buy price
        if xml_share.xml_buy_price!='None':
            plt.axhline(y=float(xml_share.xml_buy_price), linewidth=2, color='r')
            axes.set_title(share.get_name() + ' - buy price: ' + xml_share.xml_buy_price + \
                           ' - units: ' + xml_share.xml_units + ' - win or loss: ' + str(win_or_loss))
        else:
            axes.set_title(share.get_name() + ' - buy price: ' + \
                           ' - units: ' + xml_share.xml_units + ' - win or loss: ' + str(win_or_loss))

        # padding
        axes.grid(True)
        axes.margins(PADDING) # 5% padding in all directions

        # create labels
        red_patch = mpatches.Patch(color='red', label='buy price')
        green_patch = mpatches.Patch(color='green', label='last candle: today\'s estimated value')
        blue_patch = mpatches.Patch(color='blue', label='buy date')
        EMA20_patch = mpatches.Patch(color='red', label='EMA20')
        EMA50_patch = mpatches.Patch(color='green', label='EMA50') 
        
        EMA_days = []
        only_closing_values = []
          
        for entry in quotes:
            EMA_days.append(entry[DATE_POSITION])
            only_closing_values.append(entry[CLOSING_VALUE_POSITION])
         
        plt.plot(EMA_days[21:], self.exp_moving_average(historical_values=only_closing_values, time_window=20)[21:], 'r')
        plt.plot(EMA_days[51:], self.exp_moving_average(historical_values=only_closing_values, time_window=50)[51:], 'g')
          
        # if there is a trailing stop date then print it
        if xml_share.xml_trailing_stop_date != 'None':
            converted_ts_date = datetime.datetime.strptime(xml_share.xml_trailing_stop_date, "%Y-%m-%d")
            plt.vlines(x=converted_buy_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_high*VLINE_HIGH_SCALE, colors='b')
            plt.vlines(x=converted_ts_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_low*VLINE_HIGH_SCALE, colors='m')
 
            magenta_patch = mpatches.Patch(color='magenta', label='trailing stop date')
            plt.legend(handles=[red_patch, green_patch, blue_patch, magenta_patch, EMA20_patch, EMA50_patch], loc=2, prop={'size':7})
        else:
            plt.vlines(x=converted_buy_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_low*VLINE_HIGH_SCALE, colors='b')
            plt.legend(handles=[red_patch, green_patch, blue_patch, EMA20_patch, EMA50_patch], loc=2, prop={'size':7})
          
 
#         if not os.path.exists('./exports'):
#             os.makedirs('./exports')

        #plt.savefig('./exports/' + xml_share.xml_name + '.png', dpi=400) 
        plt.show()
                
     
      
    def exp_moving_average(self, historical_values, time_window):
        weigths = np.exp(np.linspace(-1., 0., time_window))
        weigths /= weigths.sum()
        a = np.convolve(historical_values, weigths)[:len(historical_values)]
        a[:time_window] = a[time_window]
        return a  
        

if __name__ == "__main__":

    trailing_stop_printer = TrailingStopPrinter()
    
    # for remote debugging
    #time.sleep(25)
    #trailing_stop_printer.print_for_all_shares()
    #trailing_stop_printer.liveStats()
    trailing_stop_printer.tradegateLiveData()
    