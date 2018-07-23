"""a module with some custom QtWidget Classes"""

from PyQt5 import QtWidgets, QtCore, QtGui


class MdiArea(QtWidgets.QMdiArea):

    urlsDropped = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(MdiArea, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(MdiArea, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(MdiArea, self).dragMoveEvent(event)

    def dropEvent(self, dropEvent):
        """
        :type dropEvent: QtGui.QDropEvent
        :return:
        """
        mime = dropEvent.mimeData()
        source = dropEvent.source()

        if mime.hasUrls():
            self.urlsDropped.emit(mime)


class TextWarning(QtWidgets.QDialog):
    def __init__(self, text, parent=None):
        super(TextWarning, self).__init__(parent)
        self.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if type(text) in (list, tuple):
            text = "\n".join(text)
        self.textBrowser.setText(text)
        self.setWindowTitle("Warning")


class WarningMsgBox(QtWidgets.QDialog):
    def __init__(self, text, title="Warning", parent=None):
        super(WarningMsgBox, self).__init__(parent)
        self.resize(500, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle(title)

        if type(text) in (list, tuple):
            text = "\n".join(text)
        self.textBrowser.setText(text)


class Spoiler(QtWidgets.QWidget):
    def __init__(self, parent=None, title='', animationDuration=300):
        """
        References:
            # Adapted from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(Spoiler, self).__init__(parent=parent)

        self.animationDuration = 300
        self.toggleAnimation = QtCore.QParallelAnimationGroup()
        self.contentArea = QtWidgets.QScrollArea()
        self.headerLine = QtWidgets.QFrame()
        self.toggleButton = QtWidgets.QToolButton()
        self.mainLayout = QtWidgets.QGridLayout()

        toggleButton = self.toggleButton
        toggleButton.setStyleSheet("QToolButton { border: none; }")
        toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggleButton.setArrowType(QtCore.Qt.RightArrow)
        toggleButton.setText(str(title))
        toggleButton.setCheckable(True)
        toggleButton.setChecked(False)

        headerLine = self.headerLine
        headerLine.setFrameShape(QtWidgets.QFrame.HLine)
        headerLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        headerLine.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.contentArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggleAnimation = self.toggleAnimation
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "minimumHeight"))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "maximumHeight"))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self.contentArea, "maximumHeight"))
        # don't waste space
        mainLayout = self.mainLayout
        mainLayout.setVerticalSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
            direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
            toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)

    def setContentLayout(self, contentLayout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()
        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, heightx=None, widthx=None, parent=None):
        super(LineEdit, self).__init__(parent)
        self.heightx = 1 if heightx is None else heightx
        self.widthx = 1 if widthx is None else widthx
        self.size = super(LineEdit, self).sizeHint()
        self.size.setHeight(self.size.height() * self.heightx)
        self.size.setWidth(self.size.width() * self.widthx)

    def sizeHint(self):
        return self.size


class LineEditNumeric(LineEdit):
    def __init__(self, parent=None):
        super(LineEditNumeric, self).__init__(widthx=0.5, parent=parent)
        self.setValidator(QtGui.QDoubleValidator())

    def value(self):
        return float(self.text())

    def setValue(self, val):
        self.setText("{:0.08g}".format(val))
