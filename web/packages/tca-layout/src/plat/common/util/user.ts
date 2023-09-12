import { get } from 'lodash';

// 项目内
// import { LOGIN_SERVER_API } from '../api';

/** 用户工具管理 */
export class UserManager {
  /**
   * 获取用户昵称
   * @param user 用户信息
   * @returns 用户昵称
   */
  static getNickName(user: any) {
    if (typeof user === 'string') return user;
    return (get(user, 'nickname') || get(user, 'username') || '') as string;
  }

  /**
   * 获取用户UID
   * @param user 用户信息
   * @returns 用户UID
   */
  static getUID(user: any) {
    const uid = get(user, 'uid') || get(user, 'username');
    if (uid) {
      return uid as string;
    }
    throw new Error('user 解析 uid failed');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  static getUserAvatarURL(_: any) {
    return '';
  }
}
