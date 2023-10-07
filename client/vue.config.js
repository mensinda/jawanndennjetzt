const { defineConfig } = require("@vue/cli-service");
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin;
const webpack = require("webpack");
const dotenv = require("dotenv");
const dotenvExpand = require("dotenv-expand");

const dotenvEnv = dotenv.config({ path: "../.env" })
dotenvExpand.expand(dotenvEnv);

function toBool(raw, def) {
  if (raw == null) {
    return def;
  }
  return raw == "1" || raw == "true";
}

subPath = process.env.JWDJ_SUBPATH || "/";

module.exports = defineConfig({
  publicPath: subPath,
  productionSourceMap: toBool(process.env.DEBUG, true),
  transpileDependencies: true,

  configureWebpack: {
    plugins: [
      new BundleAnalyzerPlugin({
        analyzerMode:
          toBool(process.env.DEBUG, true) && !toBool(process.env.DISABLE_ANALYZER, false) ? "static" : "disabled",
        openAnalyzer: false,
      }),
      new webpack.DefinePlugin({
        JWDJ_OPEN_GRAPH_IMAGE: JSON.stringify(process.env.JWDJ_OPEN_GRAPH_IMAGE),
        JWDJ_FAVICON: JSON.stringify(process.env.JWDJ_FAVICON),
      }),
    ],
    devServer: {
      historyApiFallback: {
        rewrites: [{ from: /.*/, to: subPath }],
      },
    },
  },

  devServer: {
    host: "127.0.0.1",
    port: 8080,

    proxy: {
      [`^${subPath}api/`]: {
        target: "http://127.0.0.1:8000/",
        ws: true,
        changeOrigin: false,
      },
    },
  },
});
