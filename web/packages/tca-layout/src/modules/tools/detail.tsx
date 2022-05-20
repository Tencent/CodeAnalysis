/**
 * 工具详情
 */
import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { find } from 'lodash';
import { Tabs } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import { getToolsRouter } from '@src/utils/getRoutePath';
import { getToolDetail } from '@src/services/tools';
import { getTeamMember } from '@src/services/team';
import { useStateStore } from '@src/context/store';

import BaseInfo from './baseinfo/baseinfo';
import BaseInfoManage from './baseinfo/baseinfo-manage';
import LibScheme from './lib-scheme';
import Rules from './rules';
import CustomRules from './rules/custom-rules';
import WhiteList from './white-list';
import style from './detail.scss';

const { TabPane } = Tabs;

const ToolDetail = () => {
  const history = useHistory();
  const { userinfo } = useStateStore();
  const { orgSid, toolId, tab }: any = useParams();
  const [detail, setDetail] = useState<any>({});
  const [admins, setAdmins] = useState([]);
  const isAdmin = !!find(admins, { username: userinfo.username });  // 当前用户是否是管理员
  const isCustom = orgSid === detail?.org_detail?.org_sid;   // 当前工具为自定义工具
  const isSuperuser = userinfo.is_superuser;  // 是否为超级管理员

  useEffect(() => {
    getTeamMember(orgSid).then((res) => {
      setAdmins(res.admins || []);
    });
  }, [orgSid]);

  useEffect(() => {
    getDetail();
  }, [orgSid, toolId]);

  const getDetail = () => {
    getToolDetail(orgSid, toolId).then((res) => {
      setDetail(res);
    });
  };

  return (
    <div className={style.toolDetail}>
      <Tabs
        activeKey={tab}
        // className={style.tabs}
        onChange={(key) => {
          if (key !== tab) {
            history.push(`${getToolsRouter(orgSid)}/${toolId}/${key}`);
          }
        }}
      >
        <TabPane tab={
          <div>
            <span
              className={style.backIcon}
              onClick={() => history.push(getToolsRouter(orgSid))}
            >
              <ArrowLeft />
            </span>
            <span>{detail.display_name}</span>
          </div>
        } disabled key="null" />

        <TabPane tab="基础信息" key="baseinfo">
          {
            isSuperuser ? (
              <BaseInfoManage
                data={detail}
                toolId={toolId}
                orgSid={orgSid}
                getDetail={getDetail}
              />
            ) : (
              <BaseInfo
                data={detail}
                orgSid={orgSid}
                toolId={toolId}
                editable={isCustom && isAdmin}
                getDetail={getDetail}
              />
            )
          }
        </TabPane>
        <TabPane tab='依赖配置' key='tool-libs'>
          <LibScheme
            orgSid={orgSid}
            toolId={toolId}
          />
        </TabPane>
        <TabPane tab="规则列表" key="rules">
          <Rules
            editable={(isCustom && isAdmin) || isSuperuser}
            toolDetail={detail}
            orgSid={orgSid}
            toolId={toolId}
            tab={tab}
          />
        </TabPane>
        {
          detail.open_maintain && (
            <TabPane tab="自定义规则" key="customRules">
              <CustomRules
                editable={isAdmin || isSuperuser}
                toolDetail={detail}
                orgSid={orgSid}
                toolId={toolId}
                tab={tab}
              />
            </TabPane>
          )
        }
        {
          ((isCustom && isAdmin) || isSuperuser) && (
            <TabPane tab="工具白名单" key="whitelist">
              <WhiteList
                toolDetail={detail}
                orgSid={orgSid}
                toolId={toolId}
                tab={tab}
              />
            </TabPane>
          )
        }
      </Tabs>
    </div >
  );
};

export default ToolDetail;
