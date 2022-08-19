import { toNumber } from 'lodash';
import { MAIN_SERVER_API, get, post } from '@plat/api';
import { ResultEnum } from '@src/modules/jobs/constants';

/** 格式化筛选项中的result，result_code <= 99 表示通过，result_code >= 99 表示异常 */
const formatJobResultFilter = (result?: string) => {
  if (result) {
    if (toNumber(result) === ResultEnum.SUCCESS) {
      return { result_code_lte: 99 };
    }
    return { result_code_gte: 99 };
  }
  return {};
};

/** job请求链接 */
const JOB_API_URL = `${MAIN_SERVER_API}/jobs`;

export const jobAPI = {
  /** job列表 */
  get: (params?: any) => {
    // result_code <= 99 表示通过，result_code >= 99 表示异常
    const data = { ...params, ...formatJobResultFilter(params.result) };
    return get(`${JOB_API_URL}/`, data);
  },
  /** 取消job */
  cancel: (jobId: number|string, data: any) => post(`${JOB_API_URL}/${jobId}/cancel/`, data),
  /** job 归档列表 */
  getArchived: (params?: any) => {
    const data = { ...params, ...formatJobResultFilter(params.result) };
    return get(`${JOB_API_URL}/archive/`, data);
  },
};
