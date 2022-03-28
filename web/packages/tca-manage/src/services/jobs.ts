import { get } from './index';
import { MAIN_SERVER_API } from './common';

/**
 * 获取分析记录列表
 * @param params 筛选参数
 */
export const getJobs = (params: any = null) => get(`${MAIN_SERVER_API}/jobs/`, params);
