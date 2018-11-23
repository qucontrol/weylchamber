from mpl_toolkits.mplot3d import Axes3D  # required to activate 2D plotting
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch

import numpy as np

__all__ = ['WeylChamber']


class WeylChamber():
    """Class for plotting data in the Weyl Chamber

    Class Attributes
    ----------------

    weyl_points: dict
        Dictionary of Weyl chamber point names to (c1, c2, c3) coordinates (in
        units of pi). Each point name is also a class attribute itself
    normal: dict
        Dictionary of Weyl chamber region name to normal vectors for the
        surface that separates the region from the polyhedron of perfect
        entanglers (pointing outwards from the PE's). The three regions are:

        * 'W0': region from the origin point (O) to the PE polyhedron
        * 'W0*': region from the A2 point to the PE polyhedron
        * 'W1': region from the A2 point (SWAP gate) to the PE polyhedron

    anchor: dict
        Dictionary of anchor points for the normal vectors (i.e., an arbitrary
        point on the surface that separates the region specified by the key
        from the perfect entanglers polyhedron

    Attributes
    ----------
    fig_width : float {8.5}
        Figure width, in cm
    fig_height: float {6.0}
        Figure height, in cm
    left_margin: float {0.0}
        Distance from left figure edge to axes, in cm
    bottom_margin: float {0.0}
        Distance from bottom figure edge to axes, in cm
    right_margin: float {0.3}
        Distance from right figure edge to axes, in cm
    top_margin: float {0.0}
        Distance from top figure edge to axes, in cm
    azim: float {-50}
        azimuthal view angle in degrees
    elev: float {-20}
        elevation view angle in degrees
    dpi: int {300}
        Resolution to use when saving to dpi, or showing interactively
    linecolor: str {'black'}
        Color to be used when drawing lines (e.g. the edges of the Weyl
        chamber)
    show_c1_label: bool
        Whether or not to show the c1 axis label
    show_c2_label: bool
        Whether or not to show the c2 axis label
    show_c3_label: bool
        Whether or not to show the c3 axis label
    c1_labelpad: float
        Label padding for c1 label
    c2_labelpad: float
        Label padding for c2 label
    c3_labelpad: float
        Label padding for c3 label
    c1_tickspad: float
        Padding for c1 tick labels
    c2_tickspad: float
        Padding for c2 tick labels
    c3_tickspad: float
        Padding for c2 tick labels
    weyl_edges: list
        List of tuples (point1, point2, foreground) where point1 and point2 are
        keys in `weyl_points`, and foreground is a logical to indicate whether
        the edge is in the background or foreground (depending on the
        perspective of the plot). Describes the lines that make up the Weyl
        chamber.
    weyl_edge_fg_properties: dict
        Properties to be used when drawing foreground weyl_edges
    weyl_edge_bg_properties: dict
        Properties to be used when drawing background weyl_edges
    PE_edges: list
        List of tuples (point1, point2, foreground) where point1 and point2 are
        keys in weyl_points, and foreground is a logical to indicate whether
        the edge is in the background or foreground (depending on the
        perspective of the plot). Desribes the lines that make up the
        polyhedron of perfect entanglers
    PE_edge_fg_properties: dict
        Properties to be used when drawing foreground PE_edges
    PE_edge_bg_properties: dict
        Properties to be used when drawing background PE_edges
    labels: dict
        label names => array (c1, c2, c3) where label should be drawn
    tex_labels: logical {True}
        If True wrap label names in dollar signs to produce a latex string.
    label_properties: dict
        Properties to be used when drawing labels
    z_axis_left: logical {True}
        If True, draw z-axis on the left
    grid: logical {False}
        Show a grid on panes?
    panecolor: None or tuple  {(1.0, 1.0, 1.0, 0.0)}
        Color (r, g, b, alpha) with values in [0,1] for the c1, c2, and c3
        panes
    facecolor: str {'None'}
        Name of color for figure background
    ticklabelsize: float {7}
        font size for tick labels
    full_cube: logical {False}
        if True, draw all three axes in the range [0,1]. This may result in a
        less distorted view of the Weyl chamber
    """
    A1 = np.array((1, 0, 0))
    A2 = np.array((0.5, 0.5, 0))
    A3 = np.array((0.5, 0.5, 0.5))
    O  = np.array((0, 0, 0))
    L  = np.array((0.5, 0, 0))
    M  = np.array((0.75, 0.25, 0))
    N  = np.array((0.75, 0.25, 0.25))
    P  = np.array((0.25, 0.25, 0.25))
    Q  = np.array((0.25, 0.25, 0))
    weyl_points = {'A1' : A1, 'A2' : A2, 'A3' : A3, 'O' : O, 'L' : L,
                   'M' : M, 'N' : N, 'P' : P, 'Q': Q}
    normal = {'W0' : (np.sqrt(2.0)/2.0)*np.array((-1, -1, 0)),
              'W0*': (np.sqrt(2.0)/2.0)*np.array(( 1, -1, 0)),
              'W1' : (np.sqrt(2.0)/2.0)*np.array(( 0,  1, 1))}
    anchor = {'W0': L, 'W0*': L, 'W1': A2}

    def __init__(self):
        self._fig = None
        self._ax = None
        self._artists = None
        self.azim = -50
        self.elev = 20
        self.dpi = 300
        self.fig_width = 8.5
        self.fig_height = 6.0
        self.left_margin = 0.0
        self.bottom_margin =  0.0
        self.right_margin =  0.3
        self.top_margin =  0.0
        self.linecolor = 'black'
        self.show_c1_label = True
        self.show_c2_label = True
        self.show_c3_label = True
        self.c1_labelpad = -9
        self.c2_labelpad = -14
        self.c3_labelpad = -14
        self.c1_tickspad = -6.0
        self.c2_tickspad = -4.0
        self.c3_tickspad = -6.0
        self.weyl_edge_fg_properties = {
                'color':'black', 'linestyle':'-', 'lw':0.5}
        self.weyl_edge_bg_properties = {
                'color':'black', 'linestyle':'--', 'lw':0.5}
        self.PE_edge_fg_properties = {
                'color':'black', 'linestyle':'-', 'lw':0.5}
        self.PE_edge_bg_properties = {
                'color':'black', 'linestyle':'--', 'lw':0.5}
        self.weyl_edges = [
            [ 'O', 'A1', True],
            ['A1', 'A2', True],
            ['A2', 'A3', True],
            ['A3', 'A1', True],
            ['A3',  'O', True],
            [ 'O', 'A2', False]
        ]
        self.PE_edges = [
            ['L',  'N', True],
            ['L',  'P', True],
            ['N',  'P', True],
            ['N', 'A2', True],
            ['N',  'M', True],
            ['M',  'L', False],
            ['Q',  'L', False],
            ['P',  'Q', False],
            ['P', 'A2', False]
        ]
        self.labels = {
            'A_1' : self.A1 + np.array((-0.03, 0.04 , 0.00)),
            'A_2' : self.A2 + np.array((0.01, 0, -0.01)),
            'A_3' : self.A3 + np.array((-0.01, 0, 0)),
            'O'   : self.O  + np.array((-0.025,  0.0, 0.02)),
            'L'   : self.L  + np.array((-0.075, 0, 0.01)),
            'M'   : self.M  + np.array((0.05, -0.01, 0)),
            'N'   : self.N  + np.array((-0.075, 0, 0.009)),
            'P'   : self.P  + np.array((-0.05, 0, 0.008)),
            'Q'   : self.Q  + np.array((0, 0.01, 0.03)),
        }
        self.label_properties = {
            'color': 'black',  'fontsize': 'small'
        }
        self.tex_labels = True
        self.z_axis_left = True
        self.grid = False
        self.panecolor = (1.0, 1.0, 1.0, 0.0)
        self.facecolor = 'None'
        self.ticklabelsize = 7
        self.full_cube = False
        self._scatter = []

    @property
    def figsize(self):
        """Tuple (width, height) of figure size in inches"""
        cm2inch = 0.39370079 # conversion factor cm to inch
        return (self.fig_width*cm2inch, self.fig_height*cm2inch)

    @property
    def fig(self):
        """Return a reference to the figure on which the Weyl chamber has been
        rendered. Undefined unless the `render` method has been called."""
        return self._fig

    @property
    def ax(self):
        """Return a reference to the Axes instance on which the Weyl chamber
        has been rendered. Undefined unless the `render` method has been
        called."""
        return self._ax

    @property
    def artists(self):
        """Return a list of rendered artists. This includes only artists that
        were created as part of a plotting command, not things like the edges
        of the Weyl chamber or the perfect entanglers polyhedron"""
        return self._artists

    def _repr_png_(self):  # pragma: no cover
        from IPython.core.pylabtools import print_figure
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        self.render(ax)
        fig_data = print_figure(fig, 'png')
        plt.close(fig)
        return fig_data

    def _repr_svg_(self):  # pragma: no cover
        from IPython.core.pylabtools import print_figure
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        self.render(ax)
        fig_data = print_figure(fig, 'svg')
        plt.close(fig)
        return fig_data

    def render(self, ax):
        """Render the Weyl chamber on the given Axes3D object"""
        self._ax = ax
        self._fig = ax.figure
        self._artists = []
        ax.view_init(elev=self.elev, azim=self.azim)
        ax.patch.set_facecolor(self.facecolor)
        if self.panecolor is not None:
            ax.w_xaxis.set_pane_color(self.panecolor)
            ax.w_yaxis.set_pane_color(self.panecolor)
            ax.w_zaxis.set_pane_color(self.panecolor)
        if self.z_axis_left:
            tmp_planes = ax.zaxis._PLANES
            ax.zaxis._PLANES = (tmp_planes[2], tmp_planes[3],
                                tmp_planes[0], tmp_planes[1],
                                tmp_planes[4], tmp_planes[5])
            ax.zaxis.set_rotate_label(False)
            ax.zaxis.label.set_rotation(90)
        ax.grid(self.grid)
        # background lines
        for P1, P2, fg in self.weyl_edges:
            if not fg:
                self._draw_line(ax, P1, P2, zorder=-1,
                               **self.weyl_edge_bg_properties)
        for P1, P2, fg in self.PE_edges:
            if not fg:
                self._draw_line(ax, P1, P2, zorder=-1,
                               **self.PE_edge_bg_properties)
        # scatter plots
        for c1, c2, c3, kwargs in self._scatter:
            self._artists.append(ax.scatter3D(c1, c2, c3, **kwargs))
        pass # plot everything else
        # labels
        for label in self.labels:
            c1, c2, c3 = self.labels[label]
            if self.tex_labels:
                ax.text(c1, c2, c3, "$%s$" % label, **self.label_properties)
            else:
                ax.text(c1, c2, c3, label, **self.label_properties)
        # foreground lines
        for P1, P2, fg in self.weyl_edges:
            if fg:
                self._draw_line(ax, P1, P2, **self.weyl_edge_fg_properties)
        for P1, P2, fg in self.PE_edges:
            if fg:
                self._draw_line(ax, P1, P2, **self.PE_edge_fg_properties)
        ax.set_xlabel(r'$c_1/\pi$')
        ax.set_ylabel(r'$c_2/\pi$')
        ax.set_zlabel(r'$c_3/\pi$')
        if self.full_cube:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_zlim(0, 1)
        else:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 0.5)
            ax.set_zlim(0, 0.5)
        if self.show_c1_label:
            ax.set_xlabel(r'$c_1$', labelpad=self.c1_labelpad)
        if self.show_c2_label:
            ax.set_ylabel(r'$c_2$', labelpad=self.c2_labelpad)
        if self.show_c3_label:
            ax.set_zlabel(r'$c_3$', labelpad=self.c3_labelpad)
        ax.set_xlim(0,1)
        ax.set_ylim(0,0.5)
        ax.set_zlim(0,0.5)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(['0', '', '$\pi/2$', '', r'$\pi$'])
        ax.set_yticklabels(['0', '', '', '', '', r'$\pi/2$'])
        ax.set_zticklabels(['0', '', '', '', '', r'$\pi/2$'])
        ax.tick_params(axis='x', pad=self.c1_tickspad)
        ax.tick_params(axis='y', pad=self.c2_tickspad)
        ax.tick_params(axis='z', pad=self.c2_tickspad)
        [t.set_va('center') for t in ax.get_yticklabels()]
        [t.set_ha('left') for t in ax.get_yticklabels()]
        [t.set_va('center') for t in ax.get_zticklabels()]
        [t.set_ha('right') for t in ax.get_zticklabels()]

    def plot(self, fig=None):
        """Generate a plot of the Weyl chamber on the given figure, or create a
        new figure if fig argument is not given.
        """
        if fig is None:
            import matplotlib.pylab as plt
            fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        w = self.fig_width - (self.left_margin + self.right_margin)
        h = self.fig_height - (self.bottom_margin + self.top_margin)
        pos = [self.left_margin/self.fig_width,
               self.bottom_margin/self.fig_height,
               w/self.fig_width, h/self.fig_height]
        ax = fig.add_axes(pos, projection='3d')
        self.render(ax)

    def scatter(self, c1, c2, c3, **kwargs):
        """Add a scatter plot to the Weyl chamber

        All keyword arguments will be passed to matplotlib scatter3D
        function.
        """
        self._scatter.append((c1, c2, c3, kwargs))

    def add_point(self, c1, c2, c3, scatter_index=0, **kwargs):
        """Add a point to a scatter plot with the given `scatter_index`.

        If there is no existing scatter plot with that index, a new one will be
        created.  The arguments of the scatter plot are updated with the given
        kwargs.
        """
        try:
            c1s, c2s, c3s, kw = self._scatter[scatter_index]
            kw.update(kwargs)
            self._scatter[scatter_index] = (np.append(c1s, [c1, ]),
                                            np.append(c2s, [c2, ]),
                                            np.append(c3s, [c3, ]),
                                            kw)
        except IndexError:
            self._scatter.append((np.array([c1, ]), np.array([c2, ]),
                                  np.array([c3, ]), kwargs))

    def _draw_line(self, ax, origin, end, **kwargs):
        """Draw a line from origin to end onto the given axis. Both origin and
        end must either be 3-tuples, or names of Weyl points. All keyword
        arguments are passed to the `ax.plot` method
        """
        try:
            if origin in self.weyl_points:
                o1, o2, o3 = self.weyl_points[origin]
            else:
                o1, o2, o3 = origin
        except ValueError:  # pragma: nocover
            raise ValueError("origin '%s' is not in weyl_points "
                             "or a list (c1, c2, c3)" % origin)
        try:
            if end in self.weyl_points:
                c1, c2, c3 = self.weyl_points[end]
            else:
                c1, c2, c3 = end
        except ValueError:  # pragma: nocover
            raise ValueError("origin '%s' is not in weyl_points "
                             "or a list (c1, c2, c3)" % origin)
        ax.plot([o1, c1], [o2, c2], [o3, c3], **kwargs)

    def _draw_arrow(self, ax, origin, end, **kwargs):  # pragma: nocover
        # currently undocumented/unused feature, but can be useful when having
        # to mark a point in an error in a publication graphic
        try:
            if origin in self.weyl_points:
                o1, o2, o3 = self.weyl_points[origin]
            else:
                o1, o2, o3 = origin
        except ValueError:  # pragma: nocover
            raise ValueError("origin '%s' is not in weyl_points "
                             "or a list (c1, c2, c3)" % origin)
        try:
            if end in self.weyl_points:
                c1, c2, c3 = self.weyl_points[end]
            else:
                c1, c2, c3 = end
        except ValueError:  # pragma: nocover
            raise ValueError("origin '%s' is not in weyl_points "
                             "or a list (c1, c2, c3)" % origin)
        a = _Arrow3D(
            [o1, c1], [o2, c2], [o3, c3], mutation_scale=10, lw=1.5,
            arrowstyle="-|>", **kwargs)
        ax.add_artist(a)


class _Arrow3D(FancyArrowPatch):  # pragma: no cover
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)
