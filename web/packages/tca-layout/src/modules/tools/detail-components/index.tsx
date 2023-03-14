/**
 * 工具详情
 */
import React, { useEffect, useState } from 'react';
import { t } from '@src/utils/i18n';
import { useParams, useHistory } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Tabs } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import { getToolsRouter } from '@src/utils/getRoutePath';
import { getToolDetail } from '@src/services/tools';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';
import { NAMESPACE, UserState } from '@src/store/user';
import { isEnableManage } from '@plat/util';

import BaseInfo from './baseinfo';
import LibScheme from './lib-scheme';
import Rules from './rules';
import CustomRules from './rules/custom-rules';
import WhiteList from './white-list';
import style from './style.scss';

const { TabPane } = Tabs;

const ToolDetail = () => {
  const history = useHistory();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const { orgSid, toolId, tab }: any = useParams();
  const [detail, setDetail] = useState<any>({});
  const isAdmin = useSelector((state: any) => state.APP)?.isOrgAdminUser ?? false;
  const isCustom = orgSid === detail?.org_detail?.org_sid;   // 当前工具为自定义工具
  const isSuperuser = userinfo.is_superuser;  // 是否为超级管理员
  const isManage = /^\/manage/.test(window.location.pathname);  // 管理页面
  const editable = (isCustom && isAdmin) || isSuperuser || isEnableManage();  // 编辑权限

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
              onClick={() => history.push(`${isManage ? '/manage/tools' : getToolsRouter(orgSid)}`)}
            >
              <ArrowLeft />
            </span>
            <span>{detail.display_name}</span>
          </div>
        } disabled key='null' />

        <TabPane tab={t('基础信息')} key='baseinfo'>
          <BaseInfo
            data={detail}
            orgSid={orgSid}
            editable={editable || isEnableManage()}
            getDetail={getDetail}
          />
        </TabPane>
        <TabPane tab={t('依赖配置')} key='tool-libs'>
          <LibScheme
            editable={editable}
            orgSid={orgSid}
            toolId={toolId}
          />
        </TabPane>
        <TabPane tab={t('规则列表')} key='rules'>
          <Rules
            editable={(isCustom && isAdmin) || isManage}
            toolDetail={detail}
            orgSid={orgSid}
            toolId={toolId}
            tab={tab}
          />
        </TabPane>
        {
          detail.open_maintain && (
            <TabPane tab={t('自定义规则')} key='customRules'>
              <CustomRules
                editable={isAdmin || isManage}
                toolDetail={detail}
                orgSid={orgSid}
                toolId={toolId}
                tab={tab}
              />
            </TabPane>
          )
        }
        {
          editable && (
            <TabPane tab={t('工具白名单')} key='whitelist'>
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
