from fabric.api import local, task


def heroku(cmd):
    local("heroku %s --app=pathofexilexy" % cmd)


@task
def deploy(full=0):
    """does a deploy to heroku"""
    local("git push heroku master")
    if full:
        fetch()
        update()


@task
def fetch():
    """updates the inventory data from pathofexile"""
    local("python fetch.py")


@task
def update():
    """updates the remote postgres database"""

    heroku("pg:reset HEROKU_POSTGRESQL_MAROON --confirm pathofexilexy")
    heroku("pg:push pathofexile HEROKU_POSTGRESQL_MAROON")
