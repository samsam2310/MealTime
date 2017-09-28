const path = require('path');

module.exports = {
  node: {
    __dirname: true
  },
  entry: ['./frontend/main.jsx'],
  output: {
    path: path.resolve(__dirname, 'public/bundle'),
    filename: 'index.js'
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        include: path.resolve(__dirname, 'frontend'),
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'es2016', 'react']
        }
      }
    ]
  }
};
