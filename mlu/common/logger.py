'''
logger.py

Module containing functionality for configuring and retrieving logger instances, which can be used
as a better alternative to print statements for debugging, info, error, etc purposes.

'''

import logging
import inspect

import mlu.common.file
from mlu.common.settings import MLUSettings

global _mluLogger

class SharedLoggerNotInitialized(Exception):
    '''
    Custom exception class for the type of exception thrown by getMLULogger() if the MLU shared
    logger has not yet been initialized.
    '''
    pass

def getMLULogger():
    '''
    Returns the current MLU logger instance so it can be used to define log messages in a module/
    script's code. 
    
    The shared MLU logger MUST first be initialized by calling logger.initMLULogger() from the 
    main script before this function is used. If it is not, a SharedLoggerNotInitialized exception is thrown.
    '''

    global _mluLogger
    if (_mluLogger is None):
        raise SharedLoggerNotInitialized("Python MLU project shared logger instance is not yet configured/initialized: you must call 'mlu.common.logger.initMLULogger()' first from the main script to setup the shared logger that all modules will use")

    else:
        return _mluLogger


def initMLULogger(logFilename=''):
    '''
    Creates/initializes and configures a the MLU project shared logger instance, which will be used 
    as the go-to logger instance for all functions and modules to use when defining
    log messages in the code.

    The logger is configured by default to send all log statements to the console and to a log file, 
    located in the project root folder, with the same name as the module python file for which this logger is for.

    Details - this function creates the following default configuration for the shared logger:
    - the logger will allow all messages to be passed to the handlers (debug or higher)
    - the logger has two handlers, which define how the messages should be output, which ones to output, etc:
        - a file handler, which writes all messages (debug or higher) to a log file of the given name:
            the log file will be placed in the BFT logs dir
        - a stream (console output) handler, which outputs all messages (debug or higher) to the console/stdin

    Params:
        - logFilename: Name of the log file to which the file handler will output the log messages.
            By default, uses the name of the calling script + the .log file extension.
    '''

    global _mluLogger

    # If no log filename was given,
    # get the name of the module/file that called this function so we can use it to be the log file name
    if (not logFilename):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        callerModuleFilename = mlu.common.file.GetFilename(module.__file__)

        logFilename = "{}.log".format(callerModuleFilename)

    # ask the Python logging module for a new logger, and give it the name of our new MLU logger
    _mluLogger = logging.getLogger('mluLogger')

    # allow all messages of all levels to be passed to the handlers: the handlers will have their
    # own levels set, where they can individually decide which messages to print for a more granular
    # logging control
    _mluLogger.setLevel(logging.DEBUG) 

    # create a file handler which logs all messages by default by saving them to a static log file
    # (given the filename), which is used by all the other Python modules to write log statements into: 
    # this is a global/"shared" log output file instead of having them seperated by module into various log files
    logFilepath = mlu.common.file.JoinPaths(MLUSettings.logDir, logFilename)
    fh = logging.FileHandler(logFilepath, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    # create console output handler which logs all messages (debug up through critical)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - [%(filename)s,  %(funcName)s()] - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    _mluLogger.addHandler(fh)
    _mluLogger.addHandler(ch)


def setMLULoggerConsoleOutputLogLevel(logLevel):
    '''
    Modifies the configuration of the shared logger by setting the minimum level of importance (log
    level) that log messages need to have in order to be logged to the console.
    
    NOTE: this only changes the log level for the console output handler: the log level for the file
    output handler will not be changed (debug and higher by default).

    This function is useful if the log level needs to be changed later in the script code: for instance, 
    if the user wants to change it interactively so that the console is not flooded with log messages.

    Params:
        - logLevel: one of the following log level string values: debug, info, warning, error
    
    Example: 
        setSharedLoggerConsoleOutputLogLevel("info")
    '''

    # Get the actual log level from the logging class, given the parameter
    if (logLevel.lower() == "debug"):
        level = logging.DEBUG
    elif (logLevel.lower() == "info"):
        level = logging.INFO 
    elif (logLevel.lower() == "warning"):
        level = logging.WARNING
    elif (logLevel.lower() == "error"):
        level = logging.ERROR
    else:
        raise TypeError("Invalid value given for parameter 'logLevel': it must be one of the following values: debug, info, error")

    # set the log level for the console handler only
    # get the mlu logger first, instead of using the global _mluLogger, to check that the logger
    # exists first
    mluLogger = getMLULogger()
    for handler in mluLogger.handlers:
        if (handler.__class__.__name__ == 'StreamHandler'):
            handler.setLevel(level)