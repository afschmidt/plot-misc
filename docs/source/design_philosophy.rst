Design Philosophy
=================

Overview
--------

This package aims to provide a suite of lightweight plotting functions
and utilities, built on top of `matplotlib`, with a focus on 
epidemiological and medical research applications.
The emphasis is on clarity, modularity, and compatibility with 
existing `matplotlib` axes and figures—enabling integration into 
broader workflows without imposing unnecessary constraints.

The package is intended solely as a plotting toolkit. Users are 
expected to curate and prepare their data in a format suitable for 
plotting.
However, in practice, data analysis and plotting may be  
closely linked.
In such cases, it may be appropriate to integrate 
limited analytical functionality into the plotting function.

Where this occurs, analysis components should be fully customisable 
by the user—ideally through parameters that accept `Callable` 
objects, and any generated intermediate data should be returned 
or exposed for further inspection and reuse.

The overall design encourages minimalism: each function should do 
one thing well, be easily customisable, and produce clean, 
publication-ready output.


Design Principles
-----------------

The following principles guide the structure and development of this package:

- **Matplotlib-first**: All plots are built directly on `matplotlib`.
  Functions should accept an optional `Axes` object and always return the
  modified `Axes`, enabling further customisation within broader plotting 
  contexts.

- **Plotting, not preprocessing**: Functions assume that the input data have 
  already been curated and formatted appropriately.
  If minimal processing is needed, it should remain transparent, documented,
  and not obscure the user's control over the data.

- **Lightweight analysis where justified**: In cases where analysis and
  plotting are tightly coupled, analytical components may be included,
  but should:
  
  - Be fully customisable (e.g. via `Callable` parameters);
  - Clearly separate analysis from visualisation logic;
  - Return or expose intermediate data for reuse or inspection.

- **Minimal and composable**: Each function should do one thing well.
  Shared logic and formatting should be abstracted to utilities in 
  `plot_misc.utils` to encourage reuse and consistency.

- **Transparent behaviour**: Avoid hidden state, unexpected side effects,
  or tightly coupled logic. Code should be easy to understand, inspect,
  and override.
