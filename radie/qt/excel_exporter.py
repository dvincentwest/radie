from pyqtgraph import PlotItem
from pyqtgraph.exporters.Exporter import Exporter
import pyqtgraph.functions as fn
import win32com.client as win32


def irgb_to_long(r, g, b):
    return 65536 * int(b) + 256 * int(g) + int(r)


def qcolor_to_long(qcolor):
    r = qcolor.red()
    g = qcolor.green()
    b = qcolor.blue()
    return irgb_to_long(r, g, b)


def array_to_list(xs):
    """recursively convert an array to a list."""
    try:
        return [array_to_list(x) for x in xs]
    except TypeError:
        return xs


def set_array_range(worksheet, itop_row, ileft_col, data):
    """insert a 1d or 2d array starting at given location in provided worksheet.

    Args:
        worksheet: win32 Excel object
        itop_row: top row index (zero based)
        ileft_col: left column index (zero based)
        data: numpy array

    Returns:
        win32 Excel Range object
    """
    if len(data.shape) == 1:
        data = data.reshape(data.shape[0], 1)
    ibottom_row = itop_row + data.shape[0] - 1
    iright_col = ileft_col + data.shape[1] - 1
    xlrange = worksheet.Range(
        worksheet.Cells(itop_row + 1, ileft_col + 1),
        worksheet.Cells(ibottom_row + 1, iright_col + 1))

    xlrange.Value = data.tolist()
    return xlrange


def set_cell(worksheet, i, j, val):
    """Set a cell value

    Parameters
    ----------
    worksheet : Worksheet object
    i : integer
        zero based row index
    j : integer
        zero based column index
    val : (unspecified)
        value to set in the excel cell

    Return
    ------
    range : Range object
        range including the cell that was set
    """
    range_str = "%s" % gen_excel_name(i, j)
    xlrange = worksheet.Range(range_str)
    xlrange.Value = val
    return xlrange


def gen_excel_name(row, col):
    """Translate (0,0) into A1.

    Args:
        row: row index (zero-based)
        col: column index (zero-based)

    Returns:
        string representing cell name

    """

    if col < 26:
        col_name = chr(col + ord('A'))
    else:
        col_name = chr(int(col / 26) - 1 + ord('A')) + chr((col % 26) + ord('A'))

    return "%s%s" % (col_name, row + 1)


class VariableContainer:
    pass


class ExcelExporter(Exporter):
    Name = "Excel Chart"
    enums = VariableContainer()
    enums.xlXYScatter = -4169
    enums.xlXYScatterLines = 74
    enums.xlXYScatterLinesNoMarkers = 75
    enums.xlXYScatterSmooth = 72
    enums.xlXYScatterSmoothNoMarkers = 73
    enums.xlLow = -4134
    enums.xlNextToAxis = 4
    enums.xlHigh = -4127
    enums.xlRight = -4152
    enums.msoTrue = -1
    enums.msoElementPrimaryCategoryAxisTitleAdjacentToAxis = 301
    enums.msoElementPrimaryValueAxisTitleRotated = 309
    enums.xlCategory = 1
    enums.xlPrimary = 1
    enums.xlValue = 2
    enums.xlLineStyleNone = -4142

    symbol_map = {'o': 8,
                  's': 1,
                  't': 3,
                  'd': 2,
                  '+': 9}

    def __init__(self, item):
        Exporter.__init__(self, item)
        # Indices to track data columns starting points in data worksheet
        self.data_icol = 0
        self.data_irow = 1
        self.chart = None
        self.worksheet = None
        self.workbook = None

    def parameters(self):
        return None

    def export(self, fileName=None):
        """
        If *fileName* is None, pop-up a file dialog.
        If *toBytes* is True, return a bytes object rather than writing to file.
        If *copy* is True, export to the copy buffer rather than writing to file.
        """
        if not isinstance(self.item, PlotItem):
            raise Exception("Matplotlib export currently only works with plot items")

        # acquire application object, which may start application
        application = win32.gencache.EnsureDispatch("Excel.Application")
        try:
            version = float(application.Version)
        except ValueError:
            version = 12.0  # defaults to Excel 2007
        # create new file ('Workbook' in Excel-vocabulary)
        self.workbook = application.Workbooks.Add()
        # store default worksheet object so we can delete it later
        default_worksheet = self.workbook.Worksheets(1)

        # build new chart (on separate page in workbook)
        self.chart = self.workbook.Charts.Add()

        self.chart.ChartType = self.enums.xlXYScatterLinesNoMarkers
        self.chart.Name = "Plot"
        if version >= 12:
            self.chart.ApplyLayout(1)
            self.chart.ChartArea.Format.Line.Visible = False  # not sure if this is needed
            self.chart.ChartArea.Border.LineStyle = self.enums.xlLineStyleNone
        else:
            self.chart.PlotArea.Interior.Color = 16777215
            self.chart.HasTitle = True
            self.chart.Axes(self.enums.xlCategory, self.enums.xlPrimary).HasTitle = True
            self.chart.Axes(self.enums.xlCategory, self.enums.xlPrimary).AxisTitle.Characters.Text = "xaxis"
            self.chart.Axes(self.enums.xlValue, self.enums.xlPrimary).HasTitle = True
            self.chart.Axes(self.enums.xlValue, self.enums.xlPrimary).AxisTitle.Characters.Text = "yaxis"
            self.chart.ChartArea.Border.LineStyle = self.enums.xlLineStyleNone

        # create data worksheet
        self.worksheet = self.workbook.Worksheets.Add()
        self.worksheet.Name = "Plot data"

        for item in self.item.curves:
            self.add_curve_to_chart(item)

        # setup axes
        x_axis = self.chart.Axes().Item(self.enums.xlCategory, self.enums.xlPrimary)
        y_axis = self.chart.Axes().Item(self.enums.xlValue, self.enums.xlPrimary)
        x_axis.HasMajorGridlines = True
        y_axis.HasMajorGridlines = True

        # setup axis labels
        x_label = self.item.axes['bottom']['item'].label.toPlainText()
        y_label = self.item.axes['left']['item'].label.toPlainText()
        x_axis.AxisTitle.Text = x_label if x_label else "x axis"
        y_axis.AxisTitle.Text = y_label if y_label else "y axis"
        x_axis.AxisTitle.Font.Size = 20
        y_axis.AxisTitle.Font.Size = 20
        x_axis.TickLabels.Font.Size = 18
        y_axis.TickLabels.Font.Size = 18

        # Format and place legend
        self.chart.Legend.Font.Size = 18
        self.chart.Legend.IncludeInLayout = False
        self.chart.Legend.Position = self.enums.xlRight
        self.chart.Legend.Format.Fill.Visible = self.enums.msoTrue
        self.chart.Legend.Format.Fill.ForeColor.RGB = irgb_to_long(255, 255, 255)
        self.chart.Legend.Format.Fill.Transparency = 0
        self.chart.Legend.Format.Line.Visible = self.enums.msoTrue
        self.chart.Legend.Format.Line.ForeColor.RGB = irgb_to_long(115, 115, 115)
        self.chart.Legend.Format.Line.Transparency = 0

        # Set the labels position for xaxis
        x_axis.TickLabelPosition = self.enums.xlLow

        if self.item.titleLabel.text:
            self.chart.ChartTitle.Text = self.item.titleLabel.text
        else:
            self.chart.ChartTitle.Delete()

        # Set scale
        scale = self.item.viewRange()

        # if False:
        #     x_axis.MinimumScale = scale[0][0]
        #     x_axis.MaximumScale = scale[0][1]
        #     y_axis.MinimumScale = scale[1][0]
        #     y_axis.MaximumScale = scale[1][1]

        # remove default worksheet
        default_worksheet.Delete()

        # make stuff visible now.
        self.chart.Activate()
        application.Visible = True

    def add_xy_to_worksheet(self, x, y, x_header=None, y_header=None):
        set_cell(self.worksheet, 0, self.data_icol, x_header)
        set_cell(self.worksheet, 0, self.data_icol + 1, y_header)
        x_column = set_array_range(self.worksheet, self.data_irow, self.data_icol, x)
        y_column = set_array_range(self.worksheet, self.data_irow, self.data_icol + 1, y)
        self.data_icol += 2
        return x_column, y_column

    def add_curve_to_chart(self, item):
        """
        Adds the item to teh chart and corresponding data to the worksheet

        Parameters
        ----------
        item: pyqtgraph CurveItem

        Returns
        -------

        """

        # Get data
        x, y = item.getData()
        # Get headers
        name = None
        if hasattr(item, 'implements') and item.implements('plotData') and item.name() is not None:
            name = item.name()
            x_header = "{}_x".format(name)
            y_header = "{}_y".format(name)
        else:
            x_header = "{:04d}_x".format(int(self.data_icol / 2))
            y_header = "{:04d}_x".format(int(self.data_icol / 2))

        # Write to data worksheet
        x_column, y_column = self.add_xy_to_worksheet(x, y, x_header=x_header, y_header=y_header)

        # Add series to Excel Chart
        series = self.chart.SeriesCollection().NewSeries()
        series.XValues = x_column
        series.Values = y_column
        if name is not None:
            series.Name = name

        pen = item.opts["pen"]
        symbol = item.opts["symbol"]

        if pen is not None:
            line_color = qcolor_to_long(fn.mkPen(pen).color())
            series.Border.Color = line_color
            series.Format.Line.ForeColor.RGB = line_color
            series.Format.Fill.BackColor.RGB = line_color

        if symbol is not None:
            series.MarkerStyle = self.symbol_map.get(symbol, 1)
            series.MarkerSize = item.opts["symbolSize"]
            series.MarkerBackgroundColor = qcolor_to_long(fn.mkPen(item.opts["symbolPen"]).color())
            series.MarkerForegroundColor = qcolor_to_long(fn.mkBrush(item.opts["symbolBrush"]).color())

        if name is None:
            last_index = self.chart.Legend.LegendEntries().Count
            self.chart.Legend.LegendEntries(last_index).Delete()


ExcelExporter.register()
