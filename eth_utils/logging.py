import contextlib
import logging
from typing import Any, Iterator, Type, TypeVar

from .toolz import assoc

DEBUG2_LEVEL_NUM = 8


class ExtendedDebugLogger(logging.Logger):
    """
    Logging class that can be used for lower level debug logging.
    """

    def debug2(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.log(DEBUG2_LEVEL_NUM, message, *args, **kwargs)


def setup_DEBUG2_logging() -> None:
    """
    Installs the `DEBUG2` level logging levels to the main logging module.
    """
    if not hasattr(logging, "DEBUG2"):
        logging.addLevelName(DEBUG2_LEVEL_NUM, "DEBUG2")
        setattr(logging, "DEBUG2", DEBUG2_LEVEL_NUM)  # typing: ignore


@contextlib.contextmanager
def _use_logger_class(logger_cls: Type[logging.Logger]) -> Iterator:
    original_logger_cls = logging.getLoggerClass()
    logging.setLoggerClass(logger_cls)
    try:
        yield
    finally:
        logging.setLoggerClass(original_logger_cls)


THasLoggerMeta = TypeVar("THasLoggerMeta", bound="HasLoggerMeta")


class HasLoggerMeta(type):
    """
    Metaclass which using the `__qualname__` to assign a logger instance to the
    class who's name corresponds to the import path for the class.
    """

    logger_class = logging.Logger

    def __new__(mcls, name, bases, namespace):
        if "logger" in namespace:
            # If a logger was explicitely declared we shouldn't do anything to
            # replace it.
            return super().__new__(mcls, name, bases, namespace)
        if "__qualname__" not in namespace:
            raise AttributeError("Missing __qualname__")

        with _use_logger_class(mcls.logger_class):
            logger = logging.getLogger(namespace["__qualname__"])

        return super().__new__(mcls, name, bases, assoc(namespace, "logger", logger))

    @classmethod
    def replace_logger_class(
        mcls: Type[THasLoggerMeta], value: Type[logging.Logger]
    ) -> Type[THasLoggerMeta]:
        return type(mcls.__name__, (mcls,), {"logger_class": value})

    @classmethod
    def meta_compat(
        mcls: Type[THasLoggerMeta], other: Type[type]
    ) -> Type[THasLoggerMeta]:
        return type(mcls.__name__, (mcls, other), {})


class _BaseHasLogger(metaclass=HasLoggerMeta):
    # This class exists to a allow us to define the type of the logger.  Once
    # python3.5 is deprecated this can be removed in favor of a simple type
    # annotation on the main class.
    logger = logging.Logger("")  # type: logging.Logger


class HasLogger(_BaseHasLogger):
    pass


HasExtendedDebugLoggerMeta = HasLoggerMeta.replace_logger_class(ExtendedDebugLogger)


class _BaseHasExtendedDebugLogger(metaclass=HasExtendedDebugLoggerMeta):  # type: ignore
    # This class exists to a allow us to define the type of the logger.  Once
    # python3.5 is deprecated this can be removed in favor of a simple type
    # annotation on the main class.
    logger = ExtendedDebugLogger("")  # type: ExtendedDebugLogger


class HasExtendedDebugLogger(_BaseHasExtendedDebugLogger):
    pass
