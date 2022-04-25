import React from 'react';
import ReactMarkdown from 'react-markdown';
import cn from 'classnames';
import { invert, get } from 'lodash';
import { Drawer, Row, Col, Tag } from 'coding-oa-uikit';
import { SEVERITYENUM, SEVERITY } from '../constants';

import style from './style.scss';

interface RuleDetailProps {
  visible: boolean;
  data: any;
  onClose: () => void;
}

const RuleDetail = ({ visible, data, onClose }: RuleDetailProps) => (
  <Drawer
    title='规则详情'
    visible={visible}
    onClose={onClose}
    width={420}
    className={style.ruleDetail}
  >
    <Row className={style.row}>
      <Col span={6} className={style.label}>规则名称</Col>
      <Col span={18}>{data.display_name}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>规则简介</Col>
      <Col span={18}>{data.rule_title}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>规则状态</Col>
      <Col span={18}>
        <Tag className={cn(style.tag, style[`status-${data.disable ? 2 : 0}`])}>{data.disable ? '不可用' : '可用'}</Tag>
      </Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>适用语言</Col>
      <Col span={18}>{data.languages?.join(' | ')}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>规则分类</Col>
      <Col span={18}>{data.category_name}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>严重级别</Col>
      <Col span={18}>
        <Tag className={data.severity === 4 ? 'processing' : invert(SEVERITYENUM)[data.severity]}>
          {get(SEVERITY, data.severity)}
        </Tag>
      </Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>规则参数</Col>
      <Col span={18}>{data.rule_params}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>解决方法</Col>
      <Col span={18}>{data.solution}</Col>
    </Row>
    <Row className={style.row}>
      <Col span={6} className={style.label}>详细描述</Col>
      {
        data.checkruledesc?.desc && (
          <Col span={18}>
            <ReactMarkdown source={data.checkruledesc?.desc} />
          </Col>
        )
      }
    </Row>
  </Drawer>
);

export default RuleDetail;
