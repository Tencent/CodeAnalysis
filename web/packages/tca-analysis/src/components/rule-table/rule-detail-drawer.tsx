import React, { useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { get, isEmpty } from 'lodash';
import { Drawer, Tag, Divider } from 'tdesign-react';
import ReactMarkdown from 'react-markdown';

import { RuleSeverityEnum, RuleSeverityInvertEnum, RULE_SEVERITY_CHOICES } from '@src/constant';
import s from './style.scss';

interface RuleDetailDrawerProps {
  orgSid: string;
  ruleDetail: any;
  visible: boolean;
  handleClose: () => void;
  /** 获取规则详情请求 */
  getRuleDetail: (ruleId: number) => Promise<any>;
}

const RuleDetailDrawer = ({ ruleDetail, visible, handleClose, getRuleDetail }: RuleDetailDrawerProps) => {
  const [ruleInfo, setRuleInfo] = useState<any>({});
  const toolInfo = ruleDetail?.checktool;

  useEffect(() => {
    if (visible && ruleDetail.id) {
      if (isEmpty(ruleDetail?.checkrule)) {
        setRuleInfo(ruleDetail);
      } else {
        getRuleDetail?.(ruleDetail.checkrule.id).then((res: any) => {
          setRuleInfo(res);
        });
      }
    }
  }, [visible, ruleDetail]);

  const getRuleStatesTag = () => {
    switch (get(ruleInfo, 'disable')) {
      case false:
        return <Tag theme="success" variant="light">{t('活跃')}</Tag>;
      case true:
        return <Tag theme="danger" variant="light">{t('失效')}</Tag>;
      default:
        return <Tag>{t('未知')}</Tag>;
    }
  };

  return (
      <Drawer header={t('规则详情')} visible={visible} onClose={handleClose} size='500px' footer={null}>
        {!isEmpty(ruleDetail?.checkrule) && <>
          <Divider>{t('规则定制配置')}</Divider>
          <div className={s.ruleInfo} style={{ marginBottom: 60 }}>
            <div className={s.row}>
              <span className={s.col}>{t('严重级别')}</span>
              <span>
                <Tag className={RuleSeverityInvertEnum[get(ruleDetail, 'severity')]?.toLowerCase()}>
                  {RULE_SEVERITY_CHOICES[get(ruleDetail, 'severity') as RuleSeverityEnum]}
                </Tag>
              </span>
            </div>
            <div className={s.row}>
              <span className={s.col}>{t('规则参数')}</span>
              <span>{get(ruleDetail, 'rule_params')}</span>
            </div>
          </div>
          <Divider>{t('规则初始详情')}</Divider>
        </>}
        <div className={s.ruleInfo}>
          <div className={s.row}>
            <span className={s.col}>{t('规则名称')}</span>
            <span>{get(ruleInfo, 'real_name')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('展示名称')}</span>
            <span>{get(ruleInfo, 'display_name')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('所属工具')}</span>
            <span>
              <a
                className="link-name"
                target='_blank'
                rel="noopener noreferrer"
              >
                {get(toolInfo, 'display_name')}
                {get(toolInfo, 'scope', 0) === 1 && <span className='fs-12'>{t('（私有）')}</span>}
              </a>
            </span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('规则概述')}</span>
            <span>{get(ruleInfo, 'rule_title')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('责任人')}</span>
            <span>{get(ruleInfo, 'owner')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('规则状态')}</span>
            <span>{getRuleStatesTag()}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('适用语言')}</span>
            <span>{get(ruleInfo, 'languages')?.join(', ') || '通用'}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('严重级别')}</span>
            <span>
              <Tag className={RuleSeverityInvertEnum[get(ruleInfo, 'severity')]?.toLowerCase()}>
                {RULE_SEVERITY_CHOICES[get(ruleInfo, 'severity') as RuleSeverityEnum]}
              </Tag>
            </span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('规则参数')}</span>
            <span>{get(ruleInfo, 'rule_params')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('解决方法')}</span>
            <span>{get(ruleInfo, 'solution')}</span>
          </div>
          <div className={s.row}>
            <span className={s.col}>{t('详细描述')}</span>
            <div className={s.desc}>
              <ReactMarkdown>{get(ruleInfo, 'checkruledesc.desc', '')}</ReactMarkdown>
            </div>
          </div>
        </div>
      </Drawer>
  );
};

export default RuleDetailDrawer;
