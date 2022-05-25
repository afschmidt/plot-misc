from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster import hierarchy as hc
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_samples, silhouette_score
from typing import Any, List, Type, Union, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pick_clusters(data:pd.DataFrame, metric:str='euclidean', method:str='complete',
               nmax:int=10, m:Union[int,None]=None, col:str='Set2') -> pd.DataFrame:
    '''
    Function to select the optimum cut-point for a hc cluster algorithm and,
    generate groups and colours.
    '''
    # optimum no. of clusters
    silhoutte = {}
    for n in range(2,nmax+1):
        groups = hc.fclusterdata(data, metric=metric, method=method,
                    criterion='maxclust', t=n)
        silhoutte[n] = silhouette_score(data, groups)
        print(str(n) + ': ' + str(silhoutte[n]))
        del groups
    
    if m is None:
        nocluster = pd.DataFrame(silhoutte, index=[0]).transpose().idxmax()[0]
    else:
        nocluster = m
    groups = pd.Series(hc.fclusterdata(data, metric=metric, method=method,
                    criterion='maxclust', t=nocluster))
    lut = dict(zip(groups.unique(),sns.color_palette(col, nocluster)))
    row_colors = pd.DataFrame(groups)[0].map(lut).to_frame()
    row_colors.rename(columns = {'[0]': 'cluster'}, inplace=True)
    row_colors.columns = ['Groups']
    row_colors.set_index(data.index, inplace=True)
    print('Optimal number of clusters: ' + str(nocluster))
    print('Validity metric: ' + str(silhoutte[nocluster]))
    
    return row_colors

# # EXAMPLE USAGE
# # standardizing the rows (so we will cluster on differences between lipids)
# sd2 = pval2.sub(pval2.mean(1), axis=0).div(pval2.std(1), axis=0)
# sd1 = pval1.sub(pval1.mean(1), axis=0).div(pval1.std(1), axis=0)
# # standardizing the columns
# # sd1=(pval1-pval1.mean())/pval1.std()
# # sd2=(pval2-pval2.mean())/pval2.std()
# link2 = hc.linkage(sd2, method='average')
# link1 = hc.linkage(sd1, method='average')
# # groups
# rc2 = sel_groups(sd2, method='average', metric='euclidean', nmax=20, col='Set3')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def clustermap(data:pd.DataFrame, annot:pd.DataFrame, col:List[float],
               fsize:Tuple[float]=(20, 25), fscale:float=0.393700787,
               linewidths:float=1.0,
               cpos:Tuple[float]=(0.09, 0.02, 0.03, 0.10), fmt:str=".3",
               annotsize:float=6, clab:str=r"dir $\times -\log_{10}$(p)",
               clabfs:float=7, clabpos:str='left', clabtsize:float=5,
               xticklabsize:float=8, yticklabsize:float=6,
               **kwargs:Optional[Any]) -> plt.Figure:
    '''
    Wrapper over seaborn.clustermap.
    
    Arguments
    ---------
    data         : pd.DF
    annot        : pd.DF
    fsize        : tuple of floats
    fscale       : float
    linewidths   : float
    cpos         : tuple of floats
    annotsize    : float
    clab         : str
    clabsf       : float
    clabpos      : str
    clabsize     : float
    xticklabsize : float
    yticklabsize : float
    **kwargs     : dict
    
    Returns
    -------
    seaborn.clustermap figure
    
    '''
            
    cm = sns.clustermap(data, fmt=fmt, linewidths=linewidths,
                    figsize=(fsize[0] * fscale, fsize[1] * fscale),
                    cmap=col,
                    annot=annot, cbar_pos=cpos,
                    annot_kws={"size": annotsize},
                    **kwargs
                   )
    # cbar labels
    cm.ax_cbar.axes.yaxis.set_label_text(clab, fontsize=clabfs)
    cm.ax_cbar.axes.yaxis.set_label_position(clabpos)
    cm.ax_cbar.tick_params(labelsize=clabtsize)
    # heatmap tick labels
    cm.ax_heatmap.set_xticklabels(cm.ax_heatmap.get_xmajorticklabels(),
                                   fontsize = xticklabsize)
    cm.ax_heatmap.set_yticklabels(cm.ax_heatmap.get_ymajorticklabels(),
                                   fontsize = yticklabsize)
    # removing axis labels
    cm.ax_heatmap.set_ylabel("")
    cm.ax_heatmap.set_xlabel("")
    # add both xy ticks (should add this as arguments)
    cg.ax_heatmap.tick_params('both', reset=False, bottom=True, right=True)
    return cm


