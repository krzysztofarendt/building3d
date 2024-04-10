import uuid

import building3d.logger


def random_id() -> str:
    return str(uuid.uuid4())
