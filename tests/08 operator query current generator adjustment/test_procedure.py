from data_chan.instruments.fermiumlabs_labtrek_jv import hall_effect_apparatus as ht
import data_chan
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from dialog import Dialog


def operator_query_instructions(TESTNAME):
    d = Dialog(dialog="dialog")

    d.set_background_title("Testing: " + TESTNAME)
    testquery = d.msgbox("Alimenta il minuscolo arduino della scheda 4ohm con la USB. Conferma se fa click-click-click", width=60)
    testquery = d.msgbox("Tara il generatore affinche' ci sia minima variazione della corrente", width=60)

    # The user pressed cancel
    if testquery is not "ok":
        d.msgbox("Test Interrotto")
        return False
    else: #the user pressed ok
        return True



def test_procedure(TESTNAME,testDict):
    d = Dialog(dialog="dialog")

    d.set_background_title("Testing: " + TESTNAME)

    if not operator_query_instructions(TESTNAME):
        return False


    try:
        ht.init()
        # Acquire the Hall Effect Apparatus
        scan = ht.acquire(0x16d0,0x0c9b)
    except Exception:
        d.msgbox("Data-chan initialization failed")
        return False




    # Start Measuring
    ht.enable(scan)
    ht.set_channel_gain(scan, 3, 5)

    # Set CC gen
    ht.set_current_fixed(scan, 0.3)

    win = pg.GraphicsWindow()
    win.setWindowTitle(TESTNAME)
    meas = {"ch3":{}}
    meas["ch3"]["name"] = "V on CC Shunt"
    for key in meas:
        meas[key]["plotobj"] = win.addPlot(title=meas[key]["name"])
        meas[key]["data"] = [0]*100
        meas[key]["curveobj"] = meas[key]["plotobj"].plot(meas[key]["data"])

    def update():
        popped_meas = ht.pop_measure(scan)
        if popped_meas is not None:
            for key in meas:
                meas[key]["data"][:-1] = meas[key]["data"][1:]
                meas[key]["data"][-1] = popped_meas[key]
                meas[key]["curveobj"].setData(meas[key]["data"])

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)

    ## Start Qt event loop unless running in interactive mode or using pyside.
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    ht.disconnect_device(scan)
    ht.deinit()

    return True
