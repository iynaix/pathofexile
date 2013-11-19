from fabric.api import local, task


def heroku(cmd):
    local("heroku %s --app=pathofexilexy" % cmd)


@task
def deploy():
    #do the deploy
    local("git push heroku master")

    heroku("pg:reset")
    heroku("pg:push pathofexile")
