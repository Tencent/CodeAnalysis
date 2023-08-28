import React from 'react';
import { get } from 'lodash';
import classnames from 'classnames';
import { useParams, useHistory } from 'react-router-dom';
import { Row, Col, Space, Divider, Tabs, TdTabsProps, TabPanelProps, TabValue } from 'tdesign-react';

import s from './style.scss';

const { TabPanel } = Tabs;

/** tab 参数项 */
export interface PageHeaderTabProps {
  /** tab项 */
  options: TabPanelProps[];
  /** useParams 路由key，默认取tabName */
  key?: string;
  /** 路由跳转路径处理 */
  routeChangeHandler?: (value: TabValue) => string;
  /** tab参数项 */
  props?: Omit<TdTabsProps, 'value' | 'onChange' | 'size'>
  /** tab value */
  value?: TabValue,
  /** tab change */
  onChange?: (value: TabValue) => void;
}

/** page header 参数项 */
interface PageHeaderProps {
  /** 标题 */
  title: React.ReactNode;
  /** 描述 */
  description?: React.ReactNode;
  /** tab */
  tab?: PageHeaderTabProps;
  /** 操作 */
  action?: React.ReactNode;
  /** page header class */
  className?: string;
  /** page header style */
  style?: React.CSSProperties;
}

const PageHeader = ({ title, description, action, tab, className, style }: PageHeaderProps) => {
  const routeParams = useParams();
  const history = useHistory();

  let tabComponent = <></>;
  if (tab) {
    const { options, routeChangeHandler, key = 'tabName', value, onChange, props = {} } = tab;
    const tabValue: TabValue = value || get(routeParams, key);
    tabComponent = <Tabs {...props} value={tabValue} onChange={onChange ? onChange : (value) => {
      routeChangeHandler && history.push(routeChangeHandler(value));
    }}>
      {options.map(item => <TabPanel key={item.value} {...item} />)}
    </Tabs>;
  }

  return <Row className={classnames(s.pageHeader, tab ? s.existTab : '', className)} style={style} align='center' >
    <Col flex="auto">
      <Space size={10} align='center' separator={<Divider layout="vertical" />} >
        <div>
          <p className={s.pageHeaderTitle}>{title}</p>
          {description && <p className={s.pageHeaderDesc}>{description}</p>}
        </div>
        {tabComponent}
      </Space>
    </Col>
    <Col flex="200px" className='tca-text-right'>
      <Space align='center' style={{ height: '100%' }} >{action}</Space>
    </Col>
  </Row>;
};

export default PageHeader;
