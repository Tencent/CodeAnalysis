/**
 * 规则列表公共组件
 */

import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import cn from 'classnames';
import { isEmpty, get } from 'lodash';
import { Table, Button, Tooltip, Tag } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';

// 项目内
import { RULE_SEVERITY_CHOICES, RuleSeverityInvertEnum } from '@src/constant';
import RuleDetail from './rule-detail';
import style from '../style.scss';

const { Column } = Table;

interface ListComponentProps {
  data: any;
  loading: boolean;
  pager: any;
  editable: boolean;  // 表示是否有操作权限
  onChangePageSize: (page: number, pageSize: number) => void;
  onShowSizeChange: (current: number, size: number) => void;
  onEdit: (data: any) => void;
  onDel: (data: any) => void;
}

const ListComponent = (props: ListComponentProps) => {
  const { data, loading, pager, editable, onChangePageSize, onShowSizeChange, onEdit, onDel } = props;
  const { pageSize, pageStart, count } = pager;
  const [visible, setVisible] = useState(false);
  const [ruleDetail, setRuleDetail] = useState({});

  return (
    <>
      <Table
        dataSource={data}
        loading={loading}
        rowKey={(item: any) => item.id}
        style={{ padding: '0 20px' }}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: true,
          showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
          onChange: onChangePageSize,
          onShowSizeChange,
        }}
      >
        <Column
          title={t('规则名称')}
          dataIndex='display_name'
          render={(name: string, data: any) => (
            <a className='link-name' onClick={() => {
              setVisible(true);
              setRuleDetail(data);
            }}>{name}</a>
          )}
        />
        <Column
          title={t('规则简介')}
          dataIndex='rule_title'
          width={400}
        />
        <Column
          title={t('分类')}
          dataIndex='category_name'
        />
        <Column
          title={t('严重级别')}
          dataIndex='severity'
          render={severity => (
            <Tag className={cn(style.tag, RuleSeverityInvertEnum[severity].toLocaleLowerCase())}>
              {get(RULE_SEVERITY_CHOICES, severity)}
            </Tag>
          )}
        />
        <Column
          title={t('适用语言')}
          dataIndex='languages'
          render={(lang: any) => (isEmpty(lang) ? t('通用') : lang.join(' | '))}
        />
        <Column
          title={t('状态')}
          dataIndex='disable'
          width={editable ? undefined : 82}
          render={(disabled: boolean) => (
            <Tag className={cn(style.tag, style[`status-${disabled ? 2 : 0}`])}>{disabled ? t('不可用') : t('可用')}</Tag>
          )}
        // render={(status: any) => <span className={cn(style.ruleStatus,
        // { [style.disable]: status })}>{status ? '不可用' : '可用'}</span>}
        />
        {
          editable && (
            <Column
              title={t('操作')}
              dataIndex='id'
              width={92}
              render={(id: any, item: any) => (
                <>
                  <Tooltip title={t('编辑')}>
                    <Button type='text' icon={<Edit />} onClick={() => onEdit(item)} />
                  </Tooltip>
                  <Tooltip title={t('删除')}>
                    <Button type='text' icon={<Trash />} onClick={() => onDel(item)} />
                  </Tooltip>
                </>
              )}
            />
          )
        }
      </Table>
      <RuleDetail
        visible={visible}
        onClose={() => setVisible(false)}
        data={ruleDetail}
      />
    </>
  );
};

export default ListComponent;
