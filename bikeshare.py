"""Explore bikeshare data
File: bikeshare.py
Created by: Alan Glasper

Explores datasets provided by Udacity as a project within the Data
Analyst Nanodegree (DAND Term 1 cohort: June 2018).

This file was built to run in a python 3 environment.
Style is PEP8 compliant except: continuation lines are indented
8 spaces.

The following functions include assumptions specific to bikeshare data:
get_filters - Prompt user to enter filtering requirements.
load_data - Load bikeshare data from csv files based on filtering.
time_stats - Summary statistics of most frequent trip start times.
station_stats - Summary statistics of start and end stations and paths.
trip_duration_stats - Summary statistics of trip durations.
user_stats - Summary statistics of user characteristics.
main_loop - Main control loop to interact with user and display data.
main - Process command line switches and handle exceptions in main_loop.

The following functions will also work generically:
clean_input - Handling of user input including KeyboardInterrupt.
list_csv_files - Return filenames of csv files in working directory.
match_start_string - Return options in list that match substring.
unique_selection - Interact with user to identify unique option in list.
display_categories - Category and result columns adjusted to data.
display_counts_shares - Display category column counts and shares.
display_most_common - Display the most frequent item(s) in column.
display_duration - Display value in seconds as more readable time units.

No exceptions are raised in this file. There is exception handling in
main() and the clean_input() function. In addition to a general
exception catchall (non-silent), KeyboardInterrupt is intercepted to
cleanly exit the program. A command line switch is provided
(-d, --debug) that allows this exception handling to be switched off
during development or investigation of problems.

Invoke with '-h_ or --help' to display all optional arguments.
"""
import time
import numpy as np
import pandas as pd
# argparse - Needed for function "main"
import argparse
# glob - Needed for function "list_csv_files"
import glob
# ---------------------------------------------------------------------
# USER CONSTANTS - This section contains structures extendable in usage

# This is the list of supported files. Only files that are in this list
# AND in the working directory will be offered to user for selection.
# Assumes that filenames are not duplicated with different case.
# Assumes no missing data in any columns except gender & birth year.
# USER: add files as they become available, including test files.
# Not all files need to be present to use the program.
CITY_DATA = { 'Chicago': 'chicago.csv',
        'New York City': 'new_york_city.csv',
        'Washington': 'washington.csv',
        'Add new city files here!': 'newcityfile.csv',
        'Test Data': 'testdata.csv',
        }
# ---------------------------------------------------------------------
# A quick map of months - simpler than importing calendar.
# First entry is a Dummy so no need to change start index from 1 to 0).
# USER: add months as they become available in the data files.
# TODO Having a special value is not pythonic? Consider removing dummy.
MONTHS = ('Dummy', 'January', 'February', 'March', 'April', 'May', 'June',
       #'July', 'August', 'September', 'October', 'November',
       #'December',
        )

# MODULE CONSTANTS
# Numbering of days in the data files uses standard where Sunday is 0.
WEEKDAYS = ('Sunday', 'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday',
        )

# Strings that are used in multiple places are defined once here.
QUIT_RECOGNIZED = 'You requested to quit. The program has ended.'
SIGNOFF = '\nThanks for using this bikeshare data explorer! \n'


def clean_input(prompt):
    """Obtain input from user and handle KeyboardInterrupt cleanly.

    There is a special value for the return string:
        "Quit" - If a KeyboardInterrupt occurs during input.
    Args:
        (str) prompt - Text to display to user when requesting input.
    Returns:
        (str) Input from user returned by input function, or "Quit".
    """
    try:
        return input(prompt)
    # There is a general handling of KeyboardInterrupt in main() but
    # here it leads to a cleaner exit as the option to quit is returned.
    except KeyboardInterrupt:
        return 'Quit'


def list_csv_files():
    """Get a list of csv files from the working directory.

    This function requires glob to be imported.
    It returns a list of the names of the files, WITHOUT the ".csv".
    Returns:
        (list) list of filenames of csv files in working directory.
    """
    # See README.txt Ref#2.
    return [filename for filename in glob.glob("*.csv")]


def match_start_string(list_to_search, substring):
    """Search a list of strings for a starting substring.

    Both the string and the list to search are compared in lower case.
    However, the string returned retains case as in the searched list.
    The match is always from the start of the strings.
    Args:
        (list) list_to_search - List of strings to be searched.
        (str) substring - String being searched for (case insensitive).
    Returns:
        (list) List of strings that matched, with case of original list.
    """
    # Whitespace is stripped before and after the substring,
    # but not within (e.g. " New York City " -> "New York City").
    clean_substring = substring.lstrip().rstrip().lower()
    items_found = []
    ([items_found.append(item) for item in list_to_search
            if clean_substring == item[:len(clean_substring)].lower()])
    return items_found


def unique_selection(prompt_text, option_list):
    """Request selection of option and ensure is unique within the list.

    The function will continue interaction with the user until a unique
    selection from the list of options has been achieved or user quits.
    Args:
        (str) prompt_text - Text to display when requesting input.
        (list) option_list - List of valid option strings.
    Returns:
        (str) - The uniquely matched option. Note: string, not a list.
    """
    while True:
        selection = clean_input(prompt_text)

        # Get list of options that match input string from the start.
        matched = match_start_string(option_list, selection)
        if(len(matched) == 0):
            print('\nThere was no match for "{}". Please try again.'
                    ' Here are the options: '.format(selection))
            [print('\t{}'.format(option)) for option in option_list]
        else:
            if(len(matched) > 1):
                print('\nThere was more than one match to "{}":'
                        .format(selection))
                [print('\t{}'.format(match)) for match in matched]
                print('Please be more specific or "quit".')
            else:    # One clear option has been selected.
                break
    # Now there is only one item in the list, return it as a string.
    return str(matched).strip("'[]")


def display_categories(results_dict, category_header, result_header):
    """Display category values in columns, adjusting to content.

    Args:
        (dict) results_dict - Dictionary of categories and values.
        (str) category_header - Header of category column.
        (str) result_header - Header of result column.
    Returns:
        None.
    """
    pad = 5   # number of spaces between columns

    # Calculate column widths as length of header or longest content,
    # whichever is longer.
    max_category_width = max(len(category_header), max(
            [len(c) for c in results_dict.keys()]))
    max_result_width = max(len(result_header), max(
            [len(str(r)) for r in results_dict.values()]))

    # Display header and row of dashes aligned to columns.
    print('{}'.format(category_header).ljust(max_category_width)
            + ' ' * pad + '{}'.format(result_header).rjust(max_result_width))
    print('-' * max_category_width + '-' * pad + '-' * max_result_width)

    # Display content in columns.
    for category,result in results_dict.items():
        print('{}'.format(category).ljust(max_category_width)
                + ' ' * pad + '{}'.format(result).rjust(max_result_width) )
    print('')   # Blank line after final output improves format.


def display_counts_shares(df, title, column_name, precision):
    """Display counts and shares of a dataframe column of categories.

    Args:
        (DataFrame) df - Pandas dataframe.
        (str) title - Name to display as header of categories column.
        (str) column_name - Pandas dataframe column with categories.
        (int) precision - Number of decimal places for the share values.
    Returns:
        None.
    """
    category_counts = dict(df[column_name].value_counts())
    total_categories = df[column_name].count()

    # Display shares of user types.  Floating precision set by argument.
    category_shares = {k: '{0:.{1}f}%'.format(100 * v
            / total_categories, precision) for k,v in category_counts.items()}

    display_categories(category_counts,title,'Count')
    display_categories(category_shares,title,'Share(%)')


def display_most_common(description, df, column_name,
        show_in_rows=False):
    """Display the most common elements in a dataframe.

    Elements may be categories or values (types supporting .mode()).
    In the case of multiple categories having the same count, a list of
    these is displayed. If the optional 'list' argument is set to True,
    the output is displayed with one item per row. Otherwise the list
    is displayed as a series of comma-separated categories. The argument
    name list is not to be confused with the type list.
    Args:
        (str) description - Descriptive text preceding list of items.
        (DataFrame) df - Pandas dataframe.
        (str) column_name - Pandas dataframe column name.
        (bool) show_in_rows - Show results in rows or in line (default).
    Returns:
        None.
    """
    most_common = df[column_name].mode().tolist()

    if show_in_rows:    # Display in rows (useful for large columns).
        print(description)
        list_output = '\t' + '\n\t'.join(str(s) for s in most_common)
        print(list_output)
        print('\n',end='')     # Inserts newline after last line in list.
    else:               # Display in a comma-separated line (the default).
        print(description + ', '.join(str(s) for s in most_common))


def display_duration(description, total_seconds):
    """Display durations in seconds in a readable form.

    Args:
        (str) description - Descriptive text preceding the values.
        (float) total_seconds - Value in seconds to be displayed.
    Returns:
        None.
    """
    duration_args = ['{0} days, ','{1} hours, ','{2} minutes, ','{3} seconds ']
    duration_names = ['days', 'hours', 'minutes', 'seconds']
    duration_unit_in_seconds = [24 * 60 * 60, 60 * 60, 60, 1]

    # Calculate time units, rounding fractional seconds,
    # and casting to integer for divmod
    minutes, seconds = divmod(int(round(total_seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    # Build print string with relevant units only.
    # Top unit index indexes into this list, which is enumerated.
    duration_list = [days, hours, minutes, seconds]

    # Find the lowest non-zero units ("top").
    # The "else 3" ensures at least 0 seconds as output.
    top_unit_index = min([index if value > 0 else 3
            for index, value in enumerate(duration_list)])
    top_calc = float(total_seconds) / duration_unit_in_seconds[top_unit_index]
    top_name = duration_names[top_unit_index]

    # Build the string.
    print_string = ''.join([duration_args[index] if value > 0 else ''
            for index, value in enumerate(duration_list)])
    # Add the exact calculation for the highest relevant units.
    print_string += '(= {4:.{prec}f} {5})'

    # Note that only arguments included in the string are printed out.
    print(description + ' ' + print_string.format(days, hours, minutes, seconds,
            top_calc, top_name, prec=2))


def get_filters(available_cities, all_flag):
    """Ask user to specify a city, month, and day to analyze.

    Note that the available cities might include other names that are
    not city names but entries in the CITY_DATA directory,
    e.g. test files. If true, the all_flag argument will limit the
    questions to which city, so no further questions about filtering
    month and day will be asked.
    There are two special values for the return values:
        "All" - No filtering is made. This is not an option for cities.
        "Quit" - If user decides to Quit, all three return values are
        set to "Quit".
    Args:
        (list) available_cities - List of cities with data available.
        (bool) all_flag - If true, skip the month and day filtering.
    Returns:
        (str) city - Name of city to analyze, or "Quit".
        (str) month - Name of month to filter by, "All", or "Quit".
        (str) day - Name of day of week to filter by, "All", or "Quit".
    """
    # Make a string from the city key list for available data files.
    city_string = ', '.join(available_cities)

    # Get user input for city.
    # Note that "All" is not an option here - cities cannot be combined.
    city = unique_selection('\nWhich city (available are: '
            + city_string + ')? ', available_cities + ['Quit'])
    print('You selected: ', city)
    if city == 'Quit':    # Quit at city, so skip getting month and day.
        month = 'Quit'
        day = 'Quit'
    else:
        # Check command line option to switch off optional filtering.
        if all_flag:
            month = 'All'
            day = 'All'
        else:
            # Get user input for month.
            # There is a dummy entry at the start of the month list for
            # later mapping, so start slicing at 1 and end at 12.
            # TODO perhaps this dummy is an unnecessary complication.
            # In addition to the months, "All" and "Quit" are allowed.
            month = unique_selection('\nWhich month (or "all")? ',
                    list(MONTHS[1:13]) + ['All','Quit'])
            print('You selected: ', month)
            if month == 'Quit':    # Quit at month, so skip getting day.
                day = 'Quit'
            else:
                # Get user input on day of week.
                # In addition to the days, "All" and "Quit" are allowed.
                day = unique_selection('\nWhich day of the week (or "all")? ',
                        list(WEEKDAYS) + ['All','Quit'])
                print('You selected: ', day)
    return city, month, day


def load_data(city, month, day):
    """Load data for specified city, month and day, or as applicable.

    There is a special value for the argument values:
        "All" - No filtering is made. This is not an option for city.

    Args:
        (str) city - Name of the city to load.
        (str) month - Name of the month to filter by, or "All".
        (str) day - Name of the day of week to filter by, or "All".
    Returns:
        (DataFrame) - Pandas DataFrame of city filtered by month & day.
    """
    # Load data file into a dataframe.
    print('\nLoading data for city = {}, month = {}, day = {}...'
          .format(city, month, day))
    df = pd.read_csv(CITY_DATA[city])

    # Convert the Start Time column to datetime.
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    # Extract month, day of week, hour from Start Time to create new columns.
    df['Month'] = [MONTHS[int(m)] for m in df['Start Time'].dt.month]
    df['Day of Week'] = df['Start Time'].dt.weekday_name
    df['Hour'] = df['Start Time'].dt.hour
    # Create a column for the start and end station pairs.
    df['Path'] = df['Start Station'] + ' => ' + df['End Station']

     # Filter by month, if applicable.
    if month != 'All':
        df = df[df['Month'] == month]
    # Filter by day of week, if applicable
    if day != 'All':
        df = df[df['Day of Week'] == day]
    return df


def time_stats(df, timing_off_flag, month, day):
    """Display statistics on the most frequent times of travel.

    The function assumes the presence in the Dataframe of columns for
    'Month', Day of Week' and 'Hour' and that Hour is an integer
    representing the hour in 24 hour format (e.g. 17 = 5pm, 5 = 5am).
    There is a special value for the argument values month and day:
        "All" - No filtering was made, so it is valid also to show
        which was the most frequent. If filtering was made, then the
        arguments are a specific month or day, but this detail is not
        currently used.
    Args:
        (DataFrame) df - Pandas DataFrame of city data after filtering.
        (bool) timing_off_flag - If true, timing of function is skipped.
        (str) month - Name of the month that was filtered, or "All".
        (str) day - Name of the day of week that was filtered, or "All".
    Returns:
        None.
    """
    print('\nCalculating The Most Frequent Times of Travel...\n')
    if not timing_off_flag:
        start_time = time.time()

    # If more than one month, display the most common month.
    if month == "All":
        display_most_common('The most common month(s):', df, 'Month')

    # If more than one day, display the most common day of week.
    if day == "All":
        display_most_common('The most common day(s):  ', df, 'Day of Week')

    # Display the most common start hour.
    display_most_common('The most common hour(s): ', df, 'Hour')
    print(' (hour(s) in 24h format)')

    print('')        # Blank line after final output improves format.
    if not timing_off_flag:
        print('This took {0:6f} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def station_stats(df, timing_off_flag):
    """Display statistics on the most popular stations and trip.

    The function assumes the presence in the Dataframe of columns for
    'Start Station' and 'End Station'.
    Args:
        (DataFrame) df - Pandas DataFrame of city data after filtering.
        (bool) timing_off_flag - If true, timing of function is skipped.
    Returns:
        None.
    """
    print('\nCalculating The Most Popular Stations and Trip...\n')
    if not timing_off_flag:
        start_time = time.time()

    show_in_rows = True  # Show results in rows (better for multiples).

    # Display most commonly used start station.
    display_most_common('The most common start stations(s):', df,
            'Start Station', show_in_rows)

    # Display most commonly used end station.
    display_most_common('The most common end stations(s):', df,
            'End Station', show_in_rows)

    # Display most frequent combination of start and end stations.
    display_most_common('The most common start => end combination(s):', df,
            'Path', show_in_rows)

    print('')         # Blank line after final output improves format.
    if not timing_off_flag:
        print('This took {0:6f} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def trip_duration_stats(df, timing_off_flag):
    """Display statistics on the most popular stations and trip.

    The function assumes the presence in the Dataframe of a column for
    'Trip Duration'.
    Args:
        (DataFrame) df - Pandas DataFrame of city data after filtering.
        (bool) timing_off_flag - If true, timing of function is skipped.
    Returns:
        None.
    """
    print('\nCalculating Trip Duration...\n')
    if not timing_off_flag:
        start_time = time.time()

    # Display total travel time.
    display_duration('Total duration of all trips:\n',
            df['Trip Duration'].sum())

    # EXTENSION: display minimum travel time.
    display_duration('Shortest trip duration:\n', df['Trip Duration'].min())

    # Display mean travel time.
    display_duration('Mean trip duration:\n', df['Trip Duration'].mean())

    # EXTENSION: display median travel time.
    display_duration('Half of the trips took less than:\n',
            df['Trip Duration'].median())

    # EXTENSION: display 90th percentile travel time.
    display_duration('90% of the trips took less than:\n',
            df['Trip Duration'].quantile(0.9))

    # EXTENSION: display maximum travel time.
    display_duration('Longest trip duration:\n', df['Trip Duration'].max())

    print('')         # Blank line after final output improves format.
    if not timing_off_flag:
        print('This took {0:6f} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def user_stats(df, timing_off_flag):
    """Display statistics on bikeshare users.

    The function assumes the presence in the Dataframe of a column for
    'Subscriber Type'. Further columns for 'Gender' and 'Birth Year'
    are displayed if available (some data files do not contain
    these columns).
    Args:
        (DataFrame) df - Pandas DataFrame of city data after filtering.
        (bool) timing_off_flag - If true, timing of function is skipped.
    Returns:
        None.
    """
    print('\nCalculating User Stats...\n')
    if not timing_off_flag:
        start_time = time.time()

    # Display counts and shares of user types.
    display_counts_shares(df, 'Subscriber Type',
            'User Type', precision=4)

    # Display counts of gender.
    # The gender column is not always available, so test first.
    if 'Gender' in df.columns:
        # Display counts and shares of gender categories.
        display_counts_shares(df, 'Gender', 'Gender', precision=2)
    else:
        print('No data about gender for this city.')

    # Display earliest, most recent, and most common year of birth.
    # The birth year column is not always available, so test first.
    if 'Birth Year' in df.columns:
        # Reduce df['Birth Year'] by removing NaNs, converting to int
        # and storing in a new dataframe.  Note that the conversion to
        # DataFrame is needed for compatibility with the
        # "display_most_common" function.
        bydf = pd.DataFrame([int(b_year) for b_year in df['Birth Year']
                if not np.isnan(b_year).any()])  # See README.txt Ref#1.

        print("Earliest year of birth:  {}".format(bydf[0].min()))
        print("Latest year of birth:    {}".format(bydf[0].max()))
        display_most_common('The most common year(s): ', bydf, 0)
    else:
        print('No data about birth year for this city.')

    print('')         # Blank line after final output improves format.
    if not timing_off_flag:
        print('This took {0:6f} seconds.'.format(time.time() - start_time))
    print('=' * 60)    # the "=" is used to show start and end of blocks


def main_loop(args):
    """Welcome user, confirm settings, get filtered data, display it.

    The user can choose to display the filtered data in raw format or as
    summary statistics. Note that upon restarting, if there are no
    filters for month and day and the city is the same, the data is not
    read again because the loaded DataFrame is still available.
    The loop is exited by selecting "Quit" as the option.
    Args:
        (Args) args - parser.parse_args() object from argparse.
        For details of the arguments passed in, see main() function.
    Returns:
        None.
    """
    # welcome block and basic usage (user can also use -h option)
    print('\nWelcome to the bikeshare explorer!\n'
            '\nLet\'s explore some US bikeshare data!')
    print('\nTo select data, just type enough letters'
            ' to make your selection unique.')
    print('\tFor example: c for Chicago, th for Thursday, etc.')
    print('\tTo view all the possible filter options, just hit Enter.')
    # note that "q" will work as long as this option is unique
    print('To quit the program, enter q at the next prompt.')

    if args.timeoff:
        print('At your request, timings of statistics calculations'
                ' have been switched off.')
    else:
        print('To switch off timings of statistics calculations use option -t')
    if args.all:
        print('At your request, optional filtering has been switched off.')
    else:
        print('To always use all data (no month or day filters) use option -a')

    # Check which input files are available.
    file_list = list_csv_files()

    # Dictionary comprehension to create dictionary of found data files.
    file_dict = {city_name: city_file for city_name, city_file
            in CITY_DATA.items() if city_file in file_list}

    if len(file_dict) != 0:     # There are supported files available.
        # Needed to avoid reloading the same city if no filtering made.
        previous_city = 'No previous city',
        while True:
            # Obtain the desired filter settings.
            # Only offer cities with data files.
            city, month, day = get_filters(list(file_dict.keys()),args.all)

            if 'Quit' in (city, month, day):
                print('You requested to quit. The program has ended.')
                break

            # Load the data.
            if not (city == previous_city and args.all):
                df = load_data(city, month, day)

            # Confirm filter found data and ask how to display it.
            df_row_count = len(df.index)
            if df_row_count != 0:
                what_to_display = unique_selection(
                        '\nDo you want to view Raw Data or Statistics)? ',
                        ['Raw Data','Statistics','Quit'])
                print('You selected: ', what_to_display)
                if what_to_display == 'Quit':
                    print(QUIT_RECOGNIZED)
                    break
                elif what_to_display == 'Statistics':
                    # The "=" is used to show start and end of blocks.
                    print('\n' + ('=' * 60))
                    time_stats(df, args.timeoff, month, day)
                    station_stats(df, args.timeoff)
                    trip_duration_stats(df, args.timeoff)
                    user_stats(df, args.timeoff)
                else:
                    # Remaining option is to display the raw data.
                    print('\nTo change the number of rows per page,'
                            ' use option -p.\n')
                    i = 0
                    while(i < df_row_count):
                        # Absolute pagesize just to avoid problems with
                        # user entering negative row count.
                        print(df[i:(i + abs(args.pagesize))])
                        i += abs(args.pagesize)
                        next_page = clean_input('\nEnter q to quit,'
                                ' anything else to continue...')
                        if next_page.lower() == 'q':
                            break
            else:   # Row count is zero after filtering.
                print('There was no data with this selection.')

            restart = clean_input('\nWould you like to restart?'
                    ' Enter y to restart, anything else to quit: ')
            if restart.lower() != 'y':
                break
            previous_city = city
    else:        # No data files found.
        print('No data files were found in the working directory.'
        ' Please check!' )

    print(SIGNOFF)

def main():
    """Parse optional command line switches and handle exceptions.

    Args:
        The following optional command line switches are supported:
        -h, --help - Built-in display of optional switches
        -t, --timeoff - Switch off the timing in statistics functions.
        -a, --all - All data to be used, no filtering of month or day.
        -d, --debug - Switch off Exception handling to allow tracing.
        -p, --pagesize - specify the number of rows of raw data to show
        at a time. Default is 10 rows.
    Returns:
        None.
    """
    # Set up any options when calling the program.
    # This setup is deliberately excluded from the exception handling.
    # This function requires argparse to be imported.
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeoff', action='store_true',
            help='switch off the timing displays')
    parser.add_argument('-a', '--all', action='store_true',
            help='use all data, don\'t ask about filtering')
    parser.add_argument('-d', '--debug', action='store_true',
            help='allows any and all exceptions to be fully displayed')
    parser.add_argument('-p', '--pagesize', default = 10, type=int,
            help='raw file page size, default is 10 data rows')
    args = parser.parse_args()

    # Handle exceptions elegantly, but allow for debugging if needed.
    # When in debug mode, main loop is run without exception handling.
    # Exception handling is not silent but highly simplified.
    if args.debug:
        main_loop(args)
    else:
        try:
            main_loop(args)
        except KeyboardInterrupt:      # Usually means a desire to quit.
            print(QUIT_RECOGNIZED+SIGNOFF)
        except Exception as Error:
            print('\nSomething exceptional just happened: \n{}'
                    '\nFind out why with the debug option (-d).'\
              .format(Error))

if __name__ == "__main__":
    main()
