import { get, post, put } from './index';
import { MAIN_SERVER_API } from './common';

export const getUsers = (params: any = null) => get(`${MAIN_SERVER_API}/authen/allusers/`, params);

export const postUsers = (params: any = null) => post(`${MAIN_SERVER_API}/authen/allusers/`, params);

export const getUser = (username: string) => get(`${MAIN_SERVER_API}/authen/allusers/${username}/`);

export const putUser = (username: string, params: any) => put(`${MAIN_SERVER_API}/authen/allusers/${username}/`, params);
