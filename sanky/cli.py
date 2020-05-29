import structlog
from invoke import Collection, Program

from . import tasks
from . import context
from . import stack
from . import mustack
# structlog.processors.KeyValueRenderer

structlog.configure(
    processors=[
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        # structlog.processors.TimeStamper(),
        # structlog.processors.KeyValueRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,  # or OrderedDict if the runtime's dict is unordered (e.g. Python <3.6)
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

ns = Collection()
for module in [tasks, context, stack, mustack]:
    ns.add_collection(Collection.from_module(module))

program = Program(
    version="0.1.0",
    binary_names=["sk", "sanky"],
    namespace=ns,
)
