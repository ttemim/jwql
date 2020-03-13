#! /usr/bin/env python
"""Auxilary functions for plots

    Module holds functions that are used for several plots.


Authors
-------
    - Daniel Kühbacher

Use
---


Dependencies
------------

"""
import numpy as np
import pandas as pd
from astropy.time import Time
from bokeh.models import BoxAnnotation
from bokeh.models import ColumnDataSource


def pol_regression(x, y, rank):
    """ Calculate polynominal regression of certain rank
    Parameters
    ----------
    x : list
        x parameters for regression
    y : list
        y parameters for regression
    rank : int
        rank of regression
    Return
    ------
    y_poly : list
        regression y parameters
    """
    z = np.polyfit(x, y, rank)
    f = np.poly1d(z)
    y_poly = f(x)
    return y_poly


def add_hover_tool(p, rend):
    """ Append hover tool to plot
    parameters
    ----------
    p : bokeh figure
        declares where to append hover tool
    rend : list
        list of renderer to append hover tool
    """

    from bokeh.models import HoverTool

    # activate HoverTool for scatter plot
    hover_tool = HoverTool(tooltips=
    [
        ('Name', '$name'),
        ('Count', '@data_points'),
        ('Mean', '@average'),
        ('Deviation', '@deviation'),
        ('Time', '@strTime'),
        ('Anomaly', '@amomaly')
    ], renderers=rend)
    # append hover tool
    p.tools.append(hover_tool)


def add_hover_tool_weel(p, rend):
    """ Append hover tool to plot
    parameters
    ----------
    p : bokeh figure
        declares where to append hover tool
    rend : list
        list of renderer to append hover tool
    """

    from bokeh.models import HoverTool

    # activate HoverTool for scatter plot
    hover_tool = HoverTool(tooltips=
    [
        ('Name', '$name'),
        ('Value', '@value'),
        ('Time', '@strTime'),
        ('Anomaly', '@amomaly')
    ], renderers=rend)
    # append hover tool
    p.tools.append(hover_tool)


def add_limit_box(p, lower, upper, alpha=0.1, color="green"):
    """ Adds box to plot
    Parameters
    ----------
    p : bokeh figure
        declares where to append hover tool
    lower : float
        lower limit of box
    upper : float
        upper limit of box
    alpha : float
        transperency of box
    color : str
        filling color
    """
    box = BoxAnnotation(bottom=lower, top=upper, fill_alpha=alpha, fill_color=color)
    p.add_layout(box)


def add_to_plot(p, legend, mnemonic, start, end, conn, y_axis="default", color="red", err='n'):
    """Add scatter and line to certain plot and activates hoover tool
    Parameters
    ----------
    err
    p : bokeh object
        defines plot where line and scatter should be added
    legend : str
        will be showed in legend of plot
    mnemonic : str
        defines mnemonic to be plotted
    start : datetime
        sets start time for data query
    end : datetime
        sets end time for data query
    conn : DBobject
        connection object to database
    y_axis : str (default='default')
        used if secon y axis is provided
    color : str (default='dred')
        defines color for scatter and line plot
    Return
    ------
    scat : plot scatter object
        used for applying hovertools o plots
    """

    # convert given start and end time to astropy time
    start_str = str(Time(start).mjd)
    end_str = str(Time(end).mjd)

    # prepare and execute sql query
    sql_c = "SELECT * FROM " + mnemonic + " WHERE start_time BETWEEN " + start_str + " AND " + end_str + " ORDER BY start_time"
    temp = pd.read_sql_query(sql_c, conn)

    # put data into Dataframe and define ColumnDataSource for each plot
    reg = pd.DataFrame({'reg': pol_regression(temp['start_time'], temp['average'], 3)})
    temp = pd.concat([temp, reg], axis=1)

    # get anomaly of anolmaly table
    sql_neu = "SELECT * FROM miriAnomaly WHERE plot = '" + mnemonic + "' ORDER BY start_time"
    anomaly_table = pd.read_sql_query(sql_neu, conn)

    # define lists
    list_time_element = temp['start_time']
    list_anomaly_start = anomaly_table['start_time']
    list_anomaly_end = anomaly_table['end_time']
    list_anomaly_id = anomaly_table['id']
    list_anomaly_order = []
    for i in range(len(list_time_element)):
        list_anomaly_order.append('')

    # populate info
    for i in range(len(list_anomaly_start)):
        element_anomaly_start = list_anomaly_start[i]
        element_anomaly_end = list_anomaly_end[i]
        element_anomaly_id = list_anomaly_id[i]
        for id, element_time_element in enumerate(list_time_element):
            if element_anomaly_start <= element_time_element <= element_anomaly_end:
                list_anomaly_order[id] += str(element_anomaly_id) + ' '

    # get rid of empty strings
    for id, element in enumerate(list_anomaly_order):
        if len(element) < 1:
            list_anomaly_order[id] = 'NaN'

    # make date string
    str_time = []
    for element in temp['start_time']:
        str_time.append(str(Time(element, format="mjd").iso))

    temp['strTime'] = str_time
    temp['start_time'] = Time(temp['start_time'], format="mjd").datetime
    temp['amomaly'] = list_anomaly_order

    plot_data = ColumnDataSource(temp)

    # plot data
    p.line(x="start_time", y="average", color=color, y_range_name=y_axis, legend=legend, source=plot_data)
    scat = p.scatter(x="start_time", y="average", color=color, name=mnemonic, y_range_name=y_axis, legend=legend,
                     source=plot_data)

    # generate error lines if wished
    if err != 'n':
        # generate error bars
        err_xs = []
        err_ys = []

        for index, item in temp.iterrows():
            err_xs.append((item['start_time'], item['start_time']))
            err_ys.append((item['average'] - item['deviation'], item['average'] + item['deviation']))

        # plot them
        p.multi_line(err_xs, err_ys, color=color, legend=legend)

    return scat


def add_to_wplot(p, legend, mnemonic, start, end, conn, nominal, color="red"):
    """Add line plot to figure (for wheelpositions)
    Parameters
    ----------
    nominal
    p : bokeh object
        defines figure where line schould be plotted
    legend : str
        will be showed in legend of plot
    mnemonic : str
        defines mnemonic to be plotted
    start : datetime
        sets start time for data query
    end : datetime
        sets end time for data query
    conn : DBobject
        connection object to database
    color : str (default='dred')
        defines color for scatter and line plot
    """

    start_str = str(Time(start).mjd)
    end_str = str(Time(end).mjd)

    sql_c = "SELECT * FROM " + mnemonic + " WHERE timestamp BETWEEN " + start_str + " AND " + end_str + " ORDER BY timestamp"
    temp = pd.read_sql_query(sql_c, conn)

    # normalize values
    temp['value'] -= nominal
    # temp['value'] -= 1

    # get anomaly
    sql_neu = "SELECT * FROM miriAnomaly WHERE plot = '" + mnemonic + "' ORDER BY start_time"
    anomaly_table = pd.read_sql_query(sql_neu, conn)

    # define lists
    list_time_element = temp['timestamp']
    list_anomaly_start = anomaly_table['start_time']
    list_anomaly_end = anomaly_table['end_time']
    list_anomaly_id = anomaly_table['id']
    list_anomaly_order = []
    for i in range(len(list_time_element)):
        list_anomaly_order.append('')

    # populate info
    for i in range(len(list_anomaly_start)):
        element_anomaly_start = list_anomaly_start[i]
        element_anomaly_end = list_anomaly_end[i]
        element_anomaly_id = list_anomaly_id[i]
        for id, element_time_element in enumerate(list_time_element):
            if element_anomaly_start <= element_time_element <= element_anomaly_end:
                list_anomaly_order[id] += str(element_anomaly_id) + ' '

    # get rid of empty strings
    for id, element in enumerate(list_anomaly_order):
        if len(element) < 1:
            list_anomaly_order[id] = 'NaN'

    # make date string
    str_time = []
    for element in temp['timestamp']:
        str_time.append(str(Time(element, format="mjd").iso))
    temp['strTime'] = str_time
    temp['timestamp'] = pd.to_datetime(Time(temp['timestamp'], format="mjd").datetime)
    temp['amomaly'] = list_anomaly_order

    plot_data = ColumnDataSource(temp)

    p.line(x="timestamp", y="value", color=color, legend=legend, source=plot_data)
    sc = p.scatter(x="timestamp", y="value", color=color, legend=legend, source=plot_data, name=mnemonic)

    return sc


def add_basic_layout(p):
    """Add basic layout to certain plot
    Parameters
    ----------
    p : bokeh object
        defines plot where line and scatter should be added
    """
    p.title.align = "left"
    p.title.text_color = "#c85108"
    p.title.text_font_size = "25px"
    p.background_fill_color = "#efefef"

    p.xaxis.axis_label_text_font_size = "14pt"
    p.xaxis.axis_label_text_color = '#2D353C'
    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_color = '#2D353C'

    p.xaxis.major_tick_line_color = "firebrick"
    p.xaxis.major_tick_line_width = 2
    p.xaxis.minor_tick_line_color = "#c85108"
