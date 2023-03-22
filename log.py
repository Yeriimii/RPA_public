import logging
import os

def get_logger(name=None):
    if not os.path.exists("log"):
        os.mkdir("log")
    # logger instance
    logger = logging.getLogger(name)
    # log formatter
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(message)s')
    # handler (stream, file)
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("./log/log.log")
    # logger instance에 formatter 설정
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # logger instance에 handler 설정
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # logger level set
    logger.setLevel(level="DEBUG")

    return logger
