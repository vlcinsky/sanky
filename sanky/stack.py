from invoke import task


@task
def deploy(c):
    """deploy `_deploy/<stack>` defined by cwd (use it for update too)
    """
    pass


@task
def rm(c):
    """remove `_deploy/<stack>` defined by cwd"""
    pass
