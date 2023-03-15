import React, { useRef } from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { Dialog, Form, Input, Select, Tooltip, Textarea, FormInstanceFunctions, InputAdornment } from 'tdesign-react';
import { HelpCircleIcon } from 'tdesign-icons-react';

// 项目内
import { SCM_PLATFORM_OPTIONS } from '@plat/oauth';
import s from '../style.scss';

// 模块内
import { OAuthSettingData } from './types';

const { FormItem } = Form;

const getHostName = (redirect_uri: string) => {
  if (redirect_uri) {
    const urlList = redirect_uri.split('/');
    const hostname = (urlList.length > 3) ? get(urlList, 2) : redirect_uri;
    return hostname;
  }
  return '';
};

interface OAuthModalProps {
  visible: boolean;
  scminfo: OAuthSettingData;
  onCancel: () => void;
  onOk: (scminfo: OAuthSettingData, formData: any) => void;
}

const OAuthModal = ({ scminfo, visible, onCancel, onOk }: OAuthModalProps) => {
  const formRef = useRef<FormInstanceFunctions>(null);

  /** 表单保存操作 */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        const fieldsValue = formRef.current?.getFieldsValue(true);
        onOk(scminfo, {
          ...fieldsValue,
          redirect_uri: `http://${fieldsValue.redirect_uri}/cb_git_auth/${scminfo?.scm_platform_name}`,
        });
      }
    });
  };

  /** 重置表单操作 */
  const onReset = () => {
    formRef.current?.reset();
  };

  return (
    <Dialog
      header={scminfo?.client_id ? t('更新配置') : t('创建配置')}
      visible={visible}
      onConfirm={onSubmitHandle}
      width={610}
      onClose={onCancel}
      onOpened={onReset}
      onClosed={onReset}
    >
      <Form
        layout='vertical'
        ref={formRef}
        resetType='initial'
        labelWidth={120}
      >
        <FormItem name="scm_platform" label={t('平台类型')} initialData={scminfo?.scm_platform}>
          <Select options={SCM_PLATFORM_OPTIONS} disabled />
        </FormItem>
        <FormItem
          name="client_id"
          label={t('Client ID')}
          rules={[{ required: true, message: t('Client ID为必填项') }]}
          initialData={scminfo?.client_id}
        >
          <Input />
        </FormItem>
        <FormItem
          name="client_secret"
          label={t('Client Secret')}
          rules={[{ required: true, message: t('Client Secret为必填项') }]}
          initialData={scminfo?.client_secret}
        >
          <Input type="password" />
        </FormItem>
        <FormItem
          name="redirect_uri"
          label={
            <>
              {t('回调地址')}
              <Tooltip
                content={<p>{t('请填入当前TCA平台配置的域名或IP地址')}<br />{t('（如当前页面非80端口，需要显式指定端口号）')}</p>}
                placement="top"
              >
                <HelpCircleIcon className={s.helpIcon} />
              </Tooltip>
            </>
          }
          rules={[{ required: true, message: t('回调地址为必填项') }]}
          initialData={getHostName(scminfo?.redirect_uri)}
        >
          <InputAdornment style={{ width: '100%' }}
            prepend={<div style={{ width: 46 }}>http://</div>}
            append={<div style={{ width: 150 }}>/cb_git_auth/{scminfo?.scm_platform_name}</div>}>
            <Input placeholder="部署机IP" />
          </InputAdornment>
        </FormItem>
        <FormItem
          name="scm_platform_desc"
          label={t('平台描述')}
          rules={[{ max: 64, message: '平台描述不能超过32字' }]}
          initialData={scminfo?.scm_platform_desc}
        >
          <Textarea maxlength={32} placeholder={'平台描述'} />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default OAuthModal;
