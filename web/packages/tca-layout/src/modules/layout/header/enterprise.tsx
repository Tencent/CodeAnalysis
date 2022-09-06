import React, { useState, useEffect } from 'react';
import { Link, useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { Tag, Breadcrumb, Select, Space } from 'coding-oa-uikit';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';

// 项目内
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import { getTeamRouter, getTeamsRouter, getProjectRouter, getHomeRouter } from '@src/utils/getRoutePath';
import HomeSvg from '@src/images/home.svg';
import LogoIco from '@src/images/favicon.ico';
import { getProjects } from '@src/services/team';

// 模块内
import s from './style.scss';

// 通过meta版本名称来定义是否显示Tag
const VERSION_NAME = getMetaContent('VERSION_NAME');

const { Option } = Select;

interface IProps {
  org: any;
  orgSid: string | undefined;
  teamName: string | undefined;
}

const Enterprise = ({ org, orgSid, teamName }: IProps) => {
  const history = useHistory();
  const [hoveredLogo, setHoveredLogo] = useState(false);
  const [projectOptions, setProjectOptions] = useState<Array<any>>([]);

  useEffect(() => {
    // 团队变更时重新获取项目列表
    if (org.org_sid && teamName) {
      getProjects(org.org_sid, null).then((response: any[]) => {
        setProjectOptions(response.map((item: any) => ({
          ...item,
          label: item.display_name,
          value: item.name,
        })));
      });
    }
  }, [orgSid]);

  const BreadcrumbRender = () => {
    if (orgSid && org.org_sid && orgSid === org.org_sid) {
      return (
        <>
          <Breadcrumb.Item>
            <Link
              to={`${getTeamRouter(org.org_sid)}/workspace`}
              className={s.enterpriseName}
            >
              {org.name}
            </Link>
          </Breadcrumb.Item>
          {teamName && (
            <Breadcrumb.Item>
              <Select
                value={teamName}
                onChange={(name: string) => {
                  history.push(`${getProjectRouter(org.org_sid, name)}/repos`);
                }}
                showSearch
                size="small"
                style={{ minWidth: '120px' }}
                bordered={false}
              >
                {projectOptions.map((item: any) => (
                  <Option key={item.value} value={item.value}>
                    {item.label}
                  </Option>
                ))}
              </Select>
            </Breadcrumb.Item>
          )}
        </>
      );
    }
    return (
      <Breadcrumb.Item>
        <Space>
          <strong className='text-grey-8 inline-block vertical-middle'>腾讯云代码分析</strong>
          {VERSION_NAME && <Tag>{VERSION_NAME}</Tag>}
        </Space>
      </Breadcrumb.Item>
    );
  };

  return (
    <>
      <Link
        // 如果当前在团队列表页面，则点击图标返回首页
        to={history.location.pathname === getTeamsRouter() ? getHomeRouter() : getTeamsRouter()}
        className={classnames(s.logo, s.enterpriseLogo)}
        onMouseEnter={() => setHoveredLogo(true)}
        onMouseLeave={() => setHoveredLogo(false)}
      >
        <img
          src={org.org_logo_url || LogoIco}
          className={classnames({ [s.hidden]: hoveredLogo })}
        />
        <img
          src={HomeSvg}
          className={classnames({ [s.hidden]: !hoveredLogo })}
        />
      </Link>
      <Breadcrumb separator={<AngleRight className="text-grey-6" />}>
        {BreadcrumbRender()}
      </Breadcrumb>
    </>
  );
};

export default Enterprise;
