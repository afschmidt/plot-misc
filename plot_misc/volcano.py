import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_volcano(data, label='fig_lab', legend='no', fsize=(7,10),
                 xlim = None,
                 col=('orangered','dimgrey','lightcoral'),
                 adjust=False, lim=1000, **kwargs):
    # col=('orangered','dimgrey','lightcoral')
    # data=AF
    # label='fig_lab'
    # lim=1000
    # xlim=(-0.6, 0.6)
    # fsize=(7,10)
    f, ax = plt.subplots(figsize=fsize)
    threshold = -1 * np.log10(0.00001)
    # setting a reference line (zorder=1; behind)
    ax.axvline(x=0, c=col[2], linestyle='--', zorder=1, linewidth=1)
    # getting data above threshold
    above = data[data.pval >= threshold]
    xs = above.effect
    ys = above.pval
    ax.scatter(xs, ys, c=col[0], edgecolor=(1, 1, 1, 0), zorder=2,
                label=r'$-\log_{10}$(p-value) > ' + str(round(threshold, 2)))
    # getting data below threshold
    below = data[data.pval < threshold]
    xns = below.effect
    yns = below.pval
    ax.scatter(xns, yns, c=col[1], edgecolor=(1, 1, 1, 0), label='Not Sig',
                zorder=2)
    # adding xlimits
    if not xlim is None:
        plt.xlim(xlim)
    # adding text
    texts = []
    for x, y, l in zip(xs, ys, above[label]):
        texts.append(ax.text(x, y, l, size=8))
    if legend == 'print':
        ax.legend()
    plt.xlabel('MR effect')
    plt.ylabel(r'$-log_{10}(pvalue)$')
    if adjust:
        adjust_text(texts, lim=lim, zorder=3, arrowprops=dict(arrowstyle="-", color='k',
                                                    lw=0.5), **kwargs)
    return ax


