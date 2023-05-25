import React from 'react';
import { t } from '@src/utils/i18n';
import { Form, Input } from 'coding-oa-uikit';

export const getExtraCreateTeamInfos: any = null;

export const getExtraTeamInfos = (isEdit: boolean, data: any) => (
  <>
    <Form.Item
      label={t('团队联系方式')}
      name="tel_number"
      rules={
        isEdit
          ? [{ required: true, message: t('团队联系方式为必填项') }]
          : undefined
      }
    >
      {isEdit ? <Input width={400} /> : <>{data.tel_number}</>}
    </Form.Item>
  </>
);

/** 是否开启团队删除功能 */
export const ENABLE_DELETE_ORG = true;
