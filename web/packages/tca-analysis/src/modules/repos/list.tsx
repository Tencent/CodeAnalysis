/**
 * 代码库列表
 */
import React, { useState } from 'react';
import cn from 'classnames';
import { Link, useHistory } from 'react-router-dom';
import Highlighter from 'react-highlight-words';
import { TablePaginationConfig } from 'coding-oa-uikit/lib/table';
import { Tooltip, Popover, Input, Button, message, Space } from 'coding-oa-uikit';
import PencilIcon from 'coding-oa-uikit/lib/icon/Pencil';
import ScanIcon from 'coding-oa-uikit/lib/icon/Scan';
import ShieldIcon from 'coding-oa-uikit/lib/icon/Shield';
import MemberSettingsIcon from 'coding-oa-uikit/lib/icon/MemberSettings';
import ClockIcon from 'coding-oa-uikit/lib/icon/Clock';
import AlignLeftIcon from 'coding-oa-uikit/lib/icon/AlignLeft';

import Table from '@tencent/micro-frontend-shared/component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';
import { getRepoName } from '@tencent/micro-frontend-shared/tca/util';
import { putRepo } from '@src/services/repos';
import { getProjectRouter } from '@src/utils/getRoutePath';

import MemberConfig from './member-config';
import AuthorityConfig from './authority-config';
import EditModal from './edit-modal';
import style from './style.module.scss';

const { Column } = Table;

interface RepoListProps {
  orgSid: string;
  teamName: string;
  searchWords: string;  // 搜索关键字
  loading: boolean;
  list: Array<any>;
  pagination: TablePaginationConfig;
  callback: () => void;
  /** 关闭仓库成员配置 */
  closeMemberConf?: boolean;
}

const RepoList = (props: RepoListProps) => {
  const {
    orgSid, teamName, searchWords, loading, list, pagination, callback, closeMemberConf,
  } = props;
  const history = useHistory();
  const [visible, setVisible] = useState(false);  // 修改别名
  const [name, setName] = useState('');
  const [editVsb, setEditVsb] = useState({
    visible: false,
    repoInfo: null,
  });
  const [hoverRowId, setHoverRowId] = useState(undefined);
  const [clickRowIds, setClickRowIds] = useState([]);
  const [memberConf, setMemberConf] = useState({
    visible: false,
    repoId: undefined,
  });
  const [authorityConf, setAuthorityConf] = useState({
    visible: false,
    repoInfo: null,
  });

  const updataName = (data: any) => {
    if (name && name !== data.name) {
      putRepo(orgSid, teamName, data.id, {
        ...data,
        name,
      }).then(() => {
        message.success('别名修改成功');
        callback?.();
        setVisible(false);
        setName('');
      });
    } else {
      setVisible(false);
    }
  };

  // const subscribedHandle = (repoId: number, subscribed: boolean) => {
  //   const func = subscribed ? subscribedRepo : cancelSubscribedRepo;
  //   func(orgSid, teamName, repoId).then(() => {
  //     message.success(`已${subscribed ? '关注' : '取消关注'}该项目`);
  //     callback?.();
  //   });
  // };

  return (
    <>
      <Table
        rowKey={item => item.id}
        loading={loading}
        dataSource={list}
        onRow={record => ({
          onClick: () => {
            setClickRowIds([record.id]);
          }, // 点击行
          onMouseEnter: () => {
            setHoverRowId(record.id);
          }, // 鼠标移入行
          onMouseLeave: () => {
            setHoverRowId(undefined);
          }, // 鼠标移出行
        })}
        pagination={pagination}
        scroll={{ x: true }}
      >
        <Column
          title="代码库别名"
          dataIndex='name'
          width={300}
          render={(name: string, data: any) => (
            <>
              <Link
                to={getProjectRouter(orgSid, teamName, data.id)}
                className={cn(style.scmUrl, {
                  [style.hover]: hoverRowId === data.id,
                }, 'breakall')}
              >
                <Highlighter
                  searchWords={[searchWords]}
                  autoEscape={true}
                  textToHighlight={getRepoName(data)}
                />
              </Link>
              {/* todo: 待接口完善 */}
              {/* <span className={style.starIcon} onClick={() => {
                subscribedHandle(data.id, !data.subscribed);
              }}>
                { // 关注的图标一直显示
                  (hoverRowId === data.id || data.subscribed) && (
                    <Tooltip title={`点击${data.subscribed ? '取消' : ''}关注`}>
                      {
                        data.subscribed ? <CancelStarIcon /> : <StarIcon />
                      }
                    </Tooltip>
                  )
                }
              </span> */}
              <span className={style.pencilIcon}>
                {
                  hoverRowId === data.id && (
                    <Tooltip title='点击修改别名'>
                      <Popover
                        title="修改别名"
                        trigger="click"
                        visible={visible && clickRowIds.includes(data.id)}
                        getPopupContainer={() => document.body}
                        onVisibleChange={(visible) => {
                          setVisible(visible);
                          if (!visible) {
                            setName('');
                          }
                        }}
                        content={(
                          <div>
                            <Input
                              size='small'
                              defaultValue={getRepoName(data)}
                              onChange={e => setName(e.target.value)}
                            />
                            <div style={{
                              marginTop: '16px',
                            }}>
                              <Button
                                size='small'
                                type='primary'
                                onClick={() => updataName(data)}
                                style={{ marginRight: '10px' }}
                              >修改</Button>
                              <Button size='small' onClick={() => setVisible(false)}>取消</Button>
                            </div>
                          </div>
                        )}
                      >
                        <Button type='text'>
                          <PencilIcon />
                        </Button>
                      </Popover>
                    </Tooltip>
                  )
                }
              </span>
            </>
          )}
        />
        <Column
          title="代码库地址"
          dataIndex='scm_url'
          width={400}
          render={(url: string, data: any) => (
            <a
              target='_blank'
              href={url}
              rel="noreferrer"
              className={cn(style.scmUrl, {
                [style.hover]: hoverRowId === data.id,
              }, 'breakall')}
            >
              <Highlighter
                searchWords={[searchWords]}
                autoEscape={true}
                textToHighlight={url}
              />
            </a>
          )}
        />
        <Column
          title="接入时间"
          dataIndex='created_time'
          render={time => time && <div className='nowrap'>{formatDateTime(time)}</div>}
        />
        <Column
          title="最近活跃分支"
          dataIndex='recent_active'
          render={(data: any, record: any) => (
            <div>
              <Link to={`${getProjectRouter(orgSid, teamName, record.id, data?.id)}/overview`}>
                {data?.branch_name}
              </Link>
              {
                data?.active_time && (
                  <div className={cn(style.desc, 'nowrap')}>
                    <span><ClockIcon /> {formatDateTime(data.active_time)} &nbsp;</span>
                    {data.total_line_num && <span><AlignLeftIcon /> {data.total_line_num} 行 </span>}
                  </div>
                )
              }
            </div>
          )}
        />
        {/* <Column
          title="创建渠道"
          dataIndex='created_from'
        /> */}
        <Column
          title="操作"
          dataIndex='id'
          fixed='right'
          render={(id, record: any) => (
            <Space className='nowrap'>
              <Tooltip title='切换凭证'>
                <Button size='small' icon={<ShieldIcon />}
                  type='text'
                  onClick={() => {
                    setAuthorityConf({
                      visible: true,
                      repoInfo: record,
                    });
                  }}
                />
              </Tooltip>
              {!closeMemberConf && <Tooltip title='仓库成员设置'>
                <Button size='small' icon={<MemberSettingsIcon />}
                  type='text'
                  onClick={() => setMemberConf({
                    visible: true,
                    repoId: id,
                  })}
                />
              </Tooltip>}
              <Tooltip title='进入代码分析' getPopupContainer={() => document.body}>
                <Button size='small' icon={<ScanIcon />} type='text' onClick={() => {
                  history.replace(getProjectRouter(orgSid, teamName, record.id));
                }} />
              </Tooltip>
              <Tooltip title='编辑'>
                <Button size='small' icon={<PencilIcon />}
                  type='text'
                  onClick={() => setEditVsb({
                    visible: true,
                    repoInfo: record,
                  })}
                />
              </Tooltip>
            </Space>
          )}
        />
      </Table>
      <MemberConfig
        orgSid={orgSid}
        teamName={teamName}
        visible={memberConf.visible}
        repoId={memberConf.repoId}
        onCancel={() => {
          setMemberConf({
            visible: false,
            repoId: undefined,
          });
        }}
      />
      <AuthorityConfig
        orgSid={orgSid}
        teamName={teamName}
        visible={authorityConf.visible}
        repoInfo={authorityConf.repoInfo}
        onCancel={() => {
          setAuthorityConf({
            visible: false,
            repoInfo: null,
          });
        }}
        callback={() => callback?.()}
      />
      <EditModal
        orgSid={orgSid}
        teamName={teamName}
        visible={editVsb.visible}
        repoInfo={editVsb.repoInfo}
        onCancel={() => {
          setEditVsb({
            visible: false,
            repoInfo: null,
          });
        }}
        callback={() => callback?.()}
      />
    </>
  );
};

export default RepoList;
