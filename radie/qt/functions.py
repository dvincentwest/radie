import ctypes
import os
import platform
import sys
import traceback
from os import path

from PyQt5 import QtWidgets, QtGui

from .classes import TextWarning, WarningMsgBox
from . import cfg

last_path = os.path.normpath(cfg.user_path)


def instantiate_app(sys_argv=[]):
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys_argv)
    cfg.set_dpi_scaling()
    return app


def excepthook(*args):
    return sys.__excepthook__(*args)


def reset_excepthook():
    sys.excepthook = excepthook


def popup_excepthook(type, value, tback):
    WarningMsgBox(traceback.format_exception(type, value, tback), "Uncaught Exception").exec_()


def set_popup_exceptions():
    sys.excepthook = popup_excepthook


def error_popup(error):
    if not type(error) is str:
        etype, value, tb = sys.exc_info()
        error = "\n".join(traceback.format_exception(etype, value, tb))
    WarningMsgBox(error).exec_()


def text_based_error(text):
    warning = TextWarning(text)
    warning.exec_()


def warnMissingFeature():
    msg = "Coming soon..."
    QtWidgets.QMessageBox.warning(None, "Feature Missing", msg, QtWidgets.QMessageBox.Ok)


def getOpenFileName_Global(caption, filter, start_path=None, **kwargs):
    global last_path
    if start_path is None:
        start_path = last_path
    fname = str(QtWidgets.QFileDialog.getOpenFileName(None, caption, start_path, filter, **kwargs)[0])
    if fname in ("", None):
        return ""
    last_path = path.dirname(fname)
    return fname


def getOpenFileNames_Global(caption, filter, start_path=None, **kwargs):
    global last_path
    if start_path is None:
        start_path = last_path
    fnames = QtWidgets.QFileDialog.getOpenFileNames(None, caption, start_path, filter, **kwargs)[0]
    fnames = [str(fname) for fname in fnames]
    if fnames in ("", None, []):
        return []
    last_path = path.dirname(fnames[0])
    return fnames


def getSaveFileName_Global(caption, filter, start_path=None, **kwargs):
    global last_path
    if start_path is None:
        start_path = last_path
    fname = str(QtWidgets.QFileDialog.getSaveFileName(None, caption, start_path, filter, **kwargs)[0])
    if fname in ("", None):
        return ""
    last_path = path.dirname(fname)
    return fname


def getDirName_Global(caption=None, start_path=None, **kwargs):
    global last_path
    if start_path is None:
        start_path = last_path
    dirname = str(QtWidgets.QFileDialog.getExistingDirectory(None, caption, start_path, **kwargs))
    if dirname in ("", None):
        return ""
    last_path = path.dirname(dirname)
    return dirname


def set_process_id(appid=None):
    """
    in windows, setting this parameter allows all instances to be grouped under the same taskbar icon, and allows
    us to set an icon that is different from whatever the python executable is using.
    :param appid: str, unicode
    :return:
    """
    if appid and type(appid) is str and platform.system() == "Windows":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)


def setup_style(style=cfg.preferred_style):
    """

    Parameters
    ----------
    style : str
        the Qt Style keyword matching the system style, default is fusion
    """
    available_styles = QtWidgets.QStyleFactory.keys()
    if style:
        if "QT_STYLE_OVERRIDE" in os.environ.keys():
            os.environ.pop("QT_STYLE_OVERRIDE")

        if style in available_styles:
            QtWidgets.QApplication.setStyle(style)
        else:
            for s in cfg.preferred_styles:
                if s in available_styles:
                    QtWidgets.QApplication.setStyle(s)

    elif platform.system() != "Windows" and os.environ["QT_API"] == "pyqt5":
        if "QT_STYLE_OVERRIDE" in os.environ.keys():
            os.environ.pop("QT_STYLE_OVERRIDE")
        if len(available_styles) == 2:
            # available styles are Windows, and Fusion
            # qt5-style-plugins are not installed, take action:
            for s in cfg.preferred_styles:
                if s in available_styles:
                    QtWidgets.QApplication.setStyle(s)


def icon(filename):
    """
    a convience function to get QIcons from the radie/qt/resources/icons directory

    Parameters
    ----------
    filename : str

    Returns
    -------
    QtGui.QIcon
    """
    return QtGui.QIcon(os.path.join(cfg.icon_path, filename))
