const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));

function compilarSass() {
  return gulp.src('scss/main.scss')
    .pipe(sass({ outputStyle: 'expanded' }).on('error', sass.logError))
    .pipe(gulp.dest('static'));
}

function watchSass() {
  gulp.watch('scss/**/*.scss', compilarSass);
}

exports.sass = compilarSass;
exports.watch = watchSass;
exports.default = gulp.series(compilarSass, watchSass);