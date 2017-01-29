"""
This is written and tested for python 2.7
"""

import datetime
import curses
import traceback
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY, date2num
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from yahoo_finance import Share

import xml_share_repository as xsr


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
            curses.start_color()
        except curses.error:
            print 'Could not init curses'


    def print_for_all_shares(self):
        """
        This function prints all the textual information about a share.
        """
        try:
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self.stdscr.addstr(0, 0, 'pyShares')
            self.stdscr.addstr(0, 0, 'Refreshing ...')

            pretty_print_result = ''

            share_repository = xsr.xml_share_repository()
            share_repository.built_up_repository()


            for temp_share in share_repository.xml_shares:
                xml_share = share_repository.xml_shares[temp_share]

#                 self.my_print(str(xml_share.xml_name) + '\n')
#                 self.my_print(str(xml_share.xml_units) + '\n')
#                 self.my_print(str(xml_share.xml_buy_price) + '\n')
#                 self.my_print(str(xml_share.xml_trailing_stop_date) + '\n')
#                 self.my_print(str(xml_share.xml_trailing_stop_percentage) + '\n')
#                 self.my_print(str(xml_share.xml_trailing_stop_absolute) + '\n')
#                 self.my_print(str(xml_share.xml_trailing_stop_init) + '\n')

                share = Share(xml_share.xml_name)
                pretty_print_result = pretty_print_result + share.get_name() + ': '
                self.my_print(share.get_name() + '\n')
                #self.my_print(str(share.get_info()) + '\n')

                self.stdscr.refresh()

                today = datetime.datetime.now()

                if (xml_share.xml_trailing_stop_date != 'None') and (xml_share.xml_trailing_stop_date != today.strftime('%Y-%m-%d')):
                    historical_data_maximum = 0.0
                    historical_data = share.get_historical(xml_share.xml_trailing_stop_date,
                                                           today.strftime('%Y-%m-%d'))


                    for historical_date in historical_data:
                        if historical_data_maximum < float(historical_date['High']):
                            historical_data_maximum = float(historical_date['High'])

                    self.my_print('historical_data_maximum: {}\n'\
                                                     .format(historical_data_maximum))
                    self.stdscr.refresh()

                    if xml_share.xml_trailing_stop_percentage != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        (historical_data_maximum * (float(xml_share.xml_trailing_stop_percentage) / 100))

                        if float(xml_share.xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + \
                                str(possible_trailing_stop) + '\n'
                            self.my_print('trailingStop {}\n'\
                                                             .format(possible_trailing_stop))
                            self.stdscr.refresh()
                        else:
                            pretty_print_result = pretty_print_result + xml_share.xml_trailing_stop_init + '\n'
                            self.my_print('trailingStop {} - still on init value\n'\
                            .format(xml_share.xml_trailing_stop_init), curses.A_BOLD)

                    if xml_share.xml_trailing_stop_absolute != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        float(xml_share.xml_trailing_stop_absolute)

                        if float(xml_share.xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + str(possible_trailing_stop) + '\n'
                            self.my_print('trailingStop {}\n'\
                                                             .format(possible_trailing_stop))
                        else:
                            pretty_print_result = pretty_print_result + xml_share.xml_trailing_stop_init + '\n'
                            self.my_print('trailingStop {} (still on init value)\n'
                                          .format(xml_share.xml_trailing_stop_init), curses.A_BOLD)

                    if (xml_share.xml_trailing_stop_percentage == 'None') and\
                        (xml_share.xml_trailing_stop_absolute == 'None'):
                        pretty_print_result = pretty_print_result + 'No stop set\n'
                else:
                    self.my_print('Trailing stop set today '+\
                                                     '=> no historical data available yet')
                    pretty_print_result = pretty_print_result + \
                    'Trailing stop set today => no historical data available yet\n'

                #pretty_print_result = pretty_print_result + ' --- '

                self.my_print('Open: {}\n'.format(share.get_open()))
                self.my_print('Current: {}\n'.format(share.get_price()))
                self.my_print('Update time: {}\n'.format(share.get_trade_datetime()))
                #self.my_print('-----------------\n')
                self.stdscr.hline(self.line_counter, 0, '-', NUMBER_OF_HORIZONTAL_CHARACTERS)
                self.line_counter = self.line_counter + 1
                self.my_print('\n')

                current_win_or_loss = (int(xml_share.xml_units) * float(share.get_price())) - \
                                        (int(xml_share.xml_units) * float(xml_share.xml_buy_price))

                self.stdscr.refresh()
                self.plot_candle_stick_diagram(share_symbole=xml_share.xml_name, share=share, units=xml_share.xml_units, buy_price=xml_share.xml_buy_price, buy_date=xml_share.xml_buy_date, current_price=share.get_price(), today_open=share.get_open(), win_or_loss=current_win_or_loss, trailingstop_date=xml_share.xml_trailing_stop_date)

            self.stdscr.addstr(0, 0, 'pyShares              - has_colors(){} - can_change_color(){}'\
                               .format(curses.has_colors(), curses.can_change_color()))
            self.stdscr.refresh()

            self.my_print(pretty_print_result, curses.A_BOLD)
            self.line_counter = self.line_counter + pretty_print_result.count('\n')

            self.my_print('Press a key to stop')
            self.stdscr.refresh()
            self.stdscr.getch()
        except BaseException as base_exception:
            with open('error_log.txt', 'w') as error_log:
                error_log.write(str(base_exception))
                error_log.write(str(traceback.print_exc()))
                error_log.write('line_counter was ' + str(self.line_counter))
            self.my_print('exception {}'.format(base_exception))
            self.stdscr.addstr(0, 0, 'Something went terribly wrong               ')
            self.stdscr.getch()
        finally:
            #deinit stdscr
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    def my_print(self, text, mode=curses.A_NORMAL):
        """
        This method is used for printing one line
        to the console and increment the line counter.
        """
        if self.line_counter < MAX_LINES_OF_TERMINAL:
            self.stdscr.addstr(self.line_counter, 0, text, mode)
            self.line_counter = self.line_counter + 1
        else:
            self.stdscr.addstr(self.line_counter, 0, 'Press a key to show the next page')
            self.stdscr.getch()
            self.stdscr.clear()
            self.line_counter = 1
            self.stdscr.addstr(self.line_counter, 0, text, mode)
            self.line_counter = self.line_counter + 1


    def plot_candle_stick_diagram(self, share_symbole, share, units, buy_price, buy_date, current_price, today_open, win_or_loss, trailingstop_date):
        """
        This method is used for printing candle stick diagrams.
        """

        converted_buy_date = datetime.datetime.strptime(buy_date, "%Y-%m-%d")
        today = datetime.datetime.now()

        # the last six months
        date1 = today - datetime.timedelta(6*365/12)
        date2 = (today.year, today.month, today.day)

        mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        alldays = DayLocator()              # minor ticks on the days
        #week_formatter = DateFormatter('%d. %b')  # e.g., 12. Jan
        week_formatter = DateFormatter('%Y-%m-%d')  # e.g., 12. Jan

        quotes = quotes_historical_yahoo_ohlc(share_symbole, date1, date2)

        #fake the candle of today
        #d, open, high, low, close, volume
        temp_high = 0
        temp_low = 0
        temp_close = 0

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

        candlestick_ohlc(axes, quotes, width=0.6, colorup='#83F52C', colordown='r')

        axes.xaxis_date()
        axes.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=LABEL_ROTATION, horizontalalignment='right')

        # print the buy price
        plt.axhline(y=float(buy_price), linewidth=2, color='r')

        # padding
        axes.grid(True)
        axes.margins(PADDING) # 5% padding in all directions

        axes.set_title(share.get_name() + ' - buy price: ' + buy_price + \
                     ' - units: ' + units + ' - win or loss: ' + str(win_or_loss))

        # create labels
        red_patch = mpatches.Patch(color='red', label='buy price')
        green_patch = mpatches.Patch(color='green', label='last candle: today\'s estimated value')
        blue_patch = mpatches.Patch(color='blue', label='buy date')

        # if there is a trailing stop date then print it
        if trailingstop_date != 'None':
            converted_ts_date = datetime.datetime.strptime(trailingstop_date, "%Y-%m-%d")
            plt.vlines(x=converted_buy_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_high*VLINE_HIGH_SCALE, colors='b')
            plt.vlines(x=converted_ts_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_low*VLINE_HIGH_SCALE, colors='m')

            magenta_patch = mpatches.Patch(color='magenta', label='trailing stop date')
            plt.legend(handles=[red_patch, green_patch, blue_patch, magenta_patch], loc=2)
        else:
            plt.legend(handles=[red_patch, green_patch, blue_patch], loc=2)
            plt.vlines(x=converted_buy_date, ymin=temp_low*VLINE_LOW_SCALE, ymax=temp_low*VLINE_HIGH_SCALE, colors='b')

        #plt.show(block=False)
        plt.show()

if __name__ == "__main__":
    #debugInput = raw_input('This is an entry point for remote debugging\n')

    trailing_stop_printer = TrailingStopPrinter()
    trailing_stop_printer.print_for_all_shares()
    