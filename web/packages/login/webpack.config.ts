import { webpackConfig } from '@tencent/micro-frontend-webpack/src/index';
import { merge } from 'webpack-merge';

const { config } = webpackConfig({
  configWebpackOptions: {
    match: '^/login',
  },
});

export default merge(config, {
  devServer: {

  },
});
