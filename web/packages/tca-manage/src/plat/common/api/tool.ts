import { MAIN_SERVER_API, get } from './common';

export class ToolAPI {
  static getTools = (params?: any) => get(`${MAIN_SERVER_API}/checktools/`, params);
}
