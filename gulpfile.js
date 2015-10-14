var gulp = require('gulp'),
    elm = require('gulp-elm');

var app = require('./package.json')
var paths = {
    elm: 'elm',
    js: 'static/js'
    // managepy: app.name + '/manage.py'
}

// compiles elm
gulp.task('elm-init', elm.init);
gulp.task('elm', ['elm-init'], function() {
    return gulp.src(paths.elm+'/*.elm')
        .pipe(elm())
        .pipe(gulp.dest(paths.js))
});

// watch
gulp.task('watch', function() {
    gulp.watch(paths.elm+'/*.elm', ['elm']);
});

// run flask server
gulp.task('flask', function(){
    var process = require('child_process');
    var spawn = process.spawn;
    var PIPE = {stdio: 'inherit'};
    spawn('python', ['views.py'], PIPE);
});

// default task, django runserver with watching
gulp.task('default', ['watch', 'flask'])
