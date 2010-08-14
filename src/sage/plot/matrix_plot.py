"""
Matrix Plots
"""

#*****************************************************************************
#       Copyright (C) 2006 Alex Clemesha <clemesha@gmail.com>,
#                          William Stein <wstein@gmail.com>,
#                     2008 Mike Hansen <mhansen@gmail.com>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.plot.primitive import GraphicPrimitive
from sage.plot.misc import options, rename_keyword
from sage.plot.colors import to_mpl_color, get_cmap

class MatrixPlot(GraphicPrimitive):
    """
    Primitive class for the matrix plot graphics type.  See
    ``matrix_plot?`` for help actually doing matrix plots.

    INPUT:

    - ``xy_data_array`` - list of lists giving matrix values corresponding to
      the grid

    - ``xrange`` - tuple of 2 floats indicating range for horizontal direction
      (number of columns in the matrix)

    - ``yrange`` - tuple of 2 floats indicating range for vertical direction
      (number of rows in the matrix)

    - ``options`` - dict of valid plot options to pass to constructor

    EXAMPLES:

    Note this should normally be used indirectly via :func:`matrix_plot`::

        sage: from sage.plot.matrix_plot import MatrixPlot
        sage: M = MatrixPlot([[1,3],[2,4]],(1,2),(2,3),options={'cmap':'winter'})
        sage: M
        MatrixPlot defined by a 2 x 2 data grid
        sage: M.yrange
        (2, 3)
        sage: M.xy_data_array
        [[1, 3], [2, 4]]
        sage: M.options()
        {'cmap': 'winter'}

    Extra options will get passed on to :meth:`~sage.plot.plot.Graphics.show`, as long as they are valid::

        sage: matrix_plot([[1, 0], [0, 1]], fontsize=10)
        sage: matrix_plot([[1, 0], [0, 1]]).show(fontsize=10) # These are equivalent

    TESTS:

    We test creating a matrix plot::

        sage: matrix_plot([[mod(i,5)^j for i in range(5)] for j in range(1,6)])
    """
    def __init__(self, xy_data_array, xrange, yrange, options):
        """
        Initializes base class MatrixPlot.

        EXAMPLES::

            sage: M = matrix_plot([[mod(i,5)^j for i in range(5)] for j in range(1,6)], cmap='jet')
            sage: M[0].xrange
            (0, 5)
            sage: M[0].options()['cmap']
            'jet'
            sage: M[0].xy_array_row
            5
        """
        self.xrange = xrange
        self.yrange = yrange
        self.xy_data_array = xy_data_array
        if hasattr(xy_data_array, 'shape'):
            self.xy_array_row = xy_data_array.shape[0]
            self.xy_array_col = xy_data_array.shape[1]
        else:
            self.xy_array_row = len(xy_data_array)
            self.xy_array_col = len(xy_data_array[0])
        GraphicPrimitive.__init__(self, options)

    def get_minmax_data(self):
        """
        Returns a dictionary with the bounding box data.

        EXAMPLES::

            sage: m = matrix_plot(matrix([[1,3,5,1],[2,4,5,6],[1,3,5,7]]))[0]
            sage: list(sorted(m.get_minmax_data().items()))
            [('xmax', 3.5), ('xmin', -0.5), ('ymax', -0.5), ('ymin', 2.5)]


        """
        from sage.plot.plot import minmax_data
        limits= minmax_data(self.xrange, self.yrange, dict=True)
        if self.options()['origin']!='lower':
            # flip y-axis so that the picture looks correct.
            limits['ymin'],limits['ymax']=limits['ymax'],limits['ymin']

        # center the matrix so that, for example, the square representing the
        # (0,0) entry is centered on the origin.
        for k,v in limits.iteritems():
            limits[k]-=0.5
        return limits

    def _allowed_options(self):
        """
        Return the allowed options for the MatrixPlot class.

        EXAMPLES::

            sage: M = matrix_plot([[sin(i*j) for i in range(5)] for j in range(5)])
            sage: isinstance(M[0]._allowed_options(),dict)
            True
        """
        return {'cmap':"""the name of a predefined colormap,
                        a list of colors, or an instance of a
                        matplotlib Colormap. Type: import matplotlib.cm; matplotlib.cm.datad.keys()
                        for available colormap names.""",
                'zorder':"The layer level in which to draw",
                'marker':"The marker for sparse plots",
                'markersize':"The marker size for sparse plots",
                'norm': "The normalization function",
                'vmin': "The minimum value",
                'vmax': "The maximum value",
                'origin': "If 'lower', draw the matrix with the first row on the bottom of the graph"}

    def _repr_(self):
        """
        String representation of MatrixPlot primitive.

        EXAMPLES::

            sage: M = matrix_plot([[sin(i*j) for i in range(5)] for j in range(5)])
            sage: m = M[0]; m
            MatrixPlot defined by a 5 x 5 data grid
        """
        return "MatrixPlot defined by a %s x %s data grid"%(self.xy_array_row, self.xy_array_col)

    def _render_on_subplot(self, subplot):
        """
        TESTS::

            sage: matrix_plot(random_matrix(RDF, 50), cmap='jet')
        """
        options = self.options()
        cmap = get_cmap(options.pop('cmap',None))
        origin=options['origin']

        norm=options['norm']

        if norm=='value':
            import matplotlib
            norm=matplotlib.colors.NoNorm()

        if hasattr(self.xy_data_array, 'tocoo'):
            # Sparse matrix -- use spy
            opts=options.copy()
            for opt in ['vmin', 'vmax', 'norm', 'origin']:
                del opts[opt]
            if origin=='lower':
                subplot.spy(self.xy_data_array.tocsr()[::-1], **opts)
            else:
                subplot.spy(self.xy_data_array, **opts)
        else:
            opts = dict(cmap=cmap, interpolation='nearest', aspect='equal',
                      norm=norm, vmin=options['vmin'], vmax=options['vmax'],
                      origin=origin,zorder=options.get('zorder',None))
            subplot.imshow(self.xy_data_array, **opts)
        if origin=='upper':
            subplot.xaxis.tick_top()
        elif origin=='lower':
            subplot.xaxis.tick_bottom()

@options(cmap='gray',marker='.',frame=True, axes=False, norm=None,
         vmin=None, vmax=None, origin='upper',ticks_integer=True)
def matrix_plot(mat, **options):
    r"""
    A plot of a given matrix or 2D array.

    If the matrix is dense, each matrix element is given a different
    color value depending on its relative size compared to the other
    elements in the matrix.  If the matrix is sparse, colors only
    indicate whether an element is nonzero or zero, so the plot
    represents the sparsity pattern of the matrix.

    The tick marks drawn on the frame axes denote the row numbers
    (vertical ticks) and the column numbers (horizontal ticks) of the
    matrix.

    INPUT:

    - ``mat`` - a 2D matrix or array

    The following input must all be passed in as named parameters, if
    default not used:

    - ``cmap`` - a colormap (default: 'gray'), the name of
      a predefined colormap, a list of colors,
      or an instance of a matplotlib Colormap.
      Type: ``import matplotlib.cm; matplotlib.cm.datad.keys()``
      for available colormap names.

    - ``norm`` - If None (default), the value range is scaled to the interval
      [0,1].  If 'value', then the actual value is used with no
      scaling.  A :class:`matplotlib.colors.Normalize` instance may
      also passed.

    - ``vmin`` - The minimum value (values below this are set to this value)

    - ``vmax`` - The maximum value (values above this are set to this value)

    - ``origin`` - If 'upper' (default), the first row of the matrix
      is on the top of the graph.  If 'lower', the first row is on the
      bottom of the graph.

    EXAMPLES:

    A matrix over `\ZZ` colored with different grey levels::

        sage: matrix_plot(matrix([[1,3,5,1],[2,4,5,6],[1,3,5,7]]))

    Here we make a random matrix over `\RR` and use ``cmap='hsv'``
    to color the matrix elements different RGB colors::

        sage: matrix_plot(random_matrix(RDF, 50), cmap='hsv')

    By default, entries are scaled to the interval [0,1] before
    determining colors from the color map.  That means the two plots
    below are the same::

        sage: P = matrix_plot(matrix(2,[1,1,3,3]))
        sage: Q = matrix_plot(matrix(2,[2,2,3,3]))
        sage: P; Q

    However, we can specify which values scale to 0 or 1 with the
    ``vmin`` and ``vmax`` parameters (values outside the range are
    clipped).  The two plots below are now distinguished::

        sage: P = matrix_plot(matrix(2,[1,1,3,3]), vmin=0, vmax=3)
        sage: Q = matrix_plot(matrix(2,[2,2,3,3]), vmin=0, vmax=3)
        sage: P; Q

    We can also specify a norm function of 'value', which means that
    there is no scaling performed::

        sage: matrix_plot(random_matrix(ZZ,10)*.05, norm='value')

    Generally matrices are plotted with the (0,0) entry in the upper
    left.  However, sometimes if we are plotting an image, we'd like
    the (0,0) entry to be in the lower left.  We can do that with the
    ``origin`` argument::

        sage: matrix_plot(identity_matrix(100), origin='lower')

    Another random plot, but over `\GF{389}`::

        sage: m = random_matrix(GF(389), 10)
        sage: matrix_plot(m, cmap='Oranges')

    It also works if you lift it to the polynomial ring::

        sage: matrix_plot(m.change_ring(GF(389)['x']), cmap='Oranges')

    Here we plot a random sparse matrix::

        sage: sparse = matrix(dict([((randint(0, 10), randint(0, 10)), 1) for i in xrange(100)]))
        sage: matrix_plot(sparse)

    ::

        sage: A=random_matrix(ZZ,100000,density=.00001,sparse=True)
        sage: matrix_plot(A,marker=',')

    As with dense matrices, sparse matrix entries are automatically
    converted to floating point numbers before plotting.  Thus the
    following works::

        sage: b=random_matrix(GF(2),200,sparse=True,density=0.01)
        sage: matrix_plot(b)

    While this returns an error::

        sage: b=random_matrix(CDF,200,sparse=True,density=0.01)
        sage: matrix_plot(b)
        Traceback (most recent call last):
        ...
        ValueError: can not convert entries to floating point numbers

    To plot the absolute value of a complex matrix, use the
    ``apply_map`` method::

        sage: b=random_matrix(CDF,200,sparse=True,density=0.01)
        sage: matrix_plot(b.apply_map(abs))

    Plotting lists of lists also works::

        sage: matrix_plot([[1,3,5,1],[2,4,5,6],[1,3,5,7]])

    As does plotting of NumPy arrays::

        sage: import numpy
        sage: matrix_plot(numpy.random.rand(10, 10))

    TESTS::

        sage: P.<t> = RR[]
        sage: matrix_plot(random_matrix(P, 3, 3))
        Traceback (most recent call last):
        ...
        TypeError: cannot coerce nonconstant polynomial to float

    ::

        sage: matrix_plot([1,2,3])
        Traceback (most recent call last):
        ...
        TypeError: mat must be a Matrix or a two dimensional array

    ::

        sage: matrix_plot([[sin(x), cos(x)], [1, 0]])
        Traceback (most recent call last):
        ...
        ValueError: can not convert entries to floating point numbers
    """
    import numpy as np
    import scipy.sparse as scipysparse
    from sage.plot.plot import Graphics
    from sage.matrix.all import is_Matrix
    from sage.rings.all import RDF
    if is_Matrix(mat):
        sparse = mat.is_sparse()
        if sparse:
            entries = list(mat._dict().items())
            try:
                data = np.asarray([d for _,d in entries], dtype=float)
            except:
                raise ValueError, "can not convert entries to floating point numbers"
            positions = np.asarray([[row for (row,col),_ in entries],
                                    [col for (row,col),_ in entries]], dtype=int)
            mat = scipysparse.coo_matrix((data,positions), shape=(mat.nrows(), mat.ncols()))
        else:
            mat = mat.change_ring(RDF).numpy()
    elif hasattr(mat, 'tocoo'):
        sparse = True
    else:
        sparse = False


    try:
        if sparse:
            xy_data_array = mat
        else:
            xy_data_array = np.asarray(mat, dtype = float)
    except TypeError:
        raise TypeError, "mat must be a Matrix or a two dimensional array"
    except ValueError:
        raise ValueError, "can not convert entries to floating point numbers"

    if len(xy_data_array.shape) < 2:
        raise TypeError, "mat must be a Matrix or a two dimensional array"

    xrange = (0, xy_data_array.shape[1])
    yrange = (0, xy_data_array.shape[0])

    g = Graphics()
    g._set_extra_kwds(Graphics._extract_kwds_for_show(options))
    g.add_primitive(MatrixPlot(xy_data_array, xrange, yrange, options))
    return g
