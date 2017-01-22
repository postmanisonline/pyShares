"""
This is written and tested for python 2.7
"""

import datetime
import xml.etree.ElementTree
import curses
import traceback
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from yahoo_finance import Share


MAX_LINES_OF_TERMINAL = 44
NUMBER_OF_HORIZONTAL_CHARACTERS = 200


class TrailingStopPrinter:
    """
    This class is used to determine the current trailing stop value.
    """

    def __init__(self):
        self.line_counter = 1
        try:
            self.stdscr = curses.initscr()
            curses.start_color()
            #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
            #curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
            #curses.use_default_colors()
        except:
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

            xml_shares_root = xml.etree.ElementTree.parse('shares.xml').getroot()

            for xml_share in xml_shares_root.findall('share'):
                xml_name = ''
                xml_units = ''
                xml_buy_price = ''
                xml_trailing_stop_date = ''
                xml_trailing_stop_percentage = ''
                xml_trailing_stop_absolute = ''
                xml_trailing_stop_init = ''

                for xml_name_temp in xml_share.findall('name'):
                    xml_name = str(xml_name_temp.text)
                    self.print_and_increase_line_counter(xml_name + '\n')
                for xml_units_temp in xml_share.findall('units'):
                    xml_units = str(xml_units_temp.text)
                    self.print_and_increase_line_counter('-> Units {}\n'
                                                         .format(xml_units))
                for xml_buy_price_temp in xml_share.findall('buyPrice'):
                    xml_buy_price = str(xml_buy_price_temp.text)
                    self.print_and_increase_line_counter('-> buy price {}\n'
                                                         .format(xml_buy_price))
                for xml_trailing_stop_date_temp in xml_share.findall('trailingStopDate'):
                    xml_trailing_stop_date = str(xml_trailing_stop_date_temp.text)
                    self.print_and_increase_line_counter('-> Date {}\n'
                                                         .format(xml_trailing_stop_date))
                for xml_trailing_stop_percentage_temp in xml_share.findall('trailingStopPercentage'):
                    xml_trailing_stop_percentage = str(xml_trailing_stop_percentage_temp.text)
                    self.print_and_increase_line_counter('-> Percentage {}\n'\
                                                     .format(xml_trailing_stop_percentage))
                for xml_trailing_stop_absolute_temp in xml_share.findall('trailingStopAbsolute'):
                    xml_trailing_stop_absolute = str(xml_trailing_stop_absolute_temp.text)
                    self.print_and_increase_line_counter('-> Absolute {}\n'\
                                                     .format(xml_trailing_stop_absolute))
                for xml_trailing_stop_init_temp in xml_share.findall('trailingStopInit'):
                    xml_trailing_stop_init = str(xml_trailing_stop_init_temp.text)
                    self.print_and_increase_line_counter('-> Init {}\n'
                                                         .format(xml_trailing_stop_init))

                share = Share(xml_name)
                pretty_print_result = pretty_print_result + share.get_name() + ': '
                self.print_and_increase_line_counter(share.get_name() + '\n')
                #self.print_and_increase_line_counter(str(share.get_info()) + '\n')

                self.stdscr.refresh()

                if xml_trailing_stop_date != datetime.datetime.now().strftime('%Y-%m-%d'):
                    historical_data_maximum = 0.0
                    historical_data = share.get_historical(xml_trailing_stop_date,
                                                           datetime.datetime.now().strftime('%Y-%m-%d'))

                    #self.drawPlot(share, xml_trailing_stop_date)


                    for historical_date in historical_data:
                        #self.print_and_increase_line_counter(str(historical_date) + '\n')
                        if historical_data_maximum < float(historical_date['High']):
                            historical_data_maximum = float(historical_date['High'])

                    self.print_and_increase_line_counter('historical_data_maximum: {}\n'\
                                                     .format(historical_data_maximum))
                    self.stdscr.refresh()

                    if xml_trailing_stop_percentage != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        (historical_data_maximum * (float(xml_trailing_stop_percentage) / 100))

                        if float(xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + \
                                str(possible_trailing_stop) + '\n'
                            self.print_and_increase_line_counter('trailingStop {}\n'\
                                                             .format(possible_trailing_stop))
                            self.stdscr.refresh()
                        else:
                            pretty_print_result = pretty_print_result + xml_trailing_stop_init + '\n'
                            self.print_and_increase_line_counter('trailingStop {} - still on init value\n'\
                            .format(xml_trailing_stop_init), curses.A_BOLD)

                    if xml_trailing_stop_absolute != 'None':
                        possible_trailing_stop = historical_data_maximum - \
                        float(xml_trailing_stop_absolute)

                        if float(xml_trailing_stop_init) < possible_trailing_stop:
                            pretty_print_result = pretty_print_result + str(possible_trailing_stop) + '\n'
                            self.print_and_increase_line_counter('trailingStop {}\n'\
                                                             .format(possible_trailing_stop))
                        else:
                            pretty_print_result = pretty_print_result + xml_trailing_stop_init + '\n'
                            self.print_and_increase_line_counter('trailingStop {} (still on init value)\n'
                                .format(xml_trailing_stop_init), curses.A_BOLD)

                    if (xml_trailing_stop_percentage == 'None') and\
                        (xml_trailing_stop_absolute == 'None'):
                        pretty_print_result = pretty_print_result + 'No stop set\n'
                else:
                    self.print_and_increase_line_counter('Trailing stop set today '+\
                                                     '=> no historical data available yet')
                    pretty_print_result = pretty_print_result + \
                    'Trailing stop set today => no historical data available yet\n'

                #pretty_print_result = pretty_print_result + ' --- '

                self.print_and_increase_line_counter('Open: {}\n'
                                                     .format(share.get_open()))
                self.print_and_increase_line_counter('Current: {}\n'
                                                     .format(share.get_price()))
                self.print_and_increase_line_counter('Update time: {}\n'
                                                     .format(share.get_trade_datetime()))
                #self.print_and_increase_line_counter('-----------------\n')
                self.stdscr.hline(self.line_counter, 0, '-', NUMBER_OF_HORIZONTAL_CHARACTERS)
                self.line_counter = self.line_counter + 1
                self.print_and_increase_line_counter('\n')

                current_win_or_loss = (int(xml_units) * float(share.get_price())) - \
                                        (int(xml_units) * float(xml_buy_price))

                self.plot_candle_stick_diagram(share_symbole=xml_name, share=share, units=xml_units, buy_price=xml_buy_price, win_or_loss=current_win_or_loss, start_date=xml_trailing_stop_date)

            self.stdscr.addstr(0, 0, 'pyShares              - has_colors(){} - can_change_color(){}'\
                               .format(curses.has_colors(), curses.can_change_color()))
            self.stdscr.refresh()

            self.print_and_increase_line_counter(pretty_print_result, curses.A_BOLD)
            self.line_counter = self.line_counter + pretty_print_result.count('\n')

            self.print_and_increase_line_counter('Press a key to stop')
            self.stdscr.refresh()
            self.stdscr.getch()
        except BaseException as base_exception:
            with open('error_log.txt', 'w') as error_log:
                error_log.write(str(base_exception))
                error_log.write(str(traceback.print_exc()))
                error_log.write('line_counter was ' + str(self.line_counter))
            self.print_and_increase_line_counter('exception {}'.format(base_exception))
            self.stdscr.addstr(0, 0, 'Something went terribly wrong               ')
            self.stdscr.getch()
        finally:
            #deinit stdscr
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    def print_and_increase_line_counter(self, text, mode=curses.A_NORMAL):
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


    def plot_candle_stick_diagram(self, share_symbole, share, units, buy_price, win_or_loss, start_date):
        """
        This method is used for printing candle stick diagrams.
        """
        dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        today = datetime.datetime.now()

        date1 = (dt.year, dt.month, dt.day)
        date2 = (today.year, today.month, today.day)

        mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        alldays = DayLocator()              # minor ticks on the days
        week_formatter = DateFormatter('%d. %b')  # e.g., 12. Jan

        quotes = quotes_historical_yahoo_ohlc(share_symbole, date1, date2)
        if len(quotes) == 0:
            raise SystemExit

        fig, axes = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        axes.xaxis.set_major_locator(mondays)
        axes.xaxis.set_minor_locator(alldays)
        axes.xaxis.set_major_formatter(week_formatter)

        #plot_day_summary(axes, quotes, ticksize=3)
        candlestick_ohlc(axes, quotes, width=0.6, colorup='#83F52C', colordown='r')

        axes.xaxis_date()
        axes.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

        plt.axhline(y=float(buy_price), linewidth=4, color='r')

        axes.grid(True)
        axes.margins(0.05) # 5% padding in all directions

        axes.set_title(share.get_name() + ' - buy price: ' + buy_price + \
                     ' - units: ' + units + ' - atm: ' + str(win_or_loss))
        red_patch = mpatches.Patch(color='red', label='buy price')
        plt.legend(handles=[red_patch])
        plt.show()

if __name__ == "__main__":
    #debugInput = raw_input('This is an entry point for remote debugging\n')

    tsp = TrailingStopPrinter()
    tsp.print_for_all_shares()
    