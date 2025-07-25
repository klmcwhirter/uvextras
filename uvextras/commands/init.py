import logging

from uvextras.context import AppContext


def cmd(ctx: AppContext) -> None:
    logging.info('starting...')
    _ = ctx
    logging.info('done.')
