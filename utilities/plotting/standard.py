from matplotlib.pyplot import subplots, tight_layout, savefig
from numpy import arange, array, ndarray
from utilities.plotting.utilities import generate_3d_figure


def bar_plot(values, features, fig_title, filename=None, horizontal=False):
    """
    Generates a bar plot
    :param values: List of values
    :param features: List of features
    :param fig_title: Figure title
    :param filename: File path to save figure to, (default doesn't save)
    :param horizontal: Whether to use a horizontal bar plot, (default False)
    :return: (figure, axis) to allow further modification of plot
    """
    fig, ax = subplots()

    plot_type = ax.bar if not horizontal else ax.barh
    plot_type(list(range(len(values))), values)

    ax.set_xticks(arange(len(features)))
    ax.set_xticklabels(features, rotation='vertical')
    ax.set_title(fig_title)
    tight_layout()

    if filename is not None:
        savefig(filename)

    return fig, ax


def scatter_plot(values, fig_title, weights=None, filename=None, pre_split=True, c_bar_title=None, cmap='Blues'):
    """
    Makes a 2D scatter plot
    :param values:
    :param fig_title:
    :param weights:
    :param filename:
    :param pre_split:
    :param c_bar_title:
    :param cmap:
    :return:
    """
    fig, ax = subplots()

    if not pre_split:
        values = values if type(values) is ndarray else array(values)
        x, y = values[:, 0], values[:, 1]
    else:
        [x, y] = values

    img = ax.scatter(x, y, c=weights, cmap=cmap, edgecolors='k')

    ax.set_title(fig_title)
    if weights is not None:
        c_bar = fig.colorbar(img, ax=ax)
        if c_bar_title is not None:
            c_bar.ax.set_ylabel(c_bar_title)
    if filename is not None:
        savefig(filename)

    return ax


def scatter_3_plot(values, fig_title, weights=None, filename=None, ax_titles=None, cmap='Blues', c_bar_title=None):
    fig, ax = generate_3d_figure()

    values = array(values) if type(values) is not ndarray else values
    if len(values) != 3:
        raise ValueError('Values should has shape (3, X), got', values.shape)
    if ax_titles is not None and len(ax_titles) != 3:
        raise ValueError('Axis titles should be a list or tuple with length 3')

    x, y, z = values
    if weights is None:
        ax.scatter(x, y, z)
    else:
        img = ax.scatter(x, y, z, c=weights, cmap=cmap, edgecolors='k')
        c_bar = fig.colorbar(img, ax=ax)
        if c_bar_title is not None:
            c_bar.ax.set_ylabel(c_bar_title)

    if ax_titles is not None:
        x_t, y_t, z_t = ax_titles
        ax.set_xlabel(x_t)
        ax.set_ylabel(y_t)
        ax.set_zlabel(z_t)
    ax.set_title(fig_title)

    if filename is not None:
        savefig(filename)

    return ax
