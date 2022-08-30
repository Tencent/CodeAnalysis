/**
 * 工具依赖
 */

import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import cn from 'classnames';
import qs from 'qs';
import { omitBy, toNumber, isString, get } from 'lodash';
import { Table, Button, Tag } from 'coding-oa-uikit';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';
import { useURLSearch, useURLParams } from '@tencent/micro-frontend-shared/hooks';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';
import Search from '@tencent/micro-frontend-shared/component/search';

import { NAMESPACE, UserState } from '@src/store/user';
import { getToolLibs } from '@src/services/tools';
import { DEFAULT_PAGER, LIB_TYPE, LibTypeEnum, LIB_ENV } from '@src/constant';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';

import { TOOLLIB_FILTER_FIELDS as filterFields, TOOLLIB_SEARCH_FIELDS } from './constants';
import CreateToollibs from './create-libs';
import style from './style.scss';

const { Column } = Table;

export const ToolLibs = () => {
  const history = useHistory();
  const { orgSid }: any = useParams();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const [modalData, setModalData] = useState({
    visible: false,
    libId: null,
  });
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);

  const query = useURLSearch();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const { searchParams } = useURLParams(filterFields);
  const isAdmin = useSelector((state: any) => state.APP)?.isOrgAdminUser ?? false;
  const isSuperuser = userinfo?.is_superuser;  // 是否为超级管理员
  const editable = isAdmin || isSuperuser;  // 编辑权限

  useEffect(() => {
    getListData();
  }, []);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => isString(item) && !item),
    };

    setLoading(true);
    getToolLibs(orgSid, params)
      .then((response: any) => {
        history.replace(`${location.pathname}?${qs.stringify(params)}`);
        setCount(response.count);
        setList(response.results);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  return (
    <div className={style.toollibs}>
      <div className={style.header}>
        <span className={style.title}>工具依赖</span>
      </div>
      <Search
        loading={loading}
        searchParams={searchParams}
        route={false}
        style={{ padding: '1px 24px' }}
        fields={TOOLLIB_SEARCH_FIELDS}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
        extraContent=      {
          editable && (
            <Button
              type='primary'
              onClick={() => setModalData({
                visible: true,
                libId: null,
              })}
            >
              添加依赖
            </Button>
          )
        }
      />
      <Table
        rowKey={(item: any) => item.id}
        loading={loading}
        dataSource={list}
        className={style.libsTable}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
          onChange: onChangePageSize,
        }}
      >
        <Column
          title='依赖名称'
          dataIndex='name'
        />
        <Column
          title='环境变量'
          dataIndex='envs'
          render={(envs: any) => envs && (
            // todo: 没有按顺序遍历出环境变量，环境变量是否有顺序依赖关系？
            <code>
              {
                Object.entries(envs).map(([key, value]) => (
                  <p className={style.envs} key={key}>{key} = {value}</p>
                ))
              }
            </code>
          )}
        />
        <Column
          title='依赖系统'
          dataIndex='lib_os'
          render={(os: string) => os.split(';').map((item: string) => (
            <Tag key={item}>{get(LIB_ENV, item, item)}</Tag>
          ))}
        />
        <Column
          title='类型'
          dataIndex='lib_type'
          render={(lib_type: string) => (
            <div className={style.lib}>
              <Tag className={cn(style.libTag, { [style.privite]: lib_type === LibTypeEnum.PRIVATE })}
              >{LIB_TYPE[lib_type] || lib_type}</Tag>
            </div>
          )}
        />
        <Column
          title='创建时间'
          dataIndex='created_time'
          render={(time: any) => time && formatDateTime(time)}
        />
        <Column
          title='创建人'
          dataIndex={['creator', 'nickname']}
        />
        {
          editable && (
            <Column
              title='操作'
              dataIndex='id'
              render={(id: number) => (
                <Button
                  type='text'
                  icon={<EditIcon />}
                  onClick={() => setModalData({
                    visible: true,
                    libId: id,
                  })}
                />
              )}
            />
          )
        }
      </Table>
      {
        editable && (
          <CreateToollibs
            orgSid={orgSid}
            isSuperuser={isSuperuser}
            visible={modalData.visible}
            libId={modalData.libId}
            onClose={() => setModalData({
              visible: false,
              libId: null,
            })}
            callback={() => getListData()}
          />
        )
      }
    </div>
  );
};

export default ToolLibs;
