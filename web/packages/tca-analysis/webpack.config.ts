import { webpackConfig } from '@tencent/micro-frontend-webpack/src/index';
import { merge } from 'webpack-merge';

const { config } = webpackConfig({
  configWebpackOptions: {
    match: '^/t/[^/]+/p/[^/]+/(code-analysis|repos|template|profile|group)|^/t/[^/]+/template',
  },
  envConfig: {
    envs: {
      DISABLE_MICRO_LAYOUT: process.env.DISABLE_MICRO_LAYOUT,
      // route listener 发送 postmsg 的目标源
      ROUTE_LISTENER_TARGET_ORIGIN: process.env.ROUTE_LISTENER_ORIGIN || process.env.ROUTE_LISTENER_TARGET_ORIGIN,
      // route listener 接收 postmsg 的发送源
      ROUTE_LISTENER_EVENT_ORIGIN: process.env.ROUTE_LISTENER_ORIGIN || process.env.ROUTE_LISTENER_EVENT_ORIGIN,
      // route listener 消息数据类型
      ROUTE_LISTENER_DATA_TYPE: process.env.ROUTE_LISTENER_DATA_TYPE,
      // 开启代码分析前缀路径精确匹配
      ENABLE_ANALYSIS_PREFIX_EXACT_MATCH: process.env.ENABLE_ANALYSIS_PREFIX_EXACT_MATCH,
    },
    runtimeEnvs: {
      // route listener 发送 postmsg 的目标源
      ROUTE_LISTENER_TARGET_ORIGIN: '__ROUTE_LISTENER_TARGET_ORIGIN__',
      // route listener 接收 postmsg 的发送源
      ROUTE_LISTENER_EVENT_ORIGIN: '__ROUTE_LISTENER_EVENT_ORIGIN__',
      // route listener 消息数据类型
      ROUTE_LISTENER_DATA_TYPE: '__ROUTE_LISTENER_DATA_TYPE__',
    },
  },
});

export default merge(config, {
  devServer: {

  },
});
