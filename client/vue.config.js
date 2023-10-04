const { defineConfig } = require("@vue/cli-service");
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin;

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
