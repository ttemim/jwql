"""ice_voltage_tab.py

    Module prepares plots for mnemonics below, combines plots in a grid and
    returns tab object.

    Plot 1:
    IMIR_HK_ICE_SEC_VOLT1
    IMIR_HK_ICE_SEC_VOLT3

    Plot 2:
    IMIR_HK_ICE_SEC_VOLT2

    Plot 3:
    IMIR_HK_ICE_SEC_VOLT4 : IDLE and HV_ON

    Plot 4:
    IMIR_HK_FW_POS_VOLT
    IMIR_HK_GW14_POS_VOLT
    IMIR_HK_GW23_POS_VOLT
    IMIR_HK_CCC_POS_VOLT

Authors
-------
    - [AIRBUS] Daniel Kübacher
    - [AIRBUS] Leo Stumpf

Use
---
    The functions within this module are intended to be imported and
    used by ``dashborad.py``, e.g.:

    ::
        from .plots.bias_tab import bias_plots
        tab = bias_plots(conn, start, end)

Dependencies
------------
    The file miri_database.db in the directory jwql/jwql/database/ must be populated.

References
----------
    The code was developed in reference to the information provided in:
    ‘MIRI trend requestsDRAFT1900301.docx’

Notes
-----
    For further information please contact Brian O'Sullivan
"""
from bokeh.layouts import gridplot, Column
from bokeh.models.widgets import Panel

import jwql.instrument_monitors.miri_monitors.data_trending.plots.plot_functions as pf
import jwql.instrument_monitors.miri_monitors.data_trending.plots.tab_object as tabObjects
import jwql.instrument_monitors.miri_monitors.data_trending.utils.utils_f as utils


def volt4(conn, start, end):
    """Create specific plot and return plot object
    Parameters
    ----------
    conn : DBobject
        Connection object that represents database
    start : time
        Startlimit for x-axis and query (typ. datetime.now()- 4Months)
    end : time
        Endlimit for x-axis and query (typ. datetime.now())
    Return
    ------
    p : Plot object
        Bokeh plot
    """

    p = utils.get_figure(end, "ICE_SEC_VOLT4", "Voltage (V)", 560, 500, [4.2, 5])

    a = pf.add_to_plot(p, "Volt4 Idle", "IMIR_HK_ICE_SEC_VOLT4_IDLE", start, end, conn, color="orange")
    b = pf.add_to_plot(p, "Volt4 Hv on", "IMIR_HK_ICE_SEC_VOLT4_HV_ON", start, end, conn, color="red")

    pf.add_hover_tool(p, [a, b])
    p.legend.click_policy = "hide"

    return p


def volt1_3(conn, start, end):
    """Create specific plot and return plot object
    Parameters
    ----------
    conn : DBobject
        Connection object that represents database
    start : time
        Startlimit for x-axis and query (typ. datetime.now()- 4Months)
    end : time
        Endlimit for x-axis and query (typ. datetime.now())
    Return
    ------
    p : Plot object
        Bokeh plot
    """

    p = utils.get_figure(end, "ICE_SEC_VOLT1/3", "Voltage (V)", 560, 500, [30, 50])

    a = pf.add_to_plot(p, "Volt1", "IMIR_HK_ICE_SEC_VOLT1", start, end, conn, color="red")
    b = pf.add_to_plot(p, "Volt3", "IMIR_HK_ICE_SEC_VOLT3", start, end, conn, color="purple")

    pf.add_hover_tool(p, [a, b])
    p.legend.click_policy = "hide"

    return p


def volt2(conn, start, end):
    """Create specific plot and return plot object
    Parameters
    ----------
    conn : DBobject
        Connection object that represents database
    start : time
        Startlimit for x-axis and query (typ. datetime.now()- 4Months)
    end : time
        Endlimit for x-axis and query (typ. datetime.now())
    Return
    ------
    p : Plot object
        Bokeh plot
    """

    p = utils.get_figure(end, "ICE_SEC_VOLT2", "Voltage (V)", 560, 500, [60, 80])

    a = pf.add_to_plot(p, "Volt2", "IMIR_HK_ICE_SEC_VOLT2", start, end, conn, color="red")

    pf.add_hover_tool(p, [a])
    p.legend.click_policy = "hide"

    return p


def pos_volt(conn, start, end):
    """Create specific plot and return plot object
    Parameters
    ----------
    conn : DBobject
        Connection object that represents database
    start : time
        Startlimit for x-axis and query (typ. datetime.now()- 4Months)
    end : time
        Endlimit for x-axis and query (typ. datetime.now())
    Return
    ------
    p : Plot object
        Bokeh plot
    """

    p = utils.get_figure(end, "Wheel Sensor Supply", "Voltage (mV)", 560, 500, [280, 300])

    a = pf.add_to_plot(p, "FW", "IMIR_HK_FW_POS_VOLT", start, end, conn, color="red")
    b = pf.add_to_plot(p, "GW14", "IMIR_HK_GW14_POS_VOLT", start, end, conn, color="purple")
    c = pf.add_to_plot(p, "GW23", "IMIR_HK_GW23_POS_VOLT", start, end, conn, color="orange")
    d = pf.add_to_plot(p, "CCC", "IMIR_HK_CCC_POS_VOLT", start, end, conn, color="firebrick")

    pf.add_hover_tool(p, [a, b, c, d])
    p.legend.click_policy = "hide"

    return p


def volt_plots(conn, start, end):
    """Combines plots to a tab
    Parameters
    ----------
    conn : DBobject
        Connection object that represents database
    start : time
        Startlimit for x-axis and query (typ. datetime.now()- 4Months)
    end : time
        Endlimit for x-axis and query (typ. datetime.now())
    Return
    ------
    p : tab object
        used by dashboard.py to set up dashboard
    """

    descr = tabObjects.generate_tab_description(utils.description_IceVoltage)

    plot1 = volt1_3(conn, start, end)
    plot2 = volt2(conn, start, end)
    plot3 = volt4(conn, start, end)
    plot4 = pos_volt(conn, start, end)
    data_table = tabObjects.anomaly_table(conn, utils.list_mn_iceV)

    l = gridplot([[plot1, plot2], [plot3, plot4]], merge_tools=False)
    layout = Column(descr, l, data_table)

    tab = Panel(child=layout, title="ICE VOLTAGE")

    return tab
