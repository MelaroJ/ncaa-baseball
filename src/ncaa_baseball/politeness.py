import random
import time

from ncaa_baseball.config import Config


def sleep_before_request(config: Config) -> None:
    delay = random.uniform(
        config.min_delay_seconds,
        config.max_delay_seconds,
    )

    time.sleep(delay)
