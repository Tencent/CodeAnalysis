import { webpackConfig } from '@tencent/micro-frontend-webpack/src/index';
import { merge } from 'webpack-merge';

const { config } = webpackConfig({
  configWebpackOptions: {
    match: '^/t/[^/]+/p/[^/]+/(code-analysis|repos|template|profile|group)',
  },
});

export default merge(config, {
  devServer: {

  },
});
