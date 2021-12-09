const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    mode: 'development',
    devtool: "cheap-module-eval-source-map",
    entry: {
        app: "./src/index",
        vendor: [
            "classnames", "history", "immutable", "lodash", "moment",
            "nprogress", "react", "react-bootstrap", "react-dom", "react-redux",
            "react-router", "redux", "redux-logger", "redux-thunk",
            "reselect", "superagent"
        ],
    },
    resolve: {
        modules: ["src", "node_modules"]
    },
    output: {
            filename: 'bundle.js',
            path: path.join(__dirname, 'build/js')
    },
    optimization: {
            splitChunks: {
            name: 'vendor',
            chunks: 'all',
        }
    },
    module: {
        rules: [
        {
            test: /\.m?(js|jsx)$/,
            include: path.join(__dirname, "src"),
            use: {
            loader: 'babel-loader',
            options: {
                presets: ["@babel/preset-env", "@babel/preset-react"]
            }
            }
        },
        {
            test: require.resolve("immutable"),
            loader: "expose?immutable"
        },
        {
            test: /\.less$/,
            loader: MiniCssExtractPlugin.loader
        },
        {
            test: /\.(jpg|ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            loader: "file?name=[path][name].[ext]?[hash]&context=./node_modules"
        },
        {
            test: /\.(sass|less|css)$/,
            loaders: ['style-loader', 'css-loader', 'postcss-loader']
        }
        ]
    }  
};