# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from typing import Any, List, Type, Union, Tuple, Dict

# #############################################################################
# functions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _assign_distance(df:pd.DataFrame, group:str, within_pad:float=2,
                     between_pad:float=4, start:float=0, new_col:str='y_axis',
                     sort_dict:Union[Dict[str,int], None]=None,
                     strata:Union[str, None]=None,
                     ):
    """
    A helper function that adds a `y-axis` column (useful for Cartesian graphs)
    to a dataframe based on group membership. The within_pad arguments
    determines the spacing `between` groups with the same value, while
    between_pad sets the spacing `between` distinct groups.
    
    Arguments
    ---------
    df : pd.DataFrame,
        The dataframe that contains the `group` of interrest.
    group : str,
        A string that maps to a column in df.
    strat : str, default None
        An optional df column which nests the `group` values.
    within_pad : float,
        The distance between point estimates nested within a group.
    between_pad : float,
        The distance between groups of point estimates. This is the y-axis
        distance that will be skipped between the last y-axis coordinate in the
        previous group and the starting y-axis coordinate of the current group.
    start : float, default 0,
        The starting position of the sequence.
    new_col : str, default `y_axis`
        The name of the column that will be added to `df`.
    sort_dict : dict, default None
        Supply a key:value-float combination dictionary to sort the rows on
        `group` membership.
    
    Returns
    -------
    df : pd.DataFrame
    """
    # check input
    if not group in df.columns:
        raise KeyError('df does not contain column {0}'.format(group))
    if strata is None:
        # use a place-holder strata
        strata='strata_del'
        df[strata]=1
    # sort index to group column values together
    if sort_dict is None:
        # sort by group value
        df.sort_values(by=[group, strata], inplace=True)
    else:
        # sort by costom order
        order='order'
        df[order] = df[group].map(sort_dict)
        df.sort_values(by=[order, strata], inplace=True)
        del df[order]
    # number of groups and number of rows
    n_strat = len(df[strata].unique())
    n_group = len(df[group].unique())
    l_group = df[group].value_counts().unique()/n_strat
    if l_group.shape[0] != 1:
        raise ValueError('The number of group elements is not unique')
    else:
        l_group = l_group[0]
    # getting spacing
    y_axis = []
    i = 0
    while i < n_group:
        # within group sequence
        chunk = np.arange(start, stop=start+within_pad*l_group, step=within_pad)
        y_axis = y_axis + chunk.tolist()
        # between group space
        start = y_axis[-1] + between_pad
        # incrementing
        i+=1
    # loop over the strata
    df[new_col] = np.nan
    for strat in df[strata].unique():
        df.loc[df[strata] == strat, new_col] = y_axis
    # return stuff
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_forest(df:pd.DataFrame, x_col:str, lb_col:Union[str, None]=None,
                ub_col:Union[str, None]=None, y_col:str='y_axis',
                s_col:str='o', c_col:str='black', g_col:Union[str, None]=None,
                shape_size:float=40, ci_lwd:float=2,
                ci_colour:str='indianred', connect_shape:bool = False,
                connect_shape_colour:str='black', connect_shape_lwd:float=1,
                span:bool = True, span_colour:List[str] = ['white', 'lightgrey'],
                ax:Union[plt.Axes, None]=None, figsize:tuple=(10, 10),
                reverse_y:bool=True,
                kwargs_scatter_dict:Dict[Any, Any]={},
                kwargs_plot_ci_dict:Dict[Any, Any]={},
                kwargs_connect_segments_dict:Dict[Any, Any]={},
                kwargs_span_dict:Dict[Any, Any]={}
                ):
                    
    """
    A forest plot function, that allows for grouping of estimates by `group`.
    Related if there are estimates with the same `y_col` value these get
    depicted as a horizontal sequence linked by a line segement.
    
    Arguments
    ---------
    df : pd.DataFrame,
    x_col : str,
        The column name of the x-axis values (typically point estimates).
    lb_col : str, default None,
        The column name of the lower bound of an confidence interval.
    ub_col : str, default None,
        The column name of the upper bound of an confidence interval.
    y_col : str, default 'y_axis',
        The column name of the y-axis values used to differentiate
        estimates/studies.
    s_col : str, default 'o',
        The column name of the shape indicators. If string is not found in `df`
        the string value will be added to an `s_col` column.
    c_col : str, default 'black',
        The column name of the shape colour indicators. If string is not found
        in `df` the string value will be added to an `s_col` column.
    g_col : str, default None,
        The column name of the group indicator; often the outcome or study
        indicators. If None, a column with a unique value for each row will be
        added - so there are no groups. This column will also be used to
        provide y-axis ticklabels.
    shape_size : float, default 40,
        The shape size.
    ci_lwd : float, default 1,
        The line width of the confidence intervals.
    ci_colour : float, default 'indianred'
        The line colour of the confidence intervals
    connect_shape : boolean, default False,
        If the point estimates should be connected with a line. Only relevant
        when estimates have the same y-axis.
    connect_shape_colour : str, default `grey`,
        The line colour.
    connect_shape_lwd : float, default 1,
        The line width.
    span : boolean, default True,
        Whether an colour-interchanging horizontal background segment should
        be added
    span_colour : list of two string, default ['white', 'lightgrey'],
        The colours of the span.
    ax : plt.axes, default None
        An optional matplotlib axis. If supplied the function works on the axis.
    figsize : tuple of two floats, default (10, 10),
        The figure size, when ax==None.
    reverse_y : boolean, default True,
        inverts the y-axis.
    kwargs_*_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            kwargs_scatter_dict          --> ax.scatter
            kwargs_plot_ci_dict          --> ax.plot
            kwargs_connect_segments_dict --> ax.plot
            kwargs_span_dict             --> ax.axhspan
    
    Returns
    -------
    Unpacks a matplotlib figure, axes
    """
    # ################### do check and set defaults
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df should be a pd.DataFrame')
    # set default shape and colour
    s_col_name = s_col
    c_col_name = c_col
    if s_col_name not in df.columns:
        s_col_name = 's_col'
        df[s_col_name] = s_col
        warnings.warn('`s_col` not found in `df`, creating `s_col` column '
                      'with value {}.'.format(s_col), RuntimeWarning)
        del s_col
    if c_col not in df.columns:
        c_col_name = 'c_col'
        df[c_col_name] = c_col
        warnings.warn('`c_col` not found in `df`, creating `c_col` column '
                      'with value {}.'.format(c_col), RuntimeWarning)
        del c_col
    if g_col is None:
        g_col = 'g_col'
        df[g_col] = range(df.shape[0])
    # ################## should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = None
    # ################## plot points and errors
    for _, row in df.iterrows():
        # coordiantes
        xs = row[x_col]
        ys = row[y_col]
        # add points
        ax.scatter(x=xs, y=ys, s=shape_size, marker=row[s_col_name],
                   c=row[c_col_name], **kwargs_scatter_dict)
        # add confidene intervals
        # if none replace with the point estimate
        if lb_col is None:
            lb = xs
        else:
            lb = row[lb_col]
        if ub_col is None:
            ub = xs
        else:
            ub = row[ub_col]
        # plot
        x_values = [lb, ub]
        y_values = [ys, ys]
        ax.plot(x_values, y_values, c=ci_colour, linewidth=ci_lwd,
                **kwargs_plot_ci_dict)
    # ################## aggregate coordinates
    # NOTE define min, max, mean as constants at the start
    group_y = df.groupby(y_col).agg({x_col: {'min', 'max'}})
    y_locations = df.groupby(g_col).agg({y_col: {'mean', 'min', 'max'}})
    # ################## segments between points
    if connect_shape ==True:
        xg_value = [ [min, max] for min, max in zip(group_y[x_col,'min'], group_y[x_col,'max'])]
        yg_value = [ [yval, yval] for yval in  group_y.index]
        for xg, yg in zip(xg_value, yg_value):
            # only add segments if there are two distinct x-values
            if np.unique(xg).shape[0] == 2:
                ax.plot(xg, yg, c=connect_shape_colour,
                        linewidth=connect_shape_lwd, zorder=0,
                        **kwargs_connect_segments_dict)
            else:
                warnings.warn('The line segments have the same x-axis value, '
                              'the line plotting will be skipped.', RuntimeWarning)
    # ################### calculate y-axis mid points
    y_locations = y_locations[y_col].sort_values('min')
    y_mid = []
    for r in range(y_locations.shape[0]):
        maxy = y_locations.iloc[r]['max']
        try:
            miny = y_locations.iloc[r+1]['min']
        except IndexError:
            miny = np.nan
        # get mid
        y_mid.append(np.nanmean([maxy, miny]))
    # add the starting and endpoints
    y_mid.insert(0, y_locations.iloc[0]['min'])
    y_mid[-1] = ax.get_ylim()[1] # replace with y-axis limit
    # ################### Add horizontal segments
    if span ==True:
        # NOTE: not sure this part is required
        # # ensure y_mid is a whole number
        # whole_bool = [float(y).is_integer() for y in y_mid]
        # if all(whole_bool) == False:
        #     # round
        #     y_mid = [y if b==True else round(y,0) for y,b in zip(y_mid, whole_bool)]
        #     # warn
        #     warnings.warn('The axis mid-points are not a whole number, will use \
# approximate coordinates for the horizontal segments', RuntimeWarning)
        # NOTE: end
        # add segments
        for t in range(len(y_mid)):
            ymin = y_mid[t]
            # stop if t is too large
            try:
                ymax = y_mid[t+1]
            except IndexError:
                ymax = y_mid[t]
                pass
            # change every second step
            if t % 2 == 0:
                col = span_colour[0]
            else:
                col = span_colour[1]
            # plot
            ax.axhspan(ymin, ymax, color=col,zorder=0, **kwargs_span_dict)
    # ################### adjust y margins
    new_margins = [ax.get_ylim()[0], ax.get_ylim()[1]]
    new_margins[1] = y_mid[-1]
    ax.set_ylim(new_margins)
    # ################### add y-axis labels
    ax.set_yticks(y_locations['mean'])
    ax.set_yticklabels(y_locations.index)
    # ################### invert y-axis
    if reverse_y == True:
        ax.invert_yaxis()
        # plt.gca().invert_yaxis()
    # ################### return the figure and axis
    return f, ax


