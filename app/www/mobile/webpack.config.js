const path = require('path');

module.exports = {
  devtool: "source-map",
  entry: './static_src/js/build-babel/Main.js',
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, 'static/js')
  }
};
