import { webpackConfig, Envs } from '@tencent/micro-frontend-webpack/src/index';
import { merge } from 'webpack-merge';

/**
 * 配置自定义环境变量
 * @returns 返回envs, runtimeEnvs
 */
const customEnvConfig = () => {
  const envs: Envs = {
    MICRO_VERSION_INTERVAL: process.env.MICRO_VERSION_INTERVAL,
    MICRO_VERSION_ENABLED: process.env.MICRO_VERSION_ENABLED,
    MICRO_FRONTEND_SETTING_API: process.env.MICRO_FRONTEND_SETTING_API,
    MICRO_FRONTEND_API: process.env.MICRO_FRONTEND_API,
  };
  const runtimeKeys = [
    'MICRO_FRONTEND_API',
    'MICRO_FRONTEND_SETTING_API',
  ];
  const runtimeEnvs: Envs = {};

  runtimeKeys.forEach((key) => {
    runtimeEnvs[key] = `__${key}__`;
  });
  return { envs, runtimeEnvs };
};

const { config } = webpackConfig({
  configWebpackOptions: {
    enable: 'false',
  },
  envConfig: customEnvConfig(),
});

export default merge(config, {
  devServer: {
    port: 4000,
    proxy: {
      '/static': {
        ws: false,
        target: 'https://tca.tencent.com',
        changeOrigin: true,
      },
      '/server': {
        ws: false,
        target: 'https://tca.tencent.com',
        changeOrigin: true,
      },
    },
  },
});
