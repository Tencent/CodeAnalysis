/**
 * utils - time 工具库
 */

import Moment, { MomentInput } from 'moment';

/**
 * 格式化time为日期字符串
 * @param time 时间
 * @param format 格式化字符串
 * @returns 格式化日期字符串
 */
export const formatDate = (time: MomentInput, format = 'YYYY-MM-DD') => (time ? Moment(time).format(format) : null);

/**
 * 格式化time为时间字符串
 * @param time 时间
 * @param format 格式化字符串
 * @returns 格式化时间字符串
 */
export const formatDateTime = (time: MomentInput, format = 'YYYY-MM-DD HH:mm:ss') => formatDate(time, format);

/**
 * 根据秒转化为H 时 m 分 s 秒格式
 * @param sec 秒
 * @returns H 时 m 分 s 秒
 */
export const secToHMS = (sec: number) => {
  const time = Moment.duration(sec, 'seconds');
  const h = time.hours();
  const m = time.minutes();
  const s = time.seconds();
  const format = `${h ? 'H 时 ' : ''}${m ? 'm 分 ' : ''}s 秒`;
  return Moment({ h, m, s }).format(format);
};
