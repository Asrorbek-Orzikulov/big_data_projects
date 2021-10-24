from collections import defaultdict

FILENAME = "small_file.csv"


def read_csv(filename):
    """
    Parse a CSV file with the given `filename`.

    Parameters
    ----------
    filename : str
        Full name of the CSV file containing records.

    Yields
    ------
    list of str
        Each line of the CSV file split into a list.

    """
    with open(filename, 'r') as file:
        for line in file:
            line_clean = line[:-1].replace("\"", "").replace(", ", ": ")
            yield line_clean.split(",")


contents = read_csv(FILENAME)

next(contents)

i = 0
for row in contents:
    if i < 5:
        print(row)
        i += 1
    else:
        break


def find_indices(rows_gen, column_names):
    """
    Find the indices of given columns.

    Modifies the input generator by moving it by 1 row.

    Parameters
    ----------
    rows_gen : generator
        Generator yielding the rows of the text file.
    column_names : tuple of str
        Names of the columns whose indices we need.

    Returns
    -------
    list of int
        List containing the index of each column.

    """
    header = next(rows_gen)
    indices = []
    for column in column_names:
        indices.append(header.index(column))
    return indices


def apply_map(filename, map_func, column_names):
    """
    Iterate over `filename` and apply `map_func` on its each line.

    Parameters
    ----------
    filename : str
        Full name of a text file containing records.
    map_func : func
        Map function returning a tuple for each line.
    column_names : tuple of str
        Names of the columns that `map_func` needs.

    Returns
    -------
    list of tuples
        Contains tuples returned by each call of `map_func`. If the
        map result was (None, None), it is not included in the list.
    """
    lines = read_csv(filename)
    column_indices = find_indices(lines, column_names)
    map_result_list = []
    for line in lines:
        map_result = map_func(line, column_indices)
        if map_result != (None, None):
            map_result_list.append(map_result)

    return map_result_list


def apply_reduce(tuples_dict, reduce_func):
    """
    Iterate over `tuples_dict` and apply `reduce_func` on each key.

    Parameters
    ----------
    tuples_dict : dict of tuples
        Dictionary of key-value pairs produced by the corresponding
        shuffle function.
    reduce_func : func
        Reduce function returning a tuple for each key in `tuples_dict`.

    Returns
    -------
    list of tuples
        Contains tuples returned by each call of `reduce_func`.

    """
    reduce_list = []
    for key in tuples_dict:
        reduce_list.append(reduce_func(tuples_dict, key))

    return reduce_list


# Question 1
def map_empty(line, column_indices):
    """
    Create a tuple for flights having at most 10% occupancy rate.

    Parameters
    ----------
    line : list of str
        Each line of a text file split into a list.
    column_indices : list of int
        List containing the indices of Passengers, Seats, and
        Flights columns.
    Returns
    -------
    tuple of (float, int) or (None, None)
        Each tuple is (occupancy rate, flight count) if occupancy
        rate is at most 10%. Otherwise, it is (None, None).

    """
    passenger_idx, seats_idx, flights_idx = column_indices
    passengers = int(line[passenger_idx])
    seats = int(line[seats_idx])
    try:
        occupancy_rate = passengers / seats
        if occupancy_rate <= 0.1:
            flights = int(line[flights_idx])
            return round(occupancy_rate, 2), flights
        else:
            return None, None
    except ZeroDivisionError:
        return None, None


columns = ("Passengers", "Seats", "Flights")
map_empty_result = apply_map(FILENAME, map_empty, columns)
map_empty_result[:7]


def shuffle_flights(tuples_list):
    """
    Take the key-value pairs created by a map function and
    create a list of all values corresponding to the same key.

    Parameters
    ----------
    tuples_list : list of (hashable type, any type)
        List of tuples, where each tuple is a (key, value) pair.

    Returns
    -------
    defaultdict of {hashable type : list of any type}
        Keys are the individual values of the grouping variable,
        and values are the lists corresponding to same key.

    """
    pairs_dict = defaultdict(list)
    for key, value in tuples_list:
        pairs_dict[key].append(value)

    return pairs_dict


shuffle_empty_result = shuffle_flights(map_empty_result)
shuffle_empty_result[0.09]


def reduce_flights(pairs_dict, key):
    """
    Sum all values corresponding to the given key.

    Parameters
    ----------
    pairs_dict : dict of {hashable type : list of int}
        Keys are the individual values of the grouping variable,
        and values are the lists corresponding to same key.
    key : hashable type
        Individual value of the grouping variable for which we
        need a sum.

    Returns
    -------
    tuple of (hashable type, int)
        tuple of the form (key, sum of all values).

    """
    values_list = pairs_dict[key]
    values_sum = sum(values_list)
    return key, values_sum


reduce_empty_partial = apply_reduce(shuffle_empty_result, reduce_flights)
reduce_empty_partial

reduce_empty_full = sum(x[1] for x in reduce_empty_partial)
print("The number of almost empty flights is", reduce_empty_full)


# Question 2
def map_flights(line, column_indices):
    """
    Create a tuple of (group variable, flight count).

    Parameters
    ----------
    line : list of str
        Each line of a text file split into a list.
    column_indices : list of int
        List containing the indices of the grouping variable
        and the Flights columns.

    Returns
    -------
    tuple of (hashable type, int)
        Hashable type is the type of the grouping variable.

    """
    group_var_idx, flights_idx = column_indices
    group_var = line[group_var_idx]
    flight_count = int(line[flights_idx])
    return group_var, flight_count


columns = ("Destination_airport", "Flights")
map_top_airports = apply_map(FILENAME, map_flights, columns)
map_top_airports[:10]


# def shuffle_top_flights(tuples_list):
#     """
#     Aggregate flight counts by the grouping variable.
#
#     Parameters
#     ----------
#     tuples_list : list of (group type, int)
#         Group type is the type of the grouping variable.
#
#     Returns
#     -------
#     defaultdict of {group type : list of int}
#         Keys are the levels of the grouping variable, and the values
#         are lists of flight counts corresponding to each group level.
#
#     """
#     result = defaultdict(list)
#     for group_var, flight_count in tuples_list:
#         result[group_var].append(flight_count)
#     return result


shuffle_top_airports = shuffle_flights(map_top_airports)
shuffle_top_airports["END"]


# def reduce_top_flights(group_dict, key):
#     """
#     Sum all flights corresponding to the same `key`.
#
#     Parameters
#     ----------
#     group_dict : dict of {group type : list of int}
#         Keys are the levels of the grouping variable, and the values
#         are lists of flight counts corresponding to each group level.
#     key : grouping variable type
#         Individual value of the grouping variable to sum flights for.
#
#     Returns
#     -------
#     tuple of (group type, int)
#         Consists of one value of the grouping variable and the total
#         number of flights corresponding to that value.
#     """
#     flight_count = sum(group_dict[key])
#     return key, flight_count


reduce_top_airports = apply_reduce(shuffle_top_airports, reduce_flights)
reduce_top_airports.sort(key=lambda x: x[1], reverse=True)
print("The top-5 airports are", reduce_top_airports[:5])


# Question 3
columns = ("Destination_city", "Flights")
map_top_cities = apply_map(FILENAME, map_flights, columns)
map_top_cities[:10]

shuffle_top_cities = shuffle_flights(map_top_cities)
shuffle_top_cities["Ames: IA"]

reduce_top_cities = apply_reduce(shuffle_top_cities, reduce_flights)
reduce_top_cities.sort(key=lambda x: x[1], reverse=True)
print("The top-5 cities are", reduce_top_cities[:5])


# Question 4
def map_connections1(line, column_indices):
    """
    Create a tuple for flights between two cities by month/year.

    Parameters
    ----------
    line : list of str
        Each line of a text file split into a list.
    column_indices : list of int
        List containing the indices of Origin_city, Destination_city,
        Flights, and Fly_date columns.
    Returns
    -------
    tuple of ((str, str, str), int)
        Each tuple is ((date, city1, city2), flight count).

    """
    source_idx, destination_idx, flights_idx, date_idx = column_indices
    source = line[source_idx]
    destination = line[destination_idx]
    flights = int(line[flights_idx])
    date = line[date_idx][:-3]
    if source > destination:
        destination, source = source, destination  # ordering pairs alphabetically

    joint_key = (date, source, destination)
    return joint_key, flights


columns = ("Origin_city", "Destination_city", "Flights", "Fly_date")
map_connections_result1 = apply_map(FILENAME, map_connections1, columns)
map_connections_result1[:10]


# def shuffle_connections1(map_pairs):
#     """
#     Aggregate flights between two cities by month/year.
#
#     Parameters
#     ----------
#     map_pairs : list of ((str, str, str), int)
#         List of tuples, where each tuple is of the form
#         ((date, city1, city2), flight count).
#
#     Returns
#     -------
#     defaultdict of {(str, str, str) : list of int}
#         Keys are tuples of (date, city1, city2), and values
#         are the lists of flight counts between the two cities.
#
#     """
#     count_dict = defaultdict(list)
#     for key, flight in map_pairs:
#         count_dict[key].append(flight)
#     return count_dict


shuffle_connections_result1 = shuffle_flights(map_connections_result1)
shuffle_connections_result1[("1990-02", "Bend: OR", "Seattle: WA")]


# def reduce_connections1(flights_dict):
#     """
#     Sum flights between pairs of cities by month/year.
#
#     Parameters
#     ----------
#     flights_dict : dict of {(str, str, str) : list of int}
#         Keys are tuples of (date, city1, city2), and values
#         are the lists of flight counts between the two cities.
#
#     Returns
#     -------
#     list of ((str, str, str), int)
#         List of tuples of the form ((date, city1, city2), count),
#         where count is the total number of flights between the
#         two cities by month/year.
#
#     """
#     monthly_flights = []
#     for key, values in flights_dict.items():
#         monthly_sum = sum(values)
#         monthly_flights.append((key, monthly_sum))
#     return monthly_flights


reduce_connections_result1 = apply_reduce(shuffle_connections_result1, reduce_flights)
reduce_connections_result1[:10]


def map_connections2(key, flights):
    """
    Regroup flights between two cities by month/year.

    Parameters
    ----------
    key : tuple of (str, str, str)
        A tuple of the form (date, city1, city2)
    flights : int
        Count of flights between the two cities by month/year.

    Returns
    -------
    tuple of (str, (str, str, int))
        Each tuple is of the form (date, (city1, city2, count)).

    """
    date, source, destination = key
    new_value = (source, destination, flights)
    return date, new_value


map_connections_result2 = []
for key, flights in reduce_connections_result1:
    map_result = map_connections2(key, flights)
    map_connections_result2.append(map_result)

map_connections_result2[:10]


# def shuffle_connections2(map_pairs):
#     """
#     Aggregate flights that took place in the same month/year.
#
#     Parameters
#     ----------
#     map_pairs : list of (str, (str, str, int))
#         List of tuples of the form (date, (city1, city2, count))
#
#     Returns
#     -------
#     defaultdict of {str : list of (str, str, int)}
#         Keys are dates, and values are lists of tuples of the form
#         (city1, city2, count).
#
#     """
#     flight_dict = defaultdict(list)
#     for key, value in map_pairs:
#         flight_dict[key].append(value)
#     return flight_dict


shuffle_connections_result2 = shuffle_flights(map_connections_result2)
shuffle_connections_result2['1999-01']


def reduce_connections2(flights_dict, date):
    """
    Find the top-5 cities with the most flights for the given date.

    Parameters
    ----------
    flights_dict : dict of {str : list of (str, str, int)}
        Keys are dates, and values are lists of tuples of the form
        (city1, city2, count).
    date : str
        Date of the form yyyy-mm for which we need the top-5 cities.

    Returns
    -------
    tuple of (str, list of (str, str, int))
        A tuple of the form (date, list of (city1, city2, count)).

    """
    flight_info = flights_dict[date]
    flight_info.sort(key=lambda x: x[2], reverse=True)
    return date, flight_info[:5]


reduce_connections_result2 = apply_reduce(
    shuffle_connections_result2, reduce_connections2)
reduce_connections_result2.sort()
reduce_connections_result2[:5]


# Question 5

