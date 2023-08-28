import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useHistory, useParams } from 'react-router-dom';
import { filter } from 'lodash';
import { Breadcrumb, Select } from 'tdesign-react';

// 项目内
import { getTeamRouter, getProjectRouter } from '@src/utils/getRoutePath';
import { getProjects } from '@src/services/team';

const { BreadcrumbItem } = Breadcrumb;

/** 路由到团队页面 */
const routerToTeam = (history: any, orgSid: string, replace = false) => {
  const pathname = `${getTeamRouter(orgSid)}/workspace`;
  if (location.pathname !== pathname) {
    if (replace) {
      history.replace(pathname);
    } else {
      history.push(pathname);
    }
  }
};

const Enterprise = () => {
  const [projectOptions, setProjectOptions] = useState<Array<any>>([]);
  const org = useSelector((state: any) => state.APP)?.org ?? {};
  const { orgSid, name: teamName }: any = useParams();

  const history = useHistory();

  useEffect(() => {
    // 团队变更时重新获取项目列表
    if (org.org_sid === orgSid && teamName) {
      getProjects(org.org_sid, null).then((response: any[]) => {
        // 只显示未禁用的项目
        const activeProjects = filter(response, { status: 1 });
        setProjectOptions(activeProjects.map((item: any) => ({
          ...item,
          label: item.display_name,
          value: item.name,
        })));
      });
    } else if (org.org_sid !== orgSid) {
      routerToTeam(history, org.org_sid, true);
    }
  }, [org?.org_sid, orgSid, history, teamName]);

  if (org.org_sid !== orgSid) {
    return <></>;
  }

  return <Breadcrumb maxItemWidth="160px">
    <BreadcrumbItem >
      <span onClick={() => {
        routerToTeam(history, org.org_sid);
      }}>{org.name}</span>
    </BreadcrumbItem>
    {teamName && (
      <BreadcrumbItem>
        <Select
          borderless
          value={teamName}
          onChange={(name: string) => {
            history.push(`${getProjectRouter(org.org_sid, name)}/repos`);
          }}
          options={projectOptions}
        />
      </BreadcrumbItem>
    )}
  </Breadcrumb>;
};

export default Enterprise;
