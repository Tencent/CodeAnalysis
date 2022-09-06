/**
 * utils 工具类
 */
import { message } from 'coding-oa-uikit';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import { UserManager } from '@plat/util';

export const { getNickName, getUID, getUserAvatarURL } = UserManager;

export function logout(content: string) {
  message.info(content);
  localStorage.removeItem('userInfo');
  localStorage.removeItem('associate_userinfo');
  localStorage.removeItem('accessToken');
  const timer = setTimeout(() => {
    window.location.href = '/';
    clearTimeout(timer);
  }, 300);
}

/**
 * 是否开启后台管理版本
 */
export const isEnableManage = () => getMetaContent('ENABLE_MANAGE', process.env.ENABLE_MANAGE) === 'TRUE';
