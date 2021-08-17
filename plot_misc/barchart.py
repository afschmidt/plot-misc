"""
Various bar chart functions.
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stack_bar(df, label, columns, ax, colours=['tab:blue', 'tab:pink'],
              transparancy=0.7, wd=1, edgecolour='black', **kwargs):
    '''
    Function for a bar chart, remove top and left spines.
    
    Arguments
    ---------
    df : pd.DataFrame
    label : str
        Column name in `df`.
    columns : list of strings
        List of column names in `df`.
    ax : plt.ax
    colours : list
        List with the number of colours equal to len(columns).
    transparancy : float, 0.7
        Degree of transparancy, between 0 and 1 (solid).
    wd : float
        Bar width.
    edgecolour : str of colours, default `black`.
    kwargs : dict
        Dictionary of kwargs
    
    Returns
    -------
    plt.ax
    '''
    
    # get labels
    labels = df[label]
    # get columns
    fields=columns
    
    # actual plotting
    left = len(df) * [0]
    for idx, name in enumerate(fields):
        ax.bar(labels, height=df[name], bottom = left, edgecolor=edgecolour,
                width=wd, color=colours[idx], alpha=transparancy,
                **kwargs)
        left = left + df[name]
    
    # removing spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stack_barh(df, label, columns, ax, colours=['tab:blue', 'tab:pink'],
              transparancy=0.7, wd=1, edgecolour='black', **kwargs):
    '''
    Function for a horizontal bar chart, remove top and left spines.
    
    Arguments
    ---------
    df : pd.DataFrame
    label : str
        Column name in `df`.
    columns : list of strings
        List of column names in `df`.
    ax : plt.ax
    colours : list
        List with the number of colours equal to len(columns).
    transparancy : float, 0.7
        Degree of transparancy, between 0 and 1 (solid).
    wd : float
        Bar width.
    edgecolor : str of colours, default `black`
    kwargs : dict
        Dictionary of kwargs
    
    Returns
    -------
    plt.ax
    '''
    
    # get labels
    labels = df[label]
    # get columns
    fields=columns
    
    # actual plotting
    left = len(df) * [0]
    for idx, name in enumerate(fields):
        ax.barh(labels, width=df[name], left = left, edgecolor=edgecolor,
                height=wd, color=colours[idx], alpha=transparancy,
                **kwargs)
        left = left + df[name]
    
    # removing spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def total_bar(df, label, subtotal_col, ax,
              total_col=None, colours=['grey', 'tab:blue'],
              transparancy=[0.7, 0.9], wd=[1, 0.6],
              edgecolour=['black', 'black'], **kwargs):
    '''
    A bar chart with a total column and overplotted subtotal columns.
    The first entry of each argument refers to the total chart, the second to
    the subtotal chart.
    
    Arguments
    ---------
    df : pd.DF
    label, total_col, subtotal_col : str
        a string referring to a column in `df`. Skip total_col by setting it
        to None (default).
    colours : list
        A list of colours.
    transparancy, wd : float
        A float to specify the colour alpha and bar width, respectivly.
    edgecolour : str
        The bar edgecolour.
    ax : plt.ax
    kwargs : dict
        Provide a dict of dictionaries with two keys `total_kwargs` and
        `subtotal_kwargs` to supply kwargs for the individual calls to ax.bar.
    '''
    
    # get labels
    labels = df[label]
    
    # counts
    total = df[total_col]
    subtotal = df[subtotal_col]
    
    # kwargs = {'total_kwargs':{'test': 'test'}, 'subtotal_kwargs': {'kwargs': 'test'}}
    if 'total_kwargs' in kwargs and 'subtotal_kwargs' in kwargs:
        total_kwargs = kwargs['total_kwargs']
        subtotal_kwargs = kwargs['subtotal_kwargs']
    else:
        total_kwargs = kwargs
        subtotal_kwargs = kwargs
    
    # plot total
    if not total_col is None:
        ax.bar(labels,height=total, edgecolor=edgecolour[0], width=wd[0],
               color=colours[0], alpha=transparancy[0],
               **total_kwargs)
    
    # plot subtotal
    ax.bar(labels,height=subtotal, edgecolor=edgecolour[1],
           width=wd[1], color=colours[1], alpha=transparancy[1],
           **subtotal_kwargs)
    
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bar(df, label, column, ax, colours=['tab:blue', 'tab:pink'],
              transparancy=0.7, wd=1, edgecolour='black', **kwargs):
    '''
    Plot a barchart with sequentially coloured bars.
    
    Arguments
    ---------
    df : pd.DF
    label, columns : str
        a string referring to a column in `df` representing the x-axis labels
        and the y-axis values, respectivly.
    colours : list
        A list of colours.
    transparancy, wd : float
        A float to specify the colour alpha and bar width, respectivly.
    edgecolour : str
        The bar edgecolour.
    ax : plt.ax
    kwargs : dict
        Provide a dict of dictionaries with two keys `total_kwargs` and
        `subtotal_kwargs` to supply kwargs for the individual calls to ax.bar.
    '''
    # get labels
    labels = df[label]
    
    # actual plotting
    ax.bar(labels,height=df[column], edgecolor=edgecolour,
           width=wd, color=colours, alpha=transparancy, **kwargs)
    
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    return ax
